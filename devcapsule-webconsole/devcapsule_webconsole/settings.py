"""What the console needs to start, and where each value comes from.

The runtime passes everything on the command line when it starts the console
as a supervised child. On a host a developer passes the same arguments by
hand. Environment variables fill in the project path and the token file so a
capsule's defaults need no arguments at all.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Mapping, Sequence

PROJECT_ENV = "PROJECT_PATH"
TOKEN_FILE_ENV = "DEVCAPSULE_CONSOLE_TOKEN_FILE"
CLI_ENV = "DEVCAPSULE_CONSOLE_CLI"
DEFAULT_CLI = "devcapsule"
DEFAULT_LISTEN = "127.0.0.1"
DEFAULT_PORT = 8080


class SettingsError(ValueError):
    """A start-up value is missing or malformed; the message says which."""


@dataclass(frozen=True)
class Settings:
    project: Path
    """The project mount: the only tree the console reads files from."""
    cli: tuple[str, ...]
    """The runtime CLI, run as a subprocess for every ``--json`` document."""
    token: str
    """The run token every request must carry."""
    listen: str = DEFAULT_LISTEN
    port: int = DEFAULT_PORT

    @property
    def static_root(self) -> Path:
        return Path(str(resources.files(__package__) / "static"))


def read_token(path: Path) -> str:
    """The launcher-supplied per-run token: one line, no whitespace."""
    try:
        token = path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise SettingsError(f"cannot read the console token at {path}: {error}") from error
    if not token or any(character.isspace() for character in token):
        raise SettingsError(f"the console token at {path} is empty or malformed")
    return token


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="devcapsule-webconsole",
        description="Serve the capsule web console on one loopback port, behind the run token.",
    )
    result.add_argument("--project", type=Path, help=f"Project mount to read; default ${PROJECT_ENV}.")
    result.add_argument("--cli", help=f"Runtime CLI executable; default ${CLI_ENV}, then {DEFAULT_CLI!r} on PATH.")
    result.add_argument("--token-file", type=Path, help=f"File holding the run token; default ${TOKEN_FILE_ENV}.")
    result.add_argument("--listen", default=DEFAULT_LISTEN, help=f"Address to bind; default {DEFAULT_LISTEN}.")
    result.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind; default {DEFAULT_PORT}.")
    return result


def settings_from_arguments(argv: Sequence[str], environ: Mapping[str, str]) -> Settings:
    arguments = parser().parse_args(list(argv))
    project = arguments.project or (Path(environ[PROJECT_ENV]) if environ.get(PROJECT_ENV) else None)
    if project is None:
        raise SettingsError(f"no project: pass --project or set ${PROJECT_ENV}")
    if not (project / ".devcapsule").is_dir():
        raise SettingsError(f"{project} is not a DevCapsule project: no .devcapsule directory")
    token_file = arguments.token_file or (
        Path(environ[TOKEN_FILE_ENV]) if environ.get(TOKEN_FILE_ENV) else None
    )
    if token_file is None:
        raise SettingsError(f"no token: pass --token-file or set ${TOKEN_FILE_ENV}")
    cli = arguments.cli or environ.get(CLI_ENV) or DEFAULT_CLI
    if not 0 < arguments.port < 65536:
        raise SettingsError(f"port must be between 1 and 65535, not {arguments.port}")
    return Settings(
        project=project.resolve(),
        cli=(cli,),
        token=read_token(token_file),
        listen=arguments.listen,
        port=arguments.port,
    )
