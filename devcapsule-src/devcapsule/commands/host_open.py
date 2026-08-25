"""Hidden image-side command for the URL-only physical-host bridge."""

from __future__ import annotations

import argparse

from devcapsule.commands.framework import Command
from devcapsule.compat import CliError
from devcapsule.host_open import HostOpenError, open_host_url


class HostOpenCommand(Command):
    name = "host-open"
    hidden = True
    help = "Ask an authorized physical-host broker to open one HTTP(S) URL."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("url")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            open_host_url(arguments.url)
        except HostOpenError as exc:
            raise CliError(str(exc)) from exc
        return 0


COMMAND = HostOpenCommand
