"""Forward the PEX runtime command to the container-side entrypoint."""

from __future__ import annotations

from typing import Sequence

from devcapsule.commands.framework import Command
from devcapsule.container_runtime.entrypoint import main as runtime_main


class RuntimeCommand(Command):
    name = "runtime"
    help = "Run the container-side entrypoint from the DevCapsule PEX."

    # The container entrypoint owns its entire argument surface, including any
    # future options and its own help; the CLI must forward every token
    # untouched rather than model that surface here.
    @classmethod
    def invoke(cls, prog: str, argv: Sequence[str], context: object | None = None) -> int:
        return runtime_main(list(argv))


COMMAND = RuntimeCommand
