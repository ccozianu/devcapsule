# Intake: Intake Staleness Is Left To You, Unspecified

Delivered: 2026-08-17

From: `workflow-improvements`, recording a product-owner decision made the same
day.

## What Is Being Handed Over

The intake mechanism now has an acknowledgement path and deliberately has no
staleness signal. `workflow-improvements` will not specify one. Whether
anything detects an item sitting undispositioned, and what, is yours to decide
as you see fit — including deciding that nothing should.

No rule was added to `WORKFLOW.md`. That is the decision, not an omission.

## Why It Belongs Here

Routing and lifecycle are yours, and this is a question about when the project
notices that a workstream has stopped doing something rather than about how the
protocol works.

## The Reasoning You Are Inheriting

V1 cannot be produced while anything remains in its backlog. A rotting intake
item is therefore already caught — by the release gate rather than by a
staleness mechanism — and the workstream that owns release readiness is the one
positioned to notice. A dedicated signal would duplicate a check the project
performs anyway, on a schedule that matters less than it first appears: an item
nobody needed for months cost nothing by waiting for them.

## What Already Exists, So You Are Not Starting Cold

**Acknowledgement is done.** Each workstream now keeps
`intake-dispositions.md` beside its handoff, written in the same outbox commit
that removes an item from its queue. See *The Disposition Log* in
`WORKFLOW.md`.

**That produced an invariant worth knowing about.** On `main`, every item ever
delivered to a workstream is in exactly one of two places: still in its
`intake/`, meaning undispositioned, or in its disposition log, meaning
resolved. Never both, never neither.

That is mechanically checkable, which makes an automated staleness check cheap
should you ever want one — the age of a file in any `intake/` on `main` is the
whole computation. It would fit naturally alongside the documentation-invariant
checking your
[V1 readiness assessment](../2026-08-16-v1-readiness-assessment.md) records as
unowned, where the finding is that 258 tests guard the Python distribution and
nothing guards durable project memory.

## Two Options Considered And Not Taken

Offered so you do not re-derive them, not as constraints.

- **A registry column** showing queue depth and oldest age. Argued against on
  your own evidence: the V1 readiness assessment documents the registry being
  stale in three separate ways as it was written, with "no mechanism that would
  ever surface the disagreement". Another hand-maintained field on a document
  already proven to drift buys little.
- **A sweep at each portfolio checkpoint.** This works, and works for the right
  reason — the checker is not the delinquent party, which matters because the
  failure case is a workstream nobody is working on. It was not adopted because
  `workflow-improvements` should not place a recurring obligation on another
  workstream by writing it into the protocol. Adopting it yourself is a
  different act and entirely open to you.

## One Thing To Note About The Sender

`workflow-improvements` is close to having nothing to do. Its intake is empty,
and one acknowledged item remains — the external-resource ownership convention
— which is blocked on `recursive-e2e` Stage 7. Whether it stays open waiting or
concludes and hands that convention onward is a lifecycle call that belongs to
you, and it is cheaper to make before the workstream idles than after.

Priority and sequencing are this workstream's judgment, not the sender's.
