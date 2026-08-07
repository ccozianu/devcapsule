"""Public VSCodium configuration with pinned Node.js/npm tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from devcapsule.compat import CliError

from ._image_build import build_codium_image, parse_codium_build_options
from ._launcher import CodiumRunOptions, run_codium


class CodiumWithClaudeConfiguration:
    name = "codium_with_claude"
    help = "Build and run VSCodium with pinned Node.js/npm tooling."
    ide = "vscodium"
    agent = "claude-code"

    def to_click_command(self) -> click.Command:
        group = click.Group(name=self.name, help=self.help, no_args_is_help=True)
        group.add_command(self.build_command())
        group.add_command(self.run_command())
        return group

    def build_command(self) -> click.Command:
        return click.Command(
            name="build",
            callback=self.build_from_cli_options,
            params=[
                click.Option(["--image"], default="codium-with-claude:latest", show_default=True),
                click.Option(["--base-image"], default="ubuntu:24.04", show_default=True),
                click.Option(["--network"], default="default", show_default=True),
                click.Option(["--extra-apt-package"], multiple=True),
                click.Option(
                    ["--ide-archive"],
                    type=click.Path(path_type=Path),
                    help="Local VSCodium .tar.gz archive containing bin/codium; skips the VSCodium apt repository.",
                ),
            ],
            help="Build VSCodium with Python 3.12 and pinned Node.js/npm tooling.",
        )

    def run_command(self) -> click.Command:
        def callback(**kwargs: Any) -> int:
            try:
                return run_codium(
                    CodiumRunOptions(
                        project=kwargs["project"],
                        profile=kwargs["profile"],
                        image=kwargs["image"],
                        name=kwargs["name"],
                        state=kwargs["state"],
                        project_state=kwargs["project_state"],
                        project_state_root=kwargs["project_state_root"],
                        project_mount=kwargs["project_mount"],
                        network=kwargs["network"],
                        debug_shell=kwargs["debug_shell"],
                        extra_docker_args=tuple(kwargs["docker_arg"]),
                    )
                )
            except CliError as exc:
                raise click.ClickException(str(exc)) from exc

        return click.Command(
            name="run",
            callback=callback,
            params=[
                click.Option(["--project", "-p"], type=click.Path(path_type=Path), default=Path("."), show_default=True),
                click.Option(["--profile"], help="Named Codium state profile under ~/.config/devcapsule-codium-with-claude-NAME."),
                click.Option(["--image"], default="codium-with-claude:latest", show_default=True),
                click.Option(["--name"]),
                click.Option(["--state"], type=click.Path(path_type=Path), help="Persistent VSCodium and Claude home."),
                click.Option(["--project-state"], type=click.Path(path_type=Path), help="Persistent project-local cache state."),
                click.Option(
                    ["--project-state-root"],
                    type=click.Path(path_type=Path),
                    help="Root for mirrored per-project state paths outside the source tree.",
                ),
                click.Option(["--project-mount"], help="In-container project path."),
                click.Option(
                    ["--network"],
                    help="Docker network mode. Use 'host' only when direct host-network access is required.",
                ),
                click.Option(
                    ["--debug-shell"],
                    is_flag=True,
                    help="Run an interactive Bash shell through the image entrypoint instead of VSCodium.",
                ),
                click.Option(["--docker-arg"], multiple=True, help="Append one advanced docker run argument."),
            ],
            help="Launch VSCodium against a host project using X11.",
        )

    def build_from_cli_options(
        self,
        *,
        image: str,
        base_image: str,
        network: str,
        extra_apt_package: tuple[str, ...],
        ide_archive: Path | None,
    ) -> int:
        try:
            options = parse_codium_build_options(
                image=image,
                base_image=base_image,
                network=network.lower(),
                extra_apt_packages=tuple(extra_apt_package),
                ide_archive=ide_archive,
            )
            return build_codium_image(options)
        except CliError as exc:
            raise click.ClickException(str(exc)) from exc
