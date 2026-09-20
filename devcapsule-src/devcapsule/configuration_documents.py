"""Admission and lossless writes for versioned configuration documents.

Admission is deliberately weaker than readiness: an understood document can
contain unanswered or invalid nodes which the developer needs to repair.
Unknown representations cannot be repaired by pretending they are version 1.
All released configuration formats are currently version 1; a future decoder
belongs here, with predecessor fixtures demonstrating semantic preservation.
"""

from __future__ import annotations

from enum import Enum
import json
import math
from typing import Any, Mapping

from devcapsule.compat import CliError


class ProjectConfigurationError(CliError):
    """An actionable project configuration failure."""


class Artifact(Enum):
    manifest = "devcapsule-schema-version"
    lock = "devcapsule-lock-format-version"
    checkout = "devcapsule-checkout-schema-version"
    resolution = "devcapsule-resolved-schema-version"


def table(document: Mapping[str, Any], *path: str) -> Mapping[str, Any]:
    """Read an optional table without conflating absence and a malformed value."""
    value: Any = document
    for key in path:
        value = value.get(key, {})
        if not isinstance(value, dict):
            raise ProjectConfigurationError(f"{'.'.join(path)} must be a table.")
    return value


def admit_document(document: Mapping[str, Any], artifact: Artifact, source: object) -> None:
    version = document.get(artifact.value)
    if type(version) is not int or version != 1:
        raise ProjectConfigurationError(
            f"{source} has an unsupported {artifact.name} schema version: {version!r}; "
            f"requires {artifact.value} = 1. The file has not been converted."
        )
    paths = {
        Artifact.manifest: ("project", "capabilities", "configuration.values", "host"),
        Artifact.lock: ("components", "base", "materialization", "image"),
        Artifact.checkout: (
            "project", "checkout", "configuration.values", "configuration.bindings.host-directory",
            "configuration.bindings.host-environment", "state.adopted", "host", "authorization",
        ),
        Artifact.resolution: (
            "sources", "runtime", "configuration.values", "state.adopted", "state.bindings",
            "secret.bindings.host-environment", "host", "authorization",
        ),
    }
    for path in paths[artifact]:
        try:
            table(document, *path.split("."))
        except ProjectConfigurationError as exc:
            raise ProjectConfigurationError(f"{source}: {exc}") from exc
    if artifact is Artifact.resolution:
        sources = table(document, "sources")
        if any(not isinstance(value, str) for value in sources.values()):
            raise ProjectConfigurationError(f"{source}: resolution sources must contain string fingerprints.")
        if sources.get("manifest-scope") not in (None, "configuration-v1"):
            raise ProjectConfigurationError(f"{source}: unsupported manifest fingerprint scope; left intact.")
    if artifact is Artifact.checkout:
        # This file is an input, not a plugin extension point. Refusing unknown
        # fields protects both their meaning and their bytes during an edit.
        shapes = {
            (): {artifact.value, "project", "checkout", "configuration", "state", "host", "authorization"},
            ("project",): {"creator", "slug"},
            ("checkout",): {"path"},
            ("configuration",): {"values", "omitted-values", "bindings"},
            ("configuration", "bindings"): {"host-directory", "host-environment"},
            ("state",): {"adopted"},
        }
        for field_path, allowed in shapes.items():
            unknown = set(table(document, *field_path)) - allowed
            if unknown:
                names = ", ".join(".".join((*field_path, key)) for key in sorted(unknown))
                raise ProjectConfigurationError(f"{source}: unsupported checkout fields: {names}; left intact.")


def render_document(document: Mapping[str, Any]) -> str:
    """Serialize the entire admitted input, never a projection of its answers.

    Unlike the former specialized checkout writer, even an invalid answer is
    retained when a different node is repaired. Unsupported scalar encodings
    fail before the atomic write. Comments/formatting are not semantic input.
    """
    def scalar(value: Any) -> str:
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return repr(value) if math.isfinite(value) else str(value)
        if isinstance(value, list):
            return "[" + ", ".join(scalar(item) for item in value) + "]"
        if isinstance(value, dict):
            return "{ " + ", ".join(f"{scalar(k)} = {scalar(v)}" for k, v in sorted(value.items())) + " }"
        raise ProjectConfigurationError(f"Unsupported checkout scalar type {type(value).__name__}; left intact.")

    lines: list[str] = []

    def emit(value: Mapping[str, Any], path: tuple[str, ...]) -> None:
        if path:
            lines.extend(["", "[" + ".".join(scalar(key) for key in path) + "]"])
        for key, item in sorted(value.items()):
            if not isinstance(item, dict):
                lines.append(f"{scalar(key)} = {scalar(item)}")
        for key, item in sorted(value.items()):
            if isinstance(item, dict):
                emit(item, (*path, key))

    emit(document, ())
    return "\n".join(lines) + "\n"
