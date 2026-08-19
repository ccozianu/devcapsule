# Intake: Making The Workflow Replaceable, And Possibly Extracting It

Delivered: 2026-08-17

From: `workflow-improvements`, relaying a product-owner position raised while
deciding to leave that workstream.

## What Is Being Handed Over

The product owner's position: the workflow is to some extent orthogonal to the
essence of this project. At minimum, adopters should be able to install a
different workflow; beyond that, the workflow's instructions and documentation
might belong in their own GitHub repository.

Two decisions, separable, and one is a prerequisite for the other.

## Why It Belongs Here, And Why It Cannot Be Only A Task

`R-PRODUCT-004` states that the workflow "is part of the product idea, not just
an internal convenience". The premise that it is orthogonal contradicts an
accepted requirement. That is not an objection — the requirement may well be
wrong, and it was written before the workflow grew to its present size — but it
means the extraction question needs a `D-####` decision record amending or
reinterpreting `R-PRODUCT-004`, not a task ticket. Requirement-level changes and
release scope are yours.

## The Recommendation: Do The Seam Now, Decide Extraction Separately

**The seam is the cheap half and the prerequisite for the expensive half.**
State what the product actually depends on, which as far as this workstream can
tell is exactly three things:

- `AGENTS.md` as the entry point an agent reads first;
- `workflow-type` in `.devcapsule/devcapsule.toml`; and
- the `engineering-docs/` directory layout.

Everything else in `WORKFLOW.md` is protocol content that an adopter could
replace wholesale. Saying so — in `WORKFLOW.md`'s *Applying This To Other
Projects*, which currently assumes adopters take this workflow rather than
choose one — delivers the "offer adopters the option" value immediately, and it
is a documentation change rather than an architectural one.

Without that seam, extraction is guesswork about what is coupled. With it,
extraction later becomes packaging.

## The Costs Of Extraction, Named So They Are Not Discovered Late

- **The dogfood loop would cross a repository boundary.** `workflow-improvements`
  improves `WORKFLOW.md` in-tree, and its intake, outbox, disposition log, and
  registry row all live here. Move the file and either that machinery follows it
  out, or the workflow that governs cross-workstream work has to operate across
  two repositories — which nothing in the protocol covers.
- **A separate repository implies versions.** Which implies adopters pinned to
  old ones, which implies migration. None of that exists today, and the workflow
  has changed eleven times in two days.
- **Submodule versus vendoring is a live tradeoff**, and `sample-projects` is
  deciding the same question separately for its own submodules. Worth deciding
  once, consistently.

## What Accepting It Would Mean

The seam: one editing session, no code, no new failure modes.

The extraction: a decision record, a repository, a distribution mechanism, a
versioning story, and a resolution for how a workflow-improvement cycle runs
across two repositories. Not V1-shaped as far as this sender can see, though the
release target is yours to set.

## Related

Delivered alongside two other packaging questions the same day — the
human-readable document and layered on-demand loading. A decision to extract
would largely determine both, so you may prefer to take all three together.

Priority, sequencing, and release target are this workstream's judgment, not the
sender's.
