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
- Workstream intake was introduced on 2026-08-16 at the product owner's
  direction, as a second deliberate bootstrap exception: `project-management`
  published the `WORKFLOW.md` and `AGENTS.md` changes because handing the item
  to `workflow-improvements` required the very mechanism being defined. The
  four workstreams now have `intake/` directories, and the two checkpoint items
  that were never delivered on 2026-08-15 have been delivered, along with the
  product owner's commit-cadence and branch-synchronization proposal.
- A V1 readiness assessment is recorded for 2026-08-16. Its central finding is
  that V1 itself is untracked: the gap review defines four milestones, three of
  which appear in no other document and have no owning workstream. Defining V1
  precisely is therefore this workstream's next task.
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

Last task: assess V1 readiness at the product owner's request, separating
shortcomings that no workstream is on a path to solve from documented items at
risk of being deferred out of the release.

Status: complete. The
[V1 readiness assessment](2026-08-16-v1-readiness-assessment.md) records eight
unowned shortcomings and seven documented items to pin to V1. The preceding
task, the first portfolio checkpoint, is also complete: it recorded three
decisions, handed four derived items to `workflow-improvements`, and reflected
one repository-wide coordination fact in root `CURRENT-STATUS.md`.

## Next Resumable Task

Define V1. Until now V1 has been a target held in the product owner's head plus
a dated gap-review snapshot; the obvious prerequisites were clear, but the
release boundary is not. Complete the [V1 scope ledger](v1-scope-ledger.md),
which is open with its first decided row.

Done means:

- every gap in the V1 gap review carries a release verdict — in V1, deferred to
  a later release, or rejected — with the rejections and deferrals stated rather
  than left silent;
- every item retained for V1 names an owning workstream, and any milestone with
  no owning workstream is either registered as one or explicitly reassigned;
- the five functional scope decisions the gap review left open are decided, or
  carry a decision date and a named decider;
- V1 acceptance is stated as criteria that can be checked: which requirement
  records must reach `validated`, which open bugs block, and which documents
  must exist;
- the seven at-risk items in the readiness assessment each hold a single
  recorded home rather than several partial ones; and
- the ledger's cross-workstream consequences actually reach the affected
  workstream handoffs, given that the previous checkpoint's handoff to
  `workflow-improvements` never arrived in the document that workstream reads.

Record a further checkpoint only when the next cross-workstream priority,
sequence, dependency, or lifecycle decision becomes due. Checkpoints are
written because a decision is needed, not on a schedule.

## Deferred From This Workstream

Decide the release target for the file locking protocol in the
[coordination backlog](coordination-backlog.md), including whether ordinary Git
conflict resolution makes it unnecessary. Recording that it is unnecessary is a
valid outcome. This was the previously planned next task and is deliberately
sequenced behind defining V1, since the V1 boundary determines whether the
protocol is a release commitment at all.

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
- [V1 readiness assessment 2026-08-16](2026-08-16-v1-readiness-assessment.md)
- [V1 scope ledger](v1-scope-ledger.md)
- [Workflow prior-art comparison 2026-08-16](2026-08-16-workflow-prior-art-comparison.md)
- [Coordination backlog](coordination-backlog.md)
