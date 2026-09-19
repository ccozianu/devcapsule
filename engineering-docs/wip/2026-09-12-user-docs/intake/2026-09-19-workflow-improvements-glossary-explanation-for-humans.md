# Intake: Explain The Workflow's Terms For Humans, Defining None

Delivered: 2026-09-19

From: `workflow-improvements`, recording a product-owner decision of the same
day about where the workflow's information model lives.

## What Is Being Handed Over

`WORKFLOW.md` now opens with a *Glossary*: every term the workflow uses with a
fixed meaning, defined once in plain words, with where it lives and what it
must not be confused with. That is the normative half and it stays in the
definition, because the rules cite it and agents read it there.

The other half is yours. The owner decided that the explanation humans learn
from belongs in user documentation: why these concepts exist, how they fit
together, worked examples, a diagram if one helps, and the redundancy a
person needs and an agent does not. The V1 ledger's `in-v1` row for a
human-readable workflow onramp is the place it was already expected.

## The One Rule That Keeps The Two From Drifting

The user document may explain any term and defines none. Every term it uses
exists in the *Glossary* under that name. A term that needs explaining but is
not in the glossary is a defect in the glossary, to be delivered to
`workflow-improvements` through its intake rather than defined locally. This
is checkable mechanically and is stated in `WORKFLOW.md` under *How To Read
This Document*.

## The Settled Names

Write against these; the older names remain understood as synonyms for one
release and are then retired:

- workstream name (was mnemonic)
- decision, decision log (was disposition, disposition log; the file keeps
  the name `intake-dispositions.md`)
- status file (was handoff)
- workstream list (was registry)
- judgment where this document is silent (was latitude)
- finishing (was finalization)
- milestone and stage are optional planning words; no rule depends on them
- priority for requirements and backlog items: `gating`, `wanted`,
  `optional`, `later`

## Why It Belongs Here

`docs/` is user-docs' territory and voice. `workflow-improvements` owns the
definition and the glossary, not the explanation.

## What Accepting Would Mean

Writing the human-facing explanation of the workflow's terms and structure
against the glossary, in `docs/`, under the drift rule above, when this
workstream resumes. Nothing here changes the release schedule.
