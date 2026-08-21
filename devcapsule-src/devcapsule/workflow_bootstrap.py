"""Install reusable workflow definitions and initialize project-owned state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from importlib.resources import files
from pathlib import Path
import re
import tomllib
from typing import Mapping

from devcapsule.project_configuration import atomic_write


WORKFLOW_TYPES = frozenset({"single-stream", "multiple-streams"})
ASSET_PACKAGE = "devcapsule.assets.project_workflow"
DEFINITION_ASSETS: Mapping[Path, str] = {
    Path("AGENTS.md"): "definition/AGENTS.md",
    Path("WORKFLOW.md"): "definition/WORKFLOW.md",
}
COMMON_TEMPLATES: Mapping[Path, str] = {
    Path("README.md"): "templates/common/README.md.template",
    Path("REQUIREMENTS.md"): "templates/common/REQUIREMENTS.md.template",
    Path("engineering-docs/bugs/_template.md"): "templates/common/bug-template.md.template",
    Path("index.md"): "templates/common/index.md.template",
}
ENGINEERING_DIRECTORIES = (
    "docs",
    "engineering-docs/requirements",
    "engineering-docs/specifications",
    "engineering-docs/decisions",
    "engineering-docs/design-notes",
    "engineering-docs/implementation-notes",
    "engineering-docs/wip",
    "engineering-docs/archive",
    "engineering-docs/bugs",
    "engineering-docs/session-records",
)
GITIGNORE_ENTRIES = (
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    ".Python",
    ".venv/",
    "venv/",
    "env/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".coverage",
    "htmlcov/",
    ".idea/",
)


class WorkflowBootstrapError(ValueError):
    """The project cannot be initialized with a valid workflow instance."""


@dataclass(frozen=True)
class BootstrapReport:
    target: Path
    workflow_type: str
    created: tuple[Path, ...]
    updated: tuple[Path, ...]
    refreshed: tuple[Path, ...]
    preserved: tuple[Path, ...]

    def render(self) -> str:
        lines = [
            f"Bootstrapped {self.workflow_type} DevCapsule workflow in:",
            f"  {self.target}",
        ]
        for heading, paths in (
            ("Created", self.created),
            ("Updated project support file", self.updated),
            ("Refreshed reusable definition", self.refreshed),
            ("Preserved existing", self.preserved),
        ):
            if paths:
                lines.extend([f"{heading}:", *(f"  {path}" for path in paths)])
        return "\n".join(lines)


def bootstrap_project(
    target: Path,
    *,
    refresh_workflow_definition: bool = False,
    today: date | None = None,
) -> BootstrapReport:
    root = target.expanduser().resolve()
    if not root.is_dir():
        raise WorkflowBootstrapError(f"project directory does not exist: {root}")
    workflow_type = project_workflow_type(root)
    requested_date = today or datetime.now(timezone.utc).date()
    start_date = (
        _project_management_start_date(root, requested_date)
        if workflow_type == "multiple-streams"
        else requested_date
    )
    project_name = _project_name(root)
    substitutions = {
        "{{PROJECT_NAME}}": project_name,
        "{{START_DATE}}": start_date.isoformat(),
        "{{WORKSTREAM_INDEX}}": _workstream_index(workflow_type, start_date),
    }

    for directory in ENGINEERING_DIRECTORIES:
        (root / directory).mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    updated: list[Path] = []
    refreshed: list[Path] = []
    preserved: list[Path] = []

    for relative, asset in DEFINITION_ASSETS.items():
        destination = root / relative
        existed = destination.exists()
        if existed and not refresh_workflow_definition:
            preserved.append(relative)
            continue
        content = _asset_text(asset)
        atomic_write(destination, content, mode=0o644)
        (refreshed if existed else created).append(relative)

    for relative, asset in COMMON_TEMPLATES.items():
        destination = root / relative
        if destination.exists():
            preserved.append(relative)
            continue
        content = _render(_asset_text(asset), substitutions)
        if relative == Path("index.md"):
            content = _include_existing_markdown(root, content)
        atomic_write(destination, content, mode=0o644)
        created.append(relative)

    status_path = root / "CURRENT-STATUS.md"
    if status_path.exists():
        preserved.append(Path("CURRENT-STATUS.md"))
    elif workflow_type == "single-stream":
        content = _single_stream_status(root, substitutions)
        atomic_write(status_path, content, mode=0o644)
        created.append(Path("CURRENT-STATUS.md"))
    else:
        content = _render(
            _asset_text("templates/multiple-streams/CURRENT-STATUS.md.template"),
            substitutions,
        )
        atomic_write(status_path, content, mode=0o644)
        created.append(Path("CURRENT-STATUS.md"))

    if workflow_type == "multiple-streams":
        _initialize_project_management(
            root,
            start_date,
            substitutions,
            created=created,
            preserved=preserved,
        )

    _update_gitignore(root, created=created, updated=updated, preserved=preserved)
    return BootstrapReport(
        target=root,
        workflow_type=workflow_type,
        created=tuple(sorted(set(created))),
        updated=tuple(sorted(set(updated))),
        refreshed=tuple(sorted(set(refreshed))),
        preserved=tuple(sorted(set(preserved))),
    )


def project_workflow_type(root: Path) -> str:
    declaration = root / ".devcapsule" / "devcapsule.toml"
    if not declaration.is_file():
        return "single-stream"
    try:
        value = tomllib.loads(declaration.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise WorkflowBootstrapError(f"cannot read {declaration}: {exc}") from exc
    selected = value.get("workflow-type", "single-stream")
    if not isinstance(selected, str) or selected not in WORKFLOW_TYPES:
        raise WorkflowBootstrapError(
            f"{declaration} has invalid workflow-type {selected!r}; expected "
            "'single-stream' or 'multiple-streams'"
        )
    return str(selected)


def _initialize_project_management(
    root: Path,
    start_date: date,
    substitutions: Mapping[str, str],
    *,
    created: list[Path],
    preserved: list[Path],
) -> None:
    workstream = Path("engineering-docs/wip") / (
        f"{start_date.isoformat()}-project-management"
    )
    templates = {
        workstream / "CURRENT-STATUS.md": (
            "templates/multiple-streams/project-management-CURRENT-STATUS.md.template"
        ),
        workstream / "intake/README.md": (
            "templates/multiple-streams/intake-README.md.template"
        ),
        workstream / "intake-dispositions.md": (
            "templates/multiple-streams/intake-dispositions.md.template"
        ),
    }
    for relative, asset in templates.items():
        destination = root / relative
        if destination.exists():
            preserved.append(relative)
            continue
        atomic_write(
            destination,
            _render(_asset_text(asset), substitutions),
            mode=0o644,
        )
        created.append(relative)


def _project_management_start_date(root: Path, fallback: date) -> date:
    candidates = sorted(
        path.parent
        for path in (root / "engineering-docs" / "wip").glob(
            "????-??-??-project-management/CURRENT-STATUS.md"
        )
    )
    if len(candidates) > 1:
        raise WorkflowBootstrapError(
            "multiple project-management workstream handoffs already exist: "
            + ", ".join(str(path.relative_to(root)) for path in candidates)
        )
    if not candidates and (root / "CURRENT-STATUS.md").exists():
        raise WorkflowBootstrapError(
            "multiple-streams project is incompletely initialized: "
            "CURRENT-STATUS.md exists but the reserved project-management "
            "workstream handoff does not"
        )
    if not candidates:
        return fallback
    prefix = candidates[0].name.removesuffix("-project-management")
    try:
        return date.fromisoformat(prefix)
    except ValueError as exc:
        raise WorkflowBootstrapError(
            f"project-management workstream has invalid start date: {prefix!r}"
        ) from exc


def _single_stream_status(root: Path, substitutions: Mapping[str, str]) -> str:
    legacy = _legacy_readme_handoff(root / "README.md")
    if legacy is None:
        return _render(
            _asset_text("templates/single-stream/CURRENT-STATUS.md.template"),
            substitutions,
        )
    _, _, body = legacy.partition("\n")
    return (
        "# Current Status\n\n"
        "Workflow type: `single-stream`\n\n"
        "> Initialized from the pre-WORKFLOW DevCapsule handoff previously kept "
        "in README.md. Maintain this file as the canonical handoff now.\n\n"
        f"{body.lstrip()}"
    )


def _legacy_readme_handoff(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"^## Current State(?: And Next Step)?\s*$", text, flags=re.MULTILINE
    )
    return None if match is None else text[match.start() :].rstrip() + "\n"


def _project_name(root: Path) -> str:
    declaration = root / ".devcapsule" / "devcapsule.toml"
    if declaration.is_file():
        try:
            value = tomllib.loads(declaration.read_text(encoding="utf-8"))
            project = value.get("project")
            if isinstance(project, dict):
                name = project.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
        except (OSError, tomllib.TOMLDecodeError):
            pass
    return root.name


def _workstream_index(workflow_type: str, start_date: date) -> str:
    if workflow_type == "single-stream":
        return ""
    path = f"engineering-docs/wip/{start_date.isoformat()}-project-management/CURRENT-STATUS.md"
    return "## Workstream Handoffs\n\n- [Project management current status](" + path + ")"


def _include_existing_markdown(root: Path, content: str) -> str:
    excluded_parts = {
        ".git",
        ".idea",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
    existing: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if any(part in excluded_parts for part in relative.parts):
            continue
        if f"]({relative.as_posix()})" not in content:
            existing.append(relative)
    if not existing:
        return content
    lines = [
        content.rstrip(),
        "",
        "## Other Existing Documentation",
        "",
        *(f"- [{path.as_posix()}]({path.as_posix()})" for path in sorted(existing)),
        "",
    ]
    return "\n".join(lines)


def _update_gitignore(
    root: Path,
    *,
    created: list[Path],
    updated: list[Path],
    preserved: list[Path],
) -> None:
    relative = Path(".gitignore")
    path = root / relative
    existed = path.exists()
    text = path.read_text(encoding="utf-8") if existed else ""
    lines = text.splitlines()
    missing = [entry for entry in GITIGNORE_ENTRIES if entry not in lines]
    if not missing:
        preserved.append(relative)
        return
    if text and not text.endswith("\n"):
        text += "\n"
    if lines:
        text += "\n"
    text += "# Python / DevCapsule defaults\n" + "\n".join(missing) + "\n"
    atomic_write(path, text, mode=0o644)
    (updated if existed else created).append(relative)


def _asset_text(relative: str) -> str:
    selected = files(ASSET_PACKAGE).joinpath(*relative.split("/"))
    try:
        return selected.read_text(encoding="utf-8")
    except OSError as exc:
        raise WorkflowBootstrapError(
            f"packaged workflow asset is unavailable: {relative}: {exc}"
        ) from exc


def _render(template: str, substitutions: Mapping[str, str]) -> str:
    rendered = template
    for marker, value in substitutions.items():
        rendered = rendered.replace(marker, value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", rendered)))
    if unresolved:
        raise WorkflowBootstrapError(
            "workflow template has unresolved markers: " + ", ".join(unresolved)
        )
    return rendered
