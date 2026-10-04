"""JetBrains Rider .NET IDE, with its own IDE state namespace."""

from collections.abc import Mapping

from devcapsule.components import ComponentDefinition, LockedArtifactDeclaration, SecretInputDeclaration, StateEnvironmentDeclaration
from devcapsule.components.discovery import RiderDiscovery
from devcapsule.components.jetbrains import jetbrains_template
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


class RiderComponent(ComponentDefinition):
    @property
    def id(self) -> str:
        return "rider"

    @property
    def capability(self) -> str:
        return "dotnet-ide"

    def discovery_channel(self) -> RiderDiscovery:
        return RiderDiscovery()

    def channel_omission_reason(self) -> str:
        return "IDE upgrades require a reviewed catalog pin and graphical acceptance."

    def required_components(self) -> tuple[str, ...]:
        return ("dotnet-sdk",)

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return jetbrains_template(self.id, "bin/rider.sh", "RIDER_PROPERTIES", recover_directory_lock=True)

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(self, metadata: Mapping[str, object], platform: str) -> tuple[LockedArtifactDeclaration, ...]:
        # The surface materializer verifies and installs the whole vendor archive.
        return ()


DEFINITION: ComponentDefinition = RiderComponent()
