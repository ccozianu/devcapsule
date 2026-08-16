---
date: 2026-08-16
capture-mode: detailed
requested-by: user
scope: Stage 6 inspector hardening, the first sample project, container-aware launching, and the workflow bootstrap
session-span: 2026-08-13 to 2026-08-16
related:
  - CURRENT-STATUS.md
  - WORKFLOW.md
  - engineering-docs/wip/2026-08-06-recursive-e2e/CURRENT-STATUS.md
  - engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md
  - engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md
  - engineering-docs/wip/2026-08-09-project-management/2026-08-15-portfolio-checkpoint.md
  - engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md
  - engineering-docs/bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md
  - engineering-docs/implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md
  - engineering-docs/implementation-notes/devcapsule/2026-08-06-recursive-dogfood-e2e-milestone-plan.md
---

# Session Record: Inspector Hardening, Sample Projects, And The Workflow Bootstrap

This is a detailed, sanitized, agent-authored reconstruction. It is not a
verbatim transcript. Host filesystem paths are redacted as
`<redacted-host-path>` following the product's own convention; stable artifact
identities such as image digests, container IDs, and commit revisions are
retained because resuming the work depends on them.

The session spanned four calendar days and three workstreams. It began inside
the `recursive-e2e` workstream, opened and delivered the first `sample-projects`
work, and ended in `project-management` publishing workflow changes.

## Why This Session Mattered

Three things changed that the repository will feel for a while.

First, the Stage 6 independent inspector went from a claim to a proof. It had
been comparing four fields; it now compares a complete expected plan, and that
was demonstrated against a real launched container rather than only in tests.

Second, DevCapsule gained its first sample project and, through building it,
two product capabilities it turned out to need: a redistributable
`postgresql-client` component and container-aware launching.

Third, and least expected, the session exposed that DevCapsule's workflow
protocol governs Git state well and external state not at all. That produced a
portfolio checkpoint, a bug, and the first workflow changes written to break a
bootstrap deadlock.

## Chronology And Decisions

### 1. Stage 6 Inspector Hardening

The session opened with the user asking what the current workstream and task
were, then asking what "harden the inspector" actually meant.

The honest answer was that `_validate_inspection` asserted only four things:
container name, image ID, the four `devcapsule.e2e.*` ownership labels, and
that the container was running. The milestone plan's Automated Inspection
Contract demanded far more. Notably, the code could not detect an **extra**
bind mount at all, which is a security-relevant blind spot rather than a
completeness gap.

The user said "have a go at it."

Design chosen: derive an `ExpectedSuccessorPlan` from exactly the translated
`docker run` arguments a launch issues, retain it beside the run manifest as
mode-0600 `expected-plan.json`, and bind it to the manifest by SHA-256 so a
later independent inspection cannot be silently relaxed.

Decisions worth preserving:

- **Mount comparison is set equality, not subset.** An unplanned mount is a
  hard failure. This was the check that was entirely missing.
- **Redaction is structural.** Only the owner-private plan holds daemon-side
  sources; evidence and every error message name destinations only.
- **The parser fails closed** on any unmodelled Docker flag, with a
  launcher-coupled test pinning the model to `build_docker_args`, so a new
  launcher flag cannot silently escape comparison.

Before trusting the comparator, its field assumptions were validated against
real `docker inspect` output from the running development container: `.Mounts`
carries only `bind` entries, tmpfs appears only under `HostConfig.Tmpfs`,
absent capability lists are `null`, and materialized image labels are inherited
into `Config.Labels`.

### 2. A Correction The User Should Know About

While updating the `recursive-e2e` handoff, direct inspection contradicted a
recorded risk. The handoff claimed the successor launch lacked
`DEVCAPSULE_RECURSIVE_E2E=1`. It did not: both the retained successor and the
development container carried the marker. The stale claim belonged to the
retired v024-derived control container.

The handoff was corrected rather than left to mislead a future reader into
planning a relaunch around a defect that did not exist.

### 3. Live Stage 6 Proof

The user asked what the tight path to closing Stage 6 was, proposing a package
rebuild, a new base image, and a development-environment relaunch.

The answer, verified in code rather than asserted, was that all three were
unnecessary:

- The inspector runs on the launching side; the successor image needs no new
  code.
- `devcapsule.pex.sha256` and `devcapsule.source.revision` are **base image**
  labels, so a new base matters only for Stage 8 recursion.
- The formation descriptor excludes the devcapsule source revision, so a launch
  from new code **strictly reuses** the canonical environment image.
- Preflight scores a running-source/image-revision mismatch as a *warning*,
  explicitly allowed for bootstrap, so no relaunch was needed.

What was actually required was a commit, because the local-clone protocol
asserts a clean tree.

The live run then proved the hardened inspector against real infrastructure.
All eleven daemon-side checks passed, and the independent inspection added
`runtime_plan`, proving the in-container SHA-256 of the runtime plan matched
the launch record and that its mount was read-only.

### 4. The Sample Projects Workstream

The user opened a new workstream for sample demo projects carried as
submodules, with the standing rule that a missing DevCapsule feature should
pause the work in favour of `project-management`.

Two decisions were taken by the user during setup: the mnemonic
`sample-projects`, and adding the sample as a real submodule rather than
gitignoring it. A typo in the remote name was corrected mid-turn
(`devcapsule-sample-fastapi-webbapp`, with a doubled `b`, is the real name).

Building the sample surfaced three gaps, all ruled on by the product owner:

1. **No service dependency model** — deliberately **out of scope for V1**. It
   would expand implementation, verification, and testing considerably for a
   problem a sample can state in prose. Backlogged instead.
2. **No port declaration** — same ruling. Host networking is an accepted V1
   simplifying assumption, stated as such in the sample's declaration, with
   tighter alternatives documented.
3. **No `psql` in the base** — **resolved**. Because PostgreSQL is
   redistributable under a permissive licence, the client was added as a
   component delivered by the pinned base rather than acquired per developer.
   This is the deliberate contrast with Claude Code.

Adding samples under `devcapsule-src/tests/resources/` also broke the gate:
pytest collected the sample's tests and mypy type-checked its sources against
dependencies the gate does not install. Both tools now skip `sample_projects`.
Sample projects are fixtures for DevCapsule, not part of its gate.

### 5. Adopter-Path Verification And Container-Aware Launching

Verifying the sample from an adopter's starting point exposed the session's
most consequential defect.

Ordinary `devcapsule project run` performed no host-path translation: it
assumed it ran on the host. Issued from inside a DevCapsule container it would
hand the host daemon a bind source that does not exist there, and **Docker
creates missing bind sources as empty directories**. The IDE would open an
empty project rather than fail.

The user directed that the utility become aware of running inside a container
and either translate paths or fail loudly.

The implementation detects two signals rather than guessing: `/.dockerenv`, and
whether the Docker socket is a **mount point** in `/proc/self/mountinfo`. That
second signal is the discriminator that matters, because docker-in-docker
creates its socket as an ordinary file and correctly needs no translation.

Attempting the launch then found two further host-only assumptions that reading
the code had not revealed:

- the host socket defaulted to `/var/run/docker.sock` even when `DOCKER_HOST`
  already named the socket in use; and
- transient launch files were staged on a container-local tmpfs the external
  daemon cannot read, so those binds would have arrived **empty** — the same
  silent-corruption class as the original defect. This one was found *by the
  loud failure added minutes earlier*, which named the exact unbacked path.

The change also revealed that four existing CLI tests were silently
environment-dependent, passing on a laptop and taking a different path inside a
container. The suite now defaults to host behaviour, and tests opt in to
translation explicitly.

### 6. Workflow Findings And The Bootstrap Deadlock

The user asked directly whether the rebase-and-reset manoeuvres had followed the
documentation, or had been improvised.

The honest answer was that they were a **deviation**. `WORKFLOW.md` says to stop
and ask when refs diverge; instead the divergence was verified with `git cherry`
and resolved by resetting. It was safe and reported, but not what the document
said.

The important conclusion was not that the improvisation was clever. It was that
it was **unauditable**: the user had no way to check in real time that
verification preceded the reset. Documented procedures make agent behaviour
inspectable, not merely repeatable.

The user then observed that all work so far had been sequential task-switching
in one repository and environment, and that genuine concurrency would need
documented, actionable procedures. That produced the portfolio checkpoint.

Two user decisions closed the session:

- **File editing is not exclusive to any workstream**, except where a documented
  locking protocol exists and is used. The handoff carve-out was explicitly
  kept.
- **Publish the minimal workflow improvements from `project-management`**,
  because `workflow-improvements` cannot start cleanly without the very
  procedures it was meant to write.

## Implementation And Documentation Changes

| Area | Change |
|---|---|
| Stage 6 inspector | `recursive_successor_plan.py`, expected-plan retention, digest binding, runtime-plan digest probe |
| Components | `postgresql_client.py`, delivered by the base under `delivery-policy = "base-image"` |
| Base recipe | Version 5 adds `postgresql-client` and its licence label |
| Launcher | `host_daemon.py`; container detection, path translation, loud failure, socket discovery, host-backed staging |
| Gate | `sample_projects` excluded from pytest and mypy; suite made environment-independent |
| Sample | First sample project, published as its own repository and added as a submodule |
| Workflow | Verifying Shared Branch State; rule 11 rewritten as non-exclusive editing with a handoff carve-out |
| Records | Portfolio checkpoint, coordination backlog, cleanup bug, two V1 backlog items |

## Validation And External-State Evidence

- Final gate: `258 passed`, `8 deselected`; mypy clean over 92 source files;
  five packaging integrations.
- Stage 6 live proof, run `482c34f24fc5c438da7b24ff172a619b`: eleven daemon-side
  checks plus `runtime_plan`, then a repeat inspection after a 90-second window
  returning identical identity with `RestartCount=0`.
- Base `ubuntu-24.04-v026` published, registry digest
  `sha256:a9f00250515b757d8e9d8ad832d9cab09a9a6e000f630651704e8538a4702998`.
  Verified by strict pull-by-digest after removing the local tag: `psql
  (PostgreSQL) 16.14`, recipe version 5, exact PEX and source lineage, and
  Claude Code correctly absent from the public base.
- Sample verified end to end: backend `4 passed`, full CRUD against real
  PostgreSQL 17 over `psycopg`, frontend production build, and the
  `postgresql-client` component confirmed present in the materialized
  environment.
- Adopter launch succeeded from inside a container. The project mount resolved
  to the correct host path and the launched container saw real project files
  rather than an empty directory.
- Foreground cleanup confirmed: the sample's container was removed when its
  client exited, in direct contrast to the two detached containers that
  survive. That contrast is the evidence in the cleanup bug.

## Rejected Or Deferred Alternatives

- **A service dependency model.** Rejected for V1 by the product owner as too
  expensive for the benefit; samples state their database needs in prose.
- **Rebuilding the base and relaunching the environment to close Stage 6.**
  Proposed by the user, shown unnecessary in code, and not done.
- **Burning a new base version for recipe 5.** The unpublished `v026` tag was
  reused rather than advancing to `v027`.
- **A worktree procedure and external-resource ownership.** Identified as
  needed, deliberately excluded from the minimal workflow set because both
  require design and one requires code.
- **Assuming a locking protocol must be built.** The backlog explicitly records
  that concluding it is unnecessary is a valid outcome.

## Unresolved Questions And Next Work

- `recursive-e2e` remains paused with **two commits genuinely not on `main`**,
  including the Stage 6 inspector. Its Stage 6 failure-path coverage — early
  successor exit, staging lifetime, cleanup refusal — is outstanding.
- The `sample-projects` registered goal still describes samples only, although
  the workstream now owns core-launcher work by explicit decision.
- The file locking protocol has no release target; V1 or V2 undecided.
- Items 3 and 4 of the workflow handoff remain for `workflow-improvements`,
  which still has no branch.
- `Git Hygiene` item 4 still asserts that pushing may be blocked by missing
  credentials. That assumption was stale for two sessions in this environment
  and was left unchanged as out of the agreed minimal scope.

## Corrections Made During The Session

Recorded because each was a stale fact that had already influenced decisions:

- The claim that the successor launch lacked the recursive-E2E marker was
  false.
- The claim that this environment has no Git publication credentials was false,
  and had caused work to be withheld twice.
- A suggestion that `scripts/build-pex.sh` returned a wrong exit code was
  itself wrong; the misreading came from a shell pipeline reporting `tail`'s
  status.
