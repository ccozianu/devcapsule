"""Parameterized JetBrains product adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ..contract import RuntimePlan, RuntimePlanError


@dataclass(frozen=True)
class JetBrainsLaunch:
    properties_path: str
    properties_environment_variable: str
    properties: str
    command: tuple[str, ...]


def _string(configuration: Mapping[str, object], key: str) -> str:
    value = configuration.get(key)
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RuntimePlanError(f"JetBrains component {key} must be a non-empty string")
    return value


def plan(runtime: RuntimePlan) -> JetBrainsLaunch:
    config = runtime.component.configuration
    slots = runtime.slots_by_name()
    mapping = config.get("state_slot_mapping")
    if not isinstance(mapping, dict):
        raise RuntimePlanError("JetBrains component state_slot_mapping must be an object")
    properties: list[str] = []
    for property_name in ("config", "system", "plugins", "log"):
        local_slot_name = mapping.get(property_name)
        if not isinstance(local_slot_name, str):
            raise RuntimePlanError(f"JetBrains {property_name} mapping must name a declared state slot")
        slot_name = runtime.component.slot_name(local_slot_name)
        if slot_name not in slots:
            raise RuntimePlanError(f"JetBrains {property_name} mapping must name a declared state slot")
        properties.append(f"idea.{property_name}.path={slots[slot_name]}")
    additional = config.get("additional_properties", {})
    if not isinstance(additional, dict):
        raise RuntimePlanError("JetBrains component additional_properties must be an object")
    managed_properties = {f"idea.{name}.path" for name in ("config", "system", "plugins", "log")}
    for name, value in sorted(additional.items()):
        if (
            not isinstance(name, str)
            or not name
            or any(character in name for character in "\x00\r\n= ")
            or name in managed_properties
        ):
            raise RuntimePlanError("JetBrains additional property names must be safe and unmanaged")
        if not isinstance(value, str) or "\x00" in value or "\r" in value or "\n" in value:
            raise RuntimePlanError(f"JetBrains additional property {name!r} must be one line")
        properties.append(f"{name}={value}")
    installation_path = Path(_string(config, "installation_path"))
    launcher = _string(config, "launcher")
    if Path(launcher).is_absolute() or ".." in Path(launcher).parts:
        raise RuntimePlanError("JetBrains launcher must be relative to installation_path")
    return JetBrainsLaunch(
        properties_path=_string(config, "properties_path"),
        properties_environment_variable=_string(config, "properties_environment_variable"),
        properties="\n".join(properties) + "\n",
        command=(str(installation_path / launcher), runtime.project_path),
    )
