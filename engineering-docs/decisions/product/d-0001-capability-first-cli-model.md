---
id: D-0001
title: Capability-First CLI Model
status: adopted
date-proposed: 2026-07-16
date-decided: 2026-07-23
decided-by: Costin Cozianu
requirements:
  - R-IDE-CONFIG-001
  - R-FRAMEWORK-001
  - R-IMAGE-BUILD-001
  - R-PRODUCT-001
  - R-PRODUCT-002
supersedes:
superseded-by:
---

# D-0001: Capability-First CLI Model

## Context

DevCapsule currently asks users to pick a product configuration by name:

```text
devcapsule CONFIGURATION ACTION [options]
```

This is the accepted model recorded in R-IDE-CONFIG-001 (status:
`implemented`). Two configurations exist: `pycharm` and `codium_with_claude`.

Three pressures make that model hard to carry into V1.

**Configurations are code, and code drifts.** Each configuration is a
hand-written Python class owning its own image spec and launcher. With exactly
two of them, they have already diverged far enough to need a bug record:
`engineering-docs/bugs/devcapsule/2026-07-13-codium-run-option-parity.md`.
Codium is missing Git transport, Docker modes, native debugging, sudo, and
writable-root controls that PyCharm has. That divergence is not an oversight to
be patched; it is the predictable behavior of a design where every
IDE-times-toolchain-times-agent combination is a separate hand-written artifact.

**The declared value proposition is not implemented.** `docs/product/v1-announcement.md`
promises that "the project can declare the IDE surface, runtime profile, state
layout, allowed host resources, and the current project memory in version
controlled files." Only project memory is actually declared today. The other
four live as roughly thirty command-line flags whose correct combination
survives in a developer's shell history. That is the same failure the
announcement's own Problem section indicts: "half-remembered setup steps, and
undocumented assumptions." The flags are the new stale notes.

**Users do not want our products; they want their tools present.** Nobody wants
a Dockerized PyCharm. They want Python, an IDE that understands it, and Docker
to be there when they open the repository. Configuration-first makes the user
translate their need into our catalog. That translation is our job.

Additionally, the announcement commits to project types (`python-cli`,
`python-lib`, `fastapi`, `java-lib`, `quarkus-rest`) via `devcapsule new
--type`. That introduces a second noun competing with configuration, and a bare
verb that already violates R-IDE-CONFIG-001's stated grammar.

Constraints this decision must respect:

- Reproducibility is the core product promise, so whatever is declared must be
  pinnable to exact versions.
- PyCharm must remain the default answer for the capability set
  {python, python-ide, gemini}.
- Gemini CLI is the default agent capability because it can be redistributed
  inside DevCapsule images.
- Docker images are linear layer stacks, not sets. Composition is not union.
- Root documentation stays implementation-agnostic (R-DOCS-001).

## Options Considered

### Option A: Keep the configuration-first model

Users continue selecting `pycharm` or `codium_with_claude` by name. New
combinations become new hand-written configurations.

Cost: every combination is code. The parity bug is the evidence that this does
not survive two configurations, let alone the five project types V1 has already
promised publicly. The announcement's declarative claim stays false, so either
the product or the announcement has to give.

### Option B: Capability-first with a full composition engine

Users declare arbitrary capabilities; a resolver composes any combination on
demand and builds the image.

Cost: this is a dependency resolver with version solving, ordering, and
conflict detection — a package manager. Docker's linear layer model means
arbitrary union has no cheap implementation: multi-stage `COPY` works only for
relocatable trees (like the existing `/opt/node/node-{version}`) and breaks on
apt dependency graphs, `/etc` mutation, and system users. Building this before
V1, with two configurations and unfinished parity, is a multi-year detour.
Resolvers are where package managers go to die.

### Option C: Capability-first declaration with curated bases and add-ons

Users declare capabilities. A curated matrix resolves them to complete base
images and may add pinned, relocatable toolchains from a small certified
catalog. Combinations outside the matrix and catalog fail with an honest
message and a request path rather than being composed arbitrarily.

Cost: the matrix, add-on catalog, and allowed combinations are maintained and
tested by hand. Users who want an uncurated combination wait for us. The first
local materialization may also require substantial downloads.

## Decision

Adopt **Option C**.

Adopted 2026-07-23 by Costin Cozianu after final human-agent review of sections
1 through 9 and the supporting host-backed state model in
`engineering-docs/specifications/product/state-and-persistence.md`.

### 1. Portable project declaration and developer-owned runtime realization

Configuration is a hierarchical key-value tree. Ordinary values are resolved
by applying four layers in increasing order of precedence:

1. workstation configuration, which supplies this developer's defaults for
   every project on the workstation;
2. committed project-global `.devcapsule/devcapsule.toml`, which supplies
   portable values
   for every checkout and workstation instantiating the project;
3. uncommitted project-local configuration owned by this developer on this
   workstation; and
4. run-once command-line values, which are intentionally not persisted.

The last specified ordinary value wins. Policy constraints are not ordinary
values: applicable constraints combine restrictively and a higher-precedence
value cannot silently bypass them.

The committed `.devcapsule/devcapsule.toml` is hand-authored repository
content. It declares portable capabilities, project identity,
container-internal settings, and safe values:

```toml
devcapsule-schema-version = 1

[capabilities]
need = ["python", "python-ide", "docker-cli", "gemini"]

[project]
name = "DevCapsule"
slug = "devcapsule"
creator = "https://github.com/ccozianu"
mount = "/workspace/project"

[host.docker.mode.recommended]
value = "host-socket"
justification = "Required to run peer DevCapsule instances during the full test suite."
enables = ["full-test-suite"]
```

`devcapsule-schema-version` is a required positive integer. `devcapsule init`
always writes it. Backward-compatible schema additions retain the current
version; a change that alters the meaning of existing content increments it.
DevCapsule fails with an actionable error when the key is missing or its value
is unsupported, and never guesses or silently upgrades a manifest version.
Generated platform locks carry their own independent format version.

Committed repository content is untrusted for purposes of workstation access.
It must not activate host Docker socket access, host networking, credential or
agent-state mounts, arbitrary host-path mounts, devices, privileged mode,
Linux capabilities, or similar host exposure. It may constrain such exposure
or recommend a value, but a recommendation is not a configured value and does
not participate directly in overlay precedence. Security-sensitive access is
activated only by developer-owned project-local configuration or an explicit
run-once choice. With neither, the safe value applies. If the requested action
cannot work safely, DevCapsule stops and explains the missing authorization
instead of silently relaxing isolation.

Each security-sensitive recommendation contains a proposed `value`, a
project-authored `justification`, and the functionality it `enables`.
DevCapsule presents that text alongside a DevCapsule-authored explanation of
the security effect; repository text must not define its own risk description.
An unresolved interactive recommendation offers at least: deny for this run,
allow for this run, persistently allow for this checkout, and persistently deny
for this checkout. Denial is the default. Noninteractive execution never
prompts or grants access: it uses an existing developer-owned decision or
fails with an actionable instruction. A changed recommendation never mutates
an earlier adoption silently, and workstation policy may prohibit a
recommended value.

The workstation configuration root is
`$XDG_CONFIG_HOME/devcapsule/`. If `XDG_CONFIG_HOME` is unset or empty, it is
`~/.config/devcapsule/`; non-XDG platforms use their platform-appropriate user
configuration directory. `devcapsule config path` prints the actual resolved
file. Workstation-wide values live in `config.toml` beneath that root.

A project has a portable, self-asserted identity formed by a `creator` URI and
a `slug`. A creator may be an HTTPS profile URL or a `mailto:` URI; a plain
email entered during bootstrap is normalized to `mailto:`. DevCapsule warns
that both values will be committed and may become public. The pair is useful
for organization and local collision detection but is neither authenticated
ownership nor a grant of trust. Federated identity, ownership transfer, forks,
mirrors, and cross-workstation verification are deferred beyond this
local-first specification.

Project-local configuration lives under:

```text
$XDG_CONFIG_HOME/devcapsule/projects/<url-encoded-creator>/<url-encoded-slug>/
```

DevCapsule defines one canonical URI normalization and percent-encoding so an
identity maps deterministically. The common one-checkout case uses two clearly
named files:

```text
devcapsule.checkout.toml
devcapsule.resolved.toml
```

`devcapsule.checkout.toml` is durable developer-owned input. It records the
decoded project identity, workstation-observed canonical checkout path,
adopted state mappings, and persistent host-access decisions. The default
checkout needs no name. It is mode `0600`, contains no credential values, and
is never committed.

```toml
devcapsule-checkout-schema-version = 1

[project]
creator = "https://github.com/ccozianu"
slug = "devcapsule"

[checkout]
path = "/workspace/301e4208ef81-ChatGPT_Codex"

[state.adopted]
home = "/home/developer/.local/share/legacy-devcapsule/home"
"pycharm/config" = "/home/developer/.local/share/legacy-devcapsule/config"

[host]
docker-daemon = "host-socket"
development-sudo = true
network = "bridge"
```

Missing `[state.adopted]` or `[host]` tables mean that no external state or
special host access is configured. Entries in `[host]` are direct,
developer-owned authorization for this checkout. They contain decisions, not
tokens or credential material. `state adopt` updates `[state.adopted]`
atomically.

`devcapsule.resolved.toml` is generated local output. It records the effective
values produced from workstation defaults, the committed declaration, and the
checkout file. It is not an additional configuration layer and must not be
edited as source. Run-once command-line values are applied after it and are not
written into it. It carries its own `devcapsule-resolved-schema-version` and a
`[sources]` table containing the manifest, platform-lock, workstation-config,
and checkout-input SHA-256 digests. A missing optional source is represented
explicitly rather than by hashing an invented empty document.

When the same project identity gains another checkout, paired records use:

```text
checkouts/<checkout-name>.checkout.toml
checkouts/<checkout-name>.resolved.toml
```

The default records are not moved or renamed. Additional checkout names are
workstation-owned labels. Each checkout input repeats its decoded creator,
slug, optional checkout name, and canonical path so it remains understandable
and salvageable with an ordinary text editor. DevCapsule verifies the observed
path before applying the record. A fresh clone, fork, or second checkout cannot
inherit another checkout's security approvals merely by copying or claiming
the same committed project identity. Removing a checkout does not promote
another automatically.

Generated locks and resolved files record SHA-256 digests of the
schema-validated inputs from which they were produced. DevCapsule parses TOML,
validates it against the applicable schema, encodes the resulting value tree
as RFC 8785 canonical JSON, and hashes those bytes. V1 manifest schemas use
only value types supported by that canonical representation. TOML whitespace,
comments, and key ordering therefore do not make generated output stale.
Python's standard `tomllib` supplies parsing; the dependency-free Apache-2.0
`rfc8785` package is the accepted canonical encoder.

A platform lock records the digest of the committed declaration relevant to
resolution. A local resolved file records the digests of its committed
declaration, matching platform lock, workstation configuration, and checkout
input. If a digest no longer matches, normal launch refuses to run and prints
the exact regeneration command: `devcapsule lock` for a stale platform lock
and `devcapsule config resolve` for stale local resolution. Modification times
are informational only and never establish freshness.

`devcapsule run --force` may run once using stale generated values after a
conspicuous warning. It does not rewrite generated files, persist an approval,
grant host access absent from the stale resolution, or override restrictive
workstation policy. This is distinct from `run-image --force`, which skips
image metadata and compatibility checks.

Personal tool state and credentials remain developer-owned and outside the
committed declaration and image. This includes IDE settings and extensions,
Git identity and credential material, agent login and conversation state,
token values, and database contents. The project may describe an integration
it needs, but it cannot supply credentials, assume a developer's host paths,
or authorize their exposure.

Every normal launch receives a DevCapsule-managed persistent home, scoped to
the observed checkout by default and mounted as the container user's standard
`HOME`. This is not the developer's real host home. It lets IDEs, Codex,
Gemini CLI, Claude Code, Antigravity, and tools unknown to DevCapsule preserve
their normal settings, credentials, and conversations without tool-specific
launcher code.

The persistent home is a fallback, not the only persistence mechanism. A
curated component may declare namespaced state slots with its required
container path, lifecycle, sensitivity, scope, storage implementation,
ownership, concurrency, and deletion behavior. Names such as
`pycharm/plugins`, `codium/extensions`, and `postgres/data` belong to their
components rather than forming a hard-coded global IDE model. Components that
keep their state correctly beneath `HOME` need no additional slots.

DevCapsule stores its own configuration and authorization records beneath the
workstation configuration root. Persistent homes and durable component data
use the workstation data root; operational history uses the state root; and
rebuildable indexes, packages, and other caches use the cache root. This keeps
container-writable payloads away from DevCapsule's policy files and gives
cleanup commands a reliable lifecycle boundary.

Host paths are selected by convention from the verified project and checkout;
ordinary use does not require path options. A developer-owned setting may
relocate a slot. Named profiles may deliberately share a home or component
state, but every checkout separately authorizes a profile that may expose
credentials or conversations. Committed project configuration can neither
select a profile nor provide an arbitrary host path.

The exact layout, state-contract schema, conflict rules, authorization,
inspection, relocation, cleanup, and `run-image` behavior are specified in
`engineering-docs/specifications/product/state-and-persistence.md` and form part of this working
decision.

Resolution separately produces a generated and committed platform lock named
`.devcapsule/devcapsule.<platform-alias>.lock`, for example
`.devcapsule/devcapsule.linux-amd64.lock`. It pins the matrix and add-on catalog
versions, target platform, base-image digest, exact components and add-on
artifact digests, and the materialization recipe version. The lock is
resolution output, not a fifth general-purpose configuration overlay. `run`
uses these locked inputs; it does not silently re-resolve.

### 2. A capability is an abstract requirement; the lock holds concrete components

`python-ide` is a requirement. `vscodium@1.126.04524` is a component. Users
declare requirements; the resolver selects components and writes them to the
lock. Project types (`python-lib`, `fastapi`) are input-time templates that
expand to capabilities when `devcapsule init` or `devcapsule new`
writes the manifest. A manifest stores the expanded capability list, not both
a type and a second potentially conflicting list. This collapses the
announcement's second noun into the first while keeping the friendly
project-creation vocabulary.

### 3. Capability sets are named by intent

Named sets take intent names (`python-lib`, `fastapi`). Naming a set after its
implementation bakes in a lie the first time the implementation changes.

The abstract capability set {python, python-ide, gemini} resolves to the
curated PyCharm image by default in the initial matrix. The selected concrete
IDE is recorded in the matching platform lock and may change only through an
explicit lock update. A project that genuinely depends on one
implementation may add an implementation constraint to resolution, but
ordinary users declare intent and do not select an IDE product in the run
command. The exact constraint spelling remains schema work.

The primary launch form is `devcapsule run`, normally invoked from within the
project. DevCapsule discovers `.devcapsule/devcapsule.toml`, identifies the
local checkout, loads the configuration layers and durable-state conventions
from section 1, and runs the materialized image selected by the lock. An
explicit project path may be accepted when launching from elsewhere.

The pre-V1 configuration-first forms such as `devcapsule pycharm run` carry no
compatibility commitment and may be removed. Image build and maintainer
workflows are separate from the normal project launch grammar.

Routine launch state does not remain a collection of product-specific flags.
Image selection comes from the lock; project and checkout identity select
state paths by convention; IDE configuration and plugins persist in the IDE
state mount; project caches persist in the project-runtime state mount; and
Git identity, credentials, Docker access, debugging privileges, sudo,
networking relaxations, and other workstation choices come from
developer-owned configuration and the recommendation flow. Alternate launch
modes such as a diagnostic shell should be actions rather than IDE-specific
flags. Command-line values remain for inspection, explicit project selection,
and conspicuous run-once exceptions; the exact generic override spelling is
part of the remaining grammar review.

### 4. Two IDE capabilities resolve to one interactive surface

Requesting `python-ide` and `javascript-ide` means "one interactive IDE surface
that understands both," not two editor processes. The matrix selects one
complete image whose single interactive-surface component provides both
capabilities; if no such image is curated, resolution fails and lists the
nearest supported sets that were considered.

Exactly one component in a resolved image may provide the interactive surface
and own the normal container foreground lifecycle. Agent CLIs, terminals, and
debug shells are tools or alternate launch modes, not additional interactive
surface providers. This needs no supervisor and no second IDE process because
the collapse happens during resolution rather than at runtime.

When the foreground IDE terminates, cleanly or otherwise, the container
terminates and propagates its exit status. DevCapsule does not restart it
automatically. It preserves actionable failure evidence, while the durable
source, IDE, and runtime-state mounts allow a later invocation to resume the
workflow.

### 5. Resolution selects a curated base and worry-free add-ons

The resolution matrix selects one complete, tested base image for the
normalized capability set and target platform. The resolver may additionally
select user-requested toolchains from a versioned DevCapsule catalog of
worry-free add-ons. Users request capabilities such as `nodejs` or `java`; they
do not need to know whether the resolver provides them in the base or as an
add-on.

A worry-free add-on is a pinned, relocatable toolchain installed under an
isolated prefix. It does not use apt, create services or system users, run
arbitrary installation scripts, or mutate the base filesystem outside its
declared paths and environment settings. Node.js and OpenJDK are the initial
candidate add-ons.

Allowed add-on combinations are explicitly certified against supported base
families and platforms. DevCapsule does not assume that two independently
supported add-ons are mutually compatible. A request outside the certified
combinations fails with an actionable explanation.

DevCapsule materializes the resolved image on the developer's workstation from
the pinned base and add-on artifacts. Materialization is deterministic and is
limited to copying or extracting verified artifacts, applying declared
environment settings, and recording metadata. It does not compile the
toolchains, run general-purpose installers, or perform dependency resolution.
Docker layer and artifact caching make repeated materialization inexpensive.
Popular combinations may later be published as complete images without
changing the project declaration or capability model.

### 6. Lock lifecycle and failure behavior

`devcapsule lock` normalizes the declared capability set, selects an exact
supported matrix entry for the current execution platform, and writes
`.devcapsule/devcapsule.<platform-alias>.lock`. Stable aliases use normalized
OCI names in the form `<os>-<architecture>[-<variant>]`; the initial alias is
`linux-amd64`, corresponding to `linux/amd64`. A host-relative name such as
`native` is never stored in a filename or lock.

V1 does not generate locks for a different target platform. A developer adds
a lock for another supported platform by running and validating DevCapsule on
that platform. Cross-compiling project artifacts from within one capsule is a
separate toolchain concern and does not require cross-platform IDE execution
or cross-target lock generation.

Each platform lock records at least:

- a lock-format version and resolution-matrix version;
- the SHA-256 digest of the canonical validated project declaration used for
  resolution;
- the normalized requested capabilities and selected components;
- the target operating system and architecture;
- the immutable base-image registry reference and digest;
- the add-on catalog version, exact add-on versions, and artifact digests;
- the deterministic add-on order and materialization recipe version.

`devcapsule run` requires the lock matching its execution platform to be
consistent with the manifest. A missing or stale matching lock produces an
actionable instruction to run `devcapsule lock` on that platform; it never
changes the selected image implicitly. An
unavailable base or add-on artifact is a pull or registry error, not permission
to select a different input. Lock regeneration is explicit, and the generated
format must be deterministic so ordinary branch merges can distinguish a real
resolution change from serialization noise. The resulting local image ID
belongs to uncommitted workstation state; if it is missing, DevCapsule
rematerializes it from the locked inputs.

An unsupported capability set fails before materialization or run. The error
reports the normalized request, target platform, nearest curated sets, and the
documented request path. V1 does not fall back to arbitrary composition.

Locks make environments reproducible, not permanently frozen. DevCapsule never
updates a lock implicitly, but V1 periodically checks trusted catalog metadata
and warns when a locked component has a known relevant security advisory, is
approaching or past end of support, or has a recommended compatible update.
The warning provides the explicit `devcapsule lock --update` command. That
command shows proposed changes before rewriting the lock. Offline use
continues with cached metadata and reports when that metadata is stale.
Ordinary warnings do not block launch; this record does not define an artifact
revocation policy.

### 7. Having a tool does not grant access to the host

A capability says which tools and runtimes are available inside the capsule.
It does not give those tools permission to access resources on the developer's
workstation. Host access is configured separately so that installing a useful
tool never grants an unrelated security permission as a side effect.

For example, the `docker-cli` capability puts the Docker command-line client
inside the capsule. It does not let that client control the workstation's
Docker daemon. Access to the host Docker socket is a separate choice owned by
the developer. In the same way, including Git, an AI agent, a debugger, or a
device-supporting tool does not automatically expose credentials, agent login
state, host processes, or physical devices to the capsule.

The committed project declaration may explain that a host integration is
useful or required for part of the project. It may recommend a setting and
describe what that setting enables, but it cannot approve the access. A
developer must approve security-sensitive host access for their own checkout,
either persistently in developer-owned configuration or explicitly for one
run. Without that approval, DevCapsule keeps the safer setting and explains
which functionality will be unavailable.

A one-run choice applies only to that invocation and never changes the project
declaration, lock, or persistent developer configuration. Before launching,
DevCapsule shows the host access being granted and its security effect.
Interactive use may ask for confirmation. Noninteractive use never grants the
access merely because the project requested it; automation must provide an
explicit acknowledgement defined for that purpose or the command fails with
an actionable explanation.

The CLI specification must identify every option that relaxes isolation and
apply these rules consistently to Docker access, networking, credentials,
personal state, host paths, devices, Linux capabilities, privileged mode, and
similar workstation resources.

### 8. DevCapsule is independent of the Dev Container specification

DevCapsule's manifest, capabilities, resolution, lock, add-on, and runtime
models are independent of the Dev Container specification. Dev Container
Features are not DevCapsule's project capability or add-on format. The detailed
rationale will be recorded separately.

This boundary does not prohibit a future optional import, export, or
interoperability tool. Such a tool would not define or change DevCapsule's
native model.

### 9. Grammar

```text
devcapsule init [PATH] --need python --need python-ide --need nodejs
devcapsule new NAME --type python-lib
devcapsule lock
devcapsule lock --update
devcapsule run
devcapsule run --force
devcapsule run --project PATH
devcapsule run --docker-daemon host-socket
devcapsule run --network host
devcapsule run --device nvidia
devcapsule run-image IMAGE [--force]
devcapsule run-image IMAGE --shell
devcapsule config path
devcapsule config show
devcapsule config resolve
devcapsule status
```

`init` adopts an existing project and creates `.devcapsule/`. It is
create-only: if the project is already initialized for DevCapsule, `init`
fails without changing existing files and directs the operator to explicit
inspection or update commands. It never merges with or overwrites an existing
DevCapsule declaration implicitly. `new` creates a project from a type
template, which expands to capabilities rather than being stored as a second
source of truth. `run` discovers the project from the current directory unless
`--project` identifies another path.

`run-image` is the legacy, compatibility, dogfood, and recovery escape hatch
for cases in which the normal resolved path is unavailable or insufficient. It
accepts a local Docker image name, tag, ID, or DevCapsule alias and may run
with or without a project declaration. It does not read the project lock,
resolve capabilities, pull an alternative, update, or build. It fails if the
requested image is not local.

When `run-image` discovers `.devcapsule/devcapsule.toml`, it uses applicable
values from that declaration unless they are overridden explicitly on the
command line. Effective values use the ordinary configuration hierarchy from
section 1: workstation defaults, the project declaration, developer-owned
checkout configuration, and finally command-line values. Command-line values
have the highest ordinary-value precedence and represent choices for that
invocation only. After resolving the overlays, `run-image` fails with an
actionable error if a value required for the requested operation was supplied
by neither the configuration layers nor the command line and has no safe
default.

Committed recommendations remain recommendations and never become effective
host permissions merely because `run-image` discovered them. Explicit
command-line host-access options are run-once developer authorization, but
they cannot override restrictive workstation policy. `run-image` still
applies DevCapsule's project-mount planning, display, foreground lifecycle, and
developer-owned host-access rules. Because it is the expert recovery path, it
permits broad, explicit mount and Docker-specific command-line choices. It
requires structurally valid values, rejects conflicting destinations within
the generated plan, and makes unusual or risky choices conspicuous, but does
not maintain a broad forbidden-path or forbidden-option list. The developer is
allowed to depart substantially from curated defaults and is warned that doing
so assumes responsibility for Docker behavior and host exposure. Restrictive
workstation policy remains the upper boundary. `--force` skips DevCapsule image
metadata and compatibility checks; it never bypasses host-access authorization
or silently relaxes isolation.

The exact spelling of security-override acknowledgement, implementation
constraints, and generic privilege options is deferred until after the first
dogfood implementation of this contract. Their behavioral and security
constraints are part of this decision; the implementation must not invent
ambient access while their final spelling remains open.

## Rationale

**Bounded composition is useful; arbitrary composition is a research
project.** Curated bases plus worry-free add-ons cover common mixed-language
work without creating a dependency solver. Node.js and OpenJDK can live in
isolated prefixes and be applied deterministically; apt dependency graphs,
services, system users, and arbitrary third-party installers cannot. When
someone requests an uncurated combination, maintainers can certify a new entry
without promising that the client can compose anything.

**The declaration makes the standing rule mechanical.** A project can explain
why it recommends an integration, while only developer-owned configuration can
authorize the corresponding host exposure. The choice and its security effect
remain visible at adoption and launch instead of being implied by repository
content. This converts "keep any isolation relaxation explicit and documented"
from a rule people must remember into a property of the format and command
behavior.

**It attacks the cause of the parity bug.** A shared manifest and runtime
planner make common behavior data-driven and testable in one place. PyCharm and
Codium may still need thin adapters for IDE-specific entrypoints, sandboxing,
and validation, but those adapters no longer own copies of the shared host and
state policy. The parity work is therefore a down payment on this decision when
it extracts the common planner instead of copying flags.

**The lock makes materialization predictable and repeatable.** A first use may
still download a large IDE, GPU stack, or toolchain, but it does not compile
the toolchains or rediscover the recipe. Docker reuses the pinned base,
artifacts, and materialized layers on later runs. DevCapsule can report and
minimize unavoidable cost; it cannot make large development environments
small.

Option A was rejected because the parity bug already demonstrates its failure
at N=2. Option B was rejected on scope, not on merit: it may become justified
later, but arriving there before V1 means never shipping V1.

## Consequences

What becomes true:

- Shared runtime policy and resolution become data, with thin IDE-specific
  build and launch adapters where behavior genuinely differs.
- Project recommendations are committed and reviewable, while actual host
  exposure authorization remains developer-owned and checkout-specific.
- Project type stops being stored as a second source of truth and becomes an
  input-time template for capabilities.
- Personal state and credentials are explicitly outside the committed project
  declaration and lock.
- A small catalog of worry-free add-ons supports useful mixed-language
  environments without exposing arbitrary composition.
- `run-image` remains available as an expert path for local image construction
  and diagnosis without weakening host-access rules.

What becomes harder:

- The curated matrix is hand-maintained, and uncurated combinations fail. That
  failure must be honest and actionable, listing what was tried and how to
  request an addition. A vague failure here poisons the whole model.
- Each supported platform requires tested base and add-on combinations.
- Platform locks need a deterministic format, explicit update behavior, useful
  merge-conflict handling, and maintained advisory metadata.
- Docker Hub publication becomes a prerequisite rather than a nice-to-have, so
  the existing namespace task is now on the critical path.
- One-off isolation relaxations remain possible but must be conspicuous and
  cannot silently rewrite committed policy.

What is accepted as lost:

- Arbitrary composition on day one. Users asking for combinations we have not
  curated get a clear "not yet," not magic.
- The Dev Container specification does not define DevCapsule's native format.

Cleanups this decision forces, each currently a public-API wart:

- `--profile` is overloaded: it means "named state directory" in the CLI while
  the announcement uses "runtime profile" and "capability profile" for host
  exposure. Three concepts, one word. Rename before launch.
- `--docker` / `--docker-in-docker` / `--no-docker` are an enum modeled as
  three booleans with a runtime conflict check, even though `DockerMode`
  already exists internally. Same for the Git identity pair. Expose the enum.
- `codium_with_claude` is the only underscored command in a kebab-case CLI.
- `--plugins` is PyCharm vocabulary that does not survive contact with Codium
  extensions; `--git-token-host` is singular but takes a list.

Open questions deliberately left to sibling decisions:

- **D-0002**: agent autonomy inside the capsule, and the portable declaration
  of it across agent runtimes.
- **D-0003**: Gemini CLI as the default agent capability, recording the
  redistribution rationale that currently exists only in chat history.
- A later document will record the detailed rationale for keeping DevCapsule
  independent of the Dev Container specification.

## Reopen If

- Requests for uncurated capability combinations become the dominant support
  load. That is the signal that the matrix has stopped scaling and the composer
  from Option B is worth building.
- The resolver acquires version solving. At that point this is a package
  manager and deserves its own decision record rather than growing quietly
  inside a CLI.
- Local materialization becomes too slow or duplicates too much data despite
  Docker layer and artifact caching.
- Real projects need more than one simultaneously running interactive IDE
  surface often enough that the single-surface model becomes an obstacle.
- Project policy and personal state cannot remain cleanly separated without
  making normal setup materially harder.
