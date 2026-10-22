# Review brief for the claude + claude-fable-5-1 pair: PR236.1 on E2E scenario video recorder and Eclipse Java debugger demo

The Antigravity + Gemini 4 Argon (High) pair opened PR #236 ("Package E2E
scenario video recorder and Eclipse Java debugger demo") from
`ws-maintenance/4PR-e2e_videos-2` into `main`. No earlier review of this slice
exists. Your job is one improvement pull request (PR236.1) against
`ws-maintenance/4PR-e2e_videos-2`.

## Your checkout

You are in the git worktree at `/home/devcapsule/worktrees/maintenance-review`,
on the branch `ws-maintenance/4PR-e2e_videos-2-review`, branched from
`ws-maintenance/4PR-e2e_videos-2`. Work only there. Do not touch the main
checkout at `/workspace/301e4208ef81-ChatGPT_Codex`.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md`, `WORKFLOW-LOCAL.md`,
`engineering-docs/work-orders/2026-10-19-eclipse-java-1brc-hero-video.md`,
`engineering-docs/wip/2026-09-18-maintenance/CURRENT-STATUS.md` (the
`2026-10-21 (ws-maintenance/e2e_videos-2)` section under `## Current State`),
`devcapsule-src/tests/e2e/scenario_recorder.py`,
`devcapsule-src/tests/e2e/scenarios/eclipse-hello-time-debug.json`, and
`devcapsule-src/tests/test_scenario_recorder.py`.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against
`ccozianu/devcapsule`. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists. Run unit tests and mypy from
`devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-claude"`:

    PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-claude" .venv/bin/python -m pytest -q tests/test_scenario_recorder.py tests/test_noxfile.py tests/test_visual_smoke.py tests/test_base_contract.py
    .venv/bin/python -m mypy devcapsule tests

This PR touches:
- `devcapsule-src/tests/e2e/scenario_recorder.py` (new)
- `devcapsule-src/tests/e2e/scenarios/eclipse-hello-time-debug.json` (new)
- `devcapsule-src/tests/test_scenario_recorder.py` (new)
- `devcapsule-src/tests/e2e/test_ide_comes_alive.py` (modified)
- `devcapsule-src/noxfile.py` (modified)
- `README.md`, `index.md`, `engineering-docs/development/README.md`,
  `engineering-docs/development/e2e-tests.md`,
  `engineering-docs/development/running-e2e-scenario-recordings.md` (new),
  `engineering-docs/implementation-notes/devcapsule/2026-10-21-e2e-scenario-video-recorder.md` (new),
  `engineering-docs/blog/assets/2026-10-21-eclipse-debug/*` (new).

The gate type-checks `tests/` too. Run `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-claude" .venv/bin/python -m nox -s build`
from `devcapsule-src` before your final push and report its result.

Do not build Docker images, launch capsules, or run `nox -s e2e` or
`nox -s ide-smoke`; the implementor pair already ran the live Eclipse container
session and recorded the artifacts under
`engineering-docs/blog/assets/2026-10-21-eclipse-debug/`.

## The task

Review the diff of PR 236 against its base:

    gh pr diff 236

Read first inside the diff: the module docstring and data structures of
`devcapsule-src/tests/e2e/scenario_recorder.py`, its sibling
`devcapsule-src/tests/e2e/visual_smoke.py` and `devcapsule-src/tests/e2e/ai_driver.py`,
and the `noxfile.py` `ide_smoke` integration.

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines:
   - Does `ActionStep.parse` reject booleans, non-integers, out-of-bounds
     coordinates, negative or excessive wait durations, and missing required
     action payloads (for example `press` with an empty key or `click` when
     `seconds`/`ms` are malformed)?
   - Does `ScenarioSpec.from_dict` reject path traversal, absolute paths,
     empty or whitespace-only paths, or directory-only paths in `seed_files`,
     and does `seed_scenario_workspace` safely resolve paths inside
     `workspace`?
   - In `BurstFrameRecorder.encode_webm`, what happens if `ffmpeg` exits early
     with a broken pipe while writing frames to `proc.stdin`, or if `proc.wait`
     times out? Are subprocess pipes and threads always cleaned up deterministically
     without leaking a running `ffmpeg` child process?
   - In `serve_interactive_controller` and `send_controller_command`, what
     happens on malformed JSON in the HTTP POST body, or if `controller.json`
     is read while partially written (non-atomic write)?
   - In `noxfile.py` (`ide_smoke`), are mutually exclusive or invalid option
     combinations (for example `--scenario` together with `--agent`, or
     `--relaunch` with `--scenario`) handled cleanly?
2. Clarity of the new and modified lines. The standard is "obviously no
   deficiencies".
3. Test coverage of the new and modified lines. Add tests in
   `devcapsule-src/tests/test_scenario_recorder.py` (or `test_noxfile.py`)
   where a branch is not exercised (such as `encode_webm` failure/success paths
   with a fake subprocess or page, atomic `controller.json` / `send_controller_command`
   round-trip, and `ActionStep` / `ScenarioSpec` edge cases). Every test must
   fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: packaging the E2E scenario controller, video
recorder, Eclipse debugger scenario, and its documentation. Do not change
`ide_session.py`, `browser_session.py`, `visual_smoke.py`, or `ai_driver.py`.
Do not widen the scenario schema; if you believe it is wrong, say why in the PR
body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the
  `evidence/` directory, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files,
  `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main` or to any branch other than
  your review branch `ws-maintenance/4PR-e2e_videos-2-review`.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/4PR-e2e_videos-2-review`, each message naming the
   component and the evidence, with `--author="Costin Cozianu <ccozianu@gmail.com>"`
   and ending with your `Co-Authored-By:` line:
   `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
2. Push the branch and open one pull request with:
   `gh pr create --base ws-maintenance/4PR-e2e_videos-2 --head ws-maintenance/4PR-e2e_videos-2-review`
   Title: "Correctness, clarity and coverage review of #236 (PR236.1)".
   The body lists each finding as: what was wrong or unclear, where, what
   you changed, how the test proves it. Separate "changed" from
   "considered and left alone, because". List the proposals you did not
   implement. State the gate result with counts and what was skipped. If
   you find nothing to change, say so in the PR body and open the PR with
   the added tests only, or, if there are none, say that in your final
   report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you
   opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per
sentence, about twenty words, active voice. Every claim about behavior
must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials,
stop and say exactly what blocked you. Do not work around a blocker.
