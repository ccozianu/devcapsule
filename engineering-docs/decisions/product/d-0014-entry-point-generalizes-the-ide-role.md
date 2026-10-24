---
id: D-0014
title: The IDE Role Stays As It Is, Or Generalizes To An Entry Point That Owns The Container's Lifetime
status: proposed
date-proposed: 2026-10-24
date-decided:
decided-by:
requirements: []
supersedes:
superseded-by:
---

# D-0014: The IDE Role Stays As It Is, Or Generalizes To An Entry Point That Owns The Container's Lifetime

In scope for V1. Tabled by the product owner on 2026-10-24 from the
discussion of the [capabilities and components work order](../../work-orders/2026-10-24-capabilities-and-components.md);
the order keeps `ide` as the command-line word and decides nothing here.

## Context

One component per launch is the one the capsule starts for the user:
PyCharm, IntelliJ, Eclipse, Rider or VSCodium today, selected by
`config ide`, recorded in the lock as `components.interactive-surface`.
The contract the launcher keeps with it is small and uniform: a log, the
persisted directories it declares, the project path on its command line
in the form it understands (`-data` for Eclipse, the project argument for
JetBrains, the folder for VSCodium), and the display. What this component
actually owns is the lifetime of the Docker container: the capsule ends
when it exits. It uses the display; it does not own it. On Linux the
launcher takes extra steps for X integration, the contained desktop or
host X11 passthrough, and those remain a special case of the display, not
of the role.

The owner's observation: the role can be generalized and the code made
simpler and less case-based by naming it what it is, the capsule's
entry point, and by making the display a declaration of the component
rather than a property of the role. Two future shapes then become
expressible without a new concept: a capsule whose entry point needs no
desktop at all, and, by V2, an entry point that coordinates a desktop
shared by several graphical tools.

## Decision

Open. The two options:

1. **Stay with what we have.** The role is called the IDE at the command
   line and in the documentation, exactly one per launch, and it is
   assumed to use the display. The launcher's one special branch and the
   catalog's list of five names remain.
2. **Generalize to the entry point.** The role is named `entry-point`:
   the component the capsule starts for the user, which owns the
   container's lifetime and declares whether it uses the display. Exactly
   one per launch for V1. `config ide` and `--ide` become retired
   spellings of `config entry-point` and `--entry-point`; the lock's
   `interactive-surface` becomes `entry-point`; the documentation says
   "entry point, usually your IDE". The headless shape and the shared
   desktop are not built until a component needs them; the contract
   merely holds them.

## Rationale

For option 2: every launcher step for the IDE is already a per-component
declaration except the branch that names the role; the display is the
only thing the role assumes, and the assumption is false for the shapes
the owner foresees. For option 1: "entry point" is also Docker's word for
the container's first process, which in a capsule is DevCapsule's
supervisor, a moment of confusion for people who read Dockerfiles; and no
component in the catalog today runs without a display, so the
generalization buys nothing until one does.

## Consequences

Whichever option is taken, the launcher's and the documentation's words
say that this component uses the display and owns the container's
lifetime; no record says it owns the display. The capabilities and
components work order is written with that wording and with `ide` kept.

## Reopen If

A component that needs no display enters the catalog, or a second
graphical tool is to share the desktop; either forces option 2 or an
explicit refusal of it.
