# 0.3 direction: launcher compatibility, environment transitions and recovery

From: component-catalog
To: project-management
Date: 2026-10-04

## Owner direction

After the shared-checkout Playwright failure, the owner reported recovery by
using an already-built executable in `dist`, accessible from the host. The
owner then asked that the lessons inform the next 0.3 and reiterated that
DevCapsule needs a 0.3 release. This records a release direction, not an
approved complete scope, schedule, release driver or instruction to replace
the existing 0.2.16 plan. No version bump has been performed.

## Evidence

Component commit `ada153c` added an unreleased capability to the shared need
and lock. A released launcher failed with `no V1 runtime template is available
for component 'playwright'`. Development-executable E2E acceptance did not
exercise the owner's normal host restart path. The owner recovered with a
built development executable; its exact identity has not been supplied.

The immediate rollback/rule/guard change is `3dbe4cb` with record stamp
`267fe30`, on `ws-component-catalog/intellij-idea`, awaiting owner integration.
The bug record is
`engineering-docs/bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md`.
The rollback has source-level compatibility evidence; the owner's development
executable recovery is not confirmation of that separate rollback path.

## Proposed 0.3 requirements and acceptance criteria (agent recommendations)

1. **Compatibility is explicit.** Define a contract relating manifest, lock,
   consuming launcher and delivered runtime. Detect incompatibility before
   downloads or materialization; identify the running executable and give an
   actionable supported recovery path. Decide the contract's representation;
   do not assume a minimum-version field alone fully describes compatibility.
2. **Environment changes preserve restartability.** Before promoting changed
   needs/locks into a working project, establish the launcher's ability to use
   them or carry out an explicitly agreed upgrade. Preserve a compatible
   recovery pair and make interrupted transitions recoverable.
3. **Bootstrap and recovery do not depend on a running capsule.** Provide a
   documented, identifiable host-side launcher acquisition/selection path.
   Recovery must not require compiling inside the environment that cannot
   start, or finding an incidental artifact in `dist`. Intentional development
   builds remain possible; their identity and selection must be explicit.
4. **Acceptance covers the next session.** Exercise a prior released host
   launcher with a newer project/lock, a deliberate launcher upgrade, a cold
   restart and recovery after an interrupted/failed transition. A child smoke
   with the development executable is a separate assertion. Existing shipped
   launchers cannot acquire better diagnostics retroactively, so include their
   external migration/recovery instructions.

## Requested disposition

Take the owner's 0.3 direction into release planning. Decide with the owner
which of these recommendations become requirements, their workstream owners,
and how 0.3 relates to the existing 0.2.16 scope. Coordinate with
component-upgrades on its already-agreed consent/recovery work rather than
creating a competing upgrade policy. Separate the local safety rule and
immediate regression repair from the product guarantee to be designed for 0.3.
