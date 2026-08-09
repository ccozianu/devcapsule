# Workstream Current Status: Multiple-Stream Workflow

Mnemonic: `multi-workflow`

State: integrating

Integration target: `main`

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Goal

Replace the repository's implicit single-threaded project-memory model with an
explicit, optional workflow that can keep several bounded efforts independently
resumable and safely integrable.

## Current State

- The project manifest selects `workflow-type = "multiple-streams"`.
- The authoritative workflow defines main-first registration, flat
  workstreams, branch ownership, WIP documentation, successful and
  unsuccessful completion, integration, and recovery.
- Root `CURRENT-STATUS.md` is the compact open-workstream registry.
- The existing recursive E2E effort has its own detailed WIP handoff.
- Requirement `R-PRODUCT-006` captures the coordination contract.
- Reusable workflow bootstrap assets teach projects to select a workflow type.
- Integration into `main` is still pending because this transition was authored
  on the pre-existing recursive branch and local `main` has diverged.

## Last Task And Status

Last task: finalize the agreed workstream lifecycle and transition the current
checkout to multiple-stream metadata and documentation.

Status: complete. The documentation and repository structure are ready for an
integration checkpoint.

## Next Resumable Task

Create a coherent transition commit, integrate it safely into current `main`,
then perform successful completion:

1. verify the main integration does not overwrite its four divergent commits;
2. merge or otherwise integrate the accepted transition checkpoint;
3. remove `multi-workflow` from root `CURRENT-STATUS.md`;
4. move this file to
   `engineering-docs/archive/multi-workflow/CURRENT-STATUS.md`;
5. change its final state to `successful` and record the integration revision;
   and
6. update `index.md`.

Do not open another workstream before this checkpoint reaches `main`.

## Evidence

- Project configuration parses with `workflow-type = "multiple-streams"`.
- The platform lock manifest digest agrees with the updated project manifest
  without changing runtime selections.
- Fast repository tests passed: `223 passed`, `8 deselected`.
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
WIP-placement rules existed. That bootstrap circumstance is not a precedent.
Later workstreams must be registered on `main` and developed on mnemonic-prefixed
branches.
