"""Capability policy values. Parsing does not depend on the installed catalog.

The project owns required/optional intent and SDK majors. The developer owns
extra selections and omissions. Unknown optional names remain ordinary data;
only a consumer decides which of them it can supply.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .documents import ProjectConfigurationError, table


def names(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item or item.strip() != item or "\x00" in item
        for item in value
    ):
        raise ProjectConfigurationError(f"{label} must be an array of non-empty capability names.")
    return tuple(sorted(set(value)))


@dataclass(frozen=True)
class CapabilityPolicy:
    required: tuple[str, ...]
    optional: tuple[str, ...] = ()
    sdk_major: tuple[tuple[str, int], ...] = ()
    layered: bool = False

    @classmethod
    def read(cls, manifest: Mapping[str, Any]) -> CapabilityPolicy:
        value = table(manifest, "capabilities")
        layered = "required" in value
        if layered and "need" in value:
            raise ProjectConfigurationError("Use capabilities.required or legacy capabilities.need, not both.")
        key = "required" if layered else "need"
        required = names(value.get(key), f"capabilities.{key}")
        optional = names(value.get("optional", []), "capabilities.optional")
        overlap = set(required) & set(optional)
        if overlap:
            raise ProjectConfigurationError(f"Capabilities cannot be both required and optional: {', '.join(sorted(overlap))}.")
        majors = table(value, "sdk-major")
        for capability, major in majors.items():
            if capability not in required or type(major) is not int or major < 1:
                raise ProjectConfigurationError("Each capabilities.sdk-major entry must name a required capability and a positive integer major.")
        return cls(required, optional, tuple(sorted(majors.items())), layered)

    def document(self) -> dict[str, Any]:
        return {"required": list(self.required), "optional": list(self.optional),
                "sdk-major": dict(self.sdk_major)}


@dataclass(frozen=True)
class LocalCapabilities:
    selected: tuple[str, ...] = ()
    without: tuple[str, ...] = ()

    @classmethod
    def read(cls, checkout: Mapping[str, Any]) -> LocalCapabilities:
        value = table(checkout, "capabilities")
        if set(value) - {"selected", "without", "lock"}:
            raise ProjectConfigurationError("Unsupported local capability fields; left intact.")
        selected = names(value.get("selected", []), "local capabilities.selected")
        without = names(value.get("without", []), "local capabilities.without")
        if set(selected) & set(without):
            raise ProjectConfigurationError("A local capability cannot be both selected and omitted.")
        if "lock" in value and not isinstance(value["lock"], str):
            raise ProjectConfigurationError("Local capabilities.lock must contain a TOML lock.")
        return cls(selected, without)

    def validate(self, policy: CapabilityPolicy) -> None:
        invalid = set(self.without) - set(policy.optional)
        if invalid:
            raise ProjectConfigurationError("Only project optional capabilities may be omitted locally: " + ", ".join(sorted(invalid)) + ".")
