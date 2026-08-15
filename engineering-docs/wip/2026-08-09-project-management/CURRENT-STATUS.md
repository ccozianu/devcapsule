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

- The first portfolio checkpoint is recorded for 2026-08-15.
- The minimal workflow improvements it identified are published in
  `WORKFLOW.md`: verified divergence resolution, the merge-landed check,
  and non-exclusive file editing with a handoff carve-out. This was a
  deliberate bootstrap exception, because `workflow-improvements` could not
  start cleanly without them.
- The current execution focus is `sample-projects`. `recursive-e2e` is paused
  by product-owner decision with Stage 6 substantially complete.
- `workflow-improvements` is open and its intake is now ready: four concrete
  items were handed to it by the checkpoint.
- `project-management` is the standing home for cross-workstream priority,
  sequencing, dependency, and lifecycle decisions.
- No other workstream's task details or WIP documents have been moved here.

## Last Task And Status

Last task: record the first portfolio checkpoint.

Status: complete. The checkpoint records three decisions, hands four derived
items to `workflow-improvements`, and reflects one repository-wide coordination
fact in root `CURRENT-STATUS.md`: file editing is not exclusive to any
workstream absent a documented locking protocol.

## Next Resumable Task

Decide the release target for the file locking protocol in the
[coordination backlog](coordination-backlog.md), including whether ordinary Git
conflict resolution makes it unnecessary. Recording that it is unnecessary is a
valid outcome.

Record a further checkpoint only when the next cross-workstream priority,
sequence, dependency, or lifecycle decision becomes due. Checkpoints are
written because a decision is needed, not on a schedule.

Done means:

- the decision identifies the affected workstreams and why coordination is
  required;
- detailed implementation state remains in each affected workstream handoff;
- any repository-wide routing fact is reflected in root `CURRENT-STATUS.md`;
  and
- the next editing checkout remains explicit and unmixed.

## External State And Risks

- Corrected 2026-08-15: this environment does have Git publication credentials
  and can push branches and unprotected `main`, and the local Docker CLI is
  authenticated to the registry. The earlier statement that a human must
  publish mainline commits was stale for at least two sessions and cost
  avoidable friction. Verify such constraints before relying on them.
- The permanent lifecycle is a documented repository-local exception until
  the `workflow-improvements` workstream defines and validates the general
  rule.
- Project management must remain coordination rather than a path for bypassing
  branch ownership, integration policy, or another workstream's handoff.

## Workstream Document Index

- [Portfolio checkpoint 2026-08-15](2026-08-15-portfolio-checkpoint.md)
- [Coordination backlog](coordination-backlog.md)
