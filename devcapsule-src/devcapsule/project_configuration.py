"""Capability-first project configuration for the initial PyCharm dogfood slice."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import quote


from devcapsule.compat import CliError
from devcapsule.platforms import Platform, UnsupportedPlatformError, XdgHomes
from devcapsule.components.catalog import (
    COMPONENTS,
    ComponentCatalogError,
    selected_component_definitions,
    selected_runtime_templates,
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

# The curated V1 host-access recommendation vocabulary.  Each entry maps a
# node's canonical name to the manifest subtree that declares its
# recommendation and to the single supported V1 value.  ``init`` asks exactly
# these questions when it authors a manifest, and ``authorization_declarations``
# turns present declarations into authorization nodes; they share this one
# table so the asked question and the honored declaration cannot drift.
CURATED_HOST_RECOMMENDATIONS: dict[str, tuple[tuple[str, ...], AuthorizationScalar]] = {
    "docker-daemon": (("docker", "mode", "recommended"), "host-socket"),
    "network": (("network", "mode", "recommended"), "host"),
    "development-sudo": (("privilege", "development-sudo", "recommended"), True),
    "host-browser": (("browser", "host-open", "recommended"), True),
}

# Host capabilities that exist as authorization nodes on every project,
# whether or not the project recommends them. Settled by the product owner on
# 2026-08-24: host-browser, docker-daemon, and development-sudo are proper
# configuration nodes under authorize. These are developer-owned choices —
# "Denial is the default. The developer may deny it, allow it once, allow it
# for this checkout" — so their availability cannot depend on the project's
# advice; a recommendation merely attaches the project's justification and
# rebinds the answer to it. Host networking is deliberately absent: its
# run-once form is the raw docker passthrough, and its persistent relaxation
# remains a project-recommended decision.
WORKSTATION_CAPABILITY_DEFAULTS: dict[str, tuple[AuthorizationScalar, str]] = {
    "docker-daemon": (
        "host-socket",
        "Expose the host Docker daemon socket to the capsule; this permits broad "
        "control of the host.",
    ),
    "development-sudo": (
        True,
        "Enable the declared development-sudo behavior inside the capsule.",
    ),
    "host-browser": (
        True,
        "Open HTTP(S) links from the capsule in the physical host's default browser "
        "through the URL-only broker.",
    ),
    # Host X11 passthrough survives only as this node (contained-display
    # design note, T7): never a default, never a project recommendation,
    # and the trade-off is stated where the answer is given.
    "host-x11": (
        True,
        "Run the IDE on the host's X session instead of the capsule's contained "
        "display, handing the capsule your full X session credential: keystroke "
        "capture across the session, window capture, input injection, and "
        "clipboard access. The session-credential boundary test is waived for such runs.",
    ),
}

# Each string-valued authorization node's deny spelling — the value the run
# path falls back to when nothing grants the capability. Recording it is the
# developer's reduce-privilege decision (owner rulings 2026-09-03: denial is a
# *value*, so a checkout's recorded denial outranks a workstation-level
# allow); bool nodes deny with plain ``false`` and need no entry here.
AUTHORIZATION_DENY_VALUES: dict[str, str] = {
    "docker-daemon": "none",
    "network": "bridge",
}


def authorization_deny_value(declaration: "AuthorizationDeclaration") -> AuthorizationScalar | None:
    """The node's deny value, or None for nodes with no deny state (base-image)."""

    if isinstance(declaration.recommended_value, bool):
        return False
    return AUTHORIZATION_DENY_VALUES.get(declaration.name)


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
    # False for workstation-capability defaults the project did not recommend;
    # bulk authorization of "everything recommended" must not include them.
    project_recommended: bool = True
    # "acquisition" nodes gate a vendor download with per-user terms; init has
    # no safe omission for them and asks each one. Everything else is "host".
    kind: str = "host"
    # For acquisition nodes: the capability whose removal from the need is the
    # alternative to authorizing, and the vendor product name for messages.
    capability: str | None = None
    subject: str | None = None

    @property
    def required(self) -> bool:
        """Selected executables/acquisitions require consent; host access does not."""
        return self.name == "base-image" or self.kind == "acquisition"


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
class AuthorizationChoice:
    """An explicit decision, never an instruction to grant permission implicitly."""

    name: str
    value: str
    meaning: str

    def command(self, project: Path | None = None) -> str:
        context = ["--path", str(project)] if project is not None else []
        return shlex.join(["devcapsule", "project", *context, "config", "authorize", self.name, self.value])


@dataclass(frozen=True)
class AuthorizationReview:
    """One interpretation of a recorded answer for inspection and resolution.

    A problem prevents resolution. Choices are alternatives, not a script to
    execute in sequence. A valid denial remains a denial even when the project
    recommends granting the capability.
    """

    name: str
    status: str
    recorded: str
    recommended: str
    description: str
    value: AuthorizationScalar | None = None
    problem: str | None = None
    choices: tuple[AuthorizationChoice, ...] = ()

    def render(self, project: Path | None = None) -> str:
        lines = [
            f"{self.name}: {self.status}; recorded: {self.recorded}; recommended: {self.recommended}",
            f"  {self.description}",
        ]
        if self.problem is not None:
            lines.append(f"  {self.problem}")
        for choice in self.choices:
            lines.append(f"  {choice.meaning}: {choice.command(project)}")
        return "\n".join(lines)


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
    if isinstance(value, str) and value.strip().lower() == "default":
        # 'default' is an input artifact, never a stored value: it resolves
        # to the node's declared default at the moment the decision is made
        # (owner ruling 2026-09-03, uniform across node families).  Value
        # declarations carry no default field today, so there is nothing for
        # it to resolve to here.
        raise ProjectConfigurationError(
            f"Configuration value {name!r} declares no default for 'default' to "
            "resolve to; set an explicit value, or use 'unset' to leave the "
            "value absent."
        )
    if isinstance(value, str) and value.strip().lower() == "none":
        # Reserved alongside 'default' (owner ruling 2026-09-03): the
        # explicit-absence answer is recorded by the carriers as an omission,
        # never stored as a literal — a "none" reaching normalization is a
        # carrier that failed to intercept it.
        raise ProjectConfigurationError(
            f"Configuration value {name!r} cannot hold the reserved literal 'none'; "
            "the 'none' answer records an explicit omission."
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


def checkout_omitted_values(checkout: Mapping[str, Any]) -> tuple[str, ...]:
    """The names a checkout explicitly keeps absent from the runtime config."""

    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    omitted = configuration.get("omitted-values", [])
    if not isinstance(omitted, list) or not all(isinstance(name, str) for name in omitted):
        raise ProjectConfigurationError(
            "Checkout configuration omitted-values must be an array of node names."
        )
    return tuple(sorted(set(omitted)))


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

    omitted = checkout_omitted_values(checkout)
    for name in omitted:
        if name not in declarations:
            raise ProjectConfigurationError(
                f"Checkout omits undeclared configuration value {name!r}."
            )
        if declarations[name].get("required", False):
            raise ProjectConfigurationError(
                f"Configuration value {name!r} is mandatory and cannot be omitted; "
                f"record a value with 'devcapsule project config set {name} VALUE'."
            )
        if name in raw_values:
            raise ProjectConfigurationError(
                f"Configuration value {name!r} is both recorded and omitted; "
                "re-answer it with 'devcapsule project config set' or 'unset'."
            )

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
    for component_id, metadata in components.items():
        if component_id == "interactive-surface":
            continue
        definition = COMPONENTS.get(component_id) if isinstance(component_id, str) else None
        if definition is None:
            # Unknown ids fail later at catalog selection.
            continue
        contract = definition.acquisition()
        if contract is None:
            # Components without vendor terms need no acquisition authorization.
            continue
        if not isinstance(metadata, dict):
            raise ProjectConfigurationError(f"components.{component_id} must be a table.")
        if metadata.get("acquisition-authorization") != contract.authorization:
            raise ProjectConfigurationError(
                f"components.{component_id} must declare acquisition-authorization = "
                f"{contract.authorization!r}."
            )
        if metadata.get("terms-url") != contract.terms_url:
            raise ProjectConfigurationError(
                f"components.{component_id} terms-url must be {contract.terms_url!r}."
            )
        version = metadata.get("version")
        if not isinstance(version, str) or not version:
            raise ProjectConfigurationError(
                f"components.{component_id}.version must be a non-empty string."
            )
        declarations[contract.authorization] = AuthorizationDeclaration(
            name=contract.authorization,
            recommended_value=True,
            recommendation_digest=canonical_digest(
                {"name": contract.authorization, "component": metadata}
            ),
            description=(
                f"Download checksum-pinned {contract.display_name} {version} directly "
                f"from {contract.vendor} during local materialization, subject to "
                f"{contract.terms_url}."
            ),
            kind="acquisition",
            capability=definition.capability,
            subject=contract.display_name,
        )

    host = manifest.get("host", {})
    if not isinstance(host, dict):
        raise ProjectConfigurationError("Project declaration host metadata must be a table.")
    for name, (path, supported_value) in CURATED_HOST_RECOMMENDATIONS.items():
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
    for name, (supported_value, description) in WORKSTATION_CAPABILITY_DEFAULTS.items():
        if name in declarations:
            continue
        # The digest is a stable constant distinct from every recommendation
        # digest, so a later project recommendation correctly stales the
        # workstation-default answer: the question changed, so it is re-asked.
        declarations[name] = AuthorizationDeclaration(
            name=name,
            recommended_value=supported_value,
            recommendation_digest=canonical_digest(
                {"name": name, "recommendation": "workstation-default"}
            ),
            description=description,
            project_recommended=False,
        )
    return declarations


def normalize_authorization_value(
    declaration: AuthorizationDeclaration, value: object
) -> AuthorizationScalar:
    expected = declaration.recommended_value
    deny = authorization_deny_value(declaration)
    if isinstance(value, str):
        keyword = value.strip().lower()
        if keyword == "default":
            # The reserved keyword accepting the recommendation for one key
            # (owner ruling 2026-09-03); the bulk counterpart is
            # --all-recommended. Input artifact only: the resolved value is
            # what gets stored.
            return expected
        if keyword == "none":
            # The reserved denial keyword (owner ruling 2026-09-03): resolves
            # to the node's deny value at decision time and stores it, so a
            # checkout's recorded denial outranks a workstation-level allow.
            if deny is None:
                raise ProjectConfigurationError(
                    f"Authorization {declaration.name!r} is mandatory and has no deny "
                    "state; 'none' cannot apply. Accept the recommendation with "
                    "'default' or record a different selection."
                )
            return deny
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
        normalized = value
    else:  # pragma: no cover - AuthorizationScalar makes this defensive only.
        raise ProjectConfigurationError(f"Unsupported authorization metadata for {declaration.name!r}.")
    if normalized != expected and (deny is None or normalized != deny):
        # Deliberately source-neutral: the recommendation may be a project's
        # or a workstation default, and denial is always the developer's to
        # record — only values *beyond* recommendation-or-deny need reviewed
        # metadata (2026-09-02 denial-grammar bug, aggravations 1 and 2).
        accepted = f"its recommended value {render_authorization_value(expected)!r}"
        if deny is not None:
            accepted += f", its deny value {render_authorization_value(deny)!r}"
        raise ProjectConfigurationError(
            f"Authorization {declaration.name!r} accepts {accepted}, or the keywords "
            f"'default'/'none'; got {normalized!r}. Any other value requires distinct "
            "reviewed metadata."
        )
    return normalized


def base_recovery_choices(record: Mapping[str, Any]) -> tuple[AuthorizationChoice, ...]:
    """Always offer the reviewed pin; renew a local override only by exact ID.

    The old published digest is not an accepted value under the new lock.
    Replaying a local tag is also wrong: it may now point at different bytes.
    """

    choices = [AuthorizationChoice("base-image", "default", "Accept the current project recommendation")]
    identity = record.get("image-id")
    if (
        isinstance(identity, str)
        and identity.startswith("sha256:")
        and SHA256_PATTERN.fullmatch(identity.removeprefix("sha256:")) is not None
    ):
        choices.append(AuthorizationChoice(
            "base-image", identity, "Keep the exact local image, if still available and valid"
        ))
    return tuple(choices)


def _authorization_choices(
    declaration: AuthorizationDeclaration, recorded_value: AuthorizationScalar | None
) -> tuple[AuthorizationChoice, ...]:
    """Construct only values accepted by this declaration's own validator."""

    if declaration.kind == "acquisition":
        # Keeping a declined mandatory acquisition is legitimate, but is not
        # a recovery action: the selected environment then cannot be built.
        return (AuthorizationChoice(declaration.name, "true", "Authorize the selected acquisition after review"),)
    values: list[tuple[AuthorizationScalar, str]] = []
    if recorded_value is not None:
        values.append((recorded_value, "Keep the recorded decision after review"))
    values.append((declaration.recommended_value, "Accept the current recommendation"))
    deny = authorization_deny_value(declaration)
    # Base selection has its own choices; all remaining host nodes have a
    # denial state by the curated authorization contract.
    assert deny is not None
    values.append((deny, "Deny this capability"))
    choices: list[AuthorizationChoice] = []
    for value, meaning in values:
        normalized = normalize_authorization_value(declaration, value)
        rendered = render_authorization_value(normalized)
        if all(choice.value != rendered for choice in choices):
            choices.append(AuthorizationChoice(declaration.name, rendered, meaning))
    return tuple(choices)


def review_authorizations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> tuple[AuthorizationReview, ...]:
    """Assess every authorization without writes, Docker calls or early refusal.

    The same result drives inspection and resolution. Missing optional host
    access is safe; missing base consent or selected vendor acquisition is not
    run-ready. Stale answers must be renewed, never silently reinterpreted.
    """

    declarations = authorization_declarations(manifest, lock)
    records = checkout.get("authorization", {})
    if not isinstance(records, dict):
        raise ProjectConfigurationError("Checkout authorization must be a table.")
    reviews: list[AuthorizationReview] = []
    for name, declaration in sorted(declarations.items()):
        record = records.get(name)
        required = declaration.required
        recommended = declaration.display_value or render_authorization_value(declaration.recommended_value)
        recorded = "unanswered"
        value: AuthorizationScalar | None = None
        problem: str | None = None
        choices: tuple[AuthorizationChoice, ...] = ()
        if name not in records:
            status = "missing-required" if required else (
                "missing-recommended" if declaration.project_recommended else "available"
            )
            if required:
                problem = "An explicit decision is required before this environment can run."
        elif not isinstance(record, dict):
            status = "invalid"
            problem = f"Checkout authorization {name!r} must be a table."
        elif name == "base-image":
            recorded = str(record.get("reference", "missing reference"))
            if record.get("image-id") is not None:
                recorded += f" (local image {record['image-id']})"
            try:
                selection = authorized_base_selection(lock, checkout)
            except ProjectConfigurationError as exc:
                status = "stale" if (
                    isinstance(record.get("reference"), str) and record["reference"]
                    and record.get("lock-digest") != declaration.recommendation_digest
                ) else "invalid"
                problem = (
                    "The recorded base selection was authorized against a different lock. "
                    "Review the previous selection and current recommendation before choosing."
                    if status == "stale" else str(exc)
                )
            else:
                assert selection is not None  # required=True either returns a selection or raises
                status = "authorized-local" if selection.is_local else "authorized"
                value = selection.reference
        else:
            recorded = str(record.get("value", "missing value")).lower() if isinstance(
                record.get("value"), bool
            ) else str(record.get("value", "missing value"))
            try:
                value = normalize_authorization_value(declaration, record.get("value"))
            except ProjectConfigurationError as exc:
                status = "invalid"
                problem = str(exc)
            else:
                if record.get("recommendation-digest") != declaration.recommendation_digest:
                    status = "stale"
                    problem = "The recommendation changed; review it and explicitly renew or change your answer."
                elif value == authorization_deny_value(declaration):
                    status = "denied"
                    if required:
                        problem = (
                            f"The selected {declaration.subject} acquisition is denied. "
                            f"Remove {declaration.capability!r} from the project need, or explicitly authorize it."
                        )
                else:
                    status = "authorized"
        if problem is not None:
            choices = (
                base_recovery_choices(record if isinstance(record, dict) else {})
                if name == "base-image"
                else _authorization_choices(declaration, value)
            )
        reviews.append(AuthorizationReview(
            name, status, recorded, recommended, declaration.description, value, problem, choices
        ))
    for name in sorted(set(records) - set(declarations)):
        reviews.append(AuthorizationReview(
            name, "unsupported", "recorded", "not declared", "This node no longer belongs to the project configuration.",
            problem="Remove the obsolete entry from the checkout authorization table after review.",
        ))
    return tuple(reviews)


def resolved_checkout_authorizations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, AuthorizationScalar]:
    reviews = review_authorizations(manifest, lock, checkout)
    problems = [review for review in reviews if review.problem is not None]
    if problems:
        raise ProjectConfigurationError(
            "Configuration needs authorization decisions:\n"
            + "\n".join(review.render() for review in problems)
        )
    return {review.name: review.value for review in reviews if review.value is not None}


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


def config_root(env: Mapping[str, str] | None = None) -> Path:
    return XdgHomes.from_environment(env).config


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

    try:
        current = Platform.current()
    except UnsupportedPlatformError as exc:
        raise ProjectConfigurationError(str(exc)) from exc
    path = root / ".devcapsule" / f"devcapsule.{current}.lock"
    if not path.is_file():
        raise ProjectConfigurationError(
            f"Missing {path}: this project carries no platform lock for {current}. "
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
        choices = base_recovery_choices(authorization)
        raise ProjectConfigurationError(
            "The checkout's base-image authorization is stale for the current lock; "
            f"previous selection: {authorized_reference}; current recommendation: {locked_reference}. "
            + " ".join(f"{choice.meaning}: {choice.command()}." for choice in choices)
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


def resolution_source_digests(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, str]:
    """The exact source digests a fresh generated resolution must record."""

    return {
        "manifest": canonical_digest(manifest),
        "platform-lock": canonical_digest(lock),
        "checkout-input": canonical_digest(checkout),
    }


def stale_resolution_inputs(
    manifest: Mapping[str, Any],
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    resolution: Mapping[str, Any],
) -> tuple[str, ...]:
    """Name exactly which generated-resolution inputs have drifted.

    This is the single staleness policy for the resolution layer: drift is
    detected here — never by a loader refusing to read an artifact — and the
    remedy is always ``devcapsule project config resolve``.  Every consumer
    (``config list``, ``run``, ``fresh_resolved_project``) asks this one
    function so the policy cannot fork.
    """

    actual = resolution.get("sources", {})
    if not isinstance(actual, dict):
        raise ProjectConfigurationError("Generated resolution sources must be a table.")
    expected = resolution_source_digests(manifest, lock, checkout)
    return tuple(name for name, digest in expected.items() if actual.get(name) != digest)


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
    stale = stale_resolution_inputs(manifest, lock, checkout, resolution)
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
