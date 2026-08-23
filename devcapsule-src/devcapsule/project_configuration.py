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
from devcapsule.components.catalog import (
    ComponentCatalogError,
    selected_component_definitions,
    selected_runtime_templates,
)
from devcapsule.components.claude_code import (
    CLAUDE_CODE_AUTHORIZATION,
    CLAUDE_CODE_TERMS_URL,
)


class ProjectConfigurationError(CliError):
    """An actionable project configuration failure."""


CHECKOUT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
OCI_REPOSITORY_COMPONENT_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
OCI_REGISTRY_HOST_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
CONFIGURATION_VALUE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
MEMORY_SIZE_PATTERN = re.compile(r"^([1-9][0-9]*)(B|KiB|MiB|GiB|TiB)$")
RELEASE_BUILD_MNEMONIC_PATTERN = re.compile(r"^v[0-9][0-9A-Za-z._-]*$")
CONFIGURATION_VALUE_TYPES = {"string", "integer", "boolean", "memory-size"}
RUNTIME_EFFECT_TYPES = {"docker.memory-limit": "memory-size"}

ConfigurationScalar = str | int | bool
AuthorizationScalar = str | bool


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


@dataclass(frozen=True)
class ConfigurationBindingDeclaration:
    name: str
    container_path: str
    sensitivity: str
    concurrent: bool
    description: str
    kind: str
    component_id: str | None = None
    slot_name: str | None = None


@dataclass(frozen=True)
class AuthorizationDeclaration:
    name: str
    recommended_value: AuthorizationScalar
    recommendation_digest: str
    description: str
    display_value: str | None = None


@dataclass(frozen=True)
class AuthorizedBaseSelection:
    """Developer-approved base bound to the current lock and optional local image ID."""

    reference: str
    lock_digest: str
    local_image_identity: str | None = None

    @property
    def is_local(self) -> bool:
        return self.local_image_identity is not None


@dataclass(frozen=True)
class SecretInputMetadata:
    name: str
    environment_variable: str
    required: bool
    description: str
    exposure: str


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
    configuration_value_declarations(value, source=str(path))


def configuration_value_declarations(
    manifest: Mapping[str, Any], *, source: str = "project declaration"
) -> dict[str, Mapping[str, Any]]:
    """Return and validate ordinary configuration-value metadata."""

    configuration = manifest.get("configuration")
    if configuration is None:
        return {}
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError(f"{source} configuration must be a table.")
    values = configuration.get("values", {})
    if not isinstance(values, dict):
        raise ProjectConfigurationError(f"{source} configuration.values must be a table.")

    declarations: dict[str, Mapping[str, Any]] = {}
    for name, declaration in values.items():
        field = f"{source} configuration.values.{name}"
        if not isinstance(name, str) or CONFIGURATION_VALUE_NAME_PATTERN.fullmatch(name) is None:
            raise ProjectConfigurationError(
                f"{source} configuration value names must be lowercase dotted or hyphenated identifiers; "
                f"found {name!r}."
            )
        if not isinstance(declaration, dict):
            raise ProjectConfigurationError(f"{field} must be a table.")
        value_type = declaration.get("type")
        if value_type not in CONFIGURATION_VALUE_TYPES:
            choices = ", ".join(sorted(CONFIGURATION_VALUE_TYPES))
            raise ProjectConfigurationError(f"{field}.type must be one of: {choices}.")
        required = declaration.get("required", False)
        if not isinstance(required, bool):
            raise ProjectConfigurationError(f"{field}.required must be a boolean when present.")
        description = declaration.get("description")
        if description is not None and not isinstance(description, str):
            raise ProjectConfigurationError(f"{field}.description must be a string when present.")
        effect = declaration.get("runtime-effect")
        if effect is not None:
            expected_type = RUNTIME_EFFECT_TYPES.get(effect) if isinstance(effect, str) else None
            if expected_type is None:
                choices = ", ".join(sorted(RUNTIME_EFFECT_TYPES))
                raise ProjectConfigurationError(f"{field}.runtime-effect must be one of: {choices}.")
            if value_type != expected_type:
                raise ProjectConfigurationError(
                    f"{field}.runtime-effect {effect!r} requires type {expected_type!r}."
                )
        declarations[name] = declaration
    return declarations


def normalize_configuration_value(
    manifest: Mapping[str, Any], name: str, value: object
) -> ConfigurationScalar:
    declarations = configuration_value_declarations(manifest)
    declaration = declarations.get(name)
    if declaration is None:
        available = ", ".join(sorted(declarations)) or "none"
        raise ProjectConfigurationError(
            f"Configuration value {name!r} is not declared by this project; declared values: {available}."
        )
    value_type = str(declaration["type"])
    field = f"configuration value {name!r}"
    if value_type == "string":
        if not isinstance(value, str) or not value or "\x00" in value:
            raise ProjectConfigurationError(f"{field} must be a non-empty string.")
        return value
    if value_type == "integer":
        if isinstance(value, bool):
            raise ProjectConfigurationError(f"{field} must be an integer.")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and re.fullmatch(r"-?[0-9]+", value):
            return int(value)
        raise ProjectConfigurationError(f"{field} must be an integer.")
    if value_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            return value.lower() == "true"
        raise ProjectConfigurationError(f"{field} must be true or false.")
    if not isinstance(value, str) or MEMORY_SIZE_PATTERN.fullmatch(value) is None:
        raise ProjectConfigurationError(
            f"{field} must be a positive memory size using B, KiB, MiB, GiB, or TiB, for example 8GiB."
        )
    return value


def resolve_configuration_values(
    manifest: Mapping[str, Any], checkout: Mapping[str, Any]
) -> tuple[dict[str, ConfigurationScalar], dict[str, int]]:
    """Validate checkout values and derive curated runtime effects from metadata."""

    declarations = configuration_value_declarations(manifest)
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    raw_values = configuration.get("values", {})
    if not isinstance(raw_values, dict):
        raise ProjectConfigurationError("Checkout configuration.values must be a table.")

    normalized: dict[str, ConfigurationScalar] = {}
    effects: dict[str, int] = {}
    for name, value in raw_values.items():
        if not isinstance(name, str):
            raise ProjectConfigurationError("Checkout configuration value names must be strings.")
        normalized[name] = normalize_configuration_value(manifest, name, value)
    missing = sorted(
        name
        for name, declaration in declarations.items()
        if declaration.get("required", False) and name not in normalized
    )
    if missing:
        commands = ", ".join(f"project config set {name} VALUE" for name in missing)
        raise ProjectConfigurationError(f"Required configuration values are missing: {commands}.")

    for name, value in normalized.items():
        effect = declarations[name].get("runtime-effect")
        if effect == "docker.memory-limit":
            effects["memory-limit-bytes"] = memory_size_bytes(str(value))
    return normalized, effects


def configuration_binding_declarations(
    lock: Mapping[str, Any], *, source: str = "platform lock"
) -> dict[str, ConfigurationBindingDeclaration]:
    """Return logical host-directory targets from the locked component metadata."""

    components = lock.get("components")
    if not isinstance(components, dict):
        raise ProjectConfigurationError(f"{source} components must be a table.")
    try:
        interactive, ancillary = selected_runtime_templates(lock)
    except ComponentCatalogError as exc:
        raise ProjectConfigurationError(str(exc)) from exc
    declarations = {
        "home": ConfigurationBindingDeclaration(
            name="home",
            container_path="/home/devcapsule",
            sensitivity="credentials",
            concurrent=False,
            description="Persistent container home, including developer and tool state.",
            kind="durable",
        )
    }
    for template in (interactive, *ancillary):
        declarations.update(
            {
            template.logical_slot_name(slot.name): ConfigurationBindingDeclaration(
                name=template.logical_slot_name(slot.name),
                container_path=slot.container_path,
                sensitivity=slot.sensitivity,
                concurrent=slot.concurrent,
                description=slot.deletion_effect,
                kind=slot.kind,
                component_id=template.component.id,
                slot_name=slot.name,
            )
            for slot in template.persistence.state_slots
            }
        )
    return declarations


def component_secret_inputs(
    lock: Mapping[str, Any], *, source: str = "platform lock"
) -> dict[str, SecretInputMetadata]:
    """Return optional/required secret inputs declared by selected components."""

    try:
        interactive, ancillary = selected_component_definitions(lock)
    except ComponentCatalogError as exc:
        raise ProjectConfigurationError(f"{source}: {exc}") from exc
    result: dict[str, SecretInputMetadata] = {}
    for component in (interactive, *ancillary):
        for declaration in component.secret_inputs():
            logical_name = f"{component.id}/{declaration.name}"
            result[logical_name] = SecretInputMetadata(
                name=logical_name,
                environment_variable=declaration.environment_variable,
                required=declaration.required,
                description=declaration.description,
                exposure=declaration.exposure,
            )
    return result


def resolve_secret_bindings(
    lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, str]:
    """Resolve secret source names without reading or serializing secret values."""

    declarations = component_secret_inputs(lock)
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    bindings = configuration.get("bindings", {})
    if not isinstance(bindings, dict):
        raise ProjectConfigurationError("Checkout configuration.bindings must be a table.")
    raw = bindings.get("host-environment", {})
    if not isinstance(raw, dict):
        raise ProjectConfigurationError(
            "Checkout configuration.bindings.host-environment must be a table."
        )
    resolved: dict[str, str] = {}
    for name, source in raw.items():
        declaration = declarations.get(str(name))
        if declaration is None:
            available = ", ".join(sorted(declarations)) or "none"
            raise ProjectConfigurationError(
                f"Secret input {name!r} is not declared by the selected components; "
                f"declared secret inputs: {available}."
            )
        if source != declaration.environment_variable:
            raise ProjectConfigurationError(
                f"Secret input {name!r} must bind its declared host environment variable "
                f"{declaration.environment_variable!r}."
            )
        resolved[str(name)] = source
    missing = sorted(
        name for name, declaration in declarations.items() if declaration.required and name not in resolved
    )
    if missing:
        raise ProjectConfigurationError(
            "Required secret bindings are missing: " + ", ".join(missing) + "."
        )
    return resolved


def resolve_configuration_bindings(
    lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, str]:
    declarations = configuration_binding_declarations(lock)
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    bindings = configuration.get("bindings", {})
    if not isinstance(bindings, dict):
        raise ProjectConfigurationError("Checkout configuration.bindings must be a table.")
    host_directories = bindings.get("host-directory", {})
    if not isinstance(host_directories, dict):
        raise ProjectConfigurationError(
            "Checkout configuration.bindings.host-directory must be a table."
        )

    resolved: dict[str, str] = {}
    for name, raw_source in host_directories.items():
        if not isinstance(name, str) or name not in declarations:
            available = ", ".join(sorted(declarations))
            raise ProjectConfigurationError(
                f"Configuration binding {name!r} is not declared by the selected component; "
                f"declared bindings: {available}."
            )
        if not isinstance(raw_source, str):
            raise ProjectConfigurationError(
                f"Host-directory binding {name!r} must contain a filesystem path string."
            )
        source = Path(raw_source).expanduser().resolve()
        if not source.is_dir():
            raise ProjectConfigurationError(
                f"Host-directory binding {name!r} is not an existing directory: {source}"
            )
        resolved[name] = str(source)
    return resolved


def authorization_declarations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any]
) -> dict[str, AuthorizationDeclaration]:
    """Build the curated V1 authorization catalog from project recommendations."""

    declarations: dict[str, AuthorizationDeclaration] = {}
    if "base" in lock:
        reference = locked_base_reference(lock)
        build_mnemonic = locked_base_build_mnemonic(lock)
        display_value = (
            f"{build_mnemonic} — {reference}" if build_mnemonic is not None else None
        )
        declarations["base-image"] = AuthorizationDeclaration(
            name="base-image",
            recommended_value=reference,
            recommendation_digest=canonical_digest(lock),
            description=(
                f"Execute DevCapsule {build_mnemonic} at the exact registry digest selected "
                "by the platform lock."
                if build_mnemonic is not None
                else "Execute the exact registry digest selected by the platform lock."
            ),
            display_value=display_value,
        )

    components = lock.get("components", {})
    if not isinstance(components, dict):
        raise ProjectConfigurationError("Platform lock components must be a table.")
    claude_code = components.get("claude-code")
    if claude_code is not None:
        if not isinstance(claude_code, dict):
            raise ProjectConfigurationError("components.claude-code must be a table.")
        if claude_code.get("acquisition-authorization") != CLAUDE_CODE_AUTHORIZATION:
            raise ProjectConfigurationError(
                "components.claude-code must declare acquisition-authorization = "
                f"{CLAUDE_CODE_AUTHORIZATION!r}."
            )
        if claude_code.get("terms-url") != CLAUDE_CODE_TERMS_URL:
            raise ProjectConfigurationError(
                f"components.claude-code terms-url must be {CLAUDE_CODE_TERMS_URL!r}."
            )
        version = claude_code.get("version")
        if not isinstance(version, str) or not version:
            raise ProjectConfigurationError(
                "components.claude-code.version must be a non-empty string."
            )
        declarations[CLAUDE_CODE_AUTHORIZATION] = AuthorizationDeclaration(
            name=CLAUDE_CODE_AUTHORIZATION,
            recommended_value=True,
            recommendation_digest=canonical_digest(
                {"name": CLAUDE_CODE_AUTHORIZATION, "component": claude_code}
            ),
            description=(
                f"Download checksum-pinned Claude Code {version} directly from Anthropic "
                f"during local materialization, subject to {CLAUDE_CODE_TERMS_URL}."
            ),
        )

    host = manifest.get("host", {})
    if not isinstance(host, dict):
        raise ProjectConfigurationError("Project declaration host metadata must be a table.")
    recommendation_paths: dict[str, tuple[tuple[str, ...], AuthorizationScalar]] = {
        "docker-daemon": (("docker", "mode", "recommended"), "host-socket"),
        "network": (("network", "mode", "recommended"), "host"),
        "development-sudo": (("privilege", "development-sudo", "recommended"), True),
    }
    for name, (path, supported_value) in recommendation_paths.items():
        recommendation: object = host
        for key in path:
            if not isinstance(recommendation, dict) or key not in recommendation:
                recommendation = None
                break
            recommendation = recommendation[key]
        if recommendation is None:
            continue
        if not isinstance(recommendation, dict):
            raise ProjectConfigurationError(
                f"Project authorization recommendation for {name!r} must be a table."
            )
        value = recommendation.get("value")
        justification = recommendation.get("justification")
        if value != supported_value:
            raise ProjectConfigurationError(
                f"Project recommendation {name!r} must use the supported V1 value "
                f"{supported_value!r}; found {value!r}."
            )
        if not isinstance(justification, str) or not justification:
            raise ProjectConfigurationError(
                f"Project recommendation {name!r} must include a non-empty justification."
            )
        declarations[name] = AuthorizationDeclaration(
            name=name,
            recommended_value=supported_value,
            recommendation_digest=canonical_digest({"name": name, "recommendation": recommendation}),
            description=justification,
        )
    return declarations


def normalize_authorization_value(
    declaration: AuthorizationDeclaration, value: object
) -> AuthorizationScalar:
    expected = declaration.recommended_value
    if isinstance(expected, bool):
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            normalized: AuthorizationScalar = value.lower() == "true"
        elif isinstance(value, bool):
            normalized = value
        else:
            raise ProjectConfigurationError(
                f"Authorization {declaration.name!r} requires true or false."
            )
    elif isinstance(value, str):
        if not isinstance(value, str):
            raise ProjectConfigurationError(
                f"Authorization {declaration.name!r} requires value {expected!r}."
            )
        normalized = value
    else:  # pragma: no cover - AuthorizationScalar makes this defensive only.
        raise ProjectConfigurationError(f"Unsupported authorization metadata for {declaration.name!r}.")
    if normalized != expected:
        raise ProjectConfigurationError(
            f"Project recommendation {declaration.name!r} is exactly {expected!r}, not {normalized!r}. "
            "Authorizing a different value requires distinct reviewed metadata."
        )
    return normalized


def resolved_checkout_authorizations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, AuthorizationScalar]:
    declarations = authorization_declarations(manifest, lock)
    authorization = checkout.get("authorization", {})
    if not isinstance(authorization, dict):
        raise ProjectConfigurationError("Checkout authorization must be a table.")
    unknown = sorted(str(name) for name in authorization if name not in declarations)
    if unknown:
        raise ProjectConfigurationError(
            "Checkout contains unsupported authorization entries: " + ", ".join(unknown) + "."
        )

    resolved: dict[str, AuthorizationScalar] = {}
    for name, record in authorization.items():
        declaration = declarations[name]
        if name == "base-image":
            selection = authorized_base_selection(lock, checkout)
            if selection is not None:
                resolved[name] = selection.reference
            continue
        if not isinstance(record, dict):
            raise ProjectConfigurationError(f"Checkout authorization {name!r} must be a table.")
        value = normalize_authorization_value(declaration, record.get("value"))
        if record.get("recommendation-digest") != declaration.recommendation_digest:
            raise ProjectConfigurationError(
                f"Checkout authorization {name!r} is stale; review the current recommendation and run "
                f"'devcapsule project config authorize {name} {render_authorization_value(declaration.recommended_value)}'."
            )
        resolved[name] = value
    return resolved


def render_authorization_value(value: AuthorizationScalar) -> str:
    return str(value).lower() if isinstance(value, bool) else value


def memory_size_bytes(value: str) -> int:
    match = MEMORY_SIZE_PATTERN.fullmatch(value)
    if match is None:
        raise ProjectConfigurationError(f"Invalid memory size: {value!r}.")
    quantity = int(match.group(1))
    multiplier = {
        "B": 1,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4,
    }[match.group(2)]
    return quantity * multiplier


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


def render_toml_scalar(value: ConfigurationScalar) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    return quote_toml(value)


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
    """Load the committed platform lock for this host's platform.

    The lock is the project-side record of one resolution: the version set and
    property defaults selected for one platform. It is a record, not a
    permission gate: loading it must never refuse ordinary work because some
    other project input changed. Drift between the manifest and a checkout's
    generated resolution belongs to the resolution layer
    (``fresh_resolved_project``), whose source digests name exactly what
    drifted and whose remedy — ``devcapsule project config resolve`` — actually
    reconciles it. See "The Lock Is A Record, Not A Mandate" in
    ``engineering-docs/design-notes/devcapsule/v1-user-experience.md``.

    Committed locks may carry a ``manifest-digest`` of the whole manifest.
    This function once compared it and refused every dependent command after
    any manifest edit, fatally and with a remedy that could not help. The
    field is deliberately not read: a lock derives from the capability set and
    the platform, so no other manifest field may affect its validity (the
    scoped-digest principle), and R-COMPAT-001 forbids demanding user action
    to keep existing committed locks working.
    """

    path = root / ".devcapsule" / f"devcapsule.{platform_alias()}.lock"
    if not path.is_file():
        raise ProjectConfigurationError(
            f"Missing {path}: this project carries no platform lock for {platform_alias()}. "
            "The platform lock is authored on the project side and committed with the project."
        )
    value = load_toml(path)
    if value.get("devcapsule-lock-format-version") != 1:
        raise ProjectConfigurationError(f"{path} has an unsupported lock format version.")
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


def locked_base_build_mnemonic(lock: Mapping[str, Any]) -> str | None:
    base = lock.get("base")
    if not isinstance(base, dict):
        raise ProjectConfigurationError("Platform lock does not define formation base inputs.")
    value = base.get("build-mnemonic")
    if value is None:
        return None
    if not isinstance(value, str) or RELEASE_BUILD_MNEMONIC_PATTERN.fullmatch(value) is None:
        raise ProjectConfigurationError(
            "Platform lock base.build-mnemonic must be a release mnemonic such as 'v026'."
        )
    return value


def authorized_base_selection(
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    *,
    required: bool = True,
) -> AuthorizedBaseSelection | None:
    locked_reference = locked_base_reference(lock)
    build_mnemonic = locked_base_build_mnemonic(lock)
    authorization_root = checkout.get("authorization")
    authorization = (
        authorization_root.get("base-image") if isinstance(authorization_root, dict) else None
    )
    command = f"devcapsule project config authorize base-image {locked_reference}"
    if not isinstance(authorization, dict):
        if required:
            recognizable_base = (
                f"DevCapsule {build_mnemonic} base {locked_reference}"
                if build_mnemonic is not None
                else f"base {locked_reference}"
            )
            raise ProjectConfigurationError(
                f"The lock recommends {recognizable_base}, but this checkout has not authorized it; "
                f"run '{command}', or explicitly authorize an inspected local DevCapsule base."
            )
        return None
    authorized_reference = authorization.get("reference")
    if not isinstance(authorized_reference, str) or not authorized_reference:
        raise ProjectConfigurationError(
            "The checkout's base-image authorization must contain a non-empty reference."
        )
    authorized_lock = authorization.get("lock-digest")
    expected_lock = canonical_digest(lock)
    if authorized_lock != expected_lock:
        refresh = f"devcapsule project config authorize base-image {authorized_reference}"
        raise ProjectConfigurationError(
            "The checkout's base-image authorization is stale for the current lock; "
            f"review the lock and run '{refresh}'."
        )
    local_identity = authorization.get("image-id")
    if authorized_reference == locked_reference:
        if local_identity is not None:
            raise ProjectConfigurationError(
                "The lock-recommended base-image authorization must not contain a local image ID."
            )
        return AuthorizedBaseSelection(
            reference=authorized_reference,
            lock_digest=expected_lock,
        )
    try:
        immutable_registry_reference(authorized_reference)
    except ProjectConfigurationError:
        pass
    else:
        raise ProjectConfigurationError(
            f"Published base {authorized_reference!r} is not the lock-recommended digest; "
            "a different published artifact requires distinct project-reviewed metadata."
        )
    if (
        not isinstance(local_identity, str)
        or not local_identity.startswith("sha256:")
        or not SHA256_PATTERN.fullmatch(local_identity.removeprefix("sha256:"))
    ):
        raise ProjectConfigurationError(
            "A non-recommended base-image authorization must be bound to an exact local "
            "Docker image ID; rerun "
            f"'devcapsule project config authorize base-image {authorized_reference}'."
        )
    return AuthorizedBaseSelection(
        reference=authorized_reference,
        lock_digest=expected_lock,
        local_image_identity=local_identity,
    )


def authorized_base_reference(
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    *,
    required: bool = True,
) -> str | None:
    """Compatibility accessor for consumers needing only the selected reference."""

    selection = authorized_base_selection(lock, checkout, required=required)
    return selection.reference if selection is not None else None


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
    values: Mapping[str, ConfigurationScalar] | None = None,
    host_directory_bindings: Mapping[str, str] | None = None,
    host_environment_bindings: Mapping[str, str] | None = None,
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
