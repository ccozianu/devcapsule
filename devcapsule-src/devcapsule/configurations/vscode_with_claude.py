"""VS Code plus Claude IDE configuration."""

from __future__ import annotations

import argparse
from typing import Mapping

from devcapsule.commands.framework import Command, Group
from devcapsule.compat import CliError


def _not_implemented(command: str) -> int:
    raise CliError(
        f"vscode_with_claude {command} is registered as the next configuration module, "
        "but its Docker image and launcher are not implemented yet."
    )


class VscodeBuildCommand(Command):
    name = "build"
    help = "Build the VS Code plus Claude image."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        return _not_implemented("build")


class VscodeRunCommand(Command):
    name = "run"
    help = "Launch the VS Code plus Claude configuration."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        return _not_implemented("run")


class VscodeWithClaudeConfiguration(Group):
    """WIP interface for the VS Code plus Claude proof-point configuration."""

    name = "vscode_with_claude"
    help = "WIP: VS Code plus Claude is registered but not implemented."
    ide = "vscode"
    agent = "claude"
    implemented = False

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            VscodeBuildCommand.name: VscodeBuildCommand,
            VscodeRunCommand.name: VscodeRunCommand,
        }


__all__ = ["VscodeWithClaudeConfiguration"]
