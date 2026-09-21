# Workstream Current Status: Component Upgrades

Mnemonic: `component-upgrades`

Start date: 2026-09-21

State: paused; work order prepared for implementation in a fresh session

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

The owner requested rebasing maintenance on origin/main, opening this feature
workstream, and writing its working order for a fresh session. Maintenance was
rebased onto `e4a96dc`, deliberately paused, committed at `357c5ce`, pushed,
and published on coordination. Its bug triage remains deferred.

This branch starts at `origin/main` (`e4a96dc`) with registration and the work
order only. Feature implementation has not started. The work order records the
settled product direction, bounded implementation freedom, evidence gaps,
acceptance checks and scope exclusions. User-selected upgrades belong in user
configuration; upstream contribution is optional and deliberate.

Registration follows Beginning A Workstream step 6: the initial registration
commit belongs on the first branch forked from main and is published live on
coordination; its mainline row arrives with ordinary integration. The earlier
wording about creation on main is treated as the starting baseline, not an
instruction to commit or push registration directly to main.

## Planned Next Step

In the fresh session, read the work order and Open Threads; fetch and
synchronize this branch under current policy, take mail, and trace component
acquisition, configuration ownership and known-good recording into a bounded
implementation plan. Then implement the agreed journey autonomously through
reviewable feature/code and tests. Do not wait for a registration-only PR.

## Validation And External State

The preparation gate on the unchanged source baseline passed: 917 tests,
18 deselected, one existing xfail, mypy, and nine packaging tests. The local
artifact is `devcapsule-src/dist/devcapsule-local.pex`; the build did not replace
the distributable PEX while documentation changes were uncommitted.
The existing seven history-focused tests prove snapshots, not version-set
rollback. No feature code or new tests were written during preparation.

No open bugs are currently owned by `component-upgrades`; mail retrieval
found no pending items. New documentation links and whitespace checks passed.

No containers were launched or environments provisioned for this handoff.
Maintenance's older retained acceptance environment is historical evidence,
not a prerequisite or permission to alter it. Git push is available; owner
GitHub PR creation/merge remains the delivery arrangement.

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
