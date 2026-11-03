"""Locate the exact launcher artifact to deliver into a formation."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from devcapsule.build_info import BuildInfoError, read_pex_build_info
from devcapsule.compat import CliError
from devcapsule.platforms import Platform

RUNTIME_PEX_ENV = "DEVCAPSULE_RUNTIME_PEX"

# ELF e_machine values, by the architecture spelling of platform keys.
_ELF_MACHINES = {0x3E: "amd64", 0xB7: "arm64"}
_MACH_O_MAGICS = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe")


def runtime_artifact() -> Path:
    """The DevCapsule executable this launch delivers into the capsule.

    A packaged launcher delivers itself when its binary runs on the capsule
    platform. A launcher that cannot, a macOS executable launching Linux
    capsules, delivers the runtime ``DEVCAPSULE_RUNTIME_PEX`` names. A
    source-form launcher must name its built runtime the same way.
    """

    capsule = Platform.current()
    # scie preserves the executable's path in SCIE; PEX points to the original
    # archive too. sys.argv[0] alone can name the extracted console script.
    own = os.environ.get("SCIE") or os.environ.get("PEX")
    explicit = os.environ.get(RUNTIME_PEX_ENV)
    path = _resolved(own or explicit or sys.argv[0])
    if own and explicit and executable_platform(path) not in (None, str(capsule)):
        path = _resolved(explicit)
    try:
        read_pex_build_info(path)
    except BuildInfoError as exc:
        raise CliError(
            "Environment materialization needs a DevCapsule PEX. Run the built PEX, "
            "or build with 'nox -s pex' and set DEVCAPSULE_RUNTIME_PEX to its path "
            "when running from source."
        ) from exc
    found = executable_platform(path)
    if found not in (None, str(capsule)):
        raise CliError(
            f"{path} is a {found} executable and cannot run inside {capsule} capsules. "
            f"Set {RUNTIME_PEX_ENV} to a {capsule} DevCapsule executable of the same version."
        )
    return path


def executable_platform(path: Path) -> str | None:
    """The platform a native executable runs on, from its header.

    ``darwin`` for any Mach-O file, ``linux-<arch>`` for an ELF file of a
    known architecture, and None for anything else, such as a plain PEX
    archive, whose interpreter the capsule supplies.
    """

    try:
        with path.open("rb") as handle:
            header = handle.read(20)
    except OSError:
        return None
    if header[:4] in _MACH_O_MAGICS:
        return "darwin"
    if header[:4] == b"\x7fELF" and len(header) >= 20:
        machine = int.from_bytes(header[18:20], "little" if header[5] == 1 else "big")
        architecture = _ELF_MACHINES.get(machine)
        return f"linux-{architecture}" if architecture else "linux-unknown"
    return None


def _resolved(selected: str) -> Path:
    return Path(selected).expanduser().resolve()
