# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active 2026-10-22; releasing 0.3.0: rc2 tagged, published and verified as downloaded, the shared lock regenerated on the new pins and proven by a recursive launch, the owner's dogfooding of rc2 next; rc2 was prepared with the network node and C10 merged into the release branch, each with its review-partner loop settled; the pre-candidate merge then the tag on the owner's word; rc3 forced configuration and the diagnostics snapshot, rc4 image cleanup and C20; the base is published in the promotion; C17 stays a gate in both halves

Definition read: WORKFLOW.md@5c89396f2200, WORKFLOW-LOCAL.md@31819cc43359

Integration target: `main`

Delivery method: pull request from `release-0.3.0` to `main` before each candidate tag, as the runbook rules; the owner merges; `gh` authorized to create, update and consult pull requests since 2026-10-08

Branch association: `release-0.3.0`, the release branch, the workstream's selection from the cut to the final tag; `ws-maintenance/session-logs` (PR #207) and `ws-maintenance/log-rotation` (PR #209, then #216) are merged to `main` and closed; `ws-maintenance/post-0.2.15` is merged through PR #172 and closed; release-0.2.15 is closed and retained

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

**2026-10-22, night: PR #250's review loop is settled; the slice awaits the
owner.** PR250.1, [PR #251](https://github.com/ccozianu/devcapsule/pull/251)
by the Codex and gpt-6-astra pair, is merged after one round: inspecting
the approvals could recover an interrupted activation, a write, so the
launch defers to its loader and the command refuses with the resolve
command; EOF on the keypress is a refusal; saved approvals are named when
the resolution fails after them; the history lookup is best effort on
every error; the page and the help say what a by-name approval leaves
alone; the index lists the page; regression cases for the strict
qualification, the in-capsule refusal through a real runtime context and
the replacement order. The round: the activation journal's suffix spelled
once in `storage.py` with a predicate both sites call. Full gate on the
merged branch, 1719 unit tests, the documentation contract with 47 pages.
Both briefs are under `evidence/2026-10-22-software-approvals/`. Open
thread from the review, for the consent slice of D-0011: a stored consent
holds only its value and digest, so it cannot prove yesterday's terms,
only that the lock matches today's contract. Next: the owner merges
PR #250; the schema-version slice on the owner's go; then rc3 with the
regenerated lock.

**2026-10-22, evening: software approvals at launch, PR #250, the first
slice of rc3.** The owner's finding on the host after merging the
regenerated lock: `config resolve` asked for the Antigravity and Claude Code
consents again, one per component, nothing new to decide. The diagnosis:
the acquisition consent's digest covers the component's whole lock entry,
version included, so a pin bump re-asks; D-0011 of 2026-10-01 rules that
out, once per vendor product per user, and its slice is out of 0.3.0 with
the consent work. The owner's direction instead: when the only pending
decisions are new versions of vendor software approved before, from the
same vendors under the same terms, `project run` offers the whole list
with one y/n; on no, it names `project config approve` and a page,
*software approvals*. Three design points settled with the owner: this
replaces the digest change, the strict definition of "only component
upgrades", the command and the page. On
`ws-maintenance/0.3.0-software-approvals` off the release branch:
`devcapsule/configuration/approvals.py`, the qualification and the list;
`devcapsule/commands/_software_approvals.py`, the launch-time offer, the
last launched version from the newest known-good record, approve and
resolve, the quoted command, the page's address, the keypress helper
moved beside it; the `config approve` command, mutating, refused inside a
capsule for its own project; the hook before the launch's loading, never
in `--print-command`; the page under `docs/configuration/`. Fifteen tests
through the real command line; the documentation contract passed with the
page; the full gate, 1686 unit tests.
[PR #250](https://github.com/ccozianu/devcapsule/pull/250) into
`release-0.3.0`; the review partner is the Codex and gpt-6-astra pair, by
the owner's word, running detached. Also this evening: the owner's
requirement that configuration files declare their format and the minimum
DevCapsule that reads them went to `project-management` by mail at
`ced0ed1aab9a`; the manifest rewrite by `config capabilities` is filed as a
bug; the owner's ruling that a writer emitting the `required`/`optional`
vocabulary bumps the manifest's schema version to 2 is the next slice,
beside this one, for rc3.

**2026-10-22, afternoon: rc2 tagged and verified; the shared lock
regenerated and proven.** PR #249 merged at `e998dc0`; `v0.3.0-rc2` on
`e5b5a8b`, the candidate gate `mainline` from a detached checkout, pushed
atomically; backend run 39803285881 passed; the prerelease is public with
its three assets; the download under `~/.cache/devcapsule-releases/v0.3.0-rc2`
verifies, SHA-256 `abb9a8e1…`, version `0.3.0rc2` at `e5b5a8b`. Then the
lock, on the owner's word, the way the owner suggested: `project config
capabilities --required …` ran on a fresh clone of the release branch
inside this capsule, which the capsule rule allows for any project but its
own; it wrote the lock on matrix embedded-27, Codex 0.163.0, Claude Code
2.1.302, Antigravity CLI 1.4.2, the capabilities digest unchanged;
`config check` on the clone, the running rc1 launcher's `config check` on
this checkout and the full gate, 1672 unit tests, all passed; committed at
`0c1a555`. The recursive attached launch from a fresh clone of that commit
built the formation on the new pins and ran a successor through its eleven
inspection checks, 170 s, nothing left behind. The rc1 launcher's `versions
show` lists the running capsule on the old pins and the shared lock on the
new. Findings: the command also rewrote the manifest in canonical TOML,
dropping its comments and turning `need` into `required` and `optional`;
only the lock was taken, since the vocabulary would shut the released
0.2.15 client out of the shared checkout and the comments carry the
devcapsule0 rationale; the rewrite of an unchanged manifest is a defect
against the conservative-writers ruling, for the owner's word. The gate
scratch under `/opt/devcapsule-gate` vanished again mid-session and `/opt`
is root-owned; recreated with sudo; the filed gap stands.

**2026-10-22, evening: rc2 is go; the second synchronization.** The owner
answered yes to candidate 2 and to merging `main` into the release branch
again: PR #244 merged at `a809970`, PR #247 on `main`; `main` at `e03b060`
is merged into `release-0.3.0` at `245f067`, the status file keeping both
checkouts' entries, the version files the release side, the exception now
worded for the cycle. The changelog has its candidate-2 section and the
overview its rc2 entry. Next: the pre-candidate merge from
`4PR-3-release-0.3.0`, the tag on the tip after it, the backend, the
download, the records. The design-review record of the session logs'
Python data path is filed for V1 at the owner's direction.

**2026-10-22, later: PR #244's review loop is settled; the slice awaits the
owner.** PR244.1, [PR #246](https://github.com/ccozianu/devcapsule/pull/246)
by the Antigravity and Gemini 4 Argon (High) pair, the first review by that
engine in this workstream, is merged after one round: it hardened the
attached run, the bounded daemon stop, the kill race, the notice inside
the guarded block, an unreadable log directory, and proved the mid-chunk
tee fallback; the round took three of its own proposals as defects, the
readiness watcher stopped on the first Ctrl+C, a session the launcher gave
up on left open in its manifest so the pruner's abandonment rule governs
it, and the manifest docstring. Full gate on the merged branch, 1610 unit
tests; the interrupted-launch end-to-end test passed again against that
build. Both briefs and the transcripts are under `evidence/2026-10-22-c10/`.
Open threads from the review: the supervisor blocks SIGINT during a
child's readiness wait, so an interrupt before the desktop is ready waits
for the readiness check; a second Ctrl+C within 250 ms of the first is
absorbed by Python's own wait. Neither changes this slice. Next: the owner
merges PR #244, then rc2 on the owner's word, carrying the network node
and C10; the C17 local half and forced configuration follow.

**2026-10-22, morning: C10 is PR #244; its review partner is the
Antigravity and Gemini 4 Argon (High) pair, by the owner's word.** The two
records are filed, [the terminal](../../bugs/devcapsule/2026-10-22-healthy-launch-looks-unhealthy-in-the-terminal.md)
and [Ctrl+C](../../bugs/devcapsule/2026-10-22-ctrl-c-ends-the-launcher-with-a-traceback.md),
with their rows in the release bug table. On
`ws-maintenance/0.3.0-first-session-summary` off the release branch: the
tee writes a child's output to its file only, the console the fallback
when the file fails; the launcher runs `docker run` under `Popen` and
waits through Ctrl+C, asks the daemon after sixty seconds, stops waiting
on a second Ctrl+C naming the container, records 130 and returns it; every
session ends with one result line and the path of every log file of the
session, the owner's addition; the infrastructure exit code moved into the
runtime contract; four user pages say the result in place of the
traceback. No knob keeps the old streaming, as ruled. The full gate
passed. The end-to-end proof, `tests/e2e/test_interrupted_launch.py`,
launched a fresh VSCodium project in its own process group, sent SIGINT to
the group and read the result: the lines, exit 130, the files, the
container gone, the IDE's output in its file; the transcript is under
`evidence/2026-10-22-c10/`. [PR #244](https://github.com/ccozianu/devcapsule/pull/244)
into `release-0.3.0`. The review partner runs detached in the review
worktree with the brief on standard input; Antigravity's print mode takes
the model flag before the prompt, `antigravity --model <model>
--dangerously-skip-permissions -p '<instruction>' < <brief>`, proven on
2026-10-22 and to be recorded in the developer document. The scratch
directory under `/opt/devcapsule-gate` was recreated after the restart;
the gap is with `project-management`.

**2026-10-22, night: the network-node slice is PR #240, reviewed by
PR240.1; the first loop under topic 9.11.** On
`ws-maintenance/0.3.0-network-node` off the release branch: `network`
joins the host capabilities every project has, with `bridge` as the deny
value already recorded; a unit test on a manifest without the
recommendation proves the run-once command, the bridge default, the
persistent form, the refusal and the listing; the node-registry test's
pinned set gains the node, found by the full gate's first run; two
documentation rows and the README say the node is on every project. The
full gate passed on the branch. [PR #240](https://github.com/ccozianu/devcapsule/pull/240)
into `release-0.3.0`. The review partner, the Codex and gpt-6-astra pair,
answered with [PR #242](https://github.com/ccozianu/devcapsule/pull/242),
PR240.1: the listing attributed an unanswered workstation default to the
manifest, a real defect that predates the slice; a sharper description;
lifecycle tests for the stale transitions when a recommendation appears
and disappears, the unset path, the bulk exclusion and the init
postconditions; the run-once test now proves nothing is written. One
round: the fix was keyed on the node's name where the declaration already
carries `project_recommended`; the general condition went in, correcting
one assertion for `development-sudo`. Accepted at `494e7b0` and merged
into the slice branch; the gate on the merged branch is under
*Validation*. The briefs are committed under
`evidence/2026-10-22-network-node/`, the first under the new rule. The
scratch-mount gap went to `project-management` by mail at `cf12c9eb0393`.
Learned: this Codex version resumes a session with the prompt on standard
input and the sandbox as a config override; the developer document's
recipe says otherwise and is corrected by a small pull request to `main`.
The bug record says fixed; the IDE smoke on a fresh project closes it on
rc2. Next: C10, its two records filed first; then rc2.

**2026-10-22 (`ws-maintenance/e2e_videos-2`): updated landing-page hero eyebrow
and demo video caption in `README.md`, and fixed leftover IntelliJ WebVTT
captions ([ccozianu/devcapsule-website#10](https://github.com/ccozianu/devcapsule-website/pull/10),
[PR #245](https://github.com/ccozianu/devcapsule/pull/245)).**
- Handed the two `README.md` landing-page wording choices to the owner via the
  capsule web console (`2026-10-22-hero-eyebrow-and-caption`) and recorded the
  owner's selections (`answered-at: 2026-10-22T09:35:04+00:00`):
  - `hero-eyebrow`: `ide-list-only` (`PyCharm · IntelliJ IDEA · Eclipse · Rider · VSCodium`),
    replacing `Linux x86-64 · Windows via WSL2 · Apache-2.0 · Pre-V1`.
  - `video-caption`: `polished-close` (`"See a sample of a full graphical IDE running inside DevCapsule's isolated Docker container. More scenario illustrations coming soon."`).
- After PR #236 merged (`423819f`), the owner spotted that the `<track
  kind="captions" src="/assets/session-demo.vtt">` on the landing-page video
  still showed the 4 cues from the earlier IntelliJ IDEA persistence session
  (`"Contained Linux desktop opens after container stop and relaunch; IntelliJ IDEA 2026.2.3 starts in the workspace."`).
- Updated `website/src/assets/session-demo.vtt` ([ccozianu/devcapsule-website#10](https://github.com/ccozianu/devcapsule-website/pull/10),
  merged to `website` `main` at `2bcfe6e` and integrated via [PR #245](https://github.com/ccozianu/devcapsule/pull/245)
  at `e91b965`) and saved a matching copy at
  `engineering-docs/blog/assets/2026-10-21-eclipse-debug/eclipse-hello-time-debug.vtt`
  with 5 timed cues (`00:00.000` to `00:27.420`) mapped from the 329 recorded
  frames of `eclipse-hello-time-debug.webm`.
- Verified with `npm test` (`23 passed`), `npm run check:content` (`187 pages`),
  `npm run build`, and `npm run check` (`191 HTML pages, 13876 local links/assets/anchors`).

**2026-10-22 (`ws-maintenance/e2e_videos-2` / `ws-maintenance/4PR-e2e_videos-2`):
review-partner loop on [PR #236](https://github.com/ccozianu/devcapsule/pull/236)
completed with Claude Fable 5.1; [PR #241](https://github.com/ccozianu/devcapsule/pull/241)
(PR236.1) accepted and merged without a round; PR #236 merged at `423819f`.**
- Synchronized `ws-maintenance/e2e_videos-2` with `origin/release-0.3.0` (`106f8b3`)
  to bring in the review-partner loop rules (`WORKFLOW.md` topic 9.11,
  `WORKFLOW-LOCAL.md` *Review Partners In This Checkout*, and
  `engineering-docs/development/review-partner-loop.md`), preserving `main`'s
  `0.3.1.dev0` version on the four version-bearing files.
- Committed the review brief at
  [evidence/2026-10-22-pr236-review-brief.md](evidence/2026-10-22-pr236-review-brief.md)
  (`e2f41cd`) and ran the review partner (`claude -p --model claude-fable-5-1 --dangerously-skip-permissions`)
  in an isolated worktree (`/home/devcapsule/worktrees/maintenance-review` on
  `ws-maintenance/4PR-e2e_videos-2-review`).
- Operational finding recorded in `engineering-docs/development/review-partner-loop.md`:
  in `claude -p` (single-turn print mode), a Bash tool call started with
  `run_in_background: true` is killed when the turn exits; running `nox -s build`
  synchronously in the foreground (and resuming with `claude -c -p` when needed)
  completed the full gate in 2 minutes.
- Claude Fable 5.1 opened [PR #241](https://github.com/ccozianu/devcapsule/pull/241)
  (`a33338a`, `a9eb87b`) with ten concrete improvements and 50 new unit tests
  (96 total across the 4 touched test modules, verified with a 17-point mutation
  check):
  1. `ActionStep.parse` validates `seconds` with `_require_int` (rejecting booleans),
     refuses steps setting both `ms` and `seconds`, and requires non-empty `text`
     for `press` and `type`.
  2. `ScenarioSpec.from_dict` and `seed_scenario_workspace` reject empty,
     whitespace-padded, directory-only, absolute, and `..` paths in `seed_files`,
     and verify `target.resolve()` stays inside `workspace.resolve()` before writing.
  3. `BurstFrameRecorder.encode_webm` writes `ffmpeg` stderr to
     `scenario-video.webm.ffmpeg.log` instead of an unread pipe, reaps `proc`,
     joins `reader`, and closes pipes on every exit path; `_resolve_ffmpeg_cmd`
     catches `(OSError, subprocess.SubprocessError)` and returns `None`.
  4. `start_controller_server` and `ControllerQueue` extract the loopback HTTP
     controller so it is unit-testable without a container, returning `400` on
     malformed JSON/UTF-8 or non-dict payloads without queueing and `504` on
     command timeout; `write_json_atomically` writes `controller.json` via temp
     file + `os.replace` after unlinking stale copies; `ctl` exits `2` on
     non-object JSON and `1` when `ok` is false.
  5. `noxfile.py` (`ide_smoke`) requires a single `--surface` and refuses
     `--agent` when `--scenario` is passed.
- Accepted PR #241 without a round, merged it into `ws-maintenance/4PR-e2e_videos-2`
  and `ws-maintenance/e2e_videos-2` (`e17065e`), removed the review worktree,
  and reran `nox -s build` (`1649 passed`, `mypy` clean over 216 files,
  `17 passed` packaging, `187 pages` docs-contract, `293 passed` webconsole).

**2026-10-22, later: PR #237 and PR #239 merged; `main` merged into the
release branch.** PR #238, stacked on #237's branch, merged into that
branch instead of `main` because the branch survived #237's merge while
#238 was open against it; PR #239 carried its content and the rule-8
rewrite to `main`. Then, by the owner's direction, `main` at `c779dc2` is
merged into `release-0.3.0`, a one-time synchronization recorded under
*Exceptions* in `WORKFLOW-LOCAL.md`: nothing was developed on `main`
outside the candidate process, and the cycle's workflow rules must bind
this checkout. The version-bearing files keep the release side. The
website submodule's working tree was brought to the committed pointer so
the documentation contract could run; it passed, as did the version and
workflow suites.

**2026-10-22: two workflow pull requests to `main`, at the owner's
direction, before the network-node slice.**
[PR #237](https://github.com/ccozianu/devcapsule/pull/237), from
`ws-maintenance/gh-cli-rule` off `main`: the local file's *GitHub
Integration* section replaced by the conditional rule of 2026-10-21, the
GitHub CLI used when the human provides it under `/opt/xtras`, detected by
its file, activated per shell call, its login checked once per session,
the compare link handed over when it is absent; and Release Policy rule 8,
the throwaway copy, rewritten in the controlled style with the companion
paragraph it lacked. [PR #238](https://github.com/ccozianu/devcapsule/pull/238),
stacked on it: the review-partner loop, the mechanism of the webconsole
and diagnostics slices extracted from the transcripts of 2026-10-09 to
2026-10-12 as topic 9.11 of `WORKFLOW.md` with its Changes bullet and
companion, the local section *Review Partners In This Checkout*, and the
developer document with the brief template, the assessment forms, the
recipes per engine and the record of the loops run. The definition change
is noticed to `workflow-improvements` by mail at `574b6bc68268`. Both go
to `main` directly because a workflow rule binds every workstream now;
the release branch's copies lag as they already do for the main-reopens
rule. A finding on the way: the gate's scratch under `/opt/devcapsule-gate`
is on the container's overlay and died with the restart; the owner sees a
product gap, a host-backed scratch mount in the capsule contract, to be
filed with `project-management` on the owner's word. The network-node
branch created for the rule was deleted unused; the slice starts clean.

**2026-10-21 (`ws-maintenance/e2e_videos-2`): reusable scenario-driven E2E IDE
controller and pause-free WebM recorder packaged; Proof of Concept #1 Eclipse
Java debugger video (`eclipse-hello-time-debug.webm`) recorded, saved, and
wired into `README.md` (`website:demo`).**
- Merged PR #234 (`ccozianu/devcapsule`), PR #9 (`ccozianu/devcapsule-website`),
  and PR #235 (submodule bump to `f4d35d2`), then opened continuation branch
  `ws-maintenance/e2e_videos-2`.
- Packaged `devcapsule-src/tests/e2e/scenario_recorder.py` (`ActionStep`,
  `ScenarioSpec`, `BurstFrameRecorder`, `run_scenario_replay`,
  `serve_interactive_controller`, `send_controller_command`) and wired
  `--scenario` (`DEVCAPSULE_SMOKE_SCENARIO`) into `devcapsule-src/noxfile.py`
  (`ide-smoke`) and `devcapsule-src/tests/e2e/test_ide_comes_alive.py`, with
  unit tests in `devcapsule-src/tests/test_scenario_recorder.py`.
- Packaged the Proof of Concept #1 scenario definition at
  `devcapsule-src/tests/e2e/scenarios/eclipse-hello-time-debug.json` and saved
  the recorded 27.4 s (`1600×1000`, `1.35 MB`, 12 fps pause-free) WebM video
  and key screenshots under
  `engineering-docs/blog/assets/2026-10-21-eclipse-debug/`.
- Updated `engineering-docs/development/e2e-tests.md`, added
  `engineering-docs/development/running-e2e-scenario-recordings.md` and
  `engineering-docs/implementation-notes/devcapsule/2026-10-21-e2e-scenario-video-recorder.md`
  (indexed in `index.md`), and updated `README.md` (`website:demo`) to display
  `eclipse-hello-time-debug.webm` + `eclipse-hello-time-debug-poster.png` with
  a concise visitor-facing caption and no QA/audit boilerplate.

**2026-10-21: resumed under rc1; the owner's rulings.** This capsule runs
under the downloaded rc1 (`devcapsule0 version`: `v0.3.0-rc1`, source
`7016cdd`), on the local recipe-11 base; the console answers. The shared
lock is unchanged since 2026-10-04, so the agents in this capsule are the
old pins, Codex 0.157.1, Claude Code 2.1.283, Antigravity 1.2.12; the rc1
pins have run nowhere yet, and the freshness table's provider acceptance
stays open until the owner's lock command. `main` moved past the release
branch with PR #234 and PR #235 from the second checkout, the landing-page
work and the hero-video work order on `ws-maintenance/e2e_videos`; a test
merge of the release branch into `main` is clean. That session published
this file with the rc0 state line; this publish restores the live copy.
The owner's rulings of 2026-10-21: the console-link fix is verified on
rc1 against both bases and
[the record](../../bugs/devcapsule/2026-10-18-console-link-printed-on-a-base-without-the-console.md)
is closed, the console working as 0.3.0 requires it; the base is published
later, in the promotion of the accepted candidate; the candidates are
grouped, rc2 the network node and C10, rc3 forced configuration and the
diagnostics snapshot, rc4 image cleanup and C20; C17 stays a gate in both
halves, the generic rule in `WORKFLOW.md` with `workflow-improvements` and
this project's own operating instructions in `WORKFLOW-LOCAL.md`, since a
concrete, complex case is how the abstract rule gets debugged. The local
half, build, the three test tiers separately, selective tests, the main
program and the debugger with its attachment, is a maintenance slice of
this cycle; the generic half waits in `workflow-improvements`' mailbox
since 2026-10-11, which the owner knows.

**2026-10-19 (`ws-maintenance/e2e_videos`): landing-page work order
(`2026-10-18-landing-page-why-devcapsule.md`) baseline verified; bounded
stretch-goal inspection completed.**
- **Baseline (Deliverables 1–4):** Recorded the work order at
  `engineering-docs/work-orders/2026-10-18-landing-page-why-devcapsule.md` and
  indexed it in `index.md`. Extended Contract v1 (`website/CONTRACT.md` and
  `engineering-docs/specifications/product/content-website-contract.md`) with
  `website:demo`, `website:continuity`, multi-paragraph `website:hero`, and
  self-hosted `.webm`/`.mp4` assets. Replaced the invented right-hand hero
  schematic with a framed `1152×720` (`16:10`) 26-second (`2.6×`) WebM excerpt
  (`after-restart-hero-excerpt.webm`) and poster (`after-restart-hero-poster.png`)
  from the verified 2026-10-04 IntelliJ persistence session, with WebVTT captions,
  step summary, modal `<dialog>` expansion, and direct links to both full
  recordings (`after-restart.webm`, `first-session.webm`) and the validation
  note (`2026-10-04-intellij-playwright-validation.md`). Reorganized
  `website:benefits` into three outcome-led cards, added the four-fact
  `website:continuity` handoff excerpt, and aligned `/why/`. Verified with
  `npm test` (`23 passed`), `npm run check:content`, `npm run build`,
  `npm run check`, `nox -s docs-contract`, 50 documentation unit tests,
  `scripts/browser-check.mjs` (59 viewport/palette/WCAG A/AA audits), and
  Playwright layout/playback checks at `1366×768` and `390×844`.
- **Stretch-goal inspection (15-minute budget):** Inspected the cached
  `devcapsule-local-eclipse:59ccaf413ce00f743fbc` image. It includes Eclipse
  2026-09 R (`/opt/eclipse`), OpenJDK `25.0.4+7` (`/opt/java/jdk-25.0.4+7`),
  Apache Maven `3.9.16`, JUnit 5/6, EclEmma `3.1.12` (`org.eclipse.eclemma.ui`
  + JaCoCo `0.8.15` for source coverage highlighting), and CLI `jfr`. Two
  prerequisites for the 6-step 1BRC stretch scenario are absent without
  component/harness changes: (1) no coding agent (`claude`, `codex`, `agy`) is
  installed in the cached Eclipse image and the E2E harness does not copy parent
  agent credentials into child IDE capsules, and (2) no graphical profiler UI
  (`JDK Mission Control` / `org.openjdk.jmc.*` / `VisualVM`) is bundled in
  `eclipse-ide` (`--network none` prevents runtime Marketplace installs). Per
  the work order's stop condition, stopped the stretch pass, retained the
  verified baseline recording, and recorded the follow-up stretch-goal work
  order at
  `engineering-docs/work-orders/2026-10-19-eclipse-java-1brc-hero-video.md`
  (indexed in `index.md`) with a preamble of reusable work and unblocking
  options.

**2026-10-19: the console-link fix is PR #232, along the owner's lines.**
The launcher reads the base's promise from its labels before the launch,
`web_console_availability` in the images contract: the
`devcapsule.base.webconsole` label and recipe 11 or later, the recipe
that gives the console its process monitor. `project run` reads it beside
the display transport and hands it to the launcher, which on a base
without the console plans nothing, no port, no token, no console section,
no published port, no origin, no readiness watcher, and prints one
statement in place of the link: the base, the recipe the console needs,
the one `images build` command with the launcher's own source revision,
and the guide. The guide is new, `docs/configuration/local-base.md`, the
page the C16 gate was missing: build a base, list it, select it with
`config authorize base-image`, what the selection is and is not, the way
back. [PR #232](https://github.com/ccozianu/devcapsule/pull/232) into the
release branch; the full gate passed end to end and the hosted run passed;
the bug record says fixed, verification on a downloaded candidate against
the recipe-9 and a recipe-11 base closes it. The implementor-and-reviewer
loop's review round is the owner's to run.

**2026-10-19: the console works on a recipe-11 base built from rc0.** The
owner built the base on the host with the candidate's own `images build`,
provenance `53ebc17`, selected it for the second checkout with `config
authorize base-image`, the developer-owned selection the product
provides, resolved and launched: the console answered on the printed
link. Two things follow for the cycle. The published recipe-11 base, a
gate before the final tag, is what makes this the default for everyone;
and the user documentation has no page that walks through building and
selecting a base, which belongs to the C16 documentation gate.

**2026-10-18, the owner's first finding on rc0: a console link on a base
without the console.** The launcher prints the web console link for every
run, and the runtime then says the base has no console, which is true of
the published `ubuntu-24.04@9`. Filed as a bug by the owner's word, target
0.3.0, a release fix in this cycle:
[the record](../../bugs/devcapsule/2026-10-18-console-link-printed-on-a-base-without-the-console.md).
Then, the owner reports, the launcher waits 180 s for that console and
advises opening the link; the readiness watcher shared with the display
cannot hear the runtime's notice. The launcher can read the base's
recipe label before it prints; the fix is one statement that is true,
link or substitute line, and no port, token or wait for a console that
cannot answer. It sits beside C10, the
first-session summary, and goes in the same slice or just before it. The
changelog's *Known in candidate 0* and the bug table carry it.

**2026-10-18, rc0 tagged.** PR #231 merged; the owner said go. The tag
`v0.3.0-rc0` is on `53ebc17`, the release branch's tip at the merge, whose
source is byte-identical to the fully gated PR #230 tree; the two record
commits after it carry no source. The candidate gate script, run from a
detached checkout of the tag before the push, reported `mainline` and no
unintegrated commits. Pushed atomically with the branch; backend run
39175482525 passed, the prerelease is public with its three assets, and
the download under `~/.cache/devcapsule-releases/v0.3.0-rc0` verifies:
checksum file and manifest agree on the executable, which reports
`0.3.0rc0` at `53ebc17`. Deliverable 1 of the work order is done to its
letter. Next the owner's test on the other checkout; the local Docker
proofs against this download follow that. The owner keeps this capsule, the old workhorse,
running meanwhile.

**2026-10-18, night, second: the pre-candidate merge goes through a
throwaway copy, PR #231.** PR #229 and PR #230 are merged. The owner
keeps delete-on-merge on and rules the workaround for the one ref that
must survive its merges: each merge of the release branch into `main` is
a pull request from `4PR-NNN-release-X.Y.Z`, the owner's spelling of the
same night so that no copy starts with the `release-` prefix, a copy
created at the release branch's tip for that pull request alone, deleted
on merge;
*Release Policy* 8 in `WORKFLOW-LOCAL.md` and the runbook's step 2 say
so, with the copy named a throwaway integration ref, never a release ref,
since the definition wants release refs told by name alone.
[PR #231](https://github.com/ccozianu/devcapsule/pull/231) from
`release-0.3.0-4PR-1` is the first: the pre-candidate merge, carrying
PR #230, the policy rule and this file's record; `main` keeps 0.3.1.dev0.
After it merges, every commit of the release branch is reachable from
`main`, the main disposition for rc0 is ancestry, and the tag waits for
the owner's word.

**2026-10-18, last: the red test was wrong, not the lock; PR #230.** The
owner read `test_resolution_reconstitutes_the_dogfood_environment` and
ruled it unacceptable: it asserted that the repository's committed lock
equals the matrix's newest selection, repository housekeeping rather than
a behaviour of the code, unsatisfiable from inside a capsule since only a
host launcher command writes the lock, and silent about whether an older
project still launches. The analysis went through three candidate
triples; the owner kept one. [PR #230](https://github.com/ccozianu/devcapsule/pull/230)
into the release branch deletes the test and adds
`test_repository_lock_is_launchable_by_this_launcher`: precondition the
committed lock as written by an earlier matrix; action
`parse_locked_environment`, the reader `project run` uses; postcondition
a launchable environment, the surface, the base, one validated artifact
set per materialized component. Its TODO names the wider contract as a
new work item, [the bug record](../../bugs/devcapsule/2026-10-18-no-test-proves-old-projects-launch-with-new-releases.md):
every project initialized by an earlier release keeps launching with a
new one, to be enforced over configurations captured from each released
client; no target, next planning. The hosted unit run on the pull request
passed; the full local gate passed end to end, so the lock command on the
host is no longer a gate for rc0, only the dogfooding it always was. After
the merge, the pre-candidate merge of the release branch into `main`
carries the fix there; PR #229 stays separate.

**2026-10-18, late: `main` reopens at the cut, PR #229.** After PR #228
carried 0.3.0 onto `main`, the owner weighed cherry-pick stacking and
chose, on the agent's analysis, a protocol change instead: a development
version orders before the release it names under PEP 440, so `main` on
the old development version sits behind the release branch for the whole
cycle. From now on `main` reopens with the next development version at
the cut, by pull request, and the merges of the release branch into `main`
before each candidate tag carry no version conflict after the first.
[PR #229](https://github.com/ccozianu/devcapsule/pull/229) is the rule
and its first application: `main` to 0.3.1.dev0, the manifest's
release-branch line removed from `main`, *Version Scheme* rule 4 and an
*Exceptions* entry in `WORKFLOW-LOCAL.md` against topic 11.2.7, the
runbook's steps 1 and 7 following; the definition change is mailed to
`workflow-improvements`. Its gate fails only the lock test, as `main` does
since PR #228; the documentation contract passes with `devel` at
0.3.1.dev0. The release branch keeps its own `source-version` line, since
its source declares 0.3.0. Cherry-pick stacking was set aside: it would
need every non-merge release commit cherry-picked or excepted at each
candidate, and the version commit never can be.

**2026-10-18, night: everything merged, the release branch merged into
`main`, the branch restored, the lock still the owner's.** The owner
merged PR #224 into the release branch at `6b97657` and then the release
branch into `main` by [PR #228](https://github.com/ccozianu/devcapsule/pull/228)
at `7c20292`. `main` therefore carries the release version 0.3.0, the
matrix at embedded-27 and the manifest's release-branch line; the
decision's "`main` stays at 0.2.16.dev0" gave way to the owner's merge,
as in 0.2.14, and the prepared-merge-branch thread below is closed by it.
`main` reopens with the next development version after the final tag, as
the version scheme says. GitHub deleted `release-0.3.0` on that merge: the
repository has `delete_branch_on_merge` on, which deletes every branch a
merged pull request came from, release branches included. The ref is
restored at `6b97657`, the exact tip it had, nothing lost; the setting is
the owner's to turn off, or every pre-candidate merge will delete the
release branch again. The shared lock is still at embedded-23 on both
branches, so the dogfood-reconstitution test fails on `main` and on the
release branch until the owner's host command runs; the candidate
workflow runs the unit suite, so rc0 cannot be tagged before it.

**2026-10-18, evening: the unit gate with coverage runs on pull requests
against `main` and `release-*`; PRs #225 to #227 merged.** The owner's request of the day, as part of this
release: `tests.yml` now triggers on pull requests against `main` and
against `release-*` branches, the owner's addition of the same evening,
as well as on pushes to `main`: the same job, the summary and the report
before the merge, rapid pushes to one pull request cancelling the older
run; the badge still comes from `main` alone. [PR #225](https://github.com/ccozianu/devcapsule/pull/225)
into `release-0.3.0`, with the unit-tests document updated. Left to the
owner: making the `Python 3.12` check required in the repository rules,
and a coverage threshold if one is wanted. The owner merged PR #225 with
the `main` trigger while the `release-*` addition was still in flight;
that commit follows as PR #226 from the same branch, and since GitHub
reads a pull request's workflow from its merge commit, PR #226 is the
first real run of the `release-*` trigger.

**2026-10-18, later: the agent freshness slice is PR #224, gated on one
owner step.** The upgrade attempt the runbook asks of every release is on
`ws-maintenance/0.3.0-agent-freshness`, forked from the release branch's
tip, as [PR #224](https://github.com/ccozianu/devcapsule/pull/224) into
`release-0.3.0`: the matrix at `embedded-27` with Codex 0.163.0, Claude
Code 2.1.302 and Antigravity CLI 1.4.2, every artifact checked against its
vendor's own integrity value, the golden locks regenerated, provisional
verified edges, and a two-pass startup smoke in a disposable container on
the local recipe-11 base, where the three CLIs reported their versions as
a fresh uid-1000 user, Codex listed its 175 feature flags over the seeded
`config.toml`, Claude's debug log took `mode=bypassPermissions` from the
seeded settings without a flag, and the seed files stayed byte-identical.
The evidence is in the [overview](../../releases/v0.3.0/README.md). The
branch is not gated: the test that resolves this checkout's own need
against the matrix fails until `.devcapsule/devcapsule.linux-amd64.lock`
carries the new pins, and the local rule lets only a DevCapsule command
write it, outside the capsule, where `config capabilities` and `config
check` both refuse as launcher-only. The command for the owner, with the
PEX built from the slice in the shared checkout, is in the PR and the
overview. Judgment recorded: the slice went on its own branch for the
implementor-and-reviewer loop the owner directed for the cycle, which
reads against topic 11.3's "open no new working branch under the name";
the decision record already hands the standing rule to
`workflow-improvements`.

**2026-10-18: release 0.3.0 is cut; maintenance drives it.** The owner
decided the scope, the driver and the cut in the project-management session
of the same day: [the decision](../2026-08-09-project-management/2026-10-18-decision-release-0-3-0-scope-and-cut.md)
and [the work order](../../work-orders/2026-10-18-release-0-3-0.md). The
order was taken from the mail and acknowledged, together with the two items
of 2026-10-11 that were waiting in the intake: the bootstrap retargeting is
applied, the [record](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md)
now says 0.9 with the dated ruling; the pre-candidate sequence is superseded
by the cut decision, which moves consent out of 0.3.0 and forced
configuration into the candidate cycle. The cut commit is
`3c91183ffd2130f6c7b40d2f9e3fd41588f977eb`, `main` at the merge of PR #223,
chosen because nothing of maintenance was unmerged, PR #207 and PR #209
having reached `main` on 2026-10-11 and through #216 on 2026-10-15, and
because that commit carries the decision and the order themselves.
`release-0.3.0` starts there; its first commit, `6965c5e`, sets the version
to 0.3.0 in the three authored copies, by `nox -s bump`. `main` stays at
0.2.16.dev0 until the final tag. The release overview, the bug table and
the checklist are under [releases/v0.3.0](../../releases/v0.3.0/README.md).
The agent freshness review of this date found every vendor ahead of the
pins: Codex 0.163.0 against 0.157.1, Claude Code 2.1.302 against 2.1.283,
Antigravity 1.4.2 against 1.2.12; the table is in the overview, and the
upgrade attempt is the next step, before rc0 as 0.2.15 did it, unless the
owner says rc0 ships the current pins. The gate on the branch is under
*Validation*.

Judgment where the contract is silent, recorded as topic 3 asks: the
website's content check, which the gate runs, reads the checkout as `main`
and requires the `devel` entry's source to declare a development version;
on the release branch the source declares 0.3.0, so the check failed. The
manifest on the release branch now carries `source-version: "0.3.0"` on
the `devel` entry, the form the check itself names, with a comment that the
line is release-branch metadata, not carried to `main`, where the source
declares a development version. The durable rule, a check that knows a
release branch, or a manifest form for it, is project-management's, as the
contract's owner; mailed on 2026-10-18.

**2026-10-12: the process record was mailed to the trading-research sample
project.** At the owner's request, an intake item describing the
implementor, reviewer and owner loop with pull requests, what it produced,
what we learned, and how it may inform that project's LLM debates, was
delivered to `project-management` of
`ccozianu/devcapsule-sample-trading-research` with `devcapsule workflow
mail send`, run in the submodule checkout. That repository had no
coordination branch; the tool created it, commit `9d26eed`. A sender from
another repository is outside the definition; the item says so and the
owner directed it. The submodule pointer is untouched.

**2026-10-11, after the owner's report: the stack's conflict resolved.**
PR1's branch was rebased on GitHub onto the newer `main`; its commits kept
their content and changed their hashes, so PR2, which carried the old
merge, showed a conflict in every file. One merge of the rewritten PR1
tip into PR2's branch resolved it: every conflict took PR2's version, the
tree changed only by the coverage badge, and both PRs read mergeable
again. Note for the next time: a rebase of a stacked branch's base rewrites
history the branches above it carry; the local rule, merge rather than
rebase for published branches, exists for this.

**2026-10-11, last: round three merged; the rounds on PR2 are used; the
owner's turn.** [PR #212](https://github.com/ccozianu/devcapsule/pull/212),
the Codex pair's review of the in-process rotation, was merged: compression
completes before any history is expired, a gap in the archives ages its
slot out, short raw writes are completed and accounted, a second failure
while closing cannot stop the tee from draining the pipe, and the docs
state the limits: synchronous compression on the writer, a non-atomic
sequence with a crash table, a write rather than a line as the unit. Two
proposals stay as threads below. The gate on the merged branch is recorded
under *Validation*. The owner also asked that this change go through the
same review scheme; it did.

**2026-10-11, later again: the owner clarified the rotation; every writer rotates its
own file.** The owner's mental model was the piped rotator, the writer
that rotates on write when the size is reached, and asked for "the solid
approach with no overshooting". PR2 changes accordingly: `SegmentedFile`
in `devcapsule.logs` rotates the live file the moment a write would carry
it past its segment, compresses it to `.1.gz`, shifts the older segments
and drops the one beyond the count; the tee and the Python handler both
write through it. The logrotate child, its stanza, the reopen-on-rename
logic and base recipe 12 are gone; the base stays at recipe 11 and the
behavior is the same on every base. Exact bound: the live file never
exceeds its segment, except a single write longer than the segment, which
goes into a fresh file alone. The budget knob, the segment derivation, the
manifest and the pruning are unchanged. The earlier logrotate acceptance
evidence stands as history; the rotation it proved is replaced, and the
unit suite now proves rotation with a real child writing 4000 lines
through the tee. A third Codex round reviews this change.

**2026-10-11, late: acceptance passed on a real capsule; PR #207 and PR
#209 await the owner.** From a clean clone of PR2's branch at `174480f`, a
public PEX built the recipe-12 base through `nox -s e2e -- --build-base`:
nine end-to-end tests passed, the built base carries recipe-version 12 and
answers `logrotate --version`. A fresh codium project then ran through the
real launcher on that base with a 16 MiB budget. The session directory
held every component's file, user-owned, plus `logrotate.conf` and
`session.json`; the supervisor's record shows logrotate as the first child
and the session's end; a log padded to 1.5 MiB was rotated to `.1` by the
next tick with no complaint in `devcapsule-logrotate.log`; the launcher
recorded the `docker run` and the end, and `session.json` carries
`ended-at` and the exit code. Evidence under
[evidence/2026-10-11-session-logs](evidence/2026-10-11-session-logs/).
Not shown by this run: compression, which needs a second rotation of the
same file, and a writer's reopen, since the padded panel printed nothing
afterwards; both are pinned by unit tests.

**2026-10-11, night: PR2.1 accepted; logrotate became a supervised child.**
The Codex pair's review of PR2, [PR #210](https://github.com/ccozianu/devcapsule/pull/210),
was merged: UTC arithmetic for abandonment, the budget falls back to the
default with a warning instead of refusing the launch, `nocreate` so the
writers own the replacement file, and both rotation keys required
together. Its three proposals were right and were taken as defects: the
rotation thread was created before the supervisor blocks its signals, so a
SIGTERM could end PID 1 without the orderly stop, and the supervisor's reap
loop could take logrotate's exit first. Commit `adfbff7` runs logrotate as
a supervised child, a `sh` loop that sleeps the interval and runs
logrotate, started first and stopped last, teed into
`devcapsule-logrotate.log`. The gate passed again. The second round,
[PR #211](https://github.com/ccozianu/devcapsule/pull/211), found no
runtime defect and was merged: it pins SIGTERM and SIGKILL of the loop
under the real supervisor, hostile paths through `shlex.join`, and the
`gosu` wrap, and corrects the wording on shutdown. Rounds used on PR2: two
of three. Acceptance on a real capsule follows; see *Validation*.

**2026-10-11, evening: PR1.1 accepted; slice 2 is
[PR #209](https://github.com/ccozianu/devcapsule/pull/209), stacked on PR1.**
The Codex pair's review of PR1, [PR #208](https://github.com/ccozianu/devcapsule/pull/208),
was merged into PR1's branch without a round. It found five real gaps:
the tee waited for a newline, the per-child drain could delay signal
forwarding, `DEVCAPSULE_LOG_LEVEL` never entered the container, a log
directory an external daemon cannot see produced an empty bind, and the
console's access log could persist tokens under INFO. Its two proposals are
open threads below.

Slice 2, by the owner's brief of the same day: logrotate owns the rotation
and one knob, `DEVCAPSULE_LOG_BUDGET`, bounds the checkout's logs directory
(256 MiB by default, 16 MiB floor). The entrypoint writes `logrotate.conf`
and runs logrotate as the capsule user every 30 seconds; the writers reopen
after a rotation; the segment per file is one thirty-second of the budget
within 1 to 10 MiB, four rotations, delayed compression; the launcher
records the session's end in `session.json` and prunes only ended sessions;
base recipe 12 ships logrotate and an older base keeps the 50 MiB cut. The
reviewed PR1 is merged into the slice. Gate green; see *Validation*.

Judgments for the owner's review in PR #209: the knob is an environment
variable, not a configuration node, because a node changes the manifest
vocabulary released launchers guard; the directory may exceed the budget by
the running sessions and a file its segment by thirty seconds of output,
both stated in the docs.

**2026-10-11, later: persistent session diagnostics, slice 1, is
[PR #207](https://github.com/ccozianu/devcapsule/pull/207).** The owner
merged PR #172 and said "go for it" on item 1 of the plate, with the brief:
every critical component writes a log recognizable by its file name, at the
WARNING equivalent of slf4j, with the launcher, the supervisor, the desktop
manager, the IDE and the web console as the components; where a component
has no level, redirect its stderr and stdout through a tee so the console
keeps them. Slice 1 is the Python logging framework and that wiring:

- `devcapsule.logs`: `devcapsule-<component>.log`, WARNING baseline,
  `DEVCAPSULE_LOG_LEVEL` override, lifecycle events at INFO always, a
  UTC-stamped rotating file (10 MiB, five segments), the tee with a 50 MiB
  cut, the newest 20 sessions kept per checkout.
- The runtime plan carries a `logs` section; the supervisor tees every
  child and records starts, readiness, exits and signals; Xvnc logs at
  status (`-Log *:stderr:10`); the console honours the override; the
  launcher creates `<state namespace>/logs/<session id>`, binds it at
  `/var/log/devcapsule`, writes `session.json` and its own log, and prints
  the directory; `project info` lists the row; the diagnostics page is
  written.
- Delivery follows the owner's review scheme from the web console work:
  stacked PRs, each reviewed by the Codex and gpt-6-astra pair as PRn.1
  from a `-review` branch, at most three rounds, the owner merges.

Judgments recorded for this slice, for the owner's review in the PR:

- Xvnc's baseline is its status level, not errors only, because connection
  accepted and closed are the events the original incident needs.
- The web console writes no file of its own; its stderr is teed like every
  other child, so one mechanism covers every component.
- The IDE's native log stays in its slot; the session directory holds the
  IDE's standard streams.
- The size numbers are the work order's proposal; compression and the
  aggregate budget are the next slice, with the snapshot command after.

**2026-10-11: resumed; `main` merged in; the diagnostics work order is
accepted.**

- The owner merged PR #174 into this branch on 2026-10-08. PR #172 stays
  open against `main`.
- `origin/main` was merged in at `86f78eb`: 118 commits, no conflicts.
  The definition changed since the last read: the controlled-language
  edition, decisions handed to the human through capsule state and chat,
  work orders, materialized views, diagrams first in DOT, recorded visual
  end-to-end tests. The local file adds the web console session to the
  gate and the rules for definition changes. All are read and apply from
  now.
- Three mail items were taken and decided; see the decision log. The two
  capsule-webconsole items on the `project info` checkout name are
  superseded: the owner directed that fix into capsule-webconsole, and
  `checkout_name_for` is on `main`. The project-management item assigns
  persistent session diagnostics to maintenance, target ready for 0.3.0,
  urgent. It is accepted onto the plate below. Its work order text is the
  intake item at coordination `a535ccf`; project-management owes the
  committed file at
  `engineering-docs/work-orders/2026-10-08-persistent-session-diagnostics.md`.
- The C10 first-session bug records (a ready/stopped/error summary, Ctrl+C
  ends with a result) are not filed on `main` yet. The diagnostics slice
  coordinates with that work, as the assignment asks.
- This capsule's base has no web console tools, so decisions reach the
  owner as numbered chat text under topic 8.8.
- The gate on the merged tree passed; see *Validation And External State*.

**2026-10-08: PR #172 reviewed at `4be56a7`; fixes are in
[PR #174](https://github.com/ccozianu/devcapsule/pull/174), from
`ws-maintenance/pr172-correctness` into `ws-maintenance/post-0.2.15`.** The owner requested no edits to
#172 and a stacked fix PR. Seven regressions failed before the correction;
the focused suite now passes 69 tests. The unpack cache now locks each digest
through inspection and publication, validates completion records and root
containment, and cleans/reuses one staging path after failure. The full build
gate passed: 1,177 unit cases, nine packaged integrations, mypy, source/PEX
smokes and the documentation contract. See [review and evidence](2026-10-08-pr172-review.md).

Synchronization exception: this owner-directed review branches from #172,
leaving its source branch unchanged; main synchronization belongs to the parent
integration. Main's newer configuration-writer rules were read; this review
changes no project configuration. The explicit `gh` authorization supersedes
the local UI-only delivery rule for consulting, creating and updating PRs.
The isolated review worktree preserves the original checkout's dirty website.

The three component-catalog messages were received and acknowledged. Their
configuration implementation and format rename reached main through #170.
The maintenance configuration argument is retained as a historical snapshot
at `85bec27`; updating its old links/names is queued after this review stack
integrates, together with the existing configuration follow-ups, not mixed
into these cache corrections.

**2026-10-06: named build contexts are built and measured.** Directory
inputs are named contexts read in place, one context root per launcher
cache, archives unpacked once by digest. On the real 3.69 GB PyCharm tree
a rebuild after a launcher change transfers 1.29 MB in 1.1 s instead of
3.69 GB plus a 9 s copy; first build of a tree still sends it once. Gate
green; record updated with the table and what is left for the reuse and
reaping design review. The design as built is written up for the owner in
[image layers, the local cache, and composition](../../implementation-notes/devcapsule/2026-10-06-image-layers-local-cache-and-composition.md). Next on the plate: the universal `network` node,
then that design review.

**2026-10-05, latest: option D is built and proven; the recursive attached
launch runs from a fresh workspace.** `tests/e2e/fresh_workspace.py` is the
fresh-workspace rule as code; the attached-launch test uses it and passed
in this capsule (run `8a543a0613a9c1f22d839102d592c995`, eleven inspection
checks, container removed, workspace removed). The 2026-10-04 record and
the 2026-08-15 record are status fixed, closing on a 0.3.0 candidate.
Next on the plate: named build contexts. Seven older run directories
under the persistent home's E2E workspace predate the cleanup rule; they
are the owner's to remove.

**2026-10-05, later: the in-capsule project-command fix is on the branch,
status fixed, gate green; see the two records.**
The `project` group applies a per-subcommand `CapsuleAccess` after
resolving the subcommand without side effects: the capsule's project is
selected from any directory, read-only commands answer, mutating ones
name the launcher, unknown names are unknown. Proven by unit tests and
by the source CLI from `/opt` in this capsule. Next on the plate: the
fresh-workspace recursive test (option D).

**2026-10-05: the 0.3.0 triage is complete; the plate is set.** The decisions are listed under *Resumed 2026-10-03* and
the records they changed. Two bounded things happened on the branch beyond
records: the packaging version test now runs its check from a temp
directory (component-catalog's patch, three cases green with the editable
egg-info present), and the three component-catalog items are
dispositioned. The branch is ahead of `main` by records and that one test
change; the owner pushes and opens the PR.

### The 0.3.0 maintenance plate

The [work order of 2026-10-18](../../work-orders/2026-10-18-release-0-3-0.md)
fixes the deliverables; the order of the slices within the cycle is the
driver's, the network node and C10 first being the recommendation. Done
before the cut and on `main`: the fresh-workspace recursive test
(2026-10-05), the in-capsule project-command fix (2026-10-05), named build
contexts (2026-10-06), the session logs with in-process rotation and a
budget (#207, #209, #216). Each slice below is a maintenance slice with the
implementor-and-reviewer loop as practiced on the diagnostics slices, lands
on the release branch by the owner's direction, and merges to `main` before
the next candidate tag.

1. The cut and candidate 0: cut, version and records done 2026-10-18; the
   pull request to `main`, the tag and the downloaded-asset proofs follow
   on the owner's word.
2. The agent freshness review's upgrade attempt: done as PR #224 into the
   release branch; merges once the owner regenerates the shared lock on
   the host and the gate passes, or waits for rc1 if rc0 ships the
   current pins.
3. The universal `network` authorization node: run-once and saved
   `network host` on a project without a recommendation, bridge the
   default; closes the [bug of 2026-10-05](../../bugs/devcapsule/2026-10-05-run-once-network-authorization-needs-a-recommendation.md)
   on a candidate.
4. C10: a ready, stopped or error summary instead of streamed desktop
   diagnostics, and Ctrl+C ending with a result, not a traceback; the two
   bug records filed first; closes both on a candidate. Beside it, the
   owner's rc0 finding of 2026-10-18: the console link printed on a base
   without the console, fixed as PR #232, verified on the next candidate.
5. Forced configuration: `project config resolve --force` and `project run
   --force-config`, mandatory needs split from optional ones; the
   requirement below; the capabilities page documents both and a
   fresh-workspace launch proves them.
6. The diagnostics snapshot and export command, requirement 4 of the
   [diagnostics work order](../../work-orders/2026-10-08-persistent-session-diagnostics.md);
   runs from another terminal against a broken session, export reviewed.
7. Cleanup of obsolete images and cached files, the second half of the
   installed-IDE record; design agreed with the owner first.
8. C20, release notes and documentation automation, last: the notes block
   and the manifest promotion need no operator step.
9. Added by the owner on 2026-10-18: the unit gate with coverage on pull
   requests against `main` and `release-*`; done, PRs #225, #226 and #227
   merged into the release branch, the trigger proven on #226 and #227.

Gates before the final tag: the owner's eleven user-docs decisions; the
documentation describing the accepted candidate, the page on building and
selecting a local base now written with PR #232; a published base for the
candidate; the fixed bug records verified against a downloaded candidate;
the release notes under `releases/v0.3.0/notes.md`. Out of 0.3.0, named in
the overview: consent and vendor trust, installed-IDE reuse with an empty
launcher cache, browser evidence for diagnostics, the console's deliverable
6, and ecosystem bootstrap, at 0.9. The owner is consulted before each
candidate tag, before the image-cleanup implementation, when a slice proves
larger than the cycle tolerates, and before the final tag.

### Requirement: configuration validated and changed by commands only

From the owner's correction of 2026-10-04 (component-catalog's item of
2026-10-05, R-CONFIG-001 on its branch) and the owner's addition of
2026-10-05. Schema names and command spellings are chosen in the design
step with the owner; the behaviour is fixed:

- **Read-only validation before launch.** A command that checks the
  working-tree manifest and lock, plus a proposed change, for launch,
  without writing anything. `config list` shows recorded launcher state
  and is not that check.
- **Commands for every configuration change.** This project's
  configuration is written only by DevCapsule commands; `need` adds a
  capability, and removal and mandatory/optional classification need
  commands too, so no hand edits remain.
- **`project config resolve --force`.** Shows the configuration that would
  be produced if errors were skipped: a component the local launcher does
  not know is skipped; a missing IDE surface falls back to the IDE of last
  resort, bash (vim and the SDK are inside). It highlights what is skipped
  and shows the totality that would be in place. It writes no local lock.
- **`project run --force-config`.** Launches with that error-skipping
  configuration and warns the user about every skip. Distinct from
  today's `run --force`, which only accepts a stale resolution once.
- Behind both: mandatory needs are split from optional enhancements;
  optional ones warn and degrade, only a mandatory one refuses. This holds
  for adopter projects whose contributors run a launcher that does not
  know a newer declaration.

### Earlier state

Close-out PR #149 is merged at main `6980b60`. SSH fetch verified its tree
matches the delivered 0f6578d exactly and all three version copies read
0.2.16.dev0. This checkout fast-forwarded to main before this records-only
pause. No build rerun is needed: the integrated tree is the validated tree.
The owner now wants to dogfood the actual released 0.2.15 before judging
its everyday quality. Release verification and prior acceptance stand;
ongoing dogfooding feedback is pending, with no further work requested.


**0.2.15 is published and verified.** The owner merged the promotion; SSH
fetch found PR #148 and PR #146 at main 82a1b5d, with exactly the tested
preparation tree. The final tag is at accepted RC1 source
`a15ff8b58f4af93845c17eaca22f9c9d29c8e000`. Release-0.2.15 remains at 95c7bad;
retain the branch and both candidate tags. No candidate source was changed.

[Final release](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.15)
is public, final and marked Latest. The
[backend](https://github.com/ccozianu/devcapsule/actions/runs/36353476393)
succeeded in 3m 13s. All three downloaded assets agree; final executable
SHA-256 is `0e66b9d9947aa447b53d0466d57de3290bb85ca07309df2d739baf82e4c5e113`.
Version 0.2.15, mnemonic v0.2.15, accepted source and help invocation passed.
Frozen inputs match RC1 and the inspected final executable. Embedded acceptance
matches main's record, captured at 82a1b5d. This is final delivery verification;
RC1's seven Docker proofs and owner-interactive acceptance remain the behavioral
acceptance. No extra GUI/provider or Docker campaign was performed.

A fresh maintenance branch `ws-maintenance/post-0.2.15` starts at fetched main
8243aef (only the coverage badge followed the promotion merge). The supported
bump command sets package and both definition headers to 0.2.16.dev0; the
installed workflow declaration is unchanged. This branch brings the latest
maintenance status/decision log back from the release's records-only exception,
updates only maintenance's registry row, and records final publication.
Reopening full build passed on clean commit 52bb2cf: 1089 source tests,
20 deselected, one existing xfail and one XPASS, mypy 174 files, nine packaged
checks and exact/local PEX builds/smokes. Log: `/tmp/0215-closeout-build.log`.
The subsequent checkpoint changes records only; source inputs are unchanged.
Project-management was notified by `2026-09-27-maintenance-0215-published.md`
at coordination a498133ed199. Mail take before pause returned no items.

No release branch was rebased or synchronized. The post-release branch is
based on current main; workflow prose is unchanged. The original checkout's
unrelated dirty source/website state is untouched. Both temporary RC test
containers are absent; private fixture storage remains. Mail take was empty.
The init bug remains fixed: machine init acceptance does not establish a
separate owner-performed init walk. Broader project-command guard repair and
other deferred work remain outside this completed release.

## Release 0.3.0

Cut 2026-10-18 from `main` at `3c91183ffd2130f6c7b40d2f9e3fd41588f977eb`,
the merge of PR #223, by the owner's decision of the same day; the commit
selected by the driver because every maintenance branch was merged and the
commit carries the decision and the work order. `release-0.3.0`: version
0.3.0 at `6965c5e`, the cut's records after it. The checkout sits on the
release branch from the cut to the final tag; the status file and the
registry row are edited and published from it. Running detail, the
checklist and the evidence: [releases/v0.3.0](../../releases/v0.3.0/README.md).

| Candidate | Source | Outcome |
|---|---|---|
| rc2 | `e5b5a8b` | tagged 2026-10-22 after PR #249; gate `mainline`; backend run 39803285881 passed; published, downloaded and verified; carries the network node (#240, #242) and C10 (#244, #246); the three fixed records verify on it; the owner dogfoods the terminal and Ctrl+C |
| rc1 | `7016cdd` | tagged 2026-10-19 after PR #233; gate `mainline`; backend run 39265210147 passed; published, downloaded and verified; carries the console-link fix and the local-base guide; the owner verifies the fix on both bases |
| rc0 | `53ebc17` | tagged 2026-10-18; gate `mainline`; backend run 39175482525 passed; published, downloaded and verified; the owner's downloaded copy launched the second checkout the first time; the local Docker proofs follow the owner's session |

## Release 0.2.15

Cut 2026-09-26 from the `v0.2.14` tag (`abb785d`), not from `main`, by the
owner's ruling that 0.2.15 carries the init fix and nothing else and by lines
touched: the fix is 97/15 in two source files; `main` since the tag is 496/60
across seventeen, the rest being the base-contract naming and the images
package move, assigned to 0.2.16. `release-0.2.15`: fix cherry-picked with
origin as `9a0567c` (main `74bc4aa`, PR #143 at `3acc460`), version 0.2.15 at
`c601fb8`, release overview and the candidate gate's exception record at
`4f28a12`, gate recorded at the branch tip. Full gate passed on the branch.
Overview: [releases/v0.2.15](../../releases/v0.2.15/README.md).

Judgment where the definition is silent: *Taking A Release Over* assumes a
cut from `main`, where the working branch's records are already on `main`.
Cut from a tag, the release branch carries 0.2.14-era copies of this file and
the registry, so editing or publishing them from there would regress the live
state. This release therefore keeps the workstream records on
`ws-maintenance/post-0.2.14` and publishes from it; the release branch carries
only source, version and release documents. The row names the release branch
as the rule requires. Handed to workflow-improvements as a gap to close in
the definition.

Owner subsequently agreed to RC0 after the agent slice, with xtras and
project info in the next candidate. See the current evidence and next step
above; the original fix-only gate is historical.

## Resumed 2026-10-03: 0.2.16 Bug Triage

Resumed at owner direction for candidate C9 of project-management's 0.2.16
proposal: triage the untargeted maintenance bugs with the owner so severity
and target mean something before the cut. Synchronized with `main` at
`3038c48` by merge (`b2fc861`); one registry-row conflict resolved by
keeping `main`'s project-management row and this workstream's own row.
Three `.idea/` files that `main` tracks were set aside in the session
scratchpad, not committed; the owner ruled on 2026-10-01 that `.idea/` is
ignored in this repository and 0.2.16 documents the rule.

Decided so far:

- 2026-09-26 init discards answers: closed 2026-10-04 on the owner's
  heuristic confirmation against released 0.2.15, with the RC0 and RC1
  downloaded-candidate proofs; 0.2.15's one blocking record is done.
- 2026-08-03 JetBrains Runtime alpha compositing: retired 2026-10-04, an
  observation with no defect in two months, on a display connection the
  contained desktop has since replaced.
- 2026-08-03 PyCharm native launcher: confirmed, target 0.9, with the
  triage findings in the record (no recorded reason for the script; one
  environment variable couples the runtime to it; the binary honours the
  same); a minimal change plus the IDE smoke test as the end-to-end proof.
- 2026-08-15 detached successors: fixed 2026-10-04, target 0.2.16. The
  detached lifecycle had no reason to exist; `launch-successor` is now the
  ordinary attached launch with a cidfile, and the lifecycle enum is gone.
  Unit suite (1093 passed), typecheck and the gate's test session are green.
  The new recursive end-to-end test is blocked in this capsule by a stale
  capsule-local resolution that the in-capsule guard will not let anyone
  refresh; that is the next item's territory.
- 2026-10-04 recursive successor cannot refresh its capsule-local
  resolution: decided 2026-10-05, option D, by the owner's design. The test
  stops sharing the capsule's record: clean clone of the current branch
  into a fresh host-backed workspace, dirty source refused, resolution under
  isolated XDG roots, launch from the clone, best-effort cleanup. Options A,
  B and C set aside. Same ruling, as a general rule now in the e2e test
  doc: every end-to-end test runs on a fresh workspace, never the live
  checkout. Implementation is on the 0.3.0 plate, not started.
- 2026-09-24 installed IDE not reused by Docker: decided 2026-10-05, in
  the next release, 0.3.0, both halves (reuse across formations and
  reaping), design review with the owner before code, named build contexts
  first.
- Component-catalog's intake item on the host-network run-once launch:
  acknowledged 2026-10-05 as a bug by the owner's ruling, filed as
  `2026-10-05-run-once-network-authorization-needs-a-recommendation.md`,
  minor, target 0.3.0: `network` becomes a universal authorization node
  like docker-daemon, development-sudo and host-browser. The local
  workflow text stands.
- 2026-07-16 multi-line exec rendering: minor, target 0.9, the series the
  owner expects to host V1's betas and candidates; no attention unless it
  recurs in a release campaign.
- 2026-08-03 ecosystem-aware project bootstrap: stays a bug, minor, target
  0.3, by the owner's ruling of 2026-10-05. The feature reclassification
  was rejected: onboarding a developer in minutes is an implicit promise,
  and the 2026-10-03 incident (an agent pair unable to bring `nox` into
  scope) shows how it fails. Sequenced after the larger 0.2.16 items.

The triage is complete as of 2026-10-05. The project group guard
(2026-09-26) and in-capsule configuration inspection (2026-09-24) are owner
maintenance, target 0.3.0, by the owner's decisions of 2026-10-01, restated
on 2026-10-05 without objection; they are the in-capsule project-command
fix on the plate.

Owner's version decision of 2026-10-05, recorded here until project-management
registers it and the version scheme in `WORKFLOW-LOCAL.md` is amended: the
next release, planned as 0.2.16, is **0.3.0**, a marketing decision marking
the jump forward from 0.2.15. `main` stays at 0.2.16.dev0 until the release
branch's first commit sets the version, as the local scheme says. The
maintenance-owned records that targeted 0.2.16 now target 0.3.0; the two
other-owned ones (workflow-improvements' discoverability record,
component-catalog's IntelliJ lock record) are their owners' to retarget and
are named in the mail to project-management. Beyond 0.3.x the project
jumps to 0.9, which hosts V1's betas and release candidates; bug targets
may name 0.9 on that basis.

### Resumed 2026-10-04

Synchronized with `main` at `17532fd` by merge; the five definition changes
since the last read (two files for humans, information model, validation
commands required and printed by the brief, validation vocabulary and its
checkpoint trigger, integration is a merge commit) are read and apply from
now: this branch merges `main` in, never rebases, and its deliverables
land as merge commits. The other checkout has claimed `component-catalog`
for IntelliJ; this one takes the maintenance plate.

### Paused 2026-10-04, second session, mid-triage

Main merged in at `5e9cd94` (`581ffe2`); PR #164 had already integrated
this branch's tip, so the merge brought only component-catalog's IntelliJ
and Playwright work. Component-catalog's mail on the host-network run-once
launch was taken into intake and committed. No source was changed.

### Paused 2026-10-03, mid-triage (historical)

- Last task: the 0.2.16 bug triage with the owner; one record decided
  (multi-line exec rendering, minor, 0.9). Nothing uncommitted.
- Next resumable task: continue the triage from the ecosystem-bootstrap
  record (2026-08-03). The owner's test for the remaining records: a
  record that violates no requirement and breaks no promised behavior is
  a feature, not a bug; it leaves the bug queue for the V1 scope ledger by
  mail to project-management. Ecosystem bootstrap fails that test and is
  the first to move; the information model being written in
  workflow-improvements is what makes the test a rule.
- Owner intent for the release name, recorded for project-management's
  registration: if 0.2.16 delivers its full planned scope, new IDE
  surfaces included, it is released as **0.3.0**, marking how far the
  product is beyond the first 0.2. The release branch's first commit sets
  the version under the local scheme; the owner names it then.

## Planned Next Step

1. The network-node slice, on `ws-maintenance/0.3.0-network-node` from
   the release branch, a pull request into it with the reviewer loop;
   then C10 with its two records filed first; rc2 carries both. Then rc3:
   forced configuration and the diagnostics snapshot; rc4: image cleanup
   after the owner's design review, and C20. C17's local half, this
   project's operating instructions in `WORKFLOW-LOCAL.md`, is a slice
   of the cycle too, placed by the owner. The base is published in the
   promotion of the accepted candidate and pinned there. Before the
   final tag: the five fixed records verified on a downloaded candidate,
   two of them from inside a capsule, three with Docker; the eleven
   user-docs decisions; C17's generic half; `notes.md`.
   The lock command on the host is dogfooding at the owner's convenience;
   until it runs, no capsule has exercised the rc1 agent pins.
2. Done: the release branch is merged into `main` by PR #228; ancestry
   holds. The owner may turn `delete_branch_on_merge` off.
3. On the owner's word, tag `v0.3.0-rc0` on the release branch's tip, wait
   for the backend, download and verify the three assets, run the local
   proofs against the download, and record rc0 in the overview.
4. Then the slices in the recommended order: the network node, C10 with its
   two records filed first, forced configuration, the diagnostics snapshot,
   image cleanup after the owner's design review, C20 last.

Superseded 2026-10-18 by the cut (PR #207 and PR #209 are merged; the
recipe-12 base is history since rotation moved into the writers):

1. The owner reviews and merges PR #207, then PR #209. The three review
   rounds on PR2 are used; a further change needs the owner's word.
3. Acceptance: build a recipe-12 base and run a fresh-workspace launch,
   proving the files, the rotation and the budget on a real capsule.
4. Slice 3: the live snapshot and export command; then browser evidence.
5. Then the universal network node and the installed-IDE reuse and reaping
   design review. Configuration snapshot links stay an acknowledged
   follow-up.

Done 2026-10-11: PR1.1 (#208) merged into PR1's branch.

Done 2026-10-11: PR #172 merged by the owner; the plate position was decided
by the owner's "start working on #1".

Superseded on 2026-10-11: await owner review of PR #174; after approval the
owner merges the fix into #172, then the branch synchronizes and #172
integrates. PR #174 is merged and the branch is synchronized.

Historical planned steps (superseded by the current review):

Wait for the owner's real-use feedback on released 0.2.15. Triage any reported
problem against the published executable and route it by ownership; do not
start new implementation or infer 0.2.16 scope. Release publication and main's
0.2.16.dev0 reopening are complete. No further PR or release action is required
for this slice. This records-only pause is published through coordination and
will reach main with the next substantive maintenance integration.

Previous next step, superseded: the base-contract slice is on this branch for the owner's PR. Next after the
merge: the named-build-context fix for the 4.8 GB rebuild transfer if the
owner approves it, and the 0.2.15 sequencing from project-management.

Post-release, on `ws-maintenance/post-0.2.14`: deliver the registry rows,
the version reopening and the close-out records to `main` by PR; then the
cleanup slices the owner approves from the 0.2.15 plan: the named
build-context fix for the 4.8 GB rebuild transfer, the `v0.2.12` mnemonic
(option A recommended), and repository hygiene. 0.2.15 registration and
scope are with project-management.

0.2.14 is published and verified. Remaining for this release: the owner
pastes the notes block from the release overview into the GitHub release
body; the release overview and this status are delivered to `main` through
the ordinary PR; then the branch-name migration deferred through
publication is coordinated by project-management before substantive
next-release work, and `main` reopens with the next development version
per WORKFLOW-LOCAL.md.

The owner said "release 0.2.14" on 2026-09-25. The acceptance record
`engineering-docs/releases/v0.2.14.json` is generated from the verified rc4
download (integration by ancestry, baseline `2137108`); the final gate reads
the record from `main`, so it passes only after the merge. Next: the
owner merges the release branch to `main`; then tag `v0.2.14` on
`abb785d` (`v0.2.14-rc4^{commit}`), push, verify the published final assets
and run the local proofs against them; the owner pastes the notes text
from the release overview into the GitHub release. Then the branch-name
migration deferred through publication becomes due before next-release
work.

All 0.2.14 release-table rows are decided and rc4 is accepted on both host
checkouts. Next: on the owner's word, verify ancestry of the release branch
head on `main`, tag the final `v0.2.14` on the accepted candidate's commit
`abb785d` as the operator guide prescribes, verify the published final
assets and run the local proofs against them; carry the R-COMPAT-001
exception into the release notes.

RC4 accepted 2026-09-24: the owner tested it on `devcapsule-2` and
`devcapsule` and closed the manifest rejection, the runner-gated release,
the listing trailer and the acquisition-decision records. Open and owned
here: the `/opt` discovery fallback (minor, set aside), the installed-IDE
reuse design review, and the thirteen undecided rows in the release bug
table. Next: the owner decides the remaining rows and any further
candidate; then the final `v0.2.14` tag from the accepted candidate's
commit with the release notes carrying the R-COMPAT-001 exception.

RC2's backend run (36023910604) failed at "Verify pinned base availability
and runtime sessions": `docker build` of the disposable runtime image exited
1 after 42 seconds on the hosted runner, where the rc1 run had passed the
same step in 74 seconds with identical test code; the e2e helper discarded
the build's stderr, and the step log needs administrator rights. The local
reproduction against the same digest and PEX source passed. The owner ruled
that no test on hosted infrastructure runs Docker. Filed as a blocking bug
([record](../../bugs/devcapsule/2026-09-24-release-workflow-gated-on-docker-on-hosted-runner.md))
and fixed on this branch: the release workflow runs no Docker (both
clean-machine proofs, component-cache and runtime-session steps removed);
those proofs are local acceptance steps against the downloaded assets; the
e2e helpers now fail with the command's output; the operator guide,
DEVELOPING.md and the source README describe the new split.

Done since: PR #138 merged, `v0.2.14-rc3` tagged and published, assets and
all local proofs verified (see validation below). Next: the owner tests `config list`/`resolve` on this
repository with 0.2.12 and RC3 and the `devcapsule0` exception in a real
capsule. RC2's tag stays, without assets. The RC1 configuration-inspection
bug remains open for the owner's fix-or-defer call.

Owner-directed release steering resumed 2026-09-24 from this checkout. The
owner reported `project config list` and `config resolve` failing on a fresh
DevCapsule checkout with `runtime-effect must be one of: docker.memory-limit`.
Root cause, reproduced with the published executables: commit `658749f`
declared `runtime-effect = "devcapsule.command-name"` in this repository's
own manifest while adding it to the vocabulary; v0.2.12 and rc0 reject any
effect they do not know, so every released client failed on `main` and
`release-0.2.14`; rc1 accepts it. Filed as a blocking bug
([record](../../bugs/devcapsule/2026-09-24-released-launchers-reject-repository-manifest.md)),
then fixed on this branch: the value name `runtime.devcapsule-command` is
reserved and carries the effect without the attribute, unknown effects are
reported with the running version, the manifest drops the attribute, and a
guard test pins the repository manifest to the released vocabulary. Published
0.2.12 now lists and resolves the manifest. Full gate passed.

Next: the owner opens the PR from `release-0.2.14` to `main`. After the
merge, verify the candidate gate by ancestry, tag `v0.2.14-rc2` atomically
with the branch, download and verify the assets, and validate that RC2 applies
`devcapsule0` from the reserved name inside a real capsule. Then decide the
RC1 configuration-inspection bug with the owner: fix both causes on this
branch under maintenance, or defer. The receiving workstream is paused.

RC1 owner feedback: mostly works, except configuration inspection. Both
reported failures are confirmed; the [bug](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md)
belongs to component-upgrades' runtime inspection contract, target 0.2.14.
Evidence delivered to component-upgrades by coordination mail
`2026-09-24-maintenance-rc1-runtime-configuration.md` at `dc91dbc8e484`.
Next: agree the release repair with the owner and receiving workstream.
No source fix or workstream switch was performed. Initial coordination claims
hit SSH authentication errors and a Git push hit a remote internal-server
error; mail delivery subsequently succeeded.


The runtime CLI blocker has a source fix and Docker regression evidence on
`release-0.2.14`. Normal capsules expose the shipped `devcapsule`; the owner
requested a saved configuration exception and this repository recommends
`runtime.devcapsule-command = "devcapsule0"`. That real command leaves the normal
name for development tooling; internal absolute-path calls retain the shipped
PEX. Explicit checkout values/omissions override ordinary recommendations.
Owner accepted the real recursive PyCharm/devcapsule0 session at `9cc0868`.
PR #136 integrated the release fixes; RC1 is tagged at `cec7a0c`.
Published RC1 assets are downloaded and checksum/version/source-verified.
The owner-requested local base is built and smoke-checked. Next: carry the
local PyCharm acceptance into exact-RC1 validation before closing the blocker.

The owner requested the installed-IDE reuse bug be filed first and its design
reviewed together before implementation. No release target or implementation
approach is approved. Review the linked bug when the owner resumes that topic;
do not start cache implementation or the broader composition redesign.
No live capsule or website source was patched. URL opening and non-blocking
workflow onboarding remain with their previously notified owners.

A single entry point now supports existing-project sessions:
`smoke/runner.py launch --project PATH`, followed by `resume`, `report` and
explicit actor `note` records. It verifies exact RC0 and captures process and
container facts without promoting them into a graphical PASS. The original website observation lacked candidate details; the subsequent
runner sessions establish exact RC0 startup and file/IDE resume evidence.
Owner confirmed the website VSCodium session works. Runner attempts 2 and 3
finished with exit 0, container absent and no monitor errors; owner confirmed
the S10 file/IDE resume checklist. `launch` and `resume` now accept a per-session
`--network host|bridge` override using the product authorization grammar. Next:
continue remaining campaign checks using `--network host` per local policy;
agent continuation is still untested. Owner verified host-network attempt 4.

The owner requested an engineering test specification before further campaign
work: enumerate stories, distinguish validation prerequisites from reused data,
state feature promises/preconditions/postconditions, and assign each action to
an agent or program. The [21-story specification](../../releases/v0.2.14/smoke/stories.md)
now does that. Fixed prompt answers are automated both through an actual terminal
and through unattended flags. S02/S03 and S17 (exact preservation of unrelated
coordination blobs) pass against downloaded RC0, with durable JSON evidence.
Fresh and all three public sample configurations complete unattended. Whole
GUI/upgrade/service stories are not yet implemented or passed; continue the
runner implementation from the story table, and establish desktop-control
tooling for the assigned graphical steps. Do not transfer unfinished automation
to the human. Personal provider login/MFA and release judgment remain owner acts.
The retirement is integrated;
publish RC1 when the owner is ready to test that change. RC0 still contains
the old command; do not move its tag. No base rebuild is needed: the existing
local Ubuntu recipe-9 image and published RC0 executable were rechecked on
2026-09-23, and base build inputs are unchanged. Release refs are not rebased;
main has no workflow-definition or devcapsule-src difference from this branch.

The owner requested and received a permanent
[V1-blocking legacy capability work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md).
It preserves the full inventory, existing project-run equivalents and the
undecided image-oriented/non-DevCapsule-directory alternative. Project-management
is to register the owner's V1 gate and sequence future-release decisions and
implementation; this is not a new 0.2.14 implementation commitment.
Delivered the complete work item by coordination mail
`2026-09-22-maintenance-v1-legacy-launch-capabilities.md` at `5df12452fba6`;
project-management's acknowledgement/ledger update remains pending. Links,
all 13 inventory rows and the permanent documentation index were checked.

The two owner-approved configuration closures are applied. The networking bug
was marked retired before removal as requested, and its command is now removed.
Thirteen rows remain undecided in the [release bug table](../../releases/v0.2.14/bugs.md),
including eight targeted verifications and five deferrals. Other records still
have independent scope: shared image rendering, modern PyCharm behavior,
project display policy, and resource lifecycle do not disappear with the CLI.

Owner deferred the confirmed multiline execution-rendering bug for 0.2.14
unless it recurs during the release E2E campaign. Watch for that recurrence
during acceptance and reconsider the deferral if observed. After this release,
the accepted follow-up is a clean redesign of component image composition
around documented, unit-testable contracts; the bug and release table record
the scope. The release branch remains unsynchronized as required for release refs;
the command removal, unlike the earlier records-only decisions, needs a new candidate.

Use downloaded RC0 for the release overview's end-user acceptance journeys:
fresh project, predecessor upgrade/recovery, IDE/agent work and resume,
graphical/login behavior, diagnostic command and isolated coordination scenario.
Pick further bugs from the table, fix, verify obsolete, or explicitly defer.
Capture the actual platform/surface/agent and user-visible outcome. Neither
unit coverage nor executable portability alone completes release acceptance.
New source fixes require the next immutable candidate and a main disposition.
Only after owner acceptance of an exact candidate prepare the final JSON/tag.

## Validation And External State

Gate on `ws-maintenance/e2e_videos-2` after merging review PR #241 (`e17065e`,
2026-10-22, PR #236): `nox -s build` passed end to end: version copies agree at
`0.3.1.dev0`; syntax; `mypy` clean over 216 source files; `1649 passed, 35
deselected, 1 xfailed, 1 xpassed` in the unit suite (`96 passed` across the four
touched test modules, `50` added in PR #241 with a 17-point mutation check); CLI
smoke; local PEX built and smoked (`dist/devcapsule-local.pex`); packaging
integration `17 passed`; documentation contract `187 pages including 17 aliases`
(`devel (0.3.1.dev0)` rendered); web console `mypy` clean over 8 source files
and `293 passed`. Log `/opt/devcapsule-gate/2026-10-22-pr236-merged-build.log`.
The review worktree `/home/devcapsule/worktrees/maintenance-review` and its
branch `ws-maintenance/4PR-e2e_videos-2-review` were removed after merging PR
#241.

Gate on `ws-maintenance/0.3.0-launchable-lock-test` (2026-10-18, PR #230):
`nox -s build` passed end to end: version copies agree; syntax; mypy clean
over 214 files; 1584 unit tests passed, 35 deselected, 1 xfailed, 1
xpassed; CLI smoke; test PEX built and smoked; packaging integration 17
passed; documentation contract 186 pages; web console mypy clean, 293
tests. Hosted run on the pull request: `Python 3.12` passed. Log
`/opt/devcapsule-gate/2026-10-18-locktest-build-2.log`.

Slice gate (2026-10-18, `ws-maintenance/0.3.0-agent-freshness` at
`de9537a`): `nox -s build` passes the distribution version, the syntax
checks and mypy over 214 files and stops at the unit tests: 1583 passed,
1 failed, the dogfood-reconstitution test that needs the owner's lock
step. The suite with that test deselected: 1582 passed; one host-open
broker test failed in that run only and passed alone and in the gate's
run. The local PEX of the slice, `devcapsule-src/dist/devcapsule-local.pex`,
reports 0.3.0 and is the owner's writer for the lock. Logs
`/opt/devcapsule-gate/2026-10-18-agent-freshness-*`. Smoke output under
the session scratchpad, summarized in the overview; the two containers
were removed on exit.

Gate at the cut (2026-10-18, `release-0.3.0` at the version commit
`6965c5e` with the records in the working tree): `nox -s build` passed
every step to the documentation contract: the distribution version agrees
in its three copies; mypy clean over 214 files; 1584 unit tests passed, 35
deselected, 1 xfailed, 1 xpassed; the CLI smoke; the test PEX built and
smoked; packaging integration 17 passed. The documentation contract failed
once on the `devel` entry and passed after the manifest line described
under *Current State*: 186 pages, 17 aliases, devel rendered at 0.3.0,
the three released versions reused. The web console session, which the
gate queues after the contract, ran on its own afterwards and passed:
mypy clean over 8 files, 293 tests. Logs `/opt/devcapsule-gate/2026-10-18-release-0.3.0-build-1.log`
and `-webconsole-1.log`.

Gate after round three (2026-10-11, PR #209 at `c3dd82a`): full `nox -s
build` passed, exit 0: mypy clean over 214 files; 1584 unit tests passed,
35 deselected, 1 xfailed, 1 xpassed; packaging integration 17 passed; PEX
built and smoked; documentation contract 184 pages; web console session
mypy clean, 293 tests. Log
`/opt/devcapsule-gate/2026-10-11-log-rotation-build-4.log`.

Second session (2026-10-11, PEX of `b86b899`, the recommended recipe-9
base, budget 16 MiB): the directory held every component's file present
on that base, the launcher's and the supervisor's, user-owned, and
`session.json` with the 1 MiB segment and the end record; exit 133 as
before. Evidence under `evidence/2026-10-11-session-logs/second-session/`.
The fixture project `e2e-logs-2b5c80eb` was removed after the run.

In-process rotation gate (2026-10-11, PR #209 after the owner's
clarification): full `nox -s build` passed, exit 0: mypy clean over 214
files; 1571 unit tests passed, 35 deselected, 1 xfailed, 1 xpassed;
packaging integration 17 passed; PEX built and smoked; documentation
contract 184 pages; web console session mypy clean, 293 tests. Log
`/opt/devcapsule-gate/2026-10-11-log-rotation-build-3.log`. Rotation is
proven in the unit suite with a real child writing 4000 lines through the
tee at a 100 KB segment, and the handler at a 160-byte segment.

Acceptance (2026-10-11): base `devcapsule-base-e2e:v0.2.16.dev0-local-linux-x86_64-36bef9f1e151`,
id `sha256:5034721d…`, built over host networking from the public PEX of
`174480f` (sha256 `6047ecf0…`) in the fresh workspace
`~/.local/share/devcapsule/e2e-workspaces/logs-accept`; e2e session 9
passed: built base, component cache (5), successor lifecycle, runtime
image, self-contained PEX. Proof session `20261011-085622-321e` on the
materialized codium image, exit 133 (codium's SIGTRAP on stop, as before).
The clone, its venv, the base and the codium image remain on this machine;
the fixture project `e2e-logs-1974aad7` was removed after the run.

Slice 2 gate after the review (2026-10-11, PR #209 at `adfbff7`): full
`nox -s build` passed, exit 0: mypy clean over 214 files; 1571 unit tests
passed, 35 deselected, 1 xfailed, 1 xpassed; packaging integration 17
passed; PEX built and smoked; documentation contract 184 pages; web
console session mypy clean, 293 tests. Log
`/opt/devcapsule-gate/2026-10-11-log-rotation-build-2.log`. The rotation
loop is proven under a real `sh` with a fake logrotate.

Slice 2 gate (2026-10-11, PR #209 at `4820289`): full `nox -s build`
passed, exit 0: mypy clean over 214 files; 1548 unit tests passed, 35
deselected, 1 xfailed, 1 xpassed; packaging integration 17 passed; PEX
built and smoked; documentation contract 184 pages; web console session
mypy clean, 293 tests. Log
`/opt/devcapsule-gate/2026-10-11-log-rotation-build.log`. logrotate is
absent on this capsule's recipe-11 base, so the real binary did not run;
the rotation thread, the stanza, the reopen after a rename and the reaping
race are proven with stand-ins. PR1's merged branch passed the focused
suites and mypy in the review worktree. The second review worktree is
`/home/devcapsule/worktrees/maintenance-review-pr2`.

Slice 1 gate (2026-10-11, PR #207 at `0af89a2`): full `nox -s build`
passed, exit 0, scratch on the overlay: mypy clean over 214 files; 1523
unit tests passed, 35 deselected, 2 xfailed; packaging integration 17
passed; PEX built and smoked; documentation contract 184 pages; web
console session mypy clean, 292 tests. Log
`/opt/devcapsule-gate/2026-10-11-session-logs-build.log`. The supervisor
tee is proven with real child processes in the unit suite; no capsule was
launched. The Codex pair's review worktree is
`/home/devcapsule/worktrees/maintenance-review` with its own venv.

Gate on the merged tree (2026-10-11, commit `e7e441f` plus records): full
`nox -s build` passed with exit 0, scratch on the overlay. Type check clean
over 211 source files; 1498 unit tests passed, 35 deselected, one xfail,
one xpass; packaging integration 17 passed; PEX built and smoked; the
documentation contract rendered 184 pages; the web console session passed
with mypy clean over 8 files and 290 tests. Log
`/opt/devcapsule-gate/2026-10-11-merged-main-build.log`. No Docker or IDE
acceptance was run; nothing in the merge needs one.

2026-09-27 resumption: SSH refs, waiting mail and the current main disposition
were rechecked; no candidate tag exists. Record-only acknowledgement changes
and the release-scope overview pass whitespace checks. The vendor metadata
reads are availability evidence only, not installation or model-access tests. The clean checkout has no developer virtualenv, as
already established during the project-management handoff; no new build pass
is claimed. Set up its developer environment before implementation validation.
No containers or vendor sessions were launched for workstream selection.


Base contract slice (2026-09-26, owner-directed, from the design note): new
`base_contract` module (`BaseContract`, `Provenance`, `BaseImage`), the
recipe declares and labels its contract, matrix pins carry recipe versions
5, 6, 9 and write `contract` into locks, matrix advanced to `embedded-21`,
consent bound to the image, the prompt and `config show` name the base by
contract with provenance and a recipe permalink, and `show` adds a
compatibility report from the matrix's verified edges. The configuration
core reads the contract from the lock and keeps its no-adapter rule. This
repository's lock regenerated to exactly the three expected lines. Golden
locks updated. Tests: 8 new contract tests; 3 tests rewritten from the
lock-digest rule to the image rule; full `nox -s build` passed with 1073
tests, mypy over 166 files, PEX smokes and nine packaged integrations (exit
read directly; log `/opt/devcapsule-gate/base-contract-build.log`). Prompt
and Base block rendered on a scratch copy and read by eye.

Layout (2026-09-26, owner request): the root package was crowded, so the
recipe, the contract, the build plans, the image metadata and the toolchain
pins moved into `devcapsule/images/` as `base`, `contract`, `build`,
`metadata` and `tooling`; 18 files had their imports rewritten, including
the monkeypatch targets in tests. The recipe's path is now provenance: new
images carry `devcapsule.base.recipe-source`, and permalinks for images
built before the move keep the old file. Full `nox -s build` passed again:
1073 tests, mypy over 167 files, PEX smokes and nine packaged integrations
(exit read directly; log `/opt/devcapsule-gate/images-layout-build.log`).

Host Docker cleanup (2026-09-25, owner: "run freely"): 98 DevCapsule-related
images at 288.9 GB total store. Removed the exited recursive-run containers,
then 88 tagged images, keeping the two running capsules' images, the newest
two formations per surface, the published pinned base under both tags, the
two other matrix-pinned bases and the rc2 local twin; ten remain. Store now
80.4 GB. The BuildKit cache held 645.9 GB in 2561 entries; entries unused
for more than seven days were pruned (377.2 GB reclaimed), keeping the
stages behind this week's builds so component stages stay `CACHED`. 268.7 GB
of cache from the last week remains; 21 unused local volumes (15 GB) were
not touched, their owners being unknown.

Post-release close-out (2026-09-25, owner-directed): branch names migrated
to `ws-<name>/<sub>` by creating the new refs at the old tips and pushing
them: `ws-project-management/coordination` (was `project-management/coordination`,
c5a011d), `ws-sample-projects/fastapi-webapp` (was `sample-projects/fastapi-webapp`,
6a9776c), `ws-contained-display/display-transport` (was
`contained-display/display-transport`, fa89c53),
`ws-component-catalog/antigravity-cli` (was `component-catalog/antigravity-cli`,
85a94d6); `ws-website/initial-cut` already existed and contains
`website/initial-cut` (0658207). Maintenance left the release ref for
`ws-maintenance/post-0.2.14`, cut from the release head so the two post-tag
record commits travel with it. `nox -s bump -- 0.2.15.dev0` reopened `main`'s
development version in `pyproject.toml`, `WORKFLOW.md` and the packaged
definition; `.devcapsule/devcapsule.toml`'s `[workflow] version` still reads
`0.2.14.dev0`, as it did before the release, and the bump does not touch it.
The registry rows are updated here under the owner's instruction; each
workstream's own status names its old branch until it next publishes. For a
checkout on an old name: `git branch -m OLD NEW && git branch -u origin/NEW`.
Old-name refs were deleted once their `ws-` successors contained them.
With the owner's confirmation the retired outbox delivery branches and the
superseded triage branch were deleted too, each with one never-merged record
commit, noted here for recovery: `component-catalog/outbox` 986136f,
`component-catalog/outbox-recovered-2026-09-06` 802adaf,
`sample-projects/outbox` e62d910, `ws-project-management/outbox` 09ac366,
`ws-website/outbox` 9383efe, `ws-maintenance/triage` f565689; also the
merged `contained-display/outbox`, `project-management/outbox`,
`project-management/outbox-pending-2026-08-19`, `ws-maintenance/outbox` and
`ws-workflow-improvements/nested-cwd-fix`. Remaining non-`ws-` refs are the
project's own and were not touched. The 0.2.15 plan went to project-management as
`2026-09-25-maintenance-0215-plan.md` at `354d4c7c2aff`.

Final tag (2026-09-25): PR #141 merged the release branch, fetched main
`bb3b0aa` carries `engineering-docs/releases/v0.2.14.json`. In a scratch
worktree at `abb785d`, `scripts/release-protocol.py v0.2.14` passed:
version `0.2.14`, prerelease false, candidate `v0.2.14-rc4`, integration
by ancestry, main revision `bb3b0aa`; record at
`/opt/devcapsule-gate/final-release-protocol.json`. Annotated `v0.2.14`
tagged on `abb785d`, the accepted candidate's commit, and pushed. A
detached chain waits for the final assets, verifies them, and runs the
local proofs with the release version exported. Results: `v0.2.14` public
at 01:55 UTC as a final release and GitHub Latest; checksum verified, the
executable reports `0.2.14` at `abb785d`, SHA-256
`98ff656499208bf2d4bb43adfeeafb34676b91d48adcb8ac6e8ee4e5e5d2c7bf`; the
manifest names main revision `bb3b0aa` for the acceptance record. Local
proofs: packaging integration 9 passed, clean-machine passed, component
cache 5 passed, runtime image on the pinned base passed
(`/opt/devcapsule-gate/final-proofs.log`).

Release table settled (2026-09-25): the owner deferred five rows as minor,
closed the base-image consent, CODEX_HOME, tooling PATH, embedded-browser
preview, X11 credential, formation-lifecycle and Codex installation rows,
and sent the `/opt` discovery fallback to V1 and component-layer reuse
outside the cycle. The last row, nested-directory coordination loss, closed
after the regression test was strengthened to assert blob identity per
command: coordination module 18 passed, mypy clean, full `nox -s build`
passed with 1065 tests, mypy, PEX smokes and nine packaged integrations
(exit code read directly; log `/opt/devcapsule-gate/coord-test-build.log`).

RC4 tag (2026-09-24): the owner merged PR #140; fetched main `d11848f`
contains `abb785d`, zero unintegrated commits. `scripts/release-protocol.py
v0.2.14-rc4` passed, record at `/opt/devcapsule-gate/rc4-release-protocol.json`;
annotated tag pushed atomically with the branch, peeled commit
`abb785d7ad4069606fd3ab84009ca8efeabc22b9`. A detached chain waits for the
assets, verifies them, and runs the local proofs with the release version
exported. Results, 2026-09-24: assets published under the Docker-free
workflow; checksum verified, executable reports `0.2.14rc4` at `abb785d`,
manifest records mainline integration with no unintegrated commits; PEX
SHA-256 `d5387d8a05a278bb0b8b109e9da0ea39c29d5a753e50013d9f09dc9e2a48d16a`,
files in `/opt/devcapsule-gate/0.2.14-rc4-published/`. Local proofs against
the download with `DEVCAPSULE_EXPECTED_RELEASE_VERSION=0.2.14rc4`: packaging
integration 9 passed; clean-machine passed; component-cache 5 passed;
runtime image on the pinned v0.2.12-rc5 digest 1 passed. Log
`/opt/devcapsule-gate/rc4-proofs.log`.

Provenance in the listing (2026-09-24, owner request before tagging RC4):
every configuration row carries a SOURCE column naming the document its
status and value come from (checkout, manifest, lock, resolution, managed,
environment, with a qualifier where it helps), placed before the value
column so it survives narrow terminals; `config show` adds a `Sources:`
block expanding those tokens to the manifest, lock, checkout input and
generated resolution paths, each marked as resolved or changed since the
resolution from the same freshness facts the resolution row uses, plus the
absent workstation configuration. Contract tests cover the column and the
block; the recovery, project-command and contract modules pass (167).
Rendered on a scratch copy of this repository for readability. Correction:
commit `e534d7b` was pushed with this entry claiming a passing gate, but
that gate run had failed one test, `test_config_list_shows_the_recorded_answer_and_names_a_denial`,
which parsed listing columns by position and met the new SOURCE column;
the agent read the background wrapper's exit code instead of the log. The
test now reads the status by position and the value as the last token and
checks the source. Full `nox -s build` then passed with its own exit code
read directly: 1065 tests, 20 deselected, one xfail, one quarantined XPASS,
mypy, PEX smokes and nine packaged integrations; log
`/opt/devcapsule-gate/sources-build-2.log`.

`config list`/`config show` split (2026-09-24): implemented on the release
branch at the owner's direction after the rc3 findings. `list` prints the
checkout identity and the table only; `show` adds the review, rendered from
the generated resolution's real state; newly required acquisition decisions
say they are new in 0.2.14. Contract tests 55 passed, including the new
list/show test across fresh, stale and decisions-required states; the
upgrade-recovery, project-command, release-compatibility, version-set and
configuration modules passed (423) with the recovery test reading remedies
from `show`; mypy clean on the touched modules. Full `nox -s build` passed:
1065 tests, 20 deselected, one xfail, one quarantined XPASS, mypy, PEX smokes
and nine packaged integrations; log `/opt/devcapsule-gate/list-show-build.log`.

RC3 local proofs (2026-09-24), against the verified download
`/opt/devcapsule-gate/rc3-published/devcapsule.pex` (SHA-256
`9a82ae7f91662f448ad180854e2cd43b14b6deca54c598d30440dd4a87ae4d43`), with
`DEVCAPSULE_PEX_UNDER_TEST`, `DEVCAPSULE_EXPECTED_BUILD_MNEMONIC=v0.2.14-rc3`
and `DEVCAPSULE_EXPECTED_RELEASE_VERSION=0.2.14rc3` exported, pytest scratch
on the overlay: packaging integration tests 9 passed; clean-machine proof
(`nox -s pex_clean_machine`, `docker run` without Python or network) passed;
component-cache reuse and launcher delivery 5 passed in 91 s; runtime image
on the manifest's single pinned base, the v0.2.12-rc5 digest, 1 passed in
28 s on a warm builder cache. Log `/opt/devcapsule-gate/rc3-local-proofs.log`;
its first packaging and clean-machine attempts failed only because the
release-version variable was not exported, and passed on rerun with it.
RC2 assets verified the same way: SHA-256
`eddf2cde00e07c8d7874c229283ff1a20f409400b5b7bbdcc9b5cc54dca8d3b1`,
version `0.2.14rc2`, source `a779295`, mainline integration.

RC3 tag (2026-09-24): the owner merged PR #138 (fetched main `7c0b5a2`
contains `997cd67`, zero unintegrated commits) and reported that a rerun of
rc2's failed run succeeded, which confirms the runner failure as flakiness.
`scripts/release-protocol.py v0.2.14-rc3` passed, record at
`/opt/devcapsule-gate/rc3-release-protocol.json`; annotated tag pushed
atomically with the branch, peeled commit `997cd67445b00c78da38f1a77c7f0622eaf5a0b3`.
A watcher downloads and verifies the rc2 and rc3 assets; the three local
Docker proofs against the rc3 download follow.

Docker-free release workflow (2026-09-24): workflow YAML parses; the two
edited e2e modules collect (six e2e tests, deselected as before) and pass
mypy; full `nox -s build` passed: 1064 tests, 20 deselected, one xfail, one
quarantined XPASS, mypy, PEX smokes and nine packaged integrations; log
`/opt/devcapsule-gate/no-docker-workflow-build.log`. Local
reproduction of rc2's failed step, `tests/e2e/test_runtime_image.py` with
`DEVCAPSULE_E2E_BASE_IMAGE` set to the v0.2.12-rc5 digest and the PEX built
from `8d005b3`: one passed in 608 seconds; log
`/opt/devcapsule-gate/rc2-runtime-image-repro.log`. Step timings from the
public jobs API: rc1 runtime-session step 74 s success; rc2 42 s failure;
rc2's component-cache Docker step 71 s success, so Docker itself worked on
that runner.

RC2 tag (2026-09-24): the owner merged the release PR; fetched main
`9e2396d` contains `8d005b3` and `a779295`, zero unintegrated commits.
`scripts/release-protocol.py v0.2.14-rc2` passed; record at
`/opt/devcapsule-gate/rc2-release-protocol.json`. Annotated tag pushed
atomically with the branch; remote tag object `4a02aa31d817`, peeled commit
`a779295d7343158d846df89d2d5da184548bfd1d`. Asset publication is the
workflow's; a watcher downloads and verifies the public assets when they
appear. No matrix or lock change: the default base remains the v0.2.12-rc5
digest pin, which carries no runtime (D-0009) and whose recipe is unchanged.

Local rc2 base (2026-09-24): built `devcapsule-base:0.2.14-rc2-local`, image
`sha256:64c8db54eac0bfbefa019c20777bc486abcad4bc5b0ff420d229f79a5f50718a`,
recipe `ubuntu-24.04@9`, host-network build, root `ubuntu:24.04`, by a
revision-bearing PEX built from the pushed branch head
`8d005b38af9777b7e3314bf3e2910314effef4d2` with `--source-revision` asserted.
The recipe is unchanged since rc1, so the content matches the rc1-local base;
only builder provenance differs. Not pushed to any registry, no lock repin,
no matrix change: the owner's reading of "reference the rc2 base by tag"
(digest pin of a new base named for rc2, or a literal tag reference) and the
merge of the release PR are pending. Log `/opt/devcapsule-gate/rc2-local-base.log`.
A first attempt with the `nox -s pex` local artifact was refused by the
builder for lacking a public source revision, as designed.

Manifest compatibility fix (2026-09-24): focused tests 15 passed; full
`nox -s build` passed with 1064 tests, 20 deselected, one xfail, one
quarantined XPASS, mypy, PEX smokes and nine packaged integrations; log
`/opt/devcapsule-gate/manifest-compat-build.log`. Published v0.2.12 and rc1
executables, checksums verified, exercised against the fixed manifest with
isolated XDG state: 0.2.12 `config list` and `config resolve` exit 0; rc1
`config list` exit 0. Pytest scratch had to move to the overlay: this
capsule's 2 GB `/tmp` overflowed on the first run, and a second run under
the home directory failed only `test_unmountable_staging_fails_loudly`,
which expects an unmounted scratch path; the single test passes in `/tmp`
and on the overlay. No capsule was launched; the effect application from
the reserved name is covered by unit tests until RC2 exists.

RC1 configuration failure intake (2026-09-24): owner could not retain the log.
Original successor inspection showed exit 0 and no launch-context/configuration
mounts. One disposable read-only CLI probe of the exact image reproduced
`config list` and `versions show` failures from /opt and the actual project
mount. Bare `project config` prints help successfully. Evidence lives in the
retained run's `configuration-diagnostics.json`; the bug records exact errors
and producer/reader causes. No IDE restart, host-record edit or source fix.
Earlier recursive inspection PASS did not cover this story. No full source
suite was needed for this documentation-only intake.


Published-RC1 recursive PyCharm launch (2026-09-24): retained run
`0edc6f491291f0d5ffa4e31b0238863b` beneath the persistent-home
`e2e-workspaces/` directory. Clean clone at exact RC1 source `cec7a0c`; launched
with downloaded RC1 bytes, SHA-256
`68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
The isolated checkout explicitly selects `devcapsule-base:0.2.14-rc1-local`,
pinned locally to image `sha256:0d9a185ec5a2ac04380e9b5540bae2b212356b8b5d4c0f91c7db320d486a414a`;
the project lock is unchanged. Successor image:
`sha256:bc387eb69b8457f61f016a0a21485302e3fc14bcbbae977e4a1623b8d5544863`.
Container `devcapsule-e2e-0edc6f491291f0d5ffa4e31b0238863b-successor` is running
with host networking; the actual PyCharm JVM is PID 42. Independent
`inspect-successor` passed. As UID 1000, public `devcapsule0` reports published
RC1 and exact runtime bytes, ordinary `devcapsule` is absent, and workflow
installation succeeds in a disposable directory. Evidence in the retained run:
`inspection.json`, `runtime-check.json`, `cli-check.log`, `launch.log`.
Owner received the desktop URL; its token is not committed. Human GUI acceptance
of this exact session is pending; no full recursive Nox suite or final-release
acceptance is inferred. Both this session and the earlier local-source session
remain available. No source changes or new downloads of PyCharm were needed.


Published RC1 and local base (2026-09-24): downloaded the public PEX, checksum
and manifest into `devcapsule-src/dist/rc1-published/`. Verified version
`0.2.14rc1`, mnemonic `v0.2.14-rc1`, source
`cec7a0c2f3467b8cc9d84eca820f35ee869087ec`, and SHA-256
`68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
Used those exact bytes to build `devcapsule-base:0.2.14-rc1-local` with
`--network host`, recipe `ubuntu-24.04@9`. Image ID:
`sha256:0d9a185ec5a2ac04380e9b5540bae2b212356b8b5d4c0f91c7db320d486a414a`.
Build reused cached installation layers. Metadata and a disposable offline
container smoke passed: Python/Git/Docker, Node/JDK/Maven, display executables;
no bundled runtime PEX or agent CLI. Base is local only, with no registry push
or project-lock change. Evidence: `dist/rc1-published/local-base-build.json`;
log `/tmp/maintenance-rc1-base-build.log`. No GUI acceptance of this new base
or final-release acceptance is claimed. Source unchanged; no need to rerun
the source gate for this image build. Initial coordination claim hit a transient
SSH rejection; a subsequent claim succeeded. The release branch was not rebased.

RC1 publication trigger (2026-09-24): fetched main is
`c6bea96cfbbb15a428c86bde6924df8ff3db1c15` (PR #136); it contains release
commit `cec7a0c2f3467b8cc9d84eca820f35ee869087ec`, with matching runtime/test
sources. Candidate gate passed: mainline, zero unintegrated commits. Pushed
annotated `v0.2.14-rc1` atomically with the release branch and verified both
remote tag object and peeled commit. Expected package version is `0.2.14rc1`.
The public manifest returned HTTP 404 immediately afterward; publication is
pending, not failed or verified. No GitHub API/UI inspection was attempted.
Existing source/type/packaging and real PyCharm evidence applies; no runtime
code changed since acceptance. The release branch was not rebased.

Owner follow-up (2026-09-24): "Everything works" for the retained recursive
PyCharm session below. The installed-IDE cache gap was confirmed by reading
the acquisition/materialization path; filed with proposed acceptance scenarios,
severity minor, target none. No implementation or new Docker experiment was
performed for that report. Documentation links and whitespace were checked.

Owner-requested recursive PyCharm launch (2026-09-24): clean local clone of
`9cc08686c5f6c9b44a1a132bf81e4befd0ecf641`, retained run
`29fb2abc530735da1ebd625acd991622` beneath
`/home/devcapsule/.local/share/devcapsule/e2e-workspaces/`.
The original checkout's preflight fails on its existing website Git pointer;
the exact-commit clone passes without changing the original or its user edits.
Built a revision-bearing PEX, initialized isolated checkout configuration/state,
and ran `recursive-e2e launch-successor` with the pinned real PyCharm distribution.
Successor `devcapsule-e2e-29fb2abc530735da1ebd625acd991622-successor` remains
running with host networking. Independent `inspect-successor` passed; PyCharm's
JVM is running and the desktop has a `PyCharm User Agreement` window.
As UID 1000, `devcapsule0` reports the exact source revision and identical PEX
SHA-256 `a0e29d237e978d8c6575ccf12541571a1c0f1d9e016e8f3174ae1b1e23efb34b`;
`devcapsule` is absent. Workflow bootstrap by public command created the expected
files in a disposable in-container directory. Owner received the desktop URL;
its session token is deliberately excluded from committed records. Fresh IDE
first-run interaction and owner terminal acceptance remain pending. This was
the actual successor launch/inspection, not a claim that the full recursive
Nox suite or release-candidate campaign passed. No new release tag was published.

Owner-requested enum cleanup (2026-09-24): `RuntimeCommand` now owns the
supported public names. Configuration boundaries construct enum members;
materialization accepts the enum without repeating string-domain checks.
Existing tests pass enum members and assert typed forwarding from the launcher.
Required `nox -s build`: type checks, 1,060 source tests and nine packaged
integrations passed (20 deselected, one xfail and one quarantined XPASS).
The final Git-status step still fails on the existing website Git pointer;
the overall gate remains failed. Log:
`/tmp/maintenance-runtime-command-enum-build.log`. No new Docker/GUI campaign
was needed for this refactor; the prior command-mode evidence remains separate.
The release branch was not synchronized or rebased; its local workflow
difference from main is the already-read dogfooding rule from this repair.

CLI repair and development exception (2026-09-24): 311 focused checks passed;
four real-Docker variants passed for PyCharm/VSCodium and devcapsule/devcapsule0.
Tests invoke the command by name as UID 1000, verify exact runtime identity,
and install workflow files in a disposable project. Development mode permits
an independent development command without a shipped fallback. Three additional
filesystem cases ensure only our inherited shipped link is removed, preserving
a development script or symlink (eight runtime-artifact checks passed).
Full gate log: `/tmp/maintenance-runtime-cli-build-final.log`; final source
checks passed (1,060 tests, 20 deselected, one xfail and one quarantined XPASS),
as did type checks and nine packaged integrations. Final Git status then
failed on the existing `/home/devcapsule/.git-website` pointer; overall gate
remains failed.
No actual IDE-terminal acceptance of the new code or RC1 publication is claimed.
Earlier lowercase-help assertion failure was a harness defect, corrected before
the four Docker passes. The pre-fix Docker test reproduced exit 127 as expected.

Blocker intake (2026-09-24): live read-only Docker inspection and runtime
version/hash checks confirm the missing public CLI; IDE process environment
inspection confirms the URL-opener conditions. Evidence is in the two new bug
records. No runtime or website source was changed. New record links/index and
Git diff whitespace checks passed. Full build source/type/PEX checks and nine
packaged integrations passed, then final Git status failed on the pre-existing
website pointer to `/home/devcapsule/.git-website`; overall gate not passed.
Log: `/tmp/maintenance-rc0-blocker-intake-build.log`.
Mail delivered: `2026-09-24-maintenance-url-opening-triage.md` to
contained-display at `ba6768619aac`; workflow-onboarding item delivered to
workflow-improvements. Both await disposition, not implementation in this checkout.

Host-network validation (2026-09-24): owner confirmed the runner's host-network
session works. Attempt 4 in `dist/rc0-runs/session-7a4dbc068f58/run.json` records
requested `host`, observed Docker network `host`, exit 0, container absent and
PROCESS_CHECKS_PASSED. The owner made host networking the standing local launch
preference; see WORKFLOW-LOCAL.md, Local Launch Networking. Deliberate network
isolation tests retain their declared mode. Release branch was not rebased.

Runner network option: `--network host` or `--network bridge` on launch/resume
maps to `project run --authorize network VALUE` for that invocation only.
Omitting the option uses saved configuration, not the previous override.
Requested override is saved with each attempt; Docker inspection already
records actual network mode. Existing run records remain readable. No new
container was started solely to test argument forwarding. The eight focused
runner tests pass, including both override values and omission behavior.
Full `nox -s build` passed (source tests, type checks, PEX smokes and nine
packaged integrations); log `/tmp/maintenance-rc0-network-runner-build.log`.
The release branch was not rebased; workflow definition is unchanged.

Website run (2026-09-23): published RC0 passed its checksum gate and
launched VSCodium from this capsule through the host Docker daemon. Run directory:
`devcapsule-src/dist/rc0-runs/session-7a4dbc068f58`; container
`rc0-runner-7a4dbc068f58`; tool PTY session `73149` (now finished).
Attempt 1 failed with exit 2 before creating a container: local resolution was
missing. `config resolve` exposed unanswered local choices. Applied the existing
campaign policy to this capsule's website checkout record: pinned base plus
Claude/Antigravity downloads accepted; host network/Docker/sudo/browser/X11
denied. Explicit resolve succeeded; website source/lock were not regenerated.
Attempt 2 reused the canonical Codium image, translated bind sources to host
paths, and reached contained-desktop readiness on host loopback port 52123.
The runner captured a running container, bridge network, read-only root and
non-privileged execution with no monitor errors. Terminal reports VSCodium
startup. Owner subsequently confirmed "This is working"; recorded as an S05
startup observation in run.json, without claiming specific editing/debugging
assertions. Attempt 2 ended at 23:17:56 UTC with launcher exit 0, container
absent and no monitor errors: PROCESS_CHECKS_PASSED. Owner subsequently
confirmed the file/IDE resume checklist; attempt 3 passed
exit/cleanup checks and its S10 human observation is saved. Agent-session
continuation remains untested. Token URL stays in the terminal/chat, not this record.
The launcher warned that this capsule lacks a global Git author identity;
no identity settings were changed. Existing full gate remains applicable:
this slice changed only launch configuration and records, not implementation.

Session runner (2026-09-23): seven focused stdlib tests passed, including
Docker errors versus absence, nonzero launch, no inferred graphical PASS,
configuration preservation, wrong candidate, changed daemon and concurrent
writers. `runner.py cli --run /tmp/rc0-stories-cli-only-20260923` passed S02,
S03 and S17 against downloaded RC0; attempt `evidence/cli-y6r9a2ve`.
No real GUI/container session was launched through the new wrapper.
The full required gate passed (1,046 tests, 18 deselected, one xfail, one
quarantined XPASS, type checks and nine packaged integrations), log
`/tmp/maintenance-rc0-session-runner-build.log`. No runtime code changed.
Fetched main and live coordination were inspected; mail was empty. Workflow
files are unchanged; the release branch was not synchronized or rebased.

Story automation (2026-09-23): `verify-cli.py` passed real terminal base
accept/decline, fixed creator/default-agent/host answers, missing-base refusal
and CLI remedy, prompted/batch semantic equivalence, and nine local-remote
coordination operations checking every path/blob plus exact staged mail bytes.
Saved evidence: [CLI validation](../../releases/v0.2.14/smoke/cli-validation.json).
Every attempt gets its own directory; S17 runs independently of failed init,
while S03 requires S02's choices.json. The first harness expectation incorrectly
rejected explicit denials; its correction and retained failure are documented.
The fixed configuration wrapper passed on fresh/TypeScript/trading/FastAPI
fixtures without stdin or human answers. CLI-only preparation also passed.
The required gate passed: 1,046 tests, 18 deselected, one existing xfail and
one quarantined XPASS, type checks and nine packaged integrations; log
`/tmp/maintenance-rc0-story-contracts-build.log`. No graphical/provider/service
acceptance was inferred. Shell syntax and documentation links were checked. The retained preview/launch
helpers now fail on Docker query errors instead of misreporting absence;
fault checks distinguish daemon error, missing container and present container.

RC0 smoke harness (2026-09-23): shell syntax, complete preparation with the
verified published PEX, exact public sample clones, fresh initialization,
resolution and configuration-wrapper roundtrip passed in isolated XDG state.
Refusal checks covered an existing run directory, invalid case/arguments and
a mismatched candidate checksum before CLI execution. Validation directory:
`/tmp/rc0-smoke-script-validation-20260923` (preparation/configuration only;
not a host-backed launch location). No IDE, service or provider campaign was
run while authoring these scripts; the generated result sheet remains NOT RUN.
The required `nox -s build` passed: 1,046 tests, 18 deselected, one existing
xfail and one quarantined XPASS, mypy and nine packaged checks. Log:
`/tmp/maintenance-rc0-smoke-scripts-build.log`. These are harness/repository
checks, not acceptance of the unrun graphical campaign.

Legacy-command removal: 115 focused checks passed, followed by successful
`nox -s build`: 1,046 tests, 18 deselected, one existing xfail and one
quarantined claim XPASS, mypy over 167 source files, source/PEX smokes and
nine packaged integrations. Log: `/tmp/maintenance-retire-pycharm-run-build.log`.
Direct built-PEX checks reject bare/help/legacy-option invocations, show only
retained utilities in PyCharm help, and create no checkout state. Source tests
also prove no launcher/subprocess call. Validated artifact:
`devcapsule-src/dist/devcapsule-local.pex`. The gate skipped revision-bearing
packaging due to checkout edits; no fresh Docker/GUI run was necessary for
this command removal, and no such acceptance is claimed. Main integration
is verified through PR #133; the next candidate remains pending. The pre-existing local bug-file edit
remains unstaged and is excluded from delivery.

Bug-combing review at `8e7cc21`: fetched main remains `e50b9f1`; PR #117 merge
`d2386bb` is in main and RC0. At that review runtime/test sources matched RC0. A CLI probe with
only the launcher substituted confirms legacy `pycharm run` still passes host
networking without an explicit choice. 243 focused existing checks passed;
the earlier image review passed 45. No Docker or provider acceptance was run
for this review. The release table distinguishes prior evidence from proposed
candidate checks, including the incomplete byte-preservation assertion in the
nested-directory regression. No branch synchronization or runtime change.

RC0's integration gate passed by mainline ancestry with zero missing commits.
Local RC0 PEX and Docker base were built from a disposable exact-tag worktree,
which was removed after the build; this checkout remains on release-0.2.14.
Nine packaged assertions/checks passed: eight in the first run, then the
identity check after using the harness's canonical artifact filename. No code
was changed to satisfy that filename check. Local and downloaded PEX each
passed the networkless/no-Python clean-machine check. The locally built base
retains tag devcapsule-base:0.2.14-rc0-local and is not published to a registry.

Prior full source gate: 1,044 passed, 18 deselected, one existing xfail and one
quarantined XPASS, mypy and packaged checks. RC0 has identical runtime/test
inputs. That gate describes RC0, not the subsequent removal. The old claim-test
xfail remains; the retirement has its own validation below.

GitHub PR/workflow UI operations stay with the owner; neither gh nor SSO is
available here. No credential probes or API operations were attempted. Public
asset downloads verify publication; no credentialed Actions-run inspection is
claimed. No final release or graphical/end-user acceptance is claimed yet.

## Open Threads

- Paused 2026-10-22 evening by the owner. Nothing is uncommitted; the
  checkout sits on `release-0.3.0` at the published tip; the claim is
  released. The other checkout's sessions write their entries on `main`;
  this one's on the release branch; both met in the second synchronization.
- Done 2026-10-22: PR #249 merged; rc2 tagged, published, verified; the
  lock regenerated and proven by the recursive launch.
- Awaiting the human: PR #250 into `release-0.3.0`, software approvals,
  with its review merged after one round; the go for the schema-version
  slice; the dogfooding of rc2 on the host, the terminal and
  Ctrl+C; the wording of Release Policy 8 for the one version commit on
  the throwaway copy; the eleven user-docs decisions; the word on the
  manifest-rewrite finding; provider acceptance of the new agent pins on a
  downloaded candidate, which needs the lock in a candidate, rc3.
- On resumption, after the merge: fetch and confirm the release tip
  `e5b5a8b` is an ancestor of `main`; `git tag -a v0.3.0-rc2 e5b5a8b -m
  'DevCapsule 0.3.0 candidate 2'`; from a detached checkout of the tag,
  `scripts/release-protocol.py v0.3.0-rc2 --output
  /opt/devcapsule-gate/rc2-release-protocol.json`, expecting `mainline`;
  `git push --atomic origin release-0.3.0 v0.3.0-rc2`; the backend run;
  download the three assets into `~/.cache/devcapsule-releases/v0.3.0-rc2`,
  verify the checksum and the version; record rc2 in the overview and the
  table above, and the changelog's candidate-2 date. Then the owner's
  dogfooding of the terminal and Ctrl+C on the download, and the three
  records' verification on it.
- Then the slices: C17's local half, this project's operating instructions
  in `WORKFLOW-LOCAL.md`; forced configuration and the diagnostics snapshot
  for rc3; image cleanup after the owner's design review, and C20, for rc4.
- Weighed and unresolved, from PR244.1: the supervisor's blocked SIGINT
  during a readiness wait; the 250 ms absorption of a second Ctrl+C.
- Weighed and unresolved, from PR250.1: a stored consent cannot prove the
  terms it was given for; for the consent slice of D-0011.
- Filed for V1 at the owner's direction: the session logs' Python data
  path, [the record](../../bugs/devcapsule/2026-10-22-child-output-is-processed-in-python-on-the-data-path.md).
- External state that outlives the session: the review worktree
  `~/worktrees/maintenance-review` on
  `ws-maintenance/0.3.0-first-session-summary-review`, reusable for the
  next loop by a reset; the gate scratch under `/opt/devcapsule-gate`, on
  the overlay, gone at the next restart; the e2e evidence under
  `devcapsule-src/dist/e2e-evidence/ide-smoke/`; the local branch
  `4PR-3-release-0.3.0`, deleted by the merge on the remote and to be
  deleted locally.
- Deliberately not preserved: the session scratchpad with the Codex and
  Antigravity logs; the briefs are committed under `evidence/`.
- Paused 2026-10-22 on `ws-maintenance/e2e_videos-2` after completing the
  Claude Fable 5.1 review-partner loop ([PR #241](https://github.com/ccozianu/devcapsule/pull/241))
  for [PR #236](https://github.com/ccozianu/devcapsule/pull/236).
- Awaiting the human: review and merge [PR #236](https://github.com/ccozianu/devcapsule/pull/236)
  (`ws-maintenance/4PR-e2e_videos-2` into `main`).
- Weighed and unresolved, from PR #241 (PR236.1):
  1. Transcoding PNG frames to JPEG with Pillow in the parent process instead of
     an in-page `<canvas>`, reducing browser round-trips and decoupling WebM
     encoding from a live Playwright page.
  2. Passing `-framerate` instead of `-r` before `-i pipe:0` for `ffmpeg`'s
     `image2pipe` input.
  3. Adding a dedicated `nox` session wrapper for `tests.e2e.scenario_recorder`
     (`serve`, `ctl`, `replay`) so operators do not need `PYTHONPATH=src:.`.
- Deliberately not preserved: the review worktree
  `/home/devcapsule/worktrees/maintenance-review` and its branch
  `ws-maintenance/4PR-e2e_videos-2-review` (removed after merging PR #241);
  gate and review logs under `/opt/devcapsule-gate/` and the session scratchpad.
- Resumed 2026-10-21 under rc1; the re-verification of the 2026-10-19
  threads is in Current State. Two checkouts work this workstream; the
  second one's session published this file from `main`'s copy with the
  rc0 state line. Open with the owner: which checkout publishes the
  status file while both are on maintenance; this one, the release
  checkout, is the recommendation.
- Closed 2026-10-21: the console-link record, on the owner's verification.
- Done 2026-10-22: PR #240 merged into `release-0.3.0` at `6ebadf2`, PR #243
  into `main`; the network node is on the release branch for rc2. Next:
  C10, its details to the owner first.
- Awaiting the human: PR #244 into `release-0.3.0`, C10, with its review
  merged after one round; then the word for rc2.
- Weighed and unresolved, from PR244.1: the supervisor's blocked SIGINT
  during a readiness wait; the 250 ms absorption of a second Ctrl+C.
- To record on `main`: the Antigravity invocation form proven on
  2026-10-22, the model flag before `-p` and the brief on standard input
  behind a one-line instruction, in the developer document.
- Done 2026-10-22: PR #237, #238 and #239 merged to `main`; the
  scratch-mount item mailed to `project-management`.
- Weighed: Version Scheme rule 4, `main` reopening at the cut, has no
  companion paragraph in the humane file; left out of PR #237 unless the
  owner adds it.
- On resumption, re-verify before trusting: which launcher started the
  capsule (`devcapsule0 version`), whether the shared lock changed on disk
  (the owner may run the lock command on the host before relaunching; if
  so, commit the written lock on the release branch and rerun the gate),
  and whether this checkout was given the local recipe-11 base.
- Next slices in the recommended order: the universal `network` node,
  then C10 with its two records filed first, forced configuration, the
  diagnostics snapshot, image cleanup after the design review, C20 last.
  The local Docker proofs against the rc1 download when the host daemon
  is free.
- Deliberately not preserved: the rc0 and rc1 downloads under
  `~/.cache/devcapsule-releases/`, regenerable from the public releases;
  the gate logs under `/opt/devcapsule-gate/`; the smoke scratch of the
  agent freshness attempt in the session scratchpad.
- Closed 2026-10-18, twice: PR #228 carried the release version onto
  `main`; the owner then changed the protocol, and PR #229 reopens `main`
  at 0.3.1.dev0 at the cut, ahead of every candidate.
- Closed 2026-10-18 by the owner: delete-on-merge stays; the release
  branch merges into `main` through a throwaway copy, *Release Policy* 8.
- Awaiting the human, with the version question: whether the manifest's
  release-branch line (`source-version` on `devel`) is acceptable until the
  contract or its check gains a release-branch rule, mailed to
  project-management on 2026-10-18.
- At the owner's convenience: the one host command in PR #224 that
  regenerates the shared lock, so this checkout runs the new agents; it no
  longer gates anything.
- The local branch `ws-maintenance/release-0.3.0`, the previous session's
  parking spot at the merge of PR #222, has no commits of its own and is
  not on the remote; left for the owner to delete.
- Weighed: the C10 bug records are not filed; the C10 slice files them
  first, as the work order says.
- External state that outlives the session, all removable now that the
  PRs are merged: review worktrees `~/worktrees/maintenance-review` and
  `~/worktrees/maintenance-review-pr2`; the acceptance clone and venv under
  `~/.local/share/devcapsule/e2e-workspaces/logs-accept`; local images
  `devcapsule-base-e2e:v0.2.16.dev0-local-linux-x86_64-36bef9f1e151` and
  `devcapsule-local-codium:60ed46caf1a3e8897e5d`.

Threads of the 2026-10-12 pause, decided or overtaken on 2026-10-18 where
marked:

- Decided 2026-10-18: two items from project-management taken on
  2026-10-12, `2026-10-11-project-management-bootstrap-target-09.md` and
  `2026-10-11-project-management-pre-rc-sequence.md`, in the intake; decide
  them first on resumption, they are not forwardable.
- Done: PR #207 and PR #209 are merged (2026-10-11, and #216 on 2026-10-15).
- External state that outlives the session: review worktrees
  `~/worktrees/maintenance-review` and `~/worktrees/maintenance-review-pr2`;
  the acceptance clone and venv under
  `~/.local/share/devcapsule/e2e-workspaces/logs-accept`; local images
  `devcapsule-base-e2e:v0.2.16.dev0-local-linux-x86_64-36bef9f1e151` and
  `devcapsule-local-codium:60ed46caf1a3e8897e5d`. All removable once the
  PRs are merged.
- Weighed and unresolved, from PR1.1: the supervisor's `preexec_fn` runs
  with tee threads alive, which Python documents as unsafe; a helper that
  sets the mask and execs would remove it. Not changed, no failure seen.
- Weighed and unresolved, from PR2.3: an atomic replacement of the live
  path for readers that follow it across a rotation; a drain policy for a
  compression that outlasts the supervisor's 0.5 s allowance at shutdown.
  Neither changes the contract; both are candidates for the next slice.
- Weighed and unresolved: the budget knob is an environment variable; a
  configuration node would be durable but touches the guarded vocabulary.
  Xvnc at status level rather than errors only.
- Weighed and unresolved: the C10 first-session bug records are not on
  `main`. The diagnostics slice takes the Ctrl+C result into its scope
  unless project-management files them first.
- Deliberately not preserved: the review worktree of
  `pr172-correctness`; the web console caches under
  `devcapsule-webconsole/`, which `.gitignore` covers.
- The original checkout's website pointer stays untouched. SSH through
  `ssh.github.com:443` worked when port 22 timed out on 2026-10-08.

Earlier threads follow; read against the state above.

- Resumed 2026-10-05; main merged in at `242e13e` (fast-forward). Decisions
  (1) to (3) are taken: ecosystem bootstrap stays a bug, target 0.3.0,
  last on the plate; the recursive successor record goes by option D, the
  fresh-workspace test, with the general rule in the e2e doc; the
  installed-IDE reuse and reaping design is in the next release, which
  the owner named 0.3.0 (mail to project-management sent); (5) the
  host-network run-once item is a bug by the owner's ruling, `network`
  becomes a universal node, filed and dispositioned. (4), the in-capsule
  project-command fix, stands as decided on 2026-10-01; restated on
  2026-10-05 without objection. The triage is complete. The three
  component-catalog items are dispositioned (packaging patch applied and
  green; the conservative-writers correction is the requirement under
  *Current State*, with the owner's `resolve --force` and `run
  --force-config` addition, mailed to project-management). Next: the
  owner confirms the plate's order; no implementation has started.
- Intake item, host-network run-once launch rejected (superseded 2026-10-05
  by the bug record; kept as the trail): component-catalog's
  diagnosis is incomplete. `_RUN_ONCE_AUTHORIZATIONS` includes `network` on
  `main` and here; the node exists only on projects whose manifest
  recommends `host.network.mode` (`authorization_declarations` builds it
  from `CURATED_HOST_RECOMMENDATIONS`, and `WORKSTATION_CAPABILITY_DEFAULTS`
  deliberately omits it because raw `--network` was the run-once form,
  which run help now refuses). This repository recommends it, so the
  WORKFLOW-LOCAL command works here; the smoke's fresh project does not.
  Product choice for the owner: make network a universal authorization node,
  or amend WORKFLOW-LOCAL to say the command presupposes the recommendation
  (recommended). Owner ruled 2026-10-05: universal node; it is a bug.
- The claim on the triage slice was released at this pause.

- Final 0.2.15 publication and download verification are complete.
- PR #149 is merged and verified; main is reopened at 0.2.16.dev0.
  Await owner dogfooding feedback on released 0.2.15; no new scope is inferred.
  User-facing release notes are prepared in the release overview; GitHub's
  final release body currently contains its generated changelog link.
- Project-management receives final identity/acceptance and reopening state;
  0.2.16 scope decisions remain with that workstream and the owner.
- New source and records branch: `ws-maintenance/post-0.2.15`. The release
  records exception has ended; publish from this branch going forward.
- Final downloads: `/home/devcapsule/.cache/devcapsule-releases/v0.2.15`;
  gate `/tmp/0215-final-gate.json`; verifier `/tmp/0215-verify-final.py`.
  RC1 downloaded proofs and private fixtures remain alongside. Scratch
  evidence is regenerable; no credentials/tokens or session transcript in Git.
- Use `TMPDIR=/opt/d215` for gates. Do not infer release identity from local
  mainline dist builds. Retain published release/candidate tags unchanged.

Earlier open-thread history (read against the current scope above):

- Pause of 2026-09-26. Merged to `main` today: the base-contract slice
  (consent bound to the image, bases named by `family@recipe`, compatibility
  report), the `devcapsule.images` package, and the design-experiment work
  order. Awaiting the owner: yes or no on the named-build-context fix for
  the 4.8 GB rebuild transfer; the GitHub release body for `v0.2.14`.
  Awaiting project-management: 0.2.15 registration and scope, the
  release-notes artifact, the mycodespace note and checkout naming. Still
  open from the design note: the base as a version-set member, registry tags
  by contract and date. The `ws-user-docs/first-session` branch carries the
  mycodespace design note and needs its own PR to reach `main`.

- Pause of 2026-09-25, after 0.2.14 shipped and the close-out cleanup.
  Awaiting the owner: the PR from `ws-maintenance/post-0.2.14` (registry
  rows, 0.2.15.dev0, close-out records); the GitHub release body for
  `v0.2.14`, notes text in the release overview; option A or B for the
  `v0.2.12` mnemonic; yes or no on the named-build-context fix. Awaiting
  project-management: registration and scope of 0.2.15 (mail of
  2026-09-25), adoption of the mycodespace note and the checkout-naming
  default (mail of 2026-09-25). Awaiting workflow-improvements: the four
  workflow gaps (mail of 2026-09-25). Deliberately not preserved: the
  scratch builds and downloaded candidates under `/opt/devcapsule-gate`,
  which are regenerable from the public releases.

- Owner's rc3 test, 2026-09-24, produced three findings, all recorded and
  now dispositioned: the trailer is fixed by the list/show split (RC4); the
  acquisition decision stays required with a named release-notes exception;
  the checkout naming is not a bug. Earlier text of this thread follows:
  the launcher change rebuilt the formation with a 4.28 GB context transfer
  and 39 retained images at 266 GB (added to the installed-IDE reuse bug);
  `config list` advises resolve on a fresh resolution (new minor bug, fix
  proposed); and an untouched 0.2.12 checkout now owes a required
  antigravity-download decision (new bug under R-COMPAT-001, disposition
  needed: restore 0.2.12 behavior or name the exception in the notes).
  The rc3 launch worked and the owner confirmed `devcapsule0` on the PATH in
  the capsule: the runtime-CLI blocker is closed as verified on rc3. From
  `/opt` the configuration inspection still fails; from the project mount it
  works, so only the discovery fallback (cause 2) affects ordinary launches.

- RC2 is required: rc1 accepts the fixed manifest but applies the
  `devcapsule0` exception only from the attribute, so dogfood sessions
  launched with rc1 on the fixed manifest get the normal `devcapsule` name
  until RC2. Existing running capsules are unaffected.
- The owner's host executable was not identified; the reported message can
  only come from 0.2.12 or rc0. Ask for `devcapsule version` when closing.
- The guard test pins `docker.memory-limit` as the released vocabulary; move
  it to include `devcapsule.command-name` when 0.2.14 final ships.
- The website checkout in this capsule has an embedded `.git` directory
  since 2026-09-23; the other checkout's pointer repair did not hold, as the
  owner's `git status` failure shows. Not repaired from here.

- RC1 runtime-configuration inspection bug needs component-upgrades triage;
  owner expects read-only inspection from /opt as well as the project root.
  Mail delivered at `dc91dbc8e484`; acknowledgement and repair remain pending.
- Run `0edc6f491291f0d5ffa4e31b0238863b` subsequently exited normally (code 0);
  earlier retained-running notes below are historical. No restart was attempted.

- Published RC1 plus the newly built local base is running in retained recursive
  run `0edc6f491291f0d5ffa4e31b0238863b`; agent checks passed, owner GUI acceptance
  pending. Keep it running for the owner; do not stop the earlier session either.

- Recursive PyCharm successor run `29fb2abc530735da1ebd625acd991622` is deliberately
  retained for the owner; see validation above. Do not stop or remove it merely
  because this agent turn finishes. Owner subsequently confirmed everything works.
- The runtime CLI blocker is fixed in source, awaiting main integration and
  exact-RC1 validation; public assets now verified and PR #136 is merged. Owner accepted
  the local PyCharm/devcapsule0 session; exact-candidate validation remains.
  Existing running capsules retain their original commands until relaunched.
- URL-opening triage and workflow-onboarding work item are handed to their
  owners through coordination mail. Their acknowledgement remains pending.
- The local workflow change reported by brief is our owner-directed host-network
  rule, already read; the release branch was not synchronized or rebased.
- Website Git pointer repaired locally on 2026-09-24 after the owner reported
  plain `git status` failing. Replaced missing `/home/devcapsule/.git-website`
  with relative `../.git/modules/website`; the existing metadata HEAD matches
  the parent's pinned commit `78b7b7f`. Original pointer saved at
  `.git/codex-website-git-pointer.before`. Plain parent/submodule status now
  works; website status and staged/unstaged binary diffs are unchanged.
  No source, index or ref was reset. The earlier policy-only full build passed
  source/type/PEX checks and nine packaged integrations before failing at this
  status operation; log `/tmp/maintenance-host-network-policy-build.log`.
  That historical full gate was not rerun for this local metadata repair.
- Exact RC0 website startup and file/IDE resume now have owner confirmation.
  Do not extend that evidence to unperformed edit/debug or agent tasks.
- Website runner attempts 2/3 are complete: owner confirmed startup and
  file/IDE resume; automatic exit/cleanup checks passed. Agent continuation
  and detailed edit/debug assertions still need execution. Website submodule
  changes belong to the owner and were untouched.
- Owner rejected the earlier manual-heavy campaign. Stories now govern the
  work; do not describe all 21 as automated. Implement remaining machine steps;
  desktop-control tooling is absent here. No provider/GUI acceptance is claimed.
- A pre-existing single `c` insertion in the smoke README remains in the working
  tree and is excluded from the rewritten document's commit, like the earlier
  unrelated bug-file edit. Its intent was not inferred.

- Legacy launch capabilities now have an owner-directed V1 gate: decide what
  is already covered, migrate selected capabilities, design an image-oriented
  mode only if justified, or explicitly drop them. The work order preserves
  the findings; project-management owns scheduling and ledger registration.
- Owner review of the 13 remaining bug dispositions remains; the full rationale
  and grouped acceptance observations are in the release bug table. Review
  project-launch old-base/X11 scope before closure of the display exposure record;
  distinguish repaired formation boot behavior from remaining image cleanup.
- A pre-existing local edit in the legacy-network bug removes one word and
  leaves trailing whitespace. It was preserved verbatim and excluded from
  all agent commits. Agent-authored retirement notes in that same file are
  staged separately from the pre-existing edit.
- Image composition redesign is deferred beyond 0.2.14 unless the confirmed
  multiline-rendering defect recurs during the release E2E campaign; preserve
  its documented-contract and unit-testing scope when scheduling the work.
- RC0 is published; end-user acceptance and selected further bug dispositions remain.
- Project-management coordinates renames after 0.2.14 publication, before
  substantive next-release work. This no longer holds 0.2.14 candidates.
- Workflow-improvements owns the claim-test design repair and generic release
  propagation rule revision; the local owner exception already governs here.
- Preserve retired-outbox follow-up, configuration contracts/coverage limits,
  and historical host/blog acceptance gaps; no unrelated cleanup was done.
- The pre-existing Codium delimiter edit remains saved at
  `.git/codex-preserved-codium-sudo-edit.patch`; its intent was never inferred.
  The canonical bug record now records retirement, so review before applying it.
- No transcript/session record was requested; canonical decisions live in the
  release documents and bug records.

## Workstream Document Index

- [PR #236 review-partner brief (PR236.1)](evidence/2026-10-22-pr236-review-brief.md): brief for Claude Fable 5.1 on the E2E scenario video recorder and Eclipse Java debugger demo slice.
- [Landing-page work order (`Why DevCapsule?`)](../../work-orders/2026-10-18-landing-page-why-devcapsule.md): Deliverables 1–4 completed and verified on `ws-maintenance/e2e_videos`.
- [Stretch-goal hero video follow-up work order](../../work-orders/2026-10-19-eclipse-java-1brc-hero-video.md): Eclipse/Java 1BRC hero video stretch goal with reusable pipeline preamble and unblocking options.
- [0.3.0 release overview](../../releases/v0.3.0/README.md): the cut, the checklist, the freshness review, the candidates; open for any release question.
- [0.3.0 bug table](../../releases/v0.3.0/bugs.md): the records the release carries and their dispositions.
- [0.3.0 changelog](../../releases/v0.3.0/changelog.md): what is new and fixed since 0.2.15, maintained at every candidate; the prerelease body.
- [Diagnostics and logs](../../../docs/troubleshooting/diagnostics-and-logs.md): the user-facing statement of slice 1; open when changing what a session logs.
- [Session logs acceptance](evidence/2026-10-11-session-logs/README.md): the recipe-12 base, the real session, the rotation; open when a reviewer asks what was proven on a capsule.
- [PR #172 review](2026-10-08-pr172-review.md): findings, fixes, regression evidence and remaining limits.
- [Unpacked cache publication/recovery bug](../../bugs/devcapsule/2026-10-08-unpacked-cache-publication-and-recovery.md): fixed on review branch; close after main integration.

- [Released launchers reject the repository manifest](../../bugs/devcapsule/2026-09-24-released-launchers-reject-repository-manifest.md): blocking, fixed on branch, needs RC2.

- [RC1 runtime configuration inspection](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md): component-upgrades; confirmed, target 0.2.14.

- [Installed IDE Docker reuse](../../bugs/devcapsule/2026-09-24-installed-ide-docker-reuse.md): review design with owner before implementation; no release target.

- [Runtime CLI blocker](../../bugs/devcapsule/2026-09-24-runtime-cli-not-on-path.md): next implementation task; blocks 0.2.14.
- [URL-opening defect](../../bugs/devcapsule/2026-09-24-url-opening-without-browser-handler.md): contained-display triage.
- [Workflow onboarding](../../work-orders/2026-09-24-workflow-installation-onboarding.md): non-blocking follow-up.

- [Legacy launch capability work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md): future-release decisions and delivery, blocking V1.
- [Release overview](../../releases/v0.2.14/README.md): cut, candidates and acceptance checklist.
- [Release bug triage](../../releases/v0.2.14/bugs.md): maintained dispositions and evidence.
- [RC0 validation runner](../../releases/v0.2.14/smoke/README.md): executable coverage and exact candidate inputs.
- [RC0 validation stories](../../releases/v0.2.14/smoke/stories.md): dependency types, actors, contracts and remaining automation.

- [Attribution checkpoint](2026-09-22-record-commit-attribution.md): integrated authorship convention, owner acceptance and build evidence.

- [Run-image replacement checkpoint](2026-09-22-record-run-image-replacement.md): merged implementation, validation and coordination recovery evidence; open only for those details.
- [Prior checkpoint record](2026-09-21-record-maintenance-before-component-upgrades.md): historical implementation, tests and graphical evidence; open only for those details.
- [Proposed bug triage](2026-09-21-note-proposed-bug-triage.md): open on resuming triage; not applied.
- [Pre-V1 assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): positioning input and owner Windows correction.
- [Early-adopter blog](../../blog/2026-09-21-why-try-devcapsule-before-v1.md): merged article and editorial follow-up.
- [Upgrade recovery contract](upgrade-recovery-contract.md): scope of the merged recovery fix.
- [Configuration contract](configuration-contract.md): lifecycle requirements relevant to future changes.
- [Correctness/test map](configuration-correctness.md): implementation evidence and coverage limits.
- [Intake decisions](intake-dispositions.md): outcomes of received mail.
- Persistent session diagnostics work order: expected at `engineering-docs/work-orders/2026-10-08-persistent-session-diagnostics.md` once project-management commits it; until then the text is the intake item at coordination `a535ccf`.
- `intake/`: empty; the three items of 2026-10-09 and 2026-10-11 are decided in the decision log.
