# Work order: make “Why DevCapsule?” clear on arrival

Prepared 2026-10-18 at the product owner's request, from the landing-page
review in ResearchInSupportOfDevcapsule. Intended repository home:
`engineering-docs/work-orders/2026-10-18-landing-page-why-devcapsule.md`.
The workstream assignment follows the project's existing workflow on pickup;
this document does not assert that an assignment or implementation has begun.

Human language governs this document. The executor may improve the proposed
wording and presentation using reasonable judgment, while preserving the
outcome, factual limits and ownership rules below.

Amended at the owner's direction on 2026-10-18: replace the right-hand hero
schematic with real recorded product footage. An existing recording satisfies
the baseline; a new complex Eclipse/Java “WOW factor” WebM is a stretch goal
and must not block the landing-page improvement.

## Outcome

A developer arriving at the home page understands, before exploring the
documentation, why DevCapsule could improve their next day of work:

> Let an agent work without repeated routine approvals, then inspect, debug
> and continue its work in a full IDE sharing the same contained environment.
> Return later with the workspace's tools, settings and recorded context
> preserved.

The page connects agent autonomy, developer control and a persistent shared
environment. It makes the practical benefit tangible through a real session.
It gives the visitor a clear next action and accurate expectations of the
current release.

This is a landing-page communication and demonstration task. Success is a
clearer, truthful explanation and a usable path to trying the product.
Increased adoption is a hypothesis, not an acceptance result this work can
establish by itself.

## Starting point and diagnosis

The reviewed home page leads with “Start working on a project right away!”
and describes the IDE, agent, capsule, host permissions, persistence and
product maturity in its opening paragraph. Its later sections explain the
benefits, and `/why/` supplies more of the rationale. The visitor must connect
these pieces to discover the strongest reason to try the product.

The opening promise is generic. The explanation should bring forward the
specific experience DevCapsule enables: the agent works autonomously within
an explicit boundary, and the human retains their development tools in the
same environment. Persistence and engineering continuity reinforce that
promise. They should remain visible without making the visitor learn the
workflow's internal vocabulary first.

This diagnosis is an editorial judgment based on the page and project
documents. It is not a measured usability or conversion finding.

## Scope and ownership

Two repositories participate:

| Repository | Responsibility in this order |
| --- | --- |
| `ccozianu/devcapsule` | Author the landing copy, explanatory copy, captions and demonstration narrative; retain product claims and content decisions here; update the website submodule pin when required. |
| `ccozianu/devcapsule-website` | Render that content, implement layout and demonstration playback, preserve navigation and accessibility, and maintain the content contract. |

Read the current `CONTRACT.md` in the website repository before editing.
Its version-1 interface uses `website:*` markers in the producer's
`README.md`. The current marker set has no demonstration section; the hero
and benefits also have defined shapes. Do not assume that adding arbitrary
Markdown makes it appear on the home page. The three guide cards below the
hero are derived from current-version documentation roles.

Deliver the smallest compatible contract extension necessary for the
demonstration, its captions, and the intended page order. Record it in the
authoritative consumer contract and reconcile the producer's contract record.
Follow the existing compatibility rules; do not introduce a second copy of
authored marketing text into website templates. Keep `README.md` useful when
read directly on GitHub.

Included: hero, benefit hierarchy, a real demonstration, one concrete
continuity example, relevant `/why/` alignment, calls to action, and page
identity metadata affected by the new message. Existing documentation,
release and contribution routes remain discoverable.

Excluded: product runtime changes, authentication/proxy implementation, a
general visual rebrand, documentation completion, competitor research,
analytics infrastructure, paid acquisition, and release-policy changes.
Record a product limitation encountered during the demonstration through the
existing bug/workstream process rather than silently expanding this order.

## Deliverable 1: the reason to care is in the opening

Done means: the initial page view explains the benefit, identifies the actual
product, provides a primary action, and states supported platforms and pre-V1
status legibly. A visitor need not click “Why DevCapsule?” to find the basic
reason to use it.

Use the following as the starting copy. It is a concrete editorial proposal,
not a requirement to preserve every word:

> **Let your coding agent work. Keep your workstation yours.**
>
> Run Claude Code, Codex, or Antigravity without approving every routine
> step. DevCapsule brings your agent, a full IDE, and your project's tools
> together in one persistent container on your own computer.
>
> Your host home directory, SSH keys, and desktop session stay outside by
> default. You decide what additional access to grant.
>
> **The environment your agent tests in is the one you debug in.**

Primary action: “Open your first workspace”, linked through the existing
current-release getting-started resolution. Secondary action: “Watch a
session”, leading directly to the demonstration on this page.

Keep the platform and status line compact: Linux x86-64, Windows via WSL2,
Apache-2.0, pre-V1. Preserve any necessary prerequisite information on the
linked path. The precise line breaks, button labels and distribution of the
supporting sentences between the hero and its immediate continuation are
implementation choices. Keep the headline, core explanation and primary
action readable without a long scroll on an ordinary laptop viewport.

Update `website:social` title and description to reflect the same promise,
within the current contract's limits. Check the actual generated page title,
description, Open Graph and Twitter tags, not only their source marker.

## Deliverable 2: show the real product in the right-hand hero space

Done means: the desktop hero's right-hand `div.workspace-figure`, currently
an invented workspace illustration, is replaced by a real DevCapsule screen
recording, playable inline and expandable, with a crisp frame from the actual
recording as its poster. On narrow screens it follows the opening copy.
The poster must remain informative when playback never starts. Leaving the
schematic there and placing a video far down the page does not meet this
deliverable; neither does a download-only link.

### Baseline: use existing footage if needed

The owner explicitly authorizes an existing recording in the absence of
something better. A new capture is not a completion requirement. Review:

- `engineering-docs/blog/assets/2026-10-04-intellij/first-session.webm`:
  the owner's nominated fallback, showing real IntelliJ interaction.
- `engineering-docs/blog/assets/2026-10-04-intellij/after-restart.webm`:
  a possible companion or source of persistence footage.
- `engineering-docs/implementation-notes/devcapsule/assets/2026-10-04-eclipse/first-session.webm`:
  an alternative showing real Eclipse interaction.

Read the corresponding validation notes under
`engineering-docs/implementation-notes/devcapsule/`, dated 2026-10-04,
for provenance and scope. Choose the clearest useful footage, verify it plays,
review it for sensitive content and select a readable poster. The existing
IDE smokes show editor interaction; do not caption them as a complete Java
development, profiling or debugging demonstration. Identify the recorded
source/version, including development-build status where applicable, rather
than relabeling historical footage as the current release.

Prefer a roughly 20–30-second excerpt when the source supports it, with the
fuller recording available on expansion or through a labeled link. Keep the
useful action and its result visible. Disclosed cuts or time compression may
shorten idle model waits; preserve the original as evidence. Duration is a
guide, not a reason to discard useful footage.

Make IDE text legible at the displayed size through suitable source framing,
deliberate crops or zoom, and expansion. Remove the decorative tilt from the
real recording frame. Retain enough context to identify the capsule desktop;
do not shrink a whole high-resolution desktop into unreadable moving text.

### Stretch goal: a new Eclipse/Java “WOW factor” WebM

Make a bounded attempt to capture a richer scenario through the existing
Playwright/noVNC approach. The outer automation observes screenshots and
operates the desktop through mouse and keyboard. A coding agent inside the
capsule implements the project. Keep those two roles clear in the narrative.

The preferred story is a new Java project in Eclipse implementing a One
Billion Row Challenge-style aggregation demo:

1. Create or import the new Java project through the real Eclipse workflow.
2. Ask a selected coding agent to implement the aggregation and meaningful
   tests, and show its actual work and test execution.
3. Run tests with coverage and show a summary and highlighted source in Eclipse.
4. Set a breakpoint, launch under the debugger, observe suspension, inspect
   meaningful local variables, and step through the code.
5. Profile a representative workload using a verified Eclipse-compatible
   profiler or integration, inspect measured hotspots, and explain a finding.
   If the evidence supports a useful optimization, have the agent implement
   it, verify correctness again and compare equivalent performance runs.
6. If practical, stop and reopen the capsule to show saved work and selected
   settings/tools persisting. This is not process snapshot restoration.

First verify the uncertain prerequisites with a minimal Java program: the
JDK/project, agent authentication, coverage tools, breakpoint suspension and
a profiler that produces usable data. Do not assume the Eclipse package
includes every plugin. Then build stage-specific objectives, checkpoints,
action budgets and success checks. Merely increasing the marker-edit smoke's
action budget does not turn it into this complex scenario.

Use small deterministic inputs for correctness/debugging and a larger input
for profiling. An actual billion-row run is optional; claim it only when it
has completed and been checked. Label input sizes and time compression. Do
not compare performance timings gathered under debugger or coverage
instrumentation. Retain expected aggregation output, test results, coverage
data and a real profile artifact, alongside GUI evidence of the debugger's
suspended location and variables. A model's “done” verdict is insufficient.
Distinguish a successful demonstration from a reliable unattended E2E test.

Time-box the feasibility pass and record the chosen budget in the workstream
before starting. If a stage remains blocked after focused diagnosis, retain
the findings and use baseline footage. This stretch goal must not delay the
landing-page delivery. Report achieved stages, blockers and the smallest
useful next step. A partial advanced scenario can provide a useful excerpt
when captioned accurately. Aim for a 60–90-second edited showcase if the
full scenario succeeds, with a shorter hero excerpt and retained raw evidence.

### Playback, accessibility and provenance for either route

Use browser-compatible playback, a WebM asset and an appropriate fallback as
needed. Keep media self-hosted through the established site asset path, with
no third-party tracking embed. Inspect current asset handling: the original
movie publication used download links, so actual embedding may need consumer
work. Provide controls, avoid autoplay with sound, respect reduced-motion
preferences, reserve media dimensions, use a compressed recording and defer
loading full media until needed. Supply a transcript or adjacent step summary
that makes the demonstration understandable without audio.

No fabricated UI, simulated results, hidden grants or unreleased feature
presented as shipped. Identify the demonstrated IDE, agent and release/source
revision; one combination does not establish universal validation. Prefer a
supported published release for new capture; identify any necessary development
build and why it was used. A video demonstrates the experience, not the
security boundary itself.

Keep reused and new footage clean: no visible tokens, session URLs,
credentials, account identifiers or unrelated personal files. Preserve source
provenance, editing notes and any new recording recipe in workstream evidence.
Follow repository asset/size conventions; avoid committing large raw captures
by default.

Baseline completion requires a playable real recording in the right-hand hero
space. Stretch failure does not block completion when the baseline and other
deliverables are met. If even existing footage cannot be embedded, report
baseline delivery as partial. Do not expose a dead action or treat a storyboard
as a completed recording.

## Deliverable 3: three reasons to switch, explained concretely

Done means: the next substantive section reinforces three outcomes, in this
order, using concise copy and links to the appropriate current documentation:

| Message | Explanation the visitor should get |
| --- | --- |
| Give agents room to work | Agents can perform routine development steps without repeated approvals, inside the boundary the developer grants. |
| Inspect and debug in the same environment | The IDE, agent, SDKs, dependencies and terminals share the workspace, so human investigation continues where agent execution happened. |
| Come back ready to continue | IDE settings, personal tools and recorded project context survive between sessions, within the documented persistence model. |

Reuse and reorganize the existing benefits rather than expanding into a
feature inventory. Three cards fit the current benefits contract. A fourth
is permitted only if it materially improves clarity without duplicating
the continuity example below. Agent and IDE names are supporting specifics;
the visitor's outcome leads each explanation.

Align `/why/` with this hierarchy and use it for the deeper account of
configuration ownership, persistent extras and engineering practice. Keep the
comparison link available there. Completing the argument on the home page
must not require reading a competitive matrix.

## Deliverable 4: make engineering continuity tangible

Done means: a compact, clearly labeled example demonstrates how a person or
another agent resumes with useful context. Place it after the three benefits,
or combine it with the demonstration if that communicates it more clearly.

Use a short real handoff from a suitable project, edited
for readability, with four recognizable facts: what changed, what was
checked and its result, what remains uncertain, and the next action.
Show how the next session uses the recorded handoff. Do not introduce an
abstract dashboard or ask visitors to learn workstream and coordination
terminology to understand the example.

An illustrative example is acceptable if plainly labeled as illustrative;
never present invented history as a user story. Avoid suggesting that
memory files automatically enforce agent compliance or guarantee perfect
recall. The benefit is useful, versioned context that people and agents can
read and maintain.

Keep the existing dogfood evidence visible: DevCapsule is used to build
itself. Present that as evidence of actual use. Do not invent user counts,
testimonials or independent adoption.

## Content accuracy rules

- Validate present-tense product claims against the published release selected
  for the page. Read the current release information on
  pickup; do not assume `main`, the source version and the current release
  are identical. Label historical or development-only demonstration footage
  explicitly; existing development footage is an authorized baseline asset,
  not evidence that its features ship in the current release.
- Explain the default boundary and link to its details. Do not promise
  immunity to malicious code, universal secret protection or impossible
  host access after additional grants. Credentials stored inside the capsule
  remain a separate exposure; this order does not solve it.
- Describe local execution accurately. Cloud-backed agents may send code
  and context to their providers; do not equate a local workspace with
  offline inference or a promise that source never leaves the machine.
- Git does not protect uncommitted work or every item of persistent state.
  Avoid blanket “nothing can be lost” or “Git protects everything” copy.
- Persistence means saved files and documented state survive. Do not imply
  running processes or a debug session resume as a machine snapshot.
- Keep supported platforms and pre-V1 limitations easy to find. A concise
  statement and a details link are sufficient; the opening should explain
  value before launching into internal process and contribution instructions.
- Use approachable, concrete language. Avoid unsupported absolutes such as
  zero setup, perfect reproducibility, complete safety or superiority over
  every alternative. Retain the project's direct, human voice.

## Acceptance evidence

The completion record must identify producer and consumer revisions, the
release used for capture, and a reproducible preview/build invocation. Follow
the current repositories' instructions rather than copying stale commands.

1. **Content and contract.** Run the applicable existing content-contract
   checks and website checks for the changed paths. The current consumer
   exposes `npm run check:content`; the producer has a `docs-contract` Nox
   session. Confirm their current semantics and invocation before interpreting
   the result. Add focused coverage only for new parser/rendering behavior,
   such as a new demonstration marker or a missing required asset. Do not
   introduce brittle tests that merely pin the proposed headline's wording.
2. **Actual rendered experience.** Build and open the integrated site, not
   just the Markdown. Inspect at representative laptop and phone widths
   (for example 1366×768 and 390×844), in the supported color schemes. Verify
   readable hierarchy, no horizontal overflow, keyboard access, visible focus,
   video controls, poster, text alternative and sensible media loading.
3. **Navigation and metadata.** Exercise both hero actions, current-release
   documentation, Windows notes, containment details, `/why/`, comparison,
   journal and contribution routes. Inspect generated metadata. Confirm
   released documentation and its version navigation remain intact.
4. **Demonstrated behavior.** For reused footage, retain source/validation-record
   provenance, review the selected scenes and state their scope. A fresh runtime
   replay is not required solely to reuse a movie. For a new scenario, record
   checks and artifacts for each claimed stage, including any IDE investigation
   or persistence observed. Website test success is not evidence that the
   product workflow ran successfully.
5. **Clarity review.** Ask the reviewer in the existing review process to
   answer, from the first screen: who is this for, what useful change does it
   enable, what is running where, and how do I try it? From the next section,
   the same reader should explain why the shared IDE/agent environment matters.
   Record this as qualitative review. If no fresh reader is available, provide
   an explicit editorial self-review and retain the untested reader response
   as a limitation; do not fabricate a ten-second usability result.

Retain representative screenshots, the demonstration asset, and concise
findings in the existing evidence location. Distinguish automated checks,
manual observations and untested claims. Report every omitted or blocked
acceptance item explicitly.

## Decisions left to the executor

Final copy within the stated message; typography, spacing and responsive
layout; the responsive treatment of the right-hand recording; recording tools, editing and
encoding; the demonstration project and supported IDE/agent pair; the
minimal asset/contract extension; whether the continuity example is a small
page section or part of the demo. Resolve these using the current project
conventions without requesting approval for ordinary reversible choices.

Changing the product's security model, supported platforms, runtime scope,
ownership contract or release policy exceeds this order. Route a necessary
change through the existing workflow. This is not a request to reopen those
decisions as part of a copy edit.

## Execution and completion

Work in reviewable slices: first the message and hierarchy, then the real
recording in the right-hand space and continuity example, then integrated
verification. Attempt the advanced recording as a bounded stretch goal after
securing the baseline; its failure must not hold the page improvement. A useful
copy-only slice may integrate earlier if the project permits it, with no
unavailable demo action and an honest record of the remaining work.

Coordinate producer content and consumer rendering as one deliverable.
Publish the required consumer commit before advancing the producer's
submodule pointer; validate the exact combined pair. Preserve the current
content/publication contract and use the project's established preview,
review and publication process. This work order introduces no additional
approval gate and grants no independent production-publication authority.

Finish with a short handoff: what changed, why the new opening communicates
the value more directly, exact revisions and preview location, evidence,
remaining limitations, and any publication action still pending. The order
is complete when the integrated implementation and all four deliverables
are reviewable with their acceptance evidence; report public deployment
separately if it has not occurred.

## Sources and entry points

These were read while preparing the order. Recheck current revisions on pickup.

- [Live home page](https://devcapsule.mycodespace.ai/)
  and [Why DevCapsule?](https://devcapsule.mycodespace.ai/why/).
- [Producer README](https://github.com/ccozianu/devcapsule/blob/main/README.md):
  authoritative authored landing content and `website:*` markers.
- [Competitive comparison, 2026-10-18](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/blog/2026-10-18-where-devcapsule-sits.md):
  positioning and acknowledged limitations; competitor claims are not fresh
  benchmark evidence for this task.
- [The boundary](https://github.com/ccozianu/devcapsule/blob/main/docs/containment/the-boundary.md)
  and [project capabilities and personal choices](https://github.com/ccozianu/devcapsule/blob/main/docs/configuration/capabilities.md):
  current-tree explanations; verify applicability to the released demonstration.
- [Authoritative consumer contract](https://github.com/ccozianu/devcapsule-website/blob/main/CONTRACT.md),
  especially sections 2, 3.6, 3.7, 5.7 and 7; and the
  [producer contract record](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/specifications/product/content-website-contract.md).
- [Example work order: capsule web console](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/work-orders/2026-10-09-capsule-webconsole.md):
  the requested model for outcomes, deliverables and execution discretion.

Preparation was a document and page review, not a fresh product execution,
website implementation, or usability study. No repository file, workstream
assignment, deployment or release state was changed by preparing this order.
