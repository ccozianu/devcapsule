"""Docker launcher for VSCodium plus Claude Code."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from devcapsule.compat import CliError
from devcapsule.runtime import SharedRuntimeOptions, plan_shared_runtime

DEFAULT_IMAGE = "codium-with-claude:latest"


@dataclass(frozen=True)
class CodiumRunOptions:
    project: Path
    profile: str | None = None
    image: str = DEFAULT_IMAGE
    name: str | None = None
    state: Path | None = None
    project_state: Path | None = None
    project_state_root: Path | None = None
    project_mount: str | None = None
    network: str | None = None
    debug_shell: bool = False
    extra_docker_args: tuple[str, ...] = ()


def build_codium_run_command(options: CodiumRunOptions, env: Mapping[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    project = options.project.expanduser().resolve()
    if not project.is_dir():
        raise CliError(f"Project directory does not exist: {project}")
    display = env.get("DISPLAY")
    if not display:
        raise CliError("DISPLAY is not set; VSCodium currently requires a host X11 display")
    home = Path(env.get("HOME", str(Path.home()))).expanduser()
    try:
        runtime_plan = plan_shared_runtime(
            SharedRuntimeOptions(
                project=options.project,
                profile=options.profile,
                global_settings=options.state,
                project_state=options.project_state,
                project_state_root=options.project_state_root,
                project_mount=options.project_mount or "/workspace/project",
            ),
            env,
            explicit_profile_root_env_var="DOCKER4IDES_CODIUM_PROFILE_ROOT",
            profile_dir_prefix="devcapsule-codium-with-claude-",
            default_global_settings=home / ".config" / "devcapsule" / "codium-with-claude",
            default_project_state=lambda project_plan: project_plan.project_path / ".devcapsule" / "codium-state",
        )
    except ValueError as exc:
        raise CliError(str(exc)) from exc
    project = runtime_plan.project
    if not project.is_dir():
        raise CliError(f"Project directory does not exist: {project}")
    name = options.name or f"codium-with-claude-{os.getuid()}-{int(time.time())}"
    container_command = (
        ["bash"]
        if options.debug_shell
        else [
            "codium-foreground",
            "--user-data-dir=/ide-global-settings/codium/user-data",
            "--extensions-dir=/ide-global-settings/codium/extensions",
            runtime_plan.project_mount,
        ]
    )
    interactive_args = ["--interactive", "--tty"] if options.debug_shell else []
    network_args = ["--network", options.network] if options.network is not None else []
    return [
        "docker",
        "run",
        "--rm",
        *interactive_args,
        *network_args,
        "--name",
        name,
        "--env",
        f"DISPLAY={display}",
        "--env",
        f"HOST_UID={os.getuid()}",
        "--env",
        f"HOST_GID={os.getgid()}",
        "--volume",
        f"{project}:{runtime_plan.project_mount}",
        "--volume",
        f"{runtime_plan.global_settings}:/ide-global-settings",
        "--volume",
        f"{runtime_plan.project_state}:/ide-project-state",
        "--volume",
        "/tmp/.X11-unix:/tmp/.X11-unix:ro",
        *options.extra_docker_args,
        options.image,
        *container_command,
    ]


def run_codium(options: CodiumRunOptions, env: Mapping[str, str] | None = None) -> int:
    return subprocess.run(build_codium_run_command(options, env), check=False).returncode
