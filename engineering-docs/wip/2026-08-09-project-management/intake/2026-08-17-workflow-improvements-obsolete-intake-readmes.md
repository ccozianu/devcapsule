# Intake: Retire Obsolete Intake README Boilerplate

Delivered: 2026-08-17

From: `workflow-improvements`, at the product owner's direction.

## What Is Being Handed Over

Three workstream-local `intake/README.md` files repeat protocol text that the
current workflow has superseded:

- `engineering-docs/wip/2026-08-06-recursive-e2e/intake/README.md`
- `engineering-docs/wip/2026-08-09-project-management/intake/README.md`
- `engineering-docs/wip/2026-08-14-sample-projects/intake/README.md`

The product owner considers these files obsolete for the purpose of the
`workflow-improvements` workstream. That workstream should not clean up files
inside three other workstreams merely because it found the duplication. Route
their replacement, removal, or other disposition to an appropriate owner.

## Why It Belongs Here

This is now a cross-workstream maintenance and ownership question, not an open
workflow-protocol design question. `project-management` owns routing and
lifecycle decisions, while `workflow-improvements` remains open but paused
after publishing the corrections it has completed.

## Evidence

All three files still say that intake items are "accepted, deferred, or
rejected", that senders deliver them "to `main` promptly", and that recipients
record the disposition only in their handoff before removing the file. Those
statements duplicate protocol and are now stale:

- disposition has exactly two outcomes, acknowledge or forward; deferral is
  not a third outcome;
- senders deliver through their own `<mnemonic>/outbox` branch;
- disposition also writes `intake-dispositions.md` in the same outbox commit
  that deletes the item from `main`;
- intake gates workstream completion; and
- items from `project-management` cannot be forwarded.

`workflow-improvements/intake/README.md` already points to `WORKFLOW.md` as the
authority rather than attempting to carry a complete local copy. `WORKFLOW.md`
remains the normative source for the intake and outbox protocols.

## What Accepting Would Mean

Decide who removes or replaces the three obsolete files, or explicitly decide
that they should remain with a clear non-normative purpose. If they are kept,
make them thin pointers to `WORKFLOW.md` so future protocol changes do not
require synchronized edits across every open workstream.

Priority, sequencing, and whether this is assigned to existing workstreams or
made separate maintenance work are `project-management` decisions.
