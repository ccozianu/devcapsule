# Intake: You Own The Workflow Component, Which Is Now In V1

Delivered: 2026-08-18

From: `project-management`, recording a product-owner decision and the ownership
that follows from it.

## What Is Being Handed Over

On 2026-08-18 the product owner decided that **the workflow ships in V1 as an
optional component**, and assigned this workstream responsibility for defining
its final shape.

The decision is recorded as a row in the
[V1 scope ledger](../../2026-08-09-project-management/v1-scope-ledger.md),
*The Workflow Ships As An Optional Component*, verdict `in-v1`. Read the row
rather than this summary for the reasoning; what follows is only what changes
for you.

**The decision.** The workflow developed here is offered to adopters as a
component they may choose, not as something the product imposes. An adopter may
install it, install a different workflow, or use none, and the product works in
each case. The product owner's rationale: many users will not have had time to
develop a workflow that addresses what this one addresses, and are well served
by being able to adopt one; users who already have something better keep it.

**What you now own.** The final shape of the component: what it consists of, how
an adopter obtains and declines it, and what "install a different workflow"
concretely means. Your own earlier assessment — that the product depends on
exactly `AGENTS.md`, `workflow-type` in `.devcapsule/devcapsule.toml`, and the
`engineering-docs/` layout — is named in the row as the natural starting point.

## Why It Belongs Here

You own the workflow's rules and their expression, and this is the workflow
becoming a shipped thing rather than an internal practice. The ownership
assignment is the product owner's, not a claim by `project-management`.

This item exists because the assignment would otherwise live only in a ledger on
another workstream's branch. That is the failure mode this project has already
paid for twice, and a workstream cannot be held to an ownership it was never
told about.

## What Is Decided, And What Is Not

Decided, and not yours to reopen without raising it with the product owner:

- the workflow is in V1;
- it ships as an optional component rather than an imposition; and
- this workstream owns its shape.

Left open, and yours to work through:

- **Whether the component includes verification tooling.** The original design
  assumed the human/agent pair is itself sufficient tooling. The ledger row sets
  out where that assumption held in this repository — everywhere judgment was
  required — and where it failed, which was consistently where verification was
  required. It argues, as an argument and not a specification, for "the agent
  writes and the tool checks": a small set of verifiers and a few mechanical
  actions rather than a workflow engine, since an engine would displace the
  judgment layer that works. You may reach a different conclusion; the row does
  not bind you.
- **The V1 acceptance criteria**, which the row states as far as it can and
  leaves you to complete: an adopter can decline the component without losing
  product function; the product's real dependency on the workflow is stated;
  starting does not require reading the whole normative document first; and the
  evidence is a fresh project in each configuration.

## Sequencing

This is sequenced **behind** the information-model task delivered to you in the
same send. Verification tooling or a component boundary written against terms
that are about to be renamed would be built twice. Define the model, then the
shape, then decide tooling.

Two decisions that touch this remain with `project-management` and are held in
its intake: whether the workflow's text is extracted to its own repository, and
whether it owes humans a separate readable document. Neither blocks you.
Shipping as an optional component is compatible with every outcome of both, and
that is stated in the row so it cannot become an excuse to wait.

## Notes On Status

This workstream is paused as of 2026-08-17. Nothing here asks you to resume; it
asks that when you do resume, this is in your intake rather than in someone
else's document. Priority against your existing backlog item is yours, subject
to the sequencing above.

Items sent by `project-management` cannot be forwarded. If you judge the
ownership misplaced, raise it with the product owner.
