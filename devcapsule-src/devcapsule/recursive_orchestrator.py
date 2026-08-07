"""Public dry-run orchestration for DevCapsule's recursive dogfood E2E."""

from __future__ import annotations

from dataclasses import dataclass
import grp
import json
import os
from pathlib import Path
import secrets
from typing import Mapping

from devcapsule.container_runtime.contract import RuntimePlan, RuntimePlanError
from devcapsule.recursive_dogfood import (
    RUNTIME_PLAN_PATH,
    X11_SOCKET_DIRECTORY,
    PreflightError,
    PreflightReport,
    docker_socket_path,
    require_recursive_e2e_project,
    run_recursive_preflight,
)
from devcapsule.recursive_host import (
    HostContextError,
    HostDaemonLaunchContext,
    PathKind,
    PlannedBindMount,
    RecursiveStagingArea,
    StagedLaunchFiles,
)


HOST_DOCKER_DESTINATION = "/run/host-docker.sock"


class RecursiveE2EError(PreflightError):
    """The recursive E2E dry run could not be planned safely."""

    def __init__(
        self,
        message: str,
        *,
        preserved_workspace: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.preserved_workspace = preserved_workspace


class RecursivePreflightFailed(RecursiveE2EError):
    """The public preflight rejected recursive execution."""

    def __init__(self, report: PreflightReport) -> None:
        super().__init__("recursive dogfood preflight is not ready")
        self.report = report


@dataclass(frozen=True)
class RecursiveDryRunResult:
    """Sanitized evidence produced by the mutation-free Docker planning slice."""

    run_id: str
    preflight: PreflightReport
    launch_context: HostDaemonLaunchContext
    staged_launch: StagedLaunchFiles
    bind_mounts: tuple[PlannedBindMount, ...]
    cleanup_complete: bool

    def to_mapping(self, *, show_host_paths: bool = False) -> dict[str, object]:
        return {
            "schema_version": 1,
            "mode": "dry-run",
            "run_id": self.run_id,
            "preflight": self.preflight.to_mapping(show_host_paths=show_host_paths),
            "launch_context": self.launch_context.to_mapping(
                show_host_paths=show_host_paths
            ),
            "staging": self.staged_launch.to_mapping(show_host_paths=show_host_paths),
            "bind_mounts": [
                item.to_mapping(show_host_paths=show_host_paths)
                for item in self.bind_mounts
            ],
            "docker_mutation_performed": False,
            "cleanup_complete": self.cleanup_complete,
        }

    def to_json(self, *, show_host_paths: bool = False) -> str:
        return json.dumps(
            self.to_mapping(show_host_paths=show_host_paths),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def run_recursive_e2e_dry_run(
    checkout: Path,
    *,
    runtime_plan_path: Path = RUNTIME_PLAN_PATH,
    environ: Mapping[str, str] | None = None,
    keep_on_failure: bool = False,
    run_id: str | None = None,
) -> RecursiveDryRunResult:
    """Preflight and safely compose the first recursive E2E orchestration slice."""

    env = dict(os.environ if environ is None else environ)
    report = run_recursive_preflight(
        checkout,
        runtime_plan_path=runtime_plan_path,
        environ=env,
    )
    if not report.ready:
        raise RecursivePreflightFailed(report)
    return prepare_recursive_e2e_dry_run(
        report,
        checkout=checkout,
        runtime_plan_path=runtime_plan_path,
        environ=env,
        keep_on_failure=keep_on_failure,
        run_id=run_id,
    )


def prepare_recursive_e2e_dry_run(
    preflight: PreflightReport,
    *,
    checkout: Path,
    runtime_plan_path: Path = RUNTIME_PLAN_PATH,
    environ: Mapping[str, str] | None = None,
    keep_on_failure: bool = False,
    run_id: str | None = None,
) -> RecursiveDryRunResult:
    """Compose staging and host bind plans from already-validated preflight evidence."""

    env = dict(os.environ if environ is None else environ)
    project_root = require_recursive_e2e_project(checkout)
    selected_runtime_plan = runtime_plan_path.expanduser().resolve()
    try:
        runtime_plan = RuntimePlan.from_file(selected_runtime_plan)
    except RuntimePlanError as exc:
        raise RecursiveE2EError(f"cannot load the recursive runtime plan: {exc}") from exc

    selected_docker_socket = docker_socket_path(env.get("DOCKER_HOST"))
    xauthority_value = env.get("XAUTHORITY")
    if not xauthority_value:
        raise RecursiveE2EError("XAUTHORITY is required for recursive successor planning")
    xauthority = Path(xauthority_value).expanduser().resolve()
    state_paths = tuple(Path(slot.path) for slot in runtime_plan.state_slots)
    try:
        context = HostDaemonLaunchContext.for_recursive_dogfood(
            preflight,
            persistent_home=Path(runtime_plan.home),
            project=project_root,
            runtime_plan=selected_runtime_plan,
            docker_socket=selected_docker_socket,
            x11_socket_directory=X11_SOCKET_DIRECTORY,
            xauthority=xauthority,
            state_paths=state_paths,
        )
        host_docker_gid = selected_docker_socket.stat().st_gid
    except (HostContextError, OSError) as exc:
        raise RecursiveE2EError(str(exc)) from exc

    selected_run_id = run_id or secrets.token_hex(16)
    staging = RecursiveStagingArea(
        context,
        selected_run_id,
        keep_on_failure=keep_on_failure,
    )
    try:
        with staging:
            staged_launch = staging.prepare_launch_files(
                runtime_plan,
                xauthority=xauthority,
                host_docker_gid=host_docker_gid,
                sudo_gid=_optional_group_id("ide-sudo"),
            )
            binds = _planned_runtime_binds(
                context,
                project_root=project_root,
                runtime_plan=runtime_plan,
                docker_socket=selected_docker_socket,
                state_paths=state_paths,
                staged_launch=staged_launch,
            )
    except (HostContextError, OSError) as exc:
        preserved = (
            staging.run_root
            if keep_on_failure and staging.run_root.exists()
            else None
        )
        suffix = f"; preserved owned workspace {preserved}" if preserved else ""
        raise RecursiveE2EError(
            f"recursive dry-run preparation failed: {exc}{suffix}",
            preserved_workspace=preserved,
        ) from exc

    return RecursiveDryRunResult(
        run_id=selected_run_id,
        preflight=preflight,
        launch_context=context,
        staged_launch=staged_launch,
        bind_mounts=binds,
        cleanup_complete=not staging.run_root.exists(),
    )


def _planned_runtime_binds(
    context: HostDaemonLaunchContext,
    *,
    project_root: Path,
    runtime_plan: RuntimePlan,
    docker_socket: Path,
    state_paths: tuple[Path, ...],
    staged_launch: StagedLaunchFiles,
) -> tuple[PlannedBindMount, ...]:
    binds = [
        context.plan_bind(
            project_root,
            runtime_plan.project_path,
            read_only=False,
            kind=PathKind.directory,
        ),
        context.plan_bind(
            Path(runtime_plan.home),
            runtime_plan.home,
            read_only=False,
            kind=PathKind.directory,
        ),
        context.plan_bind(
            docker_socket,
            HOST_DOCKER_DESTINATION,
            read_only=False,
            kind=PathKind.socket,
        ),
        context.plan_bind(
            X11_SOCKET_DIRECTORY,
            str(X11_SOCKET_DIRECTORY),
            read_only=True,
            kind=PathKind.directory,
        ),
    ]
    binds.extend(
        context.plan_bind(
            source,
            slot.path,
            read_only=False,
            kind=PathKind.directory,
        )
        for source, slot in zip(state_paths, runtime_plan.state_slots, strict=True)
    )
    binds.extend(staged_launch.bind_mounts)
    return tuple(binds)


def _optional_group_id(name: str) -> int | None:
    try:
        return grp.getgrnam(name).gr_gid
    except KeyError:
        return None
