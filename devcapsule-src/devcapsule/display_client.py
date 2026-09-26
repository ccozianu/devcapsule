"""Host side of the contained display: the port, the token, the URL, the browser.

The capsule's noVNC bridge (see ``container_runtime/display.py``) is reached
from the host through one loopback port carrying one per-run token. This
module allocates that port, shapes the URL a browser (or a person) needs, and
opens it once the bridge accepts connections. Nothing here touches the host's
own X session.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
import os
import secrets
import socket
import sys
from threading import Event, Thread
import time
from urllib.parse import quote
import webbrowser

from devcapsule.container_runtime.contract import CONTAINED_DISPLAY_TRANSPORT, HOST_X11_DISPLAY_TRANSPORT
from devcapsule.compat import CliError
from devcapsule.host_daemon import in_container
from devcapsule.images.metadata import CONTAINED_DISPLAY_LABEL_VALUE, DISPLAY_LABEL
from devcapsule.host_open import HOST_OPEN_SOCKET_ENV, HostOpenError, open_host_url

# Where the launcher bind-mounts the per-run token inside the capsule and
# where the bridge listens inside the container when Docker publishes it.
DISPLAY_TOKEN_DESTINATION = "/run/devcapsule-display-token"
CONTAINER_DISPLAY_PORT = 6080
DISPLAY_TOKEN_BYTES = 24
DEFAULT_READY_TIMEOUT_SECONDS = 180.0
_READY_POLL_SECONDS = 0.25

Opener = Callable[[str], None]

# What an *unanswered* ``host-x11`` means on an image that has the display
# stack: the contained desktop, the decided default (contained-display
# design note, T6/T7). During the v0.2.12 candidates this was passthrough
# under a product-owner exception (2026-09-13, T7a); flipped for the
# release on 2026-09-14. A recorded ``false`` is now merely explicit.
UNANSWERED_HOST_X11_DISPLAY_TRANSPORT = CONTAINED_DISPLAY_TRANSPORT


def select_display_transport(image_labels: Mapping[str, str], *, host_x11_answer: object) -> tuple[str, str]:
    """The transport for a run and the one-line reason, for the launch to print.

    An image without the display stack (before base recipe 8, labelled by the
    base build) can only do host X11 passthrough. On a capable image the
    developer's ``host-x11`` answer decides: ``true`` is passthrough, and
    ``false`` or no answer is the contained desktop, the default above.
    Shared by ``project run`` and the recursive successor launch so both
    choose the same way.
    """

    if image_labels.get(DISPLAY_LABEL) != CONTAINED_DISPLAY_LABEL_VALUE:
        if host_x11_answer is False:
            raise CliError(
                "Host X11 is explicitly denied, but the selected base has no contained display. "
                "Select a base with contained-display support, or explicitly authorize host-x11 "
                "true after reviewing the host-session exposure. No environment will be built or launched."
            )
        return HOST_X11_DISPLAY_TRANSPORT, (
            "Display: host X11 passthrough; this image predates the contained display "
            "(base recipe 8). Regenerating onto a newer base closes the exposure."
        )
    if host_x11_answer is True:
        return HOST_X11_DISPLAY_TRANSPORT, (
            "Display: host X11 passthrough, authorized by 'host-x11'; the capsule receives "
            "your full X session credential and the boundary test is waived for this run."
        )
    if host_x11_answer is None and UNANSWERED_HOST_X11_DISPLAY_TRANSPORT == HOST_X11_DISPLAY_TRANSPORT:
        return HOST_X11_DISPLAY_TRANSPORT, (
            "Display: host X11 passthrough, the release-candidate default; the capsule receives "
            "your full X session credential. Answer 'host-x11 false' (--authorize host-x11 false, "
            "or 'config authorize host-x11 false') to use the contained desktop instead."
        )
    return CONTAINED_DISPLAY_TRANSPORT, (
        "Display: contained desktop, reached through your browser; no host X session is shared."
    )


def new_display_token() -> str:
    return secrets.token_hex(DISPLAY_TOKEN_BYTES)


def allocate_loopback_port() -> int:
    """A host loopback port that was free a moment ago.

    Docker binds it a little later; the residual race is accepted and, should
    it lose, Docker's own bind failure is reported rather than hidden.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def display_url(port: int, token: str) -> str:
    """The noVNC page, auto-connecting through the token-gated bridge path.

    ``resize=remote`` makes the capsule desktop follow the browser window.
    """

    path = quote(f"websockify?token={token}", safe="")
    return f"http://127.0.0.1:{port}/vnc.html?autoconnect=1&resize=remote&path={path}"


def accepts_connections(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def default_opener(env: Mapping[str, str] | None = None) -> Opener:
    """How this host opens a URL: its browser, or the host-open bridge from a capsule."""

    environment = os.environ if env is None else env
    if in_container():
        # A launcher inside a capsule has no desktop; the authorized bridge to
        # the physical host is the only way out, and printing is the fallback.
        bridge = environment.get(HOST_OPEN_SOCKET_ENV)
        if not bridge:
            return _print_only

        def open_through_bridge(url: str) -> None:
            open_host_url(url, environ=environment)
            print("Contained display is ready; opened through the host-browser bridge.", file=sys.stderr, flush=True)

        return open_through_bridge

    def open_in_browser(url: str) -> None:
        if not webbrowser.open(url, new=2):
            raise HostOpenError("no browser could be started")
        print("Contained display is ready; opened in your browser.", file=sys.stderr, flush=True)

    return open_in_browser


def _print_only(url: str) -> None:
    print(f"Contained display is ready; open it in a browser: {url}", file=sys.stderr, flush=True)


def watch_display_ready(
    port: int,
    url: str,
    opener: Opener,
    stop: Event,
    *,
    timeout: float = DEFAULT_READY_TIMEOUT_SECONDS,
) -> Thread:
    """Open ``url`` on a daemon thread once ``port`` answers; give up on ``stop``.

    The launcher keeps ``docker run`` in the foreground, so readiness is
    watched beside it rather than after it.
    """

    def watch() -> None:
        deadline = time.monotonic() + timeout
        while not stop.is_set():
            if accepts_connections(port):
                try:
                    opener(url)
                except HostOpenError as error:
                    print(
                        f"Contained display is ready but could not be opened ({error}); "
                        f"open it yourself: {url}",
                        file=sys.stderr,
                        flush=True,
                    )
                return
            if time.monotonic() >= deadline:
                print(
                    f"Contained display did not answer on port {port} within {timeout:g}s; "
                    f"if the capsule is still starting, open it yourself: {url}",
                    file=sys.stderr,
                    flush=True,
                )
                return
            stop.wait(_READY_POLL_SECONDS)

    thread = Thread(target=watch, name="devcapsule-display-ready", daemon=True)
    thread.start()
    return thread
