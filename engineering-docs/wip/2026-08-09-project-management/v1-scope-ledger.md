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

## Verdict Values

- `in-v1`: committed to the V1 release.
- `deferred`: accepted direction, explicitly outside V1, with a stated later
  home so the deferral is visible rather than silent.
- `rejected`: considered and intentionally not pursued.
- `proposed`: recorded during planning; not yet ratified by the product owner.

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

Owner: unassigned; may warrant a separate workstream rather than joining an
existing one.

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

Verdict: `proposed`. Raised by the product owner on 2026-08-16; split into two
cases here so that neither is decided by silence.

**Case A — bring your own endpoint. Proposed `in-v1`.** An open-source terminal
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

## Rows Still To Be Written

The remainder of this ledger is the next task: one row per gap `F1`–`F8` and
`E1`–`E8`, each with a verdict, an owning workstream, and acceptance evidence;
the five functional scope decisions the gap review left open; a V1 acceptance
section naming which requirement records must reach `validated`, which open
bugs block the release, and which documents must exist; and the seven at-risk
items from the readiness assessment, each reduced to a single recorded home.

The twelve-week release shape discussed on 2026-08-16, including the deferral
of VSCodium (`F4`), the conformance suite (`E5`), the starter catalog (`F5`),
scaffolding commands, the service-dependency model, and CUDA support, is
`proposed` and awaits ratification. It is deliberately not recorded as decided
here.
