"""Capability-first project configuration for the initial PyCharm dogfood slice."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote


from devcapsule.compat import CliError


class ProjectConfigurationError(CliError):
    """An actionable project configuration failure."""


CHECKOUT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
OCI_REPOSITORY_COMPONENT_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
OCI_REGISTRY_HOST_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class RegisteredCheckout:
    project_creator: str
    project_slug: str
    checkout_name: str
    checkout_path: Path
    record_path: Path
    status: str


@dataclass(frozen=True)
class ResolvedProject:
    root: Path
    manifest: dict[str, Any]
    lock_path: Path
    lock: dict[str, Any]
    checkout_path: Path
    checkout: dict[str, Any]
    resolution_path: Path
    resolution: dict[str, Any]


def discover_project(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".devcapsule" / "devcapsule.toml").is_file():
            return directory
    raise ProjectConfigurationError(
        f"No .devcapsule/devcapsule.toml found from {candidate}; run 'devcapsule project init'."
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


def checkout_record_paths(
    manifest: Mapping[str, Any],
    project_root: Path,
    env: Mapping[str, str] | None = None,
) -> tuple[Path, Path]:
    """Select the default or named checkout record matching one canonical path."""

    directory = checkout_directory(manifest, env)
    default_input = directory / "devcapsule.checkout.toml"
    matched = find_checkout_record(manifest, project_root, env)
    if matched is not None:
        return matched, resolved_record_path(matched)
    if not default_input.exists():
        return default_input, resolved_record_path(default_input)
    raise ProjectConfigurationError(
        f"Project identity is already registered for another checkout in {directory}; "
        "run 'devcapsule project --path PATH checkout register NAME'."
    )


def find_checkout_record(
    manifest: Mapping[str, Any],
    project_root: Path,
    env: Mapping[str, str] | None = None,
) -> Path | None:
    directory = checkout_directory(manifest, env)
    default_input = directory / "devcapsule.checkout.toml"
    candidates = (default_input, *sorted((directory / "checkouts").glob("*.checkout.toml")))
    expected = project_root.expanduser().resolve()
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            value = load_toml(candidate)
        except ProjectConfigurationError:
            continue
        recorded = value.get("checkout", {}).get("path")
        if recorded and Path(str(recorded)).expanduser().resolve() == expected:
            return candidate
    return None


def named_checkout_record_paths(
    manifest: Mapping[str, Any],
    name: str,
    env: Mapping[str, str] | None = None,
) -> tuple[Path, Path]:
    if not CHECKOUT_NAME_PATTERN.fullmatch(name):
        raise ProjectConfigurationError(
            "Checkout name must start with an alphanumeric character and contain only letters, digits, '.', '_', or '-'."
        )
    input_path = checkout_directory(manifest, env) / "checkouts" / f"{name}.checkout.toml"
    return input_path, resolved_record_path(input_path)


def resolved_record_path(input_path: Path) -> Path:
    if input_path.name == "devcapsule.checkout.toml":
        return input_path.with_name("devcapsule.resolved.toml")
    if input_path.name.endswith(".checkout.toml"):
        return input_path.with_name(f"{input_path.name.removesuffix('.checkout.toml')}.resolved.toml")
    raise ValueError(f"not a DevCapsule checkout record path: {input_path}")


def registered_checkouts(env: Mapping[str, str] | None = None) -> tuple[RegisteredCheckout, ...]:
    """Enumerate valid developer-owned checkout records without scanning source trees."""

    projects_root = config_root(env) / "projects"
    records: list[RegisteredCheckout] = []
    if not projects_root.is_dir():
        return ()
    candidates = sorted(projects_root.rglob("*.checkout.toml"))
    for candidate in candidates:
        try:
            value = load_toml(candidate)
        except ProjectConfigurationError:
            continue
        if value.get("devcapsule-checkout-schema-version") != 1:
            continue
        project = value.get("project")
        checkout = value.get("checkout")
        if not isinstance(project, dict) or not isinstance(checkout, dict):
            continue
        creator = project.get("creator")
        slug = project.get("slug")
        raw_path = checkout.get("path")
        if not creator or not slug or not raw_path:
            continue
        source = Path(str(raw_path)).expanduser()
        name = "default" if candidate.name == "devcapsule.checkout.toml" else candidate.name.removesuffix(
            ".checkout.toml"
        )
        if not source.exists():
            status = "missing"
        elif not (source / ".devcapsule" / "devcapsule.toml").is_file():
            status = "uninitialized"
        else:
            status = "ready"
        records.append(
            RegisteredCheckout(
                project_creator=str(creator),
                project_slug=str(slug),
                checkout_name=name,
                checkout_path=source,
                record_path=candidate,
                status=status,
            )
        )
    return tuple(
        sorted(
            records,
            key=lambda record: (
                record.project_creator,
                record.project_slug,
                record.checkout_name,
                str(record.checkout_path),
            ),
        )
    )


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
        raise ProjectConfigurationError(f"Missing {path}; run 'devcapsule project lock' on this platform.")
    value = load_toml(path)
    if value.get("devcapsule-lock-format-version") != 1:
        raise ProjectConfigurationError(f"{path} has an unsupported lock format version.")
    expected = canonical_digest(manifest)
    if value.get("manifest-digest") != expected:
        raise ProjectConfigurationError(f"{path} is stale; run 'devcapsule project lock'.")
    if "base" in value:
        locked_base_reference(value, source=str(path))
    return path, value


def immutable_registry_reference(reference: str) -> str:
    """Require a globally named OCI repository pinned by one SHA-256 digest."""

    name, separator, digest = reference.rpartition("@sha256:")
    if not separator or not SHA256_PATTERN.fullmatch(digest):
        raise ProjectConfigurationError(
            "Base references in committed locks must end with one immutable @sha256:<64-hex-digest>."
        )
    registry, slash, repository = name.partition("/")
    if not slash or not repository:
        raise ProjectConfigurationError(
            "Base references in committed locks must include an explicit global registry such as docker.io."
        )
    registry_host, colon, port = registry.rpartition(":")
    if not colon:
        registry_host = registry
    elif not port.isdigit():
        raise ProjectConfigurationError("The registry port in a committed base reference must be numeric.")
    normalized_host = registry_host.lower()
    if (
        not OCI_REGISTRY_HOST_PATTERN.fullmatch(normalized_host)
        or ".." in normalized_host
        or "." not in normalized_host
        or normalized_host == "localhost"
        or normalized_host.startswith("127.")
        or normalized_host == "0.0.0.0"
    ):
        raise ProjectConfigurationError(
            "Base references in committed locks must use a globally resolvable registry, not a local daemon name."
        )
    if registry != registry.lower() or repository != repository.lower():
        raise ProjectConfigurationError("Committed base registry and repository names must be lowercase.")
    if ":" in repository or any(
        not OCI_REPOSITORY_COMPONENT_PATTERN.fullmatch(component)
        for component in repository.split("/")
    ):
        raise ProjectConfigurationError(
            "Committed base references must name an OCI repository without a mutable tag."
        )
    return reference


def locked_base_reference(lock: Mapping[str, Any], *, source: str = "platform lock") -> str:
    base = lock.get("base")
    if not isinstance(base, dict):
        raise ProjectConfigurationError(f"{source} does not define formation base inputs.")
    reference = base.get("reference")
    if not isinstance(reference, str) or not reference:
        raise ProjectConfigurationError(f"{source} base.reference must be a non-empty string.")
    try:
        return immutable_registry_reference(reference)
    except ProjectConfigurationError as exc:
        raise ProjectConfigurationError(f"Invalid {source} base.reference {reference!r}: {exc}") from exc


def authorized_base_reference(
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    *,
    required: bool = True,
) -> str | None:
    reference = locked_base_reference(lock)
    authorization_root = checkout.get("authorization")
    authorization = (
        authorization_root.get("base-image") if isinstance(authorization_root, dict) else None
    )
    command = f"devcapsule project config authorize base-image {reference}"
    if not isinstance(authorization, dict):
        if required:
            raise ProjectConfigurationError(
                f"The lock recommends base {reference}, but this checkout has not authorized it; run '{command}'."
            )
        return None
    authorized_reference = authorization.get("reference")
    authorized_lock = authorization.get("lock-digest")
    expected_lock = canonical_digest(lock)
    if authorized_reference != reference or authorized_lock != expected_lock:
        raise ProjectConfigurationError(
            "The checkout's base-image authorization is stale or selects a different artifact; "
            f"review the current lock and run '{command}'."
        )
    return reference


def fresh_resolved_project(project: Path) -> ResolvedProject:
    """Load one checkout and require its generated resolution to be fresh."""

    root, manifest = manifest_for(project)
    lock_path, lock = lock_for(root, manifest)
    checkout_path, resolution_path = checkout_record_paths(manifest, root)
    if not checkout_path.is_file() or not resolution_path.is_file():
        raise ProjectConfigurationError(
            "Local resolution is missing; run 'devcapsule project config resolve'."
        )
    checkout = load_toml(checkout_path)
    resolution = load_toml(resolution_path)
    expected = {
        "manifest": canonical_digest(manifest),
        "platform-lock": canonical_digest(lock),
        "checkout-input": canonical_digest(checkout),
    }
    actual = resolution.get("sources", {})
    stale = [name for name, digest in expected.items() if actual.get(name) != digest]
    if stale:
        raise ProjectConfigurationError(
            f"Local resolution is stale ({', '.join(stale)}); run 'devcapsule project config resolve'."
        )
    return ResolvedProject(
        root=root,
        manifest=manifest,
        lock_path=lock_path,
        lock=lock,
        checkout_path=checkout_path,
        checkout=checkout,
        resolution_path=resolution_path,
        resolution=resolution,
    )


def render_checkout(
    manifest: Mapping[str, Any],
    project_root: Path,
    state: Mapping[str, str],
    host: Mapping[str, Any],
    authorization: Mapping[str, Any] | None = None,
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
    base_authorization = (authorization or {}).get("base-image")
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
    return "\n".join(lines) + "\n"
