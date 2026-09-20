"""Ordinary value declarations, domains, omissions and runtime effects."""

from __future__ import annotations
import re
from typing import Any, Mapping

from .documents import ConfigurationScalar, ProjectConfigurationError


CONFIGURATION_VALUE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")


MEMORY_SIZE_PATTERN = re.compile(r"^([1-9][0-9]*)(B|KiB|MiB|GiB|TiB)$")


CONFIGURATION_VALUE_TYPES = {"string", "integer", "boolean", "memory-size"}


RUNTIME_EFFECT_TYPES = {"docker.memory-limit": "memory-size"}


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
        if not isinstance(value_type, str) or value_type not in CONFIGURATION_VALUE_TYPES:
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
    problems: list[str] = []
    normalized: dict[str, ConfigurationScalar] = {}
    effects: dict[str, int] = {}
    for name in sorted(set(raw_values) | set(omitted) | set(declarations)):
        try:
            declaration = declarations.get(name)
            if declaration is None:
                raise ProjectConfigurationError(f"Checkout answers undeclared configuration value {name!r}.")
            if name in omitted:
                if declaration.get("required", False):
                    raise ProjectConfigurationError(f"Configuration value {name!r} is mandatory and cannot be omitted.")
                if name in raw_values:
                    raise ProjectConfigurationError(f"Configuration value {name!r} is both recorded and omitted.")
            elif name in raw_values:
                normalized[name] = normalize_configuration_value(manifest, name, raw_values[name])
            elif declaration.get("required", False):
                raise ProjectConfigurationError(
                    f"Required configuration value {name!r} is missing: project config set {name} VALUE."
                )
        except ProjectConfigurationError as exc:
            problems.append(str(exc))
    if problems:
        raise ProjectConfigurationError("\n".join(problems))
    for name, value in normalized.items():
        effect = declarations[name].get("runtime-effect")
        if effect == "docker.memory-limit":
            effects["memory-limit-bytes"] = memory_size_bytes(str(value))
    return normalized, effects


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
