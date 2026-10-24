"""The checkout's verbs: ide, agent, tool, set, default, env, docker-args, deny, forget, unbind, show, check."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
import tomllib

import pytest

from devcapsule import cli
from devcapsule.configuration.storage import checkout_record_paths, load_toml, registered_checkouts
from devcapsule.configuration.docker_arguments import arguments_path, read_arguments
from devcapsule.configuration.capability_commands import paths


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME"):
        monkeypatch.setenv(key, str(tmp_path / key.lower()))
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["project", "--path", str(root), "init", "--require", "node", "--offer", "browser-automation",
                     "--creator", "mailto:owner@example.test"]) == 0
    return root


def run(root: Path, *arguments: str) -> int:
    return cli.main(["project", "--path", str(root), "config", *arguments])


def record(root: Path) -> dict:
    manifest = load_toml(paths(root)[0])
    return load_toml(checkout_record_paths(manifest, root)[0])


def test_show_and_check_write_nothing_and_check_exits_three_on_pending(project: Path, capsys, tmp_path: Path) -> None:
    manifest = load_toml(paths(project)[0])
    input_path, resolution_path = checkout_record_paths(manifest, project)
    before = input_path.read_bytes()
    assert run(project, "show") == 0
    out = capsys.readouterr().out
    assert "KIND" in out and "ide     (none)" in out and "choose one:" in out
    assert "Resolution: missing" in out
    assert run(project, "check") == 3
    err = capsys.readouterr().err
    assert "Pending decisions:" in err and "config ide IDE" in err
    assert input_path.read_bytes() == before and not resolution_path.exists()
    # An unregistered checkout is listed too, from nothing.
    other = tmp_path / "elsewhere"
    other.mkdir()
    (other / ".devcapsule").mkdir()
    for name in ("devcapsule.toml", "devcapsule.linux-amd64.lock"):
        (other / ".devcapsule" / name).write_bytes((project / ".devcapsule" / name).read_bytes())
    assert run(other, "show") == 0
    assert "no record yet" in capsys.readouterr().out
    assert len(registered_checkouts()) == 1


def test_show_json_carries_the_listing(project: Path, capsys) -> None:
    assert run(project, "show", "--json") == 0
    document = json.loads(capsys.readouterr().out)
    assert document["schema-version"] == 2 and document["resolution"] == "missing"
    assert {row["kind"] for row in document["rows"]} >= {"ide", "tool", "memory", "cpus", "access"}
    assert run(project, "list", "--json") == 0
    assert json.loads(capsys.readouterr().out)["rows"] == document["rows"]
    assert run(project, "check", "--json") == 3
    assert "(none)" in json.loads(capsys.readouterr().out)["pending"]


def test_ide_agent_and_tool_verbs_edit_the_selection(project: Path, capsys) -> None:
    assert run(project, "ide", "codium") == 0
    assert "frontend-ide (codium)" in capsys.readouterr().out
    assert run(project, "agent", "add", "codex", "claude-code-agent") == 0
    assert record(project)["capabilities"]["selected"] == ["claude-code-agent", "codex-agent", "frontend-ide"]
    assert run(project, "agent", "remove", "codex-agent") == 0
    assert run(project, "ide", "python-ide") == 0
    assert record(project)["capabilities"]["selected"] == ["claude-code-agent", "python-ide"]
    assert run(project, "tool", "omit", "browser-automation") == 0
    assert record(project)["capabilities"]["without"] == ["browser-automation"]
    assert run(project, "tool", "restore", "browser-automation") == 0
    assert record(project)["capabilities"]["without"] == []
    assert run(project, "tool", "omit", "node") == 2
    assert "A required tool cannot be omitted" in capsys.readouterr().err
    assert run(project, "ide", "emacs") == 2
    assert "Unknown IDE" in capsys.readouterr().err
    assert run(project, "agent", "add", "python-ide") == 2


def test_set_memory_cpus_default_and_declared_values(project: Path, capsys, monkeypatch) -> None:
    assert run(project, "set", "memory", "6g") == 0
    assert "Set memory = 6GiB" in capsys.readouterr().out
    assert run(project, "set", "cpus", "4") == 0
    assert record(project)["configuration"]["values"] == {"memory": "6GiB", "cpus": 4}
    assert run(project, "set", "cpus", "default") == 0
    assert "cpus" not in record(project)["configuration"]["values"]
    assert run(project, "set", "memory", "none") == 2
    assert run(project, "set", "memroy", "1g") == 2
    assert "Did you mean 'memory'?" in capsys.readouterr().err
    assert run(project, "default", "cpus", "2") == 0
    assert run(project, "default", "swap", "2") == 2
    workstation = tomllib.loads((Path(os.environ["XDG_CONFIG_HOME"]) / "devcapsule" / "workstation.toml").read_text())
    assert workstation["defaults"] == {"cpus": 2}
    assert run(project, "show") == 0
    out = capsys.readouterr().out
    assert "workstation default" in out
    assert run(project, "default", "cpus", "none") == 0
    assert tomllib.loads((Path(os.environ["XDG_CONFIG_HOME"]) / "devcapsule" / "workstation.toml").read_text())["defaults"] == {}


def test_legacy_memory_name_redirects_to_memory(project: Path, capsys) -> None:
    manifest_path = paths(project)[0]
    manifest_path.write_text(manifest_path.read_text() + '\n[configuration.values."runtime.memory-limit"]\ntype = "memory-size"\nruntime-effect = "docker.memory-limit"\n')
    assert run(project, "set", "runtime.memory-limit", "8GiB") == 2
    assert "config set memory SIZE" in capsys.readouterr().err
    assert run(project, "set", "memory", "8GiB") == 0


def test_env_set_from_host_unset_and_list(project: Path, capsys) -> None:
    assert run(project, "env", "set", "POSTGRES_HOST", "db.example.org") == 0
    assert run(project, "env", "set", "POSTGRES_PASSWORD", "--from-host") == 0
    assert run(project, "env", "set", "BOTH", "x", "--from-host") == 2
    assert run(project, "env", "list") == 0
    out = capsys.readouterr().out
    assert "POSTGRES_HOST  (saved)" in out and "POSTGRES_PASSWORD  (from the host)" in out and "db.example.org" not in out
    manifest = load_toml(paths(project)[0])
    saved = read_arguments(arguments_path(checkout_record_paths(manifest, project)[0]))
    assert saved == ["--env", "POSTGRES_PASSWORD", "--env", "POSTGRES_HOST=db.example.org"]
    assert run(project, "env", "unset", "POSTGRES_HOST") == 0
    capsys.readouterr()
    assert run(project, "env", "list", "--json") == 0
    assert json.loads(capsys.readouterr().out)["from-host"] == ["POSTGRES_PASSWORD"]
    # The rc3 spellings still work, hidden, and say so.
    assert run(project, "set-env", "OLD", "v") == 0
    assert "now 'config env set'" in capsys.readouterr().err
    assert run(project, "show") == 0
    out = capsys.readouterr().out
    assert re.search(r"^env\s+OLD\s+set\s+checkout", out, re.M)


def test_env_without_a_terminal_needs_a_value(project: Path, capsys, monkeypatch) -> None:
    import sys
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert run(project, "env", "set", "SECRET") == 2
    assert "terminal is required" in capsys.readouterr().err


def test_docker_args_set_list_clear(project: Path, capsys) -> None:
    assert run(project, "docker-args", "set", "--", "--gpus", "all", "--env", "K=secret") == 0
    assert run(project, "docker-args", "list") == 0
    out = capsys.readouterr().out
    assert "--gpus all" in out and "K=<redacted>" in out
    assert run(project, "docker-args", "set", "--", "--memory", "2g") == 2
    assert "config set memory SIZE" in capsys.readouterr().err
    assert run(project, "docker-args", "set", "--", "--cpus", "2") == 2
    assert run(project, "docker-args", "set") == 2
    assert run(project, "docker-args", "clear") == 0
    capsys.readouterr()
    assert run(project, "docker-args", "list", "--json") == 0
    assert json.loads(capsys.readouterr().out)["arguments"] == []
    assert run(project, "set-extra-docker-args", "--", "--gpus", "all") == 0
    assert "now 'config docker-args set'" in capsys.readouterr().err


def test_authorize_deny_forget_and_the_wording(project: Path, capsys) -> None:
    assert run(project, "authorize", "network", "host") == 0
    out = capsys.readouterr().out
    assert "Authorized network for this checkout: host" in out
    assert "What this grants:" in out and "exact recorded image" not in out
    assert run(project, "deny", "docker-daemon") == 0
    assert "Denied docker-daemon for this checkout: none" in capsys.readouterr().out
    assert record(project)["authorization"]["docker-daemon"]["value"] == "none"
    assert run(project, "deny", "base-image") == 2
    assert run(project, "forget", "network") == 0
    assert "network" not in record(project)["authorization"]
    assert run(project, "forget", "network") == 2
    assert run(project, "authorize", "base-image", "default") == 0
    assert "exact recorded image" in capsys.readouterr().out
    assert run(project, "unset", "docker-daemon") == 0
    assert "now 'config forget'" in capsys.readouterr().err


def test_bind_and_unbind_need_an_ide_and_return_to_the_managed_default(project: Path, tmp_path: Path, capsys) -> None:
    home = tmp_path / "bound-home"
    home.mkdir()
    assert run(project, "ide", "frontend-ide") == 0
    assert run(project, "bind", "home", f"host-directory:{home}") == 0
    assert record(project)["configuration"]["bindings"]["host-directory"]["home"] == str(home)
    assert run(project, "unbind", "home") == 0
    assert "home" not in record(project)["configuration"].get("bindings", {}).get("host-directory", {})
    assert run(project, "unbind", "home") == 2


def test_every_config_leaf_is_listed_or_hidden_with_its_replacement() -> None:
    from devcapsule.commands.framework import render_command_listing
    from devcapsule.commands.project import ConfigGroup
    listing = render_command_listing(ConfigGroup.subcommands())
    for visible in ("show", "check", "ide", "agent", "tool", "set", "default", "authorize", "deny", "forget", "bind",
                    "unbind", "env", "docker-args", "require", "offer", "drop", "recommend"):
        assert f"  {visible} " in listing, visible
    for hidden in ("set-env", "list-env", "unset-env", "set-extra-docker-args", "capabilities", "need", "unset"):
        assert f"  {hidden} " not in listing, hidden
