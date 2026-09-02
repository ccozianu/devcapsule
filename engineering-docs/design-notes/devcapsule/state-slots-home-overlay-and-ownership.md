# State Slots, The Home Overlay, And The $HOME Ownership Invariant

Ruled 2026-09-02 by the product owner during the `component-catalog`
workstream, after the antigravity state bug (a slot nested two levels
beneath home left a runtime-created root-owned `~/.gemini` walling off
the CLI's sibling `config/` directory). Referenced from
`_validate_slots` and `_validate_formation_slots` in
`container_runtime/contract.py` and `prepare_home_mount_points` in the
host launcher.

## The Rulings

1. **The home overlay stays.** A component state slot may mount beneath
   the (always-mounted) persistent home. This is load-bearing: agent
   CLIs hardcode `~/.claude`, `~/.codex`, `~/.gemini`, and per-checkout
   credential persistence with independent scope, sensitivity, and
   deletion requires mounting exactly there. The deeper mount shadows
   the home source; that separation is the feature.

2. **The ownership invariant**: whatever mechanism touches the home —
   the image build, the entrypoint, or the mount mechanics — at the end
   of the day *everything under `$HOME` is owned by the user*. No step
   may leave root-owned entries in the developer's home, on either side
   of the mount boundary.

## What Enforces Them

- **Contract validation** (`_validate_slots`): an overlay slot must be
  a *direct child* of home — a deeper mount forces the container
  runtime to create the intermediate parent as root, violating the
  invariant and walling off siblings. A slot may not claim home itself
  (home belongs to the global home binding), and slots within one
  component may not overlap.
- **Formation validation** (`_validate_formation_slots`): no slot ever
  mounts inside — or at the same path as — another *component's* slot;
  ownership, sensitivity, and deletion semantics must never entangle
  across components. (PyCharm's and Codium's `~/.cache` slots share a
  spelling but can never co-occur: a lock holds exactly one surface.)
- **The host launcher** (`prepare_home_mount_points`): every
  home-overlay mount point is created inside the persistent home
  source *by the invoking user, before the daemon runs*, so the
  container runtime never creates one as root. A foreign-owned entry
  left by an earlier launch is reported — repairing it needs host
  privilege the launcher does not have.

## Boundaries And Follow-Ups

- Slots outside home with runtime-created shared parents (PyCharm's
  `/ide-project-state/{system,log}`) are outside the home invariant but
  sit in the same hazard shape; they survive because nothing writes a
  sibling there. Folding them under a general "no runtime-created
  intermediate parents" rule is open.
- The entrypoint half of the invariant — verifying at container start
  that `$HOME` and its first-level entries are user-owned, and failing
  loudly when they are not — belongs to the supervisor↔component
  contract that `contained-display` owns; recorded here as a
  coordination item rather than implemented unilaterally.
- A future component that genuinely needs a deep home path (e.g.
  `~/.config/tool`) mounts the nearest direct child (`~/.config`) whole
  or brings a case for relaxing the rule alongside launcher-side parent
  pre-creation; the validation error names this note.
