# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-09-22; release policy integrated in PR #124; 0.2.14 readiness assessed; maintenance selected as driver; scope/triage and cut instruction pending

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

PR #124 is verified on fetched main at `388ee50`; this branch fast-forwarded
to it. The merged tree is identical to the previously validated `f87c110` tree,
so the full gate result remains applicable. No new mail or PM-owned open bugs
were found. No `release-0.2.14` branch or `v0.2.14*` tag exists on the remote.

Finish 0.2.14 readiness: record the release scope, reconcile release-blocking bug triage with its owner, and establish
validation/acceptance for the chosen cut. The owner selected maintenance as the 0.2.14 driver on 2026-09-22;
no release branch or tag has been created and the cut remains unselected.
The generic-definition correction is with workflow-improvements; the owner's
local exception makes the new propagation methods usable in this project now.

The owner requested the open-bug inventory before proceeding. Maintenance
was assigned the release-driving task by coordination mail
`2026-09-22-project-management-drive-0-2-14-release.md`. This checkout remains
in project-management for the requested inventory; assigning a driver did not
create the release branch or change individual bug targets/severities.

The bounded readiness review found 18 nonterminal bug records: eight fixed,
six confirmed and four reported; 16 remain untriaged. Counts are not blockers.
Maintenance's saved triage already proposes closing the integrated configuration
fixes on existing owner/graphical acceptance. Its older run-image networking
recommendation is superseded; the separate legacy `pycharm run` host-network
default remains confirmed and needs an explicit 0.2.14 disposition. Candidate
acceptance should exercise predecessor configuration recovery, actual launch,
`project run --print-command`, and nested-directory coordination preservation.

Before RC0, reconcile the remaining old branch associations under the existing
migration deadline. Some renamed remote refs already exist, so inspect each
owner's state before renaming anything; this review changed no branch names.
This is a pre-candidate requirement, not a reason to delay the stabilization
branch. Routine version bump, build and candidate acceptance happen in the
release process. The generic workflow correction and unrelated V1 backlog need
not delay the cut because the local owner exception is already integrated.

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

- Awaiting the owner: 0.2.14 scope and bug dispositions,
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
