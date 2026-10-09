"""The console's API: the runtime CLI's ``--json`` documents, read by running it.

Each page's facts come from one command, so a change made with a command is
on the page at the next reload. Nothing is cached. The console never imports
the runtime; the subprocess boundary is the contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any, Sequence

DEFAULT_TIMEOUT_SECONDS = 60.0


class CommandError(Exception):
    """The CLI did not produce a document; the attributes say why."""

    def __init__(self, command: Sequence[str], reason: str, stderr: str = "") -> None:
        super().__init__(reason)
        self.command = tuple(command)
        self.reason = reason
        self.stderr = stderr

    def to_document(self) -> dict[str, Any]:
        return {"error": self.reason, "command": list(self.command), "stderr": self.stderr}


@dataclass(frozen=True)
class RuntimeCli:
    executable: tuple[str, ...]
    project: Path
    timeout: float = DEFAULT_TIMEOUT_SECONDS

    def command(self, *arguments: str) -> tuple[str, ...]:
        """``devcapsule project --path PROJECT ARGUMENTS... --json``."""
        return (*self.executable, "project", "--path", str(self.project), *arguments, "--json")

    def read(self, *arguments: str) -> Any:
        """Run one ``project`` subcommand with ``--json`` and parse its output."""
        command = self.command(*arguments)
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=self.timeout, check=False
            )
        except OSError as error:
            raise CommandError(command, f"cannot run the runtime CLI: {error}") from error
        except subprocess.TimeoutExpired as error:
            raise CommandError(command, f"the runtime CLI did not answer within {self.timeout:g}s") from error
        if completed.returncode != 0:
            raise CommandError(
                command, f"the runtime CLI exited with status {completed.returncode}", completed.stderr
            )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise CommandError(command, f"the runtime CLI printed no JSON document: {error}", completed.stderr) from error

    def configuration(self) -> Any:
        return self.read("config", "list")

    def versions(self) -> Any:
        return self.read("versions", "show")

    def information(self) -> Any:
        return self.read("info")
