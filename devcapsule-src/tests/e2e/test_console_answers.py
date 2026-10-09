"""The web console answers in a fresh capsule, with and without a display.

Deliverable 1 of the capsule web console work order, as the smoke the
acceptance evidence asks for: ``project run`` prints a console URL, the
console answers on it, a tokenless request is refused, and a path outside
the mount is refused. The headless case runs the same materialized image
through the runtime's job mode, which starts no display at all.
"""
from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import quote, urlsplit
import uuid

import pytest

from tests.e2e.ide_session import SURFACES, command, ide_session, wait_for_console_url

EVIDENCE_ROOT = Path(__file__).resolve().parents[2] / "dist" / "e2e-evidence" / "console-smoke"
SURFACE = next(surface for surface in SURFACES if surface.name == "codium")


def fetch(url: str, *, headers: dict[str, str] | None = None, patience: float = 30.0) -> tuple[int, str]:
    """Status and body of ``url``; retries a refused connection within ``patience``."""
    parts = urlsplit(url)
    deadline = time.monotonic() + patience
    while True:
        connection = http.client.HTTPConnection(parts.hostname or "127.0.0.1", parts.port or 80, timeout=10)
        try:
            target = parts.path + (f"?{parts.query}" if parts.query else "")
            connection.request("GET", target, headers=headers or {})
            response = connection.getresponse()
            return response.status, response.read().decode("utf-8", errors="replace")
        except OSError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)
        finally:
            connection.close()


def check_console(url: str, evidence: Path, label: str) -> dict[str, object]:
    """The four facts of deliverable 1 against a live console at ``url``."""
    token = urlsplit(url).query.removeprefix("token=")
    base = url.split("/?", 1)[0]
    headers = {"X-DevCapsule-Token": token}
    home_status, home = fetch(url)
    configuration_status, configuration = fetch(f"{base}/api/configuration", headers=headers)
    page_status, _ = fetch(f"{base}/configuration", headers=headers)
    refused_status, refused = fetch(f"{base}/api/configuration")
    traversal_status, _ = fetch(f"{base}/api/project/file?path={quote('../../etc/passwd', safe='')}", headers=headers)
    absolute_status, _ = fetch(f"{base}/api/project/file?path={quote('/etc/passwd', safe='')}", headers=headers)
    inside_status, inside = fetch(f"{base}/api/project/file?path=README.md", headers=headers)
    facts = {
        "label": label, "home_status": home_status, "configuration_page_status": page_status,
        "configuration_api_status": configuration_status, "tokenless_status": refused_status,
        "traversal_status": traversal_status, "absolute_status": absolute_status, "inside_status": inside_status,
    }
    (evidence / f"{label}-facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
    (evidence / f"{label}-configuration.json").write_text(configuration, encoding="utf-8")
    assert home_status == 200 and "DevCapsule console" in home, home[:400]
    assert page_status == 200
    assert configuration_status == 200, configuration[:400]
    assert json.loads(configuration)["schema-version"] == 1
    assert refused_status == 403 and "run token" in refused
    assert traversal_status == 403 and absolute_status == 403
    assert inside_status == 200 and inside.startswith("#")
    return facts


@pytest.mark.e2e
@pytest.mark.ide_smoke
def test_console_answers_with_and_without_a_display(built_pex: Path, tmp_path: Path) -> None:
    evidence = EVIDENCE_ROOT / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:6]}"
    evidence.mkdir(parents=True)
    with ide_session(built_pex, SURFACE, tmp_path, evidence / "with-display") as session:
        # With a display: project run printed the console URL beside the desktop's.
        assert session.launcher is not None
        console = wait_for_console_url(session.launcher, session.launcher_log)
        (evidence / "with-display" / "console-url.txt").write_text(console + "\n", encoding="utf-8")
        check_console(console, evidence / "with-display", "with-display")
        runtime = json.loads(command("docker", "exec", session.container, "cat", "/etc/devcapsule/runtime-plan.json").stdout)
        assert runtime["console"]["token_path"] == "/run/devcapsule-console-token"
        image = command("docker", "inspect", "--format", "{{.Config.Image}}", session.container).stdout.strip()
        plan = dict(runtime)

    # Without a display: the same image, the runtime's job mode, no display
    # section at all; the console still runs and still needs the token.
    headless_dir = evidence / "headless"
    headless_dir.mkdir()
    token = uuid.uuid4().hex
    token_file = tmp_path / "console-token"
    token_file.write_text(token + "\n", encoding="utf-8")
    token_file.chmod(0o644)
    plan.pop("display", None)
    plan["console"] = {"listen_address": "0.0.0.0", "port": 6081, "token_path": "/run/devcapsule-console-token"}
    plan_file = tmp_path / "runtime-plan.json"
    plan_file.write_text(json.dumps(plan) + "\n", encoding="utf-8")
    container = f"devcapsule-console-smoke-{uuid.uuid4().hex[:8]}"
    port = _free_port()
    started = subprocess.Popen(
        ["docker", "run", "--rm", "--name", container, "--entrypoint", "/opt/devcapsule/bin/devcapsule.pex",
         "--publish", f"127.0.0.1:{port}:6081",
         "--mount", f"type=bind,src={token_file},dst=/run/devcapsule-console-token,ro",
         "--mount", f"type=bind,src={plan_file},dst=/etc/devcapsule/runtime-plan.json,ro",
         "--mount", f"type=bind,src={session.workspace},dst={plan['project_path']},ro",
         image, "runtime", "/etc/devcapsule/runtime-plan.json", "--", "sleep", "300"],
        stdout=(headless_dir / "docker-run.log").open("wb"), stderr=subprocess.STDOUT,
    )
    try:
        facts = check_console(f"http://127.0.0.1:{port}/?token={token}", headless_dir, "headless")
        assert facts["home_status"] == 200
    finally:
        command("docker", "stop", "--time", "10", container, check=False, timeout=60.0)
        started.wait(timeout=60.0)


def _free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])
