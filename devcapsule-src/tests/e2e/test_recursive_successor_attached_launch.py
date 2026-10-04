"""The recursive successor is launched attached, like any capsule, and leaves nothing behind.

Runs only inside a DevCapsule capsule with host-Docker access (the
``recursive_e2e`` marker): the launcher under test realizes this
repository's own environment and starts a successor capsule from it. The
test drives ``launch-successor`` exactly as a developer holds ``project
run``: it starts the command as a subprocess, waits until the run manifest
says the successor is running, inspects it independently, stops the
container, waits for the command to return, and proves that Docker removed
the container and the run directory kept the evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

import pytest

from devcapsule.recursive_successor import (
    CONTAINER_ID_FILE,
    MILESTONE_MANIFEST,
    OWNER_MARKER,
    SUCCESSOR_LOG,
    WORKSPACE_ROOT,
    successor_container_name,
)
from devcapsule.recursive_dogfood import RUNTIME_PLAN_PATH

REPO_ROOT = Path(__file__).resolve().parents[3]
# Realizing the environment may build the formation on first use.
RUNNING_TIMEOUT = 900.0
EXIT_TIMEOUT = 180.0


def _cli(*arguments: str) -> list[str]:
    return [sys.executable, "-m", "devcapsule", "project", "--path", str(REPO_ROOT), "recursive-e2e", *arguments]


def _manifest(run_root: Path) -> dict[str, object]:
    try:
        value = json.loads((run_root / MILESTONE_MANIFEST).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _first_json_object(text: str) -> dict[str, object]:
    """The first JSON object printed on a line of its own: the running report.

    Environment realization may print progress before it, so the text is
    scanned from each line that opens an object until one decodes.
    """
    decoder = json.JSONDecoder()
    position = 0
    while (start := text.find("\n{", position)) != -1 or text.startswith("{"):
        start = 0 if text.startswith("{") and position == 0 else start + 1
        try:
            value, _ = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            position = start + 1
            continue
        if isinstance(value, dict):
            return value
        position = start + 1
    raise AssertionError(f"no JSON report in the launcher output:\n{text[-2000:]}")


def _tail(path: Path, lines: int = 40) -> str:
    try:
        return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])
    except OSError:
        return ""


@pytest.mark.e2e
@pytest.mark.recursive_e2e
def test_attached_successor_launch_runs_inspects_and_leaves_nothing_behind(tmp_path: Path) -> None:
    assert RUNTIME_PLAN_PATH.is_file(), "the recursive E2E runs inside a DevCapsule capsule"
    docker = shutil.which("docker")
    assert docker is not None, "Docker CLI is required for the recursive E2E"

    run_id = uuid.uuid4().hex
    name = successor_container_name(run_id)
    run_root = WORKSPACE_ROOT / run_id
    run_root.mkdir(parents=True, mode=0o700)
    (run_root / OWNER_MARKER).write_text(json.dumps({"schema_version": 1, "run_id": run_id}), encoding="utf-8")
    (run_root / MILESTONE_MANIFEST).write_text(
        json.dumps({"schema_version": 1, "run_id": run_id, "state": "stage-5-materialized"}), encoding="utf-8"
    )
    launcher_log = tmp_path / "launch-successor.log"
    launcher: subprocess.Popen[bytes] | None = None
    try:
        with launcher_log.open("wb") as log:
            launcher = subprocess.Popen(
                _cli("launch-successor", "--run-id", run_id, "--json"),
                stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            )

        # 1. The command stays attached while the successor runs, and the
        #    manifest says so before the command prints anything else.
        deadline = time.monotonic() + RUNNING_TIMEOUT
        while _manifest(run_root).get("state") != "stage-6-running":
            if launcher.poll() is not None:
                pytest.fail(
                    f"launch-successor exited {launcher.returncode} before the successor ran:\n"
                    f"{_tail(launcher_log)}\n--- successor log ---\n{_tail(run_root / SUCCESSOR_LOG)}"
                )
            assert time.monotonic() < deadline, f"successor not running after {RUNNING_TIMEOUT:g}s:\n{_tail(launcher_log)}"
            time.sleep(1.0)
        assert launcher.poll() is None, "the launcher returned although the successor is running"
        launch = _manifest(run_root)["launch"]
        assert isinstance(launch, dict) and launch["lifecycle"] == "attached"
        container_id = str(launch["container_id"])
        assert (run_root / CONTAINER_ID_FILE).read_text(encoding="utf-8").strip() == container_id
        running = subprocess.run([docker, "inspect", "--format", "{{.State.Running}}", container_id],
                                 text=True, capture_output=True, check=False)
        assert running.stdout.strip() == "true", running.stderr

        # 2. The running report was printed, and the independent inspection
        #    passes against the same container.
        report = _first_json_object(launcher_log.read_text(encoding="utf-8", errors="replace"))
        assert report["state"] == "running" and report["container_id"] == container_id
        inspected = subprocess.run(_cli("inspect-successor", "--run-id", run_id, "--json"),
                                   text=True, capture_output=True, check=False)
        assert inspected.returncode == 0, inspected.stdout + inspected.stderr
        assert json.loads(inspected.stdout)["state"] == "inspection-passed"

        # 3. Stopping the container ends the attached command, Docker removes
        #    the container, and the run directory keeps the evidence.
        subprocess.run([docker, "stop", "--time", "30", name], text=True, capture_output=True, check=False)
        launcher.wait(timeout=EXIT_TIMEOUT)
        final = _manifest(run_root)
        assert final.get("state") == "stage-6-exited", final
        finished = final["launch"]
        assert isinstance(finished, dict) and isinstance(finished.get("exit_code"), int) and finished.get("container_removed") is True
        assert subprocess.run([docker, "inspect", container_id], capture_output=True, check=False).returncode != 0, "Docker kept the successor"
        assert (run_root / SUCCESSOR_LOG).is_file()
        # An exited successor is reported as such, not inspected as alive.
        again = subprocess.run(_cli("inspect-successor", "--run-id", run_id, "--json"), text=True, capture_output=True, check=False)
        assert again.returncode != 0 and "has exited" in (again.stdout + again.stderr)
    finally:
        if launcher is not None and launcher.poll() is None:
            subprocess.run([docker, "stop", "--time", "10", name], capture_output=True, check=False)
            try:
                launcher.wait(timeout=60.0)
            except subprocess.TimeoutExpired:
                launcher.kill()
        subprocess.run([docker, "rm", "--force", name], capture_output=True, check=False)
        shutil.rmtree(run_root, ignore_errors=True)
