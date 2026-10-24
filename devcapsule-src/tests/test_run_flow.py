"""``project run`` derives, reports and asks: the flow before the launch, without Docker."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tomllib

import pytest

from devcapsule import cli
from devcapsule.commands._run_flow import RunFlags, prepare_launch
from devcapsule.compat import DecisionPending
from devcapsule.configuration.capability_commands import paths
from devcapsule.configuration.docker_arguments import arguments_path, read_arguments
from devcapsule.configuration.storage import checkout_record_paths, load_toml, registered_checkouts, trust_path


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME"):
        monkeypatch.setenv(key, str(tmp_path / key.lower()))
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["project", "--path", str(root), "init", "--require", "node", "--creator", "mailto:owner@example.test"]) == 0
    return root


def config(root: Path, *arguments: str) -> int:
    return cli.main(["project", "--path", str(root), "config", *arguments])


def record(root: Path) -> dict:
    return load_toml(checkout_record_paths(load_toml(paths(root)[0]), root)[0])


def test_without_a_terminal_a_pending_ide_ends_with_status_three_and_writes_nothing(project: Path, tmp_path: Path) -> None:
    with pytest.raises(DecisionPending) as failure:
        prepare_launch(project, RunFlags(), interactive=False)
    message = str(failure.value)
    assert "ide ide: Your IDE for this checkout" in message and "--ide IDE" in message
    assert "Nothing was written" in message
    assert not any(path.name.endswith(".resolved.toml") for path in (tmp_path / "xdg_config_home").rglob("*.toml"))


def test_print_only_never_asks(project: Path) -> None:
    assert config(project, "authorize", "base-image", "default") == 0
    with pytest.raises(DecisionPending):
        prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO("1\n"), print_only=True)


def test_run_once_ide_and_memory_leave_the_record_alone(project: Path) -> None:
    assert config(project, "authorize", "base-image", "default") == 0
    prepared = prepare_launch(project, RunFlags(ide="codium", memory="6g", cpus="2", environment=("A=1", "B")),
                              interactive=False)
    assert prepared.selected.resolution["runtime"]["component"] == "codium"
    assert prepared.memory_override == 6 * 1024**3 and prepared.cpus_override == 2
    assert prepared.environment_tokens == ["--env", "A=1", "--env", "B"]
    assert "capabilities" not in record(project)
    assert "memory" not in record(project).get("configuration", {}).get("values", {})
    assert prepared.selected.resolution_path.is_file()


def test_save_records_the_flags_as_the_checkouts_answers(project: Path) -> None:
    assert config(project, "authorize", "base-image", "default") == 0
    prepared = prepare_launch(project, RunFlags(ide="frontend-ide", agents=("codex",), memory="6g",
                                                environment=("A=1", "B"), authorize=(("network", "host"),), save=True),
                              interactive=False)
    saved = record(project)
    assert saved["capabilities"]["selected"] == ["codex-agent", "frontend-ide"]
    assert saved["configuration"]["values"]["memory"] == "6GiB"
    assert saved["authorization"]["network"]["value"] == "host"
    assert read_arguments(arguments_path(checkout_record_paths(load_toml(paths(project)[0]), project)[0])) == [
        "--env", "B", "--env", "A=1"]
    assert prepared.memory_override is None and prepared.environment_tokens == []
    assert "Recorded the flags given" in prepared.notes[0]


def test_a_second_checkout_is_registered_under_its_directory_name(project: Path, tmp_path: Path) -> None:
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "authorize", "base-image", "default") == 0
    second = tmp_path / "second-copy"
    second.mkdir()
    (second / ".devcapsule").mkdir()
    for name in ("devcapsule.toml", "devcapsule.linux-amd64.lock"):
        (second / ".devcapsule" / name).write_bytes((project / ".devcapsule" / name).read_bytes())
    with pytest.raises(DecisionPending):  # its own record: no IDE; the base's channel is the workstation's question
        prepare_launch(second, RunFlags(), interactive=False)
    prompts = io.StringIO()
    prepared = prepare_launch(second, RunFlags(ide="python-ide", authorize=()), interactive=True,
                              input_stream=io.StringIO("y\n"), output_stream=prompts)
    assert "Accept, once for this computer?" in prompts.getvalue()
    assert load_toml(trust_path())["channels"]["devcapsule-base"]["vendor"]
    names = {item.checkout_name: item.checkout_path for item in registered_checkouts()}
    assert names == {"default": project.resolve(), "second-copy": second.resolve()}
    assert prepared.selected.checkout_path.name == "second-copy.checkout.toml"


def test_interactive_questions_record_answers_where_the_config_family_would(project: Path, capsys) -> None:
    assert config(project, "require", "env", "POSTGRES_HOST", "--because", "the owner's database") == 0
    assert config(project, "recommend", "network", "host", "--because", "ports") == 0
    assert config(project, "recommend", "docker-daemon", "host-socket", "--because", "compose") == 0
    capsys.readouterr()
    prompts = io.StringIO()
    # In listing order: IDE by number; network: once; docker-daemon: deny; the base's channel: yes; env value.
    answers = io.StringIO("3\no\nd\ny\ndb.example.org\n")
    prepared = prepare_launch(project, RunFlags(), interactive=True, input_stream=answers, output_stream=prompts)
    transcript = prompts.getvalue()
    assert "Choose one:" in transcript and "3. frontend-ide" in transcript
    assert "POSTGRES_HOST: the owner's database" in transcript
    assert "db.example.org" not in transcript
    saved = record(project)
    assert saved["capabilities"]["selected"] == ["frontend-ide"]
    assert saved["authorization"]["docker-daemon"]["value"] == "none"
    assert "network" not in saved["authorization"]
    assert prepared.host_overrides == {"network": "host"}
    assert "base-image" not in saved.get("authorization", {})  # the channel is trusted for the workstation, not consented per checkout
    assert "devcapsule-base" in load_toml(trust_path())["channels"]
    assert read_arguments(arguments_path(checkout_record_paths(load_toml(paths(project)[0]), project)[0])) == [
        "--env", "POSTGRES_HOST=db.example.org"]
    assert prepared.selected.resolution["runtime"]["component"] == "codium"


def test_not_now_keeps_the_secure_default_and_asks_again_next_time(project: Path) -> None:
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "authorize", "base-image", "default") == 0
    assert config(project, "recommend", "network", "host", "--because", "ports") == 0
    prompts = io.StringIO()
    prepared = prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO("\n"), output_stream=prompts)
    assert "Not now; the secure default applies" in prompts.getvalue()
    assert prepared.host_overrides == {} and "network" not in record(project).get("authorization", {})
    # Without a terminal the ask is a note, never a stop.
    prepared = prepare_launch(project, RunFlags(), interactive=False)
    assert any("network host" in note and "not granted this run" in note for note in prepared.notes)


def test_a_closed_terminal_mid_question_stops_without_more_writes(project: Path) -> None:
    assert config(project, "authorize", "base-image", "default") == 0
    with pytest.raises(DecisionPending, match="terminal closed"):
        prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO(""), output_stream=io.StringIO())


def test_run_exits_three_and_the_old_resolve_derives(project: Path, capsys) -> None:
    assert cli.main(["project", "--path", str(project), "run", "--print-command"]) == 3
    err = capsys.readouterr().err
    assert "needs answers" in err and "--ide IDE" in err
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "authorize", "base-image", "default") == 0
    capsys.readouterr()
    assert config(project, "resolve") == 0
    captured = capsys.readouterr()
    assert "is gone" in captured.err and "Derived " in captured.out
    assert checkout_record_paths(load_toml(paths(project)[0]), project)[1].is_file()
    from devcapsule.commands.framework import render_command_listing
    from devcapsule.commands.project import ConfigGroup
    assert "  resolve " not in render_command_listing(ConfigGroup.subcommands())


def test_run_help_has_the_flags_and_no_force(capsys) -> None:
    assert cli.main(["project", "run", "--help"]) == 0
    text = capsys.readouterr().out
    for flag in ("--ide", "--agent", "--memory", "--cpus", "--env", "--save", "--print-command"):
        assert flag in text
    assert "--force" not in text
