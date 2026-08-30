# Intake: The Off-`main` Mail Transport — Spiked Design, Yours To Implement

Delivered: 2026-08-30

From: `project-management`, at the product owner's direction the same day.

## What Is Being Handed Over

A spiked and owner-endorsed design for moving workstream mail off `main`:
recipient-owned `mail/<mnemonic>` branches — senders append-only, only the
recipient resets its own mailbox after ingesting into its `intake/`,
session-start fetch for timeliness, and the intake exclusive-or invariant
extended to three places (mail branch, intake, disposition log). The full
spike, including the recorded comparison against a single shared
communication branch and the rejected alternatives, is
[the 2026-08-30 note](../../2026-08-09-project-management/2026-08-30-off-main-mail-transport-spike.md).

The design dissolves the three recorded defects of the outbox path: agents
needing `main` for mail, human pull requests whose only content is flushing
an outbox, and the 2026-08-17 loss where a sender-side reset destroyed
undelivered mail.

## The Owner's Ruling On Timing

The owner judges this small enough to implement **in time for V1**, but
requiring attention to detail — so it is deliberately not being done now.
Two consequences:

- This delivery does not itself unfreeze `WORKFLOW.md`. The freeze
  (2026-08-30) holds; implementing this is an explicit, owner-directed
  exception when he schedules it, or part of the release-candidate workflow
  check, whichever comes first.
- Until then the outbox rules remain the operative protocol.

## The Details That Need The Attention

Named so the implementation session starts from them rather than
rediscovering them:

- the migration moment: draining every existing outbox before the rule
  changes, so nothing is in flight across two protocols;
- exact reset semantics (`push --force-with-lease` after ingest, or
  delete-and-recreate) and what a sender's retry loop does when the ref
  moves under it;
- whether `mail/*` needs a branch-protection note in the coordination
  baseline, and what the rules say for a project whose host has no branch
  permissions at all;
- the session-start rule's wording: fetch-your-mailbox must not become
  another restatement that goes stale in every intake README (the READMEs
  are pointers now, per the 2026-08-30 ruling);
- registration and conclusion messages travel the same way — retiring *The
  Outbox Branch* section cleanly, with credit for what it got right; and
- the invariant checker (`devcapsule workflow verify`, spiked separately)
  should learn the three-place check in the same change, so the new
  protocol ships with its guard rather than ahead of it.

## Delivery Note, Recorded Latitude

This item cites a spike note that exists on `project-management/coordination`
and not yet on `main`; per the recorded target-lands-no-later-than-the-
reference precedent it travels on that branch and reaches `main` with the
note it cites.

Priority within your queue is yours; the owner's timing ruling above is the
sequencing constraint.
