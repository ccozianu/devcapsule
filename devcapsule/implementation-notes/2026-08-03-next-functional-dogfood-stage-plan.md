# Plan: Reach The Next Functional Dogfood Stage From `wip/local-pycharm-materialization` At `b5d42e8`

Status: active implementation plan
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

Current stage: Stage 3, explicit runtime effects.

Recommended source revision for the next v021 dogfood base:

```text
5401ce3506c0a8a63bfef40f4f9ef18d2b987436
```

That revision contains the completed Stages 0 through 2 and was used as both
the PEX source revision and the asserted
`images build --type base --source-revision` value. The resulting v021 base was
built, inspected, scanned, and published as immutable registry digest
`sha256:cd1a0e713e515234ef438c0502786353ec1678d2efd67b61a0bae6baf9fdc51e`.
The committed platform lock now selects that digest; each checkout must refresh
its exact base-image authorization before resolving again.

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

No real image was pulled, built, or launched by the automated work for Stages 0
through 2. The v021 base has since been built and published externally. The
next action is to retry Stage 3 with the refreshed lock and authorization,
verifying and completing the generic Docker launch plan and its positive and
negative authorization behavior before implementing the development-sudo
policy in Stage 4.

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
External acceptance must confirm the CLI is ready on `PATH`, terminal or
JetBrains authentication persists, ACP uses the mounted component state, and
a second launch retains it. Real artifact acquisition, API-key login, and the
GUI/ACP restart check remain external validation work.

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
4. authorize the exact v021 base digest, host Docker socket, host networking,
   and development sudo;
5. resolve an inspectable checkout plan without downloading, building, or
   launching;
6. run the project, automatically reusing or materializing its canonical
   PyCharm environment;
7. launch PyCharm through the generic PEX runtime with an external read-only
   checkout plan; and
8. exit and launch again with settings, plugins, login state, and intended
   checkout-specific state retained.

The new capsule should reproduce the useful behavior of the running v018
dogfood environment while deliberately using the agent-neutral v021 image and
new configuration mechanics. Different host checkout/state paths and the
absence of Gemini CLI are intentional.

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
require a pre-created `debug-v020` alias or an `images build` command.

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

Status: current next stage; not started.

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

## Stage 4: Activate Authorized Development Sudo Without Rebuilding v021

Status: externally reproduced gap; implementation pending.

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

## Stage 5: Align The Second-Checkout Acceptance Script

Update `devcapsule/tests/manual/v1-second-checkout-dogfood.sh` after the runtime
implementation is complete.

Required script changes:

- default to `$HOME/work.provisional/costin3/myProjects/devcapsule` and the
  matching dotted state root;
- support the already-existing clone instead of requiring the checkout path to
  be absent;
- require a clean checkout at an explicit tested revision;
- stop defaulting silently to `main` while the implementation lives on a WIP
  branch;
- remove the debug-image prerequisite and let `project run` prove
  canonical reuse or automatic materialization;
- retain the distinct named checkout and original-record integrity checks;
- inspect the external runtime-plan mount and require `RW=false`;
- verify the image still contains no baked checkout runtime plan;
- verify Gemini CLI is absent only as an unsupported-software regression
  guard; and
- retain first-launch, foreground-exit, automatic-removal, and second-launch
  persistence checks.

The script must remain host-only and non-destructive. It may create missing
checkout-specific system/log/cache directories, but it must not delete the
clone, persistent state, existing checkout records, or Docker images.

## Stage 6: Repository Validation From Committed Code

Before external launch:

1. add focused fast tests for Stages 1 through 4;
2. smoke the source and PEX command surfaces;
3. run `cd devcapsule && .venv/bin/python -m nox -s build`;
4. commit the coherent implementation;
5. rerun the full gate on the clean committed tree so the revision-bearing PEX
   embeds the exact tested `HEAD`; and
6. inspect that PEX with `devcapsule.pex version --json`.

No Docker GUI launch belongs in the normal automated gate. Existing explicit
Docker E2E coverage should be extended only where it remains disposable and
does not require X11 or personal state.

## Stage 7: Make The Revision Available To The External Clone

At the time this plan was written, the baseline branch was two commits ahead
of `origin/wip/local-pycharm-materialization`. Push the tested branch or merge
the tested commits into the branch selected by the external clone. Then update
the external clone to the exact revision and confirm it is clean before
building its PEX.

Do not claim a fresh-clone result while the clone is running older `main` code
or an unpublished local-only revision.

## Stage 8: External Dogfood Validation

Run the aligned acceptance script from the host after closing the current
`devcapsule-dogfood-v1` container. The shared home, PyCharm config, and plugin
directories declare exclusive concurrency and must not be mounted read-write by
both capsules simultaneously. Closing that container also ends the current
in-capsule agent session, so implementation and automated validation must be
complete first.

Inspect the first launched container and confirm:

- the host source is the new clone and its container destination is the
  established project path;
- the canonical v021 materialized image is used;
- the runtime plan is present as a read-only external bind mount;
- persistent home, shared config/plugins, and new system/log/cache sources map
  to the declared destinations;
- `HostConfig.Memory` is 8 GiB;
- the runtime user is unprivileged;
- host networking, Docker socket access, and development sudo appear only
  because this checkout authorized them;
- PyCharm remains foreground-attached below `tini` and the container uses
  automatic removal;
- Gemini CLI is not installed or configured;
- normal editing, the build/test workflow, `docker version`, `sudo -n true`,
  and one supported IDE-agent interaction work; and
- closing PyCharm removes the container.

Launch a second time and confirm settings, plugins, relevant login state, and
checkout-specific state continuity. Record any JetBrains license or agreement
prompt separately; file persistence does not guarantee uninterrupted
third-party authentication or terms acceptance.

## Completion Criteria For The Next Functional Stage

This plan is complete when all of the following are true:

- normal `project run` realizes the locked canonical environment automatically;
- the materialized image remains checkout-neutral;
- the external read-only runtime plan drives the generic PEX entrypoint;
- all resolved values, bindings, and authorizations have the intended Docker
  effects;
- safe defaults remain effective when authorizations are absent;
- the full clean-tree Nox gate passes against the committed implementation;
- the external existing-clone acceptance test passes twice; and
- the user confirms the resulting PyCharm capsule is a workable replacement
  for the current dogfood environment, within the intentional path, version,
  and unsupported-Gemini differences.

## Outside This Stage

Do not pull these tasks into the next dogfood closure unless a discovered
blocker requires an explicit scope decision:

- any Gemini CLI installation, optional component, capability, state migration,
  authentication, or validation;
- Antigravity or another optional agent component;
- general secret providers or SSH-agent forwarding;
- Docker-in-Docker, native-debugging, raw-Docker-argument, or complete Codium
  runtime parity;
- GPU/device authorization and specialized CUDA validation;
- official semantically versioned V1 artifact publication; or
- broader image/cache lifecycle management.
