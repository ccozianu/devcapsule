---
date: 2026-08-01
capture-mode: detailed
requested-by: user
scope: DevCapsule V1 configuration experience, image workflow, and initial implementation
related:
  - docs/decisions/d-0004-configuration-resolution-and-guided-run.md
  - devcapsule/docs/v1-user-experience.md
  - devcapsule/tests/manual/v1-second-checkout-dogfood.sh
  - devcapsule/README.md
  - CURRENT-STATUS.md
---

# Session Record: D-0004 Configuration And Images CLI

## Record Status And Limits

The user explicitly requested repository persistence for this consequential
session before manually testing the new image commands from the host.

This is a detailed chronological reconstruction, not a verbatim IDE transcript.
It preserves user choices, rationale, representative commands, implementation
outcomes, and validation evidence. It omits hidden model reasoning, repetitive
tool output, and credential-sensitive material. No known secret value appeared
in the recorded discussion.

Canonical decisions, requirements, current status, and user documentation
remain authoritative over this historical record.

## Starting Point

The session began by asking whether D-0004, `Configuration Resolution And
Guided Run Experience`, still required joint finalization. Repository review
established that:

- D-0001 had already adopted the capability-first model;
- D-0004 remained `proposed` and required human review;
- V1 was intended to retain an explicit configuration-resolution boundary;
  and
- the current implementation still used transitional commands and the local
  `mycodespace.ai/pycharm:debug-v018` image.

The user and agent agreed to review D-0004 by separating its durable product
decision from implementation details that could become follow-up contracts.
D-0004 was not adopted during this session.

## V1 Configuration Loop

The user proposed a clean-clone flow in which developers make several local
configuration choices and finish with holistic resolution. The refined and
confirmed model became:

```text
clone
  -> make zero or more developer-owned choices
  -> validate each choice when recorded
  -> resolve and validate the complete effective configuration
  -> run
```

Zero operations is important: a batteries-included project whose required
inputs all have safe defaults should not require fictitious setup commands.

Three semantic command families were selected as the V1 working direction:

```text
devcapsule config set NAME VALUE
devcapsule config bind NAME PROVIDER
devcapsule config authorize NAME VALUE
devcapsule config resolve
devcapsule run
```

Their responsibilities were distinguished deliberately:

- `set` records an ordinary developer-owned value. The recurring example was
  `devcapsule config set runtime.memory-limit 8GiB`.
- `bind` maps a logical project/component resource to a developer-owned
  provider. The first implementation milestone needs only existing host
  directories, such as
  `devcapsule config bind pycharm/system --host-directory PATH`.
- `authorize` records a security-sensitive host decision. Examples included
  Docker-daemon access, host networking, and development sudo.
- `config resolve` is the explicit completion signal. It validates
  completeness, cross-field compatibility, the lock, identity, paths, policy,
  state bindings, authorization, and later secret bindings. It writes a fresh
  inspectable resolution but does not download, build, mount, retrieve secrets,
  grant recommendations, or launch.
- `run` requires a fresh resolution, realizes it, and launches. A missing or
  stale resolution remains actionable rather than being regenerated silently.

The persistent commands write the developer-owned checkout file, not the
repository and not generated resolution:

```text
$XDG_CONFIG_HOME/devcapsule/projects/<encoded-creator>/<encoded-slug>/devcapsule.checkout.toml
```

When `XDG_CONFIG_HOME` is absent, the root is `~/.config`. Successful mutation
output and documentation must show the actual file. It remains mode `0600` and
contains no secret values.

## Binding Scope

The first dogfood milestone deliberately supports only existing-host-directory
bindings for component state. Managed state is the safe default and requires no
binding command.

Potential later binding providers were recorded without treating them as V1
commitments:

- host files for non-secret configuration or certificates;
- environment variables, narrowly scoped files, keychains, or password-manager
  entries as secret sources;
- local agent sockets;
- named developer profiles; and
- alternate storage such as Docker volumes.

Devices, Docker-daemon access, host networking, privilege changes, and port
publication are authorizations, not generic bindings. Every later provider
requires a readiness check, delivery contract, inspection behavior,
noninteractive semantics, and redaction rules where applicable.

## Target V1 User Documentation

The existing design draft at `devcapsule/docs/v1-user-experience.md` was
expanded to document:

- the exact checkout-file location and ownership;
- zero-or-more configuration operations;
- memory-limit, state-binding, and host-authorization examples;
- immediate versus holistic validation;
- the initial and potential provider catalog; and
- a clear warning that this is target V1 behavior rather than the current
  transitional interface.

D-0004 was updated in parallel so the user narrative and architectural working
decision describe the same boundaries.

## Second-Checkout Dogfood Acceptance Test

The user requested an ambitious grounding test: clone the project on the same
laptop at:

```text
~/work/provisional/costin3/myProjects/devcapsule
```

and run it under a distinct checkout identity.

The agent inspected the committed manifest/lock, the developer-owned host
checkout configuration, and running container `322ca969a6d9`. Sensitive
environment values were not dumped. The observed legacy runtime had:

- image `mycodespace.ai/pycharm:debug-v018` with immutable image ID beginning
  `7dfb761eee8b`;
- the PyCharm-specific Bash entrypoint;
- user `1000:1000`;
- project destination `/workspace/301e4208ef81-ChatGPT_Codex`;
- shared legacy home, PyCharm config, and plugins;
- checkout-specific PyCharm system, log, and cache directories;
- explicit host Docker and development sudo;
- the known temporary host-network relaxation; and
- foreground auto-remove lifecycle.

The inspection also clarified which values are launcher outputs rather than
developer configuration: X11/Xauthority mounts, generated account files, host
Docker group IDs, and selected GPU runtime.

The current implementation stores only one default checkout record per
portable project identity. A second canonical checkout path therefore exposed
a real implementation gap. The proposed one-time registration form became:

```text
devcapsule --project /path/to/second/checkout \
  config checkout register costin3-devcapsule
```

After registration, canonical-path discovery selects the named record without
repeating its label. The original checkout record must remain byte-for-byte
unchanged.

The executable acceptance script was created at
`devcapsule/tests/manual/v1-second-checkout-dogfood.sh`. It specifies:

- a fresh clone and full build gate;
- named checkout configuration/resolution records;
- an 8 GiB container memory setting;
- explicit reuse of legacy home, config, and plugins after stopping the first
  capsule;
- new checkout-specific system, log, and cache directories;
- persisted Docker, network, and sudo authorizations;
- holistic resolution;
- live Docker-plan inspection;
- foreground/auto-remove checks; and
- a second launch for persistence validation.

The script is intentionally red until the target V1 commands and named
checkout behavior exist.

## Why v019 Is Required

The discussion initially considered reusing v018 while implementing host-side
configuration. The user correctly observed that the in-container entrypoint
would likely evolve with the configuration mechanism and argued that assuming
a v019 checkpoint was prudent.

Inspection confirmed that v018 is a roughly 5.5 GB monolithic image using
`/usr/local/bin/entrypoint.sh`, with no embedded DevCapsule PEX identity and no
generic runtime-plan command. It remains the known-good legacy comparison, not
the image under test for the next slice.

The v019 checkpoint must use:

```text
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]
CMD ["/etc/devcapsule/runtime-plan.json"]
```

and exercise the Python runtime contract in
`devcapsule.container_runtime.entrypoint`.

## Local Image Naming And Build Workflow

The canonical local environment-image name was settled as:

```text
devcapsule-local-<component>:<materialization-identity>
```

Project identity is intentionally absent. Projects with identical immutable
formation inputs may reuse an image without sharing source, configuration,
authorization, or state. A debug name such as
`devcapsule-local-pycharm:debug-v019` is an alias only; the canonical identity
remains content-addressed.

The image commands were grouped under a new `images` category. Action
subcommands were preferred over mutually exclusive `--list`/`--new` flags:

```text
devcapsule images list [--include-legacy]
devcapsule images build --type base --tag IMAGE [options]
devcapsule --project PATH images build --type environment [options]
```

Only listing and base building were implemented in this session. Environment
building remains the next image-formation slice.

### Base Contract

`images build --type base` builds one reusable, JetBrains-free OCI development
runtime. The initial contract includes Ubuntu 24.04, Python 3.12, compiler and
debugger tooling, Git/SSH and diagnostics, Docker client/buildx/Compose/daemon
binaries, GUI runtime libraries, `tini`, `gosu`, non-authorized sudo, the
recipe-selected Node/npm/Gemini baseline, and exactly one DevCapsule PEX.

It deliberately excludes the runtime plan, IDE/vendor artifacts, project
source, project configuration/lock, developer state, credentials, host mounts,
host authorization, and license acceptance. Consequently, the bare base is not
a runnable project environment.

The briefly proposed `--pull` option was removed at the user's request as
low-value complexity. The fixed behavior is to reuse the selected local root
image when present and otherwise obtain its registry reference. The immutable
identity actually used is recorded.

## Managed-Image Identification

Names are a human convention, not the classifier used by `images list`. The
mandatory inclusion and interpretation labels became:

```text
devcapsule.image.managed=true
devcapsule.metadata.version=1
devcapsule.image.kind=base|materialized
```

Base and materialized images also carry kind-specific recipe and formation
identities. Listing is read-only, queries only the local Docker store, groups
aliases by image ID, keeps unknown/malformed managed metadata visible, and
excludes old `devcapsule.configuration` images unless `--include-legacy` is
given. Labels classify local objects but do not establish trust; lock and
formation identities are still verified before reuse.

## Implementation Completed In This Session

The user authorized implementation of only:

```text
devcapsule images list
devcapsule images build --type base
```

The implementation added:

- `devcapsule/devcapsule/commands/images.py` for the new command group;
- `devcapsule/devcapsule/image_metadata.py` for labels, local inventory,
  classification, alias grouping, and display records;
- mandatory managed metadata in base planning;
- matching generic metadata in PyCharm materialization planning;
- PEX self-selection when base build is invoked from a PEX, with explicit
  `--pex` required from source/editable execution;
- source and PEX smoke coverage for both commands;
- focused base, materialization, inventory, and CLI tests; and
- current interface documentation in `devcapsule/README.md`.

The top-level `build-base` command was initially left as a transitional
compatibility surface; a later follow-up in this session removed it in favor of
the sole `images build --type base` contract.

## Validation Evidence

The focused test run passed 32 tests. The complete fast suite then passed 87
tests at 79% aggregate statement/branch coverage, and mypy reported no issues
across 62 source files.

The full gate passed:

```text
cd devcapsule
.venv/bin/python -m nox -s build
```

It covered compilation, shell syntax, mypy, all fast tests, source command
smokes, PEX construction, built-PEX command smokes, and the PEX integration
test.

A live read-only source and built-PEX check against the local Docker store
produced no V1-managed images in the default view and correctly showed v018 as
legacy with `--include-legacy`:

```text
KIND    CANONICAL                          IMAGE-ID      COMPONENT
legacy  mycodespace.ai/pycharm:debug-v018  7dfb761eee8b  pycharm
```

No real base image was built during this session. The large host build was
deliberately left as the next manual validation checkpoint.

## Open Work At Session Record Time

1. From a host terminal, build and inspect
   `devcapsule-base:debug-v019` through the new PEX command.
2. Review any build/runtime issues before implementing
   `images build --type environment`.
3. Continue the named-checkout and `config set`/`bind`/`authorize`/
   `resolve` implementation needed by the second-checkout acceptance script.
4. Build/materialize the v019 environment and run the second-checkout dogfood
   test.
5. Complete the remaining D-0004 human review. D-0004 remains proposed.

Unrelated existing `.idea` changes were observed throughout and deliberately
left untouched.

## Follow-Up: Explicit Base-Build Networking

Before running the new command from the host, the user requested an explicit
host-network build option:

```text
devcapsule images build --type base --network host ...
```

The implemented option accepts `default`, `host`, or `none`, defaulting to
`default`. The CLI forwards the selected string through the base builder to the
existing Docker buildx backend. For `host`, that backend also supplies
BuildKit's required `network.host` entitlement. Documentation emphasizes that
this is a build-time isolation relaxation and does not authorize host
networking for later runtime containers.

Focused CLI/builder tests passed, mypy remained clean across 62 source files,
the complete fast suite passed 88 tests, the full Nox build gate succeeded, and
the rebuilt PEX help surface displayed the new option.

## Follow-Up: GPU Base Scope And Testing

The user identified NVIDIA GPU development as a credible base-image need and
clarified that NVIDIA CUDA E2E testing is readily available on the maintainer's
NVIDIA laptops. At this point in the discussion the recipe had not yet been
selected for V1; the later follow-up below selects it as a WIP V1 recipe with a
release-blocking validation task. This agent session runs inside a container
without GPU access, so it cannot perform that host validation directly. AMD
ROCm and other GPU families require interested partner or cloud test
infrastructure and are outside the required V1 scope. A GPU recipe remains
distinct from runtime GPU-device authorization: selecting CUDA tooling in an
image must not grant a launched container access to a GPU.

GitHub-hosted Linux GPU larger runners provide one Tesla T4 with 16 GB VRAM,
four CPUs, 28 GB RAM, and 176 GB SSD. Current GitHub pricing is $0.052 per
minute, with no charge while the configured runner is idle. Larger runners
require a GitHub Team or Enterprise Cloud organization, a valid payment method,
and a positive Actions budget; included Actions minutes do not apply, including
for public repositories.

Dockerized CUDA validation is feasible rather than merely inferred from the
hardware specification. LightGBM's current successful CUDA workflow runs an
NVIDIA CUDA job container on a GitHub-hosted Linux GPU larger runner, passes
`--gpus all`, and executes `nvidia-smi`. This proves GitHub's Docker job-
container path; a short provisioning spike should still prove direct
host-level `docker run --gpus all` through DevCapsule before treating the full
nested launch path as supported. A future minimal DevCapsule check can then
build or pull one pinned CUDA-capable image, verify its labels and entrypoint,
run it with explicit GPU authorization, execute `nvidia-smi` plus one small
CUDA computation, and verify the corresponding no-authorization failure. At
the published rate, a 15-minute run costs about $0.78, 30 minutes costs $1.56,
and 60 minutes costs $3.12, excluding the required GitHub plan.

Sources consulted on 2026-08-01:

- <https://docs.github.com/en/actions/reference/runners/larger-runners>
- <https://docs.github.com/en/billing/reference/actions-runner-pricing>
- <https://github.com/lightgbm-org/LightGBM/blob/main/.github/workflows/cuda.yml>

## Follow-Up: Two Implemented Base Recipes

The user selected two base-build recipes for the V1 command surface:

```text
devcapsule images build --type base --recipe ubuntu-24.04
devcapsule images build --type base --recipe nvidia-cuda-devel
```

`ubuntu-24.04` is the default and retains the existing Ubuntu 24.04 developer
baseline. `nvidia-cuda-devel` starts from
`nvidia/cuda:12.8.1-devel-ubuntu24.04` and composes the same developer baseline
onto NVIDIA's CUDA development image. The registry manifest was confirmed to
exist for both amd64 and arm64 before selecting the tag.

The CUDA recipe is explicitly WIP in its image labels, build report, and CLI
warning. Its specialized positive and negative GPU E2E validation on the
maintainer's NVIDIA laptop is a V1 release blocker, recorded at
`devcapsule/implementation-notes/2026-08-01-nvidia-cuda-base-recipe-validation.md`.
AMD ROCm and other GPU families remain outside required V1 scope because no
local test hardware is available.

Focused recipe, CLI, and image-inventory tests passed. The full Nox build gate
then passed with clean mypy over 62 source files, 92 fast tests at 79%
statement/branch coverage, source and rebuilt-PEX command smoke tests, PEX
construction, and the PEX integration test. The built-PEX help surface
advertised both recipe choices and the `ubuntu-24.04` default. No real base
image or GPU workload was run in this container session.

## Follow-Up: First NVIDIA Build And Compatibility Removal

The user reported that the first external NVIDIA recipe test succeeded: the
new recipe produced a local NVIDIA GPU base image on an NVIDIA laptop. This is
evidence for successful image formation only; detailed inspection, CUDA
compiler/runtime execution, device-authorization boundaries, and materialized
environment validation remain open in the V1-blocking specialized task.

Because V1 does not need a compatibility layer for this unreleased command
surface, the legacy top-level `build-base` command was removed. The sole
base-build grammar is now:

```text
devcapsule images build --type base ...
```

The post-removal full Nox build gate passed with clean mypy over 61 source
files, 92 fast tests, source and rebuilt-PEX command smokes, PEX construction,
and the PEX integration test. Both top-level help surfaces omit `build-base`.

## Follow-Up: Proposed Project Command Subtree

The user selected a regular project-oriented command tree for the proposed V1
interface:

```text
devcapsule project list
devcapsule project [--path PATH] init
devcapsule project [--path PATH] checkout register NAME
devcapsule project [--path PATH] config ...
devcapsule project [--path PATH] state ...
devcapsule project [--path PATH] lock ...
devcapsule project [--path PATH] run ...
devcapsule project [--path PATH] run-image IMAGE ...
```

An omitted `--path` starts discovery at the current directory and searches
upward for the nearest `.devcapsule/devcapsule.toml`; an explicit path may be
the checkout root or any descendant. The optional positional form `project .`
was rejected as ambiguous with the subcommand name. Click can carry an
unresolved optional path in group context and resolve it only for subcommands
that require an existing declaration, allowing `list` and `init` to have their
appropriate distinct behavior.

`project list` enumerates valid developer-owned checkout records beneath
`$XDG_CONFIG_HOME/devcapsule/projects/`, normally
`~/.config/devcapsule/projects/`. It never scans source trees. Cloning or
initializing a project does not register the checkout; the first persistent
`project config set`, `bind`, `authorize`, or `resolve` operation creates the
record. Missing checkout paths remain listed as `missing` for deliberate
cleanup.

This proposed spelling deliberately replaces D-0001's top-level `devcapsule
run` with `devcapsule project run` if D-0004 is adopted. The current executable
CLI remains transitional; no project-subtree implementation was performed in
this documentation update.

The user then placed the ultimate developer escape hatch under the same
project tree. `project run-image IMAGE` is lock-independent but still
project-scoped because it mounts source and applies explicit state and host
choices. If a declaration is discoverable it may use declared defaults without
reading the lock; otherwise the selected path or current directory is used as
the source directly.

## Follow-Up: Automatic Cross-Project Image Reuse

The user confirmed that several projects should automatically share one local
materialized environment whenever their immutable formation inputs are
identical. A project lock selects those inputs; its project identity and full
lock-file digest do not own or salt the image identity.

D-0004 and the V1 user journey now define a versioned RFC 8785 canonical
formation descriptor containing platform, immutable base identity, every
component identity and artifact digest, materialization recipe parameters, and
the generic component runtime-template/entrypoint contract. Project identity,
checkout paths, source, local resolution, project mounts, UID/GID, state,
credentials, authorization, run-once choices, and aliases are excluded. The
descriptor's full SHA-256 is the reuse authority.

Before reuse, DevCapsule must verify the canonical image's full identity, base,
recipe, and complete component metadata. A malformed or conflicting canonical
tag fails with cleanup guidance rather than being silently used or overwritten.
Projects cannot force sharing when formation descriptors differ. The immutable
image carries only a generic component runtime template; `project run` supplies
the checkout-specific launch plan read-only from outside the image.

The current materialization helper does not yet meet this contract: its
identity is a simple JSON list of base, one artifact, and recipe version; it
returns immediately from an `image_exists` predicate; and it bakes the current
runtime-plan file. The `--type environment` implementation must replace those
shortcuts with the canonical descriptor, descriptor-label verification, and an
external checkout-specific launch plan.

## Follow-Up: Project Command Tree Implemented

The project syntax was implemented before beginning `images build --type
environment`. The top-level `init`, `lock`, `config`, `state`, `run`, and
`run-image` command modules were deleted without compatibility aliases. The
implemented tree is:

```text
devcapsule project [--path PATH] list
devcapsule project [--path PATH] init
devcapsule project [--path PATH] checkout register NAME
devcapsule project [--path PATH] config resolve
devcapsule project [--path PATH] state adopt ...
devcapsule project [--path PATH] lock ...
devcapsule project [--path PATH] run ...
devcapsule project [--path PATH] run-image IMAGE ...
```

The group carries one lazy path context. Existing-checkout commands discover
upward from that path or the current directory; `init` treats it as the target;
and `run-image` falls back to a plain source directory when no declaration is
discoverable. Clean `config resolve` now creates the safe default checkout
record. Named registration and subsequent path-based selection use distinct
`checkouts/NAME.checkout.toml` and `.resolved.toml` files.

`project list` enumerates valid records only from
`$XDG_CONFIG_HOME/devcapsule/projects/`, never source trees, and reports ready,
missing, or uninitialized paths. Tests cover clean registration, discovery from
a descendant, named second-checkout selection, missing records, no source-tree
scanning, the expert launcher, and removal of old top-level commands.

The full Nox build gate passed with clean mypy over 57 source files, 95 fast
tests at 79% statement/branch coverage, source and rebuilt-PEX project help
smokes, PEX construction, and the PEX integration test. This refactor did not
launch a host container. The next task is `images build --type environment`.
