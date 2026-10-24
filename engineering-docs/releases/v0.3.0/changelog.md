# DevCapsule 0.3.0 changelog, since 0.2.15

Maintained by the agent driving the release and updated at every candidate,
from the merged pull requests and the bug records, for adopters: what is
new and what is fixed since 0.2.15. Records, workflow rules and the
project's own housekeeping are left out on purpose. The adopter notes for
the final release, `notes.md`, are written from this file.

Candidate 3, tagged 2026-10-24 at `a22a215`; candidate 2 was tagged
2026-10-22 at `e5b5a8b`, candidate 1 on 2026-10-19 at `7016cdd` and
candidate 0 on 2026-10-18 at `53ebc17`.

## New

- **The web console.** Every capsule serves a small read-only website
  about itself, reached through one link the launcher prints beside the
  desktop link, valid for that run only. Pages for what the inspection
  commands report, configuration, versions, project; the capsule's
  processes and its use of CPU and memory against its limits; the
  project's Markdown records rendered, with `dot` blocks drawn as
  diagrams; decisions an agent hands to you, answered in the browser and
  written where the agent reads them; notifications from the checkout's
  environment, with a bell. Needs base recipe 10 or later; older bases
  print a notice and run without it.
- **Session logs, on by default.** Every launch gets a log directory on
  your computer, named on the `Session logs:` line, with one file per
  component, the launcher's and the supervisor's included, at a WARNING
  baseline. Inside the capsule it is `/var/log/devcapsule`, named by
  `DEVCAPSULE_LOG_DIR`. Files rotate in place with compression, and one
  budget per checkout bounds the whole. They survive the browser tab,
  Ctrl+C, the IDE's exit and the container's removal.
- **Three more IDE surfaces and browser automation.** IntelliJ IDEA
  (`java-ide`), Eclipse IDE for Java Developers (`eclipse-ide`) and
  JetBrains Rider with a pinned .NET SDK (`dotnet-ide`, `dotnet`), each
  accepted with a recorded graphical smoke. Playwright with a
  component-installed Chromium (`browser-automation`) for tests and
  agents inside the capsule.
- **Shared versus personal capabilities, and commands for every
  configuration change.** A project declares required capabilities and
  optional enhancements; a developer keeps personal IDE, agent and tool
  choices and omissions local to the checkout. `project config
  capabilities` replaces either set after validating the candidate, with
  `--preview` to look before writing; `project config need` adds
  capabilities and regenerates the lock; `project config check` validates
  the project contract, or candidate files, without writing or launching.
  `project config list` and `project versions show` answer `--json`.
- **Checkout notifications and decisions from the command line.**
  `project checkout notifications` lists, posts, reads and dismisses what
  the environment tells the developer; `project checkout decisions`
  builds a decision page for the console and `hand-off` prints the text
  for chat, so an agent sees one CLI. The console's origin reaches the
  capsule as `DEVCAPSULE_CONSOLE_URL`.
- **Bases named by what they promise.** A base is identified by its
  family and recipe, `ubuntu-24.04@11`, the contract its consumers rely
  on; the tool that built it is provenance, shown but not identity. The
  `devcapsule images` package carries the contract and a compatibility
  report.
- **Faster image rebuilds.** Directory inputs are named build contexts
  read in place and archives unpack once by digest, so a rebuild of the
  real IDE tree transfers 1.29 MB where it transferred 3.69 GB.
- **In-capsule project commands.** Inside a capsule every `project`
  subcommand finds the capsule's project, and each command declares the
  access it needs; the ones that need launcher-owned state say so and
  name the command to run outside.
- **Agent versions.** Codex 0.163.0, Claude Code 2.1.302 and Antigravity
  CLI 1.4.2, each verified against its vendor's checksum and started on
  the base with DevCapsule's seeded settings. Existing locks keep their
  pins until a checkout chooses to follow the project again.

## Fixed

- Inside a capsule, configuration inspection failed from `/opt` and from
  the mounted project (2026-09-24).
- Inside a capsule, `project <unknown>` was refused as launcher-only
  instead of as unknown (2026-09-26).
- Detached successor containers exited and were never cleaned up; the
  recursive successor is now launched attached, like every capsule
  (2026-08-15), and it launches from a fresh workspace (2026-10-04).
- The unpacked archive cache could lose concurrent work and trust an
  incomplete entry; publication is serialized and completed entries are
  validated (2026-10-08).
- Relaunching IntelliJ mistook a reused container PID for the previous
  IDE and refused on a stale directory lock (2026-10-04).
- Clearing an optional omission lost a local version pin; omitted
  optional pins stay in the persistent selection (2026-10-06).
- An unreleased component in the shared lock prevented released
  launchers from opening the checkout; a compatibility guard now keeps
  the shared configuration readable by the latest release (2026-10-04).
- Website links failed with `xdg-open` when no browser handler was
  available; the host-open bridge is verified and the record closed
  (2026-09-24).

## Documentation

The documentation is versioned and published per release at
[devcapsule.mycodespace.ai](https://devcapsule.mycodespace.ai), 43 pages
in thirteen areas for 0.2.15, with the pages this release adds: the web
console, diagnostics and logs, capabilities, the IDE surfaces, component
upgrades and freshness, and the developer documents on the unit,
integration and end-to-end suites.

## Fixed in candidate 1

- On the published base, `ubuntu-24.04@9`, candidate 0 printed a web
  console link, the capsule then said this base has no web console, and
  three minutes later the launcher reported that the console did not
  answer and suggested opening the link (2026-10-18). The launcher now
  reads the base's labels first; on a base without the console it prints
  what is missing, the one command that builds a base with it and the
  guide, and plans no console at all: no port, no token, no wait. The
  console needs a base of recipe 11 or later; a published one is a gate
  before the final release, and
  [building and selecting a local base](https://devcapsule.mycodespace.ai/docs/current/configuration/local-base/)
  is the way to have it before then.

## Fixed in candidate 2

- **The terminal during a session is quiet, and the session ends with a
  result.** The IDE's and the display stack's own output, with its
  harmless ERROR labels, goes to the session's log files only; the
  terminal carries the launcher's lines, the desktop and console links and
  the ready line, the supervisor's warnings when a component dies, and at
  the end one result line, `Session ended`, `Session failed` or `Session
  interrupted`, followed by the path of every log file of the session on
  your computer (2026-09-15, C10).
- **Ctrl+C ends the session with that result, not a traceback.** The
  launcher waits for the capsule to stop, asks Docker after a minute, and
  on a second Ctrl+C stops waiting and names the container to stop; it
  returns 130 as shells report an interrupted command (2026-09-15, C10).
- **`project run --authorize network host` works on every project.** The
  `network` authorization is a node on every project, with Docker's
  bridge as the default, whether or not the project recommends host
  networking; a recommendation attaches the project's justification
  (2026-10-05).
- The configuration listing attributed an unanswered workstation default
  to the manifest; it names the workstation default now.

## New in candidate 3

- **Saved Docker arguments for each checkout.** `project config
  set-extra-docker-args -- OPTIONS...` saves the extra `docker run` options
  a development scenario needs, GPUs, mounts, environment variables, once
  per checkout on the launcher host; `project run` passes them after its
  own options and before anything given after `run --`, so returning to
  that work is `project run` again. `list-extra-docker-args` shows the list
  with inline environment values masked, `remove-extra-docker-args` clears
  it. `set-env NAME` takes a value from a hidden prompt, out of shell
  history; `list-env` and `unset-env` edit the same list. The list is a
  private file outside Git and outside anything mounted or snapshotted;
  launcher-owned options such as `--network` and `--memory` are refused in
  every spelling. [Project versus personal](https://devcapsule.mycodespace.ai/docs/current/configuration/project-versus-personal/)
  documents it (2026-10-23).
- **Software approvals at launch, once for the whole list.** When the
  project's lock brings new versions of vendor software you approved
  before, from the same vendors under the same terms, `project run` shows
  the list and asks one y/n instead of one question per component; any
  other key stops the launch and names `project config approve`, which
  approves from the command line and inside scripts. The page
  [Software approvals](https://devcapsule.mycodespace.ai/docs/current/configuration/software-approvals/)
  says what an approval by name leaves alone (2026-10-22).

## Not in candidate 3

Planned for later candidates of this cycle: forced configuration, `project config resolve --force` and
`project run --force-config`; the diagnostics snapshot and export command;
the manifest's schema version 2 for the `required`/`optional` vocabulary;
cleanup of obsolete images and cached files; release-notes automation.
Out of 0.3.0: consent and vendor trust, installed-IDE reuse with an empty
launcher cache, browser evidence for diagnostics, the console's
materialized views, ecosystem-aware bootstrap.
