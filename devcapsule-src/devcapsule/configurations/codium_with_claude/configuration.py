"""Public VSCodium configuration with pinned Node.js/npm tooling."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from devcapsule.commands.framework import Command, Group

from ._image_build import build_codium_image, parse_codium_build_options
from ._launcher import CodiumRunOptions, run_codium


class CodiumBuildCommand(Command):
    name = "build"
    help = "Build VSCodium with Python 3.12 and pinned Node.js/npm tooling."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--image", default="codium-with-claude:latest")
        parser.add_argument("--base-image", default="ubuntu:24.04")
        parser.add_argument("--network", default="default")
        parser.add_argument("--extra-apt-package", action="append", default=[])
        parser.add_argument(
            "--ide-archive",
            type=Path,
            help=(
                "Local VSCodium .tar.gz archive containing bin/codium; skips the "
                "VSCodium apt repository."
            ),
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        options = parse_codium_build_options(
            image=arguments.image,
            base_image=arguments.base_image,
            network=arguments.network.lower(),
            extra_apt_packages=tuple(arguments.extra_apt_package),
            ide_archive=arguments.ide_archive,
        )
        return build_codium_image(options)


class CodiumRunCommand(Command):
    name = "run"
    help = "Launch VSCodium against a host project using X11."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--project", "-p", type=Path, default=Path("."))
        parser.add_argument(
            "--profile",
            help="Named Codium state profile under ~/.config/devcapsule-codium-with-claude-NAME.",
        )
        parser.add_argument("--image", default="codium-with-claude:latest")
        parser.add_argument("--name")
        parser.add_argument("--state", type=Path, help="Persistent VSCodium and Claude home.")
        parser.add_argument(
            "--project-state", type=Path, help="Persistent project-local cache state."
        )
        parser.add_argument(
            "--project-state-root",
            type=Path,
            help="Root for mirrored per-project state paths outside the source tree.",
        )
        parser.add_argument("--project-mount", help="In-container project path.")
        parser.add_argument(
            "--network",
            help="Docker network mode. Use 'host' only when direct host-network access is required.",
        )
        parser.add_argument(
            "--debug-shell",
            action="store_true",
            help="Run an interactive Bash shell through the image entrypoint instead of VSCodium.",
        )
        parser.add_argument(
            "--docker-arg",
            action="append",
            default=[],
            help="Append one advanced docker run argument.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        return run_codium(
            CodiumRunOptions(
                project=arguments.project,
                profile=arguments.profile,
                image=arguments.image,
                name=arguments.name,
                state=arguments.state,
                project_state=arguments.project_state,
                project_state_root=arguments.project_state_root,
                project_mount=arguments.project_mount,
                network=arguments.network,
                debug_shell=arguments.debug_shell,
                extra_docker_args=tuple(arguments.docker_arg),
            )
        )


class CodiumWithClaudeConfiguration(Group):
    name = "codium_with_claude"
    help = "Build and run VSCodium with pinned Node.js/npm tooling."
    ide = "vscodium"
    agent = "claude-code"

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            CodiumBuildCommand.name: CodiumBuildCommand,
            CodiumRunCommand.name: CodiumRunCommand,
        }
