"""Check configuration file structure and convert configuration data to TOML.

The four file kinds are project manifests, platform locks, local checkout
settings and saved launch plans. These helpers check format versions and table
structure, produce TOML text, and calculate hashes for detecting changes.
They work on data in memory; storage.py handles reading and writing files.

A valid file format does not mean the configuration is ready to run. Checking
individual settings, installed tools and permissions belongs to other modules.
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


class ConfigurationFileKind(Enum):
    """A configuration file's purpose and the field declaring its format version.

    Each member's value is the TOML key that must contain the version number.
    For example, a platform lock uses ``devcapsule-lock-format-version = 1``.
    """
    manifest = "devcapsule-schema-version"
    lock = "devcapsule-lock-format-version"
    checkout = "devcapsule-checkout-schema-version"
    resolution = "devcapsule-resolved-schema-version"


def table(document: Mapping[str, Any], *path: str) -> Mapping[str, Any]:
    """Return a nested table, or an empty dict if any key along the path is absent.

    For example, ``table(config, "configuration", "values")`` reads
    ``[configuration.values]``. Raise ProjectConfigurationError if an existing
    value along the path is not a table. The result is not copied.
    """
    value: Any = document
    for key in path:
        value = value.get(key, {})
        if not isinstance(value, dict):
            raise ProjectConfigurationError(f"{'.'.join(path)} must be a table.")
    return value


def validate_file_format(document: Mapping[str, Any], file_kind: ConfigurationFileKind, source: object) -> None:
    """Check the version and table structure of parsed configuration data.

    ``file_kind`` selects the expected format; ``source`` identifies the input
    in error messages, usually by path. Raise ProjectConfigurationError for an
    unsupported version or malformed structure. Only version 1 is supported.

    Checkout records also reject unknown fields and check any embedded version
    lock. Saved plans require string source hashes and a supported hash scope.
    Individual setting values and missing answers are checked elsewhere, so
    incomplete settings remain editable.
    This function leaves the input unchanged.
    """
    version = document.get(file_kind.value)
    if type(version) is not int or version != 1:
        raise ProjectConfigurationError(
            f"{source} has an unsupported {file_kind.name} schema version: {version!r}; "
            f"requires {file_kind.value} = 1. The file has not been converted."
        )
    paths = {
        ConfigurationFileKind.manifest: ("project", "capabilities", "configuration.values", "host"),
        ConfigurationFileKind.lock: ("components", "base", "materialization", "image"),
        ConfigurationFileKind.checkout: (
            "project", "checkout", "configuration.values", "configuration.bindings.host-directory",
            "configuration.bindings.host-environment", "state.adopted", "host", "authorization",
        ),
        ConfigurationFileKind.resolution: (
            "sources", "runtime", "configuration.values", "state.adopted", "state.bindings",
            "secret.bindings.host-environment", "host", "authorization",
        ),
    }
    for path in paths[file_kind]:
        try:
            table(document, *path.split("."))
        except ProjectConfigurationError as exc:
            raise ProjectConfigurationError(f"{source}: {exc}") from exc
    if file_kind is ConfigurationFileKind.resolution:
        sources = table(document, "sources")
        if any(not isinstance(value, str) for value in sources.values()):
            raise ProjectConfigurationError(f"{source}: resolution sources must contain string fingerprints.")
        if sources.get("manifest-scope") not in (None, "configuration-v1"):
            raise ProjectConfigurationError(f"{source}: unsupported manifest fingerprint scope; left intact.")
    if file_kind is ConfigurationFileKind.checkout:
        selected_version_lock(document)
        # Refuse fields we cannot interpret so an edit cannot silently drop them.
        shapes = {
            (): {file_kind.value, "project", "checkout", "configuration", "state", "host", "authorization", "version-set", "capabilities"},
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


def render_toml(document: Mapping[str, Any]) -> str:
    """Return TOML text containing every supplied field, with keys sorted.

    Preserve values even when they are invalid answers to configuration
    questions, so correcting one setting does not erase another. Formatting
    is regenerated; comments are not preserved. Raise ProjectConfigurationError
    for unsupported value types. This neither validates settings nor writes files.
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
    """Return a SHA-256 hex digest for detecting changes in configuration values.

    Hash compact UTF-8 JSON with sorted keys, so dictionary insertion order
    does not affect the result. Raise ProjectConfigurationError if JSON
    encoding fails. This does not check the configuration's file format.
    """
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    except (TypeError, ValueError) as exc:
        raise ProjectConfigurationError("Configuration contains an unsupported scalar representation.") from exc
    return hashlib.sha256(encoded).hexdigest()


def quote_toml(value: str) -> str:
    """Return a quoted TOML string, escaping quotes and control characters."""
    return json.dumps(value, ensure_ascii=False)


def render_toml_scalar(value: ConfigurationScalar) -> str:
    """Return TOML text for a string, integer or boolean configuration value."""
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
    """Build a new checkout record as TOML, without writing it to disk.

    Copy creator/slug from ``manifest`` and record ``project_root`` as the
    checkout path. ``state`` maps state slots to directories; ``host`` holds
    legacy host settings; ``authorization`` holds recorded permission answers.
    ``values`` holds setting overrides. The two binding maps associate resource
    names with host directories or environment variables. ``omitted_values``
    names settings whose project defaults the developer has explicitly disabled.

    This builds a record from the supplied fields. To edit an existing record,
    update its parsed mapping and use ``render_toml`` to retain unrelated fields.
    """
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
        # These settings were explicitly disabled; do not use project defaults.
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
    """Read the software versions explicitly pinned in this checkout.

    Return None when the checkout follows project versions. Otherwise parse
    its embedded TOML lock into a new dict and validate the lock's format.
    Raise ProjectConfigurationError for an invalid selection record or lock.
    The returned selection replaces the shared lock; callers must not fill
    missing entries from newer project recommendations.
    """
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
    validate_file_format(lock, ConfigurationFileKind.lock, "local version set")
    return lock
