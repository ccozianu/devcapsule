"""Parameterized VS Code-family editor adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ..contract import RuntimePlan, RuntimePlanError


@dataclass(frozen=True)
class VscodeLaunch:
    command: tuple[str, ...]


def _string(configuration: Mapping[str, object], key: str) -> str:
    value = configuration.get(key)
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RuntimePlanError(f"VS Code-family component {key} must be a non-empty string")
    return value


def plan(runtime: RuntimePlan) -> VscodeLaunch:
    config = runtime.component.configuration
    slots = runtime.slots_by_name()
    mapping = config.get("state_slot_mapping")
    if not isinstance(mapping, dict):
        raise RuntimePlanError("VS Code-family component state_slot_mapping must be an object")
    directories: dict[str, str] = {}
    for option in ("user-data", "extensions"):
        local_slot_name = mapping.get(option)
        if not isinstance(local_slot_name, str):
            raise RuntimePlanError(f"VS Code-family {option} mapping must name a declared state slot")
        slot_name = runtime.component.slot_name(local_slot_name)
        if slot_name not in slots:
            raise RuntimePlanError(f"VS Code-family {option} mapping must name a declared state slot")
        directories[option] = slots[slot_name]
    # Renderer sandboxing is retired (product-owner ruling 2026-09-02; see
    # engineering-docs/design-notes/devcapsule/renderer-sandboxing.md). A
    # template that still declares a sandbox, or omits --no-sandbox, would
    # not fail here but as a cryptic zygote abort at surface start — refuse
    # it at plan time instead.
    if config.get("sandbox") is not None:
        raise RuntimePlanError(
            "VS Code-family renderer sandboxing is retired; remove the sandbox "
            "declaration (see the renderer-sandboxing design note)"
        )
    additional = config.get("additional_arguments", [])
    if not isinstance(additional, list):
        raise RuntimePlanError("VS Code-family additional_arguments must be an array")
    for argument in additional:
        if not isinstance(argument, str) or not argument or any(
            character in argument for character in "\x00\r\n"
        ):
            raise RuntimePlanError("VS Code-family additional arguments must be one-line strings")
    if "--no-sandbox" not in additional:
        raise RuntimePlanError(
            "VS Code-family additional_arguments must include --no-sandbox; "
            "without it Chromium aborts at surface start under capsule "
            "hardening (see the renderer-sandboxing design note)"
        )
    installation_path = Path(_string(config, "installation_path"))
    launcher = _string(config, "launcher")
    if Path(launcher).is_absolute() or ".." in Path(launcher).parts:
        raise RuntimePlanError("VS Code-family launcher must be relative to installation_path")
    return VscodeLaunch(
        command=(
            str(installation_path / launcher),
            f"--user-data-dir={directories['user-data']}",
            f"--extensions-dir={directories['extensions']}",
            *additional,
            runtime.project_path,
        )
    )
