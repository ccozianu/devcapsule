# Intake: A Worktree Procedure

Delivered: 2026-08-16

From: `project-management`

Originally handed over by the
[portfolio checkpoint of 2026-08-15](../../2026-08-09-project-management/2026-08-15-portfolio-checkpoint.md)
as item 3 of four. That checkpoint recorded the handoff in the sender's own
document, so it never reached this workstream. Redelivered here now that the
intake mechanism exists.

## What Is Being Handed Over

`WORKFLOW.md` calls worktrees optional implementation tools and references them
throughout — switching workstreams, avoiding mixed dirty state, preparing a
registration from `main` while another workstream is checked out — without ever
saying how to create, select, or dispose of one.

They are also the only mechanism the protocol offers for genuine concurrency.

## Why It Belongs Here

It is a gap in the workflow protocol itself, discovered by using it. The
`project-management` track can observe the gap but should not write the
procedure, since improving the multiple-stream workflow from concrete dogfood
findings is this workstream's registered goal.

## Evidence

- The `workflow-improvements` workstream was itself registered from a temporary
  worktree while the primary checkout stayed on `recursive-e2e/stage-4`. That
  worktree was created ad hoc, with no documented procedure to follow and no
  recorded disposal step.
- Rule 11's second carve-out refers to "another worktree's recovery state",
  which presumes a worktree lifecycle the document never defines.
- The session-start selection rules require identifying "the current Git
  worktree, branch, and dirty state", again without saying how a second one
  comes to exist.

## What Accepting Would Mean

A documented procedure covering at least: when a worktree is warranted rather
than a branch switch; where worktrees live relative to the primary checkout;
how one is associated with exactly one workstream; how the session-start
selection rules apply inside one; how it is disposed of, including what happens
to uncommitted recovery state; and how an abandoned worktree is detected.

Priority and sequencing are this workstream's judgment, not the sender's.
