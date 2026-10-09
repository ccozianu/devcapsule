# Workstream Current Status: Capsule Web Console

Mnemonic: `capsule-webconsole`

Start date: 2026-10-09

State: active; PR1 (#184) and PR2 (#186) await the owner with their reviews merged; PR3, the runtime and base integration, is implemented on `ws-capsule-webconsole/runtime-base`, proven on a local base recipe 10 build, and ready for its pull request

Definition read: WORKFLOW.md@9593256c1f36, WORKFLOW-LOCAL.md@7362bae8ec82

Branch association: `ws-capsule-webconsole/first-slice` (PR1, #184); `ws-capsule-webconsole/console-app` (PR2, stacked on PR1); `ws-capsule-webconsole/runtime-base` (PR3, stacked on PR2)

Integration target: `main`

Delivery method: pull request, merge commit

Requirements: `R-CONSOLE-001`

Work order: [the capsule web console](../../work-orders/2026-10-09-capsule-webconsole.md), issued 2026-10-09 by `project-management`; its DOT and materialized-views amendments are in intake, and the amended text is on `project-management`'s branch until its next integration

## Goal And Scope

Every capsule serves a web console on a token-gated loopback port, whenever
the runtime runs, with or without a display. The console shows what the
`devcapsule` commands report, as HTML: the configuration, the versions, the
project information, and live process and resource data from inside the
capsule. Later slices render the repository's records and workflow state and
host the decision pages the workflow's human-input rules allow.

Owner decisions of 2026-10-09 that shape the work:

1. The console lives in the base image for every adopter. It is not a
   component and not a selectable capability. A headless user reaches it
   with an SSH port forward.
2. Architecture: a static web structure plus a FastAPI application for
   dynamic data. The console is a separate process, not part of the runtime
   PEX. It reads the mounted project and calls the runtime CLI's `--json`
   outputs as its API.
3. No existing open-source console is adopted as the framework. Glances or a
   similar tool may become an optional component later, linked from the
   console, but the configuration, records and workflow pages are ours and
   no product renders them.

## Current State

**2026-10-09, slice 3: the console runs and is reached.** The runtime plan
gained a `console` section, like the display's: a listen address, a port
and the token path, plus an optional `source_path` for the self-hosting
exception. The launcher allocates a host loopback port and a per-run token
whenever a runtime plan is launched, with or without a display, mounts the
token read-only, publishes the port off host networking, prints the console
URL, and watches readiness. The entrypoint starts the console as a supervised
child beside the display's children, or alone in a headless job. Base recipe
10 installs the console under `/opt/devcapsule-webconsole`: a venv built at
image build from the subproject's hash-pinned files, the package itself from
the same public revision as the runtime, fetched with git so the commit hash
verifies the content. The smoke of deliverable 1 is an end-to-end test with
and without a display, and the IDE smoke rows gained "console answers". A
user page documents the console link, the token and the SSH forward.

Judgments recorded for slice 3:

- One page opens by itself. With a contained display the desktop opens and
  the console is announced as ready, not opened; two tabs for one run would
  be noise. Without a desktop the console opens, so a headless or
  passthrough run still lands the developer on one page. The owner can
  flip this.
- The console runs whenever a runtime plan is launched. There is no option
  to turn it off, because the work order makes it part of every capsule;
  an older base without the console is announced and skipped, not refused,
  since the runtime is launcher-supplied and runs on any base with the
  display label.
- The self-hosting exception is mechanical: when the launched project
  carries `devcapsule-webconsole/devcapsule_webconsole/`, the console child
  runs that source ahead of the image's copy through `PYTHONPATH`, with the
  image's interpreter and dependencies, and says so. No separate mount: the
  project is already mounted. Any other project runs the base's console.
- The base fetches the console's source with `git fetch` by commit, which
  verifies the content against the hash; an archive download would not.
  The build toolchain is hash-pinned too, in `requirements-build.txt`, so
  the venv install fetches nothing unpinned.
- The console's readiness timeout is 60 s, three times the display's:
  FastAPI's import on a cold host is slower than an X server's start.

**2026-10-09, slice 2: the console subproject.** `devcapsule-webconsole/`
is a second distribution: a FastAPI application, a static tree and tests,
with hash-pinned runtime and development requirement sets. It serves the
home, configuration, versions and project pages from the runtime CLI's
`--json` documents, read by running the CLI. Every request carries the run
token or is refused, static files included; the token arrives in the printed
URL and is kept in a cookie. File reads resolve inside the project mount
only. Every route is `GET`. A new nox session, `webconsole`, type-checks and
tests it in its own environment, and the build gate queues that session.
Run by hand against this capsule's real CLI, all four pages render; the
screenshots are under [evidence/2026-10-09-console-pages](evidence/2026-10-09-console-pages/).

**PR #186 is open against PR1's branch. Its review, PR #187 by the Codex
and gpt-6-astra pair, was merged without a round.** Seven findings, all
accepted: a time-of-check race on the project-file route, closed with
descriptor-anchored `O_NOFOLLOW` reads; a malformed cookie header crashing
the gate; a non-object or non-finite JSON document passing through the
reader; token characters an unquoted cookie cannot carry; the nox session
picking the runtime's mypy configuration instead of the console's strict
one; tighter types; and 37 added tests, 89 in all. The gate on the merged
branch is recorded below.

Judgments recorded for slice 2:

- The console does not import the runtime. Its API is a subprocess call
  per document, uncached, so a change made with a command is on the page at
  the next reload, as deliverable 2 asks.
- The token is carried three ways: the query parameter from the printed URL,
  the cookie the console sets in answer to it, and a header for scripts. A
  valid query token sets the cookie `HttpOnly; SameSite=Strict`. Comparison
  is constant-time.
- Path confinement refuses any `..` component, an absolute path, a NUL, and
  a symbolic link that resolves outside the mount. The project-file route is
  the foundation of deliverable 4; in this slice it serves UTF-8 text only.
- The console takes the CLI executable as an explicit argument. The shipped
  PEX has a fixed path, but the command name is `devcapsule0` in a
  self-hosting capsule, so guessing from PATH would be wrong there.
- The subproject has its own environment and nox session, never the
  runtime's: FastAPI's dependency set would otherwise be pinned twice.
- Pages are static HTML with one script that builds the DOM from the
  documents with `textContent` only. No template engine, no build step.
- The identity block on the home page composes `project info` and
  `versions show`; see the open thread on the checkout name.

**2026-10-09, slice 1: the JSON contract.** `config list --json` and
`versions show --json` exist, with schema version 1, on the host and inside a
capsule. The text reports render from the same documents, so the two cannot
disagree. The work order's three mail items are accepted as the goal and
dispositioned. R-CONSOLE-001 is accepted, as the work order asked for the
first integration. The user documentation names the flags. The build gate
ran on this branch before the checkpoint; see *Validation And External State*.

**PR #184 is open against `main`. Its review, PR #185 by the Codex and
gpt-6-astra pair, was merged into the branch after one round.** The review
found one regression #184 had introduced: the next-launch identity was
computed outside the error boundary, so a malformed local selection hid the
running session. It also found a pre-existing confusion of a named checkout
called `devcapsule` with the default checkout, now fixed on both sides of
the mount with a `checkout-name` field in the launch context. The one
round asked for validation of that optional field beside its neighbours;
the pair delivered it with five rejection cases. The pair's gate and this
workstream's gate on the merged branch are recorded below.

Judgments recorded for this slice:

- Inside a capsule, `config list --json` carries the mounted checkout record
  and the launcher command, not the table's rows. The text report does the
  same. The rows are computed against the host: a binding row checks a host
  directory and a secret row checks the launching shell's environment, and
  neither is observable from the capsule. A row computed here would state
  something false about the host. The console's configuration page renders
  the record in a capsule and the rows on a host.
- The JSON shape rule, written beside the schema constants: adding a key
  keeps the version; renaming, removing or retyping one bumps it.
- One help text for every stable `--json` flag, shared from the command
  framework, names the console as the reader.
- `versions show` gained `--json`; `check`, `history` and the rest did not.
  The work order leaves further flags to the page that needs them.

### How the work runs

The owner's instructions of 2026-10-09, given at the switch, are an exception
to the human-input rule for this iteration. The agent implements the work
order's first iteration, deliverables 1 and 2, without stopping for
decisions. Stopping points become written proposals in the pull request.
Two limits stay: no write operation beyond deliverable 5's answer file, and
no reach beyond the loopback port and the run token. The owner merges to
`main`; the agent never does.

The slices are stacked pull requests, each reviewed by a second agent pair
before the next one starts:

```dot
digraph stack {
  rankdir=LR; node [shape=box];
  main -> "PR1 json contract" -> "PR2 console subproject" -> "PR3 runtime and base" [dir=back];
  "PR1 json contract" -> "PR1.1 review" [dir=back, style=dashed];
  "PR2 console subproject" -> "PR2.1 review" [dir=back, style=dashed];
  "PR3 runtime and base" -> "PR3.1 review" [dir=back, style=dashed];
}
```

- PR1, this branch: `--json` on `config list` and `versions show`.
- PR2, on PR1's branch: the `devcapsule-webconsole/` subproject with the
  token gate, path confinement, and the home, configuration, versions and
  project pages.
- PR3, on PR2's branch: the runtime child, port and token wiring, base
  recipe 10, the development mount, the fresh-capsule smoke and the IDE
  smoke column.
- Each PRn.1 is written by the Codex and gpt-6-astra pair from a
  `-review` branch off PRn's branch, aimed at clarity, correctness and test
  coverage of PRn's lines. This workstream reviews it in PR comments and
  merges it into PRn's branch, or pushes back, at most three rounds, then
  waits for the owner. PRn+1 starts only after PRn.1 is settled.

## Planned Next Step

1. Prove PR3 with a local base build and the console smoke, then open it
   against PR2's branch and request PR3.1 from the Codex pair.
2. Done in PR2: the console subproject, runnable on a host against the installed
   CLI, with its unit tests.
3. PR3: deliverable 1's runtime and base work, with the smokes. Propose the
   base-release trigger in that pull request.

Later iterations: deliverables 3 and 4 in the order this workstream chooses,
then 5, then 6.

## Validation And External State

- Slice 1 unit modules: 468 passed with `PYTEST_ADDOPTS` scratch under
  `/opt/devcapsule-gate/pytest`; `/tmp` overflowed at 2 GB first.
- `mypy devcapsule`: no issues in 112 files.
- Build gate `nox -s build` on this branch, 2026-10-09: 1,262 unit cases, 10
  packaged integrations, type check, source and PEX smokes, documentation
  contract; successful.
- Review PR #185 gate, by the Codex pair in its worktree: 1,276 unit cases, 10
  packaged integrations, type check, smokes; documentation contract skipped
  there, the website submodule being absent from a worktree.
- Build gate on the merged branch at `0ec121e`, 2026-10-09: 1,276 unit cases, 10
  packaged integrations, type check, smokes, documentation contract; successful.
- Console session `nox -s webconsole` on PR2's branch: mypy clean on 6
  source files, 52 tests passed.
- Build gate on PR2's branch, 2026-10-09: 1,276 unit cases, 10 packaged
  integrations, type check, smokes, documentation contract, then the console
  session; successful.
- Review PR #187 gate, by the Codex pair in its worktree: runtime unit cases,
  packaged integrations, type check, smokes, then the console session with
  strict mypy and 89 tests; documentation contract skipped there.
- Build gate on the merged PR2 branch at `7013555`, 2026-10-09: 1,276 unit
  cases, 10 packaged integrations, type check, smokes, documentation
  contract, then the console session with strict mypy and 89 tests;
  successful.
- Slice 3 unit modules: 219 passed across the launcher, runtime, display,
  base image and successor plan modules; mypy on the package and tests clean.
- Build gate on PR3's branch, 2026-10-09: 1,299 unit cases, 10 packaged
  integrations, type check, smokes, documentation contract, then the console
  session; successful.
- Base recipe 10 built locally as `devcapsule-base-e2e:webconsole-161638` from the public PEX of
  `7659c6d`, over host networking: the built-base test passed, the venv
  imports the console offline. The console smoke passed with the contained
  display and headless: home and configuration 200, tokenless 403, `..` and
  absolute paths 403, a file inside the mount 200. See
  [evidence/2026-10-09-console-smoke](evidence/2026-10-09-console-smoke/).
- IDE smoke, codium, on the built base: passed, with the new "console
  answers" fact at 200 and the tokenless probe refused.
- Manual run against this capsule's real CLI on loopback port 8765 with a
  fresh token: tokenless request refused, cookie set from the query token,
  traversal refused, four pages rendered and screenshotted with the website's
  Playwright into `evidence/2026-10-09-console-pages/`. The server was
  stopped afterwards.
- No containers or images in use.

## Open Threads

- `project info` reports the checkout name as `default` for a named
  checkout, on the host and in the capsule: it reads a `checkout.name` key
  that no writer puts in the record. `config list --json` names the record
  file and is right. The console's home page shows what `project info`
  reports, so it is wrong there until the command is fixed. Mailed to
  `maintenance` on 2026-10-09 as a defect; the console will follow the fix.
- Base-release cadence, proposal for the owner with PR3: a change under
  `devcapsule-webconsole/` that an adopter should see is a base-release
  trigger, the same as a change to the display stack, because the console
  ships only inside the base. Concretely, add to the release policy: a
  release whose range touches `devcapsule-webconsole/` or
  `images/base.py` publishes a base image, and the console's version in
  `pyproject.toml` is bumped in that range. Development needs no release:
  the self-hosting exception runs the checkout's source.
- Dependencies in the base: Ubuntu's `python3-fastapi` and friends are old;
  a hash-pinned venv at image build is the plan, like Playwright's.
- The work order on `main` lacks deliverable 6; the amended text is on
  `project-management`'s branch. The mail item carries its substance.
- Deliberately not preserved: the exploration of adopting Glances, Netdata,
  Cockpit or a Docker dashboard as the framework; the reasons are summarized
  in decision 3 above.

## Workstream Document Index

- [Intake decisions](intake-dispositions.md) and [intake](intake/README.md) — coordination
