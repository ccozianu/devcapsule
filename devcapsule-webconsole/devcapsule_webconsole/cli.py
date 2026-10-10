"""The console's API: the runtime CLI's ``--json`` documents, read by running it.

Each page's facts come from one command, so a change made with a command is
on the page at the next reload. Nothing is cached. The console never imports
the runtime; the subprocess boundary is the contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from .decisions import DECISIONS_ENV

DEFAULT_TIMEOUT_SECONDS = 60.0


class CommandError(Exception):
    """The CLI did not do what was asked; the attributes say why."""

    def __init__(self, command: Sequence[str], reason: str, stderr: str = "") -> None:
        super().__init__(reason)
        self.command = tuple(command)
        self.reason = reason
        self.stderr = stderr

    def to_document(self) -> dict[str, Any]:
        return {"error": self.reason, "command": list(self.command), "stderr": self.stderr}


class CommandRefused(CommandError):
    """The CLI refused the request, exit status 2: the request was wrong, not the CLI."""


REFUSAL_STATUS = 2


@dataclass(frozen=True)
class RuntimeCli:
    executable: tuple[str, ...]
    project: Path
    timeout: float = DEFAULT_TIMEOUT_SECONDS

    def command(self, *arguments: str) -> tuple[str, ...]:
        """``devcapsule project --path PROJECT ARGUMENTS... --json``."""
        return (*self.executable, "project", "--path", str(self.project), *arguments, "--json")

    def read(self, *arguments: str, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
        """Run one ``project`` subcommand with ``--json`` and parse its output."""
        command = self.command(*arguments)
        try:
            completed = subprocess.run(
                command, capture_output=True, timeout=self.timeout, check=False, env=environ
            )
        except OSError as error:
            raise CommandError(command, f"cannot run the runtime CLI: {error}") from error
        except subprocess.TimeoutExpired as error:
            raise CommandError(command, f"the runtime CLI did not answer within {self.timeout:g}s") from error
        stderr = completed.stderr.decode("utf-8", errors="replace")
        if completed.returncode != 0:
            raise CommandError(
                command, f"the runtime CLI exited with status {completed.returncode}", stderr
            )
        try:
            document = json.loads(completed.stdout.decode("utf-8"), parse_float=_finite_number,
                                  parse_constant=_finite_number)
            if not isinstance(document, dict):
                raise ValueError("expected a JSON object")
        except ValueError as error:
            raise CommandError(command, f"the runtime CLI printed no JSON document: {error}", stderr) from error
        return document

    def act(self, *arguments: str) -> str:
        """Run one ``project`` subcommand that changes capsule state and return what it printed.

        No ``--json``: the commands that act print one line. A refusal, exit
        status 2, is ``CommandRefused`` with the CLI's message; any other
        failure is ``CommandError``.
        """
        command = (*self.executable, "project", "--path", str(self.project), *arguments)
        try:
            completed = subprocess.run(command, capture_output=True, timeout=self.timeout, check=False)
        except OSError as error:
            raise CommandError(command, f"cannot run the runtime CLI: {error}") from error
        except subprocess.TimeoutExpired as error:
            raise CommandError(command, f"the runtime CLI did not answer within {self.timeout:g}s") from error
        stderr = completed.stderr.decode("utf-8", errors="replace")
        if completed.returncode == REFUSAL_STATUS:
            raise CommandRefused(command, stderr.strip() or "the runtime CLI refused the request", stderr)
        if completed.returncode != 0:
            raise CommandError(command, f"the runtime CLI exited with status {completed.returncode}", stderr)
        return completed.stdout.decode("utf-8", errors="replace").strip()

    def configuration(self) -> dict[str, Any]:
        return self.read("config", "list")

    def notifications(self, *, decisions: Path, unread_only: bool = False) -> dict[str, Any]:
        # The listing must merge the directory served by the decision pages,
        # including an explicit --decisions override. Do not change os.environ.
        environ = {**os.environ, DECISIONS_ENV: str(decisions)}
        return self.read("checkout", "notifications", "list", *(("--unread",) if unread_only else ()), environ=environ)

    def versions(self) -> dict[str, Any]:
        return self.read("versions", "show")

    def information(self) -> dict[str, Any]:
        return self.read("info")


def _finite_number(value: str) -> float:
    """Reject Python's non-JSON constants and numeric overflow before serving."""
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite JSON number: {value}")
    return number
