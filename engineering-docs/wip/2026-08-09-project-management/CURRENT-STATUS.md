# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-09-22; owner release-fix propagation rule recorded; release runbook aligned; awaiting owner PR integration

Definition read: WORKFLOW.md@60772d54f11b, WORKFLOW-LOCAL.md@031c167690c0

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

Synchronized with main through `2c1a503` (PR #129), including the coordination
nested-directory and claim-preservation repair. Existing project-management
blog instructions and design documents remain on this branch. The legacy
branch remains registered; use explicit `--workstream project-management`.

The owner selected 0.2.14 release readiness, then challenged the generic
merge-only rule. The 2026-09-22 decision is now in `WORKFLOW-LOCAL.md` and the
canonical release runbook: main stays open; merge when suitable, otherwise
cherry-pick, adapt the correction, or establish that main is unaffected.
Record the inspected revisions and proportionate evidence with the bug.
Method selection needs no further owner approval. Git topology alone is not
proof that the correction works. The same judgment permits selective transfer
of a main-first fix onto the release line.

The decision changes propagation methods. Existing before-each-candidate timing
is retained; the optional timing question has not received a separate owner
decision. An unresolved main bug still needs an explicit owner decision before
deferral. The existing candidate gate accepts ancestry/patch equivalence;
adapted or unaffected-main outcomes use its existing evidence record under the
standing owner direction. No release gate implementation changed.

Acknowledged the 2026-09-16 runbook-alignment intake: the guide now follows
current release branch selection, driver and version rules, with the owner's
new propagation rule superseding the intake's merge-only instruction. The
remaining 20 intake items are undecided; the maintenance-release and branch
migration items still need their other requested coordination decisions.
Generic-rule revision was delivered to workflow-improvements as
`2026-09-22-project-management-release-fix-propagation.md` on coordination commit
`5d47a901d22d`; that includes clarifying routing for selective mainline delivery.
No other workstream's records or generic workflow source were edited.

## Planned Next Step

Integrate the prepared project-management documentation through the owner's
GitHub UI PR. Then finish 0.2.14 readiness: confirm the driving workstream and
scope, reconcile release-blocking bug triage with its owner, and establish
validation/acceptance for the chosen cut. Maintenance is the proposed driver;
no release branch or tag has been created and the cut remains unselected.
The generic-definition correction is with workflow-improvements; the owner's
local exception makes the new propagation methods usable in this project now.

The saved V1 functionality/WOW discussion, operational objectives, resource
ownership, and workflow migration remain queued. The run-image and authorship
fixes are integrated; neither is an outstanding release dependency.

## Validation And External State

The required `.venv/bin/python -m nox -s build` passed on the synchronized
source: 1,045 tests, 18 deselected, one existing xfail, mypy across 167 source
files, shell/CLI checks, local PEX build/smoke and nine packaged checks. Reviewed
the guide against the release gate implementation and checked whitespace. The
working-tree build produced the local validation artifact; no release artifact
or downloaded-candidate acceptance is claimed by these documentation changes.

The Git author is Costin Cozianu and this session's recorded model is
`gpt-6-astra`; new authored commits use the model-first Codex trailer. Git uses
SSH; all GitHub PR and publication operations remain owner-operated via UI.
Coordination commands ran from the repository root with an absolute `--project`;
the nested-directory repair is now on main, but these commands do not constitute
its next real nested-directory acceptance run. No containers, host settings or
submodules were changed.

## Open Threads

- Awaiting the owner: review/integration of this branch, 0.2.14 driver and scope,
  and eventual release-cut instruction. Existing per-candidate main disposition
  timing remains operative unless the owner changes it.
- Awaiting workflow-improvements: replace the generic merge-only prohibition
  with the evidenced outcome rule and clarify selective-delivery routing.
- Preserved: 20 undecided intake items; prior blog decisions and review; V1 scope
  proposals; component-upgrade operations; resource ownership and cleanup decisions.
- Branch rename and retired-outbox reconciliation remain queued. Inspect unlanded
  records before any deletion; no old branch was deleted.
- Historic host settings remain on `project-management/local-host-settings-20260915`;
  do not restore them over a newer lock without review. No restoration requested.
- Deliberately not preserved: no chat transcript or session record. Prior status
  remains in the dated historical record; canonical policy is in the local
  workflow and release runbook.

## Workstream Document Index

- [Prior coordination status](2026-09-22-record-prior-coordination-status.md): full historical handoff, decisions, open-thread context and external-state claims; read when reconciling a specific prior topic.
- [Intake decisions](intake-dispositions.md): append-only outcomes; `intake/` contains the 20 pending items.

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
