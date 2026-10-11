"""The capsule web console as a supervised child of the entrypoint.

When the runtime plan carries a console section, the entrypoint starts the
console beside the display infrastructure, or alone in a headless capsule,
ahead of the foreground child. The console is its own distribution, installed
by the base image under ``/opt/devcapsule-webconsole`` (base recipe 10); it
reads the mounted project and calls the runtime CLI's ``--json`` outputs. See
``R-CONSOLE-001`` and ``engineering-docs/work-orders/2026-10-09-capsule-webconsole.md``.
"""

from __future__ import annotations

from pathlib import Path
import socket
import subprocess
import sys
from typing import Callable

from .contract import RuntimePlan
from .supervisor import SupervisedChild

CONSOLE_CHILD = "console"
CONSOLE_ROOT = "/opt/devcapsule-webconsole"
"""Where the base image installs the console: a hash-pinned venv and the package."""
CONSOLE_PYTHON = f"{CONSOLE_ROOT}/venv/bin/python"
RUNTIME_CLI = "/opt/devcapsule/bin/devcapsule.pex"
"""The launcher-supplied runtime executable the console calls for its documents."""
# FastAPI's import and uvicorn's bind take a few seconds on a cold, loaded
# host; the display's default margin is tuned for an X server.
CONSOLE_READY_TIMEOUT_SECONDS = 60.0

CommandWrapper = Callable[[tuple[str, ...]], tuple[str, ...]]


def console_child(plan: RuntimePlan, run_as_identity: CommandWrapper) -> SupervisedChild | None:
    """The console child for ``plan``, or ``None`` when there is none to start.

    ``None`` when the plan carries no console section, and, announced, when
    the base predates the console (recipe 9 and earlier): the runtime is
    launcher-supplied and runs on any base carrying the display label, so an
    absent console is a known degradation rather than a failed start.
    """

    console = plan.console
    if console is None:
        return None
    if not Path(CONSOLE_PYTHON).is_file():
        print(
            f"devcapsule console: this base has no web console (base recipe 10 adds it at {CONSOLE_ROOT}); "
            "the capsule runs without one",
            file=sys.stderr,
            flush=True,
        )
        return None
    command: tuple[str, ...] = (
        CONSOLE_PYTHON, "-m", "devcapsule_webconsole",
        "--project", plan.project_path,
        "--cli", RUNTIME_CLI,
        "--token-file", console.token_path,
        "--listen", console.listen_address,
        "--port", str(console.port),
    )
    if console.source_path and _monitor_dependency_available():
        # The checkout's own console source, ahead of the image's installed
        # copy: the same interpreter and dependencies, the mounted package.
        command = ("env", f"PYTHONPATH={console.source_path}", *command)
        print(
            f"devcapsule console: running the mounted checkout's source at {console.source_path}",
            file=sys.stderr,
            flush=True,
        )
    elif console.source_path:
        print(
            "devcapsule console: the base cannot import psutil (base recipe 11 adds it); "
            "running the installed console instead of the mounted source",
            file=sys.stderr,
            flush=True,
        )
    probe_address = {"0.0.0.0": "127.0.0.1", "::": "::1"}.get(console.listen_address, console.listen_address)
    return SupervisedChild(
        name=CONSOLE_CHILD,
        command=run_as_identity(command),
        ready=lambda: _accepts_connections(probe_address, console.port),
        ready_timeout_seconds=CONSOLE_READY_TIMEOUT_SECONDS,
    )


def _monitor_dependency_available() -> bool:
    """Check the base interpreter, without the checkout or ambient PYTHONPATH.

    Recipe 10 has the console but lacks psutil. Its installed console still
    works; mounting slice-5 source over it would fail at import time.
    """
    try:
        subprocess.run(
            [CONSOLE_PYTHON, "-I", "-c", "import psutil"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5.0,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _accepts_connections(address: str, port: int) -> bool:
    try:
        with socket.create_connection((address, port), timeout=0.2):
            return True
    except OSError:
        return False
