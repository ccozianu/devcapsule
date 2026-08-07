# Milestone Plan: Recursive Dogfood E2E — Build And Launch A Successor From Inside DevCapsule

Status: active milestone; Stages 0 through 3 complete

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

Status: complete on 2026-08-07

Checkpoint revision: `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
Completion evidence and immutable image identities are recorded in
`CURRENT-STATUS.md` under “Stage 2 bootstrap handoff checkpoint, 2026-08-07.”

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

Completion recheck on 2026-08-07 confirmed all five conditions. The committed
lock still selects published v023; the revision-bearing PEX, local v024 base,
canonical materialized environment, and running container retain their
recorded exact revision, checksum, and immutable lineage; embedded-PEX
preflight remains `READY`; and the implementation-equivalent full dirty-tree
gate passed clean mypy over 79 files, 221 fast tests, all command and PEX
smokes, and five packaging integrations. The strict base probe also confirmed
the expected core tooling and pinned Node archive plus absence of ambient
Codex, Claude, or Gemini commands, project source, credential state, and a
baked runtime plan. The archive's bare-image `PATH` exposure is a separate
runtime-tooling usability gap, not a failure of this completed bootstrap
lineage/handoff stage.

## Stage 3: Automate Clean Local Clone And Contributor Bootstrap

Status: complete on 2026-08-07.

### Goal

From the verified v024 container:

1. select one clean, exact source commit;
2. make an independent local clone;
3. bootstrap a clean contributor environment; and
4. prove the protocol both recursively and from a contributor laptop.

The full clean gate, revision-bearing PEX, successor image, configuration,
materialization, and launch belong to later stages.

The user-facing command remains:

```text
cd devcapsule
python -m nox -s recursive_dogfood_e2e
```

### What Already Works

- [`test_recursive_local_clone.py`](../tests/e2e/test_recursive_local_clone.py)
  proves the current container and image, makes an exact local clone without
  shared Git objects or credentials, and performs ownership-checked cleanup.
- [`test_contributor_bootstrap.py`](../tests/e2e/test_contributor_bootstrap.py)
  and its adjacent driver create a copied Python 3.12 venv, install the
  committed development dependencies, install DevCapsule editable, and prove
  import and environment isolation.
- The contributor test passes both inside v024 and directly on the laptop.
  The spawned contributor uses host networking because this dogfood host blocks
  public downloads from Docker bridge containers. Recursive mode first confirms
  through Docker inspection that the current container is also host-networked.
- The complete recursive Nox entry point passes both E2Es.

These tests are the accepted Stage 3 outcome. Additional negative, recovery,
and durability coverage is tracked in the
[V1 test backlog](2026-08-07-v1-test-backlog.md), not as a Stage 3 blocker.

### Revision Rule

Keep these identities separate:

- **v024 bootstrap:** the running image and embedded PEX must agree with
  `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
- **Selected source:** the current checkout must be clean and resolve to one
  full commit.
- **Generated artifacts:** the clean clone and its new PEX must match the
  selected source commit exactly.

The selected source will normally be newer than v024. Never require current
`HEAD` to equal the embedded v024 revision.

The local-clone protocol rejects dirty or untracked source and an abbreviated
commit. The developer's configured `origin` URL is not part of that protocol;
Stage 4 verifies public artifact metadata separately.

### Completion Evidence

- Recursive v024 run:
  `python -m nox -s recursive_dogfood_e2e` passed both Stage 3 E2Es
  (`2 passed`, `1 deselected`).
- Contributor-laptop run:
  `pytest --no-cov tests/e2e/ -m contributor_e2e` passed
  (`1 passed`, `2 deselected`).
- The clone is exact, detached, independent of the source object store, and
  contains no path-bearing local origin.
- The contributor environment uses a copied Python 3.12 venv and committed
  development dependencies without receiving the original checkout, Docker
  socket, sudo, or credentials.
- Both tests remove only their ownership-marked resources and leave no owned
  container, network, or workspace behind.

This closes Stage 3. Stage 4 may reuse these proven protocols when it creates
the retained milestone run, builds the revision-bearing PEX, and builds the
successor base.

## Stage 4: Build And Verify The Successor Base From Inside Dogfood

Status: pending

Start by composing the accepted Stage 3 clone and bootstrap protocols into the
retained, ownership-marked milestone run. From its clean clone:

1. run the full clean Nox gate with run-owned environments;
2. build and inspect the revision-bearing public PEX;
3. record the clone revision and PEX checksum in the run manifest; and
4. use that PEX to invoke the production base-image builder against the
   authorized host Docker daemon.

The PEX must report the clean clone's full public revision and must not import
from the original checkout or contributor venv. The run must preserve the
global ownership, redaction, and cleanup rules above.

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

### Outcome And Boundary

Launch the Stage 5 canonical environment on the host daemon, return control to
the agent while that successor remains running, then prove the launched
container matches the exact resolved production plan. This is an engineering
mode of the shared launcher, not a second adopter workflow: ordinary
`devcapsule project run` remains foreground and the contributor still invokes
the recursive scenario through `recursive-e2e run` or its Nox wrapper.

The clean clone's revision-bearing PEX must execute the successor-launch
boundary. The project-scoped child-process interfaces are:

```text
CLEAN_PEX project --path CLEAN_CLONE recursive-e2e launch-successor \
  --run-id RUN_ID --json

CLEAN_PEX project --path CLEAN_CLONE recursive-e2e inspect-successor \
  --run-id RUN_ID --json
```

These subcommands derive `manifest.json` from the validated
`e2e-workspaces/RUN_ID` root rather than accepting an arbitrary manifest or
host path. They are engineering process boundaries used by `recursive-e2e
run`, not alternative ways to enter an ordinary project environment.

Detached mode uses the same resolved project, canonical realization,
`RuntimePlan`, component metadata, and Docker argument planner as ordinary
foreground launch. Only the execution/lifecycle policy differs. `tini` and
PyCharm remain the container's foreground process; no shell wrapper or
background IDE process is introduced, and IDE exit ends the running container.
The E2E may retain the resulting stopped container until ownership-checked
cleanup so startup failures remain inspectable; that retention does not change
the process lifecycle.

### Required Refactoring Seam

The current production path combines four concerns in `run_pycharm`: resolving
launcher configuration, creating temporary runtime files, assembling Docker
arguments, and synchronously executing `docker run --rm -i` followed by
immediate file cleanup. Stage 6 separates these without creating a parallel
Docker planner:

1. one production service resolves the selected project and canonical image
   into the existing `PycharmRunConfig` and checkout `RuntimePlan`;
2. one launch-input interface supplies the runtime plan, passwd/group,
   optional shadow/sudo policy, and Xauthority files;
3. the existing Docker argument planner consumes those inputs and a typed
   attachment/lifecycle mode; and
4. foreground and recursive-detached executors consume the same completed
   plan.

The ordinary executor retains its current foreground behavior and temporary
file cleanup. The recursive executor supplies `RecursiveStagingArea` files
with verified host-daemon sources, uses detached execution, and keeps those
files for as long as the successor may read them. No recursive code may copy
and then independently evolve the production list of mounts, environment
variables, capabilities, or runtime limits.

### Preconditions And Manifest State

Before any launch mutation, the orchestrator must:

- rerun Stage 0 preflight so the current container, mount map, Docker socket,
  display, and authorization evidence are current;
- load an ownership-valid run manifest in the Stage 5 `materialized` state;
- verify the clean clone, isolated XDG roots, persistent home, component state,
  canonical environment identity and immutable image ID against that manifest;
- strictly reuse the Stage 5 canonical image rather than materializing a new
  identity during launch;
- reject a dirty or revision-mismatched clean clone and a stale generated
  resolution;
- reject an already-recorded live successor unless this is an explicit resume
  that proves the same immutable container identity and labels; and
- atomically record the deterministic container name, intended image ID,
  launch-plan digest, and `launching` state before calling Docker.

Use a collision-safe name derived from the run ID, for example
`devcapsule-e2e-RUN_ID-successor`. Docker resources must carry the common E2E
labels plus a role label:

```text
devcapsule.e2e.managed=true
devcapsule.e2e.run-id=RUN_ID
devcapsule.e2e.source-revision=REVISION
devcapsule.e2e.role=successor
```

Container name and labels are discovery aids. The full Docker container ID and
image ID become authoritative immediately after creation.

### Runtime Inputs And Host Translation

The recursive launch must translate and stage:

- clean-clone project source;
- persistent home and component state;
- external read-only checkout runtime plan;
- generated identity/group files;
- optional development-sudo policy;
- host Docker socket when authorized;
- X11 socket and fresh restrictive Xauthority material; and
- any other declared runtime mount.

Every bind source is first expressed in the current v024 container namespace,
resolved through `HostDaemonLaunchContext`, and translated through the longest
verified writable or readable mount prefix. The resulting Docker plan contains
host-daemon paths, but ordinary output and retained evidence show only the
logical purpose, successor destination, access mode, and a stable non-secret
identity. `--show-host-paths` remains the only explicit disclosure mode.

Stage under the ownership-marked run root with these minimum rules:

- the checkout runtime plan, passwd, and group files use mode `0644` and are
  mounted read-only;
- Xauthority and shadow use mode `0600`, the sudo policy uses mode `0440`, and
  none of their contents or host paths enter logs or the manifest;
- Xauthority contains only authorization material needed for the selected
  display and fails closed when no usable entry can be prepared;
- the host Docker socket is included only for the authorized positive plan;
- shadow and sudo policy are absent unless development sudo is authorized;
- all persistent directories already belong to this run and are not removed
  with transient staging; and
- transient staging is not removed while the recorded container is running or
  still available for requested failure inspection.

### Docker Plan And Launch Handshake

The shared Docker planner must preserve the realized image's generic OCI
entrypoint and runtime-plan command. The recursive executor must not append a
PyCharm command override. Concretely, it replaces foreground `--rm -i` with
`--detach`: omitting `-i` prevents stdin attachment, and omitting `--rm` retains
an exited E2E-owned container for bounded evidence and exact cleanup. The
ordinary foreground plan remains unchanged. The detached plan must retain
`--pull=never` and must not silently add host networking, Docker access, sudo,
capabilities, security options, devices, or privilege beyond the resolved
Stage 5 plan.

The launch handshake is:

1. invoke `docker run` once with the completed production plan;
2. require one syntactically valid full container ID from Docker stdout and no
   ambiguous extra result;
3. inspect that exact ID immediately, without rediscovering it by name;
4. prove its name, E2E labels, immutable image ID, and running state before
   atomically changing the manifest from `launching` to `running`;
5. run bounded readiness inspection and record `inspection-passed` only after
   every automated assertion succeeds; and
6. return a sanitized JSON result containing the run ID, container ID, image
   ID, source revision, evidence path, and state, but no host source or secret.

If Docker returns an ID but inspection cannot prove ownership or identity, the
orchestrator treats the result as an untrusted launch: it records the failure,
does not select the object by name for later operations, and reports the exact
manual diagnosis needed. Automatic stop/removal is allowed only after exact ID
and label ownership are both proven.

### Automated Inspection Contract

Inspection uses the exact recorded container ID and must confirm:

- successor image ID and source revision;
- project destination and exact host source;
- runtime UID/GID, supplementary groups, and home/XDG values;
- runtime-plan destination, read-only mode, and cleanup behavior;
- network, memory, Docker, sudo, capability, security-option, and privileged
  state;
- the PyCharm component process and exact Codex component availability;
- E2E ownership labels; and
- continued health after the launching command returns to the agent.

More precisely, daemon inspection must compare the actual container against a
machine-readable expected plan and verify:

- `Config.Image` resolves to the Stage 5 canonical environment and `.Image`
  equals its immutable ID;
- managed materialized-image labels identify the clean-clone source revision,
  expected base image, PyCharm component, Codex component, and formation
  identity;
- the container user, work directory, selected non-secret environment values,
  supplementary group IDs, network mode, memory limit, read-only root,
  `Privileged`, `CapAdd`, `CapDrop`, `SecurityOpt`, and restart policy exactly
  match the resolved plan;
- the mount set has no missing or extra bind, each destination and read-only
  flag matches, and each daemon-side source equals the internally retained
  translated source; ordinary evidence redacts those sources;
- the checkout runtime plan is mounted at
  `/etc/devcapsule/runtime-plan.json` read-only and its SHA-256 equals the
  launch-plan record;
- PID 1 is the expected `tini`/DevCapsule runtime chain and the PyCharm process
  is alive with the clean-clone project destination;
- unprivileged in-container probes report the expected UID, primary GID,
  supplementary groups, `HOME`, XDG roots, project directory, Docker access,
  and sudo behavior; and
- the exact declared Codex executable and version are available. Stage 6 does
  not automatically start a persistent or credential-bearing Codex session;
  interactive Codex behavior remains part of Stage 8 manual acceptance.

“Continued health after return” requires a second public inspection after the
detached launch child process has exited, not merely a check inside that child.
The outer orchestrator reacquires the exact ID from the manifest, observes it
running in at least two bounded samples separated by a short stability window,
and proves that it has not restarted or changed identity. A Docker healthcheck
is useful if the canonical image declares one but is not fabricated solely for
this stage.

### Failure And Cleanup Semantics

- Failure before Docker mutation cleans transient staging unless
  `--keep-on-failure` is active.
- Failure before a container ID is returned must not guess a cleanup target by
  name or prefix.
- Failure after exact ownership is proven stops/removes only that ID when
  cleanup is requested; otherwise it preserves the container and staging with
  sanitized inspection instructions.
- An early successor exit is a launch failure even when Docker itself returned
  success. Preserve exit code, timestamps, and bounded sanitized diagnostics;
  do not retain Xauthority contents or environment secrets.
- Successful Stage 6 intentionally retains the running successor, its manifest,
  persistent state, and required staging for Stage 7. It performs no broad
  image, volume, build-cache, workspace, or container cleanup.
- Staging cleanup occurs only after inspection proves the successor is stopped
  and any retained container has been removed or explicitly abandoned under
  `--keep-on-failure`.

Manifest writes are atomic and monotonic. At minimum they distinguish
`materialized`, `launching`, `running`, `inspection-passed`, `stopped`,
`failed`, and `cleaned`; record timestamps, exact immutable identities, and
sanitized artifact paths without recording credentials or bind-source values.

### Validation Slices

Implement and close Stage 6 in these slices:

1. **Shared planner seam.** Refactor production foreground launch behind typed
   plan/input/executor interfaces. Golden public-interface tests prove the
   foreground Docker plan is unchanged.
2. **Detached plan and manifest transition.** Add E2E labels, exact-ID capture,
   atomic `materialized -> launching -> running` transitions, and tests for
   malformed/ambiguous Docker output.
3. **Host-backed staging lifetime.** Integrate translated
   `RecursiveStagingArea` inputs and prove they remain while the detached
   container exists and are ownership-safely cleaned afterward.
4. **Inspector.** Compare Docker inspection and in-container probes against the
   expected plan with host-path/secret redaction tests.
5. **Failure handling.** Cover pre-mutation failure, immediate exit, identity or
   label mismatch, timeout, inspect failure, cleanup refusal, and
   `--keep-on-failure` through public CLI/orchestrator interfaces.
6. **Live recursive proof.** From v024, launch the actual Stage 5 canonical
   successor through the clean-clone PEX, let the launch command return, run the
   independent inspector, and preserve sanitized evidence for Stage 7.

Fast tests may use a recording Docker process boundary, but they must exercise
the public launcher/orchestrator interfaces rather than private helpers. Add a
small real-Docker detached lifecycle integration where practical; the actual
GUI/X11 successor launch remains part of the explicit recursive E2E and not the
ordinary `nox -s build` gate.

### Completion Evidence

Done means the agent can launch and inspect the successor without a host-terminal
command and without stopping or blocking the current dogfood container. The
retained evidence must include:

- run ID, exact clean-clone revision, PEX SHA-256, canonical environment name,
  formation identity, base ID, environment image ID, and container ID;
- sanitized expected-versus-actual Docker plan results;
- successful runtime identity, mount, security, PyCharm-process, Codex-binary,
  and stability probes;
- proof the launch child returned while the same successor remained running;
- proof the current v024 dogfood container was not stopped or modified; and
- the exact owned resources intentionally retained for Stage 7.

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
- the embedded v024 PEX/image revision and the later selected source/clean-clone
  revision are separately recorded, with agreement inside each required pair
  and no false requirement that both generations use one revision;
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
- the full recursive run starts inside the exact v024 container, first executes
  its matching embedded-PEX preflight, records the later clean selected-source
  revision, and then uses the clean-clone PEX for successor production
  boundaries rather than conflating those two generations;
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

Begin Stage 4 by composing the accepted Stage 3 protocols into one retained,
ownership-marked milestone run. From its clean clone, run the full clean Nox
gate, build and verify the revision-bearing PEX, then use that PEX to build and
inspect the successor base through the authorized host Docker daemon.

Additional workspace, retry, corruption, redaction, and isolation hardening is
tracked in [the V1 test backlog](2026-08-07-v1-test-backlog.md). It is not a
Stage 3 closure condition.
