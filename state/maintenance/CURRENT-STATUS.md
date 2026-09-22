# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused 2026-09-22 at owner request to switch to project-management; PR #128 integration verified

Definition read: WORKFLOW.md@60772d54f11b, WORKFLOW-LOCAL.md@0f44773f837c

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `ws-maintenance/triage`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

Run-image replacement and incident recovery evidence are preserved in the
[completed-slice checkpoint](2026-09-22-record-run-image-replacement.md).

## Last Task

Verified PR #128 merged at `ca3f1d3`; `git cherry origin/main HEAD` reported no
unintegrated commits and the tree differed only in the generated coverage badge.
Fast-forwarded to fetched main `0d13111`. The attribution policy and closed bug
are integrated; owner-confirmed GitHub display and full-gate evidence are in the
[attribution checkpoint](2026-09-22-record-commit-attribution.md). No code changed
for this handoff, so the passing validation of the delivered tree remains sufficient.
The owner explicitly directed switching this clean checkout to project-management.
Maintenance mailbox and intake are empty; all owed mail was delivered.

## Planned Next Step

Resume the saved bug triage with the owner when maintenance is selected again.
Retired-outbox verification remains accepted follow-up. Run-image replacement
and commit attribution are integrated; the legacy PyCharm networking issue remains
open. Do not reopen either completed delivery merely because older records say
integration was pending.

## Validation And External State

No new runtime validation is required for this integration-verification record.
The checkout-local human Git identity remains configured; future agent commits
must follow the integrated model-first attribution rule. No session-owned
containers or ports were created, and retained historical containers were untouched.

## Open Threads

- Awaiting the owner: select maintenance again to resume the preserved triage.
  Run-image and attribution deliveries are integrated in PRs #125 and #128.
- Awaiting workflow-improvements: fix the nested-directory coordination bug.
  Use the root-cwd workaround. The separate diff-handoff rule is now on main.
- Preserved: 14-item triage, remaining legacy host-network issue, broader
  configuration evidence/docs, release sequencing and retired-outbox verification.
- Production blog deployment and incident-era exact host bytes remain unverified;
  no new live acceptance or cleanup is claimed.
- Deliberately not preserved: no transcript/session record; the received diff
  remains in intake history and coordination history after disposition.

## Workstream Document Index

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
- `intake/`: no pending items; both project-management messages acknowledged in the decision log.
