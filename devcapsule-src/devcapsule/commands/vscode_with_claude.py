"""WIP VS Code plus Claude command adapter."""

from __future__ import annotations

from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.vscode_with_claude import VscodeWithClaudeConfiguration


class VscodeWithClaudeCommand(BaseCommand):
    name = VscodeWithClaudeConfiguration.name
    help = VscodeWithClaudeConfiguration.help

    @classmethod
    def to_click_command(cls) -> click.Command:
        return VscodeWithClaudeConfiguration().to_click_command()

    def run(self) -> Any:
        raise NotImplementedError("VS Code plus Claude is a Click command group.")


COMMAND = VscodeWithClaudeCommand
