"""Failure boundaries for the shared graphical scenario, without paid calls."""
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from tests.e2e.ai_driver import CliDriver, Decision, DriverError
from tests.e2e.ide_session import SURFACES, SessionFacts
from tests.e2e.visual_smoke import drive_scenario


def decision(action: str = "done") -> Decision:
    return Decision(action, 0, 0, "", 0, "test observation")


def test_provider_defaults_and_explicit_model_override() -> None:
    assert CliDriver.select("codex").model == "gpt-6-astra"
    assert CliDriver.select("claude").model == "claude-fable-5-1"
    assert CliDriver.select("claude", "custom").model == "custom"
    with pytest.raises(DriverError, match="Unsupported"):
        CliDriver.select("unknown")


@pytest.mark.parametrize("field,value", [("action", "shell"), ("x", -1), ("y", 1000), ("seconds", 11), ("x", True), ("text", None)])
def test_invalid_model_actions_are_rejected(field: str, value: Any) -> None:
    payload = asdict(decision())
    payload[field] = value
    with pytest.raises(DriverError):
        Decision.parse(payload)


class FakePage:
    def screenshot(self, *, path: str) -> None:
        Path(path).write_bytes(b"test frame")

    def wait_for_timeout(self, milliseconds: int) -> None:
        pass


class FakeDriver:
    def __init__(self, answer: Decision) -> None:
        self.answer = answer
        self.calls = 0

    def decide(self, prompt: str, images: tuple[Path, ...], evidence: Path, timeout: float) -> Decision:
        self.calls += 1
        return self.answer


def session(workspace: Path) -> SessionFacts:
    return SessionFacts(SURFACES[-1], "test-child", "http://test", workspace, workspace / "launcher.log")


def test_positive_ai_verdict_cannot_pass_without_saved_edit(tmp_path: Path) -> None:
    driver = FakeDriver(decision())
    recognizer = FakeDriver(decision())
    with pytest.raises(DriverError, match="did not save"):
        drive_scenario(FakePage(), session(tmp_path), tmp_path, driver, recognizer)
    assert recognizer.calls == 0
    assert '"status": "failed"' in (tmp_path / "agent-result.json").read_text()


def test_action_limit_stops_waiting_model(tmp_path: Path) -> None:
    driver = FakeDriver(decision("wait"))
    with pytest.raises(DriverError, match="action limit"):
        drive_scenario(FakePage(), session(tmp_path), tmp_path, driver, driver, max_actions=2)
    assert driver.calls == 3


def test_missing_cli_fails_explicitly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(DriverError, match="unavailable codex"):
        CliDriver.select("codex").decide("test", (), tmp_path / "evidence", 1)
    assert (tmp_path / "evidence/invocation.json").is_file()
