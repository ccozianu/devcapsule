---
id: D-0015
title: A Project Constrains Its Base Directly, Not Through Capabilities Or Components
status: proposed
date-proposed: 2026-10-25
date-decided:
decided-by:
requirements: []
supersedes:
superseded-by:
---

# D-0015: A Project Constrains Its Base Directly, Not Through Capabilities Or Components

In scope for V1. Tabled by the product owner on 2026-10-25, during the
0.3.0 candidate cycle, with the design and the implementation deferred to
V1; this record keeps the considerations so far. Nothing here is built.

## Context

The platform lock pins one exact base: its registry digest, the launcher
that built it, and since rc5 its contract, `<family>@<recipe>`, with the
recipe source path since [PR #284](https://github.com/ccozianu/devcapsule/pull/284).
The project owner does not choose it. `init --regenerate` copies the
newest pin of the embedded resolution matrix, and the constraint that
made a base acceptable is recorded nowhere, so regeneration cannot honour
it and a newer launcher cannot refuse an old lock for the right reason.

Two cases made this visible on 2026-10-25.

- **The web console.** It lives in the base from recipe 10 and needs
  recipe 11. Until the recipe-11 base was published and pinned, every
  project on the default pin, `ubuntu-24.04@9`, ran without a console,
  and the AI Learning bootstrap project could not reach one by any route:
  a hand-edited digest is untracked by the matrix, a locally built base
  cannot be named in the lock, and the per-checkout override
  `config authorize base-image <local image>` is refused when the manifest
  carries a minimum version, because a local base cannot establish a
  guarantee (`configuration/model.py`). Publishing the base closed this
  case; it did not give the project a way to say "recipe 11 or later".
- **GPU projects.** The next sample project runs machine-learning course
  work and needs an NVIDIA base: the `nvidia-cuda-devel` recipe exists,
  status `wip`, on `nvidia/cuda:12.8.1-devel-ubuntu24.04`, labelled with
  the GPU vendor and the CUDA version. By the matrix's rules it is a
  second base family, inheriting no validation. The least the launcher
  must be able to say is: this checkout must use a GPU-enabled base. The
  same project will later want a Python environment with the usual
  scientific libraries and a notebook endpoint beside the IDE; those are
  capabilities and components, not part of this decision.

## Options considered

1. **A base-supplied capability.** `cuda` joins `python`, `node` and
   `java` as a capability the base supplies with a version from its
   label; only the NVIDIA family's pins satisfy it; `config require
   'cuda>=12.8'` resolves onto that family or is refused by the existing
   path, "No base ships everything this project needs". The resolver
   needs no change. The console case has no capability to name.
2. **Marker components.** Components that exist in the matrix only when
   the base is of a given family or recipe, so that requiring one forces
   the base. Nothing new in the model either.
3. **A direct constraint on the base.** The manifest states what it
   needs of the base in the base's own vocabulary: the family, a minimum
   recipe within it, and the traits the base's labels declare, the GPU
   vendor and the CUDA version among them. Regeneration pins the newest
   matrix base that satisfies the constraint. A checkout's local base is
   checked against the constraint by its labels instead of being refused
   outright. The refusal names the constraint and the base that fails it.

The owner's view on 2026-10-25: options 1 and 2 work through the matrix
and both are indirect; the user would have to understand that a
capability or a component stands for a property of the base, which
confuses the concepts the capabilities and components order just made
clean. A straightforward addition to the base image concept is
preferable. Option 3 is the direction; its shape is the V1 design.

## Decision

Open; the direction is option 3. What the design must settle:

- The manifest's form for the constraint and the words the owner types:
  a family, a minimum recipe, and labelled traits, in the `>=` form the
  minimums use where a version is meant.
- How a trait is declared by a base so that the constraint and the label
  agree: the recipe writes the label, the matrix pin states it, the
  contract carries it, as `services` is carried today.
- What the lock records: the exact base as now, plus the constraint it
  satisfied, so a later regeneration and a later launcher read the
  intent and not only the result.
- The local override: satisfied by labels, refused by name when the
  labels fall short, and no longer refused merely because the manifest
  has a minimum.
- The host side of a GPU: whether the device is an authorization node the
  project recommends and only the user grants, as `network host` is, or
  stays the saved Docker argument `--gpus all` it is today. The boundary
  doctrine of D-0012 argues for the node; the owner has not ruled.
- The NVIDIA base: leaves `wip`, is built from a public revision and
  published, becomes the first pin of its family; its evidence needs a
  machine with the hardware.

## Consequences

Until this is built, a project that needs a particular base has one
route: the published default pin, moved forward by DevCapsule's releases.
The 0.3.0 cycle takes that route for the console: the recipe-11 base is
published and pinned, and a regenerated lock follows it. No recipe
minimum and no capability is added for the base in 0.3.0; the
capabilities and components model stays as decided on 2026-10-24.

## Reopen If

The NVIDIA base is to be published, or the sample project that needs it
starts, whichever comes first: either forces the design above, since a
second family cannot be reached by regeneration without a constraint.
