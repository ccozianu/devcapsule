# Intake: Intake Has No Acknowledgement Or Staleness Signal

Delivered: 2026-08-16

From: `project-management`

The product owner has further ideas about how intake should be processed and
has deliberately reserved them for this workstream rather than settling them in
a project-management session. Ask before designing.

## What Is Being Handed Over

The *Workstream Intake* mechanism added to `WORKFLOW.md` on 2026-08-16 is
one-directional. Two gaps follow from that, both identified by the sender
immediately after writing the mechanism.

**No acknowledgement.** A receiving workstream records its disposition —
accepted, deferred, or rejected — in its own handoff, which the sender does not
read. The sender therefore never learns what happened to an item it delivered.
Delivery is fire-and-forget, and the sender's own checkpoint is left asserting
that a handoff occurred with no way to confirm it was received or acted on.

**No staleness signal.** Nothing surfaces an item that has sat undispositioned
for a long time. An ignored intake is silent, which is the same failure class as
the announced-but-undelivered handoff the mechanism was built to fix, one
directory further along.

## Why It Belongs Here

Both are properties of the workflow protocol. The sender created them and should
not also adjudicate them.

## Sender's Analysis

Offered as analysis, not as constraints.

- The cheap symmetry is that dispositioning an item means writing a short reply
  into the sender's own intake, then removing the original. The queue then
  carries replies as well as requests, and "still present" continues to mean
  "not yet decided" in both directions.
- Staleness pairs naturally with the documentation-invariant checking recorded
  as unowned in the
  [V1 readiness assessment](../../2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md):
  an undispositioned item older than some threshold should appear somewhere a
  human actually reads, most obviously the registry.
- The general shape now in place — a shared bus, per-workstream mailboxes, and a
  proposed outbound queue — is message passing between isolated processes. That
  is a well-understood design, and its known failure modes are undelivered
  messages, unacknowledged messages, unbounded queues, and no dead-letter
  handling. The first is now fixed. The rest are open.

## What Accepting Would Mean

An acknowledgement path and a staleness signal defined in `WORKFLOW.md`, or an
explicit decision that fire-and-forget is sufficient and why.
