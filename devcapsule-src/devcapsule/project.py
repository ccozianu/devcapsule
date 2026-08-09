"""Project path planning helpers for DevCapsule launchers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


class ProjectMountError(ValueError):
    """Raised when an in-container project mount path is invalid."""


RESERVED_PROJECT_MOUNT_ROOTS = frozenset(
    {
        "/",
        "/dev",
        "/etc",
        "/home",
        "/ide-global-settings",
        "/ide-plugins",
        "/ide-project-state",
        "/opt",
        "/proc",
        "/run",
        "/sys",
        "/tmp",
        "/usr",
        "/var",
    }
)


@dataclass(frozen=True)
class ProjectPlan:
    """Resolved project identity and in-container mount path."""

    project_path: Path
    project_id: str
    project_mount: str


def sanitize_name(value: str) -> str:
    """Match the shell launcher's project-name sanitization rules."""

    sanitized = "".join(char if _is_safe_name_char(char) else "-" for char in value)
    sanitized = sanitized.strip("-")
    return sanitized or "project"


def project_namespace(project_path: str | Path) -> str:
    """Return the stable project namespace used by the PyCharm launcher."""

    path_text = str(project_path)
    safe_base = sanitize_name(Path(path_text).name)
    digest = hashlib.sha256(path_text.encode()).hexdigest()[:12]
    return f"{digest}-{safe_base}"


def default_project_mount(project_id: str) -> str:
    return f"/workspace/{project_id}"


def normalize_project_mount(project_mount: str | None, project_id: str) -> str:
    """Return a validated in-container project mount path."""

    mount = project_mount or default_project_mount(project_id)
    if mount != "/":
        mount = mount.removesuffix("/")

    if not mount.startswith("/"):
        raise ProjectMountError("--project-mount must be an absolute in-container path.")
    if is_reserved_project_mount(mount):
        raise ProjectMountError(f"--project-mount uses a reserved container path: {mount}")

    return mount


def is_reserved_project_mount(project_mount: str) -> bool:
    return any(
        project_mount == root or project_mount.startswith(f"{root}/")
        for root in RESERVED_PROJECT_MOUNT_ROOTS
    )


def plan_project(project_path: str | Path, project_mount: str | None = None) -> ProjectPlan:
    """Resolve project launcher identity without touching Docker."""

    resolved_project_path = Path(project_path).expanduser().resolve(strict=False)
    project_id = project_namespace(resolved_project_path)
    return ProjectPlan(
        project_path=resolved_project_path,
        project_id=project_id,
        project_mount=normalize_project_mount(project_mount, project_id),
    )


def _is_safe_name_char(char: str) -> bool:
    return char.isascii() and (char.isalnum() or char in "._-")
