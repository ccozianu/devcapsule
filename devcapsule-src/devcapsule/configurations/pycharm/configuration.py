"""PyCharm configuration public interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

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


class PycharmConfiguration:
    """Public interface for the Dockerized PyCharm configuration."""

    name = "pycharm"
    help = "Build and run the PyCharm IDE configuration."

    _forward_context = {
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "help_option_names": [],
    }

    _run_params: list[click.Parameter] = [
        click.Option(
            ["--project", "-p"],
            type=click.Path(path_type=Path),
            default=Path("."),
            help="Host project directory to open. Defaults to the current directory.",
        ),
        click.Option(["--profile"], help="Named PyCharm state profile under ~/.config/docker-pycharm-NAME."),
        click.Option(["--image"], help="Docker image to run."),
        click.Option(["--name"], help="Container name."),
        click.Option(
            ["--global-settings", "--state"],
            type=click.Path(path_type=Path),
            help="Shared IDE config/home root.",
        ),
        click.Option(
            ["--home"],
            type=click.Path(path_type=Path),
            help="Persistent DevCapsule home mounted at /home/devcapsule.",
        ),
        click.Option(
            ["--project-state"],
            type=click.Path(path_type=Path),
            help="Per-project IDE cache/log/workspace root.",
        ),
        click.Option(
            ["--project-state-root"],
            type=click.Path(path_type=Path),
            help=(
                "Root for mirrored per-project state paths. "
                "Example: /work/.state mirrors /work/project to /work/.state/project."
            ),
        ),
        click.Option(
            ["--config-mode"],
            type=click.Choice(["shared", "project", "custom"], case_sensitive=False),
            help="PyCharm config path mode: shared, project, or custom.",
        ),
        click.Option(
            ["--ide-config"],
            type=click.Path(path_type=Path),
            help="PyCharm config dir. Implies --config-mode custom.",
        ),
        click.Option(
            ["--project-config"],
            is_flag=True,
            help="Compatibility shorthand for --config-mode project.",
        ),
        click.Option(
            ["--shared-config"],
            is_flag=True,
            help="Compatibility shorthand for --config-mode shared.",
        ),
        click.Option(["--project-mount"], help="In-container project path."),
        click.Option(
            ["--plugins"],
            type=click.Path(path_type=Path),
            help="Persistent PyCharm plugins dir.",
        ),
        click.Option(["--ssh-agent"], is_flag=True, help="Forward host SSH agent socket."),
        click.Option(["--git-user-name"], help="Git user.name inside IDE."),
        click.Option(["--git-user-email"], help="Git user.email inside IDE."),
        click.Option(["--git-identity-from-host"], is_flag=True, help="Require host Git identity import."),
        click.Option(["--no-git-identity-from-host"], is_flag=True, help="Disable host Git identity import."),
        click.Option(
            ["--git-token-file", "--github-token-file"],
            type=click.Path(path_type=Path),
            help="HTTPS Git token file.",
        ),
        click.Option(
            ["--git-token-env", "--github-token-env"],
            help="Environment variable containing HTTPS Git token.",
        ),
        click.Option(["--git-token-user", "--github-user"], help="Username for HTTPS Git askpass."),
        click.Option(["--git-token-host"], help="Comma/space-separated hosts allowed to receive the token."),
        click.Option(["--docker", "--host-docker"], is_flag=True, help="Connect to the host Docker daemon."),
        click.Option(
            ["--docker-socket"],
            type=click.Path(path_type=Path),
            help="Host Docker socket for --docker.",
        ),
        click.Option(
            ["--docker-in-docker", "--dind"],
            is_flag=True,
            help="Start an isolated inner Docker daemon.",
        ),
        click.Option(["--no-docker"], is_flag=True, help="Disable Docker access."),
        click.Option(
            ["--debug-native"],
            is_flag=True,
            help="Add ptrace/seccomp permissions for native debugging.",
        ),
        click.Option(
            ["--dev-sudo", "--sudo"],
            is_flag=True,
            help="Enable passwordless sudo for the IDE user.",
        ),
        click.Option(
            ["--writable-root"],
            is_flag=True,
            help="Do not run with a read-only root filesystem.",
        ),
        click.Option(
            ["--ignore-config-lock"],
            is_flag=True,
            help="Skip preflight for an existing PyCharm config .lock.",
        ),
        click.Option(
            ["--host-browser/--no-host-browser"],
            default=False,
            show_default=True,
            help="Explicitly allow HTTP(S) links to open in the physical host's default browser.",
        ),
        click.Option(
            ["--docker-arg"],
            multiple=True,
            help="Append one raw docker-run argument; repeat for advanced cases.",
        ),
    ]

    def to_click_command(self) -> click.Command:
        group = click.Group(name=self.name, help=self.help, no_args_is_help=True)
        group.add_command(self.run_command())
        group.add_command(self.build_command())
        group.add_command(self.check_runtime_command())
        return group

    def run_command(self, *, name: str = "run", help_text: str | None = None) -> click.Command:
        def callback(**kwargs: Any) -> int:
            return self.run_from_cli_options(**kwargs)

        return click.Command(
            name=name,
            callback=callback,
            params=self._run_params,
            help=help_text or "Launch PyCharm through the translated Python launcher.",
        )

    def build_command(self, *, name: str = "build") -> click.Command:
        return click.Command(
            name=name,
            callback=self.build_image_from_cli_options,
            params=[
                click.Option(
                    ["--pycharm"],
                    type=click.Path(path_type=Path),
                    required=True,
                    help="PyCharm .tar.gz archive or unpacked PyCharm directory.",
                ),
                click.Option(["--image"], default="pycharm-isolated:latest", help="Docker image tag to create."),
                click.Option(
                    ["--base-image"],
                    default="ubuntu:24.04",
                    show_default=True,
                    help="Base OCI image used for the IDE image.",
                ),
                click.Option(
                    ["--network"],
                    default="default",
                    show_default=True,
                    help="Build network mode passed to docker buildx through python-on-whales.",
                ),
                click.Option(
                    ["--extra-apt-package"],
                    multiple=True,
                    help="Extra apt package to install into the image. Repeat as needed.",
                ),
            ],
            help="Build the current Dockerized PyCharm image with pinned Node.js/npm tooling.",
        )

    def check_runtime_command(self, *, name: str = "check-runtime") -> click.Command:
        @click.pass_context
        def callback(ctx: click.Context, **kwargs: Any) -> int:
            return self.check_runtime(list(ctx.args))

        return click.Command(
            name=name,
            callback=callback,
            help="Run the current PyCharm runtime dependency check.",
            context_settings=self._forward_context,
        )

    def run_from_cli_options(self, **kwargs: Any) -> int:
        options = self._run_options_from_cli(**kwargs)
        try:
            return run_pycharm(options)
        except PycharmRunError as exc:
            raise click.ClickException(str(exc)) from exc

    def build_image_from_cli_options(
        self,
        *,
        pycharm: Path,
        image: str,
        base_image: str,
        network: str,
        extra_apt_package: tuple[str, ...],
    ) -> int:
        try:
            options = parse_pycharm_build_options(
                pycharm=pycharm,
                image=image,
                base_image=base_image,
                network=network.lower(),
                extra_apt_packages=tuple(extra_apt_package),
            )
            return build_pycharm_image(options)
        except CliError as exc:
            raise click.ClickException(str(exc)) from exc

    def check_runtime(self, args: list[str]) -> int:
        return run_script("docker4pycharm/check-runtime-deps.sh", args)

    def _run_options_from_cli(self, **kwargs: Any) -> PycharmRunOptions:
        return PycharmRunOptions(
            project=kwargs["project"],
            profile=kwargs["profile"],
            image=kwargs["image"],
            name=kwargs["name"],
            global_settings=kwargs["global_settings"],
            persistent_home=kwargs["home"],
            project_state=kwargs["project_state"],
            project_state_root=kwargs["project_state_root"],
            config_mode=self._resolve_config_mode(
                self._as_ide_config_mode(kwargs["config_mode"]),
                kwargs["ide_config"],
                kwargs["project_config"],
                kwargs["shared_config"],
            ),
            ide_config=kwargs["ide_config"],
            project_mount=kwargs["project_mount"],
            plugins=kwargs["plugins"],
            use_ssh_agent=kwargs["ssh_agent"],
            git_user_name=kwargs["git_user_name"],
            git_user_email=kwargs["git_user_email"],
            git_identity_from_host=self._resolve_git_identity_mode(
                kwargs["git_identity_from_host"],
                kwargs["no_git_identity_from_host"],
            ),
            git_token_file=kwargs["git_token_file"],
            git_token_env=kwargs["git_token_env"],
            git_token_username=kwargs["git_token_user"],
            git_token_hosts=kwargs["git_token_host"],
            docker_mode=self._resolve_docker_mode(kwargs["docker"], kwargs["docker_in_docker"], kwargs["no_docker"]),
            host_docker_socket=kwargs["docker_socket"],
            debug_native=kwargs["debug_native"],
            writable_root=kwargs["writable_root"],
            enable_sudo=kwargs["dev_sudo"],
            ignore_config_lock=kwargs["ignore_config_lock"],
            enable_host_browser=kwargs["host_browser"],
            extra_docker_args=list(kwargs["docker_arg"] or []),
        )

    def _as_ide_config_mode(self, value: str | None) -> IdeConfigMode | None:
        if value is None:
            return None
        return IdeConfigMode(value.lower())

    def _resolve_config_mode(
        self,
        config_mode: IdeConfigMode | None,
        ide_config: Path | None,
        project_config: bool,
        shared_config: bool,
    ) -> IdeConfigMode | None:
        requested_shorthands = [project_config, shared_config]
        if sum(1 for requested in requested_shorthands if requested) > 1:
            raise click.BadParameter("choose only one of --project-config or --shared-config")
        if config_mode is not None and any(requested_shorthands):
            raise click.BadParameter("do not combine --config-mode with --project-config or --shared-config")
        conflicting_config_mode = config_mode in {IdeConfigMode.shared, IdeConfigMode.project}
        if ide_config is not None and (conflicting_config_mode or any(requested_shorthands)):
            raise click.BadParameter("--ide-config can only be used with --config-mode custom")
        if project_config:
            return IdeConfigMode.project
        if shared_config:
            return IdeConfigMode.shared
        if config_mode is not None:
            return config_mode
        if ide_config is not None:
            return IdeConfigMode.custom
        return None

    def _resolve_git_identity_mode(self, from_host: bool, no_from_host: bool) -> str | None:
        if from_host and no_from_host:
            raise click.BadParameter("choose only one of --git-identity-from-host or --no-git-identity-from-host")
        if from_host:
            return "1"
        if no_from_host:
            return "0"
        return None

    def _resolve_docker_mode(self, docker: bool, docker_in_docker: bool, no_docker: bool) -> DockerMode | None:
        requested_modes = [docker, docker_in_docker, no_docker]
        if sum(1 for requested in requested_modes if requested) > 1:
            raise click.BadParameter("choose only one Docker mode flag")
        if docker:
            return DockerMode.host
        if docker_in_docker:
            return DockerMode.dind
        if no_docker:
            return DockerMode.none
        return None
