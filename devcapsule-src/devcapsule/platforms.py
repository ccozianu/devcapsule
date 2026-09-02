"""How this host names and locates things (D-0006).

This module owns the project's friction with the host platform: OS-specific
and environment-specific conventions. Code belongs here if and only if it
expresses how the host names or locates things by OS or environment
convention — and would therefore change only when those conventions or the
supported-platform set change, never when product features change. Feature
code that merely consumes environment variables stays with its feature.

The module is terminal in the package's dependency graph: it imports nothing
of DevCapsule's.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path
import platform as host_platform
from typing import Mapping

__all__ = ["Platform", "UnsupportedPlatformError", "XdgHomes"]


class UnsupportedPlatformError(ValueError):
    """A platform key outside the supported set; the message is displayable."""


class Platform(StrEnum):
    """The supported-platform declaration and its wire format.

    Members are the single authority on what platforms DevCapsule supports;
    values are the wire format serialized into lock filenames, lock
    documents, and artifact tables. Because committed locks carry these
    values, members are append-only and never renamed.

    A client never constructs a key from parts: it obtains one from
    ``current()`` (the platform it is running on) or ``parse()`` (the
    platform a lock records), and only carries it between those points.
    """

    LINUX_AMD64 = "linux-amd64"

    @classmethod
    def current(cls) -> Platform:
        """The platform this process is running on."""

        system = host_platform.system().lower()
        machine = host_platform.machine().lower()
        architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
        return cls.parse(f"{system}-{architecture}")

    @classmethod
    def parse(cls, key: str) -> Platform:
        """The member a lock's recorded platform key names."""

        try:
            return cls(key)
        except ValueError:
            supported = ", ".join(member.value for member in cls)
            raise UnsupportedPlatformError(
                f"Unsupported platform {key!r}; supported platforms: {supported}."
            ) from None


@dataclass(frozen=True)
class XdgHomes:
    """DevCapsule's user-scoped directories per the XDG base-directory spec.

    The one derivation of the convention: each directory honors its
    ``XDG_*_HOME`` override and falls back to the specified default under
    ``HOME``, always scoped by a ``devcapsule`` segment.
    """

    config: Path
    data: Path
    state: Path
    cache: Path

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> XdgHomes:
        values = os.environ if env is None else env
        home = Path(values.get("HOME", "~")).expanduser()

        def scoped(variable: str, *default: str) -> Path:
            return Path(values.get(variable) or home.joinpath(*default)) / "devcapsule"

        return cls(
            config=scoped("XDG_CONFIG_HOME", ".config"),
            data=scoped("XDG_DATA_HOME", ".local", "share"),
            state=scoped("XDG_STATE_HOME", ".local", "state"),
            cache=scoped("XDG_CACHE_HOME", ".cache"),
        )
