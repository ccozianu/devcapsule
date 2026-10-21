"""Unit tests for the E2E scenario recorder, action parser, and catalog."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

import noxfile
from tests.e2e.ai_driver import DriverError
from tests.e2e.scenario_recorder import (
    ActionStep,
    BurstFrameRecorder,
    ScenarioSpec,
    list_scenarios,
    load_scenario,
    seed_scenario_workspace,
)


def test_eclipse_hello_time_debug_scenario_is_registered_and_valid(tmp_path: Path) -> None:
    assert "eclipse-hello-time-debug" in list_scenarios()
    spec = load_scenario("eclipse-hello-time-debug")
    assert spec.id == "eclipse-hello-time-debug"
    assert spec.surface == "eclipse"
    assert set(spec.seed_files) == {".project", ".classpath", "src/HelloTime.java"}
    assert "LocalDateTime.now()" in spec.seed_files["src/HelloTime.java"]
    assert any(step.action == "press" and step.text == "F11" for step in spec.actions)
    assert sum(1 for step in spec.actions if step.action == "press" and step.text == "F6") >= 3

    written = seed_scenario_workspace(tmp_path, spec)
    assert len(written) == 3
    assert (tmp_path / "src/HelloTime.java").is_file()


def test_action_step_substitution_and_validation() -> None:
    step = ActionStep.parse(
        {"action": "type", "text": "${PROJECT_PATH}/src", "reason": "import root"}
    ).substitute({"PROJECT_PATH": "/workspace/demo"})
    assert step.text == "/workspace/demo/src"

    wait_step = ActionStep.parse({"action": "wait", "seconds": 2})
    assert wait_step.ms == 2000


@pytest.mark.parametrize(
    "payload",
    [
        "not-a-dict",
        {"action": "exec"},
        {"action": "click", "x": -1, "y": 10},
        {"action": "click", "x": 1600, "y": 10},
        {"action": "click", "x": 10, "y": 1000},
        {"action": "wait", "ms": 35_000},
        {"action": "click", "x": True, "y": 10},
    ],
)
def test_invalid_action_step_is_rejected(payload: Any) -> None:
    with pytest.raises(DriverError):
        ActionStep.parse(payload)


def test_scenario_spec_rejects_traversal_and_unknown_surface() -> None:
    with pytest.raises(DriverError, match="not a registered IDE surface"):
        ScenarioSpec.from_dict({"id": "x", "surface": "vim", "title": "t"})

    with pytest.raises(DriverError, match="relative"):
        ScenarioSpec.from_dict(
            {
                "id": "x",
                "surface": "eclipse",
                "title": "t",
                "seed_files": {"../escape.txt": "bad"},
            }
        )


class FakeMouse:
    def __init__(self) -> None:
        self.events: list[tuple[str, int, int]] = []

    def move(self, x: int, y: int, steps: int = 1) -> None:
        self.events.append(("move", x, y))

    def click(self, x: int, y: int, button: str = "left") -> None:
        self.events.append((f"click:{button}", x, y))

    def dblclick(self, x: int, y: int) -> None:
        self.events.append(("dblclick", x, y))


class FakeKeyboard:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def type(self, text: str, delay: int = 0) -> None:
        self.events.append(("type", text))

    def press(self, key: str) -> None:
        self.events.append(("press", key))


class FakeCanvasPage:
    def __init__(self) -> None:
        self.mouse = FakeMouse()
        self.keyboard = FakeKeyboard()
        self.waits: list[int] = []

    def screenshot(self, *, path: str) -> None:
        Path(path).write_bytes(b"PNG")

    def wait_for_timeout(self, ms: int) -> None:
        self.waits.append(ms)


def test_burst_frame_recorder_records_frames_only_during_active_steps(tmp_path: Path) -> None:
    page = FakeCanvasPage()
    recorder = BurstFrameRecorder(tmp_path / "frames")
    recorder.apply_step(page, ActionStep(action="click", x=100, y=200))
    recorder.apply_step(page, ActionStep(action="double_click", x=150, y=250))
    recorder.apply_step(page, ActionStep(action="right_click", x=150, y=250))
    recorder.apply_step(page, ActionStep(action="type", text="HelloTime"))
    recorder.apply_step(page, ActionStep(action="press", text="F11"))
    recorder.apply_step(page, ActionStep(action="wait", ms=500))

    assert recorder.frame_count > 20
    assert len(list((tmp_path / "frames").glob("frame-*.png"))) == recorder.frame_count
    assert ("press", "F11") in page.keyboard.events
    assert ("click:left", 100, 200) in page.mouse.events
    assert ("dblclick", 150, 250) in page.mouse.events
    assert ("click:right", 150, 250) in page.mouse.events


def test_ide_smoke_forwards_scenario_flag_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock()
    session.env = {}
    session.posargs = ["--surface", "eclipse", "--scenario", "eclipse-hello-time-debug"]
    monkeypatch.delenv(noxfile.PEX_UNDER_TEST_ENV, raising=False)
    monkeypatch.setattr(noxfile, "build_test_pex", Mock())
    noxfile.ide_smoke(session)
    assert session.env["DEVCAPSULE_SMOKE_SCENARIO"] == "eclipse-hello-time-debug"
    assert session.env["DEVCAPSULE_SMOKE_DISPLAY"] == "1"
    assert "-k" in session.run.call_args.args
    assert "eclipse" in session.run.call_args.args

