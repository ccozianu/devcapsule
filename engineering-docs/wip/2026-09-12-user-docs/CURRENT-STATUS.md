# Workstream Current Status: User Documentation

Mnemonic: `user-docs`

Start date: `2026-09-12`

State: active 2026-09-16; owner authorized interim docs, landing edits, and both blog versions for mainline delivery; v1 cleanup backlogged

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
boundaries and durable state. The owner redirected this work to designing the
intended v1 experience through user documentation. Compare current v0.x behavior
against that target to discover implementation gaps, prioritize them over coming
iterations, and refine the docs from implementation feedback. Release-specific
observations are evidence, not the design target. Keep unimplemented behavior
explicitly identified while drafting; do not advertise it as available today.

The first sessions should start a small project using at least one AI, possibly
two. An adopter without AI access remains supported but is a secondary path,
not the audience around which to design the main experience. The project,
IDE/agent pairing, and role of a possible second AI remain open.

The owner wants to encourage investing in excellent tools: time saved and
learning can justify a paid AI subscription, with $20/month as an accessible
example and $200/month as a professional investment. These are positioning
ideas, not verified provider prices or a purchase prerequisite. A requested
Erik Meijer quotation about paying for tools remains unverified verbatim;
[Nathan Jones's 2015 account](https://nathanpjones.com/posts/) paraphrases his
comparison to chefs buying premium knives. Do not turn that into a direct quote.

The owner challenged the agent's unilateral product choices and
the cost of its runtime investigations. The resulting slice added generic
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

## Interim First-Session Slice Accepted For Mainline

The following was initially implemented without agreeing the intended journey
with the owner. On 2026-09-16 the owner explicitly authorized pushing the work
for mainline integration, accepting that occasional visitors may encounter the
v0.2.12-specific experience temporarily. This accepts an interim delivery; the
intended v1 journey remains AI-first and needs the choices below.

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
stands between the reader and a first result. It is now accepted as an interim
exercise, not as the agreed v1 introduction.

## Accepted Follow-Up Backlog: Replace The v0.2.12-Specific Journey

Owner: `user-docs`. Accepted 2026-09-16; these items follow the current mainline
delivery and do not block it. Work in this order unless the owner redirects:

1. **UD-001 — Design the v1 first sessions with AI.** Agree a small project,
   useful outcome, and IDE/agent pairing, then replace the no-AI JavaScript
   exercise as the main journey. Decide whether a second AI adds value. Draft
   the intended experience and record implementation gaps for coordination.
2. **UD-002 — Remove incidental dependence on v0.2.12.** Review the download
   URL, expected version output, platform prerequisites, and release references
   across `docs/guides/first-session.md`, `your-project.md`, `windows-wsl2.md`,
   and their entry points. Agree how users get a supported release without
   requiring the whole journey to be redesigned per patch release. Keep
   executable instructions and checksum verification tied to actual artifacts;
   do not just replace version strings with unverified future commands.
3. **UD-003 — Retire obsolete workaround prose as fixes arrive.** Revisit the
   RC-labelled base prompt, init answers, launch diagnostics, browser opening,
   and Ctrl+C/exit guidance against the implementation selected for the guide.
   Coordinate runtime changes through project-management's existing UX intake;
   this workstream owns the documentation changes and relevant verification.
4. **UD-004 — Close documented platform evidence gaps.** Incorporate the
   owner's Windows/WSL2 findings when available and confirm the browser
   clipboard/fullscreen and resume instructions needed by the chosen journey.

Done means the main entry points describe the agreed v1 experience, remaining
release-specific limitations are clearly identified, and the published steps
match the release they claim to support. The later OpenCode setup requirement
below remains accepted after the first-session scoping; it is not forgotten
or an immediate installation task.

## Accepted Later Requirement: OpenCode Setup

Owner direction, 2026-09-15: user-docs will test and document an adopter setup
using OpenCode. This is accepted work for later, after the current first-session
journey is scoped; it is not an instruction to install or test OpenCode now.

Cover one concrete setup from selecting OpenCode and connecting a model through
a small coding task and resuming work, including prerequisites, persistent state,
and explicit host access. Include a locally run open model in the setup we
evaluate; Gemma is a candidate, not a selected or validated pairing. Record
implementation gaps rather than silently changing the intended v1 experience.

Project-management is asked to arrange OpenCode testing and determine any
implementation ownership and sequencing. Its intake item is
`2026-09-15-user-docs-opencode-evaluation.md`. Use the resulting evidence when
verifying the documented journey; do not assume endpoint compatibility proves
that the selected agent/model combination works well.

## Intake Acknowledgments

- `2026-09-13-contained-display-desktop-in-the-browser-tutorial.md`: acknowledged
  for this slice. Cover the browser URL, closing a tab versus ending a session,
  keyboard/fullscreen/clipboard behavior, and explicit host-X11 opt-in.
- `2026-09-13-contained-display-windows-wsl2-warning-and-workarounds.md`:
  acknowledged. Put the Windows warning before installation; include verified
  facts now. The exact additional owner workarounds remain accepted follow-up,
  waiting for the source conversation rather than being invented or forwarded.
  The shared Gemini URL could not be read; the owner was asked for its text.

Both acknowledgments, intake removals, and the disposition log reached main
through `user-docs/outbox` in PR #85, verified on 2026-09-16.

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

The earlier guide validation checked 186 local links/anchors, the three guides'
shell-block syntax, their permanent index entries, and Git whitespace. Both
badge lines remain unchanged; the owner subsequently edited the landing copy
and approved its grammar corrections and informal installation wording. The
index's existing uninitialized sample-submodule link is the one unavailable
local target. No runtime source changed or broad test suite was run. This uses an existing Docker
host/cache, not a clean workstation or measured cold download. Browser keyboard,
clipboard and Windows checks must not be claimed from this evidence alone.

Delivery checks on 2026-09-16: reviewed 203 relative Markdown link targets and
parsed 19 shell blocks with `bash -n`; both health badges remain unchanged.
The existing index link into the uninitialized `typescript_tictactoe_5inrow`
sample submodule is the only unavailable local target. Git whitespace checks
pass. No runtime tests or installations were repeated for this prose delivery.

## Planned Next Step

At the owner's request, wrote the second development-blog entry,
[I asked for user docs](../../blog/2026-09-16-i-asked-for-user-docs.md), in the
owner's voice with its AI-assisted authorship and edited quotations disclosed.
The owner reviewed it positively, then requested a separate, funnier version
as an imaginary dialogue between friends, including more of the autonomy
argument and Navier–Stokes budget thought experiment. That alternative,
[Does the subscription include Navier–Stokes?](../../blog/2026-09-16-does-the-subscription-include-navier-stokes.md),
explicitly distinguishes invented dialogue from a transcript and makes no claim
that a mathematical problem was solved. The owner clarified that the two friends
are Costin and the AI itself, imagined as golfing/drinking buddies. Rewrote the
alternative as Costin and Astra, explicitly identified as the Codex assistant;
Astra argues its own case and answers for its decisions rather than appearing
as a third party discussed by an invented human. On 2026-09-16 the owner
authorized pushing the accumulated work for mainline integration. Both versions
are included; no separate blog-site publication or implementation experiment
was requested.

The owner merged the isolated agent-guidance delivery through PR #84, verified
on remote main at `1965be0`; this checkout has merged that main. The delivery
contained only root `AGENTS.md` and this handoff, grouped on one temporary branch
at the owner's explicit request. This environment has neither PR write rights
nor `gh`; future PR opening and merging remains the owner's work.

Push `user-docs/first-session` and give the owner the GitHub comparison link for
the mainline merge. After the owner merges, verify the delivered tree on remote
main and synchronize this checkout without discarding any unique work. This is
an interim slice; the workstream stays open for UD-001 through UD-004 and the
accepted OpenCode requirement. Then agree the AI-first project and outcome
before resuming implementation or runtime experiments. The hypothetical
autonomous product-development experiment remains unauthorized.

The user-docs
records outbox reached remote main through PR #85 at `bfbfa5a`, verified on
2026-09-16 and merged into this checkout. The project-management pause outbox
and onboarding documentation branch remain unmerged as of that fetch.
The guides are at permanent paths with their entry-point changes applied and
are now accepted for this interim integration. No existing guide work has been
discarded.
That records delivery included the OpenCode evaluation intake and the pending
routing, intake dispositions, and UX intake. The onboarding guides travel with
the current ordinary delivery, separately from that already-merged outbox.

## Open Threads

- Choose the small project, first useful outcome, and AI/IDE pairing with the
  owner. Decide whether and how a second AI improves the first sessions.
- Verify the exact Meijer quotation if the owner supplies its source; the
  located secondary account supports a paraphrase only.
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

- [Second development-blog entry: I asked for user docs](../../blog/2026-09-16-i-asked-for-user-docs.md) — first-person version.
- [Alternative second entry: Does the subscription include Navier–Stokes?](../../blog/2026-09-16-does-the-subscription-include-navier-stokes.md) — fictional Costin/Astra dialogue.
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)

## Source Documents

- [Landing page](../../../README.md)
- [Product documentation index](../../../docs/README.md)
- [CLI source and contributor reference](../../../devcapsule-src/README.md)
- [Current-interface requirement](../../requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)
- [Contained desktop design](../2026-08-19-contained-display/display-transport-design.md)
