# Intake: Whether The Workflow Should Be Packaged As A "Skill"

Delivered: 2026-08-17

From: `workflow-improvements`, relaying a product-owner question raised while
deciding to leave that workstream.

## What Is Being Handed Over

Today the workflow is a `WORKFLOW.md` file referenced from `AGENTS.md`. The
question is whether it would be better structured and advertised as a "skill" —
the packaging some agent vendors provide for on-demand instruction sets.

Decide it as a feature, a task, or a rejection.

## Why It Belongs Here

Packaging the product's workflow for particular agent vendors is a product
decision that touches `D-0005` and the V1 component selection, both of which are
yours. `workflow-improvements` owns the protocol's content, not how the product
distributes it.

## The Recommendation On The Question As Asked

Recommended against, on three grounds that are already project decisions rather
than opinions:

- skills are a vendor mechanism, and `R-PRODUCT-004` requires the workflow to
  transfer across agents;
- this repository's own `CLAUDE.md` forbids storing anything in agent-specific
  files, for exactly that reason; and
- `AGENTS.md` is the neutral entry point several agents already read, so
  reshaping around one vendor's loader inverts a decision taken deliberately.

## The Finding Underneath It, Which Is Worth Keeping

The instinct behind the question is sound and is not really about skills. What a
skill buys is **progressive disclosure**: load a small core, pull the rest when
the situation calls for it.

`AGENTS.md` currently points at a single 1772-line document with no layering, so
every agent in every session carries the completion sequence, the archive
format, the decision-record ceremony, and the bug-intake protocol whether or not
it will reach any of them. Most sessions reach none. That cost is real,
measurable, and paid on every turn of every session in every adopting project.

The portable fix is the same fix: a small mandatory core covering selection,
synchronization, intake, and checkpoints, with procedure in linked files loaded
on demand. It requires no vendor feature, and it improves the human onramp
question delivered alongside this one as a side effect.

If the vendor packaging is still wanted after that, it has a natural home in a
shape this project already uses: per-agent adapters generated from the neutral
source, materializing per developer after explicit authorization, exactly like
the three agent CLIs the V1 scope ledger curates. That way the neutral source
never depends on the adapter.

## What Accepting It Would Mean

The layering is a real editing job on a 1772-line document plus updates to
`AGENTS.md` and the bootstrap template, and it is the kind of change that risks
breaking cross-references — worth doing once, deliberately, rather than
incrementally.

Rejecting the skill packaging outright costs nothing today and can be revisited
whenever an adapter is actually wanted.

Priority, sequencing, and release target are this workstream's judgment, not the
sender's.
