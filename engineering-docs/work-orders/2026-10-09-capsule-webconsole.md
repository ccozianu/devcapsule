# Work order: the capsule web console

Issued 2026-10-09 by `project-management` at the product owner's direction, for
the `capsule-webconsole` workstream, registered the same day. Human language
governs this document. Where a slice needs a precise check, derive it from the
text and the embedded blocks when you reach that slice.

## Outcome

A developer who runs `devcapsule project run`, with a graphical desktop or
over SSH, opens one URL and sees their development environment as a web page:
what the `devcapsule` commands report about the capsule and its project, live
process and resource data from inside the capsule, the project's records
rendered from markdown, the workflow state, and, when a decision is pending,
a page that presents the decision and collects the answer. The text commands
remain and keep working. The console adds the picture.

## Decisions already taken, binding

1. The console is in the base image for every adopter. It is not a component
   and not a capability. It starts whenever the runtime runs, with or without
   a display. A headless user reaches it with an SSH port forward.
2. It is a separate process from the runtime, not part of the runtime PEX: a
   static web structure plus a FastAPI application for dynamic data. It
   reads the mounted project and the runtime's read-only records, and calls
   the runtime CLI's `--json` outputs as its API. It imports none of the
   runtime's internals.
3. It is reached like the contained display: one host loopback port, one
   per-run token on every request, bound inside the capsule only. Paths
   resolve inside the project mount and the mounted records. It changes
   nothing on the host, in configuration or in records, except where a
   decision page collects an answer; see deliverable 5.
4. No existing open-source console is the framework. Glances or a similar
   monitor may be linked later as an optional component. The configuration,
   records and workflow pages are ours.
5. Markdown is rendered client-side with `markdown-it`, the website's
   renderer, vendored into the static tree, and diagrams with a vendored
   Graphviz build for the browser. No build step and no Node in the capsule.

Requirement: `R-CONSOLE-001`, proposed. Accept it in your first integration
or say why its statement is wrong.

## Deliverable 1: the console runs and is reached

Done means: in a fresh capsule, with and without a display, `project run`
prints a console URL, the console answers on it, a request without the token
is refused, and a path outside the mount is refused.

- Runtime: a plan field for the console; a supervised child beside
  websockify or alone in a headless capsule; host loopback port and token
  wiring mirroring `display_client.py` and `container_runtime/display.py`;
  the URL printed and opened when a browser exists.
- Base recipe 10: the console's dependencies in a hash-pinned venv built at
  image build, like Playwright's, and the console wheel installed from the
  verified public revision the runtime PEX is built from. A local base build
  proves it. Prefer the venv over Ubuntu's `python3-fastapi`, which is old.
- Development: the checkout's `devcapsule-webconsole/` source mounted over
  the image's copy under the recorded self-hosting exception, so an edit
  shows on the next run without a release.

## Deliverable 2: what the commands report, as pages

Done means: the configuration, versions and project information pages show
the same facts as `config list`, `versions show` and `project info`, read
from the runtime CLI's `--json` output, and a change made with a command
appears on the page after reload.

- Add `--json` to `config list` and `versions show`; `project info --json`
  and `version --json` exist. Declare the JSON shape stable when the page
  depends on it, and say so in the command's help.
- One home page that links every page and shows the capsule's identity:
  project, checkout, version set, base.

## Deliverable 3: live processes and resources

Done means: a page lists the capsule's processes with CPU and memory, and
shows the capsule's CPU and memory use against its cgroup limit, refreshed
without reload.

- `psutil` for processes; `/sys/fs/cgroup` for the capsule's limits and use.
- The API is `GET` only. No signal, kill, or restart from the console.

## Deliverable 4: the records and the workflow state

Done means: any markdown file in the project renders, `index.md` is the
navigation, the root `CURRENT-STATUS.md` and the open workstreams' status
files render with their links working, and fenced `dot` blocks render as
Graphviz diagrams.

- Relative links between markdown files resolve inside the console.
- DOT rendered client-side with a vendored Graphviz build for the browser,
  such as `viz.js` or `d3-graphviz`, like `markdown-it`. No other diagram
  notation; owner decision of 2026-10-09, `WORKFLOW.md` topic 9.6 rule 6.
- Read only, from the mounted branch; no fetch of the coordination branch in
  this deliverable.

## Deliverable 5: decision pages

Done means: an agent inside the capsule can hand the human a decision with
several options as a page in the console; the human reads the records cited
beside each option, chooses, and the choice is written where the agent reads
it back; the agent records the decision in the normal files; the page is
discardable and never a record itself.

This deliverable implements the workflow's rule that a decision with more
than a handful of options is presented as a structured artifact, from the
owner's reading of Karpathy's 2026-10-02 post. Decisions taken for it:

- The console is the baseline host for such pages, which makes them portable
  to every agent and every environment, headless included.
- Pages both present and collect. A collected answer lands in one place the
  agent reads, under the capsule's writable state, never in configuration or
  records; the agent records the decision in the status file or decision
  record and then discards the page.
- The threshold is judgment, with three examples that are the first uses:
  an intake disposition pass over many items, the legacy launch capabilities
  L1 to L13, and a release scope with many candidates.

Design the page contract with the first use in front of you: the
project-management intake pass. Keep the contract small enough that a
different agent can produce a page from a markdown table.

## Acceptance evidence

- Unit tests for routing, token refusal, path traversal refusal, and the
  JSON readers.
- A smoke that starts the console in a fresh capsule, with and without a
  display, fetches the home page and the configuration page, and checks that
  a tokenless request is refused.
- The IDE smoke rows gain "console answers".
- The owner opens the console from `project run` on the desktop and from an
  SSH port forward, and says it shows the environment.

## Decisions left to you

The port allocation detail; the static tree's layout and styling; the exact
JSON shapes; the page contract for deliverable 5; the order of deliverables
3 and 4; which commands beyond the two named gain `--json`.

## Decisions left to the owner, stopping points

- Whether `R-CONSOLE-001` is accepted as written.
- Any write operation beyond deliverable 5's answer file.
- The base-release cadence: when a console change is published to adopters,
  given that it needs a base image rebuild. Propose a trigger for the release
  policy when deliverable 1 lands.
- Anything that would widen the console's reach beyond the loopback port and
  the run token.

## Mainline evidence read before writing

`display_client.py` and `container_runtime/display.py` for the port and
token model; `container_runtime/entrypoint.py` and `supervisor.py` for
children; `components/playwright.py` for a venv delivered by pinned
artifacts; `images/base.py` for recipe version 9, the apt list and the
embedded verified PEX; `runtime_configuration.py` for the read-only records
view; `commands/project.py` and `commands/version.py` for the existing
`--json` flags; the website's `package.json` for `markdown-it`.

## Execution

Work in slices of one deliverable or less. Record each in the status file.
Integrate deliverables 1 and 2 together as the first pull request if they are
ready together; otherwise deliverable 1 alone is a valid first integration.
Stop at the stopping points above and ask. The author is `project-management`;
raise disagreement with the owner rather than forwarding this item.
