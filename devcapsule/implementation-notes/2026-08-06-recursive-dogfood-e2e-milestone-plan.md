# Milestone Plan: Recursive Dogfood E2E — Build And Launch A Successor From Inside DevCapsule

Status: active milestone; execution plan accepted and Stage 0 implemented

Release target: V1

Milestone branch: `milestone/recursive-dogfood-e2e`

Baseline branch: `main`

Baseline revision:
`237d4939f8d1dcfcfbe2061209f16f8692542c08`
(`Merge branch 'wip/local-pycharm-materialization'`)

Date started: 2026-08-06

Requirements: root `R-PRODUCT-001`, `R-PRODUCT-002`, `R-PRODUCT-004`, and
`R-PRODUCT-005`; DevCapsule `R-STATE-001`, `R-SCOPE-001`, `R-DOCKER-001`,
`R-PYTHON-MVP-001`, `R-PYTHON-MVP-002`, `R-PYTHON-MVP-003`,
`R-IMAGE-BUILD-001`, and `R-FRAMEWORK-001`.

Gap-review sources: engineering gaps E1 through E6 in
`devcapsule/implementation-notes/2026-08-06-v1-gap-review.md`.

## Milestone Outcome

After one bootstrap handoff from v023 to an intermediate v024 dogfood
checkpoint, an agent working inside the updated, authorized DevCapsule
container can execute one explicitly invoked end-to-end scenario that:

1. creates a clean local clone at an exact committed revision without relying
   on the current checkout's virtual environment;
2. bootstraps that clone and runs the repository's full build gate;
3. produces a revision-bearing PEX;
4. uses the PEX to build a new managed DevCapsule base through the host Docker
   daemon;
5. configures the clean clone with isolated developer-owned state;
6. authorizes the exact newly built local base and only the host capabilities
   required by the scenario;
7. resolves and materializes the canonical PyCharm/Codex environment through
   production commands;
8. starts a successor container on the host without blocking the agent in the
   current dogfood container;
9. inspects all machine-visible runtime, security, identity, persistence, and
   lifecycle acceptance criteria; and
10. cleans only resources owned by that E2E run.

The user may perform two narrow manual actions: close/reopen the IDE to hand
dogfood from v023 to the local v024 checkpoint, then confirm the final successor
IDE and close the previous IDE when ready. The agent must perform every build,
configuration, launch, inspection, and cleanup operation from a running
dogfood container.

## Why This Milestone Is Next

The product owner selected recursive dogfood engineering ahead of the proposed
PyCharm functional-closure milestone. This gives future agents a repeatable way
to build, launch, inspect, and validate their own changes from the real dogfood
environment instead of depending on a human to translate every host-level
Docker step.

The milestone does not make engineering-only mechanics part of the ordinary
adopter workflow. Generally useful inspection, safe path handling, and
detached lifecycle behavior may become shared product capabilities; the
recursive orchestrator remains an explicit, expensive validation operation.

## Trusted Starting Point

The committed Linux dogfood lock at the baseline selects:

```text
docker.io/mycodespaceai/devcapsule-base@sha256:e8ec48fa1f45f566e997735ac5e8ce8086a2512681db0e8a22696ee0801a8aa1
```

That published v023 base and its canonical materialized environment embed
source revision:

```text
a33988a24a91ef382c1c5c6265ba2a34762ba115
```

The accepted dogfood runtime already provides:

- an embedded DevCapsule PEX at `/opt/devcapsule/bin/devcapsule.pex`;
- Python 3.12 and the development-tooling baseline;
- the Docker CLI and an explicitly authorized host Docker socket;
- an unprivileged mapped user with validated optional development sudo;
- a writable project checkout and persistent container home;
- X11 plus a working PyCharm/Codex process; and
- an external read-only container runtime plan.

This v023 environment is the trusted bootstrap executor for the initial
implementation slices only. It may run a new source-built PEX from the mounted
checkout, but that alone is not recursive-dogfood acceptance because the
running image still embeds the older v023 PEX.

After recursive preflight, host-daemon translation/staging, and an initial
orchestrator skeleton exist, v023 builds a local v024 base carrying their exact
committed revision. The user then manually relaunches dogfood through the
v024-based canonical environment. Full acceptance runs from inside v024 and
builds the next uniquely identified successor base—expected to be v025 or an
equivalent revision-derived E2E identity—from a clean clone. This establishes
a two-generation proof:

```text
v023 + mounted milestone source -> bootstrap v024
v024 with embedded recursive capability -> clean clone -> next base -> successor
```

The v024 checkpoint is local, developer-authorized, and internal to the
milestone. It is not a release candidate, need not be published, and must not
replace the committed v023 lock. Both v024 and the final E2E successor use the
existing developer-owned exact-local-image authorization path until a later
publication decision.

## Clarification: Clean Clone Versus Existing Checkout

The existing checkout is already build-ready because it has a contributor
virtual environment and has repeatedly passed the Nox gate. The engineering
gap is that a fresh clone does not inherit that environment.

This milestone must automate:

```text
clean clone -> isolated contributor bootstrap -> full Nox gate -> PEX/image
```

It must not solve the gap by copying the current checkout's `.venv`, installing
all contributor dependencies ambiently in the base, or silently depending on
personal caches. A minimal repository-owned contributor bootstrap is permitted
for this milestone. It does not by itself claim completion of the broader
user-facing ecosystem-bootstrap contract in V1 gap F1.

## Execution Surface

The recommended public developer entry point is an explicit Nox session:

```text
cd devcapsule
python -m nox -s recursive_dogfood_e2e
```

This invokes the costly test from inside an already-running development
environment. It is not an alternative launcher. Contributors continue to enter
this project with ordinary `devcapsule project run`; when the selected project
contains `devcapsule/pyproject.toml` with `[project].name = "devcapsule"`, that
normal launch derives recursive readiness from developer-approved host access.
`devcapsule project run --no-recursive-e2e` is a one-launch safe downgrade.
It forces host Docker off, bridge networking, and development sudo off without
rewriting the developer's accepted configuration.

A small standard-library bootstrap entry point may prepare the clean clone's
isolated contributor environment before Nox is available. The Nox session may
delegate orchestration to a repository-owned Python module or script, but the
scenario itself must invoke the built PEX and production DevCapsule commands at
the important CLI/process boundaries.

This costly, host-sensitive session is not part of the default `nox -s build`
gate. It must fail preflight with actionable guidance when it is not running in
an explicitly authorized recursive-dogfood environment.

## Safety Invariants

These invariants apply to every stage:

1. Host Docker access, host networking, development sudo, host filesystem
   paths, display authorization, and credential-bearing state remain separate,
   explicit choices.
2. The orchestrator never mounts an arbitrary host path inferred from project
   text or an unvalidated environment variable.
3. Path translation uses only verified mounts of the current dogfood container
   and the longest matching mounted prefix. Unmapped, read-only, ambiguous, or
   escaping paths fail closed.
4. Test checkout and XDG roots live beneath one writable, persistent mount
   already owned by the current checkout. The recommended location is a
   dedicated E2E workspace beneath the DevCapsule-managed persistent home,
   never inside the active source checkout.
5. A local clone uses the existing checkout as its source with Git's local
   transport and no copied Git, SSH, registry, or agent credentials. Use an
   isolated object store rather than hard links when necessary for deterministic
   cleanup and independence.
6. Mutable PyCharm and Codex credential state is not shared with the successor
   by default. Any later shared profile requires an explicit, separately
   validated choice.
7. The scenario uses unique names and ownership labels derived from a generated
   run ID. Cleanup selects by exact run ownership, never by a broad name prefix
   alone.
8. Temporary runtime plans, account files, sudo policy, Xauthority material,
   and other bind-mounted launch inputs live in a verified host-backed staging
   root, use restrictive modes, are never logged, and are cleaned on success or
   failure.
9. No command deletes the current checkout, personal state, credentials,
   unrelated Docker resources, or shared build cache.
10. The current IDE/container is never stopped automatically. Successor launch
    and old-container closure are distinct operations.
11. Gemini CLI remains unsupported and absent from active plans, images, and
    validation except for a negative inventory guard.

## E2E-Owned Resources

Every run receives a cryptographically random or equivalently collision-safe
run ID. All resources created for the run are recorded in a local manifest
beneath its isolated workspace before mutation continues.

The manifest may include only non-secret ownership and identity data:

- run ID and start time;
- source and baseline revisions;
- test workspace and isolated XDG roots;
- container names and IDs;
- image tags and immutable IDs;
- test-owned Docker volume names, if any;
- runtime artifact paths without file contents; and
- cleanup state.

Images and containers use at least:

```text
devcapsule.e2e.managed=true
devcapsule.e2e.run-id=RUN_ID
devcapsule.e2e.source-revision=REVISION
```

Cleanup verifies these labels and the recorded immutable identity before
removal. A `--keep-on-failure` mode preserves test-owned resources and prints a
sanitized inspection/cleanup command; it never changes the ownership boundary.

## Stage 0: Prove Recursive Preflight And Threat Boundaries

Status: complete on the milestone working tree as of 2026-08-06

Implement a read-only preflight that establishes whether recursive execution
is safe and possible before cloning, building, or launching anything.

It must inspect and report, with sensitive values redacted:

- distribution and exact source revision of the running PEX;
- current checkout revision and cleanliness;
- current container identity validated through the authorized daemon;
- host Docker client/server reachability and selected socket;
- current container bind mounts and their writable/read-only status;
- the persistent-home mount usable as the test workspace root;
- project-mount, runtime-plan, X11 socket, display, and Xauthority readiness;
- free disk space relevant to clone, PEX, base, and materialized-image builds;
  and
- any required authorization or unsupported environment condition.

Raw host paths, Xauthority contents, environment secret values, and credential
state must not appear in ordinary logs. An explicit local debug view may show
approved host path mappings after warning that host Docker authorization already
grants broad host control.

Done means:

- preflight passes in the accepted dogfood environment without mutation;
- each missing or unsafe prerequisite fails before mutation with an actionable
  message;
- unit tests cover malformed self-identity, daemon mismatch, missing socket,
  ambiguous mounts, read-only workspace, path escape, missing display, and
  redaction; and
- the source/local-PEX command surfaces expose the same behavior if a public
  inspection command is introduced.

Implementation and evidence:

- `devcapsule project --path PATH recursive-e2e preflight` provides
  human-readable and stable JSON reports, returning nonzero when any
  prerequisite is unsafe or missing;
- ordinary output redacts all host mount sources and the Xauthority container
  path, while `--show-host-paths` requires an explicit disclosure warning;
- v024 launch plans carry the generated non-secret container name for exact
  daemon inspection, with a read-only overlay identity fallback allowing the
  accepted v023 bootstrap container to be inspected before that metadata
  exists;
- Git discovery disables optional locks, and preflight performs no clone,
  build, launch, workspace creation, or Docker mutation;
- failure-first tests cover malformed identity/name, daemon mismatch, missing
  socket selection/socket, ambiguous/read-only mounts, symlink and traversal
  escape, missing display, redaction, and CLI result status; and
- the accepted v023 environment returned `READY` from both source and local
  PEX surfaces with host paths redacted. The only warnings were the expected
  dirty working tree and source-vs-embedded-v023 bootstrap distinction.

## Stage 1: Add Verified Host-Daemon Path Translation And Staging

Status: complete on the milestone working tree as of 2026-08-06

Introduce one reusable internal host-daemon launch context. It must derive a
validated mapping from current-container destinations to host-daemon sources
and translate only paths beneath approved mounts.

The context owns:

- longest-prefix path translation with canonical containment checks;
- distinction between readable and writable source mounts;
- a test-owned writable host-backed staging root;
- preparation and cleanup of runtime plan, identity, group, sudo-policy,
  Xauthority, and related transient launch inputs;
- source-path validation for project, state, Docker socket, and X11 mounts; and
- sanitized plan inspection that distinguishes container-visible paths from
  host-daemon paths without disclosing secrets.

The ordinary host-launched DevCapsule path must remain unchanged. Recursive
translation activates only after verified preflight and explicit recursive E2E
invocation; it is not an ambient heuristic applied to every container run.

Done means:

- focused tests cover nested mount precedence, symlinks, traversal, deleted
  paths, file mounts, socket mounts, read-only mounts, and unmapped paths;
- every temporary file uses the intended restrictive mode and cleanup occurs
  after preparation or launch failure;
- Docker planning receives host-valid sources while runtime plans retain the
  correct successor-container destinations; and
- no real container is required for the fast-test closure of this stage.

Implementation and evidence:

- `HostDaemonLaunchContext.for_recursive_dogfood` accepts only a successful
  Stage 0 report carrying the exact inspected container and then approves the
  named project, runtime-plan, persistent-home, state, Docker-socket, X11, and
  Xauthority mounts;
- translation resolves existing paths canonically, preserves unique
  longest-prefix mount selection, blocks an approved-parent fallback across a
  more-specific unapproved mount, distinguishes read and write access, and
  validates directory, regular-file, and Unix-socket sources;
- bind plans contain host-daemon-valid sources while retaining exact successor
  destinations. Ordinary mappings, string representations, and dataclass
  representations redact raw host sources and sensitive staged paths;
- `RecursiveStagingArea` creates a collision-safe ownership-marked run root
  beneath persistent home, writes runtime-plan/account/Xauthority/development-
  sudo inputs with tested modes, identifies the sudo policy's later root-owner
  requirement, and deletes only the exactly marked run root;
- default cleanup is covered after partial preparation, bind planning, and a
  later launch failure. `keep_on_failure` preserves the owned run only when
  explicitly selected, and mismatched ownership refuses deletion;
- focused Docker-free coverage includes nested mounts, same-mount and escaping
  symlinks, traversal, deleted/unmapped paths, file and socket mounts,
  read-only access, malformed host sources, state paths, modes, redaction, and
  pre-existing workspace protection; and
- a live dry run in the accepted v023 container approved six exact mounts,
  staged four non-sudo launch inputs, planned project/Docker/X11 binds with all
  host sources redacted, invoked no Docker mutation, and verified complete
  ownership-marked cleanup;
- the full dirty-tree Nox gate passed 215 fast tests, clean mypy over 78 source
  files, source and local-PEX command smoke, execution of the Stage 1 public
  interface through the local PEX, and all five packaging integrations. As
  designed, the dirty-tree gate did not create a revision-bearing public PEX.

## Stage 2: Build v024 And Perform The Manual Dogfood Handoff

Status: pending

Bootstrap prerequisite status: minimum orchestrator and normal-run readiness
integration implemented and validated in the milestone working tree on
2026-08-07; v024 itself has not been built.

Execution checklist:
[`2026-08-06-recursive-dogfood-stage-2-execution-checklist.md`](2026-08-06-recursive-dogfood-stage-2-execution-checklist.md).

Once Stages 0 and 1 plus the minimum recursive orchestrator skeleton pass their
repository gates, build a revision-bearing PEX and local managed v024 base from
the clean committed milestone checkpoint while still running v023.

The initial skeleton uses `devcapsule project --path PATH recursive-e2e run` as
the public orchestration surface and a thin `recursive_dogfood_e2e` Nox wrapper.
Normal `devcapsule project run` supplies readiness to this repository when the
developer has authorized host Docker access; the E2E command never becomes a
second project-launch path.

The v024 checkpoint must:

- embed the exact committed checkpoint revision and matching PEX;
- contain the recursive preflight, verified host-daemon path translation,
  host-backed staging, and enough orchestration entry-point behavior to resume
  the milestone from inside v024;
- pass managed-image metadata, inventory, source/PEX agreement, generic OCI
  process, and negative ambient-agent checks;
- receive a developer-owned exact-local-base authorization without changing
  the committed v023 lock; and
- materialize under its canonical environment identity rather than depend on a
  mutable debug alias.

The user then closes the v023 IDE and launches or confirms the v024 canonical
environment. The resumed agent verifies that the running container and embedded
PEX carry the v024 checkpoint revision before proceeding. The handoff and exact
local image identities are recorded in `CURRENT-STATUS.md` without publishing
v024.

Done means:

- repository gates pass at the clean v024 checkpoint revision;
- the v024 base and materialized environment strictly validate;
- the user confirms the v024 IDE/Codex dogfood environment is usable;
- the resumed agent proves it is executing inside that exact environment; and
- no full recursive acceptance result is claimed yet.

## Stage 3: Automate Clean Local Clone And Contributor Bootstrap

Status: pending

Create the E2E workspace beneath the approved persistent-home mount and clone
the current repository locally at the exact committed revision selected for the
run. Refuse a dirty or uncommitted acceptance revision.

The clone/bootstrap flow must:

- avoid network and Git credentials for the local clone;
- avoid sharing the source checkout's `.venv`;
- initialize a new isolated contributor environment from committed project
  metadata;
- report exact Python and packaging-tool identities;
- run the complete repository Nox build gate;
- produce `dist/devcapsule.pex` with the clone's exact full revision and public
  source URL; and
- record sanitized logs and artifact checksums in the E2E manifest.

Downloads required by the committed contributor setup may use ordinary
networking, but the plan must identify them and failures must leave the clone
safe to retry. Personal package credentials are not imported automatically.

Done means:

- the flow succeeds after deleting any previous test clone and environment;
- it proves the new environment does not resolve to the original checkout's
  `.venv`;
- a second bootstrap is deterministic or safely reuses only its own isolated
  state;
- corrupt/incomplete bootstrap state produces repair guidance; and
- the built PEX reports the exact clean clone revision.

## Stage 4: Build And Verify The Successor Base From Inside Dogfood

Status: pending

Use the newly built revision-bearing PEX to invoke the production base-image
builder against the authorized host Docker daemon.

The base gets a unique E2E discovery tag, while its immutable image ID and
managed metadata remain authoritative. The build must not overwrite the
published v023 tag or any unrelated canonical image.

Verification includes:

- managed metadata version and kind;
- recipe and root-image identity;
- exact source revision and canonical public source URL;
- embedded PEX SHA-256 matching the clone artifact;
- generic OCI entrypoint and command;
- expected baseline tools and explicit absence of ambient agent CLIs;
- absence of project source, checkout configuration, state, credentials,
  runtime authorization, and a baked checkout runtime plan; and
- build failure/interrupt behavior and ownership-safe cleanup.

Done means the verified image ID is recorded in the run manifest and can be
authorized as an exact managed local base. Merely creating a mutable tag is not
sufficient evidence.

## Stage 5: Configure, Resolve, And Materialize The Clean Clone

Status: pending

Run the built PEX against the clean clone with all developer-owned configuration
roots isolated beneath the E2E workspace.

The production command flow must:

1. initialize/list checkout readiness;
2. bind or select only test-owned persistent state;
3. authorize the exact new local base image ID and current lock digest;
4. grant only the selected Docker, network, and sudo choices for the positive
   scenario;
5. resolve and inspect the generated plan without acquisition or launch side
   effects; and
6. materialize or strictly reuse the canonical PyCharm/Codex environment through
   ordinary realization code.

The scenario must also produce a safe unauthorized plan proving that absence of
authorization yields bridge/no-host-Docker/no-sudo behavior. It need not start a
second GUI for every negative case when the complete Docker plan and a small
non-GUI container probe provide equivalent evidence.

Done means:

- checkout, resolution, cache, and state paths are confined to the run root;
- the resolution selects the newly built exact local base without changing the
  committed v023 lock;
- canonical materialization identity and complete metadata validate;
- a second realization strictly reuses the matching image; and
- no personal checkout record, state, credential, or unrelated image changes.

## Stage 6: Launch And Inspect A Detached Successor

Status: pending

Add an explicit detached successor-launch mode that uses the same production
runtime plan and Docker argument planner as ordinary foreground launch. Detached
mode changes client attachment, not the IDE-owned container lifecycle: `tini`
and the IDE remain the container's foreground process, and IDE exit still ends
the container.

The recursive launch must translate and stage:

- clean-clone project source;
- persistent home and component state;
- external read-only checkout runtime plan;
- generated identity/group files;
- optional development-sudo policy;
- host Docker socket when authorized;
- X11 socket and fresh restrictive Xauthority material; and
- any other declared runtime mount.

Automated inspection must confirm:

- successor image ID and source revision;
- project destination and exact host source;
- runtime UID/GID, supplementary groups, and home/XDG values;
- runtime-plan destination, read-only mode, and cleanup behavior;
- network, memory, Docker, sudo, capability, security-option, and privileged
  state;
- PyCharm and Codex component processes;
- E2E ownership labels; and
- continued health after the launching command returns to the agent.

Done means the agent can launch and inspect the successor without a host-terminal
command and without stopping or blocking the current dogfood container.

## Stage 7: Prove Persistence, Failure Paths, And Deterministic Cleanup

Status: pending

Complete the orchestrated scenario around the successful successor launch.

It must:

- create a test-owned persistence sentinel through the first successor;
- stop or close only the test-owned successor through a deliberate E2E action;
- launch it again and prove the sentinel plus declared state persists;
- exercise at least clone/bootstrap failure, base-build failure, stale local-base
  authorization, materialization conflict, launch failure, and interrupted-run
  cleanup;
- preserve sanitized diagnostics under `--keep-on-failure`;
- resume or clean a previously interrupted run from its manifest; and
- remove only exact labelled/recorded resources when cleanup is requested.

Done means repeated successful runs leave no unrequested test container,
checkout, XDG tree, transient secret, or image alias, and failure injection
cannot select unrelated resources for cleanup.

## Stage 8: Full Recursive Dogfood Acceptance

Status: pending

From the accepted running v024 dogfood container, the agent executes the
documented single entry point against a later clean committed milestone
revision.

Repository and automated evidence:

- fast tests and the ordinary full Nox build gate pass;
- the explicit recursive E2E completes all post-handoff Stages 3 through 7,
  while retained evidence confirms the Stage 0 through 2 bootstrap lineage;
- the new PEX and base agree on exact source revision and digest;
- the successor uses the new base and canonical materialized image;
- positive and safe negative authorization behavior passes;
- persistence and deterministic cleanup pass; and
- logs and retained evidence contain no credentials or Xauthority contents.

Manual evidence permitted:

1. the user confirms the new IDE window is visible and usable;
2. the user confirms representative editor, terminal, preview, and Codex
   behavior; and
3. the user closes the previous IDE when ready, or explicitly keeps both during
   diagnosis.

The agent records the manual result in `CURRENT-STATUS.md`. No laptop-specific
absolute path, personal credential, or mutable debug tag becomes a committed
acceptance dependency.

## Milestone Completion Criteria

The milestone is complete only when all of the following are true:

- one explicit command initiated by the agent inside dogfood orchestrates the
  clean-clone-to-successor scenario;
- v023 first builds a validated local v024 checkpoint and the user manually
  hands dogfood over to it without changing the committed v023 lock;
- the full recursive run is initiated from a container and embedded PEX carrying
  the exact v024 checkpoint revision rather than borrowing newer code only from
  the mounted checkout;
- the clean clone bootstraps independently of the existing checkout's `.venv`;
- the full gate creates a revision-bearing PEX;
- that PEX builds a strictly verified managed base through host Docker;
- the clean clone authorizes the exact local base without changing the
  committed published-base lock;
- production resolution, realization, runtime planning, and launch paths create
  the successor;
- every bind source is valid in the host daemon's namespace and confined to
  approved mappings;
- authorized and safe unauthorized Docker/network/sudo behavior is verified;
- persistence, interruption, evidence, and ownership-safe cleanup are tested;
- the successor remains alive and inspectable after detached launch;
- the final GUI usability/handoff check is manually accepted; and
- the product owner accepts the milestone based on recorded evidence.

## Explicit Non-Goals

This milestone does not by itself:

- complete the general user-facing ecosystem-bootstrap adapters in F1;
- finish PyCharm functional closure, ordinary-value defaults, or state-lifecycle
  UX;
- reimplement VSCodium or settle its historical bugs;
- create the starter IDE/demo catalog;
- publish or select an official V1/next-version registry base;
- update the committed v023 dogfood lock to a mutable local image;
- introduce arbitrary host filesystem orchestration;
- automate pixel-level GUI interaction;
- eliminate the one-time v023-to-v024 manual dogfood handoff;
- share personal Git, registry, PyCharm, or Codex credentials by default;
- stop the current dogfood container automatically;
- support Gemini CLI; or
- remove unrelated images, containers, volumes, state, or build caches.

## Next Task

Review and commit the minimum recursive orchestrator skeleton and Nox entry
point, then rerun the full repository gate from that clean exact revision. Use
its revision-bearing PEX to build and verify the local v024 base and canonical
environment from v023, then request the manual dogfood handoff.
