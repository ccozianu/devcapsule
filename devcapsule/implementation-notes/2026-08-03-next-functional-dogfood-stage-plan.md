# Plan: Reach The Next Functional Dogfood Stage From `wip/local-pycharm-materialization` At `b5d42e8`

Status: landed; functional dogfood checkpoint manually accepted on 2026-08-05
Baseline branch: `wip/local-pycharm-materialization`
Baseline revision: `b5d42e8502919c3e1c0fa533ea02d31351b1417f`
Date: 2026-08-03

This document is the execution plan for reaching the next functional dogfood
stage from the branch and committed revision above. The target is a workable
second DevCapsule checkout launched through the new capability-first project
configuration, canonical environment materialization, and generic Python
runtime mechanics. It is deliberately narrower than the complete V1 backlog.

Requirements: root `R-PRODUCT-001`, root `R-PRODUCT-002`,
`devcapsule` `R-STATE-001`, `R-SCOPE-001`, `R-DOCKER-001`,
`R-IDE-CONFIG-001`, `R-PYTHON-MVP-003`, `R-IMAGE-BUILD-001`, and
`R-FRAMEWORK-001`.

## Current Progress

Current stage: complete by product-owner manual acceptance. The scripted
Stage 5 implementation is waived; fuller automated E2E coverage is a later V1
task.

The single current dogfood image-version variable for this plan is:

```bash
DOGFOOD_IMAGE_VERSION=v023
```

All forward-looking stage instructions and acceptance checks refer to
`${DOGFOOD_IMAGE_VERSION}`. Advancing the dogfood base should require changing
only this assignment. Literal `v020`, `v021`, and `v022` references below are
historical evidence and must remain literal.

The validated local base is
`devcapsule-local-base:${DOGFOOD_IMAGE_VERSION}`. Docker inspection records
image ID
`sha256:a69887edc5aea3b559aaf0fd69b9e4b451ff99488aa3099239c869e052dccbfe`
and exact source revision:

```text
a33988a24a91ef382c1c5c6265ba2a34762ba115
```

The running canonical materialized environment derived from that base carries
the same exact source revision and completed the Stage 4 host validation.
The product owner externally tagged and pushed that exact base as
`docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v023`. Registry
inspection resolved the tag and the local image's `RepoDigests` to the same
immutable manifest digest:

```text
sha256:e8ec48fa1f45f566e997735ac5e8ce8086a2512681db0e8a22696ee0801a8aa1
```

The committed Linux dogfood lock now selects that immutable digest. The tag is
discovery metadata only and is not the committed formation input. The updated
lock passed manifest-digest and lock-parser validation; the Docker-free Nox
tests, source command smokes, and type checks also passed without rebuilding
the already-validated PEX or images.

For historical context, the published v021 dogfood base used source revision:

```text
5401ce3506c0a8a63bfef40f4f9ef18d2b987436
```

That revision contained the completed Stages 0 through 2 and was used as both
the PEX source revision and the asserted
`images build --type base --source-revision` value. The resulting v021 base was
built, inspected, scanned, and published as immutable registry digest
`sha256:cd1a0e713e515234ef438c0502786353ec1678d2efd67b61a0bae6baf9fdc51e`.
The committed platform lock selected that digest; later local dogfood versions
use the exact developer-owned local-base authorization path until published
and selected by an immutable registry digest.

The original `b5d42e8` baseline above remains the historical starting point for
this plan. Progress from that baseline is:

- Stage 0 and interactive `config authorize --all-recommended` were committed
  as `3608ffc` (`Add project configuration readiness workflow`). The full gate
  passed with 146 fast tests at 80% coverage, clean mypy, source/local-PEX
  smokes, PEX construction, and three packaging integrations.
- Stage 1 was committed as `c07ae3b` (`Share project environment realization`).
  `images build --type environment` and formation-based `project run` now use
  one authorization-enforcing canonical realization service. Its full gate
  passed with 155 fast tests at 80% coverage, clean mypy, and all packaging
  checks.
- Stage 2 is implemented and validated in the current checkpoint. It
  generates the redacted checkout runtime plan, delivers it through an
  external read-only mount, preserves the canonical image's OCI
  entrypoint/CMD, and cleans plan and identity files on success or failure.
  Its full dirty-tree gate passed with 161 fast tests at 80% coverage, clean
  mypy over 69 files, source/local-PEX smokes, PEX construction, and all three
  packaging integrations.
- Stage 3 is implemented and validated. Resolved memory, Docker-daemon,
  network, and development-sudo choices flow into the shared launch options.
  Focused tests prove the complete authorized Docker plan and the safe
  negative plan. Its full gate passed with 178 fast tests at 81% coverage,
  clean mypy over 73 source files, source/local-PEX smokes, PEX construction,
  and all three packaging integrations.
- Stage 4 is implemented and fully validated. Authorized launches create
  a group-scoped temporary sudoers policy, use a constrained no-network,
  read-only, `CHOWN`-only helper to satisfy sudo's root-ownership requirement,
  mount the policy read-only, and clean it after success or failure. The full
  gate passed with 182 fast tests at 81% coverage, clean mypy over 73 source
  files, source/local-PEX smokes, PEX construction, and all three packaging
  integrations. The live `${DOGFOOD_IMAGE_VERSION}` formation-based launch
  then passed the authorized and unauthorized host checks recorded in Stage 4.

No real image was pulled, built, or launched by the automated work for Stages 0
through 2. The later v021 base was built and published externally; Stages 3
and 4 were subsequently completed against newer local dogfood checkpoints.
The product owner subsequently accepted the satisfactorily running second
checkout as the functional dogfood result. Stages 5 through 8 are closed by
the scope decision recorded below rather than by maintaining a laptop-specific
acceptance script.

Post-v021 dogfood checkpoint: revision
`43073361c8bb11fecece7913b3a511b47dd2778a` adds the optional Codex component,
the accepted JCEF compatibility setting, and the explicit abstract component
contract. A local `devcapsule-local-base:v022` embeds that exact revision.
Developer-owned `config authorize base-image LOCAL_NAME` now supports testing
such a managed local base without weakening committed-lock rules: it pins the
inspected Docker image ID and current lock, and resolve/run reject a missing or
retagged image. Publishing and locking v022 by registry digest remain pending.
An isolated-XDG smoke against the real local v022 image passed authorization,
resolution, and readiness inspection. The full dirty-tree Nox gate then passed
with 176 fast tests at 80% coverage, clean mypy over 73 source files, source
and local-PEX command smokes, PEX construction, and all three packaging
integrations.

## Executive Scope Decision: Gemini CLI Is Unsupported

DevCapsule will not support Gemini CLI. Active code, images, manifests, locks,
runtime plans, launchers, state contracts, tests, and user instructions must
not install, select, configure, mount state for, or advertise Gemini CLI.

This product-owner direction retires D-0005's former open possibility that
Gemini CLI might later become an optional component. D-0005 remains immutable
as a historical accepted decision; its agent-neutral base direction remains in
force, but its Gemini possibility is no longer active product scope.

The dogfood acceptance test may verify that `gemini` is absent as a negative
regression guard. That check does not make Gemini a supported component or a
dogfood dependency. Historical records and historical images may continue to
describe the Gemini-bearing behavior they actually had.

## Optional Codex Component Checkpoint

The product owner selected Codex as the dogfood agent component while keeping
the base agent-neutral. The dogfood manifest advertises `codex-agent`; the
platform lock pins the JetBrains ACP integration, Codex CLI version, license,
platform artifact URL, exact SHA-256, and archive member. Its trusted runtime
contract owns credential-bearing `codex/home` state at
`/home/devcapsule/.codex` and contributes `CODEX_HOME` only when selected.

Curated components explicitly inherit a trusted abstract Python contract for
runtime templates, state-to-environment mappings, optional-secret inputs, and
lock-pinned artifacts. Codex uses it to install the verified CLI at
`/usr/local/bin/codex`, map `codex/home` to `CODEX_HOME`, and advertise an
optional `OPENAI_API_KEY` input without importing it automatically. The user
authenticates with normal `codex login` inside the running capsule; the result
persists in component state. As an explicit higher-exposure alternative, the
existing generic `config bind` action can bind the declared same-named host
environment variable; only its name enters checkout/resolution data, and the
CLI warns that all capsule processes and Docker inspection can observe the
value while the container runs.

The key and `auth.json` must remain absent from committed metadata, checkout
TOML, generated resolution, runtime plans, Docker arguments, images, and logs.
The remaining external acceptance for CLI readiness on `PATH`, terminal or
JetBrains authentication persistence, ACP use of mounted component state, and
second-launch continuity is carried into later work below. It does not keep
this landed dogfood stage open.

The refined implementation passed the full dirty-tree gate with 172 fast
tests at 80% coverage, clean mypy over 73 source files, source and local-PEX
command smokes, PEX construction, and all three packaging integrations. Tests
also prove that built-in components explicitly inherit the abstract contract
and that an incomplete implementation cannot be instantiated.

## Starting Point

Revision `b5d42e8` provides:

- the committed capability declaration and digest-pinned v020 Linux lock;
- the agent-neutral v020 base and canonical PyCharm 2026.2.0.1 environment
  already materialized locally;
- generic `project config set NAME VALUE`, including the metadata-driven
  `runtime.memory-limit` Docker effect;
- generic `project config bind NAME --host-directory PATH` for persistent home
  and the five component-declared PyCharm slots;
- generic `project config authorize NAME VALUE` for the exact base image, host
  Docker socket, host network, and development sudo;
- fresh checkout resolution, named checkout registration, strict image
  metadata verification, and canonical environment reuse; and
- a clean full Nox gate with 138 fast tests, clean mypy, source and PEX command
  smokes, three packaging integrations, and a revision-bearing PEX for
  `b5d42e8`.

At that baseline, the blocker was `devcapsule project run`: it required a
legacy completed image in the generated resolution and invoked the legacy
PyCharm launcher command override. Stages 1 and 2 above have now removed both
parts of that baseline blocker while keeping the v020 image free of a baked
checkout runtime plan.

## Target Outcome

From the existing host clone at:

```text
$HOME/work.provisional/costin3/myProjects/devcapsule
```

the developer can use a clean PEX to:

1. register the checkout under a distinct workstation-owned name;
2. set an 8 GiB memory limit;
3. bind persistent home, shared PyCharm config/plugins, and checkout-specific
   PyCharm system/log/cache directories;
4. authorize the exact `${DOGFOOD_IMAGE_VERSION}` base identity, host Docker
   socket, host networking, and development sudo;
5. resolve an inspectable checkout plan without downloading, building, or
   launching;
6. run the project, automatically reusing or materializing its canonical
   PyCharm environment;
7. launch PyCharm through the generic PEX runtime with an external read-only
   checkout plan; and
8. exit and launch again with settings, plugins, login state, and intended
   checkout-specific state retained.

The new capsule should reproduce the useful behavior of the running v018
dogfood environment while deliberately using the agent-neutral
`${DOGFOOD_IMAGE_VERSION}` image and new configuration mechanics. Different
host checkout/state paths and the absence of Gemini CLI are intentional.

## Stage 0: Show Configuration Readiness

Status: implemented and validated.

Add the initializing inspection helper:

```text
devcapsule project [--path PATH] config list
```

It is an initializing inspection command. On first use it materializes the
selected checkout name, workstation configuration directory, valid minimal
checkout input, and unresolved generated-plan placeholder before listing:

- every ordinary value declared by project metadata and whether it is set,
  missing and required, or unset and optional;
- persistent home and every component-declared state resource, showing an
  explicit host-directory binding or the managed-default fallback;
- every authorization recommended by the project or lock, showing authorized,
  missing, or stale status and the exact recommended value; and
- whether the generated resolution is missing, fresh, or stale.

The command must identify the selected project, checkout name, checkout record,
and generated-plan path. Initialization must be idempotent and must not rewrite
existing choices or a resolved plan. When the portable project identity already
has a checkout record for another path, `config list` must not invent a name or
inherit that record; it fails with the existing instruction to run `project
checkout register NAME`, after which `config list` materializes any remaining
per-checkout placeholder. An incomplete but valid checkout remains successful
inspection rather than a command failure. Malformed committed metadata remains
an error; malformed developer values should be identified as invalid where the
row can be reported safely.

As a security-preserving convenience, `project config authorize
--all-recommended` previews every exact authorization and justification, then
accepts the complete current set only when the user presses the lowercase `y`
key in an interactive terminal. Any other key or a non-interactive invocation
writes nothing; scripted workflows retain explicit `authorize NAME VALUE`
commands.

Closure evidence:

- focused tests cover default-checkout initialization, an explicitly named
  checkout, idempotence, partial configuration, complete configuration, stale
  authorization, and stale resolution;
- source and PEX help smokes include `project config list`; and
- user documentation explains the status vocabulary and non-destructive
  behavior after initialization.

Recorded result: complete in `3608ffc`; the combined Stage 0 and interactive
authorization gate passed 146 fast tests at 80% coverage plus clean mypy and
all packaging checks.

## Stage 1: Share Environment Realization With `project run`

Status: implemented and validated.

Extract or introduce a host-side environment realization service reusable by
both `images build --type environment` and `project run`.

The service must:

- consume one fresh resolved project rather than re-read inconsistent layers;
- require the exact checkout-owned base-image authorization;
- obtain the locked digest reference only when it is not already local;
- validate managed-image metadata, schema version, kind, platform, and base
  identity;
- compute the canonical formation descriptor and image name;
- strictly verify and reuse a matching canonical environment before artifact
  acquisition;
- otherwise acquire and checksum-verify the locked PyCharm archive and build
  the canonical environment under the existing filesystem locks; and
- return the canonical image identity without adding a debug alias or
  launching a container.

`project run` must invoke this service automatically. Ordinary dogfood must not
require a pre-created debug alias or an `images build` command.

Closure evidence:

- focused tests prove strict reuse, missing-image materialization, exact base
  authorization, conflict rejection, and lack of a container launch during
  realization; and
- the existing `images build --type environment` behavior and output remain
  covered.

Recorded result: complete in `c07ae3b`; the full gate passed 155 fast tests at
80% coverage, clean mypy, and all packaging checks without pulling, building,
or launching a real image.

## Stage 2: Generate And Deliver The Checkout Runtime Plan

Status: implemented and validated.

Generate a version-1 `RuntimePlan` from the same component template that
participates in the formation descriptor.

The plan must contain only in-container runtime information:

- the established project destination;
- `/home/devcapsule` as persistent home;
- the host developer UID, GID, and runtime username;
- the component identifier, adapter, and component configuration; and
- the five component-declared state-slot destinations.

It must not contain host source paths, checkout configuration paths,
credentials, secrets, authorization evidence, or personal values. Host source
paths belong only in the Docker mount plan.

Write the plan to a temporary launcher-owned file, make it readable by the
runtime user, and bind-mount it read-only at:

```text
/etc/devcapsule/runtime-plan.json
```

The materialized image must continue to contain only the generic component
template. `project run` must use the image's OCI entrypoint and command:

```text
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]
CMD ["/etc/devcapsule/runtime-plan.json"]
```

It must not override the command with the legacy
`/opt/pycharm/bin/pycharm.sh` path. Temporary plan and identity files must be
removed after the foreground container exits or launch preparation fails.

Closure evidence:

- plan-contract tests cover serialization, redaction boundaries, permissions,
  cleanup, and component-template agreement;
- Docker-plan tests prove the runtime plan is an external read-only mount; and
- image inspection continues to prove no checkout runtime plan is baked in.

Recorded result: complete in the current checkpoint. The full gate passed 161 fast
tests at 80% coverage, clean mypy over 69 files, source/local-PEX smokes, PEX
construction, and three packaging integrations. No real container was
launched.

## Stage 3: Launch The Generic Environment With Explicit Runtime Effects

Status: implemented and validated.

Build a launch plan for the canonical environment while preserving safe
defaults and the validated dogfood behavior.

Required Docker behavior:

- foreground `docker run --rm` lifecycle;
- unprivileged `1000:1000` developer process;
- selected host checkout at the manifest's established container destination;
- persistent home plus the five resolved PyCharm state mounts;
- X11 socket and generated Xauthority delivery;
- generated passwd/group identity files with `/home/devcapsule` as the account
  home;
- the resolved `8589934592` byte Docker memory limit;
- host Docker socket and matching supplementary group only when authorized;
- host networking only when authorized, otherwise Docker bridge;
- development sudo only when authorized; and
- no ambient devices, credentials, SSH agent, host home, or unrelated host
  filesystem access.

The legacy PyCharm launcher may supply reusable low-level identity, X11, mount,
and Docker helpers, but the normal project path must not use its product-path
command override or ambient host-network behavior.

Closure evidence:

- positive tests cover all three runtime authorizations and memory;
- negative tests prove bridge networking, no Docker socket, and no sudo without
  authorization; and
- command inspection proves project, state, X11, identity, and runtime-plan
  mounts are scoped as intended.

Recorded result: focused tests cover resolved 8 GiB memory propagation and
the exact positive and negative Docker argument plans. Inspection of the live
formation-based dogfood capsule confirmed the generic PEX entrypoint and
external runtime plan, unprivileged identity, host-network and Docker-socket
effects, persistent component mounts, foreground lifecycle, and absence of
privileged mode and ambient Gemini. That already-running instance predated the
new checkout memory setting and initially reported `memory.max=max`. Docker's
live resource update then applied 8 GiB to that exact instance; Docker inspect
and cgroup inspection both reported `8589934592`. The dogfood declaration
continues to rely on an explicit checkout value until later-V1 ordinary-value
defaults are implemented; a configured fresh launch plan emits
`--memory 8589934592`. The instance's failing `sudo -n true` is the known
Stage 4 policy gap rather than a Stage 3 propagation failure.

## Stage 4: Activate Authorized Development Sudo Without Rebuilding The Base

Status: implemented and fully validated.

The existing v021 image contains `sudo` but no
`/etc/sudoers.d/ide-sudo` policy. Do not make sudo ambient and do not require a
new base merely for this dogfood checkpoint.

External v021 dogfood confirmed that configuration and resolution are working:
the selected checkout's generated TOML contains
`[authorization] development-sudo = true`. The launch path currently converts
that value only into `ENABLE_SUDO=1` and supplementary group `44000`; the
generic runtime does not consume the legacy flag, and the image has no
`NOPASSWD` sudoers entry. Consequently, `sudo COMMAND` prompts for a password.
This is the exact Stage 4 gap, not an authorization or resolution failure.
The misleading enabled banner, reproduction, security constraints, and close
criteria are tracked in
`implementation-notes/bugs/2026-08-03-authorized-development-sudo-misreported.md`.

When and only when `development-sudo true` is resolved, the launcher should:

- generate a narrowly scoped temporary sudoers policy for the runtime
  development group;
- mount it read-only under `/etc/sudoers.d/`;
- add the authorized supplementary group;
- retain the writable-root behavior required for meaningful in-container
  administration; and
- clean up the temporary policy after exit or failure.

Without authorization, do not mount a sudoers policy, do not add the group,
retain the stricter capability/no-new-privileges profile, and keep the root
filesystem read-only where compatible with the launch mode.

Closure evidence:

- Docker-plan tests cover positive and negative policy delivery;
- the positive host check is `sudo -n true`; and
- the negative host check confirms passwordless sudo is unavailable when not
  authorized.

Recorded result: focused tests cover exact policy content and modes, the
constrained ownership helper, read-only delivery, truthful banner ordering,
the unauthorized plan, actionable helper failure, and normal/failure cleanup.
A disposable container using the exact v022-derived image and generated
account-file contract passed `sudo -n true` and returned `0` from
`sudo -n id -u`; the root-owned policy was then removed. The already-running
authorized v022 capsule was repaired ephemerally with the same policy and
passes both checks.

On 2026-08-05, a fresh formation-based `project run` from exact source
revision `a33988a24a91ef382c1c5c6265ba2a34762ba115` completed the pending
host validation. Docker inspection showed the mapped `1000:1000` user,
supplementary group `44000`, writable root, no privileged mode, and the
generated policy mounted read-only. Inside the capsule the policy was
`root:root` mode `0440`, contained the expected group-scoped rule,
`sudo -n true` returned zero, and `sudo -n id -u` printed `0`. A disposable
run of the same materialized image with the unauthorized read-only,
capability-dropped, `no-new-privileges` profile had no policy and rejected
`sudo -n true`. Together with the positive/negative Docker-plan and cleanup
tests, this fully validates Stage 4. At that point Stages 5 and 8 still owned
the broader second-checkout lifecycle and persistence acceptance, not sudo
activation. That broader outcome was subsequently accepted manually under the
scope decision below.

## Stage 5: Align The Second-Checkout Acceptance Script

Status: manual outcome validated; scripted implementation waived by the product
owner on 2026-08-05.

The product owner is running DevCapsule satisfactorily from the established
second checkout inside the private monorepo. Together with the live Docker
inspection recorded in Stages 3 and 4, this supplies the useful functional
evidence that the laptop-specific script was intended to collect. Updating and
rerunning that script would spend substantial effort on a one-workstation
harness with marginal additional confidence.

The obsolete `devcapsule/tests/manual/v1-second-checkout-dogfood.sh` is removed.
This is an explicit scope decision, not a claim that the old script itself
passed. Its intended portable coverage is transferred to the later V1
orchestrated E2E task below.

## Stage 6: Repository Validation From Committed Code

Status: complete for this functional checkpoint.

The focused fast-test audit found no missing Stage 1-through-4 behavior that
would be usefully covered by another mocked test. Existing tests cover:

- canonical realization reuse, materialization, exact authorization, local
  image-ID pinning, retag/conflict rejection, and no launch after failure;
- the resolved-project handoff from `project run` into canonical realization
  and launch;
- runtime-plan serialization, host-data redaction, component-template
  agreement, read-only delivery, OCI command preservation, and normal/failure
  cleanup;
- positive memory, network, Docker-socket, state-mount, and development-sudo
  propagation plus the safe unauthorized Docker plan; and
- sudo policy content, modes, constrained ownership preparation, banner
  ordering, actionable failure, and cleanup.

On 2026-08-05, `cd devcapsule && .venv/bin/python -m nox -s tests` passed all
182 selected fast tests at 81% statement/branch coverage. The earlier runtime
implementation gate also passed source and PEX smokes, PEX construction,
integration tests, clean mypy, and the same fast suite. The remaining gap is a
real Docker/process/project-orchestration boundary and therefore belongs in the
later E2E task rather than another fast test.

This closeout changes documentation and removes an obsolete host-only manual
script; it does not change runtime code, packaging inputs, image recipes, or
component artifacts. It may be committed without rebuilding the PEX, base
image, or materialized environment. The validated v023 artifacts deliberately
continue to identify runtime source revision
`a33988a24a91ef382c1c5c6265ba2a34762ba115`; the later documentation-only
commit must not be presented as their embedded source revision.

## Stage 7: Make The Revision Available To The External Clone

Status: complete for the runtime checkpoint.

The external second checkout ran exact runtime revision
`a33988a24a91ef382c1c5c6265ba2a34762ba115`, which was available on
`origin/wip/local-pycharm-materialization` and is embedded in the v023 base and
materialized environment. The documentation-only closeout commit can follow
the normal publication workflow and does not require rebuilding those images.

## Stage 8: External Dogfood Validation

Status: manually validated and accepted by the product owner on 2026-08-05.

Sustained satisfactory work from the second checkout validates the useful IDE,
project, state, lifecycle, Docker, sudo, and selected Codex behavior. Docker
inspection independently confirmed the v023-derived canonical image, generic
PEX entrypoint, external read-only runtime plan, unprivileged runtime user,
expected project and component-state mounts, explicit host network and Docker
socket, non-privileged container, automatic removal, and the authorized
development-sudo policy. The unsupported Gemini CLI remained absent.

The inspected live container reported `HostConfig.Memory=0`, not the planned
8 GiB limit. The product owner accepts that discrepancy for this checkpoint;
it is transferred to the later V1 memory-configuration task below rather than
silently recorded as verified. Scripted temporary-checkout repetition is also
transferred to the later orchestrated E2E task.

## Later V1 Task: Memory Configuration And Ordinary-Value Defaults

The accepted v023 dogfood container reported `HostConfig.Memory=0`. Existing
fast tests prove that an explicit checkout value of `8GiB` resolves to
`8589934592` bytes and reaches the Docker argument plan, but the running second
checkout did not have that effective value. Address this later in V1 rather
than reopening the accepted dogfood checkpoint.

Add a generic, schema-validated `default` field to ordinary project
configuration declarations. A committed default is an effective safe value
when the developer has not selected a checkout-specific value; `config set`
must override it. Resolution should record the effective value and derive its
curated runtime effect, while `config list` distinguishes defaulted and
overridden values. A changed default must stale prior resolution through the
manifest digest.

Defaults apply only to ordinary values. They must not grant host authorization,
select secret sources, or create filesystem/socket/device bindings. After this
contract is implemented, this repository should declare `default = "8GiB"`
for `runtime.memory-limit`, so normal dogfood launches receive the limit unless
the developer opts into another valid value. The V1 task must also prove with
Docker inspection that the effective default or checkout override reaches both
`HostConfig.Memory` and `/sys/fs/cgroup/memory.max`, and that an explicit
checkout override retains precedence.

This follow-up belongs later in V1 and does not block this manually accepted
functional dogfood checkpoint.

## Later V1 Task: Orchestrated Multi-Project E2E

Replace the retired laptop-specific script with a fuller, explicitly invoked
E2E orchestrator. It must exercise production orchestration rather than encode
the current workstation's personal paths or state.

The E2E should:

- select exact repository revisions and create DevCapsule plus representative
  project checkouts beneath a unique temporary root;
- use isolated XDG configuration, data, state, cache, and runtime roots so it
  cannot read or modify real checkout records, personal state, or credentials;
- build the selected base image when required, otherwise strictly inspect and
  reuse a matching managed base, then automatically materialize canonical
  environments through normal project commands;
- configure ordinary values and state bindings, grant only the exact
  authorizations required by each case, resolve, run, and inspect the running
  containers;
- cover at least the DevCapsule dogfood declaration and additional
  representative project declarations, including both authorized and safe
  unauthorized launch plans;
- inspect base/materialized identity, generic OCI entrypoint and command,
  external read-only runtime plan, absence of a baked checkout plan, project
  and state mounts, runtime user, network, memory, Docker access, sudo policy,
  privilege boundaries, foreground lifecycle, and automatic removal;
- verify a second launch where persistence is part of the contract;
- use unique names and ownership labels, emit sanitized diagnostics, and
  deterministically clean temporary checkouts, XDG roots, containers, and
  test-owned images on success, failure, or interruption; and
- never delete or mutate unrelated Docker resources, project source,
  persistent personal state, or credential stores.

GUI usability, third-party license prompts, and real credential login may
remain separately manual, but the orchestrator should make all Docker-visible
behavior machine-verifiable. This is a substantial later V1 task and is not a
condition for closing the present dogfood plan.

## Completion Criteria For The Next Functional Stage

This plan is complete by product-owner acceptance because all of the following
are true:

- normal `project run` realizes the locked canonical environment automatically;
- the materialized image remains checkout-neutral;
- the external read-only runtime plan drives the generic PEX entrypoint;
- the committed Linux lock selects the published v023 base by immutable
  registry digest;
- the inspected bindings and authorizations have the intended Docker effects;
- safe defaults remain effective when authorizations are absent;
- the implementation full gate passed and the closeout fast suite passes all
  182 selected tests;
- the user confirms the resulting PyCharm capsule is a workable replacement
  for the current dogfood environment, within the intentional path, version,
  and unsupported-Gemini differences; and
- the unverified 8 GiB live-memory criterion and retired scripted repetition
  are explicitly preserved as later V1 tasks rather than misreported as
  passing.

## Next Task

Review the current gaps to V1, and decide on a project plan to take us to V1.

## V1 IDE Configuration Sequencing And Starter Catalog

The product owner has clarified that repairing the VSCodium proof point
represented by `codium_with_claude` is a must-have V1 outcome. It is not,
however, the next abstraction slice. The v0 proof point deliberately took
shortcuts to reach a working second IDE, and its configuration-specific
launcher and currently filed bugs must not become the template for the V1
framework merely because they already exist.

V1 work should first settle the end-user configuration experience and the
reusable component, configuration, materialization, state, authorization, and
runtime abstractions using the better-understood PyCharm path. Once those
contracts are coherent, the project must circle back and implement at least
one VSCodium-based configuration through them, including repairing or
replacing the current `codium_with_claude` proof point. Only then should the
old Codium bugs be reproduced against the resulting V1 path: behavior that
still fails is a real V1 defect to fix, while bugs tied only to the retired v0
launcher can be closed as obsolete with evidence. In particular, this
sequencing does not waive V1's safe-default requirement; no supported Codium
configuration may retain ambient sudo, writable root, host access, or another
unapproved isolation relaxation.

V1 should also ship a small curated starter catalog of IDE configurations and
matching demonstration projects. Its purpose is not to claim exhaustive IDE
support. It gives new users quick, low-commitment experiments that demonstrate
the configuration model, component selection, persistence, and explicit host
authorization before they create more advanced configurations of their own.
The catalog is also the product proof that configuration authoring is
genuinely reusable and sufficiently self-service rather than another set of
hard-coded launchers. The exact catalog entries and count remain for the V1
plan to select.

## Later Functional Tasks Carried Forward

The following implementation work is deliberately carried forward rather than
left as an open condition on this landed dogfood stage. The V1 gap review must
classify, prioritize, combine, or defer it explicitly:

- the disposable multi-project E2E orchestrator specified above;
- ordinary-value defaults and live memory-limit verification specified above;
- PyCharm-led closure of the shared user experience and configuration/component
  abstractions, followed by a VSCodium implementation through those contracts
  and fresh triage of the old `codium_with_claude` bugs;
- a small curated starter catalog of IDE configurations and matching demo
  projects that proves the supported authoring path is self-service;
- final external Codex CLI, ACP, authentication, and persistence validation;
- the accepted JCEF workaround's external GUI validation;
- component runtime-path and ecosystem-aware project-bootstrap follow-ups;
- official semantically versioned V1 artifact publication;
- GPU/device authorization and specialized CUDA validation;
- Docker-in-Docker, native-debugging, raw-Docker-argument, and the Codium
  runtime behavior that remains applicable after the V1 reimplementation; and
- safe image/cache lifecycle management and stronger supply-chain provenance.

The following remain explicitly unsupported or optional rather than implicit
closure work:

- any Gemini CLI installation, optional component, capability, state migration,
  authentication, or validation;
- Antigravity or another optional agent component;
- general secret providers or SSH-agent forwarding;
- broader alternative-environment work beyond the V1 starter catalog.
