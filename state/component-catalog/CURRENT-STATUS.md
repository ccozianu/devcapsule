# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: active 2026-10-03; bringing IntelliJ IDEA into the catalog as an optional IDE surface, targeted at 0.2.16; implementation not yet started

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@6ff07c49a7ea

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Goal And Scope

Accept and test IDE surfaces and agent CLIs as regular catalog components.
The current task is to make IntelliJ IDEA an option alongside the existing
IDE surfaces, using the existing JetBrains adapter where appropriate.

The owner's 2026-10-01 decision, delivered by project-management and confirmed
in this checkout on 2026-10-03, assigns IntelliJ to this workstream for
0.2.16 and lifts the historical Antigravity scope freeze. New IDE components
belong here; component orchestration, upgrades and channels belong to
`component-upgrades`. Eclipse is not scheduled.

## Current State

- Antigravity is completed work per the owner. Its old branch
  `ws-component-catalog/antigravity-cli` remains intact as history; do not
  resume its obsolete delivery tasks or merge its intermediate changes as
  a prerequisite to IntelliJ.
- The continuation branch starts at current `main`, `69ced64`, with the
  current workflow definition and local rules. No synchronization was
  needed at this checkpoint. Future synchronization of the published
  branch merges `main` in, following the current integration policy.
- The registry and this status now identify the IntelliJ continuation.
  No runtime code or product requirements were changed by this setup.
- No open bug records owned by `component-catalog` were found on this
  mainline baseline. Re-read the queue at the next session.
- The website gitlink remains exactly the one on `main`; the owner reserves
  pointer updates to the docs workstream.

## Planned Next Step

Scope and implement IntelliJ IDEA as a selectable IDE component for 0.2.16.
First read the project-management decision and release-planning addendum,
then inspect the existing PyCharm component and JetBrains launch adapter.
Identify any unresolved edition, distribution, licensing or persistence
choices before investing in implementation; do not infer product decisions
from what is easiest to code.

Done means: a developer can select and launch IntelliJ through the ordinary
project path, with its component declaration, required documentation and
relevant checks in place. Acceptance includes an IntelliJ row in the
existing parametrized IDE smoke test, proving the IDE starts and owns a
`jetbrains-idea` window. This checkpoint claims no implementation or
acceptance evidence.

## Open Threads

- The next session reloads the current workflow, project-management records,
  requirements and component implementation before selecting the first slice.
- 0.2.16 is the assigned target; release driver, cut and formal work order
  remain project-management responsibilities. Re-verify their latest state.
- The workflow migration notice is accepted. Publish status and use
  coordination mail. Before removing any legacy outbox refs, establish
  whether they hold unlanded records and preserve those records; no legacy
  ref is removed by this checkpoint.
- No builds, containers or services were started for IntelliJ. The earlier
  website recovery files remain in this checkout's `.git/recovery/`.
- Historical status is preserved verbatim in the record below. Its old next
  steps and external-state claims are historical, not current instructions.

## Validation

Status and routing update only. Validation results are recorded at the
checkpoint after the required checks run.

## Workstream Document Index

- [Project-management status](../2026-08-09-project-management/CURRENT-STATUS.md):
  read *Owner Decisions Of 2026-10-01* for surface ownership and IntelliJ scope.
- [0.2.16 planning](../2026-08-09-project-management/2026-09-27-0216-release-planning.md):
  read C12 and its owner-decision addendum for the release target.
- [Intake decisions](intake-dispositions.md): accepted handoffs and their disposition.
- [Intake](intake/README.md): any received, undecided work.
- [Historical Antigravity status](2026-10-03-record-antigravity-status.md):
  prior implementation and acceptance history; consult only for historical evidence.
- [Antigravity license analysis](antigravity-cli-license-and-redistribution-analysis.md):
  historical agent-component licensing evidence, not IntelliJ licensing evidence.
- [Release-candidates proposal](release-candidates-proposal.md): historical proposal;
  current release policy is in WORKFLOW-LOCAL.md and the release runbook.
