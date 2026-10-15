"""Browser connection shared by deterministic capture and AI-driven interaction."""
from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
import os
from pathlib import Path
import socket
import subprocess
import time
from typing import Any, TYPE_CHECKING
import uuid

from tests.e2e.ai_driver import DriverError

if TYPE_CHECKING:
    from tests.e2e.ide_session import SessionFacts


@contextmanager
def smoke_browser(playwright: Any, session: SessionFacts, evidence: Path) -> Iterator[Any]:
    """Optionally use the browser component in the fresh child, keeping AI auth in the parent."""
    if os.environ.get("DEVCAPSULE_SMOKE_COMPONENT_BROWSER") != "1":
        browser = playwright.chromium.launch()
        try:
            yield browser
        finally:
            browser.close()
        return
    if "browser-automation" not in session.surface.needs:
        raise DriverError("Component-browser mode requires browser-automation in the child")
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    token = uuid.uuid4().hex
    pidfile = f"/tmp/devcapsule-browser-{token}.pid"
    endpoint = f"ws://127.0.0.1:{port}/{token}"
    wrapper = ("import os,sys; from pathlib import Path; "
               f"Path({pidfile!r}).write_text(str(os.getpid())); "
               "os.execv(sys.executable,[sys.executable,'-m','playwright','run-server',"
               f"'--host','127.0.0.1','--port',{str(port)!r},'--path','/{token}','--max-clients','1'])")
    server_log = evidence / f"component-browser-server-{token[:8]}.log"
    with server_log.open("w") as log:
        server = subprocess.Popen([
            "docker", "exec", "--user", f"{os.getuid()}:{os.getgid()}",
            "-e", "PLAYWRIGHT_BROWSERS_PATH=/opt/playwright/browsers", session.container,
            "/opt/playwright/venv/bin/python", "-c", wrapper,
        ], stdout=log, stderr=subprocess.STDOUT)
        browser = None
        try:
            deadline = time.monotonic() + 30
            while "Listening on" not in server_log.read_text():
                if server.poll() is not None or time.monotonic() >= deadline:
                    raise DriverError(f"Child Playwright server did not start; see {server_log.name}")
                time.sleep(0.2)
            browser = playwright.chromium.connect(endpoint, timeout=30_000)
            yield browser
        finally:
            if browser is not None:
                browser.close()
            subprocess.run(["docker", "exec", session.container, "python3", "-c",
                            "import os,signal; from pathlib import Path; "
                            f"p=Path({pidfile!r}); os.kill(int(p.read_text()),signal.SIGTERM); p.unlink()"],
                           capture_output=True, timeout=15, check=False)
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


