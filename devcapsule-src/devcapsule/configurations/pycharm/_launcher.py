"""Translated PyCharm launcher for DevCapsule."""

from __future__ import annotations

import grp
import os
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping

from ...container_runtime.contract import RuntimePlan
from ...host_daemon import (
    current_container,
    docker_socket,
    is_host_backed,
    requires_translation,
    translate_bind_sources,
)
from ...host_open import (
    HOST_OPEN_BROWSER,
    HOST_OPEN_INTEGRATION,
    HOST_OPEN_SOCKET_DESTINATION,
    HOST_OPEN_SOCKET_ENV,
    HostOpenError,
    host_open_bridge,
)
from ...materialization import RUNTIME_PLAN_PATH
from ...project import ProjectMountError
from ...runtime import (
    plan_shared_runtime,
    resolve_existing_or_create,
    SharedRuntimeOptions,
)


class PycharmRunError(Exception):
    """User-facing PyCharm launcher error."""


class DockerMode(str, Enum):
    host = "host"
    dind = "dind"
    none = "none"


class IdeConfigMode(str, Enum):
    shared = "shared"
    project = "project"
    custom = "custom"


class ContainerLifecycle(str, Enum):
    foreground = "foreground"
    detached = "detached"


@dataclass(frozen=True)
class HostUser:
    uid: int
    gid: int
    name: str
    group_name: str


@dataclass
class TempRuntimeFiles:
    xauth_file: Path
    passwd_file: Path
    group_file: Path
    shadow_file: Path | None = None
    sudoers_directory: Path | None = None
    sudoers_file: Path | None = None
    token_file: Path | None = None
    runtime_plan_file: Path | None = None


SUDOERS_POLICY_PATH = "/etc/sudoers.d/devcapsule-development-sudo"
SUDOERS_POLICY = "%ide-sudo ALL=(ALL:ALL) NOPASSWD: ALL\n"


@dataclass
class PycharmRunOptions:
    project: Path
    profile: str | None = None
    image: str | None = None
    name: str | None = None
    global_settings: Path | None = None
    persistent_home: Path | None = None
    project_state: Path | None = None
    project_state_root: Path | None = None
    ide_system: Path | None = None
    ide_log: Path | None = None
    tool_cache: Path | None = None
    config_mode: IdeConfigMode | None = None
    ide_config: Path | None = None
    project_mount: str | None = None
    plugins: Path | None = None
    use_ssh_agent: bool = False
    git_user_name: str | None = None
    git_user_email: str | None = None
    git_identity_from_host: str | None = None
    git_token_file: Path | None = None
    git_token_env: str | None = None
    git_token_username: str | None = None
    git_token_hosts: str | None = None
    docker_mode: DockerMode | None = None
    host_docker_socket: Path | None = None
    debug_native: bool = False
    writable_root: bool = False
    enable_sudo: bool = False
    ide_sudo_gid: str | None = None
    ignore_config_lock: bool = False
    network_mode: str = "host"
    memory_limit_bytes: int | None = None
    runtime_plan: RuntimePlan | None = None
    use_image_process: bool = False
    additional_state_mounts: dict[str, tuple[Path, str]] = field(default_factory=dict)
    additional_environment: dict[str, str] = field(default_factory=dict)
    secret_environment: tuple[str, ...] = ()
    extra_docker_args: list[str] = field(default_factory=list)
    enable_host_browser: bool = False


@dataclass
class PycharmRunConfig:
    image: str
    name: str
    project: Path
    global_settings: Path
    persistent_home: Path
    project_state: Path
    ide_system: Path
    ide_log: Path
    tool_cache: Path
    ide_config: Path
    ide_config_mode: str
    plugins: Path
    project_mount: str
    docker_mode: str
    host_docker_socket: Path
    host_docker_gid: int | None
    use_ssh_agent: bool
    git_user_name: str
    git_user_email: str
    git_token_file: Path | None
    git_token_env: str
    git_token_username: str
    git_token_hosts: str
    debug_native: bool
    writable_root: bool
    enable_sudo: bool
    ide_sudo_gid: int
    ignore_config_lock: bool
    network_mode: str
    memory_limit_bytes: int | None
    runtime_plan: RuntimePlan | None
    use_image_process: bool
    host_browser_socket: Path | None = None
    additional_state_mounts: tuple[tuple[str, str, str], ...] = ()
    additional_environment: tuple[tuple[str, str], ...] = ()
    secret_environment: tuple[str, ...] = ()
    extra_docker_args: list[str] = field(default_factory=list)
    libgl_always_software: str = "1"
    mesa_loader_driver_override: str = "llvmpipe"
    libgl_dri3_disable: str = "1"


def run_pycharm(options: PycharmRunOptions, env: Mapping[str, str] | None = None) -> int:
    """Run PyCharm through the translated Python launcher."""

    try:
        runtime_env = host_backed_runtime_environment(
            dict(os.environ if env is None else env)
        )
        with host_open_bridge(
            runtime_env,
            enabled=options.enable_host_browser,
        ) as browser_socket:
            if browser_socket is None:
                runtime_env.pop(HOST_OPEN_SOCKET_ENV, None)
            else:
                runtime_env[HOST_OPEN_SOCKET_ENV] = str(browser_socket)
            config = build_run_config(options, runtime_env)
            files = prepare_temp_runtime_files(config, runtime_env)
            try:
                if config.enable_sudo:
                    ensure_sudoers_policy_ownership(config, files, runtime_env)
                docker_args = build_docker_args(config, files, runtime_env)
                docker_args = translate_for_external_daemon(docker_args, runtime_env)
                print_storage_summary(config)
                if config.enable_sudo:
                    print_sudo_warning()
                command = ["docker", "run", *docker_args, config.image]
                if not config.use_image_process:
                    command.extend(["/opt/pycharm/bin/pycharm.sh", config.project_mount])
                completed = subprocess.run(command, check=False, env=runtime_env)
                return completed.returncode
            finally:
                cleanup_temp_runtime_files(files)
    except HostOpenError as exc:
        raise PycharmRunError(str(exc)) from exc


def host_backed_runtime_environment(env: Mapping[str, str]) -> dict[str, str]:
    """Stage transient launch files where an external daemon can read them.

    The launcher writes an Xauthority, passwd/group, and runtime plan and binds
    them into the container it starts. `XDG_RUNTIME_DIR` normally points at a
    container-local tmpfs, which an external daemon cannot see, so those binds
    would arrive empty. Move the staging directory somewhere backed by a mount.
    """

    runtime_env = dict(env)
    if not requires_translation(runtime_env):
        return runtime_env
    container = current_container(runtime_env)
    existing = runtime_env.get("XDG_RUNTIME_DIR")
    if existing and is_host_backed(Path(existing), container):
        return runtime_env
    data_home = runtime_env.get("XDG_DATA_HOME") or str(
        Path(runtime_env.get("HOME", "~")).expanduser() / ".local/share"
    )
    staging = Path(data_home) / "devcapsule" / "launch-staging"
    try:
        staging.mkdir(parents=True, exist_ok=True)
        staging.chmod(0o700)
    except OSError as exc:
        raise PycharmRunError(f"Cannot prepare a host-backed staging directory: {exc}") from exc
    if not is_host_backed(staging, container):
        raise PycharmRunError(
            f"This launch runs inside a container against an external Docker daemon, but "
            f"{staging} is not backed by any mount of this container, so the daemon cannot "
            "read the launcher's transient files. Set XDG_RUNTIME_DIR to a mounted directory, "
            "or run the launch from the host."
        )
    runtime_env["XDG_RUNTIME_DIR"] = str(staging)
    return runtime_env


def translate_for_external_daemon(
    docker_args: list[str],
    env: Mapping[str, str],
) -> list[str]:
    """Rewrite bind sources when launching from inside a container.

    On the host this is a no-op. Inside a container whose Docker socket comes
    from an external daemon, the daemon resolves bind sources in the host
    filesystem, where this process's paths do not exist. Docker would create
    them as empty directories, so translate them or fail loudly.
    """

    if not requires_translation(env):
        return docker_args
    container = current_container(env)
    translated = translate_bind_sources(docker_args, container)
    print(
        "Launching from inside a container against an external Docker daemon; "
        "bind sources were translated to their host paths.",
        file=sys.stderr,
    )
    return translated


def build_run_config(options: PycharmRunOptions, env: Mapping[str, str]) -> PycharmRunConfig:
    base_data_dir = Path(
        env.get("XDG_DATA_HOME") or str(Path(env.get("HOME", "~")).expanduser() / ".local/share")
    ) / "pycharm-docker"
    profile = options.profile or env.get("DOCKER4IDES_PYCHARM_PROFILE", "")
    host_user = current_host_user()

    docker_mode = initial_docker_mode(env)
    if options.docker_mode is not None:
        docker_mode = options.docker_mode.value

    git_identity_from_host = env.get("PYCHARM_GIT_IDENTITY_FROM_HOST", "auto")
    if options.git_identity_from_host is not None:
        git_identity_from_host = options.git_identity_from_host
    git_identity_from_host = normalize_git_identity_mode(git_identity_from_host)

    ide_config_mode = resolve_ide_config_mode(options, env)

    ignore_config_lock = parse_bool_env(
        env.get("PYCHARM_IGNORE_CONFIG_LOCK", "0"),
        "PYCHARM_IGNORE_CONFIG_LOCK",
    )
    if options.ignore_config_lock:
        ignore_config_lock = True

    enable_sudo = parse_bool_env(env.get("PYCHARM_ENABLE_SUDO", "0"), "PYCHARM_ENABLE_SUDO")
    if options.enable_sudo:
        enable_sudo = True

    ide_sudo_gid_text = options.ide_sudo_gid or env.get("PYCHARM_IDE_SUDO_GID", "44000")
    if not ide_sudo_gid_text.isdigit():
        raise PycharmRunError("PYCHARM_IDE_SUDO_GID must be a numeric group ID.")
    ide_sudo_gid = int(ide_sudo_gid_text)

    writable_root = options.writable_root
    if enable_sudo:
        writable_root = True

    if not env.get("DISPLAY"):
        raise PycharmRunError("DISPLAY is not set; this X11 launcher needs an active X session.")
    if options.network_mode not in {"bridge", "host", "none"}:
        raise PycharmRunError("The Docker network mode must be bridge, host, or none.")
    if options.use_image_process and options.runtime_plan is None:
        raise PycharmRunError("Using the image process requires an external runtime plan.")

    global_settings_default = base_data_dir / "state"

    try:
        runtime_plan = plan_shared_runtime(
            SharedRuntimeOptions(
                project=options.project,
                profile=profile or None,
                global_settings=options.global_settings or env.get("PYCHARM_GLOBAL_SETTINGS_DIR"),
                project_state=options.project_state or env.get("PYCHARM_PROJECT_STATE_DIR"),
                project_state_root=options.project_state_root or env.get("PYCHARM_PROJECT_STATE_ROOT") or None,
                project_mount=options.project_mount or env.get("PYCHARM_PROJECT_MOUNT"),
            ),
            env,
            explicit_profile_root_env_var="DOCKER4IDES_PYCHARM_PROFILE_ROOT",
            profile_dir_prefix="docker-pycharm-",
            default_global_settings=global_settings_default,
            default_project_state=lambda project_plan: base_data_dir / "project-state" / project_plan.project_id,
        )
    except (ProjectMountError, ValueError) as exc:
        raise PycharmRunError(str(exc)) from exc

    project = runtime_plan.project
    if not project.is_dir():
        raise PycharmRunError(f"Project directory does not exist: {project}")

    profile_root = runtime_plan.profile_root
    plugins_default = profile_root / "plugins" if profile_root else base_data_dir / "plugins"
    global_settings = runtime_plan.global_settings
    project_state = runtime_plan.project_state

    xdg_data_home = Path(
        env.get("XDG_DATA_HOME") or str(Path(env.get("HOME", "~")).expanduser() / ".local/share")
    ).expanduser()
    xdg_state_home = Path(
        env.get("XDG_STATE_HOME") or str(Path(env.get("HOME", "~")).expanduser() / ".local/state")
    ).expanduser()
    xdg_cache_home = Path(
        env.get("XDG_CACHE_HOME") or str(Path(env.get("HOME", "~")).expanduser() / ".cache")
    ).expanduser()
    data_namespace = xdg_data_home / "devcapsule" / "projects" / "by-path" / runtime_plan.project_id
    state_namespace = xdg_state_home / "devcapsule" / "projects" / "by-path" / runtime_plan.project_id
    cache_namespace = xdg_cache_home / "devcapsule" / "projects" / "by-path" / runtime_plan.project_id

    legacy_global_settings = (
        options.global_settings is not None
        or bool(env.get("PYCHARM_GLOBAL_SETTINGS_DIR"))
        or bool(profile)
    )
    persistent_home = resolve_existing_or_create(
        options.persistent_home
        or env.get("DEVCAPSULE_HOME_DIR")
        or (global_settings / "home" if legacy_global_settings else data_namespace / "home")
    )

    ide_config_arg = options.ide_config if options.ide_config is not None else env.get("PYCHARM_IDE_CONFIG_DIR", "")
    if ide_config_mode == "shared":
        ide_config = resolve_existing_or_create(
            global_settings / "config"
            if legacy_global_settings
            else data_namespace / "components" / "pycharm" / "config"
        )
    elif ide_config_mode == "project":
        ide_config = resolve_existing_or_create(project_state / "config")
    else:
        if not ide_config_arg:
            raise PycharmRunError(
                "--ide-config or PYCHARM_IDE_CONFIG_DIR is required when PYCHARM_IDE_CONFIG_MODE=custom."
            )
        ide_config = resolve_existing_or_create(ide_config_arg)

    plugins = resolve_existing_or_create(
        options.plugins
        or env.get("PYCHARM_PLUGIN_DIR")
        or (plugins_default if options.profile else data_namespace / "components" / "pycharm" / "plugins")
    )

    legacy_project_state = options.project_state is not None or options.project_state_root is not None
    ide_system = resolve_existing_or_create(
        options.ide_system
        or (project_state / "system"
        if legacy_project_state
        else cache_namespace / "components" / "pycharm" / "system")
    )
    ide_log = resolve_existing_or_create(
        options.ide_log
        or (project_state / "log"
        if legacy_project_state
        else state_namespace / "components" / "pycharm" / "log")
    )
    tool_cache = resolve_existing_or_create(
        options.tool_cache
        or (project_state / "home" / ".cache"
        if legacy_project_state
        else cache_namespace / "components" / "pycharm" / "cache")
    )

    if not ignore_config_lock and ide_config_mode != "project" and (ide_config / ".lock").exists():
        raise PycharmRunError(config_lock_message(ide_config, project, project_state))

    # Inside a container the daemon's socket is wherever it was mounted, which
    # DOCKER_HOST already names. Preferring it over the host default keeps a
    # containerized launch working without the developer restating it.
    host_docker_socket = Path(
        options.host_docker_socket or env.get("HOST_DOCKER_SOCKET") or docker_socket(env)
    )
    host_docker_gid: int | None = None
    if docker_mode == "host":
        if not is_socket(host_docker_socket):
            raise PycharmRunError(
                f"Host Docker socket is not available: {host_docker_socket}\n"
                "Start Docker on the host, set HOST_DOCKER_SOCKET, or launch with --docker-in-docker / --no-docker."
            )
        host_docker_socket = host_docker_socket.resolve()
        host_docker_gid = host_docker_socket.stat().st_gid

    if enable_sudo:
        while ide_sudo_gid in {0, host_user.gid, host_docker_gid}:
            ide_sudo_gid += 1

    git_user_name = options.git_user_name or env.get("PYCHARM_GIT_USER_NAME", "")
    git_user_email = options.git_user_email or env.get("PYCHARM_GIT_USER_EMAIL", "")
    if git_identity_from_host in {"1", "auto"}:
        git_user_name, git_user_email = apply_host_git_identity(
            git_identity_from_host,
            git_user_name,
            git_user_email,
        )

    git_token_file = options.git_token_file or env.get("PYCHARM_GIT_TOKEN_FILE") or env.get("GITHUB_TOKEN_FILE")

    if options.runtime_plan is not None:
        if options.runtime_plan.project_path != runtime_plan.project_mount:
            raise PycharmRunError(
                "The external runtime plan project path does not match the Docker project mount."
            )
        if options.runtime_plan.home != "/home/devcapsule":
            raise PycharmRunError("The external runtime plan home must be /home/devcapsule.")

    additional_state_mounts: list[tuple[str, str, str]] = []
    runtime_slots = options.runtime_plan.slots_by_name() if options.runtime_plan is not None else {}
    ancillary_ids = {
        component.id for component in options.runtime_plan.ancillary_components
    } if options.runtime_plan is not None else set()
    for logical_name, (source, destination) in sorted(options.additional_state_mounts.items()):
        namespace, separator, _local_name = logical_name.partition("/")
        planned_destination = runtime_slots.get(logical_name)
        if not separator or namespace not in ancillary_ids:
            raise PycharmRunError(
                f"Additional state mount {logical_name!r} is not owned by a declared ancillary component."
            )
        if planned_destination is not None and planned_destination != destination:
            raise PycharmRunError(
                f"Additional state mount {logical_name!r} conflicts with the external runtime plan."
            )
        destination_path = Path(destination)
        if not destination_path.is_absolute() or ".." in destination_path.parts:
            raise PycharmRunError(
                f"Additional state mount {logical_name!r} must use an absolute container destination."
            )
        resolved_source = resolve_existing_or_create(source)
        additional_state_mounts.append((logical_name, str(resolved_source), destination))
    host_browser_socket: Path | None = None
    configured_browser_socket = env.get(HOST_OPEN_SOCKET_ENV)
    if options.enable_host_browser and configured_browser_socket:
        candidate = Path(configured_browser_socket)
        if not candidate.is_absolute() or ".." in candidate.parts or not is_socket(candidate):
            raise PycharmRunError("The authorized host-browser socket is absent or unsafe.")
        host_browser_socket = candidate

    selected_runtime_plan = options.runtime_plan
    if host_browser_socket is not None and selected_runtime_plan is not None:
        selected_runtime_plan = selected_runtime_plan.with_host_integration(
            HOST_OPEN_INTEGRATION
        )
    fixed_environment = selected_runtime_plan.component_environment() if selected_runtime_plan else {}
    if host_browser_socket is not None and (
        "BROWSER" in fixed_environment or HOST_OPEN_SOCKET_ENV in fixed_environment
    ):
        raise PycharmRunError(
            "Component runtime metadata conflicts with the host-browser integration."
        )
    additional_environment: list[tuple[str, str]] = []
    for name, value in sorted(options.additional_environment.items()):
        if not name.isascii() or not name.isidentifier() or name.upper() != name:
            raise PycharmRunError(
                f"Additional environment name {name!r} must be an uppercase identifier."
            )
        if not value or "\x00" in value:
            raise PycharmRunError(
                f"Additional environment variable {name!r} must have a non-empty value."
            )
        if name in fixed_environment:
            raise PycharmRunError(
                f"Additional environment variable {name!r} conflicts with component runtime metadata."
            )
        if name in options.secret_environment:
            raise PycharmRunError(
                f"Additional environment variable {name!r} conflicts with a secret binding."
            )
        additional_environment.append((name, value))
    for name in options.secret_environment:
        if name in fixed_environment:
            raise PycharmRunError(
                f"Secret environment variable {name!r} conflicts with component runtime metadata."
            )
        if name not in env:
            raise PycharmRunError(
                f"Bound secret environment variable {name!r} is not set on the host."
            )

    return PycharmRunConfig(
        image=options.image or env.get("IMAGE", "pycharm-isolated:latest"),
        name=options.name or f"pycharm-isolated-{host_user.name}-{int(time.time())}",
        project=project,
        global_settings=global_settings,
        persistent_home=persistent_home,
        project_state=project_state,
        ide_system=ide_system,
        ide_log=ide_log,
        tool_cache=tool_cache,
        ide_config=ide_config,
        ide_config_mode=ide_config_mode,
        plugins=plugins,
        project_mount=runtime_plan.project_mount,
        docker_mode=docker_mode,
        host_docker_socket=host_docker_socket,
        host_docker_gid=host_docker_gid,
        use_ssh_agent=options.use_ssh_agent,
        git_user_name=git_user_name,
        git_user_email=git_user_email,
        git_token_file=Path(git_token_file).expanduser().resolve() if git_token_file else None,
        git_token_env=options.git_token_env or env.get("PYCHARM_GIT_TOKEN_ENV") or env.get("GITHUB_TOKEN_ENV", ""),
        git_token_username=options.git_token_username
        or env.get("PYCHARM_GIT_TOKEN_USERNAME")
        or env.get("GITHUB_USER", "x-access-token"),
        git_token_hosts=options.git_token_hosts or env.get("PYCHARM_GIT_TOKEN_HOSTS", "github.com"),
        debug_native=options.debug_native,
        writable_root=writable_root,
        enable_sudo=enable_sudo,
        ide_sudo_gid=ide_sudo_gid,
        ignore_config_lock=ignore_config_lock,
        network_mode=options.network_mode,
        memory_limit_bytes=options.memory_limit_bytes,
        runtime_plan=selected_runtime_plan,
        use_image_process=options.use_image_process,
        host_browser_socket=host_browser_socket,
        additional_state_mounts=tuple(additional_state_mounts),
        additional_environment=tuple(additional_environment),
        secret_environment=tuple(sorted(set(options.secret_environment))),
        extra_docker_args=list(options.extra_docker_args),
        libgl_always_software=env.get("PYCHARM_LIBGL_ALWAYS_SOFTWARE", env.get("LIBGL_ALWAYS_SOFTWARE", "1")),
        mesa_loader_driver_override=env.get(
            "PYCHARM_MESA_LOADER_DRIVER_OVERRIDE",
            env.get("MESA_LOADER_DRIVER_OVERRIDE", "llvmpipe"),
        ),
        libgl_dri3_disable=env.get("PYCHARM_LIBGL_DRI3_DISABLE", env.get("LIBGL_DRI3_DISABLE", "1")),
    )


def build_docker_args(
    config: PycharmRunConfig,
    files: TempRuntimeFiles,
    env: Mapping[str, str],
    *,
    lifecycle: ContainerLifecycle = ContainerLifecycle.foreground,
) -> list[str]:
    host_user = current_host_user()
    args = [
        *(
            ["--rm", "-i"]
            if lifecycle is ContainerLifecycle.foreground
            else ["--detach"]
        ),
        "--name",
        config.name,
        "--workdir",
        config.project_mount,
        "--env",
        "DISPLAY",
        "--env",
        "XAUTHORITY=/tmp/.docker.xauth",
        "--env",
        f"PROJECT_PATH={config.project_mount}",
        "--env",
        f"DEVCAPSULE_CONTAINER_NAME={config.name}",
        "--env",
        "HOME=/home/devcapsule",
        "--env",
        "XDG_CONFIG_HOME=/home/devcapsule/.config",
        "--env",
        "XDG_CACHE_HOME=/home/devcapsule/.cache",
        "--env",
        "XDG_DATA_HOME=/home/devcapsule/.local/share",
        "--env",
        "IDE_GLOBAL_SETTINGS_PATH=/home/devcapsule",
        "--env",
        "IDE_CONFIG_PATH=/ide-config",
        "--env",
        "IDE_PROJECT_STATE_PATH=/ide-project-state",
        "--env",
        f"IDE_UID={host_user.uid}",
        "--env",
        f"IDE_GID={host_user.gid}",
        "--env",
        f"IDE_USER={host_user.name}",
        "--env",
        "QT_X11_NO_MITSHM=1",
        "--env",
        "_JAVA_AWT_WM_NONREPARENTING=1",
        "--env",
        f"LIBGL_ALWAYS_SOFTWARE={config.libgl_always_software}",
        "--env",
        f"MESA_LOADER_DRIVER_OVERRIDE={config.mesa_loader_driver_override}",
        "--env",
        f"LIBGL_DRI3_DISABLE={config.libgl_dri3_disable}",
        "--mount",
        f"type=bind,src={config.project},dst={config.project_mount}",
        "--mount",
        f"type=bind,src={config.persistent_home},dst=/home/devcapsule",
        "--mount",
        f"type=bind,src={config.ide_config},dst=/ide-config",
        "--mount",
        f"type=bind,src={config.ide_system},dst=/ide-project-state/system",
        "--mount",
        f"type=bind,src={config.ide_log},dst=/ide-project-state/log",
        "--mount",
        f"type=bind,src={config.tool_cache},dst=/home/devcapsule/.cache",
        "--mount",
        f"type=bind,src={config.plugins},dst=/ide-plugins",
        "--mount",
        "type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,ro",
        "--mount",
        f"type=bind,src={files.xauth_file},dst=/tmp/.docker.xauth,ro",
        "--mount",
        f"type=bind,src={files.passwd_file},dst=/etc/passwd,ro",
        "--mount",
        f"type=bind,src={files.group_file},dst=/etc/group,ro",
        "--tmpfs",
        "/tmp:rw,exec,nosuid,nodev,size=2g",
        "--tmpfs",
        "/run:rw,nosuid,nodev,size=128m",
        "--tmpfs",
        "/var/tmp:rw,exec,nosuid,nodev,size=1g",
        "--ipc",
        "private",
        "--network",
        config.network_mode,
        "--pids-limit",
        "4096",
    ]

    if config.runtime_plan is not None:
        for name, value in sorted(config.runtime_plan.component_environment().items()):
            args.extend(["--env", f"{name}={value}"])
    if config.host_browser_socket is not None:
        args.extend(
            [
                "--env",
                f"BROWSER={HOST_OPEN_BROWSER}",
                "--env",
                f"{HOST_OPEN_SOCKET_ENV}={HOST_OPEN_SOCKET_DESTINATION}",
                "--mount",
                (
                    f"type=bind,src={config.host_browser_socket},"
                    f"dst={HOST_OPEN_SOCKET_DESTINATION},ro"
                ),
            ]
        )
    for name, value in config.additional_environment:
        args.extend(["--env", f"{name}={value}"])
    for name in config.secret_environment:
        args.extend(["--env", name])

    for _logical_name, source, destination in config.additional_state_mounts:
        args.extend(["--mount", f"type=bind,src={source},dst={destination}"])

    if config.enable_sudo:
        if files.shadow_file is None or files.sudoers_file is None:
            raise PycharmRunError(
                "Development sudo requires generated shadow and sudoers files."
            )
        args.extend(["--mount", f"type=bind,src={files.shadow_file},dst=/etc/shadow,ro"])
        args.extend(
            [
                "--mount",
                f"type=bind,src={files.sudoers_file},dst={SUDOERS_POLICY_PATH},ro",
            ]
        )
    if files.runtime_plan_file is not None:
        args.extend(
            [
                "--mount",
                f"type=bind,src={files.runtime_plan_file},dst={RUNTIME_PLAN_PATH},ro",
            ]
        )
    if config.git_user_name:
        args.extend(["--env", f"GIT_USER_NAME={config.git_user_name}"])
    if config.git_user_email:
        args.extend(["--env", f"GIT_USER_EMAIL={config.git_user_email}"])

    append_docker_mode_args(args, config, host_user)

    if not config.writable_root and config.docker_mode != "dind":
        args.append("--read-only")
    if config.debug_native and config.docker_mode != "dind":
        args.extend(["--cap-add", "SYS_PTRACE", "--security-opt", "seccomp=unconfined"])

    if config.use_ssh_agent:
        ssh_auth_sock = env.get("SSH_AUTH_SOCK", "")
        if not ssh_auth_sock or not is_socket(Path(ssh_auth_sock)):
            raise PycharmRunError("--ssh-agent was requested, but SSH_AUTH_SOCK is not a socket.")
        args.extend(
            [
                "--mount",
                f"type=bind,src={ssh_auth_sock},dst=/run/host-ssh-agent.sock",
                "--env",
                "SSH_AUTH_SOCK=/run/host-ssh-agent.sock",
            ]
        )

    git_token_file = resolve_git_token_file(config, files, env)
    if git_token_file:
        args.extend(
            [
                "--mount",
                f"type=bind,src={git_token_file},dst=/run/secrets/git-token,ro",
                "--env",
                "GIT_TOKEN_FILE=/run/secrets/git-token",
                "--env",
                f"GIT_TOKEN_USERNAME={config.git_token_username}",
                "--env",
                f"GIT_TOKEN_HOSTS={config.git_token_hosts}",
            ]
        )

    if config.memory_limit_bytes is not None:
        if config.memory_limit_bytes <= 0:
            raise PycharmRunError("The container memory limit must be positive.")
        args.extend(["--memory", str(config.memory_limit_bytes)])
    args.extend(config.extra_docker_args)
    return args


def append_docker_mode_args(args: list[str], config: PycharmRunConfig, host_user: HostUser) -> None:
    if config.docker_mode == "host":
        print_host_docker_warning(config)
        args.extend(
            [
                "--user",
                f"{host_user.uid}:{host_user.gid}",
                "--group-add",
                str(config.host_docker_gid),
                "--env",
                "ENABLE_DIND=0",
                "--env",
                f"ENABLE_SUDO={int(config.enable_sudo)}",
                "--env",
                f"IDE_SUDO_GID={config.ide_sudo_gid}",
                "--env",
                "DOCKER_HOST=unix:///run/host-docker.sock",
                "--mount",
                f"type=bind,src={config.host_docker_socket},dst=/run/host-docker.sock",
            ]
        )
        append_sudo_or_restrictions(args, config)
    elif config.docker_mode == "dind":
        print_dind_warning(config)
        args.extend(
            [
                "--privileged",
                "--env",
                "ENABLE_DIND=1",
                "--env",
                f"ENABLE_SUDO={int(config.enable_sudo)}",
                "--env",
                f"IDE_SUDO_GID={config.ide_sudo_gid}",
                "--mount",
                "type=volume,dst=/var/lib/docker",
            ]
        )
        if config.enable_sudo:
            args.extend(["--group-add", str(config.ide_sudo_gid)])
    else:
        args.extend(
            [
                "--user",
                f"{host_user.uid}:{host_user.gid}",
                "--env",
                "ENABLE_DIND=0",
                "--env",
                f"ENABLE_SUDO={int(config.enable_sudo)}",
                "--env",
                f"IDE_SUDO_GID={config.ide_sudo_gid}",
            ]
        )
        append_sudo_or_restrictions(args, config)


def append_sudo_or_restrictions(args: list[str], config: PycharmRunConfig) -> None:
    if config.enable_sudo:
        args.extend(["--group-add", str(config.ide_sudo_gid)])
    else:
        args.extend(["--cap-drop", "ALL", "--security-opt", "no-new-privileges"])


def prepare_temp_runtime_files(config: PycharmRunConfig, env: Mapping[str, str]) -> TempRuntimeFiles:
    runtime_parent = Path(env.get("XDG_RUNTIME_DIR", "/tmp"))
    runtime_parent.mkdir(parents=True, exist_ok=True)
    files = TempRuntimeFiles(
        xauth_file=make_temp(runtime_parent, "pycharm-docker-xauth."),
        passwd_file=make_temp(runtime_parent, "pycharm-docker-passwd."),
        group_file=make_temp(runtime_parent, "pycharm-docker-group."),
    )
    try:
        write_xauthority(files.xauth_file, env)
        write_user_files(config, files)
        if config.enable_sudo:
            files.sudoers_directory = Path(
                tempfile.mkdtemp(prefix="devcapsule-sudoers.", dir=runtime_parent)
            )
            files.sudoers_directory.chmod(0o700)
            files.sudoers_file = files.sudoers_directory / "policy"
            files.sudoers_file.write_text(SUDOERS_POLICY, encoding="utf-8")
            files.sudoers_file.chmod(0o440)
        if config.runtime_plan is not None:
            files.runtime_plan_file = make_temp(runtime_parent, "devcapsule-runtime-plan.")
            files.runtime_plan_file.write_text(config.runtime_plan.to_json() + "\n", encoding="utf-8")
            files.runtime_plan_file.chmod(0o644)
        return files
    except BaseException:
        cleanup_temp_runtime_files(files)
        raise


def make_temp(parent: Path, prefix: str) -> Path:
    fd, name = tempfile.mkstemp(prefix=prefix, dir=parent)
    os.close(fd)
    return Path(name)


def write_xauthority(xauth_file: Path, env: Mapping[str, str]) -> None:
    if shutil.which("xauth"):
        nlist = subprocess.run(
            ["xauth", "nlist", env.get("DISPLAY", "")],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if nlist.stdout:
            family_wild = "".join(f"ffff{line[4:]}" for line in nlist.stdout.splitlines(keepends=True))
            subprocess.run(
                ["xauth", "-f", str(xauth_file), "nmerge", "-"],
                input=family_wild,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
    xauth_file.chmod(0o600)
    if xauth_file.stat().st_size == 0:
        # Deliberately no `xhost +SI:localuser:...` advice here: that command
        # widens host X access control, and this launcher must not teach users
        # to weaken the very boundary the product exists to keep.
        print(
            "Warning: no Xauthority cookie was copied, so PyCharm may be unable to open a window. "
            "Note that host X11 passthrough already hands the capsule your X session credential "
            "(keystroke capture, window capture, input injection, clipboard); a contained display "
            "that closes this exposure is in development.",
            file=sys.stderr,
        )


def write_user_files(config: PycharmRunConfig, files: TempRuntimeFiles) -> None:
    host_user = current_host_user()
    files.passwd_file.write_text(
        "\n".join(
            [
                "root:x:0:0:root:/root:/bin/bash",
                f"{host_user.name}:x:{host_user.uid}:{host_user.gid}:PyCharm Docker User:/home/devcapsule:/bin/bash",
                "",
            ]
        )
    )
    group_lines = [
        "root:x:0:",
        f"{host_user.group_name}:x:{host_user.gid}:",
    ]
    if config.host_docker_gid is not None and config.host_docker_gid != host_user.gid:
        group_lines.append(f"host-docker:x:{config.host_docker_gid}:")
    if config.enable_sudo:
        group_lines.append(f"ide-sudo:x:{config.ide_sudo_gid}:{host_user.name}")
        files.shadow_file = make_temp(files.group_file.parent, "pycharm-docker-shadow.")
        shadow_last_change = int(time.time()) // 86400
        files.shadow_file.write_text(
            "\n".join(
                [
                    f"root:*:{shadow_last_change}:0:99999:7:::",
                    f"{host_user.name}:*:{shadow_last_change}:0:99999:7:::",
                    "",
                ]
            )
        )
        files.shadow_file.chmod(0o600)
    files.group_file.write_text("\n".join([*group_lines, ""]))
    files.passwd_file.chmod(0o644)
    files.group_file.chmod(0o644)


def ensure_sudoers_policy_ownership(
    config: PycharmRunConfig,
    files: TempRuntimeFiles,
    env: Mapping[str, str],
) -> None:
    policy = files.sudoers_file
    if not config.enable_sudo or policy is None:
        raise PycharmRunError("Development sudo requires a generated sudoers policy.")
    try:
        os.chown(policy, 0, 0)
    except PermissionError:
        destination = "/run/devcapsule-sudoers-policy"
        command = [
            "docker",
            "run",
            "--rm",
            "--pull=never",
            "--network",
            "none",
            "--read-only",
            "--pids-limit",
            "64",
            "--cap-drop",
            "ALL",
            "--cap-add",
            "CHOWN",
            "--security-opt",
            "no-new-privileges",
            "--user",
            "0:0",
            "--mount",
            f"type=bind,src={policy},dst={destination}",
            "--entrypoint",
            "/bin/chown",
            config.image,
            "0:0",
            destination,
        ]
        completed = subprocess.run(
            command,
            check=False,
            env=dict(env),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip()
            suffix = f": {detail}" if detail else "."
            raise PycharmRunError(
                "Could not prepare the root-owned development-sudo policy" + suffix
            )
    if file_owner_uid(policy) != 0:
        raise PycharmRunError(
            "Development-sudo policy ownership is not root after preparation."
        )


def file_owner_uid(path: Path) -> int:
    return path.stat().st_uid


def resolve_git_token_file(
    config: PycharmRunConfig,
    files: TempRuntimeFiles,
    env: Mapping[str, str],
) -> Path | None:
    git_token_file = config.git_token_file
    if config.git_token_env:
        token = env.get(config.git_token_env, "")
        if not token:
            raise PycharmRunError(
                f"--git-token-env {config.git_token_env} was requested, but that variable is empty or unset."
            )
        token_file = make_temp(Path(env.get("XDG_RUNTIME_DIR", "/tmp")), "pycharm-docker-git-token.")
        token_file.write_text(token)
        token_file.chmod(0o600)
        files.token_file = token_file
        git_token_file = token_file

    if git_token_file:
        git_token_file = git_token_file.expanduser().resolve()
        if not os.access(git_token_file, os.R_OK):
            raise PycharmRunError(f"Git token file is not readable: {git_token_file}")
    return git_token_file


def cleanup_temp_runtime_files(files: TempRuntimeFiles) -> None:
    for path in [
        files.xauth_file,
        files.passwd_file,
        files.group_file,
        files.shadow_file,
        files.sudoers_file,
        files.token_file,
        files.runtime_plan_file,
    ]:
        if path:
            path.unlink(missing_ok=True)
    if files.sudoers_directory:
        try:
            files.sudoers_directory.rmdir()
        except FileNotFoundError:
            pass


def initial_docker_mode(env: Mapping[str, str]) -> str:
    if env.get("DOCKER_MODE"):
        return normalize_docker_mode(env["DOCKER_MODE"])
    if env.get("DOCKER_IN_DOCKER"):
        dind = env["DOCKER_IN_DOCKER"]
        if dind in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}:
            return "dind"
        if dind in {"0", "false", "FALSE", "no", "NO", "off", "OFF"}:
            return "none"
        raise PycharmRunError("DOCKER_IN_DOCKER must be 1/0, true/false, yes/no, or on/off.")
    return "host"


def resolve_ide_config_mode(options: PycharmRunOptions, env: Mapping[str, str]) -> str:
    if options.config_mode is not None:
        return options.config_mode.value
    if options.ide_config is not None:
        return "custom"
    if env.get("PYCHARM_IDE_CONFIG_MODE"):
        return normalize_ide_config_mode(env["PYCHARM_IDE_CONFIG_MODE"])
    if env.get("PYCHARM_IDE_CONFIG_DIR"):
        return "custom"
    return "shared"


def normalize_docker_mode(value: str) -> str:
    if value in {"host", "HOST", "docker", "DOCKER", "socket", "SOCKET"}:
        return "host"
    if value in {"dind", "DIND", "docker-in-docker", "DOCKER-IN-DOCKER"}:
        return "dind"
    if value in {"none", "NONE", "off", "OFF", "no", "NO", "false", "FALSE", "0"}:
        return "none"
    raise PycharmRunError("DOCKER_MODE must be host, dind, or none.")


def normalize_git_identity_mode(value: str) -> str:
    if value in {"auto", "AUTO", "default", "DEFAULT"}:
        return "auto"
    if value in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}:
        return "1"
    if value in {"0", "false", "FALSE", "no", "NO", "off", "OFF", ""}:
        return "0"
    raise PycharmRunError("PYCHARM_GIT_IDENTITY_FROM_HOST must be auto, 1/0, true/false, yes/no, or on/off.")


def normalize_ide_config_mode(value: str) -> str:
    if value in {"shared", "SHARED"}:
        return "shared"
    if value in {"project", "PROJECT", "per-project", "PER-PROJECT"}:
        return "project"
    if value in {"custom", "CUSTOM", "explicit", "EXPLICIT"}:
        return "custom"
    raise PycharmRunError("PYCHARM_IDE_CONFIG_MODE must be shared, project, or custom.")


def parse_bool_env(value: str, name: str) -> bool:
    if value in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}:
        return True
    if value in {"0", "false", "FALSE", "no", "NO", "off", "OFF", ""}:
        return False
    raise PycharmRunError(f"{name} must be 1/0, true/false, yes/no, or on/off.")


def apply_host_git_identity(mode: str, name: str, email: str) -> tuple[str, str]:
    if shutil.which("git") is None:
        if mode == "1":
            raise PycharmRunError("--git-identity-from-host was requested, but git is not installed on the host.")
    else:
        if not name:
            name = git_config_value("user.name")
        if not email:
            email = git_config_value("user.email")
    if not name or not email:
        if mode == "1":
            print("Warning: --git-identity-from-host did not find both host user.name and user.email.", file=sys.stderr)
        else:
            print("Warning: no complete Git author identity was provided or found in host global Git config.", file=sys.stderr)
        print(
            "Pass --git-user-name and --git-user-email, or launch with --no-git-identity-from-host to suppress host identity lookup.",
            file=sys.stderr,
        )
    return name, email


def git_config_value(key: str) -> str:
    completed = subprocess.run(
        ["git", "config", "--global", "--get", key],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return completed.stdout.strip()


def is_socket(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISSOCK(mode)


def current_host_user() -> HostUser:
    uid = os.getuid()
    gid = os.getgid()
    return HostUser(
        uid=uid,
        gid=gid,
        name=pwd.getpwuid(uid).pw_name,
        group_name=grp.getgrgid(gid).gr_name,
    )


def config_lock_message(ide_config: Path, project: Path, project_state: Path) -> str:
    return f"""PyCharm config directory appears to be locked:
  {ide_config / ".lock"}

The default shared config directory can only be used by one live PyCharm
process at a time. For concurrent sessions against different projects, launch
the second IDE with:
  devcapsule pycharm run --project "{project}" --project-config

That stores JetBrains idea.config.path under the per-project state directory:
  {project_state / "config"}

If you are sure this is a stale lock from a crashed IDE, remove the lock file
or rerun with --ignore-config-lock to let PyCharm decide."""


def print_storage_summary(config: PycharmRunConfig) -> None:
    browser_disclosure = ""
    if config.runtime_plan is not None:
        properties = config.runtime_plan.component.configuration.get("additional_properties", {})
        if isinstance(properties, dict) and properties.get("ide.browser.jcef.sandbox.enable") == "false":
            browser_disclosure = """

Embedded browser security:
  JCEF's inner Chromium sandbox is disabled for V1 container compatibility.
  Embedded content inherits the IDE user's project, state, network, and any
  separately authorized Docker access. Docker's outer isolation is unchanged."""
    host_browser_disclosure = ""
    if config.host_browser_socket is not None:
        host_browser_disclosure = """

Host browser integration:
  Enabled through a URL-only HTTP(S) broker. Any process running as the
  capsule user can ask the physical host to navigate its default browser."""
    print(
        f"""PyCharm storage:
  Persistent home:       {config.persistent_home}
  PyCharm config:         {config.ide_config} ({config.ide_config_mode})
  Shared plugins:         {config.plugins}
  PyCharm system:         {config.ide_system}
  PyCharm logs:           {config.ide_log}
  Tool cache:             {config.tool_cache}
  Container project path: {config.project_mount}{browser_disclosure}{host_browser_disclosure}""",
        file=sys.stderr,
    )


def print_host_docker_warning(config: PycharmRunConfig) -> None:
    print(
        f"""========================================================================
HOST DOCKER DAEMON IS CONNECTED TO THIS PYCHARM CONTAINER.

The launcher is mounting the host Docker socket:
  {config.host_docker_socket}

Docker commands inside PyCharm/Codex operate on the host daemon. This is the
default local-development convenience mode, but it gives tools inside the IDE
broad control over host Docker images, containers, networks, and bind mounts.

For an isolated inner daemon, run:
  devcapsule pycharm run --project "{config.project}" --docker-in-docker

For a higher-isolation session with no Docker access, run:
  devcapsule pycharm run --project "{config.project}" --no-docker
========================================================================""",
        file=sys.stderr,
    )


def print_dind_warning(config: PycharmRunConfig) -> None:
    print(
        f"""========================================================================
DOCKER-IN-DOCKER IS ENABLED FOR THIS PYCHARM CONTAINER.

The launcher is starting this IDE container with --privileged, a writable
root filesystem, and an inner Docker daemon. Use this when you want separate
Docker images, containers, and volumes inside the PyCharm environment.
The inner daemon does not manage bridge/iptables networking; use --network host
for inner builds that need network access.

To use the default host Docker daemon instead, run:
  devcapsule pycharm run --project "{config.project}" --docker

To turn Docker off for a higher-isolation session, run:
  devcapsule pycharm run --project "{config.project}" --no-docker
========================================================================""",
        file=sys.stderr,
    )


def print_sudo_warning() -> None:
    print(
        """========================================================================
DEVELOPMENT SUDO IS ENABLED FOR THIS PYCHARM CONTAINER.

The mapped IDE user can run passwordless sudo inside the container. The
launcher is also using a writable root filesystem and preserving the default
Docker container capabilities so package installs and similar development
commands can work.

This is a development convenience profile. Use the default launcher profile
when you do not need sudo.
========================================================================""",
        file=sys.stderr,
    )
