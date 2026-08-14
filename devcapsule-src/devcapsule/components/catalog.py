"""Trusted component catalog selection for the current V1 lock format."""

from __future__ import annotations

from typing import Any, Mapping

from devcapsule.components import ComponentDefinition
from devcapsule.components.claude_code import DEFINITION as CLAUDE_CODE
from devcapsule.components.codex import DEFINITION as CODEX
from devcapsule.components.postgresql_client import DEFINITION as POSTGRESQL_CLIENT
from devcapsule.components.pycharm import DEFINITION as PYCHARM
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


class ComponentCatalogError(ValueError):
    """The lock selects unsupported or malformed component metadata."""


COMPONENTS: dict[str, ComponentDefinition] = {
    PYCHARM.id: PYCHARM,
    CODEX.id: CODEX,
    CLAUDE_CODE.id: CLAUDE_CODE,
    POSTGRESQL_CLIENT.id: POSTGRESQL_CLIENT,
}


def selected_component_definitions(
    lock: Mapping[str, Any],
) -> tuple[ComponentDefinition, tuple[ComponentDefinition, ...]]:
    components = lock.get("components")
    if not isinstance(components, dict):
        raise ComponentCatalogError("platform lock components must be a table")
    interactive_id = components.get("interactive-surface")
    if interactive_id != PYCHARM.id:
        raise ComponentCatalogError(
            f"no V1 runtime template is available for interactive component {interactive_id!r}"
        )
    ancillary: list[ComponentDefinition] = []
    for component_id, metadata in components.items():
        if component_id in {"interactive-surface", interactive_id}:
            continue
        definition = COMPONENTS.get(component_id)
        if definition is None:
            raise ComponentCatalogError(
                f"no V1 runtime template is available for component {component_id!r}"
            )
        if not isinstance(metadata, dict):
            raise ComponentCatalogError(f"components.{component_id} must be a table")
        ancillary.append(definition)
    return PYCHARM, tuple(ancillary)


def selected_runtime_templates(
    lock: Mapping[str, Any],
) -> tuple[ComponentRuntimeTemplate, tuple[ComponentRuntimeTemplate, ...]]:
    interactive, ancillary = selected_component_definitions(lock)
    return interactive.runtime_template(), tuple(
        component.runtime_template() for component in ancillary
    )
