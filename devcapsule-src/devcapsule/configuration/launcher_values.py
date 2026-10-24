"""The launcher-owned values, memory and CPUs: their precedence and their runtime effects.

Answer 6 of the CLI UX redesign work order: the launcher owns the
container's memory limit and CPU count on every project. Neither needs a
declaration. The precedence is the checkout's answer, then the project's
recommendation, then the workstation default, then nothing. A manifest that
declares a value with the ``docker.memory-limit`` effect, as manifests did
before 0.3.0 rc4, is read here as a recommendation for ``memory`` and that
name as an alias, so recorded answers keep working.
"""

from __future__ import annotations

from typing import Any, Mapping

from .file_formats import ConfigurationScalar, ProjectConfigurationError
from .manifest_document import Recommendations
from .values import (
    LAUNCHER_VALUE_NAMES,
    RuntimeEffects,
    configuration_value_declarations,
    legacy_memory_names,
    memory_size_bytes,
    normalize_launcher_value,
)
from .workstation import WorkstationDefaults

__all__ = ["launcher_value_sources", "resolve_launcher_values"]


def launcher_value_sources(
    manifest: Mapping[str, Any], checkout: Mapping[str, Any], workstation: Mapping[str, Any] | None = None,
) -> dict[str, tuple[str | int | None, str]]:
    """The effective memory limit and CPU count with where each comes from.

    The precedence is the checkout's answer, the project's recommendation
    (``[recommendations]``, or a declared value carrying the memory-limit
    effect with a ``recommended`` value), the workstation default, else
    nothing: ``(None, "none")``. The source names are ``checkout``,
    ``project recommendation``, ``workstation default`` and ``none``.
    Values are validated; a bad recorded answer raises.
    """
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    raw_values = configuration.get("values", {})
    if not isinstance(raw_values, dict):
        raise ProjectConfigurationError("Checkout configuration.values must be a table.")
    recommendations = Recommendations.read(manifest)
    declarations = configuration_value_declarations(manifest)
    defaults = WorkstationDefaults.read(workstation or {}).values
    result: dict[str, tuple[str | int | None, str]] = {}
    for name in LAUNCHER_VALUE_NAMES:
        recorded: object = raw_values.get(name)
        if recorded is None and name == "memory":
            for alias in legacy_memory_names(manifest):
                if alias in raw_values:
                    recorded = raw_values[alias]
                    break
        if recorded is not None:
            result[name] = (normalize_launcher_value(name, recorded, field_name=f"checkout value {name}"), "checkout")
            continue
        recommended: object = recommendations.value(name)
        if recommended is None and name == "memory":
            for alias in legacy_memory_names(manifest):
                if "recommended" in declarations[alias]:
                    recommended = declarations[alias]["recommended"]
                    break
        if recommended is not None:
            result[name] = (normalize_launcher_value(name, recommended, field_name=f"recommended {name}"), "project recommendation")
            continue
        if name in defaults:
            result[name] = (defaults[name], "workstation default")
            continue
        result[name] = (None, "none")
    return result


def resolve_launcher_values(
    manifest: Mapping[str, Any], checkout: Mapping[str, Any], workstation: Mapping[str, Any] | None = None,
) -> tuple[dict[str, ConfigurationScalar], RuntimeEffects]:
    """The effective launcher values and their effects, ``memory-limit-bytes`` and ``cpus``."""
    values: dict[str, ConfigurationScalar] = {}
    effects: RuntimeEffects = {}
    for name, (value, _source) in launcher_value_sources(manifest, checkout, workstation).items():
        if value is None:
            continue
        values[name] = value
        if name == "memory":
            effects["memory-limit-bytes"] = memory_size_bytes(str(value))
        else:
            effects["cpus"] = int(value)
    return values, effects
