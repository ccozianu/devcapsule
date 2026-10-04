"""Pinned Linux .NET SDK, including its matching runtime and targeting packs."""

from collections.abc import Mapping

from devcapsule.compat import CliError
from devcapsule.components import ComponentDefinition, LockedArtifactDeclaration, SecretInputDeclaration, StateEnvironmentDeclaration
from devcapsule.components.discovery import DotnetDiscovery
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate

ENVIRONMENT = (("DOTNET_ROOT", "/opt/dotnet"), ("DOTNET_CLI_TELEMETRY_OPTOUT", "1"),
               ("DOTNET_NOLOGO", "1"))


class DotnetSdkComponent(ComponentDefinition):
    @property
    def id(self) -> str:
        return "dotnet-sdk"

    @property
    def capability(self) -> str:
        return "dotnet"

    def discovery_channel(self) -> DotnetDiscovery:
        return DotnetDiscovery()

    def channel_omission_reason(self) -> str:
        return "SDK upgrades require a reviewed catalog pin and build/run acceptance."

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return ComponentRuntimeTemplate.from_mapping({
            "version": 1,
            "component": {
                "id": self.id, "adapter": "ancillary", "configuration": {},
                "environment": dict(ENVIRONMENT),
                "persistence": {"home": "required", "xdg": "home-relative", "state_slots": []},
            },
        })

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(self, metadata: Mapping[str, object], platform: str) -> tuple[LockedArtifactDeclaration, ...]:
        if metadata.get("delivery-policy") != "local-materialization" or metadata.get("platform") != platform:
            raise CliError(".NET SDK requires a local-materialization pin for the selected platform.")
        values = []
        for key in ("version", "url", "sha256"):
            value = metadata.get(key)
            if not isinstance(value, str) or not value:
                raise CliError(f"components.dotnet-sdk.{key} must be a non-empty string.")
            values.append(value)
        version, url, sha256 = values
        return (LockedArtifactDeclaration(
            self.id, version, url, sha256, "/opt/dotnet", artifact_format="tar-gz-directory",
            environment=(*ENVIRONMENT, ("PATH", "/opt/dotnet:${PATH}")),
        ),)


DEFINITION: ComponentDefinition = DotnetSdkComponent()
