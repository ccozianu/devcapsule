# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active; releasing 0.2.14; owner-approved cut created; initial build and PR delivery in progress

Definition read: WORKFLOW.md@60772d54f11b, WORKFLOW-LOCAL.md@0f44773f837c

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `release-0.2.14`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

The owner directed starting the release under maintenance on 2026-09-22:
fix or defer bugs as stabilization proceeds; none of the currently listed bugs
is a showstopper for starting. This does not close bugs or silently assign
individual release targets. Work is tracked in the
[release overview](../../releases/v0.2.14/README.md) and
[bug triage table](../../releases/v0.2.14/bugs.md), not repeated chat inventories.

Cut `release-0.2.14` at preparation merge
`21371084f7137624aed6c0581b12495a04b04fbb` (PR #131), containing the release
working documents and claim-test xfail. Fetched main `c8ae736` differs only in
its later generated coverage badge. All maintenance implementation was already
integrated. Its remaining private checkpoint was records only: synchronized
it with main by rebase, resolved the registry conflict by retaining other
mainline rows, and carried its own attribution checkpoint/status into the
release branch. No source patch was omitted or duplicated. The old working
branch is now closed for modification; release source will not be rebased.

The first release commit sets source version 0.2.14 through the existing bump
command and registers maintenance as the release driver. Took and acknowledged
both project-management handoffs in the same commit as their deletion. Mailbox
and intake are empty. Claim-test design repair stays with workflow-improvements;
its xfail is integrated. The run-image and attribution fixes are integrated.
The nested-directory coordination repair is integrated and awaits applicable
live/RC acceptance, rather than implementation.

## Planned Next Step

Complete the release-source build, push the release branch, then deliver its
initial preparation PR for the owner's GitHub UI merge. Before RC0, verify
main contains the applicable release delta and reconcile the legacy branch-name
migration with project-management. Work through fixes, closure evidence and
explicit deferrals in the release bug table during stabilization. Candidate
acceptance uses the downloaded artifact and the checklist in the overview.
Do not tag an RC before the current main-disposition gate is satisfied.

## Validation And External State

Initial release build is pending. Baseline implementation passed the prior
full build with 1,044 tests, one xfail and this claim test XPASS, mypy and nine
packaged checks; a release-source build is still required after the bump.
No candidate tag, release acceptance JSON or final tag has been created.
GitHub PR operations remain owner-operated through the UI; Git pushes use SSH.

Project-management was paused and published before this switch at source
checkpoint `c5a011d`. Its own row and pause record reach main through its next
ordinary integration; published state is the live handoff. A pre-existing
one-character Codium sudo bug edit was preserved as
`.git/codex-preserved-codium-sudo-edit.patch` before the clean switch; it is not
part of the release. No containers, host settings or retained evidence were
changed. No transcript/session record was requested.

## Open Threads

- Initial release build and owner PR integration; then RC0 and artifact acceptance.
- Resolve or explicitly defer bugs as work proceeds; none of the current list
  blocks the cut under the owner's ruling. Their individual records remain open.
- Project-management retains legacy branch migration coordination before RC0.
- Workflow-improvements owns claim-test design repair and the generic release
  propagation rule revision; the local owner exception already governs here.
- Preserve the old maintenance triage, configuration contracts and validation
  limits, retired-outbox follow-up, and historical host/blog acceptance gaps.
- The preserved local delimiter edit can be restored with `git apply` of the
  patch above if the owner wants it. It was not corrected or discarded silently.

## Workstream Document Index

- [Release overview](../../releases/v0.2.14/README.md): cut, candidates and acceptance checklist.
- [Release bug triage](../../releases/v0.2.14/bugs.md): maintained dispositions and evidence.

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
