"""Generate checkout runtime plans without host paths or authorization data."""

from __future__ import annotations

import os
import pwd

from devcapsule.compat import CliError
from devcapsule.container_runtime.contract import (
    ComponentRuntimeTemplate,
    Identity,
    RuntimePlan,
)
from devcapsule.materialization import LockedEnvironment, component_runtime_template
from devcapsule.project_configuration import ResolvedProject


def project_runtime_plan(
    selected: ResolvedProject,
    locked: LockedEnvironment,
    *,
    uid: int | None = None,
    gid: int | None = None,
    user: str | None = None,
) -> RuntimePlan:
    """Build the in-container-only plan for one realized project."""

    runtime = selected.resolution.get("runtime", {})
    if not isinstance(runtime, dict):
        raise CliError("Resolved runtime configuration must be a table.")
    project_mount = runtime.get("project-mount")
    if not isinstance(project_mount, str) or not project_mount:
        raise CliError("Resolved runtime configuration must define project-mount.")

    template = ComponentRuntimeTemplate.from_mapping(component_runtime_template())
    if template.component.id != locked.component_id:
        raise CliError(
            f"Component runtime template selects {template.component.id!r}, "
            f"but realization selected {locked.component_id!r}."
        )

    runtime_uid = os.getuid() if uid is None else uid
    runtime_gid = os.getgid() if gid is None else gid
    runtime_user = pwd.getpwuid(runtime_uid).pw_name if user is None else user
    return RuntimePlan.for_component(
        template,
        project_path=project_mount,
        home="/home/devcapsule",
        identity=Identity(runtime_uid, runtime_gid, runtime_user),
    )
