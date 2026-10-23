"""Checkout-local Docker env-files, outside resolutions and configuration history.

Values are literal single-line UTF-8 strings. Readers never expand shell syntax.
The Docker client reads the file locally, even with a remote daemon.
"""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import re
import tempfile

from .file_formats import ProjectConfigurationError
from .storage import config_root

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def environment_path(checkout_record: Path) -> Path:
    # Project records are mounted into the capsule; keep files in a separate
    # tree so the mount cannot expose another checkout's environment.
    relative = checkout_record.relative_to(config_root() / "projects")
    name = relative.name.removesuffix(".checkout.toml")
    return config_root() / "environments" / relative.parent / name / "secrets.env"


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


def read_environment(path: Path) -> dict[str, str]:
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            text = stream.read()
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeError):
        raise ProjectConfigurationError(f"Cannot read managed environment file: {path}") from None
    result: dict[str, str] = {}
    # Split only on LF; other Unicode separators are literal Docker values.
    for line in text.split("\n"):
        if not line:
            continue
        name, separator, value = line.partition("=")
        if not separator or not _NAME.fullmatch(name) or name in result:
            raise ProjectConfigurationError(f"Invalid managed environment file: {path}")
        validate_value(value)
        result[name] = value
    return result


def update_environment(path: Path, name: str, value: str | None) -> None:
    validate_name(name)
    if value is not None:
        validate_value(value)
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.parent.chmod(0o700)
        # Serialize read-modify-write so concurrent settings do not lose keys.
        with (path.parent / ".lock").open("a") as lock:
            os.fchmod(lock.fileno(), 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            values = read_environment(path)
            if value is None:
                values.pop(name, None)
            else:
                values[name] = value
            temporary: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                                 prefix=".incoming-", delete=False) as stream:
                    temporary = Path(stream.name)
                    os.fchmod(stream.fileno(), 0o600)
                    for key in sorted(values):
                        stream.write(f"{key}={values[key]}\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
    except OSError:
        raise ProjectConfigurationError(f"Cannot update managed environment file: {path}") from None


def environment_docker_args(checkout_record: Path) -> list[str]:
    path = environment_path(checkout_record)
    # Validate before Docker can quote a bad line (and its value) in an error.
    return ["--env-file", str(path)] if read_environment(path) else []
