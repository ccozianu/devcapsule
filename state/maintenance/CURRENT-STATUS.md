# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused at owner request for the new component-upgrades workstream

Definition read: WORKFLOW.md@ee9065a1b3ab, WORKFLOW-LOCAL.md@488eed5a6c05

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `ws-maintenance/triage`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

The owner explicitly requested rebasing maintenance on origin/main, opening
`component-upgrades`, and preparing its work order for a fresh session.
Rebased onto `e4a96dc`; all prior maintenance content was already integrated,
so no commits needed replay. PR #117 merged the configuration fixes; PR #120
merged the early-adopter blog, positioning note, and proposed triage. The blog
has not been independently verified as deployed to the production website.

The owner said the 14-item bug triage makes sense but suspended it before
applying ratings/dispositions. Bug frontmatter remains unchanged: 14 open
maintenance records, including the two merged configuration fixes still marked
fixed. The saved proposal identifies a current major `run-image` host-network
problem; no repair is included in the upgrade workstream by default.

The subsequent owner agreement selects a component-upgrade feature for
0.2.14: generic component distribution channels, exact version sets, voluntary
unvalidated sets, developer-owned selections, rollback, and optional upstream
PR preparation. The new workstream owns its implementation and work order;
maintenance's proposal and historical evidence remain here.

## Planned Next Step

On an explicit return to maintenance, resume the saved triage, apply the settled
ratings/dispositions with evidence, then let project-management sequence the
remaining release work. Do not resume maintenance automatically after the
upgrade feature. Retired-outbox verification/deletion remains accepted follow-up.

## Validation And External State

The last completed gate passed 917 tests, one existing xfail, 18 deselected,
mypy and nine packaging tests. The blog website build checked 19 pages and
646 links/assets/anchors. The source tree has not changed in this rebase;
only the merged records and coverage badge advanced. A new shared gate is
running for the fresh-session work-order handoff, with results to be recorded
by the selected new workstream. No source edits or container launches were
made for this transition. Mail retrieval found no maintenance mail.

The stopped graphical successor and run-owned acceptance evidence are recorded
in the historical checkpoint; they were not re-inspected during this paperwork
transition. Do not delete them without verifying their ownership and purpose.

This checkpoint and record are pushed on maintenance and published live; they
will reach main with a later ordinary delivery, without a records-only PR.

## Open Threads

### Awaiting The Human

- Resume and finalize bug triage; the proposed closures/retirements are not applied.
- Project-management shapes the complete 0.2.14 scope and release sequencing.
- Blog production publication is separate from the merged article.

### Weighed And Unresolved

- Broader configuration coverage and permanent developer documentation remain.
- Workstation overlays, relocation and historical-recipe policy are outside the
  completed correction. Serialized configuration access remains the owner's
  precondition; no new locking protocol is implied.
- Exact incident-era host configuration bytes remain unavailable. Recorded
  regression and graphical-successor evidence must not be overstated.
- Retired outbox refs require verification before removal.

### Deliberately Not Preserved

No verbatim conversation export was requested. The prior status is preserved
verbatim in the dated record; the saved triage, assessment, blog, and new upgrade
work order hold the substantive outcomes. Discarded wording is not a requirement.

## Workstream Document Index

- [Prior checkpoint record](2026-09-21-record-maintenance-before-component-upgrades.md): historical implementation, tests and graphical evidence; open only for those details.
- [Proposed bug triage](2026-09-21-note-proposed-bug-triage.md): open on resuming triage; not applied.
- [Pre-V1 assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): positioning input and owner Windows correction.
- [Early-adopter blog](../../blog/2026-09-21-why-try-devcapsule-before-v1.md): merged article and editorial follow-up.
- [Upgrade recovery contract](upgrade-recovery-contract.md): scope of the merged recovery fix.
- [Configuration contract](configuration-contract.md): lifecycle requirements relevant to future changes.
- [Correctness/test map](configuration-correctness.md): implementation evidence and coverage limits.
- [Intake decisions](intake-dispositions.md): outcomes of received mail.
- `intake/`: pending work; currently only its README.
