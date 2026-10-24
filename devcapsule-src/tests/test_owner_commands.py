"""The owner's commands: require, offer, drop and recommend, over the one manifest writer."""

from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from devcapsule import cli
from devcapsule.configuration import owner_commands
from devcapsule.configuration.capability_commands import paths
from devcapsule.configuration.file_formats import ProjectConfigurationError, render_toml
from devcapsule.configuration.storage import load_toml
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES

MATRIX = MATRICES[Platform.LINUX_AMD64]


def identity() -> dict:
    return {"creator": "mailto:owner@example.test", "slug": "sample", "name": "Sample", "mount": "/workspace/sample"}


@pytest.fixture
def legacy_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A 0.2.x project: schema 1, ``need`` with the IDE inside, a lock holding the IDE."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    root = tmp_path / "legacy"
    (root / ".devcapsule").mkdir(parents=True)
    (root / ".devcapsule/devcapsule.toml").write_text(
        "# The owner's note\n\n" + render_toml({"devcapsule-schema-version": 1, "project": identity(),
                                               "capabilities": {"need": ["python", "python-ide"]}})
    )
    (root / ".devcapsule/devcapsule.linux-amd64.lock").write_text(MATRIX.resolve(["python", "python-ide"]).render_lock())
    return root


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A project in the required form, created by init without an IDE."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["project", "--path", str(root), "init", "--require", "python=3", "--creator", "mailto:owner@example.test"]) == 0
    return root


def manifest_text(root: Path) -> str:
    return paths(root)[0].read_text()


def test_require_tool_adds_regenerates_the_lock_and_writes_schema_two(project: Path, capsys) -> None:
    assert cli.main(["project", "--path", str(project), "config", "require", "tool", "node", "postgresql-client",
                     "--because", "the API and its database"]) == 0
    out = capsys.readouterr().out
    assert "Required node, postgresql-client" in out and "Required: node postgresql-client python" in out
    manifest = load_toml(paths(project)[0])
    assert manifest["devcapsule-schema-version"] == 2
    assert manifest["capabilities"] == {"required": ["node", "postgresql-client", "python"], "sdk-major": {"python": 3},
                                        "reasons": {"node": "the API and its database", "postgresql-client": "the API and its database"}}
    lock = load_toml(paths(project)[1])
    assert "postgresql-client" in lock["components"] and "interactive-surface" not in lock["components"]
    text = manifest_text(project)
    assert "[capabilities]\nrequired = [" in text and '"required"' not in text


def test_require_tool_with_major_and_drop_removes_the_major_too(project: Path) -> None:
    owner_commands.require_tools(project, ["dotnet=10"])
    manifest = load_toml(paths(project)[0])
    assert manifest["capabilities"]["sdk-major"] == {"dotnet": 10, "python": 3}
    owner_commands.drop_tools(project, ["dotnet", "python"])
    manifest = load_toml(paths(project)[0])
    assert manifest["capabilities"] == {"required": []}
    with pytest.raises(ProjectConfigurationError, match="Not declared"):
        owner_commands.drop_tools(project, ["python"])


def test_offer_moves_a_tool_out_of_required_and_drops_its_major(project: Path) -> None:
    owner_commands.offer_tools(project, ["browser-automation"], because="end-to-end tests")
    manifest = load_toml(paths(project)[0])
    assert manifest["capabilities"]["optional"] == ["browser-automation"]
    assert manifest["capabilities"]["reasons"] == {"browser-automation": "end-to-end tests"}
    with pytest.raises(ProjectConfigurationError, match="SDK major applies to a required tool"):
        owner_commands.offer_tools(project, ["python=3"])
    owner_commands.offer_tools(project, ["python"])
    assert load_toml(paths(project)[0])["capabilities"] == {"optional": ["browser-automation", "python"], "required": [],
                                                            "reasons": {"browser-automation": "end-to-end tests"}}


@pytest.mark.parametrize("name", ["frontend-ide", "codex-agent", "pycharm", "codex"])
def test_ide_and_agent_names_are_refused_as_project_tools(project: Path, name: str) -> None:
    before = manifest_text(project)
    with pytest.raises(ProjectConfigurationError, match="each developer's"):
        owner_commands.require_tools(project, [name])
    assert manifest_text(project) == before


def test_a_sole_provider_component_id_names_its_tool(project: Path) -> None:
    owner_commands.offer_tools(project, ["playwright"])
    assert load_toml(paths(project)[0])["capabilities"]["optional"] == ["browser-automation"]
    with pytest.raises(ProjectConfigurationError, match="Unknown tool 'nodejs'"):
        owner_commands.require_tools(project, ["nodejs"])


def test_preview_writes_nothing(project: Path) -> None:
    before = {path: path.read_bytes() for path in (project / ".devcapsule").iterdir()}
    assert owner_commands.require_tools(project, ["node"], preview=True).startswith("Preview")
    assert owner_commands.require_environment(project, ["X"], preview=True).startswith("Preview")
    assert owner_commands.recommend(project, "memory", "6g", preview=True).startswith("Preview")
    assert {path: path.read_bytes() for path in (project / ".devcapsule").iterdir()} == before


def test_environment_require_offer_drop_with_reasons(project: Path, capsys) -> None:
    lock_before = paths(project)[1].read_bytes()
    assert cli.main(["project", "--path", str(project), "config", "require", "env", "POSTGRES_HOST", "POSTGRES_PASSWORD",
                     "--because", "the owner supplies the database"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "offer", "env", "SMTP_HOST"]) == 0
    out = capsys.readouterr().out
    assert "Required environment: POSTGRES_HOST (the owner supplies the database), POSTGRES_PASSWORD (the owner supplies the database)" in out
    assert "config env NAME" in out
    manifest = load_toml(paths(project)[0])
    assert manifest["environment"] == {"required": {"POSTGRES_HOST": {"reason": "the owner supplies the database"},
                                                    "POSTGRES_PASSWORD": {"reason": "the owner supplies the database"}},
                                       "optional": {"SMTP_HOST": {}}}
    assert paths(project)[1].read_bytes() == lock_before, "an environment edit leaves the lock's bytes alone"
    # Offering a required name moves it and keeps its reason; dropping removes it.
    owner_commands.offer_environment(project, ["POSTGRES_PASSWORD"])
    manifest = load_toml(paths(project)[0])
    assert manifest["environment"]["optional"]["POSTGRES_PASSWORD"] == {"reason": "the owner supplies the database"}
    owner_commands.drop_environment(project, ["POSTGRES_HOST", "POSTGRES_PASSWORD", "SMTP_HOST"])
    assert "environment" not in load_toml(paths(project)[0])
    with pytest.raises(ProjectConfigurationError, match="Not declared"):
        owner_commands.drop_environment(project, ["SMTP_HOST"])
    with pytest.raises(ProjectConfigurationError, match="ASCII identifiers"):
        owner_commands.require_environment(project, ["POSTGRES-HOST"])


def test_recommend_ide_memory_cpus_and_none(project: Path, capsys) -> None:
    assert cli.main(["project", "--path", str(project), "config", "recommend", "ide", "codium"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "recommend", "memory", "6G", "--because", "the index"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "recommend", "cpus", "4"]) == 0
    out = capsys.readouterr().out
    assert "Recommended ide = frontend-ide" in out and "Recommended memory = 6GiB" in out
    manifest = load_toml(paths(project)[0])
    assert manifest["recommendations"] == {"ide": "frontend-ide", "memory": "6GiB", "cpus": 4, "reasons": {"memory": "the index"}}
    owner_commands.recommend(project, "memory", "none")
    assert load_toml(paths(project)[0])["recommendations"] == {"ide": "frontend-ide", "cpus": 4}
    with pytest.raises(ProjectConfigurationError, match="recommends no memory"):
        owner_commands.recommend(project, "memory", "none")
    with pytest.raises(ProjectConfigurationError, match="Unknown IDE"):
        owner_commands.recommend(project, "ide", "emacs")
    with pytest.raises(ProjectConfigurationError, match="positive integer"):
        owner_commands.recommend(project, "cpus", "two")
    with pytest.raises(ProjectConfigurationError, match="Unknown recommendation"):
        owner_commands.recommend(project, "swap", "1g")


def test_recommend_host_access_needs_the_reason_and_writes_the_curated_table(project: Path) -> None:
    with pytest.raises(ProjectConfigurationError, match="--because"):
        owner_commands.recommend(project, "network", "host")
    with pytest.raises(ProjectConfigurationError, match="accepts exactly 'host'"):
        owner_commands.recommend(project, "network", "bridge", because="x")
    owner_commands.recommend(project, "network", "host", because="the dev servers share localhost")
    owner_commands.recommend(project, "development-sudo", "true", because="apt in the capsule")
    manifest = load_toml(paths(project)[0])
    assert manifest["host"] == {
        "network": {"mode": {"recommended": {"value": "host", "justification": "the dev servers share localhost"}}},
        "privilege": {"development-sudo": {"recommended": {"value": True, "justification": "apt in the capsule"}}},
    }
    owner_commands.recommend(project, "network", "none")
    assert load_toml(paths(project)[0])["host"] == {
        "privilege": {"development-sudo": {"recommended": {"value": True, "justification": "apt in the capsule"}}},
    }
    owner_commands.recommend(project, "development-sudo", "none")
    assert "host" not in load_toml(paths(project)[0])


def test_an_owner_edit_converts_a_legacy_manifest_and_keeps_its_leading_comment(legacy_project: Path) -> None:
    owner_commands.require_tools(legacy_project, ["node"])
    text = manifest_text(legacy_project)
    assert text.startswith("# The owner's note\n\ndevcapsule-schema-version = 2\n")
    manifest = tomllib.loads(text)
    assert "need" not in manifest["capabilities"]
    # The legacy IDE in ``need`` is grandfathered as a requirement; the lock keeps it.
    assert manifest["capabilities"]["required"] == ["node", "python", "python-ide"]
    assert load_toml(paths(legacy_project)[1])["components"]["interactive-surface"] == "pycharm"


def test_an_unrelated_command_never_rewrites_a_legacy_manifest(legacy_project: Path) -> None:
    before = manifest_text(legacy_project)
    assert cli.main(["project", "--path", str(legacy_project), "config", "check"]) == 0
    assert cli.main(["project", "--path", str(legacy_project), "config", "capabilities", "--local", "python-ide"]) == 0
    assert manifest_text(legacy_project) == before


def test_retired_spellings_name_their_replacement(project: Path, capsys) -> None:
    assert cli.main(["project", "--path", str(project), "config", "need", "node"]) == 2
    assert "config require tool node" in capsys.readouterr().err
    assert cli.main(["project", "--path", str(project), "config", "capabilities", "--required", "node"]) == 2
    assert "config require tool" in capsys.readouterr().err
    assert "need" not in cli.main.__module__ or True  # the hidden alias is not listed
    from devcapsule.commands.framework import render_command_listing
    from devcapsule.commands.project import ConfigGroup
    assert " need " not in render_command_listing(ConfigGroup.subcommands())
