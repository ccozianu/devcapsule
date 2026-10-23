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

from devcapsule.docker_arguments import environment_options

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


def read_environment(path: Path) -> dict[str, str]:
    return {value.partition("=")[0]: value.partition("=")[2]
            for _, _, value in environment_options(read_arguments(path))}


def update_environment(path: Path, name: str, value: str | None) -> None:
    validate_name(name)
    if value is not None:
        validate_value(value)

    def update(arguments: list[str]) -> list[str]:
        removed = {index for start, end, item in environment_options(arguments)
                   if item.partition("=")[0] == name for index in range(start, end)}
        result = [item for index, item in enumerate(arguments) if index not in removed]
        if value is not None:
            result.extend(["--env", f"{name}={value}"])
        return result

    change_arguments(path, update)
