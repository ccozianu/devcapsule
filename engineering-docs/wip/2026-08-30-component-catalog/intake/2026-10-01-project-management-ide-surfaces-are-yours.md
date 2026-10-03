# IDE Surfaces Are Component-Catalog Work: Eclipse Folded In, IntelliJ Targeted At 0.2.16

Sent: 2026-10-01

From: `project-management`, to `component-catalog`. Owner decisions of
2026-10-01, taken in the project-management checkout.

## What Is Handed Over

1. **An IDE is a component, and you accept and test new components.** The
   owner ruled that surfaces are not a workstream each. `component-catalog`
   is the home of every new surface; `component-upgrades` owns the code
   that wires components (orchestration, upgrades, channels). This lifts
   the freeze your registry row records at the final smoke slice (PR #65):
   the owner is giving you new content, and your row is yours to update.
2. **`eclipse-surface` concluded today and is archived** at
   `engineering-docs/archive/2026-09-09-eclipse-surface/`. It never forked
   a branch or implemented anything. Its entry survey of 2026-09-09 is your
   starting material if the owner ever schedules Eclipse: the licence
   answer, the shared-installation mechanism, and the files an Eclipse
   integration touches. Eclipse is not scheduled.
3. **IntelliJ IDEA is a 0.2.16 target and yours to build**, as a second
   JetBrains surface on the existing adapter, which is PyCharm-shaped today
   (`devcapsule/components/pycharm.py`, `devcapsule/launch/pycharm/`). The
   owner's reason: the opt-in IDE smoke test (`nox -s ide-smoke`,
   `tests/e2e/test_ide_comes_alive.py`) proves from the outside that a
   surface comes alive, parametrized over the `SURFACES` table in
   `tests/e2e/ide_session.py`, so a new surface is cheap to accept. Your
   acceptance evidence is one more row there, `jetbrains-idea` window
   class, passing.

## Why It Belongs To You

Your goal is making IDE surfaces regular catalog components; VSCodium on the
normal project path was the first track. A second JetBrains product on the
same adapter is that generalization continued, and the owner named you.

## Evidence

- Owner decisions recorded in
  `engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md`,
  *Owner Decisions Of 2026-10-01*, and the addendum of the same date in
  `2026-09-27-0216-release-planning.md` (candidate C12), both on
  `ws-project-management/coordination` until integrated.
- The archived Eclipse survey, section *Finding 3*, for what a surface
  integration touches.

## What Accepting Means

Record IntelliJ as a task in your order of work and lift the frozen-scope
wording in your row. Release 0.2.16 is not registered yet; the driver,
cut trigger and the formal work order follow the owner's remaining
decisions, and the proposal's current recommendation is that `maintenance`
drives and IntelliJ merges to `main` before the cut as ordinary content.
Size is your estimate, not ours; the proposal guesses days.
