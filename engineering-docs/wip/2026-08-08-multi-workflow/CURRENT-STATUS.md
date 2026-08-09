# Workstream Current Status: Multiple-Stream Workflow

Mnemonic: `multi-workflow`

Start date: 2026-08-08

State: active

Integration target: `main`

Integration delivery: pull request by default; direct-main integration is
explicitly permitted for this owner-operated dogfood repository

Publication authority: the dogfood agent has no Git credentials; the project
owner performs required remote publication or merge actions

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Goal

Replace the repository's implicit single-threaded project-memory model with an
explicit, optional workflow that can keep several bounded efforts independently
resumable and safely integrable.

## Branch Association

The active branch is `multi-workflow/date-prefixed-layout`, created from
`origin/main` after the bootstrap transition merged. The initial workflow work
occurred on `milestone/recursive-dogfood-e2e` before branch association rules
existed and remains the documented migration exception.

## Current State

- The project manifest selects `workflow-type = "multiple-streams"`.
- The authoritative workflow defines main-first registration, flat
  workstreams, branch ownership, WIP documentation, successful and
  unsuccessful completion, integration, and recovery.
- Root `CURRENT-STATUS.md` is the compact open-workstream registry.
- The existing recursive E2E effort has its own detailed WIP handoff.
- Requirement `R-PRODUCT-006` captures the coordination contract.
- Reusable workflow bootstrap assets teach projects to select a workflow type.
- Successful integration separates agent-owned preparation and finalization
  from policy-controlled delivery. Pull-request delivery follows repository
  merge policy by default; explicitly permitted direct-main delivery uses
  rebase, fast-forward, and a normal push.
- The transition and policy-aware integration procedure reached `main` through
  PR #8 at merge revision `b648623`.
- WIP and archive directory names now combine the immutable ISO workstream
  start date with the mnemonic so human readers can see chronology directly.
- Checkout-specific default workstream selection remains to be specified.

## Last Task And Status

Last task: adopt date-prefixed WIP and archive directory names and migrate the
two existing open workstream handoffs.

Status: complete. The convention is `<start-date>-<mnemonic>`, both dates are
recorded in the root registry and handoffs, and all repository instructions,
indexes, and reusable bootstrap assets use the new paths.

## Next Resumable Task

Specify deterministic checkout-specific workstream selection:

1. define which registry snapshot an agent reads from a workstream branch;
2. define selection for mnemonic-prefixed branches, `main`, and detached HEAD;
3. decide whether an untracked worktree-local preference is useful;
4. define invalid and ambiguous selection outcomes without weakening dirty
   state isolation; and
5. update the workflow, agent instructions, design, requirement, templates, and
   handoff before final archival.

## Evidence

- Project configuration parses with `workflow-type = "multiple-streams"`.
- The platform lock manifest digest agrees with the updated project manifest
  without changing runtime selections.
- Fast repository tests passed: `223 passed`, `8 deselected`.
- The exceptional branch rebased cleanly onto fetched `origin/main` revision
  `1614594`.
- PR #8 merged the workflow transition into `main` at revision `b648623`.
- All repository Markdown files are indexed and all prose local links resolve.
- Documentation diff checks pass.

## Workstream Document Index

This workstream owns only this WIP status. Its finalized outputs already occupy
their intended permanent locations as a bootstrap exception:

- [Authoritative workflow](../../../WORKFLOW.md)
- [Accepted design and rationale](../../design-notes/multiple-stream-workflow.md)
- [Agent startup and routing instructions](../../../AGENTS.md)
- [Engineering documentation placement rules](../../README.md)
- [Multiple-workstream requirement](../../requirements/product/r-product-006-multiple-workstream-coordination.md)

## Migration Exception

This workstream was designed on the existing
`milestone/recursive-dogfood-e2e` branch before the new branch-association and
WIP-placement rules existed. Follow-up work now uses the conforming
`multi-workflow/` branch prefix. That bootstrap circumstance is not a
precedent. Later workstreams must be registered on `main` and developed on
mnemonic-prefixed branches.
