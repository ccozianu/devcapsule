"""Optional Codex component contract exposed to DevCapsule orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from devcapsule.compat import CliError
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate
from devcapsule.components import (
    ComponentDefinition,
    LockedArtifactDeclaration,
    SecretInputDeclaration,
    StateEnvironmentDeclaration,
)
from devcapsule.components.interface import resolved_state_environment


CODEX_HOME = "/home/devcapsule/.codex"
CODEX_EXECUTABLE = "/usr/local/bin/codex"


class CodexComponent(ComponentDefinition):
    """Trusted Codex component implementation."""

    @property
    def id(self) -> str:
        return "codex"

    @property
    def capability(self) -> str:
        return "codex-agent"

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return (StateEnvironmentDeclaration("CODEX_HOME", "home"),)

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return (
            SecretInputDeclaration(
                name="openai-api-key",
                environment_variable="OPENAI_API_KEY",
                required=False,
                description=(
                    "Optional OpenAI Platform API key. It is visible to all processes in the "
                    "capsule when explicitly delivered through the container environment."
                ),
            ),
        )

    def locked_artifacts(
        self, metadata: Mapping[str, object], platform: str
    ) -> tuple[LockedArtifactDeclaration, ...]:
        if metadata.get("delivery-policy") != "local-materialization":
            raise CliError("components.codex.delivery-policy must be 'local-materialization'.")
        artifacts = metadata.get("artifacts")
        artifact = artifacts.get(platform) if isinstance(artifacts, Mapping) else None
        if not isinstance(artifact, Mapping):
            raise CliError(f"components.codex has no artifact for {platform!r}.")
        version = _string(metadata.get("version"), "components.codex.version")
        return (
            LockedArtifactDeclaration(
                component_id=self.id,
                version=version,
                url=_string(artifact.get("url"), f"components.codex.artifacts.{platform}.url"),
                sha256=_string(
                    artifact.get("sha256"), f"components.codex.artifacts.{platform}.sha256"
                ),
                archive_member=_string(
                    artifact.get("archive-member"),
                    f"components.codex.artifacts.{platform}.archive-member",
                ),
                destination=CODEX_EXECUTABLE,
            ),
        )

    def runtime_template(self) -> ComponentRuntimeTemplate:
        document = _runtime_template_mapping()
        template = ComponentRuntimeTemplate.from_mapping(document)
        environment = resolved_state_environment(template, self.state_environment())
        component = document["component"]
        if not isinstance(component, dict):  # pragma: no cover - local constant is trusted.
            raise AssertionError("Codex component mapping must be a table")
        component["environment"] = environment
        return ComponentRuntimeTemplate.from_mapping(document)


def runtime_template() -> ComponentRuntimeTemplate:
    return DEFINITION.runtime_template()


def _runtime_template_mapping() -> dict[str, Any]:
    return {
        "version": 1,
        "component": {
            "id": "codex",
            "adapter": "ancillary",
            "configuration": {},
            "persistence": {
                "home": "required",
                "xdg": "home-relative",
                "state_slots": [
                    {
                        "name": "home",
                        "container_path": CODEX_HOME,
                        "kind": "durable",
                        "sensitivity": "credentials",
                        "default_scope": "checkout",
                        "storage": "directory",
                        "concurrent": False,
                        "owner": "runtime-user",
                        "permissions": "0700",
                        "reconstructable": False,
                        "deletion_effect": (
                            "Removes Codex authentication, configuration, and local session state."
                        ),
                        "home_overlay": True,
                    }
                ],
            },
        },
    }


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CliError(f"{field} must be a non-empty string.")
    return value


DEFINITION: ComponentDefinition = CodexComponent()
