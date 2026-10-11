# Release 0.3.0: Planning Proposal

Opened: 2026-09-27 as the 0.2.16 proposal. Reconciled: 2026-10-11.
Owner: `project-management`.

Status: accepted decisions recorded below; the complete scope, release driver
and cut trigger remain proposed. The owner confirmed the 23 intake dispositions
on 2026-10-09. This is not authorization to cut or publish a release.
The [prior proposal](2026-10-09-record-prior-release-proposal.md) is retained
verbatim for history; its superseded recommendations do not govern this plan.

## Accepted Direction

The next release is unconditionally **0.3.0**, by owner decision of 2026-10-05.
Do not reopen that choice or rewrite historical release identities. Source
remains at 0.2.16.dev0 until the release version step under the local scheme.

- IntelliJ is accepted and the component-catalog slice, including Playwright
  and the configuration contract, reached main through PR #170 at 6ae1a01.
  The Playwright host-restart confirmation and downloaded-candidate acceptance
  are separate from integration.
- R-CONFIG-001 is accepted, with component-catalog's implementation integrated.
  Mandatory guarantees, personal selections and recovery remain contractual.
  No self-hosting migration or host-launcher replacement follows from this record.
- Consent under D-0011, D-0012 and D-0013 is assigned to component-upgrades for
  the next release, now 0.3.0. Its published next task is implementation.
- Maintenance's published 0.3.0 plate retains fresh-workspace E2E, in-capsule
  commands, named contexts, reuse/reaping design, network authorization,
  first-session UX and release notes/gate tooling. The owner's 2026-10-11
  decision moves ecosystem bootstrap to 0.9, after project-type templating.
- For 0.3.0, workflow-improvements must make project-operation instructions
  a continuing agent responsibility: build, separate test tiers and selective
  tests, default program execution, debugging and debugger attachment. The
  generic rule belongs in WORKFLOW.md; each project's commands belong in
  WORKFLOW-LOCAL.md, established with the human and kept current even when all
  execution is delegated. See the [accepted decision](2026-10-11-decision-project-operations-and-bootstrap.md).
- Maintenance retains the accepted forced-configuration preview/run follow-up.
  Command spelling and its interaction with mandatory requirements need design
  reconciliation. This does not authorize bypassing host-access boundaries.
- Ignoring this repository's .idea files is decided. Project-management must
  untrack them without deleting local files, add the ignore rule and explain
  that other projects may choose differently. This is work, not a release gate.
- The owner requires a decision on all eleven user-docs improvement proposals
  before 0.3.0. This decision gate does not approve all eleven implementations.
- Release notes as an artifact, the backfill and documentation obligations are
  adopted. Maintenance's plate retains automation; the operator obligations
  remain in force before automation exists.

## Active Implementation Planning: Persistent Diagnostics (C21)

Owner direction, 2026-10-09: this is a "hot potato", under active consideration
for implementation targeted ready for **0.3.0**. Priority: `wanted`, not later.
The [assigned work order](../../work-orders/2026-10-08-persistent-session-diagnostics.md)
contains the October 8 incident evidence, required baseline and proposed scope.
It is independent of the closed Stage 7 resource-convention request.

Owner assignment, 2026-10-11: **maintenance** implements this work because
reliable logs are a prerequisite for diagnosis and repair. Its responsibility
includes the needed supervisor, display, launcher and IDE logging integration;
contained-display's lifecycle is not a prerequisite. Maintenance scopes the
bounded release slice and acceptance, coordinates its C10 terminal/shutdown
work, then implements and validates. Exact retention limits, browser capture
and snapshot/export scope remain design choices. No new release-blocking gate
or implementation completion is inferred.

## Candidate Accounting

Keep the earlier identifiers so existing references stay meaningful. Integrated
means source delivery, not downloaded-candidate acceptance.

| ID | Subject | Current disposition |
|---|---|---|
| C1 | Base contract and compatibility presentation | Integrated baseline; release driver validates from the candidate. |
| C2 | Preserve 0.2.15 additions | Reached main; do not regress them at the cut. |
| C3 | Agent freshness review | Runbook adopted; release driver executes it. |
| C4 | Notes artifact and backfill | Adopted; automation is tracked once under C20. |
| C5 | Named build contexts | Accepted maintenance work; published record reports implementation and review stack, not final release acceptance. |
| C6 | Old RC base label | Covered by C1, not a second implementation task. |
| C7 | Recorded-schema listing and discoverable base choice | Owner rulings accepted; retained with upgrade design in the coordination backlog; release placement unresolved. |
| C8 | In-capsule project commands | Accepted maintenance fix; candidate validation remains. |
| C9 | Bug triage | Maintenance reports the 0.3.0 triage complete; release driver checks remaining blockers before the cut. |
| C10 | First-session terminal UX and Ctrl+C | Accepted maintenance work, not reported complete. |
| C11 | Checkout-name default | Explicitly outside 0.3.0 by owner decision of 2026-10-10; decide before V1, tentatively 0.9. |
| C12 | IntelliJ and its smoke | Accepted and integrated through PR #170; release acceptance remains. |
| C13 | Broader managed updates and upgrade experience | Existing component-upgrades work and new design requests must be reconciled; the old blanket out-of-release recommendation is not an owner decision. |
| C14 | mycodespace | Explicitly outside 0.3.0 by owner decision of 2026-10-10; revisit direction before V1, tentatively 0.9. |
| C15 | Legacy launch capabilities | Mandatory V1 decision/delivery gate; not automatically a 0.3.0 implementation commitment. |
| C16 | Current release documentation | Standing release obligation; 0.2.15 docs delivered, 0.3.0 docs must describe the accepted candidate. |
| C17 | Workflow improvements | Project-operation instructions and the agent's continuing responsibility explicitly assigned for 0.3.0 on 2026-10-11; other existing scope remains separate. |
| C18 | Legacy branch migration | Completed for active workstreams; no current release hold. |
| C19 | Adopter/contributor positioning | Reconcile existing README/blog/docs delivery before asking for remaining editorial/product choices. |
| C20 | Notes and documentation release automation | Accepted on maintenance's 0.3.0 plate; retain operator steps until implemented and validated. |
| C21 | Persistent, bounded session diagnostics | Assigned to maintenance on 2026-10-11, targeted ready for 0.3.0; bounded scope, implementation and acceptance remain. |

## Decisions Still Needed

1. Set the final 0.3.0 scope, headline, driver and cut trigger. Maintenance was
   the prior recommended driver; that recommendation is not a decision.
   Include the console's actual delivery state when making the scope decision.
2. Decide the eleven user-docs proposals. The list remains on user-docs' branch
   as `2026-09-28-docs-improvements-for-0216.md`; its filename is historical.
3. Reconcile launcher recovery recommendations with R-CONFIG-001 and the
   component-upgrades decisions. Assign only the uncovered scope.
4. Maintenance scopes and implements the prioritized diagnostics slice C21
   for 0.3.0 readiness. Owner, priority and release target are decided; only
   consequential scope choices need to return to project-management/the owner.
5. Decide any selected upgrade-design slice. Preserve the separate V1 gate
   for L1-L13. Checkout naming is excluded from 0.3.0.

Consent inclusion, notes adoption, the release name and the existence of the
user-docs gate are settled. Do not ask the owner to approve them again.
Do not put later work back on the immediate agenda merely because an intake
message was closed. Consult its recorded home at its planning trigger.

## Explicitly Outside 0.3.0

Owner direction, 2026-10-11: ecosystem-aware bootstrap moves to **0.9**,
dependent on project-type templating. Tools should be on PATH throughout the
capsule by default; exceptional ecosystems may use `devcapsule project shell`
for activation. The [decision](2026-10-11-decision-project-operations-and-bootstrap.md)
records the full direction and replaces the earlier 0.3.0 maintenance target.
The 0.3.0 project-operation instruction requirement above remains in scope.

Owner direction, 2026-10-10: mycodespace/checkout naming (agenda item 7),
OpenCode evaluation (8), and routine intake-README/contract-wording cleanup (12)
are postponed until before V1, tentatively 0.9. Their scope and revisit trigger
are in the [pre-V1 backlog](coordination-backlog.md#pre-v1-work-tentatively-09-excluded-from-030).
Do not include them in 0.3.0 planning or acceptance obligations. This does not
postpone the eleven user-docs proposal decisions or ordinary release docs.

## Pagefind Routing

Owner decision, 2026-10-10: drop the Pagefind catalog proposal. Website owns
portable project-local npm integration when W10 search is picked up; no new
search schedule is implied. The handoff is delivered at coordination
`5b05eeecda11`. Temporary /opt/xtras installs must not be project prerequisites.
Playwright's existing component remains separate. Pagefind is not a pending
DevCapsule component or a new 0.3.0 implementation obligation.

## Evidence And Limits

Read origin/main at 2258ab1 and the published coordination state on 2026-10-09.
Component-catalog reports PR #170 integrated; maintenance's implementation
review stack and component-upgrades' consent implementation remain distinct
from that integration. These records establish planning facts, not fresh
runtime or downloaded-release acceptance. No release ref or tag was changed.
