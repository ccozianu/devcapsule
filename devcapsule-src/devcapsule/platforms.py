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

from dataclasses import dataclass, field
from enum import StrEnum
import os
from pathlib import Path
import platform as host_platform
from typing import Mapping

__all__ = ["HostOs", "Platform", "UnsupportedPlatformError", "XdgHomes", "host_architecture"]


class UnsupportedPlatformError(ValueError):
    """A platform key outside the supported set; the message is displayable."""


def host_architecture() -> str:
    """This host's CPU architecture in the platform keys' spelling."""

    machine = host_platform.machine().lower()
    return {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)


class HostOs(StrEnum):
    """The host operating system, for the mechanisms that differ by host.

    Locks never carry it: capsules are Linux on every host, and the lock
    names the capsule platform (``Platform``).
    """

    LINUX = "linux"
    DARWIN = "darwin"

    @classmethod
    def current(cls) -> HostOs:
        system = host_platform.system().lower()
        try:
            return cls(system)
        except ValueError:
            supported = ", ".join(member.value for member in cls)
            raise UnsupportedPlatformError(
                f"Unsupported host operating system {system!r}; supported: {supported}."
            ) from None


# The capsule platform a non-Linux host runs. Apple Silicon runs linux-amd64
# under Docker's emulation until a linux-arm64 platform exists.
_CAPSULE_PLATFORM_OF_HOST = {
    "darwin-arm64": "linux-amd64",
    "darwin-amd64": "linux-amd64",
}


class Platform(StrEnum):
    """The supported capsule platforms and their wire format.

    A platform is what capsules run as, not what the launcher runs on: a
    Mac launches Linux capsules. Members are the single authority on what
    capsule platforms DevCapsule supports; values are the wire format
    serialized into lock filenames, lock documents, and artifact tables.
    Because committed locks carry these values, members are append-only and
    never renamed.

    A client never constructs a key from parts: it obtains one from
    ``current()`` (the platform this host runs capsules as) or ``parse()``
    (the platform a lock records), and only carries it between those points.
    """

    LINUX_AMD64 = "linux-amd64"

    @classmethod
    def current(cls) -> Platform:
        """The platform this host runs capsules as.

        On Linux, the host's own platform. On macOS, the Linux platform
        Docker Desktop runs, natively or under emulation.
        """

        host = f"{host_platform.system().lower()}-{host_architecture()}"
        return cls.parse(_CAPSULE_PLATFORM_OF_HOST.get(host, host))

    @property
    def architecture(self) -> str:
        return self.value.split("-", 1)[1]

    @property
    def docker_platform(self) -> str:
        """Docker's spelling of this platform, as ``--platform`` takes it."""

        return self.value.replace("-", "/", 1)

    def emulated(self) -> bool:
        """Whether this host's CPU runs capsules of this platform only under emulation."""

        return host_architecture() != self.architecture

    def docker_platform_args(self) -> list[str]:
        """The ``--platform`` option every run and build carries under emulation.

        Empty on a native host, so a Linux launch composes the same command
        as before the option existed.
        """

        return [f"--platform={self.docker_platform}"] if self.emulated() else []

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
    chosen_by: str = field(default="default", compare=False)

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> XdgHomes:
        values = os.environ if env is None else env
        named = values.get("DEVCAPSULE_CONFIG_HOME")
        if named:
            root = Path(named).expanduser().resolve()
            return cls(root, root / "data", root / "state", root / "cache", "DEVCAPSULE_CONFIG_HOME")
        home = Path(values.get("HOME", "~")).expanduser()

        def scoped(variable: str, *default: str) -> Path:
            return Path(values.get(variable) or home.joinpath(*default)) / "devcapsule"

        return cls(
            config=scoped("XDG_CONFIG_HOME", ".config"),
            data=scoped("XDG_DATA_HOME", ".local", "share"),
            state=scoped("XDG_STATE_HOME", ".local", "state"),
            cache=scoped("XDG_CACHE_HOME", ".cache"),
            chosen_by="XDG_CONFIG_HOME" if values.get("XDG_CONFIG_HOME") else "default",
        )
