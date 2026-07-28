"""Capability-first project configuration for the initial PyCharm dogfood slice."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tomllib
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote


from devcapsule.compat import CliError


class ProjectConfigurationError(CliError):
    """An actionable project configuration failure."""


def discover_project(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".devcapsule" / "devcapsule.toml").is_file():
            return directory
    raise ProjectConfigurationError(
        f"No .devcapsule/devcapsule.toml found from {candidate}; run 'devcapsule init'."
    )


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            value = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ProjectConfigurationError(f"Cannot read {path}: {exc}") from exc
    return value


def validate_manifest(value: Mapping[str, Any], path: Path) -> None:
    version = value.get("devcapsule-schema-version")
    if version != 1:
        raise ProjectConfigurationError(
            f"{path} requires devcapsule-schema-version = 1; found {version!r}."
        )
    project = value.get("project")
    capabilities = value.get("capabilities")
    if not isinstance(project, dict) or not all(project.get(key) for key in ("name", "slug", "creator", "mount")):
        raise ProjectConfigurationError(f"{path} must define project name, slug, creator, and mount.")
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("need"), list):
        raise ProjectConfigurationError(f"{path} must define capabilities.need as an array.")


def canonical_digest(value: Mapping[str, Any]) -> str:
    # The V1 schema currently admits only JSON-native TOML values.  Sorting keys
    # and compact UTF-8 encoding is RFC 8785-equivalent for these strings,
    # integers, booleans, arrays, and objects.
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def platform_alias() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    return f"{system}-{architecture}"


def config_root(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    home = Path(values.get("HOME", "~")).expanduser()
    return Path(values.get("XDG_CONFIG_HOME") or home / ".config") / "devcapsule"


def checkout_directory(manifest: Mapping[str, Any], env: Mapping[str, str] | None = None) -> Path:
    project = manifest["project"]
    creator = quote(str(project["creator"]), safe="")
    slug = quote(str(project["slug"]), safe="")
    return config_root(env) / "projects" / creator / slug


def checkout_path(manifest: Mapping[str, Any], env: Mapping[str, str] | None = None) -> Path:
    return checkout_directory(manifest, env) / "devcapsule.checkout.toml"


def resolved_path(manifest: Mapping[str, Any], env: Mapping[str, str] | None = None) -> Path:
    return checkout_directory(manifest, env) / "devcapsule.resolved.toml"


def quote_toml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def atomic_write(path: Path, content: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(content, encoding="utf-8")
    temporary.chmod(mode)
    temporary.replace(path)


def manifest_for(project: Path) -> tuple[Path, dict[str, Any]]:
    root = discover_project(project)
    path = root / ".devcapsule" / "devcapsule.toml"
    value = load_toml(path)
    validate_manifest(value, path)
    return root, value


def lock_for(root: Path, manifest: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    path = root / ".devcapsule" / f"devcapsule.{platform_alias()}.lock"
    if not path.is_file():
        raise ProjectConfigurationError(f"Missing {path}; run 'devcapsule lock' on this platform.")
    value = load_toml(path)
    if value.get("devcapsule-lock-format-version") != 1:
        raise ProjectConfigurationError(f"{path} has an unsupported lock format version.")
    expected = canonical_digest(manifest)
    if value.get("manifest-digest") != expected:
        raise ProjectConfigurationError(f"{path} is stale; run 'devcapsule lock'.")
    return path, value


def render_checkout(
    manifest: Mapping[str, Any], project_root: Path, state: Mapping[str, str], host: Mapping[str, Any]
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
    return "\n".join(lines) + "\n"
