# Workstream Current Status: Contained Display

Mnemonic: `contained-display`

Start date: 2026-08-19

State: open; not yet started

Integration target: `main`

Delivery method: pull request

Requirements: `R-SCOPE-001`, `R-PRODUCT-002`, `R-DOCKER-001`

## Goal

Give the capsule its own display environment rather than borrowing the host X
session, closing the host-session credential exposure and delivering the desktop
integration that shares its root cause. This covers the transport decision, the
interim mitigation before that transport ships, clipboard policy, and the
regression test that keeps the boundary closed.

## Why This Workstream Exists

Opened by `project-management` on 2026-08-19 at the product owner's direction.
The [V1 scope ledger](../2026-08-09-project-management/v1-scope-ledger.md) row
*Contained Display And Desktop Integration* decided the direction on 2026-08-16
with release target v027 and recorded its owner as unassigned, noting that it
might warrant a separate workstream rather than joining an existing one. By that
ledger's own rule a row without an owner is a defect, and this workstream
resolves it.

It is named for its subject rather than for v027 deliberately. A workstream
named after a release either outlives the release or mis-fits it when scope
moves.

`recursive-e2e` was not extended to cover this work. That workstream is paused
with Stage 7 — the persistence and safe-cleanup half of its own registered goal
— still ahead of it, and it is not concluding.

## Branch Association

Branch prefix `contained-display/`. No branch exists yet; the first one is
forked from this registration commit on `main`, per *Beginning A Workstream* in
`WORKFLOW.md`.

## Scope

In scope:

- the display transport decision, currently `proposed` pending a spike, between
  a contained VNC or noVNC session and Xpra seamless mode;
- an interim mitigation for the window before that transport ships, during which
  real projects containing agents run on X11 passthrough;
- clipboard policy and its declaration in the runtime plan and inspection
  output; and
- the regression test that proves the capsule cannot reach the host session.

Not in scope: the `xdg-open` and `BROWSER` forwarding shim, which ships in v026
under `recursive-e2e` because it behaves identically under every candidate
transport.

## Current Task

None yet. The workstream is registered and awaiting its first session.

## Next Resumable Task

Decide and act on the interim mitigation, because it is the only part with a
clock on it: the product owner is starting real projects on v026 now, and those
projects run agents against a transport that grants the container a full host
session credential.

The delivered intake item recommends a nested X server as that mitigation, on
the grounds that it needs no base image change and so does not disturb v026, and
that kicking its tires is also the first half of the transport spike. Read the
item and the design note it links before planning; neither is a decision.

The permanent work follows the method the ledger row already sets: spike a
contained VNC or noVNC session and Xpra seamless mode, then perform a full day
of ordinary development inside the result before ratifying it into V1.

## External State And Risks

- The [X11 session-credential bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
  is open and is this workstream's subject. Verify its status rather than
  trusting this line.
- The transport choice interacts with the proposed WSL2 work, the sample-project
  port and networking items, and the JCEF preview bug. The ledger row records
  how.

## Workstream Document Index

None yet.
