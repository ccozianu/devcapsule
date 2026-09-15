# Workstream Current Status: User Documentation

Mnemonic: `user-docs`

Start date: `2026-09-12`

State: active 2026-09-15; collaboration guidance accepted; returning to user-docs scoping

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

The owner subsequently challenged the agent's unilateral product choices and
the cost of its runtime investigations. The current requested slice is generic
guidance in the shared root `AGENTS.md` for proportionate investigation, reasoning
from contracts, and consultation on consequential choices. This applies to agents
working here; the packaged reusable workflow definition has not been changed.
The owner accepted this guidance, including the distinction between existing
tests and newly written tests that may encode unvalidated product assumptions.

## Branch And Checkout

Selected branch: `user-docs/first-session`, created from accepted main `a09e09d`.
`user-docs/outbox` carries intake dispositions and workstream records.
Project-management was deliberately paused before switching; its pause record
is pushed through `project-management/outbox`, awaiting the owner's merge.
The owner's unrelated local host settings were saved on local-only
`project-management/local-host-settings-20260915`; they are not documentation
changes and were not copied onto this branch. No stash is the handoff boundary.

## First-Session Proposal Awaiting Owner Agreement

The following was implemented by the agent without first agreeing the adopter
journey with the owner. Preserve it as existing branch work, not an accepted
product decision or a slice authorized for publication by its test results.

1. A visible “Start here” link from the README to one short first-session guide.
2. Prerequisites, verified executable download, a disposable VSCodium/JavaScript
   exercise, explanations of every init prompt, browser desktop, and first output.
3. Save, stop and resume; then a clear route to an existing project and a coding
   agent. The first exercise needs no vendor account or project dependency setup.
4. A Windows branch before installation, with supported prerequisites and the
   confirmed browser workaround. The owner's missing Gemini conversation is
   required before adding its exact remaining WSL2 workarounds.

The agent proposed resolving sample selection by using a tiny new folder:
no private Git credentials, external sample lock, or dependency installation
stands between the reader and a first result. Whether that exercise delivers
the intended first-session value remains a product decision for the pair.

## Intake Acknowledgments

- `2026-09-13-contained-display-desktop-in-the-browser-tutorial.md`: acknowledged
  for this slice. Cover the browser URL, closing a tab versus ending a session,
  keyboard/fullscreen/clipboard behavior, and explicit host-X11 opt-in.
- `2026-09-13-contained-display-windows-wsl2-warning-and-workarounds.md`:
  acknowledged. Put the Windows warning before installation; include verified
  facts now. The exact additional owner workarounds remain accepted follow-up,
  waiting for the source conversation rather than being invented or forwarded.
  The shared Gemini URL could not be read; the owner was asked for its text.

Both acknowledgments are pushed with intake removal and the disposition log
through `user-docs/outbox`. The existing files on main remain the sender's evidence
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
output was `Hello, DevCapsule!`. A further restart retained folder trust and
the terminal state. File → Exit in VSCodium stopped the launcher cleanly with
exit code 0. Ctrl+C also stopped the container but printed KeyboardInterrupt;
the guide now prefers the clean IDE exit and explains interruption output.

Checked 186 local links/anchors, the three guides' shell-block syntax, their
permanent index entries, and Git whitespace. The landing pitch and both badge
lines are byte-for-byte preserved around the new Start here/Windows links. The
index's existing uninitialized sample-submodule link is the one unavailable
local target. No runtime source changed or broad test suite was run. This uses an existing Docker
host/cache, not a clean workstation or measured cold download. Browser keyboard,
clipboard and Windows checks must not be claimed from this evidence alone.

## Planned Next Step

Deliver the accepted agent guidance and this handoff on the owner-requested
temporary branch `user-docs/temp-pr-20260915-agent-guidance`, based on current
main and containing only these two files. The owner will open and merge the PR
on GitHub; this environment has neither PR write rights nor `gh`. The explicit
request groups the guidance and its handoff in one reviewable delivery instead
of sending the handoff separately through the standing outbox.

Then return attention to user docs. Before resuming onboarding implementation,
agree the intended adopter,
first useful outcome, and the smallest useful next slice. Do not resume the
runtime experiments or treat the existing guides as accepted on the strength
of the previous handoff. An autonomous product-development experiment was
discussed hypothetically; none has been authorized to run.

The earlier delivery proposal is superseded by this feedback. The pushed records
outboxes (`project-management/outbox` and `user-docs/outbox`) and documentation
branch remain unmerged as of the latest fetch. The guides were moved to permanent
paths on this branch and entry-point changes applied, but those mechanical steps
do not establish owner acceptance. No existing guide work has been discarded.
The older `user-docs/outbox` handoff is superseded: refresh it from the current
working branch before any future delivery rather than merging its stale account
of accepted product choices.

## Open Threads

- Revisit the agent-selected first-session journey with the owner before
  additional implementation or delivery. The collaboration guidance is accepted.
- Awaiting the owner's Windows/Gemini workaround text; basic Linux documentation
  and confirmed WSL2 notes can proceed independently.
- Actual browser clipboard/fullscreen behavior and fresh Windows installation
  need human platform checks; preserve the contained-display evidence separately
  from validation performed here.
- Two restart attempts hit a host Docker DNAT/iptables error; retrying the same
  documented command succeeded without changes to Docker or host permissions.
  This is recorded as an observed environment limitation, not an established
  DevCapsule defect or a reason to weaken the default boundary.
- v0.2.12 currently labels its selected base v0.2.12-rc5; the immutable digest
  matches the released base. Explain the prompt locally and record the UX issue.
- No new session transcript or session record was requested or created.

## Delivered-Branch Documents

The guide copies have been promoted to `docs/guides/first-session.md`,
`docs/guides/your-project.md`, and `docs/guides/windows-wsl2.md` at the repository
root, indexed by `index.md` in the same change. They travel the ordinary PR,
never the records outbox. The internal proposal remains at
`docs/entry-point-changes.md` beneath this workstream, marked applied.

The user-docs intake to project-management,
`2026-09-15-user-docs-first-session-ux.md`, records the misleading base label,
startup diagnostics and Ctrl+C traceback. It asks for implementation ownership;
it is not a change to another workstream's handoff.

## Documents

- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)

## Source Documents

- [Landing page](../../../README.md)
- [Product documentation index](../../../docs/README.md)
- [CLI source and contributor reference](../../../devcapsule-src/README.md)
- [Current-interface requirement](../../requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)
- [Contained desktop design](../2026-08-19-contained-display/display-transport-design.md)
