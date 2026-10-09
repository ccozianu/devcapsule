"""The web console as the runtime sees it: the plan section and the child."""
from __future__ import annotations

from pathlib import Path
import re

import pytest

from devcapsule.container_runtime.console import (
    CONSOLE_CHILD, CONSOLE_PYTHON, CONSOLE_ROOT, RUNTIME_CLI, console_child,
)
from devcapsule.container_runtime.contract import ConsolePlan, RuntimePlan, RuntimePlanError
from devcapsule.container_runtime.display import NOVNC_CHILD, XVNC_CHILD
from devcapsule.container_runtime.entrypoint import run
from devcapsule.images.tooling import WEBCONSOLE_ROOT, WEBCONSOLE_VENV_PYTHON
from devcapsule.materialization import ENTRYPOINT_CONTRACT
from tests.test_contained_display import contained_document
from tests.test_runtime_entrypoint import SupervisorCapture, captured_supervisor, runtime_document  # noqa: F401

CONSOLE = {"listen_address": "0.0.0.0", "port": 6081, "token_path": "/run/devcapsule-console-token"}


def test_the_runtime_and_the_base_recipe_agree_on_the_console_location() -> None:
    assert CONSOLE_ROOT == WEBCONSOLE_ROOT
    assert CONSOLE_PYTHON == WEBCONSOLE_VENV_PYTHON
    assert RUNTIME_CLI == ENTRYPOINT_CONTRACT[0]


def test_contract_round_trips_the_console_section(tmp_path: Path) -> None:
    document = runtime_document(tmp_path)
    document["console"] = dict(CONSOLE)
    plan = RuntimePlan.from_mapping(document)
    assert plan.console == ConsolePlan("0.0.0.0", 6081, "/run/devcapsule-console-token")
    assert plan.to_mapping()["console"] == CONSOLE
    with_source = RuntimePlan.from_mapping({**document, "console": {**CONSOLE, "source_path": "/workspace/project/devcapsule-webconsole"}})
    assert with_source.console is not None and with_source.console.source_path == "/workspace/project/devcapsule-webconsole"
    assert with_source.to_mapping()["console"] == {**CONSOLE, "source_path": "/workspace/project/devcapsule-webconsole"}
    assert RuntimePlan.from_mapping(plan.to_mapping()) == plan
    assert RuntimePlan.from_mapping(runtime_document(tmp_path)).console is None
    assert plan.with_console(ConsolePlan("127.0.0.1", 40000, "/run/t")).console == ConsolePlan("127.0.0.1", 40000, "/run/t")


@pytest.mark.parametrize("console, message", [
    ("text", "console must be an object"),
    ({**CONSOLE, "extra": 1}, "console must not carry extra"),
    ({**CONSOLE, "listen_address": "not a host/"}, "console.listen_address must be a host address"),
    ({**CONSOLE, "port": 0}, "console.port must be a TCP port number"),
    ({**CONSOLE, "port": True}, "console.port must be a TCP port number"),
    ({**CONSOLE, "token_path": "relative"}, "console.token_path must be an absolute normalized container path"),
    ({**CONSOLE, "source_path": "../escape"}, "console.source_path must be an absolute normalized container path"),
    ({**CONSOLE, "source_path": 5}, "console.source_path must be a non-empty string"),
])
def test_contract_rejects_a_malformed_console(tmp_path: Path, console: object, message: str) -> None:
    with pytest.raises(RuntimePlanError, match=re.escape(message)):
        RuntimePlan.from_mapping({**runtime_document(tmp_path), "console": console})


def plan_with_console(tmp_path: Path, **console: object) -> RuntimePlan:
    return RuntimePlan.from_mapping({**runtime_document(tmp_path), "console": {**CONSOLE, **console}})


def test_console_child_runs_the_installed_console_against_the_runtime_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("devcapsule.container_runtime.console.CONSOLE_PYTHON", str(tmp_path / "python"))
    (tmp_path / "python").write_text("", encoding="utf-8")
    child = console_child(plan_with_console(tmp_path), lambda command: ("as-user", *command))
    assert child is not None
    assert child.name == CONSOLE_CHILD and child.foreground is False
    assert child.command == (
        "as-user", str(tmp_path / "python"), "-m", "devcapsule_webconsole",
        "--project", "/workspace/project", "--cli", RUNTIME_CLI,
        "--token-file", "/run/devcapsule-console-token", "--listen", "0.0.0.0", "--port", "6081",
    )
    assert child.ready is not None and child.ready() is False  # nothing listens on 6081 here
    assert child.ready_timeout_seconds == 60.0


def test_console_child_prefers_the_mounted_source_and_says_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("devcapsule.container_runtime.console.CONSOLE_PYTHON", str(tmp_path / "python"))
    (tmp_path / "python").write_text("", encoding="utf-8")
    plan = plan_with_console(tmp_path, source_path="/workspace/project/devcapsule-webconsole")
    child = console_child(plan, lambda command: command)
    assert child is not None
    assert child.command[:3] == ("env", "PYTHONPATH=/workspace/project/devcapsule-webconsole", str(tmp_path / "python"))
    assert "running the mounted checkout's source at /workspace/project/devcapsule-webconsole" in capsys.readouterr().err


def test_console_child_is_absent_without_a_section_or_on_an_older_base(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert console_child(RuntimePlan.from_mapping(runtime_document(tmp_path)), lambda command: command) is None
    assert capsys.readouterr().err == ""
    monkeypatch.setattr("devcapsule.container_runtime.console.CONSOLE_PYTHON", str(tmp_path / "absent"))
    assert console_child(plan_with_console(tmp_path), lambda command: command) is None
    assert "this base has no web console (base recipe 10 adds it" in capsys.readouterr().err


def test_entrypoint_starts_the_console_beside_the_display_and_alone_headless(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, captured_supervisor: type[SupervisorCapture]  # noqa: F811
) -> None:
    monkeypatch.setattr("devcapsule.container_runtime.display.os.geteuid", lambda: 1000)
    monkeypatch.setattr("devcapsule.container_runtime.display.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr("devcapsule.container_runtime.display.X_SOCKET_DIRECTORY", str(tmp_path / ".X11-unix"))
    monkeypatch.setattr("devcapsule.container_runtime.console.CONSOLE_PYTHON", str(tmp_path / "python"))
    (tmp_path / "python").write_text("", encoding="utf-8")
    monkeypatch.delenv("DISPLAY", raising=False)
    with_display = RuntimePlan.from_mapping({**contained_document(tmp_path), "console": dict(CONSOLE)})
    assert run(with_display) == 42
    headless = RuntimePlan.from_mapping({**runtime_document(tmp_path), "console": dict(CONSOLE)})
    assert run(headless, job=("pytest", "-q")) == 42
    passthrough = RuntimePlan.from_mapping({**runtime_document(tmp_path), "console": dict(CONSOLE)})
    assert run(passthrough) == 42

    first, second, third = captured_supervisor.instances
    names = [child.name for child in first.children]
    assert names[0] == XVNC_CHILD and names[-3:] == [NOVNC_CHILD, CONSOLE_CHILD, "jetbrains"]
    assert [child.name for child in second.children] == [CONSOLE_CHILD, "job"]
    assert [child.name for child in third.children] == [CONSOLE_CHILD, "jetbrains"]
    assert all(not child.foreground for children in (first, second, third) for child in children.children[:-1])
