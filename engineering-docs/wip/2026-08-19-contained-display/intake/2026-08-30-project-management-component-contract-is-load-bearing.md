# Intake: The Supervisor↔Component Contract Is Load-Bearing; Pause Recorded

Delivered: 2026-08-30

From: `project-management`, recording product-owner decisions made the same
day.

## The Pause

`contained-display` is paused as of 2026-08-30, by the product owner, until
the newly registered `component-catalog` workstream delivers significant
progress. The supervisor-core assignment recorded in this queue on the same
date stands unchanged; only its start moves. The root registry row reflects
the pause.

## What To Pay Attention To On Resume

`component-catalog` builds directly on the contract through which the
supervisor and runtime planning consume components: `ComponentDefinition`
and its declarations in `devcapsule/components/interface.py`,
`ComponentRuntimeTemplate` and the state-slot persistence model in
`devcapsule/container_runtime/contract.py` and `devcapsule_runtime/`, and the
catalog selection in `devcapsule/components/catalog.py` — which that
workstream generalizes so `interactive-surface` is no longer hard-coded to
PyCharm, and extends with a `codium` surface and an Antigravity CLI agent
component.

When this workstream resumes supervisor work, do not change that
component-facing contract inadvertently. Deliberate changes are fine and may
well be needed — route them through coordination first: an intake item to
`component-catalog` describing the change and what it breaks, before the
change lands on `main`. The symmetric obligation is recorded in
`component-catalog`'s handoff: it consumes the contract and does not reshape
the supervisor.

## References

- Registration and scope:
  `engineering-docs/wip/2026-08-30-component-catalog/CURRENT-STATUS.md`.
- Ledger rows now owned by `component-catalog`: *Independent IDE Surface:
  VSCodium On The Normal Project Path* and the Antigravity slot of *Curated
  Agent Choice*, in
  `engineering-docs/wip/2026-08-09-project-management/v1-scope-ledger.md`.

## Delivery Note, Recorded Latitude

This item references a workstream registration that lands on `main` in the
same pull request that carries this item, so it travels on
`project-management/coordination` rather than alone through the outbox, per
the target-lands-no-later-than-the-reference precedent recorded at the
2026-08-27 pause.
