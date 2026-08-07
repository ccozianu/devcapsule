"""Forward the PEX runtime command to the container-side entrypoint."""

from __future__ import annotations

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.container_runtime.entrypoint import main as runtime_main


class RuntimeCommand(BaseCommand):
    arguments: tuple[str, ...]
    name = "runtime"
    help = "Run the container-side entrypoint from the DevCapsule PEX."
    context_settings = {
        "allow_extra_args": True,
        "help_option_names": [],
        "ignore_unknown_options": True,
    }
    params = [
        click.Argument(
            ("arguments",),
            nargs=-1,
            type=click.UNPROCESSED,
        )
    ]

    def run(self) -> int:
        return runtime_main(list(self.arguments))


COMMAND = RuntimeCommand
