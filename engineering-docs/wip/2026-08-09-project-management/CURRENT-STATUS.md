# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active; permanent coordination

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Goal

Provide the durable project-management home for project-wide priorities,
sequencing, cross-workstream dependencies, and lifecycle decisions while this
repository uses the multiple-stream workflow.

This permanent track coordinates other workstreams but does not duplicate
their detailed handoffs, implement their scoped changes, edit their WIP state,
or become a miscellaneous backlog.

## Lifecycle Exception

The user explicitly opened this permanent workstream as a one-off operation
before the general workflow defines it. Unlike ordinary bounded workstreams,
`project-management` remains open while the repository uses
`workflow-type = "multiple-streams"`. The `workflow-improvements` backlog owns
formalizing that exception for all multiple-stream projects, including any
valid retirement or workflow-mode migration procedure.

## Branch Association

The initial branch is `project-management/coordination`, forked from the
registration commit on `main`. The existing recursive E2E checkout remains
selected on `recursive-e2e/stage-4`; project-management changes require an
explicit switch to this branch or a separate clean worktree.

## Current State

- The current execution focus remains recursive E2E Stage 4.
- `workflow-improvements` is open to capture and correct concrete workflow
  findings, including formalization of this permanent track.
- `project-management` is now the standing home for future cross-workstream
  priority, sequencing, dependency, and lifecycle decisions.
- No other workstream's task details or WIP documents have been moved here.

## Last Task And Status

Last task: register the permanent project-management workstream as an explicit
one-off while keeping the recursive E2E checkout selected.

Status: complete. The registry, handoff, documentation index, and conforming
initial branch association are defined from current `main`.

## Next Resumable Task

After the pending registration commits are published to remote `main`, create
the first concise portfolio checkpoint only when a cross-workstream priority,
sequence, dependency, or lifecycle decision is needed.

Done means:

- the decision identifies the affected workstreams and why coordination is
  required;
- detailed implementation state remains in each affected workstream handoff;
- any repository-wide routing fact is reflected in root `CURRENT-STATUS.md`;
  and
- the next editing checkout remains explicit and unmixed.

## External State And Risks

- The environment has no Git publication credentials; the human must publish
  the pending mainline registration commits.
- The permanent lifecycle is a documented repository-local exception until
  the `workflow-improvements` workstream defines and validates the general
  rule.
- Project management must remain coordination rather than a path for bypassing
  branch ownership, integration policy, or another workstream's handoff.

## Workstream Document Index

This workstream currently owns only this WIP status file.
