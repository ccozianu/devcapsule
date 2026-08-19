"""Hidden image-side command for the URL-only physical-host bridge."""

from __future__ import annotations

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.compat import CliError
from devcapsule.host_open import HostOpenError, open_host_url


class HostOpenCommand(BaseCommand):
    url: str
    name = "host-open"
    hidden = True
    help = "Ask an authorized physical-host broker to open one HTTP(S) URL."
    params = [click.Argument(("url",), required=True)]

    def run(self) -> int:
        try:
            open_host_url(self.url)
        except HostOpenError as exc:
            raise CliError(str(exc)) from exc
        return 0


COMMAND = HostOpenCommand
