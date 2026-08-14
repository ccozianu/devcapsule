"""Redistributable PostgreSQL client component contract.

Unlike Claude Code, the PostgreSQL client is distributed under the permissive
PostgreSQL License, so DevCapsule can bake it into the base images it publishes
instead of acquiring it per developer. A project therefore declares the
component to state that it needs a database client, and the pinned base
provides it. Nothing is downloaded during local materialization.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from devcapsule.compat import CliError
from devcapsule.components import (
    ComponentDefinition,
    LockedArtifactDeclaration,
    SecretInputDeclaration,
    StateEnvironmentDeclaration,
)
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


POSTGRESQL_CLIENT_EXECUTABLE = "/usr/bin/psql"
POSTGRESQL_CLIENT_DELIVERY_POLICY = "base-image"
POSTGRESQL_CLIENT_LICENSE = "PostgreSQL"


class PostgresqlClientComponent(ComponentDefinition):
    """PostgreSQL command-line client provided by the pinned DevCapsule base."""

    @property
    def id(self) -> str:
        return "postgresql-client"

    @property
    def capability(self) -> str:
        return "postgresql-client"

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        # psql keeps its history and any .pgpass in the developer's home, which
        # the persistent-home binding already covers. No component-owned state
        # slot is needed, so declaring one would only add an unused mount.
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        # Database credentials belong to the project's own configuration rather
        # than to the client component.
        return ()

    def locked_artifacts(
        self, metadata: Mapping[str, object], platform: str
    ) -> tuple[LockedArtifactDeclaration, ...]:
        """Validate the lock entry and contribute no materialization artifact."""

        policy = metadata.get("delivery-policy")
        if policy != POSTGRESQL_CLIENT_DELIVERY_POLICY:
            raise CliError(
                "components.postgresql-client.delivery-policy must be "
                f"{POSTGRESQL_CLIENT_DELIVERY_POLICY!r}."
            )
        if metadata.get("license") != POSTGRESQL_CLIENT_LICENSE:
            raise CliError(
                f"components.postgresql-client.license must be {POSTGRESQL_CLIENT_LICENSE!r}."
            )
        _string(metadata.get("version"), "components.postgresql-client.version")
        if "artifacts" in metadata:
            raise CliError(
                "components.postgresql-client declares artifacts, but a base-image component "
                "is provided by the pinned base rather than materialized."
            )
        return ()

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return ComponentRuntimeTemplate.from_mapping(_runtime_template_mapping())


def runtime_template() -> ComponentRuntimeTemplate:
    return DEFINITION.runtime_template()


def _runtime_template_mapping() -> dict[str, Any]:
    return {
        "version": 1,
        "component": {
            "id": "postgresql-client",
            "adapter": "ancillary",
            "configuration": {},
            "environment": {},
            "persistence": {
                "home": "required",
                "xdg": "home-relative",
                "state_slots": [],
            },
        },
    }


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CliError(f"{field} must be a non-empty string.")
    return value


DEFINITION: ComponentDefinition = PostgresqlClientComponent()
