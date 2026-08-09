# Workstream Final Status: Multiple-Stream Workflow

Mnemonic: `multi-workflow`

Start date: 2026-08-08

End date: 2026-08-09

State: successful

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Outcome

DevCapsule replaced its implicit single-threaded project-memory model with an
optional multiple-stream workflow. The completed workflow provides:

- a compact root registry and independently resumable workstream handoffs;
- main-first registration, flat workstreams, mnemonic-prefixed branch
  ownership, and dirty-state isolation;
- immutable ISO-start-date and mnemonic directories for chronological WIP and
  archive discovery;
- deterministic checkout selection from explicit intent and registered Git
  branch/worktree state without a hidden local preference;
- policy-aware pull-request and explicitly permitted direct-main integration;
  and
- successful, unsuccessful, recovery, documentation-promotion, and archival
  procedures.

## Integration Result

- [PR #8](https://github.com/ccozianu/devcapsule/pull/8) merged the workflow
  transition and integration procedure into `main` at revision `b648623`.
- [PR #9](https://github.com/ccozianu/devcapsule/pull/9) merged the
  date-prefixed directory layout and checkout-selection procedure into `main`
  at revision `ed30a58`.
- The finalization checkpoint removes this workstream from the open registry,
  preserves this dated archive, and leaves `recursive-e2e` as the only open
  workstream. Its eventual merge revision is preserved by repository history.

## Evidence

- `.devcapsule/devcapsule.toml` parses with
  `workflow-type = "multiple-streams"`.
- The platform lock digest agrees with the project manifest without changing
  runtime selections.
- Fast repository validation passed with `223 passed`, `8 deselected`.
- Mirrored reusable workflow assets match.
- All repository-local prose links resolve outside intentionally
  target-relative reusable templates.
- Documentation diff checks pass.

## Residual Risks

- Repository state is durable coordination, not a live presence or locking
  service. Contributors must still synchronize mainline refs before shared
  lifecycle changes.
- Branch protection, review, merge queues, and publication authority remain
  repository policy rather than universal workflow constants.
- The grandfathered `recursive-e2e` branch remains the sole adoption exception;
  its later branches must follow the normal mnemonic prefix.

## Permanent Records

- [Authoritative workflow](../../../WORKFLOW.md)
- [Accepted design and rationale](../../design-notes/multiple-stream-workflow.md)
- [Agent startup and routing instructions](../../../AGENTS.md)
- [Engineering documentation placement rules](../../README.md)
- [Multiple-workstream requirement](../../requirements/product/r-product-006-multiple-workstream-coordination.md)

## Associated Branches

- `milestone/recursive-dogfood-e2e` — bootstrap exception on which the initial
  workflow transition was authored.
- `multi-workflow/date-prefixed-layout` — conforming refinement and final
  integration branch.
- `multi-workflow/finalize` — successful-completion and archival branch.
