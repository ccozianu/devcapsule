"""Project declaration admission and its configuration-relevant projection."""

from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
from devcapsule.project import normalize_project_mount, ProjectMountError

from .file_formats import ConfigurationFileKind, ProjectConfigurationError, validate_file_format
from .values import configuration_value_declarations
from .capabilities import CapabilityPolicy


def validate_manifest(value: Mapping[str, Any], path: Path) -> None:
    validate_file_format(value, ConfigurationFileKind.manifest, path)
    project = value.get("project")
    if not isinstance(project, dict) or not all(
        isinstance(project.get(key), str) and project[key] and "\x00" not in project[key]
        for key in ("name", "slug", "creator", "mount")
    ):
        raise ProjectConfigurationError(f"{path} must define project name, slug, creator, and mount.")
    try:
        normalize_project_mount(project["mount"], project["slug"])
    except ProjectMountError as exc:
        raise ProjectConfigurationError(f"{path}: {exc}") from exc
    CapabilityPolicy.read(value)
    configuration_value_declarations(value, source=str(path))


def configuration_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """The manifest projection consumed by environment resolution.

    Workflow and descriptive project metadata cannot change a derived runtime.
    Authorization fingerprints are independently scoped to their questions.
    """
    return {
        "devcapsule-schema-version": manifest.get("devcapsule-schema-version"),
        "project": {key: manifest.get("project", {}).get(key) for key in ("creator", "slug", "mount")},
        **{key: manifest.get(key, {}) for key in ("capabilities", "configuration", "host")},
    }
