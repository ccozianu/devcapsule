"""IntelliJ IDEA unified distribution, with its own IDE state namespace."""

from collections.abc import Mapping

from devcapsule.components import ComponentDefinition, LockedArtifactDeclaration, SecretInputDeclaration, StateEnvironmentDeclaration
from devcapsule.components.discovery import IntelliJDiscovery
from devcapsule.components.jetbrains import jetbrains_template
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


class IntelliJComponent(ComponentDefinition):
    @property
    def id(self) -> str:
        return "intellij"

    @property
    def capability(self) -> str:
        return "java-ide"

    def discovery_channel(self) -> IntelliJDiscovery:
        return IntelliJDiscovery()

    def channel_omission_reason(self) -> str:
        return "IDE upgrades require a reviewed catalog pin and graphical acceptance."

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return jetbrains_template(self.id, "bin/idea.sh", "IDEA_PROPERTIES")

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(self, metadata: Mapping[str, object], platform: str) -> tuple[LockedArtifactDeclaration, ...]:
        # The surface materializer verifies and installs the whole vendor archive.
        return ()


DEFINITION: ComponentDefinition = IntelliJComponent()
