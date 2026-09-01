---
id: D-0006
title: One Module For Host And Platform Friction
status: proposed
date-proposed: 2026-09-01
date-decided:
decided-by:
requirements: []
supersedes:
superseded-by:
---

# D-0006: One Module For Host And Platform Friction

## Context

Knowledge about the host platform and its environment conventions is
scattered and already drifting:

- `platform_alias()` — the `linux-amd64` platform-identity vocabulary —
  lives in `project_configuration.py`, where no reader would look for it.
- `materialization.py` hardcodes `platform: str = "linux-amd64"` as a
  default parameter in three signatures, silently duplicating that
  vocabulary as string literals.
- The XDG base-directory convention is implemented twice: `persistence.py`
  derives the data/state/cache homes and `project_configuration.py`
  independently derives the config home, each with its own copy of the
  `HOME` fallback pattern.

The resolution-matrix redesign (D-0007) needs a shared `Platform` type as
the key of its public map, which forces the question of where such a type
lives. Neither `project_configuration` nor `resolution_matrix` is that
place. Both failure modes at the extremes are known: large files
conglomerating vaguely related utilities (the current state), and
one-function-per-file fragmentation (not Pythonic either).

## Options Considered

### Option A: Leave definitions where they are, re-export as needed

Cost: the drift continues — the materialization literals and the duplicate
XDG derivations stay, and every new consumer deepens the wrong-module
imports. Solves nothing; listed because it is the default of not deciding.

### Option B: One concept per module (`platform.py`, `xdg.py`, ...)

Cost: fragmentation, and a naming trap — a `devcapsule/platform.py` must
`import platform` from the stdlib inside a file of the same name, which
works mechanically but reads as a hazard. Two- and three-line modules
multiply without a principle bounding them.

### Option C: One module owning host and platform friction

A single `devcapsule/platforms.py` that synthesizes the project's friction
with the host: OS-specific and environment-specific conventions.

Cost: needs an explicit membership rule, or it degenerates into a new
junk drawer under a nicer name.

## Decision

Option C. `devcapsule/platforms.py`, terminal in the package's dependency
graph (it imports nothing of ours), owning:

- **`Platform`**, a `StrEnum` whose members are the supported-platform
  declaration and whose values (`linux-amd64`) are the wire format used in
  lock filenames, lock documents, and artifact tables. Members are
  append-only and never renamed, because their values are serialized into
  committed locks. Two constructors, and deliberately no third way for a
  client to obtain one: `Platform.current()` (host detection, replacing
  `platform_alias()`) and `Platform.parse()` (from a lock's recorded
  platform). Both fail with an explanatory error naming the supported set,
  not a bare `ValueError`.
- **XDG base-directory derivation**, once: the config, data, state, and
  cache homes for DevCapsule, with the environment mapping injectable for
  tests, replacing both existing implementations.

The membership rule: code belongs in `platforms.py` if and only if it
expresses how the host names or locates things by OS or environment
convention — and would therefore change only when those conventions or the
supported-platform set change, never when product features change.
Feature code that merely consumes environment variables (the host-open
socket, display plumbing) stays with its feature.

## Rationale

The second-consumer rule: a type or convention graduates from a module's
private detail to a shared module when a second consumer demonstrably
exists, not before. Here the evidence is already in the tree — four
modules touch platform identity, one of them by hardcoded literal, and the
XDG convention has two independent implementations. Concentrating exactly
the code selected by the membership rule gives the module one secret (how
this host varies) in the Parnas sense, which is what distinguishes it from
a utilities conglomerate: a reader can predict what is and is not in it.

## Consequences

- `platform_alias()` is retired; lock-path construction calls
  `Platform.current()`.
- `materialization.py` loses its `"linux-amd64"` defaults; the platform
  becomes a required parameter passed down from the lock, where a
  materialization's platform actually comes from.
- `persistence.py` and `project_configuration.py` call one XDG derivation.
- D-0007's `MATRICES` map is keyed by `Platform`, making support a fact
  mypy can check.
- Accepted as lost: `project_configuration.py` remains large; this
  decision extracts only what the membership rule selects, and does not
  attempt a general decomposition of that module.

## Reopen If

The module accretes functions that fail the membership rule (feature logic
arriving because "it touches os.environ"), or per-OS divergence grows to
where the single module wants to become a package with per-platform
implementations.
