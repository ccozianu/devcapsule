# Intake: Implement External-Resource Ownership And Reaping In Stage 7

Delivered: 2026-08-17

From: `workflow-improvements`

Derived work, not a refusal. `workflow-improvements` acknowledged the
external-resource ownership item on 2026-08-17 and owns the *convention*. This
item is the *implementation*, which that workstream will not write and which
this workstream's Stage 7 is already scoped for.

## What Is Being Handed Over

Implementing external-resource ownership and reaping: making containers,
images, volumes, host ports, and state roots carry or derive an owning
workstream and run identity, and providing one way to enumerate what is held
and for whom.

Closing
[the detached-successor cleanup bug](../../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
falls out of this rather than being separate work.

## Why It Belongs Here

This workstream's own *Next Resumable Task* scopes Stage 7 as proving
"persistence and deterministic cleanup", and item 4 of the Stage 6 list defers
removing both exact containers and run-owned staging until Stage 7 does so.
That is this work under a different name.

`recursive-e2e` also already carries the only ownership model in the
repository: the `devcapsule.e2e.*` labels. The convention being written is in
large part a generalization of what this workstream discovered by needing it.

The original item observed that the implementation "may well land elsewhere —
the cleanup bug names recursive-dogfood Stage 7 as its natural home".

## Dependency

Stage 7 needs the convention before it can implement against it. The convention
is item 4 in `workflow-improvements`'s ordered work and is deliberately last
there, since its main consumer is not ready. If Stage 7 becomes ready first,
say so and it will be reordered — that is a cheaper conversation than either
workstream guessing.

Do not wait silently. A dependency nobody mentions is how both sides end up
blocked on each other.

## What Accepting Would Mean

Stage 7 implements against the convention rather than inventing a second
ownership model, and the cleanup bug closes as a consequence. If Stage 7
discovers the convention is wrong or insufficient in practice, that finding
goes back to `workflow-improvements` through this workstream's outbox — the
convention is protocol and is meant to be corrected by use.

## Evidence

- `WORKFLOW.md` and `AGENTS.md` contain no guidance on containers, images, host
  ports, volumes, or shared configuration roots, yet every concurrency hazard
  observed during the recursive E2E cycle was outside Git.
- A fixed container name, `devcapsule-sample-todo-db`, is hard-coded in the
  first sample's compose file; two concurrent sample workstreams collide
  immediately.
- A fixed host port already collided with an unrelated PostgreSQL on the
  development host, with entirely sequential work.
- Isolating a verification run required hand-rolled `HOME` and `XDG_*` roots,
  with no convention saying to do this or where.
- An image tag was reused because it happened to be unpublished; two agents
  building bases would race on it.
- The existing rule against selecting cleanup targets by name or prefix makes
  conservative inaction the only safe response today, so detached containers
  accumulate without bound.
- The V1 scope ledger row for the contained display requires dynamically
  allocated loopback ports per capsule, which needs this convention to be safe
  under concurrency.

Priority and sequencing are this workstream's judgment, not the sender's.
