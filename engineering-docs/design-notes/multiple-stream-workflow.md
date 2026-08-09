# Design: Multiple-Stream Workflow

Status: accepted

Date decided: 2026-08-08

Decided by: project owner

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Decision

Each repository declares one workflow type in `.devcapsule/devcapsule.toml`:

```toml
workflow-type = "single-stream"
```

The supported values are `single-stream` and `multiple-streams`. Missing
metadata means `single-stream` for compatibility with older repositories.

Single-stream projects retain the existing linear handoff workflow.
Multiple-stream projects use `main` as a shared coordination and integration
branch, one temporary WIP documentation area per open workstream, and one
detailed status file per workstream. The authoritative procedure is in
[WORKFLOW.md](../../WORKFLOW.md).

## Workstream Model

A workstream is a bounded set of changes developed toward one goal, possibly
in parallel with other workstreams. It has a beginning, a development phase,
and an explicit successful or unsuccessful end.

Each workstream has:

- one unique, short mnemonic;
- one or more branches whose names use that mnemonic as their prefix;
- exactly one detailed handoff at
  `engineering-docs/wip/<mnemonic>/CURRENT-STATUS.md`; and
- a declared intention to integrate into `main` if successful.

Workstreams are flat. This first revision has no parent, child, or nested
workstreams. A branch other than `main` belongs to exactly one workstream.
`main` belongs to none: it is the shared registration, visibility,
finalization, and integration branch.

## Documentation Model

Root `CURRENT-STATUS.md` on `main` is only the registry of workstreams that
have begun but not ended. Paused and blocked workstreams remain open and stay
in the registry.

All unfinished workstream documentation lives under:

```text
engineering-docs/wip/<mnemonic>/
```

Draft user documentation is the sole permitted `docs/` subdirectory beneath
an engineering workstream directory:

```text
engineering-docs/wip/<mnemonic>/docs/
```

An entirely new user document may be drafted there at its intended relative
path. A change to an existing root `docs/` file is represented there by a
human- and agent-readable change proposal rather than a duplicate of the
existing document.

Workstream documentation checkpoints may be integrated into `main` before the
source changes for visibility. They remain WIP and the workstream branch owns
the latest development state.

## Ending A Workstream

For a successful workstream:

- integrate the accepted source changes into `main`;
- move new user documents into root `docs/`;
- apply proposals to existing user documents;
- move enduring engineering records into their normal permanent categories;
- remove the workstream from root `CURRENT-STATUS.md`; and
- archive a brief final status at
  `engineering-docs/archive/<mnemonic>/CURRENT-STATUS.md`.

The workstream status is never appended to root `CURRENT-STATUS.md`.

For an unsuccessful workstream, move the entire
`engineering-docs/wip/<mnemonic>/` tree to
`engineering-docs/archive/<mnemonic>/`. Its final `CURRENT-STATUS.md` records
the unsuccessful outcome, last task, and last task status. No unfinished user
documentation is promoted into root `docs/`.

## Why This Shape

The model keeps the single-stream workflow lightweight while giving concurrent
efforts separate branches, documentation, and resumable state. Temporary WIP
namespaces prevent unfinished documents from appearing authoritative and
prevent workstream-specific state from accumulating in one central handoff.

Flat workstreams deliberately avoid hierarchy, ownership graphs, and task
databases. Git remains the changeset and integration mechanism. Repository
Markdown remains the durable human/agent memory.

## Current Repository Migration

DevCapsule adopted this workflow while work was already occurring on
`milestone/recursive-dogfood-e2e`, before the branch-prefix and main-first
registration rules existed. That branch is a grandfathered migration
exception associated with mnemonic `recursive-e2e`.

The transition checkpoint must reach `main` before another workstream is
opened under the new protocol. All later workstreams follow the normal
main-first registration and mnemonic-prefix rules.

Other branch refs that existed before adoption are inactive legacy refs. They
do not become open workstreams automatically and must not receive new work
until a source-level workstream record on `main` assigns their continuation to
one mnemonic.
