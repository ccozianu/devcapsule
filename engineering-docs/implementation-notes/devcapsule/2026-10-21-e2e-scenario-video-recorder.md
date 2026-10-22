# Scenario-driven E2E IDE controller and pause-free WebM video recorder

Date: 2026-10-21. Workstream: `maintenance`. Target: 0.3.0.

The [repeatable commands](../../development/e2e-tests.md#scenario-driven-ide-video-recording---scenario-and-scenario_recorder)
live in the E2E testing guide.

## Delivered behavior

- `tests/e2e/scenario_recorder.py` adds a reusable scenario controller and
  video recorder built on top of `ide_session.py` and `browser_session.py`:
  - **Interactive agent takeover (`serve` / `ctl`):** launches a disposable
    DevCapsule for the target IDE surface (`eclipse`, `intellij`, `pycharm`,
    `codium`, `rider`), connects Playwright to the contained display (`1600×1000`),
    seeds the scenario's initial project files into `session.workspace`, and
    exposes a local HTTP controller (`controller.json`) accepting `screenshot`,
    batched `act` (`click`, `double_click`, `right_click`, `type`, `press`,
    `wait`), and `stop`.
  - **Deterministic scenario replay (`run_scenario_replay` / `replay` /
    `nox -s ide-smoke -- --scenario`):** loads a declarative scenario JSON
    from `tests/e2e/scenarios/<id>.json`, substitutes runtime variables
    (`${PROJECT_PATH}`, `${WORKSPACE}`), replays the verified action sequence,
    and writes `scenario-video.webm`, `agent-desktop-raw.webm`, `step-NNN.png`,
    `poster.png`, `action-log.json`, and `scenario-result.json`.
- `BurstFrameRecorder` eliminates dead air during interactive agent runs by
  capturing PNG frames only during active mouse/keyboard transitions and
  bounded UI animations—never while an LLM agent is thinking between turns. At
  session end, it transcodes the PNG frames to JPEG in browser `<canvas>` memory
  and pipes them over `image2pipe` (`mjpeg` $\rightarrow$ `libvpx`, 12 fps, 3 Mbps)
  to `ffmpeg`, automatically falling back to the child container's bundled
  `/opt/playwright/browsers/ffmpeg-*/ffmpeg-linux` when the parent has no host
  `ffmpeg`.

## Proof of Concept #1: Eclipse Java debugger (`eclipse-hello-time-debug`)

Scenario catalog definition:
[`devcapsule-src/tests/e2e/scenarios/eclipse-hello-time-debug.json`](../../../devcapsule-src/tests/e2e/scenarios/eclipse-hello-time-debug.json).

The scenario seeds a standard Eclipse Java project (`.project`, `.classpath`,
`src/HelloTime.java`) that queries `LocalDateTime.now()`, formats the timestamp,
and prints `Hello world, time is now ${TIME}`:

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class HelloTime {
    public static void main(String[] args) {
        LocalDateTime now = LocalDateTime.now();
        String timestamp = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        String message = "Hello world, time is now " + timestamp;
        System.out.println(message);
    }
}
```

### Recorded session artifacts

- Pause-free WebM video (`27.4 s`, `1600×1000`, `1.35 MB`, 329 active frames at 12 fps):
  [eclipse-hello-time-debug.webm](../../blog/assets/2026-10-21-eclipse-debug/eclipse-hello-time-debug.webm)
- Poster and key step screenshots (`1600×1000`):
  - [01-editor-breakpoint.png](../../blog/assets/2026-10-21-eclipse-debug/01-editor-breakpoint.png) — `HelloTime.java` imported and opened in the Eclipse Java editor with a line breakpoint toggled on line 6 (`LocalDateTime.now()`).
  - [02-paused-at-now.png](../../blog/assets/2026-10-21-eclipse-debug/02-paused-at-now.png) — Debugger launched (`F11`), switched to the Debug perspective, and suspended at line 6 (`HelloTime.main(String[]) line: 6`).
  - [03-step-over-now.png](../../blog/assets/2026-10-21-eclipse-debug/03-step-over-now.png) — First `F6` (Step Over): `now` populated in the `Variables` view (`2026-10-21T16:56:19.297475996`).
  - [04-step-over-message.png](../../blog/assets/2026-10-21-eclipse-debug/04-step-over-message.png) — Second and third `F6` (Step Over): `timestamp` (`"2026-10-21 16:56:19"`) and `message` (`"Hello world, time is now 2026-10-21 16:56:19"`) populated in `Variables`.
  - [eclipse-hello-time-debug-poster.png](../../blog/assets/2026-10-21-eclipse-debug/eclipse-hello-time-debug-poster.png) — Fourth `F6` (Step Over): `System.out.println(message)` executed and `Hello world, time is now 2026-10-21 16:56:19` printed to the Eclipse `Console` view.
