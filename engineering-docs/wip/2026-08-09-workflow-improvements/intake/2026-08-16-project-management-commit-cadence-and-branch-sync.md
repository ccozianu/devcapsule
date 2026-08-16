# Intake: Commit Cadence And Branch Synchronization

Delivered: 2026-08-16

From: `project-management`, relaying a product-owner proposal made on
2026-08-16.

## What Is Being Handed Over

Two related rules the protocol does not currently state:

1. An agent should commit work in progress often, rather than accumulating
   uncommitted changes across a long session.
2. A workstream branch should be synchronized with `main` at least after every
   stage, with the user deciding when conflicts are addressed.

## Why It Belongs Here

Both are workflow protocol, and the current document says neither. The sender
observed the first failing in its own session and is not the right owner of the
correction.

## Evidence

- In the session that produced this item, seven files accumulated uncommitted
  across many turns before the user asked for a commit. Nothing in the protocol
  discouraged that, and an interrupted session would have lost the sequence in
  which decisions were made.
- `WORKFLOW.md` has checkpoint triggers but no commit-cadence rule, so
  "checkpoint" and "commit" are not connected.

## Points The Sender Recommends Considering

Offered as analysis, not as constraints on this workstream's judgment.

- **Rebase safety depends on publication state.** Rebasing an unpublished
  branch is clean. Rebasing a published one requires a force-push, and this
  repository has already paid for that: the
  [2026-08-16 session record](../../../session-records/devcapsule/2026-08-16-inspector-hardening-samples-and-workflow-bootstrap.md)
  documents duplicate-SHA confusion costing avoidable friction, and
  `project-management/coordination` currently carries two commits patch-identical
  to commits already on `main`. A rule phrased as *synchronize after every
  stage*, with the method following publication state, may be safer than a rule
  naming rebase specifically.
- **`AGENTS.md` already cautions** against imposing a rebase or fast-forward
  policy on a pull-request workflow, so a blanket rebase rule would need
  reconciling with that sentence.
- **Conflicts may not all be the user's decision.** `AGENTS.md` already treats
  mechanical conflict resolution as normal agent work. Splitting mechanical
  conflicts from semantic ones — two workstreams asserting incompatible things —
  would keep the user's attention on the cases that need judgment.
- **Commit cadence and clean history interact.** Frequent WIP commits plus
  pull-request delivery needs an explicit stance on whether history is squashed
  at the merge boundary; undecided, the two rules pull against each other and an
  agent hesitates to commit.

## What Accepting Would Mean

Rules in `WORKFLOW.md` stating the expected commit cadence, the branch
synchronization point and method, the split of conflict decisions between agent
and user, and the history expectation at the delivery boundary.
