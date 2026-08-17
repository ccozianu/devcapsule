# Intake: Whether The Workflow Needs A Human-Readable Document

Delivered: 2026-08-17

From: `workflow-improvements`, relaying a product-owner question raised while
deciding to leave that workstream.

## What Is Being Handed Over

`WORKFLOW.md` is written for an agent to act on correctly and efficiently. The
question is whether the project also owes its human readers — its own product
owner, and every adopter — something structured for understanding rather than
for lookup.

Decide it as a feature, a task, or a rejection. `workflow-improvements` did not
acknowledge it, for the reason in *Why It Belongs Here*.

## Why It Belongs Here

It is a scope call, not a protocol correction. Whether the project owes adopters
a readable workflow before V1 is a release-content decision, and
`workflow-improvements` is pausing with its one remaining item blocked, so
acknowledging this would place it in a queue nobody is selecting.

`R-PRODUCT-004` is the requirement it serves: the workflow must be adoptable by
users of environments this project creates. An adopter who cannot understand it
cannot adopt it, so this is arguably already a validation signal of a
requirement you own the release readiness of.

## The Evidence

`WORKFLOW.md` is 1772 lines across roughly 45 top-level sections, ordered as a
normative reference. Nothing in it is wrong for its primary audience; the
question is whether that audience is the only one.

Three sections written on 2026-08-17 are already human-facing and were written
that way deliberately: *Purpose And Principles*, *How To Read This Document*,
and *Checkouts, Branches, And Workstreams*. Together they are roughly 150 lines
and cover the model rather than the procedure. That is most of what a separate
introduction would have to say.

## The Recommendation, Which Is An Argument Against The Obvious Shape

A second, parallel document is the shape to avoid, and the reason is empirical
rather than aesthetic. This project has now paid twice for duplicated normative
text:

- each workstream's `intake/README.md` restated the delivery rule, so one
  protocol change made four of them stale simultaneously, three of which the
  author was barred from editing by restriction 11's carve-out; and
- two claims about Git behaviour in `WORKFLOW.md` survived review and were
  disproved only by the first branch to complete a round trip through `main`.

Two documents describing one protocol diverge, and the non-normative one loses,
because nobody's work breaks when it is wrong.

The cheaper shape, if this is accepted at all: extend the existing front matter
into an explicit onramp — "if you are a human, read these sections and stop" —
and mark the remainder reference material. That adds no new staleness surface,
because there is still exactly one normative document.

## What Accepting It Would Mean

Someone writes an onramp inside `WORKFLOW.md` and marks the rest reference.
Roughly a session's work in the recommended shape; substantially more if a
separate document is chosen instead, plus a permanent obligation to keep two
documents agreeing.

It interacts with the two items delivered alongside this one — layered loading,
and extraction to a separate repository. All three are about the workflow's
packaging rather than its rules, and a decision on extraction would largely
determine this one. You may prefer to take them together.

Priority, sequencing, and release target are this workstream's judgment, not the
sender's.
