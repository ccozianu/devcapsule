"""Bootstrap command adapter."""

from __future__ import annotations

from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.compat import run_script


class BootstrapCommand(BaseCommand):
    name = "bootstrap"
    help = "Bootstrap project workflow files."

    _forward_context = {
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "help_option_names": [],
    }

    @classmethod
    def to_click_command(cls) -> click.Command:
        group = click.Group(name=cls.name, help=cls.help, no_args_is_help=True)
        group.add_command(cls._project_command())
        return group

    @classmethod
    def _project_command(cls) -> click.Command:
        @click.pass_context
        def callback(ctx: click.Context, **kwargs: Any) -> int:
            return run_script("docker4pycharm/bootstrap-project.sh", list(ctx.args))

        return click.Command(
            name="project",
            callback=callback,
            help="Seed human/agent workflow files in a project.",
            context_settings=cls._forward_context,
        )

    def run(self) -> Any:
        raise NotImplementedError("Bootstrap is a Click command group.")


COMMAND = BootstrapCommand

