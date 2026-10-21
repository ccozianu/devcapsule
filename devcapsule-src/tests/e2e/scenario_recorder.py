"""Scenario-driven E2E IDE session controller and pause-free WebM video recorder.

Supports two execution modes over the shared ``ide_session`` and ``smoke_browser``
infrastructure:

1. **Interactive agent takeover (``serve`` / ``ctl``):** launches the target IDE
   surface in a disposable DevCapsule, connects Playwright to the desktop canvas,
   and exposes a local HTTP controller (``controller.json``) accepting
   ``screenshot``, batched ``act`` (``click``, ``double_click``, ``right_click``,
   ``type``, ``press``, ``wait``), and ``stop``. Frames are captured only during
   active UI interactions so LLM thinking time between turns never produces frozen
   dead air in the encoded ``scenario-video.webm``.
2. **Deterministic scenario replay (``run_scenario_replay`` / ``replay``):**
   seeds the scenario's project files into ``session.workspace``, executes its
   recorded ``ActionStep`` sequence, and produces ``scenario-video.webm``,
   ``agent-desktop-raw.webm``, ``step-NNN.png`` screenshots, and
   ``scenario-result.json``.
"""
from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Any
import urllib.request

from tests.e2e.ai_driver import DriverError
from tests.e2e.browser_session import smoke_browser
from tests.e2e.ide_session import (
    SURFACES,
    IdeSurface,
    SessionFacts,
    desktop_page_answers,
    ide_session,
    top_level_windows,
    wait_for_ide_window,
)

SCENARIOS_DIR = Path(__file__).resolve().parent / "scenarios"
VALID_STEP_ACTIONS = ("click", "double_click", "right_click", "type", "press", "wait")

SURFACE_SHORTCUTS: dict[str, dict[str, str]] = {
    "eclipse": {
        "open_resource": "Control+Shift+r",
        "open_type": "Control+Shift+t",
        "find_actions": "Control+3",
        "go_to_line": "Control+l",
        "toggle_breakpoint": "Control+Shift+b",
        "debug_last": "F11",
        "run_last": "Control+F11",
        "step_into": "F5",
        "step_over": "F6",
        "step_return": "F7",
        "resume": "F8",
        "save": "Control+s",
    },
    "intellij": {
        "find_action": "Control+Shift+a",
        "open_file": "Control+Shift+n",
        "go_to_line": "Control+g",
        "toggle_breakpoint": "Control+F8",
        "debug": "Shift+F9",
        "run": "Shift+F10",
        "step_into": "F7",
        "step_over": "F8",
        "resume": "F9",
        "save": "Control+s",
    },
    "pycharm": {
        "find_action": "Control+Shift+a",
        "open_file": "Control+Shift+n",
        "go_to_line": "Control+g",
        "toggle_breakpoint": "Control+F8",
        "debug": "Shift+F9",
        "run": "Shift+F10",
        "step_into": "F7",
        "step_over": "F8",
        "resume": "F9",
        "save": "Control+s",
    },
    "codium": {
        "command_palette": "Control+Shift+p",
        "quick_open": "Control+p",
        "go_to_line": "Control+g",
        "toggle_breakpoint": "F9",
        "debug": "F5",
        "step_over": "F10",
        "step_into": "F11",
        "save": "Control+s",
    },
    "rider": {
        "find_action": "Control+Shift+a",
        "open_file": "Control+Shift+n",
        "go_to_line": "Control+g",
        "toggle_breakpoint": "Control+F8",
        "debug": "Shift+F9",
        "run": "Shift+F10",
        "step_over": "F8",
        "resume": "F9",
        "save": "Control+s",
    },
}


@dataclass(frozen=True)
class ActionStep:
    """One mouse, keyboard, or bounded wait step in a scenario."""

    action: str
    x: int = 0
    y: int = 0
    text: str = ""
    ms: int = 0
    reason: str = ""

    @classmethod
    def parse(cls, value: object) -> ActionStep:
        if not isinstance(value, dict):
            raise DriverError("ActionStep must be a JSON object")
        action = value.get("action")
        if not isinstance(action, str) or action not in VALID_STEP_ACTIONS:
            raise DriverError(f"Unsupported scenario action: {action!r}")
        x = value.get("x", 0)
        y = value.get("y", 0)
        ms = value.get("ms", int(value.get("seconds", 0)) * 1000 if "seconds" in value else 0)
        text = value.get("text", "")
        reason = value.get("reason", "")
        if type(x) is not int or not (0 <= x <= 1599):
            raise DriverError(f"Invalid x coordinate: {x!r}")
        if type(y) is not int or not (0 <= y <= 999):
            raise DriverError(f"Invalid y coordinate: {y!r}")
        if type(ms) is not int or not (0 <= ms <= 30_000):
            raise DriverError(f"Invalid wait ms: {ms!r}")
        if not isinstance(text, str) or not isinstance(reason, str):
            raise DriverError("ActionStep text and reason must be strings")
        return cls(action=action, x=x, y=y, text=text, ms=ms, reason=reason)

    def substitute(self, variables: dict[str, str]) -> ActionStep:
        text = self.text
        for key, val in variables.items():
            text = text.replace(f"${{{key}}}", val)
        return ActionStep(
            action=self.action,
            x=self.x,
            y=self.y,
            text=text,
            ms=self.ms,
            reason=self.reason,
        )


@dataclass(frozen=True)
class ScenarioSpec:
    """Declarative specification of an E2E IDE scenario and its seed project."""

    id: str
    surface: str
    title: str
    description: str
    seed_files: dict[str, str]
    actions: tuple[ActionStep, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScenarioSpec:
        scenario_id = str(data.get("id") or "").strip()
        surface = str(data.get("surface") or "").strip()
        title = str(data.get("title") or "").strip()
        description = str(data.get("description") or "").strip()
        if not scenario_id or not surface or not title:
            raise DriverError("Scenario requires non-empty id, surface, and title")
        if surface not in {s.name for s in SURFACES}:
            raise DriverError(f"Scenario surface {surface!r} is not a registered IDE surface")
        raw_seeds = data.get("seed_files") or {}
        if not isinstance(raw_seeds, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in raw_seeds.items()
        ):
            raise DriverError("Scenario seed_files must be a string-to-string mapping")
        for rel in raw_seeds:
            path = Path(rel)
            if path.is_absolute() or ".." in path.parts:
                raise DriverError(f"Scenario seed_files path must be relative: {rel!r}")
        raw_actions = data.get("actions") or []
        if not isinstance(raw_actions, list):
            raise DriverError("Scenario actions must be a list")
        actions = tuple(ActionStep.parse(item) for item in raw_actions)
        return cls(
            id=scenario_id,
            surface=surface,
            title=title,
            description=description,
            seed_files=dict(raw_seeds),
            actions=actions,
        )


def list_scenarios() -> list[str]:
    """Return sorted scenario IDs available under ``tests/e2e/scenarios/``."""
    if not SCENARIOS_DIR.is_dir():
        return []
    return sorted(p.stem for p in SCENARIOS_DIR.glob("*.json"))


def load_scenario(name_or_path: str | Path) -> ScenarioSpec:
    """Load a scenario by its catalog ID or from an explicit JSON file path."""
    candidate = Path(name_or_path)
    if not candidate.is_file():
        candidate = SCENARIOS_DIR / f"{name_or_path}.json"
    if not candidate.is_file():
        raise DriverError(f"Scenario not found: {name_or_path}")
    data = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DriverError(f"Scenario file must contain a JSON object: {candidate}")
    return ScenarioSpec.from_dict(data)


def seed_scenario_workspace(workspace: Path, spec: ScenarioSpec) -> list[Path]:
    """Write ``spec.seed_files`` into ``workspace`` and return written paths."""
    written: list[Path] = []
    for rel_path, content in spec.seed_files.items():
        target = workspace / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


class BurstFrameRecorder:
    """Captures active UI transition frames to eliminate LLM-thinking dead air."""

    def __init__(self, frames_dir: Path) -> None:
        self.frames_dir = frames_dir
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0

    def record_frames(self, page: Any, count: int = 4, interval_ms: int = 120) -> None:
        for _ in range(count):
            self.frame_count += 1
            page.screenshot(path=str(self.frames_dir / f"frame-{self.frame_count:05d}.png"))
            if interval_ms > 0:
                page.wait_for_timeout(interval_ms)

    def apply_step(self, page: Any, step: ActionStep) -> None:
        kind = step.action
        if kind == "click":
            page.mouse.move(step.x, step.y, steps=6)
            self.record_frames(page, count=2, interval_ms=60)
            page.mouse.click(step.x, step.y)
            self.record_frames(page, count=5, interval_ms=120)
        elif kind == "double_click":
            page.mouse.move(step.x, step.y, steps=6)
            self.record_frames(page, count=2, interval_ms=60)
            page.mouse.dblclick(step.x, step.y)
            self.record_frames(page, count=6, interval_ms=120)
        elif kind == "right_click":
            page.mouse.move(step.x, step.y, steps=6)
            self.record_frames(page, count=2, interval_ms=60)
            page.mouse.click(step.x, step.y, button="right")
            self.record_frames(page, count=5, interval_ms=120)
        elif kind == "type":
            text = step.text
            chunk_size = max(1, len(text) // 6) if text else 1
            for i in range(0, len(text), chunk_size):
                page.keyboard.type(text[i : i + chunk_size], delay=20)
                self.record_frames(page, count=1, interval_ms=40)
            self.record_frames(page, count=4, interval_ms=100)
        elif kind == "press":
            page.keyboard.press(step.text)
            self.record_frames(page, count=6, interval_ms=120)
        elif kind == "wait":
            slices = max(1, step.ms // 150)
            recorded = min(slices, 20)
            self.record_frames(page, count=recorded, interval_ms=150)
            rem = step.ms - recorded * 150
            if rem > 0:
                page.wait_for_timeout(rem)
        else:
            raise DriverError(f"Unsupported action step: {kind}")

    def encode_webm(
        self,
        page: Any,
        output_webm: Path,
        container: str | None = None,
        fps: int = 12,
    ) -> bool:
        """Encode recorded PNG frames into a pause-free VP8 WebM via ffmpeg image2pipe."""
        frames = sorted(self.frames_dir.glob("frame-*.png"))
        if not frames:
            return False

        ffmpeg_cmd = self._resolve_ffmpeg_cmd(container)
        if ffmpeg_cmd is None:
            return False

        proc = subprocess.Popen(
            [*ffmpeg_cmd, "-y", "-f", "image2pipe", "-vcodec", "mjpeg", "-r", str(fps),
             "-i", "pipe:0", "-c:v", "libvpx", "-b:v", "3M", "-crf", "10", "-f", "webm", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.stdin is not None
        assert proc.stdout is not None
        chunks: list[bytes] = []

        def reader() -> None:
            assert proc.stdout is not None
            while True:
                data = proc.stdout.read(65536)
                if not data:
                    break
                chunks.append(data)

        read_thread = threading.Thread(target=reader, daemon=True)
        read_thread.start()

        try:
            for frame_path in frames:
                b64 = base64.b64encode(frame_path.read_bytes()).decode("ascii")
                jpeg_b64 = page.evaluate(
                    """async (b64) => {
                        const img = new Image();
                        img.src = "data:image/png;base64," + b64;
                        await img.decode();
                        const c = document.createElement("canvas");
                        c.width = img.width;
                        c.height = img.height;
                        c.getContext("2d").drawImage(img, 0, 0);
                        return c.toDataURL("image/jpeg", 0.95).split(",")[1];
                    }""",
                    b64,
                )
                proc.stdin.write(base64.b64decode(jpeg_b64))
            proc.stdin.close()
            read_thread.join(timeout=60)
            if proc.wait(timeout=60) != 0 or not chunks:
                return False
            output_webm.write_bytes(b"".join(chunks))
            return True
        except Exception:
            proc.kill()
            return False

    @staticmethod
    def _resolve_ffmpeg_cmd(container: str | None) -> list[str] | None:
        local = shutil.which("ffmpeg")
        if local:
            return [local]
        if container:
            probe = subprocess.run(
                ["docker", "exec", container, "sh", "-c",
                 "ls /opt/playwright/browsers/ffmpeg-*/ffmpeg-linux 2>/dev/null | head -n 1"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            child_ffmpeg = probe.stdout.strip()
            if probe.returncode == 0 and child_ffmpeg:
                return ["docker", "exec", "-i", container, child_ffmpeg]
        return None


def run_scenario_replay(
    session: SessionFacts,
    evidence: Path,
    spec: ScenarioSpec,
) -> dict[str, Any]:
    """Seed ``spec`` into ``session.workspace``, replay its actions, and record video."""
    from playwright.sync_api import sync_playwright  # type: ignore[import-not-found,unused-ignore]

    evidence.mkdir(parents=True, exist_ok=True)
    seed_scenario_workspace(session.workspace, spec)
    recorder = BurstFrameRecorder(evidence / "video-frames")
    variables = {
        "PROJECT_PATH": session.project_path or str(session.workspace),
        "WORKSPACE": str(session.workspace),
    }

    executed: list[dict[str, Any]] = []
    step_screenshots: list[str] = []

    with sync_playwright() as playwright, smoke_browser(playwright, session, evidence) as browser:
        viewport = {"width": 1600, "height": 1000}
        context = browser.new_context(
            viewport=viewport,
            record_video_dir=str(evidence),
            record_video_size=viewport,
        )
        page = context.new_page()
        video = page.video
        encoded = False
        try:
            page.goto(session.desktop_url, wait_until="load")
            page.locator("canvas").first.wait_for(state="visible", timeout=60_000)
            page.wait_for_timeout(3000)
            recorder.record_frames(page, count=8, interval_ms=120)

            for index, raw_step in enumerate(spec.actions, start=1):
                step = raw_step.substitute(variables)
                recorder.apply_step(page, step)
                executed.append(asdict(step))
                shot = evidence / f"step-{index:03d}.png"
                page.screenshot(path=str(shot))
                step_screenshots.append(shot.name)

            recorder.record_frames(page, count=12, interval_ms=120)
            if step_screenshots:
                shutil.copyfile(evidence / step_screenshots[-1], evidence / "poster.png")
            encoded = recorder.encode_webm(
                page,
                evidence / "scenario-video.webm",
                container=session.container,
            )
        finally:
            context.close()
            if video is not None:
                video.save_as(str(evidence / "agent-desktop-raw.webm"))
                video.delete()

    result = {
        "scenario_id": spec.id,
        "surface": spec.surface,
        "title": spec.title,
        "status": "passed",
        "steps_executed": len(executed),
        "frames_recorded": recorder.frame_count,
        "pause_free_webm": "scenario-video.webm" if encoded else None,
        "raw_webm": "agent-desktop-raw.webm",
        "screenshots": step_screenshots,
    }
    (evidence / "action-log.json").write_text(json.dumps(executed, indent=2) + "\n", encoding="utf-8")
    (evidence / "scenario-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def serve_interactive_controller(
    executable: Path,
    spec: ScenarioSpec,
    evidence: Path,
) -> None:
    """Start an interactive E2E IDE session and HTTP controller for live agent takeover."""
    from playwright.sync_api import sync_playwright  # type: ignore[import-not-found,unused-ignore]

    evidence.mkdir(parents=True, exist_ok=True)
    os.environ["DEVCAPSULE_SMOKE_COMPONENT_BROWSER"] = "1"
    surface: IdeSurface = next(s for s in SURFACES if s.name == spec.surface)
    recorder = BurstFrameRecorder(evidence / "video-frames")
    action_log: list[dict[str, Any]] = []
    step_counter = 0

    with tempfile.TemporaryDirectory() as tmp_str:
        with ide_session(executable, surface, Path(tmp_str), evidence) as session:
            seed_scenario_workspace(session.workspace, spec)
            assert desktop_page_answers(session.desktop_url) == 200
            window = wait_for_ide_window(session)
            variables = {
                "PROJECT_PATH": session.project_path or str(session.workspace),
                "WORKSPACE": str(session.workspace),
            }

            with sync_playwright() as pw, smoke_browser(pw, session, evidence) as browser:
                viewport = {"width": 1600, "height": 1000}
                context = browser.new_context(
                    viewport=viewport,
                    record_video_dir=str(evidence),
                    record_video_size=viewport,
                )
                page = context.new_page()
                video = page.video
                page.goto(session.desktop_url, wait_until="load")
                page.locator("canvas").first.wait_for(state="visible", timeout=60_000)
                page.wait_for_timeout(3000)
                recorder.record_frames(page, count=8, interval_ms=120)

                stop_event = threading.Event()
                command_queue: list[tuple[dict[str, Any], threading.Event, dict[str, Any]]] = []
                queue_lock = threading.Lock()

                class Handler(BaseHTTPRequestHandler):
                    def log_message(self, format: str, *args: Any) -> None:
                        pass

                    def do_POST(self) -> None:
                        length = int(self.headers.get("Content-Length", "0"))
                        payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
                        done = threading.Event()
                        response: dict[str, Any] = {}
                        with queue_lock:
                            command_queue.append((payload, done, response))
                        done.wait(timeout=120)
                        body = json.dumps(response).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)

                server = HTTPServer(("127.0.0.1", 0), Handler)
                port = server.server_address[1]
                threading.Thread(target=server.serve_forever, daemon=True).start()

                info = {
                    "port": port,
                    "scenario_id": spec.id,
                    "surface": spec.surface,
                    "shortcuts": SURFACE_SHORTCUTS.get(spec.surface, {}),
                    "container": session.container,
                    "workspace": str(session.workspace),
                    "project_path": session.project_path,
                    "initial_window": window,
                }
                (evidence / "controller.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
                print(f"CONTROLLER_READY port={port} project_path={session.project_path}", flush=True)

                try:
                    while not stop_event.is_set():
                        item = None
                        with queue_lock:
                            if command_queue:
                                item = command_queue.pop(0)
                        if item is None:
                            time.sleep(0.05)
                            continue
                        payload, done, response = item
                        try:
                            cmd = payload.get("cmd", "screenshot")
                            if cmd == "screenshot":
                                step_counter += 1
                                shot = evidence / f"step-{step_counter:03d}.png"
                                page.screenshot(path=str(shot))
                                response.update(
                                    ok=True,
                                    screenshot=str(shot),
                                    windows=top_level_windows(session.container),
                                    frames_recorded=recorder.frame_count,
                                )
                            elif cmd == "act":
                                raw_actions = payload.get("actions", [])
                                for raw in raw_actions:
                                    step = ActionStep.parse(raw).substitute(variables)
                                    recorder.apply_step(page, step)
                                    action_log.append(asdict(step))
                                step_counter += 1
                                shot = evidence / f"step-{step_counter:03d}.png"
                                page.screenshot(path=str(shot))
                                response.update(
                                    ok=True,
                                    screenshot=str(shot),
                                    windows=top_level_windows(session.container),
                                    frames_recorded=recorder.frame_count,
                                )
                            elif cmd == "stop":
                                recorder.record_frames(page, count=12, interval_ms=120)
                                encoded = recorder.encode_webm(
                                    page,
                                    evidence / "scenario-video.webm",
                                    container=session.container,
                                )
                                response.update(
                                    ok=True,
                                    stopping=True,
                                    frames_recorded=recorder.frame_count,
                                    pause_free_webm=encoded,
                                )
                                stop_event.set()
                            else:
                                response.update(ok=False, error=f"Unknown cmd: {cmd}")
                        except Exception as exc:
                            response.update(ok=False, error=str(exc))
                        finally:
                            done.set()
                finally:
                    server.shutdown()
                    (evidence / "action-log.json").write_text(
                        json.dumps(action_log, indent=2) + "\n", encoding="utf-8"
                    )
                    context.close()
                    if video is not None:
                        video.save_as(str(evidence / "agent-desktop-raw.webm"))
                        video.delete()


def send_controller_command(evidence: Path, payload: dict[str, Any], timeout: float = 180.0) -> dict[str, Any]:
    """Send a JSON command to a running ``serve_interactive_controller`` instance."""
    ctrl_file = evidence / "controller.json"
    deadline = time.monotonic() + timeout
    while not ctrl_file.is_file():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"controller.json did not appear in {evidence}")
        time.sleep(0.5)
    info = json.loads(ctrl_file.read_text(encoding="utf-8"))
    port = info["port"]
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        assert isinstance(result, dict)
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tests.e2e.scenario_recorder")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    sub.add_parser("list", help="List available E2E scenario definitions")

    serve_p = sub.add_parser("serve", help="Start an interactive E2E IDE session controller")
    serve_p.add_argument("--scenario", required=True, help="Scenario ID or path to JSON")
    serve_p.add_argument("--evidence", type=Path, required=True, help="Evidence output directory")
    serve_p.add_argument("--pex", type=Path, required=True, help="Path to devcapsule PEX executable")

    ctl_p = sub.add_parser("ctl", help="Send a JSON command to a running controller")
    ctl_p.add_argument("--evidence", type=Path, required=True, help="Evidence directory containing controller.json")
    ctl_p.add_argument("payload", nargs="?", default='{"cmd":"screenshot"}', help="JSON command payload")

    replay_p = sub.add_parser("replay", help="Run a scenario deterministically and record video")
    replay_p.add_argument("--scenario", required=True, help="Scenario ID or path to JSON")
    replay_p.add_argument("--evidence", type=Path, required=True, help="Evidence output directory")
    replay_p.add_argument("--pex", type=Path, required=True, help="Path to devcapsule PEX executable")

    args = parser.parse_args(argv)
    if args.subcommand == "list":
        for name in list_scenarios():
            print(name)
        return 0
    if args.subcommand == "serve":
        spec = load_scenario(args.scenario)
        serve_interactive_controller(args.pex, spec, args.evidence)
        return 0
    if args.subcommand == "ctl":
        res = send_controller_command(args.evidence, json.loads(args.payload))
        print(json.dumps(res, indent=2))
        return 0
    if args.subcommand == "replay":
        os.environ["DEVCAPSULE_SMOKE_COMPONENT_BROWSER"] = "1"
        spec = load_scenario(args.scenario)
        surface = next(s for s in SURFACES if s.name == spec.surface)
        with tempfile.TemporaryDirectory() as tmp_str:
            with ide_session(args.pex, surface, Path(tmp_str), args.evidence) as session:
                assert desktop_page_answers(session.desktop_url) == 200
                wait_for_ide_window(session)
                result = run_scenario_replay(session, args.evidence, spec)
                print(json.dumps(result, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
