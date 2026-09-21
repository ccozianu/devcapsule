"""Admission and lossless writes for versioned configuration documents.

Admission is deliberately weaker than readiness: an understood document can
contain unanswered or invalid nodes which the developer needs to repair.
Unknown representations cannot be repaired by pretending they are version 1.
All released configuration formats are currently version 1; a future decoder
belongs here, with predecessor fixtures demonstrating semantic preservation.
"""

from __future__ import annotations

from enum import Enum
import hashlib
import json
import math
import tomllib
from pathlib import Path
from typing import Any, Mapping, Sequence

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
        selected_version_lock(document)
        # This file is an input, not a plugin extension point. Refusing unknown
        # fields protects both their meaning and their bytes during an edit.
        shapes = {
            (): {artifact.value, "project", "checkout", "configuration", "state", "host", "authorization", "version-set"},
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


ConfigurationScalar = str | int | bool


AuthorizationScalar = str | bool


def canonical_digest(value: Mapping[str, Any]) -> str:
    # The V1 schema currently admits only JSON-native TOML values.  Sorting keys
    # and compact UTF-8 encoding is RFC 8785-equivalent for these strings,
    # integers, booleans, arrays, and objects.
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    except (TypeError, ValueError) as exc:
        raise ProjectConfigurationError("Configuration contains an unsupported scalar representation.") from exc
    return hashlib.sha256(encoded).hexdigest()


def quote_toml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_toml_scalar(value: ConfigurationScalar) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    return quote_toml(value)


def render_checkout(
    manifest: Mapping[str, Any],
    project_root: Path,
    state: Mapping[str, str],
    host: Mapping[str, Any],
    authorization: Mapping[str, Any] | None = None,
    values: Mapping[str, ConfigurationScalar] | None = None,
    host_directory_bindings: Mapping[str, str] | None = None,
    host_environment_bindings: Mapping[str, str] | None = None,
    omitted_values: Sequence[str] | None = None,
) -> str:
    identity = manifest["project"]
    lines = [
        "devcapsule-checkout-schema-version = 1",
        "",
        "[project]",
        f"creator = {quote_toml(str(identity['creator']))}",
        f"slug = {quote_toml(str(identity['slug']))}",
        "",
        "[checkout]",
        f"path = {quote_toml(str(project_root))}",
    ]
    if state:
        lines.extend(["", "[state.adopted]"])
        lines.extend(f"{quote_toml(key)} = {quote_toml(value)}" for key, value in sorted(state.items()))
    if host:
        lines.extend(["", "[host]"])
        for key, value in sorted(host.items()):
            rendered = str(value).lower() if isinstance(value, bool) else quote_toml(str(value))
            lines.append(f"{key} = {rendered}")
    if omitted_values:
        # An explicit 'none' answer (owner ruling 2026-09-03): the name is a
        # recorded decision to keep the node absent from the runtime config —
        # distinct from silence, which follows the project's default.
        rendered_names = ", ".join(quote_toml(name) for name in sorted(set(omitted_values)))
        lines.extend(["", "[configuration]", f"omitted-values = [{rendered_names}]"])
    if values:
        lines.extend(["", "[configuration.values]"])
        lines.extend(
            f"{quote_toml(key)} = {render_toml_scalar(value)}"
            for key, value in sorted(values.items())
        )
    if host_directory_bindings:
        lines.extend(["", "[configuration.bindings.host-directory]"])
        lines.extend(
            f"{quote_toml(key)} = {quote_toml(value)}"
            for key, value in sorted(host_directory_bindings.items())
        )
    if host_environment_bindings:
        lines.extend(["", "[configuration.bindings.host-environment]"])
        lines.extend(
            f"{quote_toml(key)} = {quote_toml(value)}"
            for key, value in sorted(host_environment_bindings.items())
        )
    base_authorization = (authorization or {}).get("base-image")
    for name, record in sorted((authorization or {}).items()):
        if name == "base-image":
            continue
        if not isinstance(record, dict):
            continue
        value = record.get("value")
        recommendation_digest = record.get("recommendation-digest")
        if isinstance(value, (str, bool)) and isinstance(recommendation_digest, str):
            lines.extend(
                [
                    "",
                    f"[authorization.{quote_toml(str(name))}]",
                    f"value = {render_toml_scalar(value)}",
                    f"recommendation-digest = {quote_toml(recommendation_digest)}",
                ]
            )
    if isinstance(base_authorization, dict):
        reference = base_authorization.get("reference")
        lock_digest = base_authorization.get("lock-digest")
        if reference and lock_digest:
            lines.extend(
                [
                    "",
                    "[authorization.base-image]",
                    f"reference = {quote_toml(str(reference))}",
                    f"lock-digest = {quote_toml(str(lock_digest))}",
                ]
            )
            image_identity = base_authorization.get("image-id")
            if image_identity:
                lines.append(f"image-id = {quote_toml(str(image_identity))}")
    return "\n".join(lines) + "\n"


def selected_version_lock(checkout: Mapping[str, Any]) -> dict[str, Any] | None:
    """The complete developer-owned selection; never overlay a moving lock."""
    if "version-set" not in checkout:
        return None
    selection = table(checkout, "version-set")
    if (type(selection.get("format")) is not int or selection["format"] != 1
            or not isinstance(selection.get("lock"), str)
            or not isinstance(selection.get("recommendation-digest"), str)
            or set(selection) != {"format", "lock", "recommendation-digest"}):
        raise ProjectConfigurationError("Unsupported local version-set record; left intact.")
    try:
        lock = tomllib.loads(selection["lock"])
    except tomllib.TOMLDecodeError as exc:
        raise ProjectConfigurationError(f"Malformed local version-set lock: {exc}") from exc
    admit_document(lock, Artifact.lock, "local version set")
    return lock
