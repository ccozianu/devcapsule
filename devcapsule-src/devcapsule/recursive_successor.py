"""Detached successor launch and inspection for the recursive dogfood milestone."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Mapping, Sequence

from devcapsule.build_info import current_build_info
from devcapsule.configurations.pycharm import DockerMode, PycharmRunOptions
from devcapsule.configurations.pycharm._launcher import (
    ContainerLifecycle,
    PycharmRunError,
    build_docker_args,
    build_run_config,
    cleanup_temp_runtime_files,
    prepare_temp_runtime_files,
)
from devcapsule.environment_realization import realize_environment
from devcapsule.project import project_namespace
from devcapsule.project_configuration import (
    atomic_write,
    configuration_binding_declarations,
    fresh_resolved_project,
)
from devcapsule.project_runtime_plan import project_runtime_plan
from devcapsule.recursive_dogfood import (
    RUNTIME_PLAN_PATH,
    PreflightReport,
    docker_socket_path,
    run_recursive_preflight,
)
from devcapsule.recursive_host import (
    HostContextError,
    HostDaemonLaunchContext,
    MountRequirement,
    PathAccess,
    PathKind,
)


WORKSPACE_ROOT = Path("/home/devcapsule/.local/share/devcapsule/e2e-workspaces")
OWNER_MARKER = ".devcapsule-e2e-owner.json"
MILESTONE_MANIFEST = "milestone-manifest.json"
SUCCESSOR_ROLE = "successor"
RUN_ID_PATTERN = re.compile(r"[0-9a-f]{16,64}")


class RecursiveSuccessorError(Exception):
    """A retained recursive successor could not be launched or inspected safely."""


@dataclass(frozen=True)
class SuccessorResult:
    run_id: str
    container_id: str
    container_name: str
    image_id: str
    state: str
    checks: Mapping[str, str]

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "container_id": self.container_id,
            "container_name": self.container_name,
            "image_id": self.image_id,
            "state": self.state,
            "checks": dict(self.checks),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_mapping(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def launch_successor(
    checkout: Path,
    run_id: str,
    *,
    runtime_plan_path: Path = RUNTIME_PLAN_PATH,
    environ: Mapping[str, str] | None = None,
    workspace_root: Path = WORKSPACE_ROOT,
) -> SuccessorResult:
    """Launch one retained successor using the normal resolved-project Docker planner."""

    env = dict(os.environ if environ is None else environ)
    run_root, manifest = _load_owned_run(workspace_root, run_id)
    report = run_recursive_preflight(
        checkout,
        runtime_plan_path=runtime_plan_path,
        environ=env,
    )
    if not report.ready or report.container is None:
        raise RecursiveSuccessorError("recursive preflight is not ready for successor launch")

    selected = fresh_resolved_project(checkout)
    realized = realize_environment(selected)
    runtime_plan = project_runtime_plan(selected, realized.locked)
    source_revision = current_build_info().source_revision
    name = f"devcapsule-e2e-{run_id}-successor"
    options = _resolved_run_options(
        selected,
        realized.image.reference,
        runtime_plan,
        name=name,
        source_revision=source_revision,
    )
    config = build_run_config(options, env)

    staging = run_root / "staging"
    try:
        staging.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise RecursiveSuccessorError(
            "successor staging already exists; inspect or clean up the retained run first"
        ) from exc
    staging.chmod(0o700)
    launch_env = dict(env)
    launch_env["XDG_RUNTIME_DIR"] = str(staging)
    files = prepare_temp_runtime_files(config, launch_env)
    launched = False
    container_id: str | None = None
    try:
        args = build_docker_args(
            config,
            files,
            launch_env,
            lifecycle=ContainerLifecycle.detached,
        )
        context = _launch_context(report, config.persistent_home, args)
        host_args = _translate_bind_sources(args, context)
        if files.sudoers_file is not None:
            _make_root_owned(files.sudoers_file, launch_env)
        _write_manifest(
            run_root,
            {
                **manifest,
                "state": "stage-6-launching",
                "launch": {
                    "source_revision": source_revision,
                    "container_name": name,
                    "expected_image_id": realized.image.identity,
                    "role": SUCCESSOR_ROLE,
                },
            },
        )
        completed = subprocess.run(
            ["docker", "run", *host_args, config.image],
            check=False,
            env=launch_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip()
            raise RecursiveSuccessorError(
                "detached successor launch failed" + (f": {detail}" if detail else "")
            )
        container_id = completed.stdout.strip()
        if re.fullmatch(r"[0-9a-f]{64}", container_id) is None:
            raise RecursiveSuccessorError("Docker did not return one exact successor container ID")
        inspection = _inspect_container(container_id, launch_env)
        checks = _validate_inspection(
            inspection,
            run_id=run_id,
            name=name,
            source_revision=source_revision,
            image_id=realized.image.identity,
        )
        launched = True
        _write_manifest(
            run_root,
            {
                **manifest,
                "state": "stage-6-running",
                "launch": {
                    "source_revision": source_revision,
                    "container_id": container_id,
                    "container_name": name,
                    "image_id": realized.image.identity,
                    "formation_identity": realized.image.labels.get(
                        "devcapsule.materialization.identity", ""
                    ),
                    "role": SUCCESSOR_ROLE,
                    "staging_retained": True,
                },
            },
        )
        return SuccessorResult(
            run_id,
            container_id,
            name,
            realized.image.identity,
            "running",
            checks,
        )
    except (HostContextError, OSError, PycharmRunError) as exc:
        raise RecursiveSuccessorError(str(exc)) from exc
    finally:
        if not launched:
            if container_id is not None and re.fullmatch(r"[0-9a-f]{64}", container_id):
                subprocess.run(
                    ["docker", "rm", "--force", container_id],
                    check=False,
                    env=launch_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            cleanup_temp_runtime_files(files)
            try:
                staging.rmdir()
            except OSError:
                pass


def inspect_successor(
    run_id: str,
    *,
    environ: Mapping[str, str] | None = None,
    workspace_root: Path = WORKSPACE_ROOT,
    readiness_timeout: float = 45.0,
) -> SuccessorResult:
    """Inspect exact retained successor identity and probe its selected toolchain."""

    env = dict(os.environ if environ is None else environ)
    run_root, manifest = _load_owned_run(workspace_root, run_id)
    launch = manifest.get("launch")
    if not isinstance(launch, dict):
        raise RecursiveSuccessorError("run manifest has no successor launch evidence")
    required = ("container_id", "container_name", "image_id", "source_revision")
    if not all(isinstance(launch.get(key), str) and launch[key] for key in required):
        raise RecursiveSuccessorError("run manifest has incomplete successor launch evidence")
    container_id = str(launch["container_id"])
    inspection = _inspect_container(container_id, env)
    checks = _validate_inspection(
        inspection,
        run_id=run_id,
        name=str(launch["container_name"]),
        source_revision=str(launch["source_revision"]),
        image_id=str(launch["image_id"]),
    )
    deadline = time.monotonic() + readiness_timeout
    while True:
        probe = _probe_successor(container_id, env)
        if probe.returncode == 0:
            break
        if time.monotonic() >= deadline:
            detail = probe.stderr.strip()
            raise RecursiveSuccessorError(
                "successor readiness probe failed" + (f": {detail}" if detail else "")
            )
        time.sleep(1.0)
    try:
        versions = json.loads(probe.stdout)
    except json.JSONDecodeError as exc:
        raise RecursiveSuccessorError("successor readiness probe returned malformed evidence") from exc
    if not isinstance(versions, dict) or not all(
        isinstance(value, str) and value for value in versions.values()
    ):
        raise RecursiveSuccessorError("successor readiness probe returned incomplete evidence")
    checks = {**checks, **versions}
    _write_manifest(
        run_root,
        {
            **manifest,
            "state": "stage-6-inspection-passed",
            "inspection": {"checks": checks},
        },
    )
    return SuccessorResult(
        run_id,
        container_id,
        str(launch["container_name"]),
        str(launch["image_id"]),
        "inspection-passed",
        checks,
    )


def _resolved_run_options(
    selected: Any,
    image: str,
    runtime_plan: Any,
    *,
    name: str,
    source_revision: str,
) -> PycharmRunOptions:
    runtime = selected.resolution.get("runtime", {})
    state_root = selected.resolution.get("state", {})
    state = dict(state_root.get("adopted", {}))
    state.update(state_root.get("bindings", {}))
    authorization = selected.resolution.get("authorization", {})
    memory_limit = runtime.get("memory-limit-bytes")
    if memory_limit is not None and (
        not isinstance(memory_limit, int) or isinstance(memory_limit, bool) or memory_limit <= 0
    ):
        raise RecursiveSuccessorError("resolved runtime memory limit is invalid")
    if authorization.get("docker-daemon") != "host-socket":
        raise RecursiveSuccessorError("successor checkout has not authorized the host Docker socket")
    if authorization.get("network") != "host":
        raise RecursiveSuccessorError("successor checkout has not authorized host networking")
    if authorization.get("development-sudo") is not True:
        raise RecursiveSuccessorError("successor checkout has not authorized development sudo")
    secret_root = selected.resolution.get("secret", {})
    secret_bindings = secret_root.get("bindings", {}) if isinstance(secret_root, dict) else {}
    secret_environment = (
        secret_bindings.get("host-environment", {})
        if isinstance(secret_bindings, dict)
        else {}
    )
    if not isinstance(secret_environment, dict):
        raise RecursiveSuccessorError("resolved secret environment bindings are invalid")
    return PycharmRunOptions(
        project=selected.root,
        project_mount=str(runtime["project-mount"]),
        image=image,
        name=name,
        persistent_home=Path(state["home"]) if "home" in state else None,
        ide_config=Path(state["pycharm/config"]) if "pycharm/config" in state else None,
        plugins=Path(state["pycharm/plugins"]) if "pycharm/plugins" in state else None,
        ide_system=Path(state["pycharm/system"]) if "pycharm/system" in state else None,
        ide_log=Path(state["pycharm/log"]) if "pycharm/log" in state else None,
        tool_cache=Path(state["pycharm/cache"]) if "pycharm/cache" in state else None,
        docker_mode=DockerMode.host,
        host_docker_socket=docker_socket_path(os.environ.get("DOCKER_HOST")),
        enable_sudo=True,
        network_mode="host",
        memory_limit_bytes=memory_limit,
        runtime_plan=runtime_plan,
        use_image_process=True,
        additional_state_mounts=_additional_component_state_mounts(
            selected.root,
            selected.lock,
            state,
            runtime_plan,
        ),
        additional_environment={"DEVCAPSULE_RECURSIVE_E2E": "1"},
        secret_environment=tuple(sorted(str(value) for value in secret_environment.values())),
        extra_docker_args=[
            "--pull=never",
            "--label",
            "devcapsule.e2e.managed=true",
            "--label",
            f"devcapsule.e2e.run-id={name.removeprefix('devcapsule-e2e-').removesuffix('-successor')}",
            "--label",
            f"devcapsule.e2e.source-revision={source_revision}",
            "--label",
            f"devcapsule.e2e.role={SUCCESSOR_ROLE}",
        ],
    )


def _additional_component_state_mounts(
    root: Path,
    lock: Mapping[str, Any],
    configured_state: Mapping[str, Any],
    runtime_plan: Any,
) -> dict[str, tuple[Path, str]]:
    declarations = configuration_binding_declarations(lock)
    ancillary_ids = {component.id for component in runtime_plan.ancillary_components}
    mounts: dict[str, tuple[Path, str]] = {}
    for name, declaration in declarations.items():
        if declaration.component_id not in ancillary_ids:
            continue
        configured = configured_state.get(name)
        source = (
            Path(str(configured)).expanduser().resolve()
            if configured is not None
            else _managed_binding_path(root, declaration)
        )
        source.mkdir(parents=True, exist_ok=True, mode=0o700)
        if configured is None:
            source.chmod(0o700)
        mounts[name] = (source, declaration.container_path)
    return mounts


def _managed_binding_path(root: Path, declaration: Any) -> Path:
    home = Path(os.environ.get("HOME", "~")).expanduser()
    roots = {
        "durable": Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share"),
        "state": Path(os.environ.get("XDG_STATE_HOME") or home / ".local" / "state"),
        "cache": Path(os.environ.get("XDG_CACHE_HOME") or home / ".cache"),
    }
    namespace = roots[declaration.kind] / "devcapsule" / "projects" / "by-path" / project_namespace(root)
    if declaration.name == "home":
        return namespace / "home"
    return namespace / "components" / str(declaration.component_id) / str(declaration.slot_name)


def _launch_context(
    report: PreflightReport,
    persistent_home: Path,
    docker_args: Sequence[str],
) -> HostDaemonLaunchContext:
    if report.container is None:
        raise RecursiveSuccessorError("preflight has no current-container identity")
    requirements = []
    for index, (source, read_only) in enumerate(_bind_sources(docker_args)):
        kind = _path_kind(source)
        requirements.append(
            MountRequirement(
                f"successor-bind-{index}",
                source,
                PathAccess.read if read_only else PathAccess.write,
                kind,
            )
        )
    return HostDaemonLaunchContext.from_requirements(
        report.container,
        persistent_home=persistent_home,
        requirements=requirements,
    )


def _bind_sources(docker_args: Sequence[str]) -> list[tuple[Path, bool]]:
    sources: list[tuple[Path, bool]] = []
    for index, value in enumerate(docker_args[:-1]):
        if value != "--mount":
            continue
        fields = docker_args[index + 1].split(",")
        if "type=bind" not in fields:
            continue
        source_values = [field.removeprefix("src=") for field in fields if field.startswith("src=")]
        if len(source_values) != 1:
            raise RecursiveSuccessorError("planned bind mount has no unique source")
        sources.append((Path(source_values[0]), "ro" in fields))
    return sources


def _translate_bind_sources(
    docker_args: Sequence[str],
    context: HostDaemonLaunchContext,
) -> list[str]:
    translated = list(docker_args)
    for index, value in enumerate(translated[:-1]):
        if value != "--mount":
            continue
        fields = translated[index + 1].split(",")
        if "type=bind" not in fields:
            continue
        source_indexes = [position for position, field in enumerate(fields) if field.startswith("src=")]
        if len(source_indexes) != 1:
            raise RecursiveSuccessorError("planned bind mount has no unique source")
        position = source_indexes[0]
        source = Path(fields[position].removeprefix("src="))
        result = context.translate(
            source,
            access=PathAccess.read if "ro" in fields else PathAccess.write,
            kind=_path_kind(source),
        )
        fields[position] = f"src={result.host_path}"
        translated[index + 1] = ",".join(fields)
    return translated


def _path_kind(path: Path) -> PathKind:
    if path.is_socket():
        return PathKind.socket
    if path.is_dir():
        return PathKind.directory
    if path.is_file():
        return PathKind.file
    raise RecursiveSuccessorError("planned bind source is missing or unsupported")


def _make_root_owned(path: Path, env: Mapping[str, str]) -> None:
    completed = subprocess.run(
        ["sudo", "-n", "chown", "0:0", str(path)],
        check=False,
        env=dict(env),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0 or path.stat().st_uid != 0:
        raise RecursiveSuccessorError("could not prepare the root-owned sudo policy")


def _inspect_container(container_id: str, env: Mapping[str, str]) -> Mapping[str, Any]:
    completed = subprocess.run(
        ["docker", "inspect", container_id],
        check=False,
        env=dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RecursiveSuccessorError("cannot inspect the exact successor container")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RecursiveSuccessorError("Docker returned malformed successor inspection") from exc
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise RecursiveSuccessorError("Docker returned ambiguous successor inspection")
    return value[0]


def _validate_inspection(
    inspection: Mapping[str, Any],
    *,
    run_id: str,
    name: str,
    source_revision: str,
    image_id: str,
) -> dict[str, str]:
    labels = inspection.get("Config", {}).get("Labels", {})
    expected_labels = {
        "devcapsule.e2e.managed": "true",
        "devcapsule.e2e.run-id": run_id,
        "devcapsule.e2e.source-revision": source_revision,
        "devcapsule.e2e.role": SUCCESSOR_ROLE,
    }
    if inspection.get("Name") != f"/{name}":
        raise RecursiveSuccessorError("successor name does not match the deterministic run name")
    if inspection.get("Image") != image_id:
        raise RecursiveSuccessorError("successor image ID does not match materialization evidence")
    if not isinstance(labels, dict) or any(labels.get(key) != value for key, value in expected_labels.items()):
        raise RecursiveSuccessorError("successor labels do not match exact launch ownership")
    if inspection.get("State", {}).get("Running") is not True:
        raise RecursiveSuccessorError("successor is not running")
    return {
        "container_identity": "pass",
        "image_identity": "pass",
        "labels": "pass",
        "running": "pass",
    }


def _probe_successor(container_id: str, env: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
    script = r'''set -eu
test "${DEVCAPSULE_RECURSIVE_E2E:-}" = 1
test "${DOCKER_HOST:-}" = unix:///run/host-docker.sock
test -S /run/host-docker.sock
test -d /opt/claude
test "${DISABLE_UPDATES:-}" = 1
pgrep -fa pycharm >/dev/null
python3 - <<'PY'
import json, os, subprocess
commands = {
    "claude": ["claude", "--version"],
    "codex": ["codex", "--version"],
    "node": ["node", "--version"],
    "java": ["javac", "--version"],
    "maven": ["mvn", "--version"],
}
result = {}
for name, command in commands.items():
    output = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE).stdout.splitlines()
    result[name] = output[0]
result["java_home"] = os.environ["JAVA_HOME"]
result["maven_home"] = os.environ["MAVEN_HOME"]
result["runtime_plan"] = "pass" if os.path.isfile("/etc/devcapsule/runtime-plan.json") else "fail"
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
PY'''
    return subprocess.run(
        ["docker", "exec", container_id, "/bin/bash", "-lc", script],
        check=False,
        env=dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _load_owned_run(workspace_root: Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise RecursiveSuccessorError("run ID must contain 16 to 64 lowercase hex digits")
    root = workspace_root.expanduser().resolve() / run_id
    if not root.is_dir() or root.is_symlink():
        raise RecursiveSuccessorError("retained run workspace is absent or unsafe")
    marker = _load_json(root / OWNER_MARKER)
    if marker.get("schema_version") != 1 or marker.get("run_id") != run_id:
        raise RecursiveSuccessorError("retained run ownership marker does not match")
    manifest = _load_json(root / MILESTONE_MANIFEST)
    if manifest.get("schema_version") != 1 or manifest.get("run_id") != run_id:
        raise RecursiveSuccessorError("retained run manifest does not match")
    return root, manifest


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecursiveSuccessorError(f"required retained run file is absent or malformed: {path.name}") from exc
    if not isinstance(value, dict):
        raise RecursiveSuccessorError(f"required retained run file is not an object: {path.name}")
    return value


def _write_manifest(run_root: Path, value: Mapping[str, Any]) -> None:
    atomic_write(
        run_root / MILESTONE_MANIFEST,
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        mode=0o600,
    )
