"""Inspect the source identity embedded in this DevCapsule distribution."""

from __future__ import annotations

import click

from devcapsule.build_info import build_info_json, current_build_info
from devcapsule.commands.base import BaseCommand


class VersionCommand(BaseCommand):
    as_json: bool
    name = "version"
    help = "Show this DevCapsule distribution's version and public source identity."
    params = [click.Option(("--json", "as_json"), is_flag=True, help="Emit stable machine-readable JSON.")]

    def run(self) -> int:
        info = current_build_info()
        if self.as_json:
            click.echo(build_info_json(info))
            return 0
        click.echo(f"DevCapsule {info.version}")
        click.echo(f"Source repository: {info.source_repository}")
        click.echo(f"Source revision: {info.source_revision}")
        click.echo(f"Source URL: {info.source_url}")
        return 0


COMMAND = VersionCommand
