"""PyCharm component interface.

This module owns PyCharm's installation, adapter, and persistence declarations.
Generic runtime planning consumes the declaration without knowing what the
slots mean.
"""

from __future__ import annotations

from devcapsule.components.discovery import JetBrainsDiscovery
from devcapsule.components.jetbrains import jetbrains_template

from collections.abc import Mapping

from devcapsule.container_runtime.contract import ComponentRuntimeTemplate
from devcapsule.components import (
    ComponentDefinition,
    LockedArtifactDeclaration,
    SecretInputDeclaration,
    StateEnvironmentDeclaration,
)


class PyCharmComponent(ComponentDefinition):
    """Trusted PyCharm component implementation."""

    def discovery_channel(self) -> JetBrainsDiscovery:
        return JetBrainsDiscovery()

    def channel_omission_reason(self) -> str:
        return 'IDE upgrades are outside the component-upgrade slice.'

    @property
    def id(self) -> str:
        return "pycharm"

    @property
    def capability(self) -> str:
        return "python-ide"

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return _runtime_template()

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(
        self, metadata: Mapping[str, object], platform: str
    ) -> tuple[LockedArtifactDeclaration, ...]:
        # PyCharm currently uses the established whole-directory materializer;
        # this method becomes its generic artifact adapter in a later slice.
        return ()


def runtime_template() -> ComponentRuntimeTemplate:
    return DEFINITION.runtime_template()


def _runtime_template() -> ComponentRuntimeTemplate:
    return jetbrains_template("pycharm", "bin/pycharm.sh", "PYCHARM_PROPERTIES")


def logical_state_slots() -> tuple[str, ...]:
    template = runtime_template()
    return tuple(template.logical_slot_name(slot.name) for slot in template.persistence.state_slots)




DEFINITION: ComponentDefinition = PyCharmComponent()
