# Intake: External-Resource Ownership And Reaping

Delivered: 2026-08-16

From: `project-management`

Originally handed over by the
[portfolio checkpoint of 2026-08-15](../../2026-08-09-project-management/2026-08-15-portfolio-checkpoint.md)
as item 4 of four, and never delivered. Redelivered here.

## What Is Being Handed Over

The workflow protocol governs Git state well and external state not at all.
`WORKFLOW.md` and `AGENTS.md` contain no guidance on containers, images, host
ports, volumes, or shared configuration roots, yet every concurrency hazard
observed during the recursive E2E cycle was outside Git.

Every container, image tag, volume, host port, and state root should carry or
derive a workstream identity, with names derived rather than fixed, plus one way
to enumerate what is currently held and for whom.

## Why It Belongs Here

The convention is a workflow concern that spans every workstream, and no single
implementing workstream can define it for the others. The *implementation* of
reaping may well land elsewhere — the cleanup bug names recursive-dogfood
Stage 7 as its natural home — but the ownership convention that makes safe
reaping possible is protocol.

## Evidence

Observed during the week preceding 2026-08-15:

- A fixed container name, `devcapsule-sample-todo-db`, is hard-coded in the
  first sample's compose file. Two concurrent sample workstreams collide
  immediately.
- A fixed host port collided with an unrelated PostgreSQL already listening on
  the development host. That failure is real today, with entirely sequential
  work.
- Isolating a verification run required hand-rolled `HOME` and `XDG_*` roots.
  No convention says to do this, or where.
- An image tag was reused because it happened to be unpublished. Two agents
  building bases would race on that tag.
- The shared Docker daemon has no ownership model outside the recursive E2E's
  own `devcapsule.e2e.*` labels, which live in one workstream's code rather than
  in the protocol.

## Related Consequences

- [Detached DevCapsule containers exit and are never cleaned up](../../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
  is the user-visible consequence. The existing rule against selecting cleanup
  targets by name or prefix makes conservative inaction the only safe response,
  so the pile grows without bound. Fixing ownership fixes both.
- The
  [V1 scope ledger](../../2026-08-09-project-management/v1-scope-ledger.md)
  row for the contained display requires dynamically allocated loopback ports
  per capsule, which needs this convention to be safe under concurrency.

## What Accepting Would Mean

A convention stating how an external resource derives its owning workstream and
run identity, how names avoid collision by construction rather than by
discipline, how an agent enumerates what is held and by whom, and what an agent
may and may not remove. Priority and sequencing are this workstream's judgment.
