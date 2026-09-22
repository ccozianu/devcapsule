# Workstream Current Status: User Documentation

Name: `user-docs`

Start date: `2026-09-12`

State: active 2026-09-22; resumed by the product owner to refresh the adopter

Definition read: WORKFLOW.md@a1002b6f5e67, WORKFLOW-LOCAL.md@ed70f3147563
documentation for the next release; migrated to the current workflow

Branch association: `ws-user-docs/first-session`

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

Selected branch: `ws-user-docs/first-session`, created 2026-09-22 from
current `main` under the `ws-` form; the earlier `user-docs/first-session`,
`user-docs/outbox`, and the temporary agent-guidance branch held nothing
`main` lacked and were deleted. Records travel this branch and are published
live on the coordination branch; there is no outbox.
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

## Last Task And Planned Next Step

The owner accepted the interim guides, landing edits, and both blog versions
for mainline delivery. Verified PR #86 (`6a44168`) and the final landing follow-up
PR #87 (`2e5f3b1`) on remote main; this checkout is synchronized through
`21367b8`, including the subsequent coverage-badge update. Agent instructions
and earlier coordination records already landed through PRs #84 and #85.

At the owner's direction, prepared the permanent
[website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md)
in this workstream, then the `website` registration through `user-docs/outbox`.
Deliver the work order through `user-docs/first-session` before merging the
registration outbox, so its linked brief exists on main. The outbox carries
this handoff verbatim and pauses user-docs in the registry. The owner authorized
a prepared `website/initial-cut` branch from this workstream's branch; record
that narrow pre-registration branch exception in the new handoff.

Website implementation has not started. The human will use `/new` and explicitly
select `website/initial-cut` after the deliveries land. Leave this checkout on
user-docs for that handoff; do not switch or begin the experiment in this context.
The initial setup/credentials checkpoint belongs to the new pair. Its work order
is self-contained and expressly includes the repository-owned development blog.

On a future human-directed return to user-docs, resume UD-001: agree the small
AI-first project and outcome, then design the v1 journey and record gaps.
UD-002 through UD-004 and the later OpenCode requirement remain accepted.
No remaining website design choices should be decided here.

## Open Threads

- Pending delivery: work-order PR, then registration outbox; verify external
  merge state before starting website. Git push works, but the human opens and
  merges PRs. No infrastructure access has been requested for the experiment.
- This is a deliberate pause, not completion of user-docs. The v1 guide cleanup,
  OpenCode setup, and platform follow-ups remain here.
- Preserved for the next pair: the work order and website handoff. No full chat
  transcript or unpublished speculative website design is being carried over;
  the blog dialogue is illustrative fiction, not an additional task contract.

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

- [Website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md) — agreed experiment brief handed to website.

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
