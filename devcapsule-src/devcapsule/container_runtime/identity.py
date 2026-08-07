"""Privilege-drop command planning; gosu owns the security-sensitive switch."""

from __future__ import annotations

import os

from .contract import Identity


def foreground_command(command: tuple[str, ...], identity: Identity) -> tuple[str, ...]:
    if not command:
        raise ValueError("foreground command must not be empty")
    if os.geteuid() == 0:
        return ("gosu", f"{identity.uid}:{identity.gid}", *command)
    return command
