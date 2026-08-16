# Intake: The Outbox Branch Is Adopted, And Two Of Your Deliveries Are Stuck

Delivered: 2026-08-16

From: `workflow-improvements`, implementing a product-owner decision made the
same day.

This item is itself the first use of the mechanism it describes.

## What Is Being Handed Over

The outbox-branch proposal this workstream received on 2026-08-16 is accepted
and implemented, together with the commit-cadence and branch-synchronization
item. `WORKFLOW.md` gains restriction 13, *The Outbox Branch*, *Staying Current
With `main`*, and a commit-cadence rule in *Development And Checkpoints*.

Every workstream now sends through a standing `<mnemonic>/outbox` branch, reset
from current `main`, carrying only what is being sent and never working
changes. Every workstream stays current with `main` by synchronizing often,
because `main` is the medium every message travels through.

Three consequences are actionable for this workstream.

## 1. Two Of Your Deliveries Are Stuck

`project-management/coordination` currently carries two intake files that have
not reached their recipients:

- `engineering-docs/wip/2026-08-09-workflow-improvements/intake/2026-08-16-project-management-bug-vocabulary.md`
- `engineering-docs/wip/2026-08-06-recursive-e2e/intake/2026-08-16-project-management-v026-deliverables.md`

Both are invisible to their recipients until that branch merges, which is the
failure the intake mechanism was built to fix. Neither recipient can act on
what it cannot see, and `workflow-improvements` has just finished
dispositioning its queue without the bug-vocabulary item in it.

Resending them through `project-management/outbox` costs one branch reset and
one commit, and does not disturb `project-management/coordination`.

## 2. The Registration Question Is Closed

The outbox item asked to be designed together with the standing question of how
main-first registration coexists with a pull-request delivery policy. It was.
Registration now travels the sender's outbox like any other message, so opening
a workstream no longer requires committing directly to `main`. *Beginning A
Workstream* step 6 states this, with initialization as the one case where no
sender exists yet.

This may affect how this workstream sequences the opening of future
workstreams, which is why it is called out rather than left to be discovered.

## 3. Three Intake READMEs Are Now Stale

Each `intake/README.md` restated the delivery rule in its own words, so
changing that rule made every copy stale at once. `workflow-improvements`
updated its own to point at `WORKFLOW.md` instead of restating the protocol,
which removes the recurrence for that one directory.

The READMEs in `2026-08-06-recursive-e2e`, `2026-08-09-project-management`, and
`2026-08-14-sample-projects` still say to deliver items "to `main` promptly",
which is now the wrong instruction. `workflow-improvements` did not fix them:
restriction 11's carve-out bars it from editing inside another workstream's
directory, and the intake README itself repeats that bar.

That leaves a gap this workstream may want to route, since it is a coordination
question rather than a workflow-protocol one: **who owns protocol boilerplate
that lives inside another workstream's carve-out?** Each workstream updating
its own copy works but relies on all of them noticing. Making the READMEs
pointers rather than restatements, as `workflow-improvements` did for its own,
removes the problem permanently but still requires someone allowed to edit
those three files. `workflow-improvements` has recorded this as an open thread
but does not own the answer.

## Evidence

- `WORKFLOW.md`: restriction 13, *The Outbox Branch*, *Staying Current With
  `main`*, *Development And Checkpoints*, *Beginning A Workstream* step 6.
- `git diff --name-only main...project-management/coordination` lists both
  undelivered intake files.
- The dispositions and reasoning are recorded in the
  [`workflow-improvements` handoff](../../2026-08-09-workflow-improvements/CURRENT-STATUS.md).

Priority and sequencing are this workstream's judgment, not the sender's.
