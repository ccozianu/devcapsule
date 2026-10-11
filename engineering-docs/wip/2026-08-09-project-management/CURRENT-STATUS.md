# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-10-11; ecosystem bootstrap moved to 0.9; project-operation instructions assigned to workflow-improvements for 0.3.0; approved intake dispositions retained

Definition read: WORKFLOW.md@2b576adb1a40, WORKFLOW-LOCAL.md@7362bae8ec82

Branch association: `ws-project-management/coordination`

Integration target: `main`

Delivery method: pull request for deliverables; records published on coordination

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Goal

Own project-wide priorities, sequencing, dependencies and lifecycle decisions.
This reserved workstream remains open for the lifetime of multiple-stream mode.
The immutable start date and adoption exception remain in the workstream list.

## Current State

The owner confirmed the proposed 23 dispositions on 2026-10-09, then directed
closure of the obsolete Stage 7 resource-convention request with no action.
The owner then prioritized the separate persistent-diagnostics request for
active implementation planning, targeted ready for 0.3.0. On 2026-10-10 the owner postponed agenda items 7, 8 and 12 until before V1,
tentatively 0.9, explicitly outside 0.3.0. The owner also dropped Pagefind catalog inclusion and required a portable
website dependency handoff. Thirty messages are closed in the same commit as their appended log entries: 29 acknowledgements and one dropped
request. Eight original messages remain undecided; one new testing-policy
reconciliation message is received and pending separately.
Closing an intake does not complete retained implementation or acceptance work.

The next release is **0.3.0**, by the owner's unconditional 2026-10-05
ruling. Current planning uses that name. Historical references and the source
version 0.2.16.dev0 remain unchanged. Scope, driver and cut still need decisions.
The [current proposal](2026-09-27-0216-release-planning.md) separates accepted
commitments from proposals; its historical filename is retained.

### Latest Decision: Project Operations Now, Bootstrap At 0.9

Owner decision, 2026-10-11: ecosystem-aware project bootstrap moves from
0.3.0 to 0.9, dependent on project-type templating. Project tools should be on
PATH throughout the capsule by default; exceptional project types may require
`devcapsule project shell` to activate them. The examples include Java/Maven,
Scala/sbt, Python/nox, Node/npm and Node/Yarn. The [complete decision](2026-10-11-decision-project-operations-and-bootstrap.md)
preserves the scope and the distinction from earlier agenda item 7.

For 0.3.0, the agent must know how to build, run each test tier and selective
tests, run the default program, debug it, and explain debugger attachment.
WORKFLOW.md must require this continuing responsibility. WORKFLOW-LOCAL.md
must hold each project's actual instructions, established and maintained with
the human even when all execution is delegated to the agent. This is assigned
to workflow-improvements; the testing-policy intake remains separately undecided.

Delivered the full decision to maintenance as
`2026-10-11-project-management-bootstrap-target-09.md` at coordination
`133a049ad96e`, and to workflow-improvements as
`2026-10-11-project-management-project-operation-instructions-030.md` at
`c878496a5533`. Maintenance owns updating the canonical bug and its plate;
workflow-improvements owns rule implementation. Neither recipient's source or
status file was edited here. The new rule and shell command are not claimed
implemented. The templating dependency's implementation owner remains open
for 0.9 planning.

### Reasons for closing the 23 messages

| Messages | Decision and evidence |
|---|---|
| Blog establishment and review (2) | Local blog rules, the repository blog and website publication mechanism exist. The broken PUBLISHING.md link is resolved. Optional editorial suggestions are not outstanding obligations. |
| Display delivery (1) | v0.2.12 acceptance and the delivery notice establish the contained desktop; the V1 ledger is ratified. Display follow-ups remain separate. |
| Maintenance ownership (1) | Workflow and runbook already assign maintenance releases and bug triage; no repeated owner decision is needed. |
| Branch migration (3) and definition notice (1) | Active workstream rows use ws-prefixed branches; this workstream publishes to coordination, has no old outbox ref and has read the current definition. The old deadlines and instructions are historical. |
| Configuration decisions, assignment and delivery (3) | R-CONFIG-001 and PR #170 at 6ae1a01 establish the accepted contract and integration. Rollout and recovery limits remain; integration does not prove host restart. |
| IntelliJ/Playwright delivery (1) | PR #170 integrated the slice. The separate Playwright host-restart acceptance condition remains with component-catalog. |
| Release rename (1) | Owner ruling fixes 0.3.0 unconditionally, without choosing the driver or cut. |
| Configuration presentation (2) | Both owner rulings are accepted: recorded schema controls listing; pinned, newer and overridden base choices must be clear. Retained in the coordination backlog for the upgrade design, not claimed implemented. |
| First-session UX (1) | New base naming covers the old RC-label complaint; maintenance's published 0.3.0 plate retains terminal presentation and normal Ctrl+C handling. |
| Status reliability (1) | Accepted R-UPGRADE-002 already belongs to component-upgrades; preserve wanted V1 work and operational choices without adding a gate. |
| Legacy capabilities (1) and user-docs proposals (1) | The owner already mandated these decision gates. The ledger and release proposal preserve them; their individual product choices remain open. |
| Release notes (1) | Notes, backfill and runbook obligations are adopted; maintenance's 0.3.0 plate retains automation. |
| Consent (1) | The owner explicitly assigned D-0011 through D-0013 to the next release, now 0.3.0. Do not ask whether it is in scope again. |
| IDE files (1) | The repository ignore policy is decided. Project-management retains execution without deleting local files; no IDE edits are included in this reconciliation. |
| Forced configuration (1) | Maintenance holds the accepted behavior. Exact interface and mandatory-guarantee reconciliation remain design work, not an unresolved adoption vote. |

### Obsolete Stage 7 request closed

The owner identified the old plan as out of sync with development and directed
its closure. The 2026-09-21 forwarded convention request itself confirms that
Stage 7 was dissolved on 2026-08-27 and explicitly retired on 2026-09-21.
It is dropped with no task, reminder or new workstream. Existing maintenance
bugs and any retained-resource constraints are separate and unchanged.

The previous grouping with persistent diagnostics was misleading. That proposal
arose from the owner's 2026-10-08 noVNC disconnect and requests persistent,
bounded logs. The owner clarified that it is urgent and must enter active
implementation planning targeted ready for 0.3.0. Its intake is acknowledged;
the complete proposal is preserved in the [assigned work order](../../work-orders/2026-10-08-persistent-session-diagnostics.md).
Candidate C21 is active, priority wanted. The owner assigned implementation to
maintenance on 2026-10-11: reliable logs are a prerequisite for maintenance to
diagnose and fix failures. Maintenance owns the needed supervisor/display,
launcher and IDE logging work, scopes the bounded release slice and acceptance,
and coordinates the existing C10 terminal/shutdown work. Ownership does not
wait on contained-display's lifecycle. Detailed engineering recommendations
remain subject to scoping; no implementation completion is claimed.

Delivered the complete work order to maintenance as
`2026-10-11-project-management-maintenance-persistent-diagnostics.md` at
coordination `a535ccf3a44e`. Maintenance acknowledged it. A fresh main fetch
verified the logging/rotation stack merged through PR #209 at 26fdc6a;
snapshot/export and browser evidence remain in its published plan. Older
acceptance evidence does not automatically establish the later rotation design.

### Pagefind catalog proposal closed; website handoff delivered

Owner direction, 2026-10-10: Pagefind belongs in the website's npm dependencies
when search is implemented. The /opt/xtras installation was a temporary
experiment, not a portable build prerequisite. Current package.json and build
script inspection found no Pagefind integration; this is not a claim of an
existing production dependency. Playwright's delivered component is separate.

Delivered `2026-10-10-project-management-pagefind-project-dependency.md` to
website at coordination `5b05eeecda11`. The handoff asks that website record
this in its independent project's W10 work: pinned npm devDependency and
lockfile, project-local build invocation, generated static assets, and a
fresh-checkout build/browser check without global Pagefind or /opt/xtras.
Indexing must preserve the build's atomic publication behavior. No new search
schedule or implementation was authorized. The original combined intake is
closed; implementation and acknowledgement of this new handoff belong to website.

### Retained work and when to revisit it

The [coordination backlog](coordination-backlog.md#accepted-work-retained-after-intake-closure)
records the accepted configuration-presentation, reliability and IDE-file work.
The release proposal records 0.3.0 obligations, and the V1 ledger records the
legacy-capability gate. These are the homes of the work; the intake log is the
receipt. Do not duplicate those receipts as questions on every resumption.
A later priority must not weaken either existing release gate.

Delivered the configuration-presentation requirements and confirmed consent/
reliability commitments to component-upgrades as
`2026-10-09-project-management-accepted-upgrade-followups.md` at coordination
`387656fed15e`. No implementation priority or new release gate was assigned.

The seven-item Karpathy list remains closed. The console work order remains
with capsule-webconsole in its separate checkout. Main includes subsequent
console integrations through PR #201; the earlier published second-iteration
handoff is historical. This reconciliation does not claim owner acceptance
of further console work.

## Planned Next Step

Follow the two delivered scope decisions in recipient publications. Bootstrap
is excluded from 0.3.0; the project-operation instruction rule is included.
Maintenance continues the remaining diagnostics slices and acceptance.
Project-management resumes final release scope and ship criteria with the owner.
The broader critical path remains
0.3.0 scope, driver and cut, and the eleven user-docs proposals. The release
name, consent inclusion, release-notes adoption and the two decision gates are
already settled. Do not present them as open product decisions.

Items 7 (mycodespace/checkout naming), 8 (OpenCode evaluation) and 12 (routine
documentation cleanup) are recorded in the [pre-V1 backlog](coordination-backlog.md#pre-v1-work-tentatively-09-excluded-from-030).
They are explicitly outside 0.3.0. Revisit at 0.9 or the final pre-V1 planning
cycle, whichever comes first; do not raise them during ordinary 0.3.0 planning.

The eight remaining intake messages form the following groups, not another
38-item review after the older agenda:

| Group | Messages | Remaining work |
|---|---:|---|
| Upgrade design | 3 | Experience, automated component validation and claims from experiments; one design discussion. |
| Configuration and recovery | 3 | init/config boundary, internal generation vocabulary and launcher-bootstrap recovery; reconcile with the newer contract first. |
| Product direction | 2 | Two adopter/blog inputs; separate delivered positioning from unsettled choices. mycodespace/checkout naming is in the pre-V1 backlog. |

Do not implement or disposition these eight under the earlier approvals.
The [prior handoff](2026-10-09-record-before-intake-reconciliation.md) preserves
older context, including the lifecycle question for contained-display and
sample-projects. Neither lack of a live publication nor this cleanup closes them.

## Validation And External State

For this records-only scope checkpoint, main is at 61396e8. Its newer changes
do not touch the selected PM records or change WORKFLOW.md/WORKFLOW-LOCAL.md.
Synchronization is deferred to the next implementation boundary; no source or
other workstream's records are edited. Mail was empty at entry. No new project-
management bug or intake disposition is created by the owner's direct decision.
The scope checkpoint's full build gate passed: 1,498 runtime tests, 17
packaged integration tests and 290 web-console tests, plus type, syntax,
smoke and documentation-contract checks. The runtime suite retained one
xfail and one XPASS, with 35 deselected. Changed-document links and whitespace
passed; both delivered items byte-match the prepared decisions. The final
mail take returned no items. No container or service was started.


The approved records were committed and pushed as 9139717 after the initial
main merge 263f5d0. The checkpoint then merged origin/main at 435d3d4;
its only conflict was the root workstream list. Resolution preserves the
current project-management row and main's rows for every other workstream.
The new workflow topic 8.8 on human decision handoffs and the accompanying
AGENTS.md instruction have been read. No product decision changed in the merge.
The updated local gate includes the separate web-console session. No mailbox
items waited at the reconciliation entry and no open bug is owned by
project-management. On 2026-10-11 one new item was taken into intake:
`2026-10-10-capsule-webconsole-reconcile-testing-approach-with-practice.md`.
It is additional to the eight original intake items and remains undecided.
It asks for a project-wide testing-policy reconciliation; no policy change or
release target is inferred from receipt.
The known manifest/definition version mismatch is unchanged; this records pass
does not refresh the workflow or edit project configuration.

The required build gate passed again after merging main at 435d3d4:
1,498 runtime tests, 35 deselected, one xfail and one XPASS; all 17 packaged
integration tests, type checks, syntax, source/PEX smokes and the 184-page
documentation contract passed. The separate web-console session passed its
type check and 290 tests. Both nox sessions succeeded in about three minutes.
No container or service was started. The dirty-tree validation artifact is
`dist/devcapsule-local.pex`; this checkpoint does not produce a release artifact.
The final mailbox check found no waiting mail.
Record checks establish exactly 30 deletions and unique appended dispositions
(29 acknowledgements and one drop), eight byte-identical remaining messages, the
diagnostics proposal retained with the owner's subsequent assignment, both historical records preserved verbatim,
resolved links in changed documents and only this workstream's list row edited.
A pre-existing broken ledger link was corrected to its current engineering home.

The owner identified the current session as GPT-6 Astra on 2026-10-11.
Commits retain the human author and credit GPT-6 Astra Codex. This is a
session-specific attribution, not a model default for future sessions.
Pre-existing or IDE-generated .idea edits remain outside the checkpoint.
The selected workstream has not changed.
The owner requested regular commits and pushes on 2026-10-11. Checkpoint each
completed decision batch instead of accumulating several batches uncommitted.

## Open Threads

- Awaiting the human: next bounded decision begins with 0.3.0 release scope and ship criteria unless the owner chooses another
  slice; maintenance now owns diagnostics implementation. The eight remaining messages are not yet approved for disposition.
- Weighed and unresolved: the older local GitHub UI-only rule versus scoped gh
  grants, workflow-rule stewardship, and timing of humane-view dependencies.
  These are preserved context, not questions to repeat during unrelated work.
- Deliberately not preserved: no transcript, new feature experiment or automatic
  reminder service. Historical handoff and release proposal are retained verbatim.

## Workstream Document Index

- [Project operations for 0.3.0; ecosystem bootstrap for 0.9](2026-10-11-decision-project-operations-and-bootstrap.md): accepted owner decision, default PATH and exceptional project shell direction, and continuing agent responsibility for project instructions.

- [Persistent session diagnostics work order](../../work-orders/2026-10-08-persistent-session-diagnostics.md): C21 assigned to maintenance on 2026-10-11, targeted ready for 0.3.0; bounded scope and acceptance remain.

- [Handoff before intake reconciliation](2026-10-09-record-before-intake-reconciliation.md): verbatim historical status; read for prior decisions and open-thread context.
- [Prior release proposal](2026-10-09-record-prior-release-proposal.md): verbatim 0.2.16-era proposal before the 0.3.0 reconciliation; historical recommendations, not current scope.

- [Work order: the website from the visitor's chair](../../work-orders/2026-09-28-website-visitor-experience.md) and [work order: visitor content and producer migration](../../work-orders/2026-09-28-visitor-content-and-producer-migration.md): issued 2026-09-28.
- [The content–website contract, version 1](../../specifications/product/content-website-contract.md): accepted 2026-09-28, promoted to the specifications on 2026-09-30; the website's `CONTRACT.md` is the authoritative text.
- [Design issue: the documentation is current when a release drops](2026-09-28-design-docs-current-at-release.md): historical design discussion; the contract and work orders record the subsequent decisions.
- [0.3.0 planning proposal](2026-09-27-0216-release-planning.md): current 0.3.0 commitments and remaining release decisions; historical filename retained.
- [Design issue: consent that means something](2026-10-01-design-consent-and-vendor-trust.md): historical problem statement; consent decisions are D-0011 through D-0013 and assigned for 0.3.0.
- [0.2.15 environment discovery work order](../../work-orders/2026-09-27-project-environment-discovery.md): approved xtras/info/agent-defaults scope, guard deferral and acceptance checks.

- [0.2.14 release overview](../../releases/v0.2.14/README.md): maintained release checklist and evidence.
- [0.2.14 bug triage](../../releases/v0.2.14/bugs.md): release dispositions and next actions; canonical bug records remain linked.

- [Prior coordination status](2026-09-22-record-prior-coordination-status.md): full historical handoff, decisions, open-thread context and external-state claims; read when reconciling a specific prior topic.
- [Intake decisions](intake-dispositions.md): append-only outcomes; `intake/` contains eight original undecided items plus the new testing-policy reconciliation, after 29 acknowledgements and the Stage 7 closure.

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
