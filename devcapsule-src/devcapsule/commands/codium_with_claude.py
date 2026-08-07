"""VSCodium plus Claude Code command adapter."""

from __future__ import annotations

from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.codium_with_claude import CodiumWithClaudeConfiguration


class CodiumWithClaudeCommand(BaseCommand):
    name = CodiumWithClaudeConfiguration.name
    help = CodiumWithClaudeConfiguration.help

    @classmethod
    def to_click_command(cls) -> click.Command:
        return CodiumWithClaudeConfiguration().to_click_command()

    def run(self) -> Any:
        raise NotImplementedError("VSCodium plus Claude Code is a Click command group.")


COMMAND = CodiumWithClaudeCommand
