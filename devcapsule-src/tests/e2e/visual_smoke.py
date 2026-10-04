"""One graphical smoke scenario, independent of the chosen AI CLI/model."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import time
from typing import Any
import uuid

from tests.e2e.ai_driver import CliDriver, Decision, DriverError, VisualDriver
from tests.e2e.ide_session import SessionFacts
from tests.e2e.browser_session import smoke_browser


def apply_action(page: Any, action: Decision) -> None:
    if action.action == "click":
        page.mouse.click(action.x, action.y)
    elif action.action == "double_click":
        page.mouse.dblclick(action.x, action.y)
    elif action.action == "type":
        page.keyboard.type(action.text, delay=12)
    elif action.action == "press":
        page.keyboard.press(action.text)
    elif action.action == "wait":
        page.wait_for_timeout(action.seconds * 1000)
    else:
        raise DriverError(f"Not a browser action: {action.action}")


def saved_marker(workspace: Path, marker: str) -> bool:
    path = workspace / "smoke.txt"
    return path.is_file() and marker in path.read_text(encoding="utf-8")


def drive_scenario(page: Any, session: SessionFacts, evidence: Path, driver: VisualDriver,
                   recognizer: VisualDriver, *, max_actions: int = 30, timeout: float = 900,
                   turn_timeout: float = 120) -> dict[str, Any]:
    """Observe, act, recognize; a positive model verdict alone never passes."""
    marker = "DEVCAPSULE_SMOKE_" + uuid.uuid4().hex[:12]
    task = (
        f"You are testing the {session.surface.name} IDE through its desktop screenshot. "
        "The browser viewport is 1600x1000. Return exactly one next action as JSON. "
        "Do not use any tools yourself: the harness applies your action through Playwright. "
        "Open the existing project and its smoke.txt file in the EDITOR, append a newline "
        f"with the exact text {marker}, save with Control+s, and visually confirm it. "
        "Do not use a terminal, command runner, shell, or script to edit the file. "
        "You may trust this test-owned project, accept the IDE's free-use terms, "
        "dismiss onboarding and decline telemetry. Use free functionality; do not start "
        "trials, subscribe or sign in. If startup shows a welcome screen, open the project "
        f"at {session.workspace}. "
        "Use click/double_click with screenshot coordinates, type with literal text, "
        "press with Playwright keys such as Control+Shift+n or Enter, or wait up to 10 seconds. "
        "Declare done only after the editor shows the saved marker; fail if blocked. "
        "Fill unused x/y/seconds with 0 and unused text with an empty string."
    )
    if os.environ.get("DEVCAPSULE_SMOKE_RELAUNCH") == "1":
        task += (" Also change the IDE's editor font size to 17 using Settings > Editor > Font, "
                 "apply it and close Settings before declaring done. This harmless IDE preference "
                 "will be checked after relaunch. Use the Settings dialog, not file edits or a terminal.")
    deadline = time.monotonic() + timeout
    history: list[dict[str, Any]] = []
    screenshots: list[Path] = []
    result: dict[str, Any] = {"marker": marker, "status": "failed", "actions": history}
    try:
        for step in range(max_actions + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise DriverError("Graphical smoke exceeded its total time limit")
            screenshot = evidence / f"frame-{step:02}.png"
            page.screenshot(path=str(screenshot))
            screenshots.append(screenshot)
            action = driver.decide(task + "\nPrior actions and observations:\n" + json.dumps(history),
                                   (screenshot,), evidence / f"action-{step:02}", min(remaining, turn_timeout))
            history.append(asdict(action))
            if action.action == "fail":
                raise DriverError(f"AI reported blocked: {action.reason}")
            if action.action == "done":
                if not saved_marker(session.workspace, marker):
                    raise DriverError("AI declared success but the IDE did not save the unique marker")
                # Review sparse frames from the same recorded browser session,
                # including the final editor state. A different provider can judge.
                frames = tuple(dict.fromkeys((screenshots[0], screenshots[len(screenshots)//2], screenshots[-1])))
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise DriverError("No time remains for visual recognition")
                verdict = recognizer.decide(
                    f"Review these chronological frames from the {session.surface.name} IDE smoke recording. "
                    f"Does the final frame show a live IDE editor with the exact marker {marker}? "
                    "Look for the editor, not a terminal, error dialog or blank desktop. "
                    "Return action done only if visibly successful, otherwise fail. "
                    "Explain the observed evidence in reason; all other fields are zero/empty. "
                    "Do not use tools.", frames, evidence / "recognition", min(remaining, turn_timeout))
                result["recognition"] = asdict(verdict)
                if verdict.action != "done":
                    raise DriverError(f"Visual recognizer did not accept the editor: {verdict.reason}")
                result.update(status="passed", marker_saved=True, frames=[p.name for p in frames])
                return result
            if step == max_actions:
                raise DriverError("AI exhausted the browser action limit")
            apply_action(page, action)
            page.wait_for_timeout(800)
        raise DriverError("AI never recognized success")
    except Exception as exc:
        result["error"] = str(exc)
        raise
    finally:
        result["marker_saved"] = saved_marker(session.workspace, marker)
        (evidence / "agent-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")



def run_visual_smoke(session: SessionFacts, evidence: Path) -> dict[str, Any]:
    # An explicitly selected agent mode fails if the browser is missing.
    from playwright.sync_api import sync_playwright  # type: ignore[import-not-found,unused-ignore]

    provider = os.environ.get("DEVCAPSULE_SMOKE_DRIVER", "codex")
    driver = CliDriver.select(provider, os.environ.get("DEVCAPSULE_SMOKE_MODEL"))
    recognizer_provider = os.environ.get("DEVCAPSULE_SMOKE_RECOGNIZER", provider)
    recognizer = CliDriver.select(recognizer_provider, os.environ.get("DEVCAPSULE_SMOKE_RECOGNIZER_MODEL")
                                 or (driver.model if recognizer_provider == provider else None))
    (evidence / "ai-selection.json").write_text(json.dumps({
        "driver": asdict(driver), "recognizer": asdict(recognizer),
    }, indent=2) + "\n", encoding="utf-8")
    with sync_playwright() as playwright, smoke_browser(playwright, session, evidence) as browser:
        context = browser.new_context(viewport={"width": 1600, "height": 1000},
                                      record_video_dir=str(evidence),
                                      record_video_size={"width": 1600, "height": 1000})
        page = context.new_page()
        video = page.video
        try:
            page.goto(session.desktop_url, wait_until="load")
            page.locator("canvas").first.wait_for(state="visible", timeout=60_000)
            page.wait_for_timeout(3000)
            result = drive_scenario(page, session, evidence, driver, recognizer,
                                    max_actions=int(os.environ.get("DEVCAPSULE_SMOKE_MAX_ACTIONS", "30")),
                                    timeout=float(os.environ.get("DEVCAPSULE_SMOKE_TIMEOUT", "900")))
            result["browser_version"] = browser.version
            result["browser_location"] = "child component" if os.environ.get("DEVCAPSULE_SMOKE_COMPONENT_BROWSER") == "1" else "parent"
            (evidence / "agent-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            return result
        finally:
            context.close()
            if video is not None:
                video.save_as(str(evidence / "agent-desktop.webm"))
                video.delete()
