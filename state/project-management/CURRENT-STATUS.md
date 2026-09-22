# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-09-22 at owner request; synchronized with main; awaiting selection of the next coordination topic

Definition read: WORKFLOW.md@60772d54f11b, WORKFLOW-LOCAL.md@6a8a24825838

Branch association: `project-management/coordination`

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Goal

Own project-wide priorities, sequencing, cross-workstream dependencies and
lifecycle decisions. This reserved workstream remains open for the lifetime of
multiple-stream mode. Its immutable 2026-08-09 start predates the general rule;
the adoption exception remains recorded in the mainline registry.

## Current State

The owner explicitly returned this checkout from maintenance on 2026-09-22.
Maintenance was paused, committed, pushed and published first, with its bug
triage preserved. PR #125 integrated the run-image replacement at `f0d6901`;
PR #128 integrated model-first Codex attribution and the owner-validated bug
closure at `ca3f1d3`. Both deliveries were verified through fetched main, not
inferred from the owner's report alone. The legacy PyCharm network-default
bug remains with maintenance; the coordination data-loss fix remains with
workflow-improvements. The recovered mail and source patch are historical
custody evidence, not outstanding delivery tasks.

Merged current main `0d13111` into this published project-management branch.
Synchronization was required because the generic definition and local workflow
had changed. Read the new misplaced-patch handoff rule and commit-attribution
convention. Resolved the sole conflict in the registry mechanically: retained
main's other workstream rows and recorded this workstream's explicit resumption.
The existing blog instructions and design documents remain on this branch;
there was no source work to discard or transfer. Local and remote branch agreed
before synchronization. The legacy branch name is still registered; commands
use explicit `--workstream project-management` until the queued rename is done.

Read the prior status in full, its current and historical open threads, the
published live state, and all 21 pending intake items. No new mail was waiting,
and no open bug on main names project-management as owner. Reading the queue
is not a disposition. Older counts, delivery warnings and release claims in the
[prior status record](2026-09-22-record-prior-coordination-status.md) are historical;
reconcile them against current evidence when their topic is selected.

## Planned Next Step

The owner selects the next coordination discussion. The saved topic is
[V1 functionality areas and the WOW journey](2026-09-19-v1-wow-functionality-areas.md):
refine the grouping and map delivered work to remaining gaps. Other pending
choices include 0.2.14 release sequencing and early-adopter scope, release-runbook
alignment, component-upgrade operational objectives for V1, resource ownership,
and workflow migration. No release or implementation task was selected by this
workstream switch.

The run-image handoff is complete through PR #125, and the proposed diff-handoff
rule has landed through PR #126. They no longer block the next discussion.
The component-upgrades checkpoint and first hosted publication were already
accepted; R-UPGRADE-002 operational detailing remains that workstream's scope.
Reconcile older upgrade and adopter intake against those deliveries before
making a new scope decision. All 21 intake items remain for decisions here.

## Validation And External State

The synchronized runtime, tests, build scripts and GitHub Actions files are
byte-identical to fetched main. Reused this session's already passing full gate
on that implementation: 1,042 tests, 18 deselected, one existing xfail, mypy,
shell/CLI checks, local PEX build/smoke and nine packaged checks. This resumption
changes records only; whitespace and the merge were checked. No runtime or
release acceptance is newly claimed.

The Git author is Costin Cozianu and this session's recorded model is
`gpt-6-astra`; new commits use the integrated model-first Codex trailer. Git
uses SSH; all GitHub PR and publication operations remain owner-operated via UI.
Coordination commands run from the repository root with an absolute `--project`
as the recorded workaround for the unresolved nested-directory defect.
No containers, ports, host settings or submodules were changed during this switch.

## Open Threads

- Awaiting the owner: next coordination topic, V1 acceptance and release sequencing.
- Preserved: 21 undecided intake items; prior blog decisions and review; V1 scope
  proposals; component-upgrade operations; resource ownership and cleanup decisions.
- Branch rename and retired-outbox reconciliation remain queued. Inspect unlanded
  records before any deletion; no old branch was deleted during this switch.
- Historic host settings remain on `project-management/local-host-settings-20260915`;
  do not restore them over a newer lock without review. No restoration requested.
- Deliberately not preserved: no chat transcript or session record. Prior status
  was moved verbatim to a dated record so history no longer obscures current work.

## Workstream Document Index

- [Prior coordination status](2026-09-22-record-prior-coordination-status.md): full historical handoff, decisions, open-thread context and external-state claims; read when reconciling a specific prior topic.
- [Intake decisions](intake-dispositions.md): append-only outcomes; `intake/` contains the 21 pending items.

- [Diagnostic print-command and run-image retirement](2026-09-21-design-editable-project-launch.md): accepted simplified contract and maintenance implementation scope.
- [Design issue: V1 completeness and the WOW experience](2026-09-19-v1-wow-functionality-areas.md)
- [Why try DevCapsule? — promoted to the project README](../../../README.md)
- [Portfolio checkpoint 2026-08-15](2026-08-15-portfolio-checkpoint.md)
- [Portfolio checkpoint 2026-08-16](2026-08-16-portfolio-checkpoint.md)
- [V1 readiness assessment 2026-08-16](2026-08-16-v1-readiness-assessment.md)
- [V1 scope ledger](v1-scope-ledger.md)
- [Competitive comparison: promoted research
  (refreshed 2026-09-12)](../../design-notes/devcapsule/competitive-comparison.md)
- [Display transport options and clipboard policy
  2026-08-19](2026-08-19-display-transport-options.md)
- [The workflow versus Jira and GitHub Issues
  2026-08-19](2026-08-19-workflow-versus-issue-trackers.md)
- [Coordination backlog](coordination-backlog.md)
