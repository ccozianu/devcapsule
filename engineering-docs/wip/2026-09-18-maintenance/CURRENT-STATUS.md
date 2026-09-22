# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active 2026-09-22; run-image replacement validated and ready for owner PR integration; broader triage preserved

Definition read: WORKFLOW.md@a1002b6f5e67, WORKFLOW-LOCAL.md@ed70f3147563

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `ws-maintenance/triage`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

The owner explicitly selected maintenance after project-management delivered the
run-image replacement as a tested diff. Project-management was paused, committed,
pushed and published before switching this clean checkout. Maintenance was rebased
onto fetched main `20336d8`: workflow/local rules and launch files had changed, so
synchronization was required. The sole conflict was the registry row; preserved
maintenance's pause record and main's newer component-upgrades registration.
Read the changed definition/local rules, full status/open threads, intake and saved
triage. No other maintenance claim was present. The independent maintenance commit
before resumption was a pause record, not unpublished implementation.

Took both project-management messages and committed receipt at `6c6f08f`. Accepted
the owner-decided removal of `project run-image` and replacement with
`project run --print-command`. The later message supplies the implementation and
supersedes the earlier request to implement it. Applied the exact embedded patch
with SHA-256 `79794674807cbd3c1784599ac1ed0ae8e03995c0958917fb0e4347e60b0cbea9`;
it passed applicability and whitespace checks against this rebased tree. Print
mode uses normal preparation/final argv, isolates stdout, identifies transient
resources, keeps cleanup, and skips project launch, update offers and success
recording. No editor/replay bundle or retained resources were added.

Fourteen open maintenance-owned bug records were listed at resumption; the saved
triage remains the inventory and proposal. Broad ratings/dispositions remain
unapplied. The network record now explains the retirement decision and preserves
the unresolved legacy `pycharm run` host-network default. This slice does not close
that entire bug. The merged configuration fixes and blog remain integrated by
main ancestry; production website deployment is not newly verified.

## Coordination Incident And Recovery

Resumption found the expected mailbox empty. Inspection showed the sender's
nested-directory mail calls had built incomplete coordination trees: `93d794a`
removed unrelated mail/state and `f0b43c6` removed the maintenance patch. Historical
blobs remained intact. Append-only recovery at `0bf1bc785774` restored 16 missing
files, preserving newer publications and legitimate recipient takes, and omitting
the explicitly released project-management claim. Both maintenance messages were
then received normally. No remote reset or force-push was used for recovery.

The [confirmed coordination bug](../../bugs/devcapsule/2026-09-22-workflow-nested-directory-loses-coordination.md)
belongs to workflow-improvements. Sent complete evidence in
`2026-09-22-maintenance-coordination-data-loss.md` at `e6dc1b022ba8` so repair does not
wait for this integration. Current workaround: run coordination commands from the
repository root with an absolute `--project`. Recovery is not a code fix. The
workflow diff-handoff proposal remains separate and has not been silently adopted.

## Planned Next Step

Owner opens/reviews/merges `ws-maintenance/triage` into main through GitHub. This
bounded implementation is validated; both intake decisions are recorded with the
items' deletion. After the owner reports integration, fetch and verify main.
No release tag or automatic workstream switch is implied. After this delivery,
resume the saved triage with the owner; retired-outbox verification/deletion
remains accepted follow-up.

## Validation And External State

The receiving branch's required `nox -s build` passed: 1,041 tests, 18 deselected,
one existing xfail, mypy on 167 files, shell/CLI checks, local PEX construction
and smoke, and nine packaged checks. This independently confirms the prior patch
validation on the rebased receiving tree. The public revision-bearing PEX was
skipped under the existing dirty-tree policy. No real Docker environment was
launched for this text-generation change. Whitespace and patch checksum checked.
Both intake items are acknowledged; the final mailbox check found no new mail.

Historical stopped-successor evidence remains recorded in the prior checkpoint;
it was not re-inspected and is not needed for this slice. Do not delete it without
verifying ownership/purpose. No session-owned containers or ports were created.
All GitHub integration remains owner-operated through the UI; Git delivery uses SSH.

## Open Threads

- Awaiting owner PR integration of the validated slice; source remains on maintenance.
- Awaiting workflow-improvements: fix the nested-directory coordination bug and
  decide the separately proposed diff-handoff rule. Use the root-cwd workaround.
- Preserved: 14-item triage, remaining legacy host-network issue, broader
  configuration evidence/docs, release sequencing and retired-outbox verification.
- Production blog deployment and incident-era exact host bytes remain unverified;
  no new live acceptance or cleanup is claimed.
- Deliberately not preserved: no transcript/session record; the received diff
  remains in intake history and coordination history after disposition.

## Workstream Document Index

- [Prior checkpoint record](2026-09-21-record-maintenance-before-component-upgrades.md): historical implementation, tests and graphical evidence; open only for those details.
- [Proposed bug triage](2026-09-21-note-proposed-bug-triage.md): open on resuming triage; not applied.
- [Pre-V1 assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): positioning input and owner Windows correction.
- [Early-adopter blog](../../blog/2026-09-21-why-try-devcapsule-before-v1.md): merged article and editorial follow-up.
- [Upgrade recovery contract](upgrade-recovery-contract.md): scope of the merged recovery fix.
- [Configuration contract](configuration-contract.md): lifecycle requirements relevant to future changes.
- [Correctness/test map](configuration-correctness.md): implementation evidence and coverage limits.
- [Intake decisions](intake-dispositions.md): outcomes of received mail.
- `intake/`: no pending items; both project-management messages acknowledged in the decision log.
