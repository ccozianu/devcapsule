# Intake: State That The Outbox Is A Mechanism, Not A Model Entity

Delivered: 2026-08-18

From: `project-management`, at the product owner's request. The product owner
proposed the outbox originally and reports that the current text does not convey
the intent behind it.

## What Is Being Handed Over

*The Outbox Branch* in `WORKFLOW.md` describes the outbox thoroughly but never
states what kind of thing it is. The product owner's stated intent is that the
outbox is a mechanistic Git convention, not a fundamental entity in the
project's information model: its purpose is to let a workstream merge to `main`
— and so reach another workstream's `intake/` — without risking that its own
work-in-progress rides along into `main`.

Half of that is documented. The work-in-progress risk is explicit under *What it
must never carry*. The other half, the outbox's standing in the information
model, is not stated anywhere, and the document's structure implies the
opposite.

## Why It Belongs Here

`WORKFLOW.md` and the concepts it defines are this workstream's subject.
`project-management` can report that the intent did not survive contact with a
reader, but it should not decide how the protocol expresses its own primitives.

## Evidence

An agent reading `WORKFLOW.md` in full on 2026-08-18, with no prior context,
came away treating the outbox as a required protocol entity and described using
it as an obligation the workstream owed rather than as the safe way to perform a
merge. The product owner corrected the framing directly. The reading is
defensible from the text:

- **Restriction 13** reserves `<mnemonic>/outbox` as a branch name in every
  workstream, placing it beside restriction 12's reserved `project-management`
  mnemonic — which *is* a model entity.
- **Restriction 6** carves an explicit exception for the outbox in the rule
  governing how branches start from and return to `main`, which reads as the
  model accommodating a first-class thing.
- **Selecting Work At Session Start, rule 6** gives a checked-out outbox
  identity semantics: it "identifies its workstream but is not an editing
  checkout."
- *The Outbox Branch* opens with "Every workstream has one standing branch named
  `<mnemonic>/outbox`" and closes with an **Ending** rule for it. Possession and
  a lifecycle are entity properties.
- The section's framing sentence — "Intake defines where a message lands. The
  outbox defines how it travels" — pairs it with intake as a peer concept.
  Intake is a model entity; the parallel invites the reader to conclude the
  outbox is one too.

The stated rationale also leads with a different argument than the product
owner's. The section's opening reason is that a working branch may run for weeks
and anything riding along is invisible until it merges. The "do not push
work-in-progress to `main`" purpose appears later and as a prohibition, not as
the reason the mechanism exists.

## Consequences Already Observed

The ambiguity leaves questions the text cannot answer:

- Would a clean throwaway branch cut from `main`, carrying only the intake file
  and deleted after merge, satisfy the protocol? Under the intent, yes — it is
  equally safe. Under restriction 13 and "every workstream has one standing
  branch," it reads as non-compliant.
- "Its own `<mnemonic>/outbox` is created on first use, not at registration"
  in *Beginning A Workstream* sits awkwardly beside "Every workstream has one
  standing branch named `<mnemonic>/outbox`." One says a workstream possesses
  it; the other says it may not exist.
- On 2026-08-18 `project-management` had no outbox branch at all, nine days
  into the convention, while two other workstreams did. Nothing in the text
  distinguishes "has not needed to send yet" from "is missing a required part."

## Sender's Analysis

Offered as analysis, not as constraints on this workstream's judgment.

- What appears to be missing is a single sentence of status, near the top of the
  section, saying that the outbox is a Git convention serving the model rather
  than part of it, and that what the model requires is that items reach
  `intake/` on `main` without the sender's unfinished work reaching `main` with
  them.
- If that is right, the reserved-name restriction is a convention worth keeping
  for predictability — an agent can find a workstream's outbox without asking —
  rather than a constraint the model imposes. Saying which it is would resolve
  the throwaway-branch question in either direction.
- Deciding that the outbox genuinely *is* a model entity, and that the product
  owner's framing should not be adopted, is a valid outcome. The finding is that
  the document does not currently say either way, not that a particular answer
  is correct.
- This may generalize past the outbox: the document defines several
  Git-mechanical conventions alongside model concepts without marking which is
  which. Whether to address that broadly or only here is this workstream's call.

## What Accepting Would Mean

A statement in `WORKFLOW.md` of what kind of thing the outbox is, reconciled
with restrictions 6 and 13, with *Beginning A Workstream* step 8, and with
whatever it implies for alternative branch arrangements that carry the same
guarantee.
