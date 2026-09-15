# Workstream Current Status: User Documentation

Mnemonic: `user-docs`

Start date: `2026-09-12`

State: active 2026-09-15; first-adopter journey under implementation

Integration target: `main`

Delivery method: pull request; GitHub API writes previously returned 403

Requirements: `R-DOCS-002`, `R-PRODUCT-001`, `R-PRODUCT-002`, `R-PRODUCT-003`

## Goal And Owner Direction

From the landing page, a curious adopter should reach useful work without a
“what am I supposed to do here?” moment. The owner explicitly selected this
workstream and this checkout on 2026-09-15. The existing landing page and
comparison are accepted starting points, already integrated through PRs #71–74.
Preserve the short pitch and health badges; make the next action obvious.

DevCapsule provides reproducible IDE/agent workspaces with explicit host
boundaries and durable state. This slice documents supported released behavior,
not prospective V1 promises or implementation history. It does not implement
runtime changes or rewrite the reusable workflow.

## Branch And Checkout

Selected branch: `user-docs/first-session`, created from accepted main `a09e09d`.
`user-docs/outbox` carries intake dispositions and workstream records.
Project-management was deliberately paused before switching; its pause record
is pushed through `project-management/outbox`, awaiting the owner's merge.
The owner's unrelated local host settings were saved on local-only
`project-management/local-host-settings-20260915`; they are not documentation
changes and were not copied onto this branch. No stash is the handoff boundary.

## Selected First Slice

1. A visible “Start here” link from the README to one short first-session guide.
2. Prerequisites, verified executable download, a disposable VSCodium/JavaScript
   exercise, explanations of every init prompt, browser desktop, and first output.
3. Save, stop and resume; then a clear route to an existing project and a coding
   agent. The first exercise needs no vendor account or project dependency setup.
4. A Windows branch before installation, with supported prerequisites and the
   confirmed browser workaround. The owner's missing Gemini conversation is
   required before adding its exact remaining WSL2 workarounds.

The formerly proposed sample selection is resolved by using a tiny new folder:
no private Git credentials, external sample lock, or dependency installation
stands between the reader and a first result. This is a first useful session,
not a speed benchmark or proof that arbitrary repositories need no setup.

## Intake Acknowledgments

- `2026-09-13-contained-display-desktop-in-the-browser-tutorial.md`: acknowledged
  for this slice. Cover the browser URL, closing a tab versus ending a session,
  keyboard/fullscreen/clipboard behavior, and explicit host-X11 opt-in.
- `2026-09-13-contained-display-windows-wsl2-warning-and-workarounds.md`:
  acknowledged. Put the Windows warning before installation; include verified
  facts now. The exact additional owner workarounds remain accepted follow-up,
  waiting for the source conversation rather than being invented or forwarded.
  The shared Gemini URL could not be read; the owner was asked for its text.

Both acknowledgments travel with intake removal and the disposition log
through the outbox. The existing files on main remain the sender's evidence
until that delivery lands.

## Current Evidence

Verified the published v0.2.12 executable against its downloaded checksum and
its reported source `2916c4c09aee13eeed85276c1a32889515ce7b19`. Exercised a fresh
VSCodium/node initialization with isolated checkout configuration, captured the
actual prompt sequence, and launched its contained desktop with default host
authorizations. Inspected the running VSCodium desktop, executed the small Node
program inside the capsule, and verified the resulting file from outside.
Stopped the capsule, relaunched the same checkout without initialization,
verified its persisted file and IDE state, trusted the demo folder through the
actual GUI, and ran `node hello.js` in VSCodium's own terminal. The displayed
output was `Hello, DevCapsule!`. Final document checks are next. This uses an existing Docker
host/cache, not a clean workstation or measured cold download. Browser keyboard,
clipboard and Windows checks must not be claimed from this evidence alone.

## Planned Next Step

Finalize the checked first-session guides and entry points, then prepare
the slice for ordinary PR delivery after the intake disposition outbox lands.
Apply the repository's draft-document rules and keep proof limits explicit.
Send any discovered product defects as intake instead of enlarging this task
into runtime implementation. The workstream remains open for additional guides.

## Open Threads

- Awaiting the owner's Windows/Gemini workaround text; basic Linux documentation
  and confirmed WSL2 notes can proceed independently.
- Actual browser clipboard/fullscreen behavior and fresh Windows installation
  need human platform checks; preserve the contained-display evidence separately
  from validation performed here.
- One restart attempt hit a host Docker DNAT/iptables error; retrying the same
  documented command succeeded without changes to Docker or host permissions.
  This is recorded as an observed environment limitation, not an established
  DevCapsule defect or a reason to weaken the default boundary.
- v0.2.12 currently labels its selected base v0.2.12-rc5; the immutable digest
  matches the released base. Explain the prompt locally and record the UX issue.
- No new session transcript or session record was requested or created.

## Draft Deliverables

The branch holds drafts at `docs/guides/first-session.md`,
`docs/guides/your-project.md`, `docs/guides/windows-wsl2.md`, and
`docs/entry-point-changes.md` beneath this workstream. They are not delivered
through the records outbox. Promotion destinations are the matching root
`docs/guides/` paths; the entry-point proposal is internal.

## Documents

- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)

## Source Documents

- [Landing page](../../../README.md)
- [Product documentation index](../../../docs/README.md)
- [CLI source and contributor reference](../../../devcapsule-src/README.md)
- [Current-interface requirement](../../requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)
- [Contained desktop design](../2026-08-19-contained-display/display-transport-design.md)
