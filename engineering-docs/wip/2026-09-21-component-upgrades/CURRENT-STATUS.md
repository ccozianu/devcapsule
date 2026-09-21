# Workstream Current Status: Component Upgrades

Mnemonic: `component-upgrades`

Start date: 2026-09-21

State: active; executing the component upgrade work order

Definition read: WORKFLOW.md@ee9065a1b3ab, WORKFLOW-LOCAL.md@488eed5a6c05

Integration target: `main`

Delivery method: pull request; agent pushes, owner opens and merges on GitHub

Branch association: `ws-component-upgrades/v1`

Branch prefix: `ws-component-upgrades/`

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-COMPAT-001`

## Goal

Deliver discoverable component upgrades with developer-owned, reproducible
version sets and proven rollback, using Codex as the first generic-channel
consumer. Intended for v0.2.14; project-management owns release sequencing.

## Current State

Resumed at owner request on `ws-component-upgrades/v1`. Remote main remains
`e4a96dc`, already contained in this branch; synchronization was unnecessary.
Root workflow commands confirmed current published state, unchanged definition,
and no mail. Running them from `devcapsule-src` had misleadingly shown no state;
use the repository root for workflow operations.

Implemented typed distribution channels (Codex npm first), complete local
version sets, preview/preparation/activation, rollback, recommendation following,
proposal export and remembered reminders. The existing materializer is shared.
Successful-use recording captures inputs before launch. Activation uses a
recoverable two-file journal; host permissions and personal state are not restored
from historical snapshots. D-0010 records the owner's work-order direction and
R-UPGRADE-001 records the contract without rewriting earlier decisions.

## Planned Next Step

Finish the isolated real Codex upgrade/rollback check and user/contributor
instructions, review the final diff, rerun required checks for final changes,
and push the reviewable feature branch. Owner opens and merges the GitHub PR.

## Validation And External State

The implementation gate passed: 948 tests, 18 deselected, one existing xfail,
mypy, source smoke, PEX construction and nine packaging tests. The focused
new suite passed 31 cases, including Codex and an unrelated component through
real CLI/configuration/acquisition/materialization with controlled Docker/GUI
boundaries. Existing release fixtures remain passing.

No open bugs are owned by this workstream; no mail was pending. The live Codex
registry reported 0.155.1 available and yielded exact meta/platform package
SHA-512 identities. An explicitly bounded real check is running in the isolated
`devcapsule-src/dist/component-upgrades-smoke` fixture, with separate XDG trees
and a tiny fixture IDE that reports Codex's executable version. It uses the
already local pinned base and the freshly built local PEX. It does not touch the
everyday checkout configuration, accounts or prior acceptance environments.

Git push is available. Owner GitHub PR creation/merge remains the delivery
arrangement; no release is authorized.

## Open Threads

### Awaiting The Human

None blocks implementation within the work order. The owner reviews the final
feature/code. Project-management decides the complete v0.2.14 scope and release
sequence; this workstream does not cut a release or resume maintenance.

### Weighed And Unresolved

- Exact CLI names, local version-set schema, typed channel interface and
  bounded reminder policy are implementation choices within the work order.
- Existing snapshot history is insufficient proof of rollback. Preserve exact
  launched inputs and current consent while adding an operational recovery path.
- Distribution availability, DevCapsule validation and local success are
  distinct. Unvalidated selection must retain structural compatibility checks.
- Reconcile canonical contracts with the owner's local-selection refinement;
  preserve decision history. Do not reinterpret local upgrades as shared locks.
- Executable rollback cannot undo vendor state migrations. Document the limit;
  do not expand into automatic personal-state backup/restoration.

### Deliberately Not Preserved

No chat transcript was requested. The work order holds the task contract;
illustrative command spellings are not frozen interfaces. Blog wording and
maintenance triage are outside the feature deliverable.

## Workstream Document Index

- [Work order](../../work-orders/2026-09-21-component-upgrades.md): mandatory on resume; scope, user experience, invariants, evidence and finish criteria.
- [Intake dispositions](intake-dispositions.md): decisions on received work.
- [Intake instructions](intake/README.md): how other workstreams deliver mail.
