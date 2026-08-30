# V1 Scope Ledger

Owned by: `project-management`

Status: draft. Opened 2026-08-16.

This is the single tracked list of what V1 contains. It exists because the
[V1 readiness assessment](2026-08-16-v1-readiness-assessment.md) found that V1
was defined only by a dated gap-review snapshot, that three of its four
milestones appeared in no other document and had no owning workstream, and that
items recorded as a sentence inside another document reliably fail to ship.

Every row carries a verdict, an owner, and acceptance evidence. A row with no
owner is an unresolved defect in this ledger, not a normal state.

**Amended 2026-08-29, by the product owner.** An unowned row is acceptable as
a standing state: workstreams are assigned when the work is picked up, not at
decision time. The rule above survives in weakened form — a row with no owner
is not a defect, but no unowned row may be reported as in progress, and the
release gate still requires every `in-v1` row to have found an owner before
its work is claimed done. This settled the 2026-08-27 resume question about
registering `codium-surface`: no registration happens until that work starts.

## Verdict Values

- `in-v1`: committed to the V1 release.
- `deferred`: accepted direction, explicitly outside V1, with a stated later
  home so the deferral is visible rather than silent.
- `rejected`: considered and intentionally not pursued.
- `proposed`: recorded during planning; not yet ratified by the product owner.
- `v1-optional`: added 2026-08-29 by the product owner. The feature is neither
  committed nor deferred; the call is deliberately postponed until a V1
  candidate exists, and is then made against the candidate rather than
  against a plan. Rows with this verdict live in *Optional For V1* below.

A `proposed` verdict is not a commitment. It is carried here so that the
pending decision is itself visible.

## Decided Rows

### Self-Contained Tool Entry Point

Verdict: `in-v1`

Decided: 2026-08-16, by the product owner, from direct experience of the
current install path.

Owner: `recursive-e2e`, delegated 2026-08-16 together with the v026 base.
Release target: **v026**, ahead of the product owner's own project starts.

Expands and corrects gap `F8`.

**Problem.** DevCapsule's own entry point is the least reproducible thing it
ships. Installing the tool currently requires the user to construct a Python
environment by hand; the product owner is running the PEX from a self-built
conda environment because that is what the documentation implies.

Verified on 2026-08-16:

- `scripts/build-pex.sh` defaults the embedded shebang to
  `/usr/bin/env python3.12`, and `pyproject.toml` sets
  `requires-python = ">=3.12"`. The artifact therefore requires an interpreter
  named `python3.12` on `PATH`, not merely a recent Python. Ubuntu 24.04 LTS's
  predecessor ships 3.10 and Debian 12 ships 3.11; a host on 3.13 with no 3.12
  alias also fails.
- The only "User Setup" documented in `devcapsule-src/README.md` is a
  contributor source install: create a virtual environment, then
  `pip install -e ./devcapsule-src`. No download-and-run path for an end user is
  documented anywhere.
- No packaging approach that removes the host-interpreter dependency is
  mentioned anywhere in the repository.

**Why F8 would not have caught this.** F8 requires "a downloadable, versioned
`devcapsule-1.0.0.pex`" plus installation and first-run instructions. It assumes
the PEX is a sufficient entry point and asks only that it be documented.
Publishing a PEX and a README satisfies F8 literally while leaving a developer
without a Python toolchain unable to run the tool at all. The premise is
corrected here.

**Audience impact.** The product targets developers adopting AI coding agents,
which is not a Python-developer audience. A Java developer has no Python at all.
A Python developer on the wrong minor version, or one who simply does not want
to think about interpreters, hits avoidable friction as their first experience
of a product whose thesis is that environments should not be assembled from
memory.

**Required outcome.**

- The primary published artifact runs on a supported host with **no Python
  installed**. The intended mechanism is a Pex scie: a single native binary
  embedding a python-build-standalone interpreter, retaining the existing
  dependency lock, embedded source revision, PEX SHA-256, provenance checks, and
  base-image embedding. Interpreter embedding is eager rather than fetched at
  first run.
- A documented one-line alternative for developers who already manage Python
  toolchains, such as `uv tool install`, which provisions its own interpreter.
- Acceptance evidence is a clean-machine proof: a host image containing no
  Python interpreter downloads the published artifact, runs it, and obtains
  help and version output. This check is the one that would have detected the
  present gap and is required, not optional.
- Published checksums cover the new artifact form, and `devcapsule version`
  continues to report product version, exact public source revision, and
  canonical source URL.
- End-user installation documentation describes the download-and-run path
  first. The existing contributor source install is relabelled as a contributor
  path rather than "User Setup".

**Explicitly not required for V1.** A Docker image as the tool's entry point is
a reasonable secondary channel, since every target user already has Docker, but
it is not the primary path: it would ask a first-time user to mount a Docker
socket into a container in order to run a product positioned on containment,
and it re-enters the host-path translation problem that `host_daemon.py`
addresses for launches. Recorded as a candidate, not a commitment.

**Estimated cost.** Roughly three to five days including multi-architecture
builds and the clean-machine proof. It expands the release-engineering block
rather than adding a milestone, so it does not change the release shape.

### Contained Display And Desktop Integration

Verdict: `in-v1` for the direction. Implementation specifics are `proposed`
pending a spike.

Direction decided: 2026-08-16, by the product owner. The capsule presents its
own contained windowing environment rather than borrowing the host X session.

Release target: **v027**, decided 2026-08-16. The change touches the base
recipe, the launcher, port allocation, and the platform matrix, and its own
ratification gate requires a full day of ordinary development inside the result
— none of which is compatible with v026 being the base the product owner starts
projects on. Deferring the transport defers the fix to the
[X11 session-credential bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md),
not the obligation: the containment claim cannot be announced as verified while
the X socket carries a full host session credential.

**Release target restated, 2026-08-30.** The `v027` label above predates the
version-identity unification; the release now numbered 0.2.7 was the argparse
CLI release and did not carry the display. The target is restated without a
number: the first release after the display spike ratifies, sequenced with
the supervisor core (which needs a session anchor under any transport), under
the maximal-wow budget. The obligation is unchanged — under the
workspace-and-containment thesis this row is release-blocking wherever the
containment claim is user-visible.

Owner: `contained-display`, the workstream opened for this row on 2026-08-19 at
the product owner's direction. It is named for its subject rather than for v027,
because a workstream named after a release either outlives it or mis-fits it
when scope moves. It owns the transport decision, the interim mitigation for the
window before that transport ships, clipboard policy, and the regression test.
The `xdg-open` shim stays with `recursive-e2e` in v026.

**The URL-open fix is split out of this row and shipped in v026.** The
`xdg-open` and `BROWSER` shim forwarding to a host-side helper behaves
identically under X11, VNC, and Xpra, so the most irritating symptom should not
wait on the transport decision. It is delegated to `recursive-e2e` with the
entry point.

New scope, not present in the gap review.

**Problem.** Two defects share one root cause. The container is an X client on
the developer's own session, which grants it a full trusted session credential
— recorded as
[a bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
— and gives it pixels with no desktop integration, so link clicks go nowhere
and the clipboard is intermittently unreliable.

**Direction.** GUI applications run inside a display environment owned by the
capsule, reached over VNC, with noVNC available so that a browser is a
sufficient client. Nothing host-side is shared.

The product-owner rationale is not only security. A window that is visibly its
own desktop makes the containment boundary legible at a glance, which reinforces
the product's central claim in every screenshot a reader will ever see.

**Consequences beyond the two defects.**

- Session persistence: disconnecting leaves the IDE running, so work resumes
  exactly where it stopped. X11 passthrough cannot do this, and it supports the
  product's resumability claim directly.
- The platform matrix largely collapses. With a browser as the client, macOS
  and Windows no longer require XQuartz or WSLg. This substantially subsumes the
  proposed WSL2 work, which is why transport must be decided before that work is
  scheduled.
- A browser inside the capsule makes dev-server preview work without host
  networking, which bears on the open sample-project port and networking items
  and on the JCEF preview bug.
- The same mechanism permits a capsule running on a remote host later. Not V1,
  but no longer foreclosed.

**Accepted regressions, to be confirmed by use before ratification.**

- A VNC desktop is a single virtual screen; multi-monitor working is lost.
- Perceived latency in a Java IDE is worse than local X, less so with a native
  VNC client than in a browser tab.
- Clipboard becomes text-only; images and files no longer cross.
- Link clicking is not fixed by the transport. An `xdg-open` shim forwarding to
  a host-side helper is required under every candidate transport and should be
  treated as unconditional.

**Required outcome.**

- GUI use requires no host X socket, no host X credential, and no `xhost` grant.
- The VNC endpoint binds to loopback only and its port is allocated
  dynamically. A fixed port reproduces the PostgreSQL 5432 collision already
  observed on this host, and a non-loopback bind would introduce a new host
  exposure in the product positioned on containment.
- Access is authorized per run by a recorded token rather than a static VNC
  password, and that authorization appears in the run manifest so inspection can
  report it.
- The `xdg-open` forwarding shim ships regardless of transport.
- X11 passthrough, if retained at all, is opt-in with its trade-off documented,
  and is not the default.

**Method.** Spike a contained VNC or noVNC session and Xpra seamless mode, then
perform a full day of ordinary development inside the result before ratifying
it into V1. Aesthetics that hold at hour six are the relevant test.

### Curated Agent Choice: Claude Code, Codex, And Antigravity

Verdict: `in-v1`

Decided: 2026-08-16, by the product owner. V1 offers three curated agent
components covering Anthropic, OpenAI, and Google, and the developer chooses.

Owner: unassigned.

This is the deliberate selection that `D-0005` anticipated, not a change to it.
That decision adopted an agent-neutral base with agent CLIs as optional,
explicitly selected components, and named Antigravity CLI as the first planned
V1 agent component with its implementation left to a later task. No new decision
record is required.

**The Google slot is Antigravity CLI, not Gemini CLI.** `D-0005` verified on
2026-08-02 that Gemini CLI is not deprecated — stable `0.53.1`, active
repository — so its exclusion is a product-boundary choice rather than a claim
about Google's support status. Antigravity is Google's current terminal agent
surface and is therefore the curated V1 choice. Gemini CLI remains unselected
and may be reconsidered later as an additional component.

**What does not change.** Bases remain agent-neutral. No ambient agent CLI is
installed into any base and no agent credential or state directory is mounted by
default. Components materialize per developer after explicit authorization, as
Claude Code already does.

**Required outcome per agent.**

- An exact pinned identity and acquisition behavior, with checksum verification
  where the artifact is downloaded.
- A license and redistribution analysis performed rather than assumed. Claude
  Code required per-developer download after explicit terms authorization
  because it cannot be redistributed; each of the other two needs the same
  question answered on its own terms before any base or component decision.
- A credential transport and persistent state contract that does not grant host
  access merely by being installed.
- Inspection output that reports which agent is selected, where its state lives,
  and what it was authorized to do.

**Test impact is smaller than it looks.** Eight assertions across five test
files assert that Gemini CLI is absent. Most remain correct and should be kept:
they assert that the *base* carries no agent, which is exactly `D-0005`'s rule
and applies equally to the three selected agents. Only the `.gemini` state-mount
assertions in `tests/test_codium_with_claude.py` and `tests/test_cli.py` need
revisiting, and only if Gemini is later selected.

**Why it earns V1 scope.** Agent neutrality is a claim no vendor-adjacent tool
can make, and it positions DevCapsule as substrate rather than as a partisan of
one model provider. It also matters directly to the learner use case, where the
developer arrives with whichever subscription they already have rather than the
one the product prefers.

**Estimated cost.** Days per component given the existing `claude_code.py`,
`codex.py`, and `postgresql_client.py` patterns. The licensing, credential, and
state contracts dominate, not the packaging.

### A Fourth, Open-Source Agent On A Self-Hosted Model

Verdict: Case A is `v1-optional`, decided 2026-08-30 by the product owner —
considered after a release candidate exists; its entry in *Optional For V1*
below states the call. Case B remains `proposed` as `deferred`. Raised by the
product owner on 2026-08-16; split into two cases here so that neither is
decided by silence.

**Case A — bring your own endpoint.** `v1-optional` since 2026-08-30; the
original proposal was `in-v1`. An open-source terminal
coding agent configured against a user-supplied OpenAI-compatible endpoint, base
URL, key, and model. This covers a self-hosted server on the developer's own
hardware, a lab machine such as the product owner's DGX-2, or any local runner
the developer already operates.

**Case B — DevCapsule runs the model. Proposed `deferred`.** DevCapsule detects
host capacity and runs a model server itself when the machine can support one.

**Why the split matters.** Case A already delivers "the user runs their own
model". Case B's marginal value over Case A is not capability but convenience:
DevCapsule installing and managing the server. That convenience costs GPU
capability profiles, model-weight licensing, capacity detection with honest
refusal, and a shared model server — which is precisely the service-dependency
model ruled out of V1 on 2026-08-14 as too expensive for the benefit. Case B
also depends on CUDA support, whose V1 status is one of the five undecided
scope questions. Case A is a component plus a configuration surface.

**Why it earns consideration at all.**

- It is the only agent configuration with no per-token cost, which matters
  directly to the learner use case: "let the agent run flat out" and metered
  billing are in tension, and a learner may hold no subscription.
- It removes the implicit asterisk in the containment claim. Today nothing
  leaves the capsule except the developer's entire codebase, sent to a vendor.
  A self-hosted endpoint closes that, and opens the audience that cannot send
  code to a vendor for employer or regulatory reasons.
- With three vendors plus a vendor-free option, the neutrality claim is
  complete rather than partial.

**What Case A requires.** Mostly credential transport: a key must reach the
capsule without being baked into an image, exposed through container
environment metadata, or written into evidence. The existing mode-0600 files,
read-only binds, structural redaction, and runtime-plan machinery already cover
this shape. Beyond that it is agent selection, pinned acquisition, and the same
per-agent state contract the other three components require.

**Open choice.** Which agent. Criteria: terminal-native so it fits the capsule
model; a permissive licence so redistribution is not the Claude Code problem
again; OpenAI-compatible provider configuration so Case A is configuration
rather than a port; and active maintenance. Aider, Goose, OpenHands, opencode,
and Continue are candidates to evaluate rather than a pick already made.

**Honest risk.** Open-source agents driving self-hosted models remain
meaningfully weaker at sustained agentic coding than the frontier CLIs. A launch
demonstration showing a learner's agent flailing would be a negative proof point
landing on the use case the story makes central. Validate quality on a
course-sized task before the announcement claims parity, and be willing to
present this option with its tradeoffs stated rather than as a peer of the other
three.

### IDE Coverage: PyCharm Suffices For V1; Java Is A Separate Question

Verdict: `in-v1` that PyCharm is the only IDE V1 requires. The Java environment
is `proposed` with its release target undecided.

Decided: 2026-08-16, by the product owner, on the basis that the projects being
started before the V1 announcement will all be Python.

**What this settles.** IntelliJ IDEA Community was pulled toward V1 by the
learner use case, because a Java course cannot use PyCharm. With the product
owner's own dogfooding projects all in Python, no V1 acceptance criterion
depends on a second IDE. IDEA returns to being optional audience expansion.

Python with JavaScript and TypeScript is already covered by the `fastapi-webapp`
sample, and better than when that sample was built: this repository's
[configuration research](../../design-notes/fastapi-webapp-configuration-research.md)
records that JavaScript, TypeScript, and CSS support moved into the free core
tier in 2026.1.

**The Java question, opened 2026-08-16.** The product owner wants a
full-featured Java environment soon after v026 and is favorable to Eclipse. Two
routes, with materially different costs and different strategic value.

*Eclipse.* Licensing is unambiguous under EPL-2.0. That is a genuine advantage
over the JetBrains route, because the same configuration research records that
JetBrains merged Community and Professional in 2025.1, that Community 2025.2 was
the final standalone Community release, and that from 2025.3 everyone is on the
unified build. A JetBrains Java IDE therefore means the unified build under a
free tier, which is a terms-and-acquisition question of the Claude Code shape
rather than a licensing non-event.

Eclipse is also a genuinely new integration — SWT over GTK rather than Swing
over the JetBrains Runtime, `eclipse.ini`, a `-data` workspace, `~/.p2`
provisioning state — and therefore the far stronger test of gap `F3`'s claim
that a configuration can be authored through supported contracts rather than by
copying PyCharm's private implementation. Four of the thirteen recorded bugs are
JetBrains-runtime-specific, so a different toolkit is how the project learns
which contracts are real abstractions and which encode JBR's quirks.

*IntelliJ IDEA.* Reuses the tarball layout, `bin/*.sh` entrypoint, JetBrains
Runtime, and settings-directory model almost entirely. Days rather than weeks,
and correspondingly weak as evidence of genericity.

**Sequencing note.** A contained display is toolkit-agnostic, whereas X11
forwarding is precisely where SWT and GTK differences surface. Java costs less
if it follows the display work rather than preceding it.

**Open.** Whether the Java environment falls inside the V1 window, where it
competes with concurrency and the entry point, or immediately after it, where it
becomes the first post-V1 milestone and gives the announcement a concrete next
promise.

**Amended 2026-08-29, by the product owner.** The open question above is
settled: Java is inside V1, as samples — a Java library project and a Quarkus
REST service — under the maximal-wow release ruling recorded in *The Release
Budget* row. The Java library sample doubles as the showcase for the
*DevCapsule On The Side* row, using an existing project of the owner's that
fits it. The Eclipse-versus-IDEA route choice and the sequencing note above
remain open and unchanged; what is no longer open is whether Java waits for a
later release.

**Amended 2026-08-30, by the product owner.** The route choice is settled as
*both*: Eclipse **and** IntelliJ IDEA are supported for the Java environment,
with **Eclipse the default** and the choice changeable by the user in their
project configuration. This keeps Eclipse's role as the strong genericity test
of gap `F3` (a genuinely different toolkit) while retaining the low-cost
JetBrains route. The sequencing note above — Java costs less after the
contained-display work — still stands.

### The Workflow Ships As An Optional Component

Verdict: `in-v1`

Decided: 2026-08-18, by the product owner.

Owner: `workflow-improvements`, assigned 2026-08-18 and responsible for defining
the final shape of the workflow component. Release target: V1; its position
within the release shape is not yet set, because the shape itself is unbuilt.

Serves `R-PRODUCT-004`. Discharges the unstated deferral named in shortcoming 8
of the [V1 readiness assessment](2026-08-16-v1-readiness-assessment.md), which
held that deferring workflow tooling past V1 is defensible but leaving the
deferral unstated is not. It is stated below.

**Decision.** The workflow developed in this repository is offered to adopters
as a component they may choose, not as something the product imposes. An
adopter may install it, install a different workflow, or use none, and the
product works in each case.

**Rationale, in the product owner's terms.** Many users will not have had time
to develop a workflow that addresses what this one addresses. Those users are
well served by being able to adopt one that makes working with agents better.
Users who already have something better keep it, and lose nothing by the offer.

**This ratifies rather than changes `R-PRODUCT-004`.** That requirement already
says the workflow should be available to users of environments this project
creates "when they choose that mode". The optionality is in the requirement;
what was missing was a release commitment to actually ship it, and an owner.
Both are recorded here.

**Consistent with `D-0005`.** Bases stay neutral and components materialize per
developer after explicit authorization. The workflow becomes one more curated,
optional component, on the same footing as the three agent components, rather
than an assumption baked into the base.

**The open sub-question: whether the component includes tooling.** The original
design assumed the human/agent pair is itself sufficient tooling. This
repository's own use gives a mixed verdict, and the split is consistent enough
to design against:

- The assumption *held* wherever judgment was required — writing intake items,
  routing work, resolving the registry-row conflict by ownership rather than by
  diff, and choosing on 2026-08-18 to append to the outbox where the documented
  reset would have destroyed undelivered mail. A tool following the letter would
  have got that last one wrong.
- The assumption *failed* wherever verification was required, and failed the
  same way each time: two intake items sat stranded on a branch for two days
  while a checkpoint asserted they were delivered; a handoff carried "awaiting a
  pull request" past the merge that resolved it; the registry collided as a hot
  shared file in `PR #26` and `PR #28`.

The failures share three properties that better prompting does not remove.
Verification is work whose expected result is "nothing to report", so it is the
first thing dropped and its omission is indistinguishable from its performance;
the agent reads its own documents as evidence; and nothing breaks when the
invariant is violated, so no signal exists for the agent to notice.

The shape this suggests, offered to the owner as an argument rather than a
specification, is **the agent writes and the tool checks** — a small set of
verifiers and two or three mechanical actions, not a workflow engine, since an
engine would displace the judgment layer that demonstrably works. It also has an
adoption argument independent of correctness: the user this row is for will not
read a 1,838-line normative document, but will run a command that tells them
what is wrong.

Not decided here. Sequenced behind the information-model task delivered to
`workflow-improvements` on 2026-08-18, because verification tooling written
against terms that are about to be renamed would be built twice.

**A storage boundary now constrains the shape.** Decided 2026-08-19 by the
product owner. Durable records — requirements, decision records, bugs, and
user-facing documentation — stay on `main`, on the main branch, where they are
reviewed and adjacent to the code that references them. Coordination state —
status, handoffs, intake, disposition logs, checkpoints, and the registry —
moves off the main branch, with a detached branch as the preferred shape because
it is the simplest thing that works.

The decision followed a measured case: 84% of non-merge commits since adoption
touch no code, work management outnumbers product code 80 to 32 with workflow
definition already discounted, and four of ten pull requests existed only to
deliver mail. Whatever storage shape the component ends up with is what adopters
inherit, so this is a product decision rather than repository housekeeping.

The owner keeps the file list, the cross-boundary link convention, the timing,
whether any of it is a V1 commitment, and how the ref is written and read. On
this analysis the outbox concept does not survive the change, which is why the
information-model task was told to treat it as contingent.

**Required outcome for V1, as far as this row can state it.**

- An adopter can obtain the workflow as a component, and can decline it without
  losing product function.
- What the product actually depends on is stated, so that "install a different
  workflow" is a real option rather than an aspiration. `workflow-improvements`
  assessed that dependency as three things — `AGENTS.md` as the agent's entry
  point, `workflow-type` in `.devcapsule/devcapsule.toml`, and the
  `engineering-docs/` layout — and that assessment is the natural starting
  point.
- Starting does not require reading the full normative document first.
- Acceptance evidence is a fresh project in each configuration: one that
  declines the component and works, and one that adopts it and can begin a
  workstream from the component's own instructions.

The owner completes these criteria as it defines the shape; they are stated here
so the row is checkable rather than aspirational, not to constrain the design.

**Explicitly not decided by this row.** Whether the component ships with
verification tooling; whether the workflow's text lives in this repository or an
extracted one; and whether the workflow owes humans a separate readable
document. The latter two are `project-management` decisions still held in its
intake, and neither blocks this row, because shipping as an optional component
is compatible with every outcome of both.

**Cost.** Unestimated, and deliberately so: the shape is undefined and the
information-model task precedes it. This is the only `in-v1` row carrying no
estimate, which matters when the release shape is rebuilt.

### Independent IDE Surface: VSCodium On The Normal Project Path

Verdict: `in-v1`

Decided: 2026-08-27, by the product owner: retiring the legacy
`codium_with_claude` command and moving VSCodium onto the normal project path
is a high-priority task, because V1 must showcase an independent,
fully open-source IDE.

Owner: unassigned. Routing options: `recursive-e2e` (owns the v0.2.7 CLI and
launch framework this must integrate with, but is paused with Stage 7
remaining) or a newly registered product workstream. This supersedes the
earlier "concurrency was chosen over VSCodium" trade for the release shape,
which must be rebuilt accordingly.

**Scope.**

- Retire the `codium_with_claude` command tree. The name welds the IDE to one
  agent, which contradicts the agent-neutrality claim; the replacement is a
  neutral `codium` interactive surface with agents as separately authorized
  components, the shape the PyCharm path already has.
- The embedded resolution matrix gains `codium` as a second
  `interactive-surface` value with its own pinned component table; `init`,
  the lock, and `project run` select it like any other node.
- Launch-path parity verified on the Codium surface: host-browser bridge,
  runtime plan, run manifest and inspection, GUID-derived cleanup.
- The extension-ecosystem boundary is stated, not discovered: VSCodium ships
  Open VSX, so TS/JS/HTML/CSS (built into core) are first-class while
  proprietary marketplace extensions such as Pylance are unavailable. The
  showcase therefore leads with a JS/TS project rather than Python.
- Acceptance evidence: a named sample project proving install → init → run →
  agent session → IDE work → clean exit on the Codium surface. Candidate,
  proposed 2026-08-27: the chess-club website — a small HTML/JS/TS site
  started by one developer and maintained by a part-time student, exercising
  the sequential-handoff story no other sample covers. It additionally
  depends on dev-server preview and promotes the different-UID
  second-developer proof from unverified to gating.

### Capsule Supervisor And Multi-IDE Sessions

Verdict: `in-v1` for the supervisor core; `deferred` for the
desktop-integration layer, whose stated later home is the first post-V1
milestone.

Decided: 2026-08-29, by the product owner, ratifying the split exactly as
proposed: the supervisor is in V1 as the capsule's lifecycle anchor — entry
process, IDEs as supervised children, supervised cleanup, explicit session
end, headless-capable, which is what answers the release-blocking
non-interactive-runs backlog item. Desktop integration — the tray icon,
one-click secondary IDEs, and multi-IDE sessions — is post-V1, so V1 states
the one-interactive-IDE limitation. Raised by the product owner on
2026-08-27.

Owner: `contained-display`, assigned 2026-08-30 by the product owner — one
workstream for one sequenced effort, the supervisor core first and the
contained display as its first consumer. The assignment is delivered to that
workstream's intake.

**The revised design assumption.** Today a capsule's lifetime is one
foreground IDE process: the launcher execs the IDE as the container's main
process and the capsule ends when it exits. That identity made exit cleanup
automatic, and it makes multi-IDE sessions impossible. Common adopter
scenarios — Java or Python backend in PyCharm/IDEA/Eclipse beside an HTML/TS
frontend in VSCodium — need two IDEs against one checkout, and the two-capsule
dodge collides on IDE state directories and ports.

**Direction.** A minimal supervisor/helper program is the container's entry
process. It offers one-click launch of secondary IDEs, desktop integration
such as a tray icon, and an explicit session end. Capsule lifetime becomes
supervisor lifetime; IDEs are children; cleanup becomes supervised rather
than a side effect of one process exiting — which revises the semantics of
the reaping item in the coordination backlog.

**Why it reaches further than multi-IDE.**

- It is the natural mechanism for non-interactive runs (the release-blocking
  backlog item): an unattended capsule is the supervisor with no GUI
  children.
- The owner's e2e thesis: if the supervisor is well integrated into the
  desktop, IDEs launched from it are too — and the supervisor is DevCapsule's
  own code, so desktop integration becomes automatable proof rather than
  manual GUI acceptance.
- A contained display needs a session anchor (tray, launcher) anyway; built
  transport-agnostic, the supervisor serves host-X11 today and the contained
  display later.
- Natural host for the host-open bridge client, run self-identification, and
  a health/inspection endpoint.

**Costs and risks.** A new product component with PID-1 duties (signal
forwarding, child reaping), a tray/toolkit choice per transport, and constant
pressure on "minimal". The resolution matrix's single `interactive-surface`
value becomes a set of installed surfaces plus the supervisor as entry
process.

**Open decisions.** The 2026-08-29 ruling settled the V1-window question (see
the verdict above): the supervisor core is in V1, and the desktop-integration
layer leads the first post-V1 milestone rather than V1 carrying a one-IDE
caveat forever. Still open: how the VSCodium row sequences against the
supervisor — its scope should be shaped to land inside the supervisor model
rather than adding a second exclusive-foreground launch path — which is the
`codium-surface` registration question. The supervisor core itself found its
owner on 2026-08-30: `contained-display`, supervisor-first, display behind
it.

### The Release Thesis: Workspace And Containment

Verdict: `in-v1`. The thesis is the release framing itself; it has no deferral
home.

Decided: 2026-08-29, by the product owner, settling the first of the four
resume questions recorded at the 2026-08-27 pause. The recorded alternatives —
a containment-led release or a workspace-led release — are both rejected as
sole leads.

Owner: `project-management`. The thesis is applied here, when writing the
remaining rows of this ledger; it assigns no implementation work of its own.

**Statement.** DevCapsule V1 is a workspace product wherein agents are sensibly
contained so that the user can happily run yolo mode by default. Workspace is
the category; containment is the differentiator. This is the product owner's
formulation, verbatim in substance: the two candidate theses were never
competing capabilities, only competing headlines, and the release claims both
because the containment is what makes the workspace safe to hand to an agent.

**Consequences.**

1. **Every user-visible containment claim is release-blocking.** The
   obligations this ledger already records stop being deferrable: the
   [X11 session-credential bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
   must be closed by the contained display before the claim is announced, and
   the Docker-socket asterisk in the fourth-agent row must be resolved or
   plainly disclaimed. An agent running unattended for hours with the host
   session credential is precisely what the headline says cannot happen.
2. **Yolo mode by default is promoted from dogfood workaround to product
   requirement.** Provisioning must seed the agent-side bypass-permissions
   configuration so the capsule comes up with the agent already trusted to act
   freely inside the boundary; today that seeding is a manual step. The
   boundary must be strong enough that this default is honest.
3. **Breadth is decided per-row, not wholesale.** The remaining gap rows
   (`F1`–`F8`, `E1`–`E8`), Java, CUDA, and the starter catalog no longer wait
   on a thesis; each is judged by one test: *does this surface keep the
   yolo-by-default promise honest and provable within the V1 window?*
4. **The announcement already carries this thesis.** The one-sentence
   positioning in `docs/product/v1-announcement.md` — a reproducible, AI-ready
   workspace with explicit host-access boundaries — is the workspace noun with
   the containment clause. Its accuracy against the implementation is a
   separate, recorded review.

### The Release Budget: Maximal Wow, In Spirit

Verdict: `in-v1` as the release framing, alongside the thesis row above.

Decided: 2026-08-29, by the product owner: "we can take longer than the initial
twelve weeks we budgeted, but it will be wow."

Owner: `project-management`, applied when writing and re-judging rows.

**Statement.** V1 ships when it earns a maximal wow factor in the spirit of the
workspace-and-containment thesis, not when a calendar window closes. The
twelve-week budget is lifted.

**Consequences.**

1. The proposed twelve-week release shape — never ratified, and already stale
   after the contained display moved — is now **superseded**, not merely stale.
   A release shape must be rebuilt wow-first once the remaining gap rows are
   written.
2. Every deferral whose only justification was the twelve-week window loses
   that justification and must be re-judged on the thesis test alone: VSCodium
   (`F4`), the conformance suite (`E5`), the starter catalog (`F5`),
   scaffolding commands, the service-dependency model, and CUDA.
3. "Longer" is not "unbounded": rows still carry acceptance evidence, and the
   wow bar is the thesis made visible — a contained workspace a reader can see
   is safe to hand to an agent in yolo mode.

### Supported Project Types: The Union

Verdict: `in-v1`

Decided: 2026-08-29, by the product owner. The announcement's concrete type
list and the 2026-08-27 supported-project-types recap had diverged; the owner
ruled the divergence reconciled by taking the union. This row also finally
writes the recap into the ledger, which had waited on the release thesis.

Owner: `project-management` for the list itself; each sample is owned by the
workstream that builds it.

**The union set.**

- Python command-line tooling;
- Python library projects;
- Python FastAPI web services, including a JavaScript/TypeScript frontend
  (the recap's "Python+TS web app", already anchored by the `fastapi-webapp`
  sample);
- Python data-research projects (anchored by
  `devcapsule-sample-trading-research`, the first named real project);
- Java library projects (also the *DevCapsule On The Side* showcase); and
- Quarkus REST services.

**Supersedes** the recap's "Java explicitly not claimable", per the amended IDE
coverage row. Of the recap's other exclusions, CUDA now carries the
`v1-optional` verdict in *Optional For V1* below — decided at candidate time,
no longer gating the plan; the team claim was settled on 2026-08-29 by the product
owner — the workflow is promised for small teams of **one to five
developers**, as recorded in `docs/product/issue-tracker-positioning.md`. This
also resolves the previously noted record tension between the 2026-08-19
use-case set (which included small teams) and the recap (which excluded team
claims), in the use-case set's favor.

### DevCapsule On The Side: Adopting A Third-Party Project

Verdict: `in-v1`

Decided: 2026-08-29, by the product owner, who supplied the scenario verbatim
and holds a Java library sample project that fits it.

Owner: none yet — acceptable under the 2026-08-29 amendment to this ledger's
owner rule; assigned when the work is picked up. The natural candidates are
the yet-unregistered `codium-surface` workstream or a new workstream
registered with it.

**Scenario.** An experienced software engineer, a hobbyist, or a student wants
to browse and work on a third-party project that has no DevCapsule support.
Sending a pull request that plants a `.devcapsule` directory inside an
established upstream project is obviously not an option. A suitable command
line therefore organizes a *devcapsule on the side*: the full workspace —
manifest, lock, state, project memory — lives outside the third-party tree,
which stays pristine.

**Why it is new scope.** Today the manifest is strictly in-tree:
`manifest_for` requires `<root>/.devcapsule/devcapsule.toml`
(`devcapsule/project_configuration.py:814`), and project discovery walks
upward looking for that directory. On-the-side needs an out-of-tree manifest
home, a discovery-or-registration path to it, and a stance on where its
project memory lives.

**Why it belongs to the thesis.** Browsing unknown third-party code is the
single strongest yolo-mode story the product has: the user is running someone
else's code, and an agent against it, precisely because the boundary makes
that safe. It is the containment differentiator demonstrated on the workspace
category's most common cold-start — code you did not write and do not yet
trust.

**Showcase.** The Java library sample from the amended IDE coverage row.

### Human-Readable Workflow Documentation

Verdict: `in-v1`

Decided: 2026-08-29, by the product owner: the project owes its human readers
— its own product owner, and every adopter — workflow documentation
structured for understanding rather than for lookup. This dispositions the
2026-08-17 intake item as accepted release content serving `R-PRODUCT-004`:
an adopter who cannot understand the workflow cannot adopt it.

Owner: none yet; assigned at pickup per the 2026-08-29 unowned-rows ruling.

**Recommended shape, inherited from the intake item and not yet ratified.**
An explicit onramp inside `WORKFLOW.md` — "if you are a human, read these
sections and stop" — with the remainder marked reference material, building
on the roughly 150 human-facing lines already written (*Purpose And
Principles*, *How To Read This Document*, *Checkouts, Branches, And
Workstreams*). A second parallel document is the shape to avoid, on this
project's own evidence: duplicated normative text has diverged twice, and
the non-normative copy loses because nobody's work breaks when it is wrong.
Roughly a session's work in the recommended shape.

**Sequencing.** Originally settled together with the workflow extraction
question; that question closed on 2026-08-29 — V1 ships with this workflow,
extraction is not pursued, and alternative-workflow installability is a
`v1-optional` check — so the recommended onramp shape has no remaining
blocker, though it stays recommended rather than ratified. The division of
labor with the adopter-facing
[issue-tracker positioning](../../../docs/product/issue-tracker-positioning.md)
stands: that document is the *why*, this one is the *how*.

**Acceptance evidence.** A reader following the marked human path can state
what adopting the workflow asks of them and what they get, without reading
the reference sections.

### Workflow Packaging As A Vendor "Skill"

Verdict: `rejected` for V1, with a stated reconsideration condition.

Decided: 2026-08-29, by the product owner: DevCapsule does not package its
workflow as a vendor "skill" for V1, **unless** the skills convention is
identified as widely adopted and as buying our users something tangible. The
condition is the reopening trigger; absent it, this stays rejected.

Owner: not applicable while rejected; the reconsideration, if triggered, is a
`project-management` routing decision.

**Grounds, inherited from the 2026-08-17 intake item** — all three are
existing project decisions rather than opinions: skills are a vendor
mechanism while `R-PRODUCT-004` requires the workflow to transfer across
agents; this repository's own root instructions forbid storing anything in
agent-specific files for exactly that reason; and `AGENTS.md` is the neutral
entry point several agents already read, so reshaping around one vendor's
loader would invert a deliberate decision. Rejecting costs nothing today.

**The finding underneath it, deliberately kept.** What a skill actually buys
is progressive disclosure — load a small core, pull the rest on demand — and
that fix is portable: a small mandatory core (selection, synchronization,
intake, checkpoints) with procedure in linked files loaded when reached.
`AGENTS.md` currently points at a single 1772-line document with no layering,
a cost paid on every turn of every session. This layering work folds into the
*Human-Readable Workflow Documentation* row's onramp shape; it does not die
with the skill rejection. If vendor packaging is ever wanted after the trigger fires, the
natural shape is per-agent adapters generated from the neutral source,
materialized per developer after explicit authorization — exactly like the
curated agent CLIs — so the neutral source never depends on the adapter.

## Optional For V1, Decided At Candidate Time

Created 2026-08-29 at the product owner's direction: a separate list of
features that are optional for V1, with the in-or-out call deliberately made
at the end, once a V1 candidate exists. Parking an item here is itself a
decision — it removes the item from the set gating the release plan without
silently dropping it. Each entry states what the candidate-time call actually
decides.

### CUDA

Verdict: `v1-optional`. Moved here 2026-08-29 by the product owner, closing
the gap review's functional scope decision 1 as a release-plan gate.

**What already works, unclaimed.** The v0.2.7 CLI's supplementary-argument
syntax ends DevCapsule arguments at `--` and hands everything after it
verbatim to `docker run` (`devcapsule/commands/project.py`, `run` and
`run-image`, with a printed warning). A user can therefore grant GPU access
today with `devcapsule project run -- --gpus all`, given the NVIDIA container
toolkit on the host; pip-installed frameworks that bundle their CUDA runtime
(PyTorch and peers) then work against the injected driver. This is the expert
path: verbatim, warned, and unvalidated.

**What the candidate-time call decides.** Whether V1 *claims* CUDA — which
means the `E8` validation set (positive device authorization, negative
no-device behavior, a real workload), documentation, possibly a first-class
authorization instead of raw passthrough, and the NVIDIA/CUDA recipe's
supported-versus-experimental status — or ships with the passthrough
available but CUDA absent from the announced feature set.

### An Alternative Workflow Can Be Installed

Verdict: `v1-optional`. Created 2026-08-29 by the product owner, who also
retired the word "seam" from this question as unintuitive for a human reader;
the plain statement below replaces it. This dispositions the 2026-08-17
extraction intake item: **V1 ships with this workflow** — `R-PRODUCT-004`
stands unamended — and whether an adopter can install an alternative workflow
is checked against the V1 candidate, not decided now.

**What the check involves, in plain words.** As far as is currently known,
the product itself depends on exactly three things: `AGENTS.md` as the entry
point an agent reads first, `workflow-type` in `.devcapsule/devcapsule.toml`,
and the `engineering-docs/` directory layout. Everything else in
`WORKFLOW.md` is protocol content an adopter could replace wholesale. The
candidate-time call decides whether V1 verifies and documents that boundary —
saying so in *Applying This To Other Projects*, which currently assumes
adopters take this workflow rather than choose one — or leaves the workflow
fixed for V1. The check is a documentation change, roughly one editing
session, no code.

**Extraction to a separate repository is not pursued.** Its named costs stand
recorded in the dispositioned intake item (Git history): the dogfood loop
would cross a repository boundary, a separate repository implies versions and
migration for a workflow that changed eleven times in two days, and the
submodule-versus-vendoring tradeoff should be decided once with
`sample-projects`. It would only become worth revisiting after installable
alternatives exist, at which point it is packaging rather than guesswork.

### Fourth Agent, Case A: Bring Your Own Endpoint

Verdict: `v1-optional`. Moved here 2026-08-30 by the product owner from its
proposed `in-v1` status; the full case, requirements, agent-selection
criteria, and honest risk stay in the decided-rows entry
*A Fourth, Open-Source Agent On A Self-Hosted Model*.

**What the candidate-time call decides.** Whether the bring-your-own-endpoint
component (an open-source terminal agent against a user-supplied
OpenAI-compatible endpoint) ships in the announced V1 feature set or becomes
early post-V1 work. The strategic stakes recorded in the row — no per-token
cost for the learner, closing the containment claim's vendor asterisk,
completing the neutrality story — are the criteria for that call.

### Workflow Improvements At The Release Candidate

Verdict: `v1-optional`. Created 2026-08-30 by the product owner, settling the
carried process-to-product commit-ratio question: **`WORKFLOW.md` is
considered frozen until a release candidate exists.** This entry is the
check scheduled for that moment — whether workflow improvements are needed,
against evidence from the intervening product-focused stretch.

**Recorded interpretation of the freeze**, so it does not contradict decided
rows: frozen means no new protocol changes — the rules stop churning. Work
already decided as release content is not blocked by it: the `in-v1`
*Human-Readable Workflow Documentation* onramp restructures presentation
without changing rules, and the pre-commit invariant checks mechanize
existing rules. `workflow-improvements` staying open-idle (decided
2026-08-29) is consistent: it resumes at this check, or earlier only if a
defect in the frozen rules blocks work.

### D-0001 Catalog Freshness And Update Preview

Verdict: `v1-optional`, **agent-proposed 2026-08-30, awaiting ratification** —
the one Optional entry not yet ruled by the product owner. This is the gap
review's functional scope decision 2: whether `D-0001`'s catalog freshness,
security-advisory warning, and explicit update-preview contract ships in 1.0.
The candidate-time call decides whether the contract is implemented against
the starter catalog as it actually ships, superseded, or explicitly deferred;
parking it here keeps the decision visible without gating the plan.

## Gap Verdicts: F1–F8 And E1–E8

Written 2026-08-30 against the
[V1 gap review](../../design-notes/devcapsule/2026-08-06-v1-gap-review.md),
under the workspace-and-containment thesis, the maximal-wow budget, and the
per-row test those rows establish: *does this surface keep the
yolo-by-default promise honest and provable?* Verdicts follow from the
owner's recorded rulings wherever one applies; the entries marked
**agent-proposed** are new judgment and await ratification. Owners are
assigned at pickup per the 2026-08-29 unowned-rows ruling. The gap review's
detailed required outcomes remain normative; these rows record the release
verdict and what has already happened.

### F1: Clean Checkout To Ready Development Environment

Verdict: `in-v1`. Follows from the announcement's core promise and the
readiness assessment's at-risk item 4, which this row gives its single home.
Owner: none yet. The ecosystem-bootstrap adapter contract, explicit first-run
consent, and idempotent readiness remain as specified; the Java samples now
supply the required non-Python adapter case. Source bugs:
[ecosystem-aware project bootstrap](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md)
and
[component tooling runtime path](../../bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md),
both release-blocking through this row.

### F2: Complete The PyCharm Reference Experience

Verdict: `in-v1`. PyCharm is the decided reference IDE. Owner: none yet.
Partially delivered by v0.2.7: the configuration grammar, elicitation engine,
offline platform locks, and defaults-versus-overrides model shipped with the
argparse CLI. Remaining: the 8 GiB default with real `HostConfig.Memory`
enforcement, Codex CLI/ACP/authentication/restart validation through
component-owned `CODEX_HOME`
([codex-acp-missing-home](../../bugs/devcapsule/2026-08-03-codex-acp-missing-home.md)),
fresh JCEF preview validation, and sanitized extended logging.

### F3: Finish The Reusable Configuration And Component Model

Verdict: `in-v1`. Owner: none yet. The component layer exists
(`claude_code`, `codex`, `postgresql_client`, `pycharm`, and the catalog);
what V1 owes is the documented, testable authoring path. The proof point is
now named by the 2026-08-30 Java ruling: **Eclipse**, a genuinely different
toolkit, authored through the contracts without copying PyCharm's private
implementation.

### F4: Reimplement The VSCodium Proof Point

Verdict: `in-v1`. Subsumed by the decided
*Independent IDE Surface: VSCodium On The Normal Project Path* row (retire
`codium_with_claude`, chess-club sample), shaped to land inside the
supervisor model. The gap review's obligation that survives unchanged:
fresh reproduction of the historical Codium bug reports
(`2026-07-13` run-option parity, `2026-07-16` ambient sudo) against the new
implementation, closing as fixed or obsolete with evidence.

### F5: Ship A Starter Configuration And Demo-Project Catalog

Verdict: `in-v1`. The exact entries — the gap review's scope decision 3 —
are decided by the *Supported Project Types: The Union* row: Python CLI,
Python library, data-research, FastAPI with JS/TS frontend, Java library
(Eclipse default), and Quarkus REST, each with its sample project. The
catalog's success criterion stands: it proves self-service authoring, not
exhaustive IDE support.

### F6: Coherent Inspection And Limited Lifecycle UX

Verdict: `in-v1` for read-only inspection — every effective value and its
source, defaults versus overrides, state slots, sanitized plans, stale-
resolution explanations — plus the already-needed safe binding and adoption.
The destructive state surface (move/remove/clean, profiles) is
**agent-proposed `v1-optional`**, resolving the gap review's scope decision 5
in line with its own recommendation: implement read-only, defer destructive
until onboarding demonstrates need, and record the change rather than omit
silently. v0.2.7's `config`/`state` commands are the foundation. Owner: none
yet.

### F7: Close Safe Expert Runtime Control

Verdict: `in-v1`. Owner: none yet. Partially delivered by v0.2.7: host
capabilities became authorization nodes, and raw docker-run passthrough after
`--` shipped (warned, verbatim). Remaining: structural validation of
repeatable advanced arguments, sanitized explanation of every relaxation, and
the restrictive-workstation-policy boundary. Two attachments:

- **The `project run` security audit** — the readiness assessment's at-risk
  item 2, homed here as a named release blocker: no option may grant host
  access beyond the resolved authorization, and `--force` must never become
  an authorization bypass. User documentation of the interface rides with it.
- **Transitional `pycharm build`: agent-proposed removal** from the supported
  V1 surface in favor of `images build`, which closes the
  [multiline exec rendering bug](../../bugs/devcapsule/2026-07-16-pycharm-build-multiline-exec-rendering.md)
  as obsolete — the gap review's scope decision 4, awaiting ratification
  together with the final list of surviving transitional commands.

### F8: Make V1 Installable And Consumable

Verdict: `in-v1`. Expanded and corrected by the decided *Self-Contained Tool
Entry Point* row: the primary artifact is a Pex scie that runs with no Python
installed, proven on a clean machine, with checksums, embedded revision, and
end-user download-first documentation. Nothing further to decide here.

### E1: Bootstrap And Build A Clean Source Clone Inside Dogfood

Verdict: `in-v1` — **delivered**. The recursive-e2e workstream concluded
2026-08-27 having built exactly this path; the v026.x and v0.2.7 releases
were produced and verified through it. Evidence in
`engineering-docs/archive/2026-08-06-recursive-e2e/`.

### E2: Support Safe Recursive Host-Docker Orchestration

Verdict: `in-v1` — **delivered** (`host_daemon.py`, `recursive_host.py`,
path translation, detached successor launch), same evidence trail. Residual:
the evidence-disposal and retained-container items dissolved from Stage 7
into the coordination backlog.

### E3: Build A Disposable Recursive Dogfood E2E Orchestrator

Verdict: `in-v1` — **delivered** as `devcapsule project recursive-e2e`
(`recursive_orchestrator.py`), which released v0.2.7. Residuals from the
dissolved Stage 7 live in the coordination backlog: the persistence proof and
evidence disposal. The supervisor row revises the lifecycle assumptions
Stage 7 was written against.

### E4: Make E2E Isolation, Evidence, And Cleanup Deterministic

Verdict: `in-v1` — **substantially delivered** with the orchestrator (unique
roots, test-ownership labels, cleanup on interruption). Remaining before the
row closes: the keep-on-failure diagnostic mode confirmed as implemented or
added, and the evidence-disposal backlog item resolved.

### E5: Add A Shared Configuration Conformance Suite

Verdict: `in-v1`, **agent-proposed** — the twelve-week shape's deferral of
this suite died with that shape, and the thesis test now argues the other
way: six project types across PyCharm, Eclipse, IDEA, and VSCodium are only
affordable, and the yolo-by-default claim only *provable*, with common
conformance tests per configuration (schema, formation identity, checksum
rejection, redaction, safe-default plans, repeat launch). The historical
Codium bugs re-close through this suite plus focused VSCodium tests. Owner:
none yet. Awaiting ratification.

### E6: Define The Automated Versus Manual GUI Boundary

Verdict: `in-v1`, as revised by the supervisor row: the supervisor is
DevCapsule's own code, so desktop integration becomes automatable proof, and
the remaining human check stays deliberately small (window appears,
representative use, handoff report). Pixel-level GUI automation stays out.

### E7: Complete Release Engineering And Publication Validation

Verdict: `in-v1`. Owner: none yet. Partially proven in practice: v026.2 and
v0.2.7 shipped as published releases with PEX checksums verified against the
live release. Remaining for V1: the artifact becomes the scie (entry-point
row), immutable OCI digests for the base, the basic security scan, the
clean-download smoke proof, and preserved sanitized release evidence. Signed
SBOMs and attestations stay post-V1.

### E8: Validate Every Platform Feature Actually Included In V1

Verdict: `in-v1` for the claimed set: supported Linux/Docker-host behavior,
safe and authorized runtime profiles, and the GUI path as the contained
display defines it. **The authorization-negative launch proof — at-risk
item 3 — is homed here as required acceptance evidence**: absence of
authorization demonstrably yields no host Docker socket, no host networking,
no development sudo, so `R-PRODUCT-002`, `R-SCOPE-001`, and `R-DOCKER-001`
are demonstrated rather than asserted. CUDA validation follows the CUDA
entry in *Optional For V1*: it is owed only if the candidate-time call
claims CUDA.

## At-Risk Items: Single Homes

The readiness assessment's seven at-risk items, each reduced from several
partial mentions to one recorded home. Recorded 2026-08-30.

1. **External-resource ownership and reaping** → the coordination backlog's
   reaping entry, whose semantics the supervisor row revises (supervised
   cleanup instead of exit-side-effect). Closes the
   [detached-successors bug](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
   when done.
2. **The `project run` interface audit and documentation** → gap row `F7`
   above, as a named release blocker.
3. **The authorization-negative launch proof** → gap row `E8` above, as
   required acceptance evidence.
4. **F1, clean checkout to ready environment** → gap row `F1` above.
5. **The functional scope decisions** → all five now dispositioned: CUDA
   (`v1-optional`), D-0001 freshness (`v1-optional`, proposed), starter
   entries (the union row), transitional commands (`F7`, proposed), state
   surface (`F6`, proposed).
6. **The silent empty-directory failure mode** → the coordination backlog's
   new *Silent Empty Bind-Source Failure* entry: make Docker's invented
   empty bind sources structurally loud, once, in V1.
7. **Submodule pointer publication ordering** → the coordination backlog's
   new *Submodule Pointer Publication Ordering* entry, with `sample-projects`
   the natural owner at pickup — `main` must never advertise a submodule
   pointer no clone resolves.

## V1 Acceptance

**Agent-proposed 2026-08-30, awaiting ratification.** V1 is accepted when:

1. **Requirements demonstrated, not asserted.** `R-PRODUCT-002`,
   `R-SCOPE-001`, and `R-DOCKER-001` reach `validated` through the
   authorization-negative proof (`E8`); `R-SETTINGS-001` through the profile
   prototype lifecycle in use; `R-PRODUCT-004` through the human-readable
   onramp; `R-GTM-001` is already satisfied.
2. **No open release-blocking bug.** Blocking set as of this writing:
   [X11 session credential](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
   (closed by the contained display — a thesis consequence),
   [detached successors](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
   (reaping), the two `F1` bootstrap bugs, and
   [codex-acp-missing-home](../../bugs/devcapsule/2026-08-03-codex-acp-missing-home.md)
   (`F2`). The multiline `pycharm build` bug closes as obsolete if `F7`'s
   removal proposal is ratified; the historical Codium bugs re-close through
   `E5`; the JBR alpha-compositing and native-launcher notes stay reviews,
   not blockers.
3. **Documents exist**: the announcement and issue-tracker positioning
   (exist), the human-readable workflow onramp, end-user install
   documentation with the download-first path, and sanitized release
   evidence for the shipped candidate.
4. **Every `in-v1` row above has found an owner and its stated evidence** —
   the release gate that the unowned-rows ruling explicitly preserved.

## Remaining Ledger Work

The ledger is now structurally complete. What remains: the product owner's
ratification of the agent-proposed items (`E5` in-v1, `F6`'s destructive-
surface split, `F7`'s `pycharm build` removal, D-0001's `v1-optional`
parking, and the *V1 Acceptance* section), and the wow-first release shape,
to be rebuilt from these rows now that the superseded twelve-week shape and
its deferrals are gone.
