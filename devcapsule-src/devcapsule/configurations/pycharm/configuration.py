"""PyCharm configuration public interface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping, Sequence

from devcapsule.commands.framework import Command, Group, UsageError
from devcapsule.compat import CliError
from devcapsule.compat import run_script

from ._launcher import (
    DockerMode,
    IdeConfigMode,
    PycharmRunError,
    PycharmRunOptions,
    run_pycharm,
)
from ._image_build import build_pycharm_image, parse_pycharm_build_options


class PycharmRunCommand(Command):
    name = "run"
    help = "Launch PyCharm through the translated Python launcher."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--project",
            "-p",
            type=Path,
            default=Path("."),
            help="Host project directory to open. Defaults to the current directory.",
        )
        parser.add_argument(
            "--profile", help="Named PyCharm state profile under ~/.config/docker-pycharm-NAME."
        )
        parser.add_argument("--image", help="Docker image to run.")
        parser.add_argument("--name", help="Container name.")
        parser.add_argument(
            "--global-settings",
            "--state",
            dest="global_settings",
            type=Path,
            help="Shared IDE config/home root.",
        )
        parser.add_argument(
            "--home", type=Path, help="Persistent DevCapsule home mounted at /home/devcapsule."
        )
        parser.add_argument(
            "--project-state", type=Path, help="Per-project IDE cache/log/workspace root."
        )
        parser.add_argument(
            "--project-state-root",
            type=Path,
            help=(
                "Root for mirrored per-project state paths. "
                "Example: /work/.state mirrors /work/project to /work/.state/project."
            ),
        )
        parser.add_argument(
            "--config-mode",
            type=str.lower,
            choices=["shared", "project", "custom"],
            help="PyCharm config path mode: shared, project, or custom.",
        )
        parser.add_argument(
            "--ide-config", type=Path, help="PyCharm config dir. Implies --config-mode custom."
        )
        parser.add_argument(
            "--project-config",
            action="store_true",
            help="Compatibility shorthand for --config-mode project.",
        )
        parser.add_argument(
            "--shared-config",
            action="store_true",
            help="Compatibility shorthand for --config-mode shared.",
        )
        parser.add_argument("--project-mount", help="In-container project path.")
        parser.add_argument("--plugins", type=Path, help="Persistent PyCharm plugins dir.")
        parser.add_argument(
            "--ssh-agent", action="store_true", help="Forward host SSH agent socket."
        )
        parser.add_argument("--git-user-name", help="Git user.name inside IDE.")
        parser.add_argument("--git-user-email", help="Git user.email inside IDE.")
        parser.add_argument(
            "--git-identity-from-host",
            action="store_true",
            help="Require host Git identity import.",
        )
        parser.add_argument(
            "--no-git-identity-from-host",
            action="store_true",
            help="Disable host Git identity import.",
        )
        parser.add_argument(
            "--git-token-file",
            "--github-token-file",
            dest="git_token_file",
            type=Path,
            help="HTTPS Git token file.",
        )
        parser.add_argument(
            "--git-token-env",
            "--github-token-env",
            dest="git_token_env",
            help="Environment variable containing HTTPS Git token.",
        )
        parser.add_argument(
            "--git-token-user",
            "--github-user",
            dest="git_token_user",
            help="Username for HTTPS Git askpass.",
        )
        parser.add_argument(
            "--git-token-host", help="Comma/space-separated hosts allowed to receive the token."
        )
        parser.add_argument(
            "--docker",
            "--host-docker",
            dest="docker",
            action="store_true",
            help="Connect to the host Docker daemon.",
        )
        parser.add_argument("--docker-socket", type=Path, help="Host Docker socket for --docker.")
        parser.add_argument(
            "--docker-in-docker",
            "--dind",
            dest="docker_in_docker",
            action="store_true",
            help="Start an isolated inner Docker daemon.",
        )
        parser.add_argument("--no-docker", action="store_true", help="Disable Docker access.")
        parser.add_argument(
            "--debug-native",
            action="store_true",
            help="Add ptrace/seccomp permissions for native debugging.",
        )
        parser.add_argument(
            "--dev-sudo",
            "--sudo",
            dest="dev_sudo",
            action="store_true",
            help="Enable passwordless sudo for the IDE user.",
        )
        parser.add_argument(
            "--writable-root",
            action="store_true",
            help="Do not run with a read-only root filesystem.",
        )
        parser.add_argument(
            "--ignore-config-lock",
            action="store_true",
            help="Skip preflight for an existing PyCharm config .lock.",
        )
        parser.add_argument(
            "--host-browser",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Explicitly allow HTTP(S) links to open in the physical host's default browser.",
        )
        parser.add_argument(
            "--docker-arg",
            action="append",
            default=[],
            help="Append one raw docker-run argument; repeat for advanced cases.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        options = PycharmRunOptions(
            project=arguments.project,
            profile=arguments.profile,
            image=arguments.image,
            name=arguments.name,
            global_settings=arguments.global_settings,
            persistent_home=arguments.home,
            project_state=arguments.project_state,
            project_state_root=arguments.project_state_root,
            config_mode=_resolve_config_mode(
                IdeConfigMode(arguments.config_mode) if arguments.config_mode else None,
                arguments.ide_config,
                arguments.project_config,
                arguments.shared_config,
            ),
            ide_config=arguments.ide_config,
            project_mount=arguments.project_mount,
            plugins=arguments.plugins,
            use_ssh_agent=arguments.ssh_agent,
            git_user_name=arguments.git_user_name,
            git_user_email=arguments.git_user_email,
            git_identity_from_host=_resolve_git_identity_mode(
                arguments.git_identity_from_host,
                arguments.no_git_identity_from_host,
            ),
            git_token_file=arguments.git_token_file,
            git_token_env=arguments.git_token_env,
            git_token_username=arguments.git_token_user,
            git_token_hosts=arguments.git_token_host,
            docker_mode=_resolve_docker_mode(
                arguments.docker, arguments.docker_in_docker, arguments.no_docker
            ),
            host_docker_socket=arguments.docker_socket,
            debug_native=arguments.debug_native,
            writable_root=arguments.writable_root,
            enable_sudo=arguments.dev_sudo,
            ignore_config_lock=arguments.ignore_config_lock,
            enable_host_browser=arguments.host_browser,
            extra_docker_args=list(arguments.docker_arg),
        )
        try:
            return run_pycharm(options)
        except PycharmRunError as exc:
            raise CliError(str(exc)) from exc


class PycharmBuildCommand(Command):
    name = "build"
    help = "Build the current Dockerized PyCharm image with pinned Node.js/npm tooling."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--pycharm",
            type=Path,
            required=True,
            help="PyCharm .tar.gz archive or unpacked PyCharm directory.",
        )
        parser.add_argument(
            "--image", default="pycharm-isolated:latest", help="Docker image tag to create."
        )
        parser.add_argument(
            "--base-image",
            default="ubuntu:24.04",
            help="Base OCI image used for the IDE image (default: ubuntu:24.04).",
        )
        parser.add_argument(
            "--network",
            default="default",
            help="Build network mode passed to docker buildx (default: default).",
        )
        parser.add_argument(
            "--extra-apt-package",
            action="append",
            default=[],
            help="Extra apt package to install into the image. Repeat as needed.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        options = parse_pycharm_build_options(
            pycharm=arguments.pycharm,
            image=arguments.image,
            base_image=arguments.base_image,
            network=arguments.network.lower(),
            extra_apt_packages=tuple(arguments.extra_apt_package),
        )
        return build_pycharm_image(options)


class PycharmCheckRuntimeCommand(Command):
    name = "check-runtime"
    help = "Run the current PyCharm runtime dependency check."

    # The dependency-check script owns its own argument surface; forward every
    # token untouched rather than modeling it here.
    @classmethod
    def invoke(cls, prog: str, argv: Sequence[str], context: object | None = None) -> int:
        return run_script("docker4pycharm/check-runtime-deps.sh", list(argv))


class PycharmConfiguration(Group):
    """Public interface for the Dockerized PyCharm configuration."""

    name = "pycharm"
    help = "Build and run the PyCharm IDE configuration."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            PycharmRunCommand.name: PycharmRunCommand,
            PycharmBuildCommand.name: PycharmBuildCommand,
            PycharmCheckRuntimeCommand.name: PycharmCheckRuntimeCommand,
        }


def _resolve_config_mode(
    config_mode: IdeConfigMode | None,
    ide_config: Path | None,
    project_config: bool,
    shared_config: bool,
) -> IdeConfigMode | None:
    requested_shorthands = [project_config, shared_config]
    if sum(1 for requested in requested_shorthands if requested) > 1:
        raise UsageError("choose only one of --project-config or --shared-config")
    if config_mode is not None and any(requested_shorthands):
        raise UsageError("do not combine --config-mode with --project-config or --shared-config")
    conflicting_config_mode = config_mode in {IdeConfigMode.shared, IdeConfigMode.project}
    if ide_config is not None and (conflicting_config_mode or any(requested_shorthands)):
        raise UsageError("--ide-config can only be used with --config-mode custom")
    if project_config:
        return IdeConfigMode.project
    if shared_config:
        return IdeConfigMode.shared
    if config_mode is not None:
        return config_mode
    if ide_config is not None:
        return IdeConfigMode.custom
    return None


def _resolve_git_identity_mode(from_host: bool, no_from_host: bool) -> str | None:
    if from_host and no_from_host:
        raise UsageError(
            "choose only one of --git-identity-from-host or --no-git-identity-from-host"
        )
    if from_host:
        return "1"
    if no_from_host:
        return "0"
    return None


def _resolve_docker_mode(
    docker: bool, docker_in_docker: bool, no_docker: bool
) -> DockerMode | None:
    requested_modes = [docker, docker_in_docker, no_docker]
    if sum(1 for requested in requested_modes if requested) > 1:
        raise UsageError("choose only one Docker mode flag")
    if docker:
        return DockerMode.host
    if docker_in_docker:
        return DockerMode.dind
    if no_docker:
        return DockerMode.none
    return None
