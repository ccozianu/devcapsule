"""Private checkout Docker arguments, outside resolutions and history.

Store literal argument tokens as JSON. Docker interprets them, never a shell.
The environment commands are conveniences over the same saved argument list.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Callable

from devcapsule.docker_arguments import ambiguous_environment_options, environment_options

from .file_formats import ProjectConfigurationError
from .storage import config_root

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def arguments_path(checkout_record: Path) -> Path:
    # Project records are mounted into the capsule; keep files in a separate
    # tree so the mount cannot expose another checkout's environment.
    relative = checkout_record.relative_to(config_root() / "projects")
    name = relative.name.removesuffix(".checkout.toml")
    return config_root() / "docker-arguments" / relative.parent / name / "arguments.json"


def validate_name(name: str) -> None:
    if not _NAME.fullmatch(name):
        raise ProjectConfigurationError("Environment name must be an ASCII identifier.")


def validate_value(value: str) -> None:
    if any(character in value for character in ("\n", "\r", "\x00")):
        raise ProjectConfigurationError("Environment values must be single-line text without NUL.")
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise ProjectConfigurationError("Environment values must be valid UTF-8 text.") from None


def validate_arguments(arguments: list[str]) -> None:
    for argument in arguments:
        if "\x00" in argument:
            raise ProjectConfigurationError("Docker arguments must not contain NUL.")
        try:
            argument.encode("utf-8")
        except UnicodeError:
            raise ProjectConfigurationError("Docker arguments must be valid UTF-8 text.") from None


def read_arguments(path: Path) -> list[str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except (UnicodeError, json.JSONDecodeError):
        raise ProjectConfigurationError(f"Invalid saved Docker arguments: {path}") from None
    except OSError as exc:
        raise ProjectConfigurationError(f"Cannot read saved Docker arguments {path}: {exc.strerror or exc}") from None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProjectConfigurationError(f"Invalid saved Docker arguments: {path}")
    try:
        validate_arguments(value)
    except ProjectConfigurationError:
        raise ProjectConfigurationError(f"Invalid saved Docker arguments: {path}") from None
    return value


def change_arguments(path: Path, change: Callable[[list[str]], list[str]], *, replace: bool = False) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.parent.chmod(0o700)
        with (path.parent / ".lock").open("a") as lock:
            os.fchmod(lock.fileno(), 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            previous = [] if replace else read_arguments(path)
            arguments = change(previous)
            validate_arguments(arguments)
            if not arguments:
                path.unlink(missing_ok=True)
                return
            temporary: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                                 prefix=".incoming-", delete=False) as stream:
                    temporary = Path(stream.name)
                    os.fchmod(stream.fileno(), 0o600)
                    json.dump(arguments, stream, ensure_ascii=True)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
    except OSError as exc:
        raise ProjectConfigurationError(f"Cannot update saved Docker arguments {path}: {exc.strerror or exc}") from None


def replace_arguments(path: Path, arguments: list[str]) -> None:
    validate_arguments(arguments)
    change_arguments(path, lambda _: arguments, replace=True)


def _refuse_ambiguous(arguments: list[str], name: str | None = None) -> None:
    """Refuse before any write when the saved list has a token the bounded
    environment helper cannot place: the value of the bare option before it,
    or an environment option. Positions only; never the tokens themselves."""
    for start, _end, value in ambiguous_environment_options(arguments):
        if name is not None and value.partition("=")[0] != name:
            continue
        subject = f"environment variable {name}" if name is not None else "an environment option"
        raise ProjectConfigurationError(
            f"Saved Docker argument {start + 1} may be {subject} or the value of argument {start}; "
            "the environment commands cannot tell which. Replace the complete list with "
            "'devcapsule project config set-extra-docker-args -- ...', placing environment options "
            "first or after a value; 'list-extra-docker-args' shows the saved tokens with values masked."
        )


def read_environment(path: Path) -> dict[str, str]:
    arguments = read_arguments(path)
    _refuse_ambiguous(arguments)
    return {value.partition("=")[0]: value.partition("=")[2]
            for _, _, value in environment_options(arguments)}


def update_environment(path: Path, name: str, value: str | None) -> None:
    validate_name(name)
    if value is not None:
        validate_value(value)

    def update(arguments: list[str]) -> list[str]:
        _refuse_ambiguous(arguments, name)
        matching = [(start, end) for start, end, item in environment_options(arguments)
                    if item.partition("=")[0] == name]
        replacement = [] if value is None else ["--env", f"{name}={value}"]
        if not matching:
            # The front of the list is never an operand, so a later edit can
            # still recognize what this one saved.
            return [*replacement, *arguments]
        result: list[str] = []
        index = 0
        for start, end in matching:
            result.extend(arguments[index:start])
            if start == matching[0][0]:
                result.extend(replacement)  # the first occurrence keeps its place
            index = end
        result.extend(arguments[index:])
        return result

    change_arguments(path, update)
