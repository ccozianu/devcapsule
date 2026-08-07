"""PyCharm command-tree adapter."""

from __future__ import annotations

from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.pycharm import PycharmConfiguration


class PycharmCommand(BaseCommand):
    name = "pycharm"
    help = PycharmConfiguration.help

    @classmethod
    def to_click_command(cls) -> click.Command:
        return PycharmConfiguration().to_click_command()

    def run(self) -> Any:
        raise NotImplementedError("PyCharm is a Click command group.")


COMMAND = PycharmCommand
