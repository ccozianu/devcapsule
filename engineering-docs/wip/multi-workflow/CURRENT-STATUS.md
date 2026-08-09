# Workstream Current Status: Multiple-Stream Workflow

Mnemonic: `multi-workflow`

State: integrating

Integration target: `main`

Integration delivery: pending project-owner selection; pull request is the
default and direct-main integration is explicitly permitted for this
owner-operated dogfood repository

Publication authority: the dogfood agent has no Git credentials; the project
owner performs required remote publication or merge actions

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
- Successful integration separates agent-owned preparation and finalization
  from policy-controlled delivery. Pull-request delivery follows repository
  merge policy by default; explicitly permitted direct-main delivery uses
  rebase, fast-forward, and a normal push.
- Integration into `main` is still pending because this transition was authored
  on the pre-existing recursive branch and must be isolated from the
  recursive-E2E-only change before delivery. The exceptional branch is now
  rebased on fetched `origin/main` revision `1614594`.

## Last Task And Status

Last task: make successful integration a deterministic agent-operated process
that supports normal pull-request delivery and explicitly permitted direct-main
delivery, then rebase the exceptional checkout on fetched `origin/main`.

Status: complete. The authoritative workflow, agent instructions, accepted
design, and coordination requirement now agree on the integration procedure,
delivery choices, and human escalation points. The five local commits rebased
cleanly without conflict.

## Next Resumable Task

Isolate a coherent accepted transition on a dedicated
`multi-workflow/integration` branch based on current `main`; the bootstrap work
must not carry the independent recursive-E2E source state into `main`. Then the
project owner selects one permitted delivery path:

1. Prefer the general pull-request path: publish the integration branch, review
   and validate it, add the final archival and registry-removal commit when it
   is merge-ready, and merge it using repository policy.
2. Alternatively, the owner may explicitly select direct-main delivery for
   this repository: rebase the frozen branch on current `main`, finalize and
   validate it, fast-forward local `main` with `--ff-only`, and push `main`
   normally.

In either path, the agent prepares all local changes and evidence. The project
owner performs the remote push or merge action that requires credentials.

Do not open another workstream before the finalized commit reaches
`origin/main`.

## Evidence

- Project configuration parses with `workflow-type = "multiple-streams"`.
- The platform lock manifest digest agrees with the updated project manifest
  without changing runtime selections.
- Fast repository tests passed: `223 passed`, `8 deselected`.
- The exceptional branch rebased cleanly onto fetched `origin/main` revision
  `1614594`.
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
