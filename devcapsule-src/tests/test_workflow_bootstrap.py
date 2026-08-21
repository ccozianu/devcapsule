from __future__ import annotations

from datetime import date
from importlib.resources import files
from pathlib import Path

import pytest

from devcapsule.workflow_bootstrap import (
    WorkflowBootstrapError,
    bootstrap_project,
    project_workflow_type,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def declaration(root: Path, workflow_type: str | None = None) -> None:
    config = root / ".devcapsule" / "devcapsule.toml"
    config.parent.mkdir(parents=True)
    selected = "" if workflow_type is None else f'workflow-type = "{workflow_type}"\n'
    config.write_text(
        selected + '[project]\nname = "Example Project"\nslug = "example"\n',
        encoding="utf-8",
    )


def test_packaged_workflow_is_the_root_reusable_definition() -> None:
    packaged = (
        files("devcapsule.assets.project_workflow")
        .joinpath("definition", "WORKFLOW.md")
        .read_text(encoding="utf-8")
    )

    assert packaged == (REPO_ROOT / "WORKFLOW.md").read_text(encoding="utf-8")


def test_single_stream_bootstrap_installs_definition_and_instance(tmp_path: Path) -> None:
    declaration(tmp_path)
    existing = tmp_path / "engineering-docs" / "design-notes" / "idea.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# Existing idea\n", encoding="utf-8")

    report = bootstrap_project(tmp_path, today=date(2026, 8, 21))

    assert report.workflow_type == "single-stream"
    assert (tmp_path / "WORKFLOW.md").is_file()
    assert "Read `WORKFLOW.md`" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    status = (tmp_path / "CURRENT-STATUS.md").read_text(encoding="utf-8")
    assert "Workflow type: `single-stream`" in status
    assert "Initial project orientation" in status
    assert "Example Project" in (tmp_path / "README.md").read_text(encoding="utf-8")
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "Reusable human/agent workflow" in index
    assert "engineering-docs/design-notes/idea.md" in index
    assert (tmp_path / "engineering-docs" / "wip").is_dir()
    assert (tmp_path / "engineering-docs" / "archive").is_dir()
    assert ".idea/" in (tmp_path / ".gitignore").read_text(encoding="utf-8")


def test_existing_project_state_is_preserved_and_legacy_handoff_is_migrated(
    tmp_path: Path,
) -> None:
    declaration(tmp_path)
    readme = "# Existing\n\n## Current State And Next Step\n\nCurrent stage: Research.\n"
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("custom agent rules\n", encoding="utf-8")

    first = bootstrap_project(tmp_path, today=date(2026, 8, 21))

    assert Path("AGENTS.md") in first.preserved
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "custom agent rules\n"
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == readme
    status = (tmp_path / "CURRENT-STATUS.md").read_text(encoding="utf-8")
    assert "Initialized from the pre-WORKFLOW DevCapsule handoff" in status
    assert "Current stage: Research." in status

    second = bootstrap_project(
        tmp_path,
        refresh_workflow_definition=True,
        today=date(2026, 8, 21),
    )

    assert Path("AGENTS.md") in second.refreshed
    assert "Read `WORKFLOW.md`" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert (tmp_path / "CURRENT-STATUS.md").read_text(encoding="utf-8") == status
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == readme


def test_multiple_streams_bootstrap_initializes_reserved_workstream(
    tmp_path: Path,
) -> None:
    declaration(tmp_path, "multiple-streams")

    report = bootstrap_project(tmp_path, today=date(2026, 8, 21))

    assert report.workflow_type == "multiple-streams"
    registry = (tmp_path / "CURRENT-STATUS.md").read_text(encoding="utf-8")
    assert "`project-management`" in registry
    handoff_root = tmp_path / "engineering-docs/wip/2026-08-21-project-management"
    assert (handoff_root / "CURRENT-STATUS.md").is_file()
    assert (handoff_root / "intake/README.md").is_file()
    assert (handoff_root / "intake-dispositions.md").is_file()
    assert "Project management current status" in (tmp_path / "index.md").read_text(
        encoding="utf-8"
    )

    repeated = bootstrap_project(tmp_path, today=date(2030, 1, 1))
    assert not repeated.created
    assert handoff_root.is_dir()
    assert not (tmp_path / "engineering-docs/wip/2030-01-01-project-management").exists()


def test_incomplete_existing_multiple_streams_instance_is_rejected(
    tmp_path: Path,
) -> None:
    declaration(tmp_path, "multiple-streams")
    (tmp_path / "CURRENT-STATUS.md").write_text(
        "# Existing registry without project management\n", encoding="utf-8"
    )

    with pytest.raises(WorkflowBootstrapError, match="incompletely initialized"):
        bootstrap_project(tmp_path, today=date(2026, 8, 21))

    assert not (tmp_path / "WORKFLOW.md").exists()


def test_invalid_declared_workflow_type_fails_before_writing(tmp_path: Path) -> None:
    declaration(tmp_path, "parallel-magic")

    with pytest.raises(WorkflowBootstrapError, match="invalid workflow-type"):
        bootstrap_project(tmp_path)

    assert not (tmp_path / "WORKFLOW.md").exists()


def test_missing_workflow_type_means_single_stream(tmp_path: Path) -> None:
    declaration(tmp_path)
    assert project_workflow_type(tmp_path) == "single-stream"
