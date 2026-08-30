"""Fake-children tests for the supervisor's reap/forward/shutdown machine.

The supervisor blocks and waits on signals in the thread that runs it, which
must not happen inside the pytest process. Every behavioral test therefore
runs the supervisor in its own process via ``tests/resources/supervisor_driver.py``
against fake children (exit/sleep/ignore-TERM shell one-liners) and observes
what PID 1 would report: the exit code and the announced evidence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from devcapsule.container_runtime.supervisor import (
    INFRASTRUCTURE_FAILURE_EXIT_CODE,
    SupervisedChild,
    Supervisor,
    SupervisorError,
)

DRIVER = Path(__file__).parent / "resources" / "supervisor_driver.py"
REPO_ROOT = Path(__file__).resolve().parents[1]


def start_supervisor(children: list[dict[str, object]], grace_seconds: float = 5.0) -> subprocess.Popen[str]:
    spec = json.dumps({"children": children, "grace_seconds": grace_seconds})
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT), environment.get("PYTHONPATH")])
    )
    return subprocess.Popen(
        [sys.executable, str(DRIVER), spec],
        env=environment,
        stderr=subprocess.PIPE,
        text=True,
    )


def wait_for_marker(marker: Path, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not marker.exists():
        assert time.monotonic() < deadline, f"marker never appeared: {marker}"
        time.sleep(0.02)


def test_foreground_exit_code_is_the_session_exit_code() -> None:
    process = start_supervisor([{"name": "job", "command": ["sh", "-c", "exit 7"], "foreground": True}])
    assert process.wait(timeout=10) == 7


def test_foreground_death_by_signal_reports_shell_convention() -> None:
    process = start_supervisor(
        [{"name": "job", "command": ["sh", "-c", "kill -KILL $$"], "foreground": True}]
    )
    assert process.wait(timeout=10) == 137


def test_sigterm_is_the_explicit_end_and_propagates_honestly(tmp_path: Path) -> None:
    marker = tmp_path / "ready"
    process = start_supervisor(
        [
            {
                "name": "ide",
                "command": ["sh", "-c", f"touch {marker}; exec sleep 30"],
                "foreground": True,
            }
        ]
    )
    wait_for_marker(marker)
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) == 128 + signal.SIGTERM
    stderr = process.stderr.read() if process.stderr else ""
    assert "session end requested (SIGTERM)" in stderr


def test_term_ignoring_child_is_killed_after_the_grace_period(tmp_path: Path) -> None:
    marker = tmp_path / "ready"
    process = start_supervisor(
        [
            {
                "name": "stubborn",
                "command": [
                    "sh",
                    "-c",
                    f'trap "" TERM; touch {marker}; while true; do sleep 0.1; done',
                ],
                "foreground": True,
            }
        ],
        grace_seconds=0.5,
    )
    wait_for_marker(marker)
    started = time.monotonic()
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) == 128 + signal.SIGKILL
    assert time.monotonic() - started >= 0.5
    stderr = process.stderr.read() if process.stderr else ""
    assert "grace period over" in stderr


def test_non_foreground_death_fails_the_session_and_names_the_child() -> None:
    process = start_supervisor(
        [
            {"name": "xvnc", "command": ["sh", "-c", "exit 3"]},
            {"name": "ide", "command": ["sleep", "30"], "foreground": True},
        ]
    )
    assert process.wait(timeout=10) == INFRASTRUCTURE_FAILURE_EXIT_CODE
    stderr = process.stderr.read() if process.stderr else ""
    assert "'xvnc' died unexpectedly (exit code 3)" in stderr


def test_foreground_exit_terminates_remaining_children_promptly() -> None:
    process = start_supervisor(
        [
            {"name": "background", "command": ["sleep", "30"]},
            {"name": "job", "command": ["sh", "-c", "exit 0"], "foreground": True},
        ]
    )
    started = time.monotonic()
    assert process.wait(timeout=10) == 0
    assert time.monotonic() - started < 10


def test_supervisor_rejects_malformed_child_sets() -> None:
    job = SupervisedChild("job", ("true",), foreground=True)
    with pytest.raises(SupervisorError, match="at least one child"):
        Supervisor(())
    with pytest.raises(SupervisorError, match="exactly one"):
        Supervisor((SupervisedChild("a", ("true",)),))
    with pytest.raises(SupervisorError, match="exactly one"):
        Supervisor((job, SupervisedChild("b", ("true",), foreground=True)))
    with pytest.raises(SupervisorError, match="unique non-empty names"):
        Supervisor((job, SupervisedChild("job", ("true",))))
    with pytest.raises(SupervisorError, match="non-empty commands"):
        Supervisor((SupervisedChild("job", (), foreground=True),))
    with pytest.raises(SupervisorError, match="grace period"):
        Supervisor((job,), grace_seconds=0)
