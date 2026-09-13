---
id: D-0009
title: One Executable Outside And Inside The Container
status: accepted
date-proposed: 2026-09-11
date-decided: 2026-09-11
decided-by: Costin Cozianu
requirements:
  - R-RUNTIME-001
supersedes:
superseded-by:
---

# D-0009: One Executable Outside And Inside The Container

## Context

A CLI that pins a base-image digest cannot also be embedded in that very
image by default without creating a circular content dependency: embedding
the CLI changes the image digest, which changes the CLI's pin. Independently
built outside and inside executables also require a compatibility policy for
the runtime plans they exchange.

v0.2.11 resolved the default path by delivering the launcher executable into
the environment during materialization. The product owner now adopts this
as the continuing design, with explicit user choice able to override it.

## Options Considered

### Option A: The launcher installs itself into the environment

Use the corresponding base selected by normal project/platform resolution
and install the invoking CLI executable into the derived environment.
Cost: executable identity participates in environment-image identity, so a
CLI change requires a new materialization; source-form launches must select
a built runtime artifact explicitly.

### Option B: Use an independently released runtime embedded in the base

Keep the runtime in the base and define which outside CLI versions can use
it. Cost: separate version lifecycles and compatibility checks, with base
publication potentially required for runtime-only fixes. Exact executable
identity is no longer the default guarantee.

## Decision

Adopt option A as the default unless explicitly overridden by user choice:

1. The CLI uses its corresponding base image, as selected by the applicable
   project/platform resolution. "Corresponding" does not require a base tag
   with the same version number as the CLI.
2. During materialization, the CLI installs its own executable into the
   derived Docker image. The outside launcher and inside runtime support
   therefore use the **same executable bytes**, not merely compatible
   versions or matching version strings.
3. An explicit user choice may override the default. A runtime inherited from
   a base image, a stale cached environment, or an incidental version match
   is not an explicit user choice.

This records the owner's decision; it does not introduce a new override
command or claim that every possible override already has an interface.

## Rationale

Runtime identity is established by construction. The base supplies OS and
tool dependencies, while the executable that creates the runtime plan also
executes it inside the container. This removes the content-hash cycle while
retaining pinned base digests and allowing ordinary CLI releases to reuse a
base. Explicit user choice remains available for deliberate departures.

## Consequences

- The default's executable identity must be part of materialization identity;
  an environment carrying an older runtime cannot satisfy a newer launcher.
- Base selection, base maintenance, and CLI releases need not share version
  numbers or publication cadence.
- The corresponding requirement is
  [R-RUNTIME-001](../../requirements/devcapsule/r-runtime-001-launcher-runtime-identity.md).
  Implementation evidence and interface limits live there, not in this record.
- This supersedes the embedded-runtime default described in D-0004's proposed
  base-build design and the embedded-runtime examples in D-0007's historical
  amendments. D-0007's resolution and verification model remains in force;
  its accepted Decision and Rationale are not rewritten.

## Reopen If

The product owner changes the default, or a supported execution environment
cannot run the launcher artifact inside its corresponding container. An
individual user's explicit override does not change the product default.
