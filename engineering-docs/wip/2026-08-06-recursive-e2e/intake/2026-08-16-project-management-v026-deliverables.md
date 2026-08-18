# Intake: The Two v026 Deliverables

Delivered: 2026-08-16

From: `project-management`, recording a product-owner decision made the same
day.

## What Is Being Handed Over

This workstream owns the v026 base and two deliverables it must carry. Bugs
fixed for v026 are the current top priority across the portfolio.

### 1. A Self-Contained Tool Entry Point

The published artifact must run on a supported host with **no Python
installed**.

Verified on 2026-08-16: `scripts/build-pex.sh` defaults the embedded shebang to
`/usr/bin/env python3.12` and `pyproject.toml` sets `requires-python = ">=3.12"`,
so the artifact requires an interpreter named `python3.12` on `PATH` rather than
merely a recent Python. The only "User Setup" documented in
`devcapsule-src/README.md` is a contributor source install.

The intended mechanism is a Pex scie — a single native binary embedding a
python-build-standalone interpreter, retaining the existing dependency lock,
embedded source revision, PEX SHA-256, provenance checks, and base-image
embedding, with the interpreter embedded eagerly rather than fetched at first
run. A documented one-line alternative for developers who already manage Python
toolchains, such as `uv tool install`, is also wanted.

**Required acceptance evidence:** a clean-machine proof. A host image containing
no Python interpreter downloads the published artifact, runs it, and obtains
help and version output. This check is the one that would have detected the
present gap, and it is required rather than optional.

Full context, including why gap `F8` would have been satisfied without closing
this, is in the
[V1 scope ledger](../../2026-08-09-project-management/v1-scope-ledger.md).

### 2. The URL-Open Fix

Clicking a link in the containerized IDE currently goes nowhere: there is no
`xdg-open` handler inside the container and no browser to handle it.

A shim inside the container — `xdg-open` plus `BROWSER` — forwarding the URL to
a small host-side helper over a socket the launcher already owns is estimated at
roughly a day.

This is deliberately **separated from the display-transport decision**, because
the shim works identically under X11, VNC, or Xpra. It should not wait for the
contained-display work, which is deferred to v027.

## Why It Belongs Here

The product owner delegated the v026 base to this workstream on 2026-08-16.

The sender notes plainly that both items are product work rather than
recursive-E2E work, and that this workstream's registered goal describes
building and launching a successor from inside the dogfood environment. Root
`CURRENT-STATUS.md` has been amended to widen the goal so the registry does not
understate where the work lives. Whether that widening is the right long-term
shape is a question this workstream may raise back.

## Related State Worth Knowing Before Resuming

- This workstream was paused, and root `CURRENT-STATUS.md` described it as
  "Stage 4 ready to begin" while this handoff reported Stage 6 substantially
  complete. Both are now corrected.
- Commits `c26d877` and `c24b442`, roughly 1,600 lines including the Stage 6
  inspector, are published on the branch and **not on `main`**. The
  [V1 readiness assessment](../../2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md)
  recorded them as the repository's clearest drop risk. Resuming is the moment
  to land them.
- The branch is named `recursive-e2e/stage-4` while the work is at Stage 6 and
  now carries v026 product deliverables. Cosmetic, but it will mislead a reader.
- Stage 6 hardening and failure-path coverage remain outstanding independently
  of these two items.

## What Accepting Would Mean

A v026 base whose entry point runs without a host Python, proven on a clean
machine, and a containerized IDE whose link clicks open a browser on the
developer's desktop. Priority between the two, and their sequencing against
Stage 6 hardening, are this workstream's judgment.
