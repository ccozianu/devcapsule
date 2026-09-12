"""The contained display: the capsule's own X server and its browser bridge.

Nothing here is declared by the user. When the runtime plan's display section
says ``contained``, the entrypoint derives three infrastructure children from
it and starts them, in order, ahead of the interactive surface:

1. ``Xvnc`` — an X server with a virtual framebuffer and the RFB server built
   in, so the capsule renders to memory and knows exactly which rectangles
   changed. It serves RFB on a Unix socket only and gates X clients with a
   per-run cookie.
2. ``openbox`` — a window manager, because Java IDEs need one for focus,
   dialogs and popups.
3. ``websockify`` — serves noVNC's page and bridges WebSocket to the RFB
   socket, admitting only requests that carry the run's token.

The surface then runs with ``DISPLAY`` and ``XAUTHORITY`` pointing at that
server. See ``engineering-docs/wip/2026-08-19-contained-display/
display-transport-design.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import secrets
import socket
import struct
from typing import Callable

from .contract import RuntimePlan, RuntimePlanError
from .supervisor import SupervisedChild

DISPLAY_NUMBER = 1
DISPLAY_NAME = f":{DISPLAY_NUMBER}"
X_SOCKET_PATH = f"/tmp/.X11-unix/X{DISPLAY_NUMBER}"
NOVNC_WEB_ROOT = "/usr/share/novnc"
DEFAULT_GEOMETRY = "1920x1080"
DEFAULT_DEPTH = "24"
DEFAULT_DPI = "96"

XVNC_CHILD = "xvnc"
WINDOW_MANAGER_CHILD = "window-manager"
NOVNC_CHILD = "novnc"

# Xauthority entry families (libXau): a wildcard entry matches any address, so
# the cookie applies however a client names the local display.
_FAMILY_WILD = 0xFFFF
_COOKIE_PROTOCOL = b"MIT-MAGIC-COOKIE-1"

CommandWrapper = Callable[[tuple[str, ...]], tuple[str, ...]]


@dataclass(frozen=True)
class ContainedDisplay:
    """What the entrypoint needs after preparation: children and environment."""

    children: tuple[SupervisedChild, ...]
    environment: dict[str, str]
    xauthority_path: str
    rfb_socket_path: str


def prepare_contained_display(
    plan: RuntimePlan,
    runtime_directory: str,
    run_as_identity: CommandWrapper,
) -> ContainedDisplay:
    """Create the per-run display files and declare the display children.

    ``runtime_directory`` is the capsule user's ``XDG_RUNTIME_DIR`` (mode
    0700). ``run_as_identity`` wraps a command so it runs as the capsule user
    when the entrypoint itself is root; every display process runs as that
    user, never as root.
    """

    display = plan.display
    if display is None or not display.is_contained:
        raise RuntimePlanError("the runtime plan does not select the contained display")
    directory = Path(runtime_directory) / "display"
    directory.mkdir(mode=0o700, exist_ok=True)
    _own(directory, plan)

    xauthority = directory / "Xauthority"
    write_xauthority(xauthority, DISPLAY_NUMBER, secrets.token_bytes(16))
    _own(xauthority, plan)

    rfb_socket = directory / "rfb.sock"
    tokens = directory / "tokens"
    tokens.write_text(f"{read_token(display.token_path)}: unix_socket:{rfb_socket}\n", encoding="utf-8")
    tokens.chmod(0o600)
    _own(tokens, plan)

    listen = f"{display.listen_address}:{display.port}"
    probe_address = "127.0.0.1" if display.listen_address in ("0.0.0.0", "::") else display.listen_address
    children = (
        SupervisedChild(
            name=XVNC_CHILD,
            command=run_as_identity(
                (
                    "Xvnc",
                    DISPLAY_NAME,
                    "-auth", str(xauthority),
                    "-rfbunixpath", str(rfb_socket),
                    "-rfbunixmode", "0600",
                    # No TCP listener at all: RFB is reachable only through
                    # the Unix socket, which only the bridge and the capsule
                    # user can open. Hence no RFB security type is needed.
                    "-rfbport", "-1",
                    "-SecurityTypes", "None",
                    "-geometry", DEFAULT_GEOMETRY,
                    "-depth", DEFAULT_DEPTH,
                    "-dpi", DEFAULT_DPI,
                    "-desktop", f"DevCapsule {plan.component.id}",
                    "-AlwaysShared",
                )
            ),
            ready=lambda: _is_socket(X_SOCKET_PATH) and _is_socket(str(rfb_socket)),
        ),
        SupervisedChild(
            name=WINDOW_MANAGER_CHILD,
            command=run_as_identity(("openbox",)),
        ),
        SupervisedChild(
            name=NOVNC_CHILD,
            command=run_as_identity(
                (
                    "websockify",
                    "--web", NOVNC_WEB_ROOT,
                    "--token-plugin", "TokenFile",
                    "--token-source", str(tokens),
                    listen,
                )
            ),
            ready=lambda: _accepts_connections(probe_address, display.port),
        ),
    )
    environment = {"DISPLAY": DISPLAY_NAME, "XAUTHORITY": str(xauthority)}
    return ContainedDisplay(children, environment, str(xauthority), str(rfb_socket))


def read_token(path: str) -> str:
    """The launcher-supplied per-run token; one line, no whitespace."""

    try:
        token = Path(path).read_text(encoding="utf-8").strip()
    except OSError as error:
        raise RuntimePlanError(f"cannot read the display token at {path}: {error}") from error
    if not token or any(character.isspace() for character in token) or ":" in token:
        raise RuntimePlanError(f"the display token at {path} is empty or malformed")
    return token


def write_xauthority(path: Path, display_number: int, cookie: bytes) -> None:
    """Write a one-entry Xauthority file granting ``cookie`` for the display.

    The format is libXau's: big-endian 16-bit family, then length-prefixed
    address, display number, protocol name and data.
    """

    def field(value: bytes) -> bytes:
        return struct.pack(">H", len(value)) + value

    entry = (
        struct.pack(">H", _FAMILY_WILD)
        + field(b"")
        + field(str(display_number).encode("ascii"))
        + field(_COOKIE_PROTOCOL)
        + field(cookie)
    )
    path.write_bytes(entry)
    path.chmod(0o600)


def _own(path: Path, plan: RuntimePlan) -> None:
    if os.geteuid() == 0:
        os.chown(path, plan.identity.uid, plan.identity.gid)


def _is_socket(path: str) -> bool:
    try:
        return Path(path).is_socket()
    except OSError:
        return False


def _accepts_connections(address: str, port: int) -> bool:
    try:
        with socket.create_connection((address, port), timeout=0.2):
            return True
    except OSError:
        return False
