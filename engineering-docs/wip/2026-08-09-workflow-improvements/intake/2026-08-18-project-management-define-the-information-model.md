# Intake: Define The Workflow's Information Model, Minimally

Delivered: 2026-08-18

From: `project-management`, at the product owner's direction. This is a task,
not a question.

## What Is Being Handed Over

Define the information model of the workflow this project proposes to its
adopters: the set of things the workflow talks about, what each one is, how they
relate, and what each is called.

Three constraints on the result, given in the product owner's words:

- **"As simple as possible, but not simpler."** The model is minimal. A concept
  earns a place only if removing it would leave something the workflow genuinely
  cannot say. Ceremony that merely feels orderly is not earning its place.
- **Optimize for human familiarity, learnability, and naturalness.** Where an
  ordinary word already names the concept, use the ordinary word. Coin a term
  only when no existing word fits, and then define it where a reader meets it
  rather than 1100 lines later.
- **Write for a reader whose first language is not English.** The product owner
  states this of himself, and every international adopter is in the same
  position. Prefer common, internationally legible vocabulary over idiomatic,
  literary, or rare English. A word that a fluent non-native reader must look up
  is a defect, not precision.

The deliverable is the model itself — the concepts, their relationships, and
their names. Whether it lands as a section of `WORKFLOW.md`, a separate
document, or a renaming pass across the existing text is yours to judge, subject
to the packaging decisions noted below.

## Why It Belongs Here

`workflow-improvements` owns the workflow's rules and their expression.
`R-PRODUCT-004` states that the workflow is part of the product idea, not an
internal convenience, and that it must be adoptable by users of the environments
this project creates. Vocabulary load is therefore a validation signal on an
accepted requirement: an adopter who must learn a private language before
starting has not been given an adoptable workflow.

The product owner has explicitly accepted the present ambiguity for the duration
of the current dogfood work. This item is not a request to stop and fix it now.
It is the record that the model is undefined, so that it is settled deliberately
rather than accreted further.

## The Evidence

Measured on 2026-08-18 against `WORKFLOW.md`, `AGENTS.md`, and `README.md`.

An adopter faces roughly 111KB across four documents and about nineteen coined
terms, with **no glossary**. The only terminology section, *Release, Milestone,
Stage, Task, And Checkpoint Terminology*, begins at line 1138 of 1838 — 62% of
the way through — and defines five of the nineteen.

Occurrences in `WORKFLOW.md`: workstream 221, handoff 68, intake 49, outbox 42,
checkout 35, mnemonic 31, registry 29, WIP 26, disposition 22, checkpoint 21,
milestone 13, deliverable 10, latitude 7, finalization 6, delivery method 6,
open threads 5, adoption exception 3, integration target 2.

Three specific defects, offered as evidence rather than as the answer:

1. **`registry` carries four unrelated meanings in this repository** — the
   open-workstream registry, a container image registry ("published, registry
   digest"), the XDG developer-owned checkout registry that `project list`
   reads, and the npm registry on the firewall allowlist. Only the first is
   workflow vocabulary.
2. **`ledger` appears zero times in `WORKFLOW.md`.** It is not workflow
   vocabulary at all. It entered on 2026-08-16 as an agent-coined document title
   (`v1-scope-ledger.md`) and was never defined anywhere. The product owner did
   not recognize it when he met it, which is the evidence that matters.
3. **`mnemonic` is used 31 times where `name` would do**, and `disposition` 22
   times where `decision` would do. Neither carries meaning the plain word
   loses.

A further observation for the model rather than the naming: the five-level
hierarchy of release, milestone, stage, task, and checkpoint is a large
structure for the solo developer in the project's own use-case set. Whether a
user needs all five levels is a model question, and is squarely in scope here.

There is no precision-versus-plainness tradeoff to manage. Precision comes from
defining a term, not from choosing an unusual one; an agent reads a common word
exactly as reliably as a rare one. Plainness is therefore free on the agent side
and paid for only on the human side, which is the side that is currently losing.

## What Accepting It Would Mean

The naming half is mechanical once the model is settled, and does not wait on
anything. The model half is genuine design work and should be done first, since
renaming before the concept list is settled would be done twice.

This item interacts with the three packaging items `workflow-improvements` sent
to `project-management` on 2026-08-17 — layered loading, extraction to a
separate repository, and whether the workflow owes humans a readable document.
Those
decisions are `project-management`'s and are not delegated by this item. If
extraction is later chosen, a settled information model is a prerequisite for it
rather than wasted work, because an extractable workflow must first be able to
say what it is made of.

Items sent by `project-management` cannot be forwarded. If you judge the task
wrong, or wrongly sequenced against the backlog item you already hold, raise it
with the product owner.

Priority within this workstream, and the release target, are open. Nothing here
is claimed for V1; the V1 scope decision has not been made.
