# First-Session Entry-Point Changes

Targets: root `README.md`, `docs/README.md`, and `devcapsule-src/README.md`.

The current landing page offers a reason to try DevCapsule but no direct action.
The product index sends the reader to a developer brief with obsolete command
examples and a v026 download among build instructions. The first path must lead
to current released commands without requiring contributor setup.

At finalization of this slice:

- Add a prominent Start here link to `docs/guides/first-session.md` near the
  top of the landing page; retain the pitch, heading and badges. Put the Windows
  caveat beside it, before any installation step.
- Make `docs/README.md` the task-oriented map: first session, existing project,
  agent, Windows help. Retain historical/product-draft links under explicit
  labels, below the current guides.
- Route the CLI README's User Setup and release-download directions to the
  first-session guide. Label editable installs as contributor setup and correct
  the opening's stale public command shape. Preserve build/operator information.
- Index the three promoted guides in `index.md`; remove their WIP copies when
  promoted, maintaining one current source for each page.

Dependencies: released v0.2.12, Linux amd64, Docker/Buildx and a local browser.
Additional Windows workarounds await the owner's source conversation; the first
Linux journey and the already-confirmed WSL notes can be finalized independently.

Verification: verify the released checksum/version, exercise init/run/Node and
stop/resume, inspect the IDE and default host boundaries, check links/anchors
and shell syntax, compare preserved badges. Distinguish those checks from an
unperformed clean-Windows or full browser-interaction walkthrough.
