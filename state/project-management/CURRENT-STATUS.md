# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-09-26; resumed at owner direction after 0.2.14 shipped; 0.2.15 registered under maintenance for the blocking init bug; 25 undecided intake items

Definition read: WORKFLOW.md@df81c25a0f2a, WORKFLOW-LOCAL.md@5b4a80ae583e

Branch association: `ws-project-management/coordination` (renamed from `project-management/coordination` by the owner-directed migration on `main`, commit `4827ade`)

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

## Release 0.2.15 (decided 2026-09-26)

The owner's first-session attempt with the released 0.2.14 launcher hit a
show stopper: `project init` discards every interactive answer when a
`--authorize` name is unknown, filed as
[the init bug](../../bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md),
owner maintenance, severity blocking, target 0.2.15. The owner ruled the same
day: no fourth version number; fix it and release 0.2.15. This decides the
first ask of maintenance's 0.2.15 plan:

- 0.2.15 is a maintenance release driven by `maintenance`, cut from `main`
  under *Taking A Release Over*, containing this fix and nothing else.
- The release ships when the fix is verified on a candidate; the fix is
  the gate.
- Owner ruling, same day: everything else named for 0.2.15 moves to
  0.2.16. That is the cleanup and optimization list from the 2026-09-25
  plan, its five candidates, the IDE-surface wish (maintenance estimates
  only IntelliJ fits a week and recommends none), and the release-notes
  artifact proposal. 0.2.16 is not yet registered; its driver and scope
  are the next planning decision.

Delivered to maintenance by mail on 2026-09-26; the acknowledgement is in
the decision log.

## Claim Test Quarantine (2026-09-22)

The owner reported inconsistent CI results at one revision for the claim
lifecycle test. A disposable-local-remote probe confirmed the assertion depends
on two real-clock calls remaining in the same second. On explicit owner
instruction, this release-readiness slice marks the existing test non-strict
xfail without changing its assertions or runtime behavior. The owner rejected
a quick fix and requested review of the testing approach. The confirmed minor
bug is `engineering-docs/bugs/devcapsule/2026-09-22-workflow-claim-test-flakiness.md`,
owned by workflow-improvements, with no release target yet. Its scope is the
claim/renewal/expiry contract and reliable tests; the combined test's assertion
coverage is temporarily quarantined. This adds one bug to the earlier inventory
(19 nonterminal records now). The full build passed: 1,044 tests passed,
18 deselected, one existing xfail and this test XPASS; mypy and nine packaged
checks passed. The owner-requested marker is the only test/source change;
no quick repair was made. Bug/design handoff delivered by coordination mail
`2026-09-22-project-management-claim-test-design.md` at `f263535437cb`.
The marker and bug await owner PR integration.

## Planned Next Step

Resumed 2026-09-26 on `ws-project-management/coordination`, synchronized with
`main` at `f4949aa` (v0.2.14 published 2026-09-25; `main` reopened at
0.2.15.dev0). The definition text is unchanged since the last read apart from
its version line; `WORKFLOW-LOCAL.md` gained the dogfooding CLI selection,
local launch networking and the deferred rename deadline, all read.

Six mailed items were taken on resume and joined the 20 already in `intake/`;
the 0.2.15 plan is decided, 25 remain. The first decisions to put to the owner, in order:

1. Done 2026-09-26: 0.2.15 registered with maintenance as driver, the
   blocking init bug its only content; see *Release 0.2.15* above. The rest
   of that plan is 0.2.16 material: register 0.2.16 with the owner once
   0.2.15 is out, sequencing the cleanup candidates and ruling on surfaces.
2. Release notes as a release artifact
   (`2026-09-26-maintenance-release-notes-artifact.md`): adopt into the
   runbook and the 0.2.15 plan or not.
3. The mycodespace design note and checkout-naming default
   (`2026-09-25-maintenance-mycodespace-and-checkout-naming.md`).
4. The V1 gate on legacy launch capabilities
   (`2026-09-22-maintenance-v1-legacy-launch-capabilities.md`): acknowledge
   into the V1 scope ledger.
5. The two branch-migration items from 2026-09-22 are overtaken by the
   migration `main` carried on 2026-09-25; decide them as acknowledged with
   the remaining cleanup named.

Then the 20 older intake items, oldest first, and the queued V1
functionality/WOW discussion. Legacy branch migration is done for the active
workstreams; `eclipse-surface` has no branch yet.

The previous planned next step, the handoff of the 0.2.14 cut to maintenance,
completed: PR #131 was the baseline, maintenance cut and published 0.2.14.

## Validation And External State

Release-workspace setup changes documentation only; relative links, all 19 bug
rows against committed metadata, and whitespace were checked. Reuse the full
build result recorded above for the unchanged runtime/test tree. A pre-existing
working-tree edit changed the Codium sudo bug's opening delimiter from `---`
to `--`. Before switching workstreams, preserved its exact diff in
`.git/codex-preserved-codium-sudo-edit.patch` and restored the committed file
for a clean switch. The edit can be recovered with `git apply` of that patch;
it has not been incorporated into release source.


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

- Handed to maintenance: approved 0.2.14 cut, progressive bug triage and
  candidate acceptance. No current bug blocks starting stabilization.
- Awaiting workflow-improvements: review and repair the quarantined claim test
  under its temporal contract; replace the generic merge-only prohibition
  with the evidenced outcome rule and clarify selective-delivery routing.
- Preserved: 20 undecided intake items; prior blog decisions and review; V1 scope
  proposals; component-upgrade operations; resource ownership and cleanup decisions.
- Branch rename and retired-outbox cleanup were done by maintenance on `main` (2026-09-25); the two 2026-09-22 migration intake items await their closing decision. Inspect unlanded
  records before any deletion; no old branch was deleted.
- Historic host settings remain on `project-management/local-host-settings-20260915`;
  do not restore them over a newer lock without review. No restoration requested.
- Deliberately not preserved: no chat transcript or session record. Prior status
  remains in the dated historical record; canonical policy is in the local
  workflow and release runbook.

## Workstream Document Index

- [0.2.14 release overview](../../releases/v0.2.14/README.md): maintained release checklist and evidence.
- [0.2.14 bug triage](../../releases/v0.2.14/bugs.md): release dispositions and next actions; canonical bug records remain linked.

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
