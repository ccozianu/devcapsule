# Intake: `project-management` Is Now A Reserved Workstream

Delivered: 2026-08-16

From: `workflow-improvements`, at the product owner's direction on 2026-08-16.

## What Is Being Handed Over

The `workflow-improvements` backlog item "make `project-management` a mandatory
permanent workstream" is implemented. `WORKFLOW.md` now defines *Initializing
Multiple-Stream Mode* and *The Reserved `project-management` Workstream*,
restriction 12 reserves the mnemonic, and `AGENTS.md`, the reusable bootstrap
template, and `R-PRODUCT-006` agree. Root `CURRENT-STATUS.md` records that this
repository's instance is no longer a one-off.

Those changes are committed on `workflow-improvements/intake` and reach `main`
through that workstream's pull request. This item travels the outbox, so it may
well arrive first; read the branch if the sections are not on `main` yet.

One part of the reconciliation cannot be done by the sender. This workstream's
handoff at
`engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md` carries a
*Lifecycle Exception* section stating that the product owner opened this
permanent workstream "as a one-off operation before the general workflow
defines it", and that `workflow-improvements` owns formalizing that exception.
That is now stale in both halves. Restriction 11 makes another workstream's
handoff a carve-out, so `workflow-improvements` reports the staleness here
rather than editing it.

## What Accepting Would Mean

Replace the *Lifecycle Exception* section with a statement that this workstream
is the reserved one required of every multiple-stream project, conforming to
the general rule rather than excepted from it. Two facts are worth keeping:

- The workstream predates the rule; it was opened on 2026-08-09 by explicit
  product-owner decision and the rule was written on 2026-08-16.
- One narrow adoption exception survives. This repository adopted
  `multiple-streams` on 2026-08-08 and created the reserved workstream on
  2026-08-09, so its immutable start date is one day later than initialization.
  A conforming project creates both in the same commit.

The retirement pointer can also go. `WORKFLOW.md` now defines retirement:
migration back to `single-stream`, in one commit on `main`, after every
ordinary workstream has been concluded.

## What Changed That This Workstream Should Read

The scope section is normative now, and it constrains this workstream rather
than merely describing it. Three exclusions are stated: it is not a second
registry, not an implementation catch-all, and not the owner of other
workstreams' state. The third restates restriction 11's carve-out. The second
says that work fitting no open workstream is a reason to *begin* one, which is
this workstream's decision to make and hand over, not work for it to perform.

Its coordination authority is recorded as advisory, not procedural: it does not
gate other workstreams' commits, integrations, or checkpoints.

## Evidence

- `WORKFLOW.md`, *Definition And Restrictions* restriction 12, *Initializing
  Multiple-Stream Mode*, and *The Reserved `project-management` Workstream*.
- `R-PRODUCT-006` statement and verification list.
- The stale text: this workstream's handoff, *Lifecycle Exception*.

Priority and sequencing are this workstream's judgment, not the sender's.
