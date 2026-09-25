# Input: Start 0.2.15 As An Optimized 0.2.14, Within A Week

Sent: 2026-09-25

From: `maintenance`, carrying the product owner's direction given on
2026-09-25 right after 0.2.14 was published, with maintenance's estimate
attached. The decisions are the owner's; sequencing and the release
registration are yours.

## The owner's direction

- 0.2.14 is stable enough. Aim for 0.2.15 within a week.
- 0.2.15 is cleanup and optimization, no new features: ship it as an
  optimized 0.2.14.
- The owner will spend significant time dogfooding 0.2.14 on a handful of
  projects: the website, the documentation project, and the trading-research
  sample.
- A wish for 0.2.15: significantly expand the IDE surface, supporting
  Eclipse, VS Code, IntelliJ, and Antigravity as an IDE. The owner asked
  whether a week is too ambitious for that.

## Maintenance's estimate on the IDE surface

Too ambitious for one week, and it contradicts "no new features"; the
honest split is:

- IntelliJ IDEA: days. Same JetBrains adapter as PyCharm, a different archive
  and checksum in the matrix, one launch validation.
- Eclipse: the `eclipse-surface` workstream is registered and awaiting your
  scoping instructions; nothing is built. A new adapter family.
- VS Code proper: the `codium` component exists; Microsoft's build differs in
  licensing, telemetry and acquisition terms, so it is a new acquisition
  gate and a consent text, not a copy of codium. Days once the terms are
  settled.
- Antigravity as an IDE: today Antigravity is an agent CLI component. The
  IDE is a separate product with its own acquisition and display needs.
  Largest and least known of the four.

Recommendation: keep 0.2.15 to cleanup and optimization on the week
horizon, and let the surfaces be the theme of the release after it, starting
with IntelliJ because it rides the existing adapter. If the owner wants one
surface in 0.2.15, IntelliJ is the one that fits a week.

## Cleanup and optimization candidates known today

From the release close-out, all recorded with root causes:

1. Formation rebuild cost on every launcher change: the build context copies
   the extracted IDE tree (3.5 GB) into a fresh temporary directory and
   BuildKit transfers 4.8 GB because the context path is new each time.
   Bounded fix proposed: named build contexts on stable extracted paths,
   the main context reduced to the PEX and small files. Recorded on the
   installed-IDE reuse bug; the full cross-formation reuse stays a design
   review.
2. The pinned 0.2.12 base carries the candidate name `v0.2.12-rc5` in
   messages and locks; Docker Hub tags the same image `v0.2.12`. Option A
   renames the display mnemonic only (no lock change); option B also
   changes the lock fragment, which advances the matrix and re-prompts base
   consent everywhere on regeneration. Maintenance recommends A.
3. No per-checkout way to select the base the client recommends when it
   is newer than the project lock's; version sets cover components only.
   A design question for component-upgrades under R-UPGRADE-001.
4. Five rows deferred as minor during acceptance, and the `/opt`
   configuration discovery sent to V1; see the 0.2.14 bug table.
5. Repository hygiene: retired `*/outbox` branches and old-name branches
   remain after the `ws-` migration; the submodule-to-workspace migration
   waits for mycodespace's bootstrap (design note of 2026-09-24).

## What maintenance did today

Migrated the active workstream branches to `ws-<name>/<sub>` at the owner's
direction, moved maintenance off the release ref to
`ws-maintenance/post-0.2.14`, reopened `main`'s development version at
0.2.15.dev0 per WORKFLOW-LOCAL.md, and updated the registry rows. Each
workstream still names its old branch in its own status until it next
publishes.

## Asked of project-management

1. Register 0.2.15 with its driver and the week horizon; maintenance can
   drive it as an optimization release if you prefer continuity.
2. Decide the IDE-surface scope against "no new features", and scope
   `eclipse-surface` if any surface enters 0.2.15.
3. Sequence the cleanup candidates above and assign the base-selection
   design question.
