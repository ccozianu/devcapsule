---
id: D-0004
title: Configuration Resolution And Guided Run Experience
status: proposed
date-proposed: 2026-07-30
date-decided:
decided-by:
requirements:
  - R-PRODUCT-001
  - R-PRODUCT-002
  - R-PRODUCT-004
  - R-PRODUCT-005
  - R-DOCS-002
  - R-STATE-001
  - R-IDE-CONFIG-001
  - R-FRAMEWORK-001
supersedes:
superseded-by:
---

# D-0004: Configuration Resolution And Guided Run Experience

## Context

D-0001 establishes a capability-first project declaration, a committed
platform lock, developer-owned checkout configuration, generated local
resolution, and `devcapsule run`. The PyCharm dogfood path proved those layers
with an already-local image and six adopted legacy state directories. The next
image-formation slice replaces that image with a redistributable base plus a
checksum-verified PyCharm archive materialized on the workstation.

Writing the intended clean-clone user journey exposed a larger configuration
experience that cannot be left to accidental CLI behavior:

- some projects can run with safe managed defaults, while others require
  developer-supplied values such as a database endpoint;
- state-directory selection is configuration, but state inspection, movement,
  and cleanup are lifecycle operations;
- credentials require bindings to developer-owned secret sources rather than
  values in project or checkout files;
- committed recommendations must remain distinct from developer authorization;
- resolution, acquisition, image formation, and launch have different side
  effects and review needs; and
- the desired long-term experience is graphical even though V1 is CLI-driven.

The current command `devcapsule state adopt SLOT --from DIRECTORY` also mixes
two mental models. It changes developer-owned configuration, yet its top-level
placement makes it look like a prerequisite state-management workflow. In the
dogfood test it is specifically a migration operation used to retain six
existing PyCharm directories. A clean user should be able to accept managed
state without performing a fictitious adoption.

D-0002 remains reserved in the handoff for agent autonomy. The former D-0003
Gemini-default topic is now resolved by accepted D-0005, which makes agent CLIs
optional components; this configuration discussion remains D-0004.

## Options Considered

### Option A: Make `run` resolve configuration implicitly in V1

`devcapsule run` could create or rewrite local configuration and immediately
continue into downloads, image construction, mounts, host exposure, and
launch.

Cost: launch would mix decision-making with consequential actions. A changed
project recommendation or stale local input could produce hidden local
mutations at the moment the user is trying to start work. CLI users and
noninteractive automation would lose a clear preflight and inspection point.

### Option B: Separate V1 resolution and execution, then combine them through a guided V2 flow

V1 uses CLI commands or deliberate checkout-TOML editing to make configuration
choices. `devcapsule project config resolve` is the user's explicit completion
signal and produces an inspectable generated plan. `devcapsule project run`
requires that plan to be fresh, materializes the locked environment if
necessary, and launches it.

V2 makes `devcapsule project run` the main interactive mechanism. Missing,
stale, or incomplete configuration opens a graphical configuration experience,
initially envisioned as an embedded local web application displayed in the
browser. The user sees required choices, optional choices and defaults,
recommendations, authorization effects, and the resulting plan before
confirming. Run then performs the same logical resolution and continues to
launch.

Cost: V1 requires one explicit resolution command for a new checkout and after
configuration changes. V2 requires a secure local UI lifecycle and a larger
interaction surface. The logical review boundary must survive even when the
command boundary disappears.

### Option C: Treat checkout TOML as the primary configuration interface

Users could edit the local file directly and use `run` as the only command.

Cost: users would need to learn internal schema paths, required-versus-optional
rules, secret-handling constraints, and component state contracts. Validation
would arrive late, migration operations could not perform safe filesystem
checks, and the product could not evolve naturally toward a guided GUI.

## Proposed Decision

Adopt Option B as the working direction, subject to human review of the
remaining open questions below.

### 0. The `project` subtree owns checkout context and registration

Most commands operate on one observed checkout: a concrete local directory
containing a project's committed `.devcapsule/` tree. The portable project
identity may have several clones or worktrees on one workstation, so identity
alone is not enough to select developer-owned configuration, state, or
authorization. The canonical checkout path disambiguates them.

Project and checkout operations are grouped under one public noun:

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

`--path PATH` is an option on the `project` group and therefore precedes its
subcommand. For commands that require an existing declaration, it accepts the
checkout root or any path within it and searches upward to the nearest
`.devcapsule/devcapsule.toml`. When omitted, the same search starts at the
current directory. Explicit selection wins over current-directory discovery.
The positional form `devcapsule project . SUBCOMMAND` is not part of the
contract because an optional positional path would be ambiguous with the
subcommand name.

The intended forms are:

```text
# From the checkout root or any descendant directory
devcapsule project config bind pycharm/system --host-directory PATH
devcapsule project config resolve
devcapsule project run

# From anywhere, or when a script/IDE must select one checkout explicitly
devcapsule project --path /path/to/checkout config bind pycharm/system --host-directory PATH
devcapsule project --path /path/to/checkout config resolve
devcapsule project --path /path/to/checkout run
```

The `project` group carries the unresolved optional path through Click context;
only a subcommand that needs a checkout resolves it. This permits `project
list`, which needs no selected checkout, `project init`, which may target a
directory before a declaration exists, and `project run-image`, which can use a
plain source directory without requiring a declaration. This does not weaken
discovery for `config`, `state`, `lock`, or `run`: if discovery finds no
declaration, those checkout-scoped commands fail with an actionable message to
run from within a DevCapsule checkout or supply `project --path PATH`. They
never silently choose an entry from the workstation registry.

`devcapsule project init` is create-only and initializes a project declaration
at `--path` or the current directory. A source clone or initialized declaration
does not by itself register a developer checkout. Registration begins when the
first persistent `project config set`, `bind`, `authorize`, or `resolve`
operation creates the developer-owned checkout record.

`devcapsule project list` enumerates those workstation records beneath:

```text
$XDG_CONFIG_HOME/devcapsule/projects/
```

When `XDG_CONFIG_HOME` is unset or empty, the effective root is
`~/.config/devcapsule/projects/`. Listing never scans Git repositories or the
filesystem for `.devcapsule` declarations. A valid checkout record is the
registration marker; an empty or malformed directory is not. At minimum, the
list shows portable project identity, checkout name where applicable,
canonical checkout path, and status. A record whose source directory no longer
exists remains visible as `missing` so cleanup is deliberate.

When the portable project identity already has a default checkout record for a
different canonical path, the new checkout must receive a distinct
workstation-owned name before persistent choices are recorded. It never
overwrites or inherits the existing record. The second-checkout dogfood test
uses this provisional registration spelling:

```text
devcapsule project --path /path/to/second/checkout checkout register costin3-devcapsule
```

After registration, normal context discovery by canonical path selects
`checkouts/costin3-devcapsule.checkout.toml` and its matching resolved file;
the user does not repeat the name on every command. The exact registration
words remain subject to review, but explicit collision handling and distinct
records are required behavior.

Workstation-global resources remain outside the subtree, notably `devcapsule
images list` and base-image construction. Project-aware image materialization
stays in the settled `images` subtree and uses current-directory discovery by
default with an explicit command-local project-path option when invoked
elsewhere.

The ultimate developer escape hatch is
`devcapsule project [--path PATH] run-image IMAGE`. It is project-scoped because
it still mounts source and applies explicit state and host choices, but it is
lock-independent: it never claims the arbitrary image matches the committed
environment. When a declaration is discoverable, it may use declared project
defaults without reading the lock. Without a declaration, `--path` or the
current directory is treated as the source directory directly. Missing
required effective launch values still fail explicitly.

This project subtree deliberately refines D-0001's adopted top-level
`devcapsule run` spelling. If D-0004 is adopted, `devcapsule project run` is the
canonical V1 and V2 project launch command; the transitional top-level project
commands are removed rather than retained as compatibility aliases.

### 1. V1 configuration is iterative and ends explicitly

V1 presents required choices separately from optional choices with documented
defaults. A clean checkout performs zero or more configuration operations; a
project whose required inputs all have safe defaults may need none. Each
operation validates the supplied value or provider as far as possible before
persisting it. The V1 command families are:

```text
devcapsule project config set NAME VALUE
devcapsule project config bind NAME PROVIDER
devcapsule project config authorize NAME VALUE
```

`set` records an ordinary value. For example, a developer may constrain this
checkout's container memory after the project declares or supports the key:

```text
devcapsule project config set runtime.memory-limit 8GiB
```

`bind` maps a project-declared logical resource to a developer-owned provider.
The first dogfood milestone needs only an existing-host-directory provider for
component state, conceptually:

```text
devcapsule project config bind pycharm/system --host-directory PATH
```

`authorize` records an explicit developer decision for a security-sensitive
host capability or exact executable artifact. Candidate examples include:

```text
devcapsule project config authorize docker-daemon host-socket
devcapsule project config authorize network host
devcapsule project config authorize development-sudo true
devcapsule project config authorize base-image docker.io/ORGANIZATION/devcapsule-base@sha256:DIGEST
```

V1 offers two explicit base-trust paths. A developer may build a managed base
locally through `images build --type base` and select that inspected immutable
image through the existing `--base` development override. Alternatively, the
developer may authorize the exact digest recommended by the committed lock
after reviewing the project's release information, published checksum, and
basic security-scan result. The exact persistent and run-once command spelling
remains an implementation task, but authorization is always scoped to one
immutable registry digest or one inspected local image ID. It never grants
blanket trust to a registry namespace, repository, tag, or future digest.

The committed lock remains a project recommendation and cannot authorize its
own executable base. The developer-owned checkout record stores the trust
decision; a changed lock digest or changed local image identity makes the
resolution stale and requires a new decision. A published checksum establishes
byte identity and a vulnerability scan reports known findings at scan time;
neither proves build provenance, source equivalence, or absence of malicious
behavior. Signed SBOMs, attestations, automated provenance verification, and
policy-based publisher trust are V2 work.

The command grammar may still be refined before V1, but these three semantic
operations are distinct. A scalar service endpoint is an ordinary value;
Docker-daemon or host-network access is authorization; and selecting an
existing directory for a declared state slot is a binding whose command must
also disclose that the directory will be exposed to the container.

All persistent operations above write the developer-owned checkout input, not
the repository and not the generated resolution. For the default checkout the
file is:

```text
$XDG_CONFIG_HOME/devcapsule/projects/<encoded-creator>/<encoded-slug>/devcapsule.checkout.toml
```

When `XDG_CONFIG_HOME` is unset or empty, its effective value is `~/.config`.
Additional checkouts use the accepted named-checkout layout beneath that
project directory. User documentation and successful mutation output must
identify the actual file written. The file remains mode `0600` and contains no
secret values.

Direct editing of that TOML remains available for ordinary values and
non-secret provider references; generated `devcapsule.resolved.toml` is never
an input.

After completing the required choices and any desired optional changes, the
user runs:

```text
devcapsule project config resolve
```

This means “my choices are complete.” Resolution validates the committed
manifest and platform lock, workstation policy and defaults, checkout identity,
developer-owned values, state bindings, host authorization, and secret-source
bindings. Missing or contradictory required choices fail with actionable CLI
or TOML guidance.

Resolution may create the safe default checkout record and managed state paths
needed for a clean checkout. It does not download vendor artifacts, build an
image, mount host data into a container, retrieve secret values, grant a
recommendation, or launch a process. It writes an inspectable generated plan
with source digests so later changes become detectably stale.

### 2. V1 `project run` realizes a fresh resolution

`devcapsule project run` requires a present, fresh resolution. It may apply
explicit run-once choices without persisting them, acquire and materialize the
exact locked environment, retrieve secrets through declared bindings,
construct the container plan, and launch the foreground development surface.

A missing or stale resolution produces an instruction to run `devcapsule
project config resolve`; normal V1 launch does not regenerate it implicitly.
Routine return to an unchanged project remains one command.

### 3. Configuration values have different security and lifecycle semantics

The configuration experience distinguishes at least:

- ordinary values, which may be stored in developer-owned checkout TOML;
- state bindings, which select managed state or an existing external directory;
- secret bindings, which identify a developer-owned provider or source without
  containing the secret value;
- authorization, which permits a specific workstation exposure or exact
  executable base artifact; and
- project recommendations, which explain a useful choice but grant nothing.

Projects declare required and optional inputs, sensitivity, safe defaults, and
container delivery shape. Secret values—including a password-bearing database
URL—never enter the committed manifest, platform lock, checkout TOML, generated
resolution, image, build context, cache, or diagnostic output. `config resolve`
validates bindings; `run` retrieves values as late as practical and injects
them through the declared channel.

Credential availability and host exposure remain independent. Supplying
database credentials does not authorize host networking, and authorizing host
networking does not supply credentials.

The initial and potential provider catalog is deliberately bounded:

- the next dogfood milestone supports binding component state slots to
  existing host directories;
- managed component state is the safe convention and needs no binding command;
- later providers may include a host file, an environment-variable secret
  source, a narrowly scoped secret file, an operating-system keychain or
  password-manager entry, and a local agent socket or named profile; and
- devices, Docker-daemon access, host networking, privilege changes, and port
  publication are not generic bindings. They require explicit authorization
  and their own validation and risk explanation.

Adding a provider requires a defined readiness check, container delivery
contract, redaction behavior where applicable, and noninteractive semantics.
Listing a possible later provider here does not include it in V1 support.

### 4. State bindings belong to configuration; lifecycle remains a state concern

The current `devcapsule state adopt` syntax is transitional. Choosing managed
or existing storage for a component state slot belongs under the configuration
experience. The candidate direction now follows the typed binding model:

```text
devcapsule project config bind pycharm/system --host-directory PATH
```

No command is necessary to accept safe managed state unless the project marks
the choice as required. A future explicit reset-to-managed operation remains
useful after an existing-directory binding has been recorded.

Inspection and lifecycle operations remain state commands:

```text
devcapsule project state list
devcapsule project state inspect pycharm/system
devcapsule project state move pycharm/system --to PATH
devcapsule project state clean --cache
```

The exact verbs and compatibility aliases are not decided by this proposal.
Whatever spelling is selected must preserve adoption's safety semantics:
validate the existing directory, record it without copying or deleting it, and
make sensitivity and sharing consequences visible.

### 5. The lock pins formation; the workstation owns realization

The committed platform lock is the project's reviewed default for one platform.
It pins the immutable redistributable base, exact components, vendor artifact
digests, and materialization recipe. It neither embeds nor redistributes
PyCharm and does not contain personal state, credentials, host authorization,
cache paths, or a local completed-image ID.

The committed base reference must be globally resolvable through an OCI/Docker
registry and pinned by digest, for example
`docker.io/ORGANIZATION/devcapsule-base@sha256:DIGEST`. Docker and buildx use
this distribution-reference grammar directly; `docker://` is not part of the
V1 lock spelling. A workstation-only tag, local image ID, daemon-local alias,
or mutable tag may be used through an explicit developer-owned override, but
must not appear as the project's committed default. This keeps the platform
lock usable by a fresh checkout on another compatible workstation while still
allowing conspicuous local development deviations.

When the completed image is absent, the client downloads the locked PyCharm
archive directly from JetBrains on the host, verifies it, builds a deterministic
`devcapsule-local-pycharm:<materialization-identity>` image from the locked
base, and launches that completed image. The container entrypoint performs no
just-in-time component download.

The advertised local-image naming contract is:

```text
devcapsule-local-<component>:<materialization-identity>
```

`<component>` is a stable curated component or environment kind such as
`pycharm`; it is not the project slug. Two projects with identical immutable
formation inputs may reuse the same local image without sharing configuration,
authorization, source, or state. `<materialization-identity>` is derived from
the immutable base identity, exact component artifacts and digests, and the
materialization recipe version. Human labels such as `debug-v019` may be added
as local aliases, but they are never the reproducible identity recorded as the
materialization result.

The project lock selects formation inputs; neither the project nor the lock
owns the resulting image. Different projects and different checkouts compute
the same materialization identity whenever their normalized formation inputs
are identical. They therefore converge automatically on the same canonical
local image without declaring a sharing relationship.

V1 distinguishes two developer-facing image operations:

```text
devcapsule images build --type base [--recipe RECIPE] [--pex PATH] [--network MODE] --tag BASE_IMAGE
devcapsule images build --type environment [--project PATH] [--base BASE_IMAGE] [--alias IMAGE]
```

`images build --type base` is a DevCapsule development and publication
operation. It builds
the JetBrains-free base containing the generic runtime and embedded PEX. When
the command itself is executed from a PEX, that PEX is the default payload;
`--pex PATH` permits an explicit artifact. `--tag` names the developer's local
or publication candidate base.

The default `ubuntu-24.04` Linux base recipe produces one OCI image with:

- Ubuntu 24.04 as the default root, resolved to and reported with its immutable
  local image identity;
- Python 3.12 and Python development/virtual-environment support;
- the compiler and debugger baseline, Git and SSH clients, common shell,
  process, filesystem, and network diagnostics;
- Docker CLI, buildx, Compose, and daemon binaries, without enabling or
  authorizing access to a host or nested daemon;
- X11, GTK, font, audio, and Mesa runtime libraries needed by curated GUI
  components;
- `tini`, `gosu`, and the `sudo` binary, without ambient sudo authorization;
- the recipe-pinned public Node.js/npm language-tooling baseline; and
- exactly one executable DevCapsule PEX at
  `/opt/devcapsule/bin/devcapsule.pex`, identical by SHA-256 to the selected
  host artifact.

The command exposes two curated recipe names. `ubuntu-24.04` is the ready
default. `nvidia-cuda-devel` is a WIP V1 recipe using the NVIDIA CUDA 12.8.1
development root for Ubuntu 24.04 and the same DevCapsule developer baseline.
Its specialized E2E validation on the maintainer's NVIDIA hardware is a V1
release blocker. AMD ROCm and other GPU families require interested partner or
cloud test infrastructure and remain outside required V1 scope. A GPU recipe
selects compatible build-time libraries and tooling, while access to GPU
devices remains a separate, explicit runtime authorization. Building a
GPU-capable image must never imply that a launched container receives a GPU.

Its OCI process contract is:

```text
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]
CMD ["/etc/devcapsule/runtime-plan.json"]
```

The base intentionally does not contain `/etc/devcapsule/runtime-plan.json`.
Running it without materialization therefore fails clearly instead of guessing
an application. It also contains no IDE or vendor component, project source,
project declaration or lock, developer checkout configuration, state,
credentials, host paths, host authorization, generated account files, or
vendor license acceptance. In particular it contains no JetBrains archive,
installation, launcher default, or product-specific Bash entrypoint.

The image carries at least `devcapsule.image.kind=base`, the base recipe
version, embedded PEX SHA-256, and source revision labels. The command reports
the output tag and immutable image ID, root-image identity, recipe version,
PEX digest, source revision, and component inventory. A publication candidate
requires immutable/pinned formation inputs and complete license/inventory
evidence; a local debug build may use a mutable convenience tag, but the actual
resulting image ID participates in every later materialization identity.

`images build --type base` uses the selected root image from the local Docker
store when present and otherwise obtains its registry reference. It may use
network access to obtain declared public packages and checksum-verified
tooling. It writes the local image and ordinary build cache only. It does not
inspect a project, modify a lock or checkout file, download PyCharm, create a
materialized image, or launch a container.

Its `--network` value is one of `default`, `host`, or `none` and is forwarded
to Docker buildx. Host mode is an explicit build-time isolation relaxation and
enables the BuildKit `network.host` entitlement; it never grants host networking
to containers later launched from the image.

`images build --type environment` is project-aware and does not launch. It
reads the project's declaration, platform lock, and fresh local resolution to
validate the project context and select the required component and
materialization recipe. Checkout resolution is not itself a formation input.
With no `--base`, it uses the lock-pinned base. `--base` is a conspicuous
developer override accepting the same Docker image-reference grammar for an
already-local image or a registry reference. A local image is reused when
present; otherwise its registry reference is obtained. This fixed behavior
never silently replaces a lock-pinned digest.

The materializer always creates or reuses the canonical
`devcapsule-local-<component>:<materialization-identity>` name first. Optional
`--alias` adds a local debugging alias such as
`devcapsule-local-pycharm:debug-v019`; the alias does not change the canonical
identity or make an overridden base the project's supported default. The
command reports both names and all resolved input identities.

Ordinary adopters do not run either developer operation. `devcapsule project
run` performs the same locked materialization automatically when the canonical
local image is absent. Base overrides and debug aliases remain explicit
developer workflows and must not be inferred from a committed recommendation.

### 5.1 Materialization identity and automatic cross-project reuse

The materialization identity is the SHA-256 digest of a versioned canonical
formation descriptor. The descriptor is serialized as RFC 8785 canonical JSON
and contains every immutable input that can affect image filesystem content or
OCI execution metadata, including:

- formation-descriptor schema name and version;
- target platform and architecture;
- the immutable base-image identity, not merely its mutable tag;
- a deterministically ordered list of every included component identifier,
  version, artifact SHA-256, and installation-relevant variant;
- materialization recipe identifier, version, and formation-affecting
  parameters; and
- the digest of the formation-owned component runtime template and entrypoint
  contract embedded in the image.

The descriptor deliberately excludes the project creator, slug, project-lock
digest, checkout name and path, source tree, generated resolution, project
mount, runtime UID/GID mapping, state paths, credentials, secrets, host
authorization, run-once options, and aliases. Artifact download URLs and cache
locations are provenance rather than formation inputs when they deliver the
same verified bytes.

The complete digest is recorded in
`devcapsule.materialization.identity`; the canonical human-readable tag uses a
documented short prefix. The full digest, not the shortened tag, is the reuse
authority. A lock change that affects only recommendations or runtime choices
may make local resolution stale but does not create a new image identity. A
change to any normalized formation input creates a distinct identity and
image.

Before building, DevCapsule computes the descriptor and canonical name. If the
canonical local image exists, it inspects its managed metadata and requires the
stored canonical descriptor to hash to the full identity and requires its base,
recipe, and complete component identities to match the expected descriptor
before reuse. A conflicting or malformed image under the canonical tag is
never silently used or overwritten; the command fails with inspection and
cleanup guidance. If no matching image exists, DevCapsule acquires and verifies
the locked artifacts, builds once, records the descriptor and identities, and
then adds any requested alias.

This is automatic structural sharing, not user-forced sharing. Projects whose
formation descriptors differ receive different images even when a user would
prefer one shared tag. An explicit `--base` produces the identity for that
actual base and is reported as a developer deviation; it cannot silently make
another project's lock mean something different.

The materialized image may contain a formation-owned generic component runtime
template, but it must not bake a checkout-specific launch plan. `project run`
generates the latter outside the image and supplies it read-only at launch. The
launch plan owns the actual project mount, developer identity, state mounts,
authorization, secrets, and run-once choices. This separation is what permits
two projects to share immutable image layers without sharing runtime state or
host exposure.

### 5.2 DevCapsule image identification and listing

Every image created by the V1 image commands carries these mandatory Docker/
OCI labels:

```text
devcapsule.image.managed=true
devcapsule.metadata.version=1
devcapsule.image.kind=base|materialized
```

`devcapsule.image.managed=true` is the authoritative inclusion marker for
`devcapsule images list`. `devcapsule.metadata.version` selects the metadata
schema, and `devcapsule.image.kind` distinguishes a reusable base from a
project-resolved environment image. The CLI's user-facing build type
`environment` maps to stored kind `materialized`, which describes how the image
was formed without implying that project source or state was baked into it.

Kind-specific identity labels remain mandatory. A base includes at least its
recipe version, PEX digest, and source revision. A materialized image includes
at least its canonical formation descriptor, materialization recipe version,
full formation identity, base identity, primary component identifier and
version, and locked artifact digest. Its canonical human-readable name is also
recorded as metadata so aliases can be distinguished from it. The descriptor
label is parsed and hashed during reuse; the identity label alone is not
sufficient.

The initial label names are:

```text
# base
devcapsule.base.recipe-version=VERSION
devcapsule.pex.sha256=SHA256
devcapsule.source.revision=REVISION

# materialized environment
devcapsule.materialization.descriptor=RFC8785_CANONICAL_JSON
devcapsule.materialization.identity=SHA256
devcapsule.materialization.recipe-version=VERSION
devcapsule.materialization.base-identity=IDENTITY
devcapsule.component.id=COMPONENT
devcapsule.component.version=VERSION
devcapsule.component.sha256=SHA256
devcapsule.image.canonical-name=devcapsule-local-COMPONENT:SHORT_IDENTITY
```

`devcapsule images list` is read-only and queries only the local Docker image
store. It includes images carrying the managed marker, groups tags that refer
to the same image ID into one result, and distinguishes the canonical name from
aliases. At minimum it displays kind, canonical name, aliases, short immutable
image ID, component when applicable, recipe version, creation time, and size.
Inspection commands may show the complete labels and formation identities.

An image with the managed marker and an unknown metadata version remains
visible as `unsupported-metadata`; it is never silently hidden or interpreted
using the wrong schema. Missing required labels are reported as
`invalid-metadata`. Listing does not establish trust: local labels can be
forged, so reuse still verifies the lock, immutable base identity, artifact
digests, and expected formation identity.

Repository/tag prefixes are conventions for human recognition only.
`devcapsule-base:*` and `devcapsule-local-*:*` do not qualify an otherwise
unlabelled image for the default list. Conversely, retagging a labelled image
does not make it disappear. Transitional images carrying only the old
`devcapsule.configuration` label are excluded by default and may be shown by
an explicit `devcapsule images list --include-legacy` compatibility view; they
are never silently upgraded to managed V1 metadata.

### 6. V2 combines the interaction but preserves the boundary

In V2, `devcapsule project run` becomes the primary interactive mechanism and
subsumes ordinary `project config resolve` interaction. The graphical flow
must distinguish:

- choices that must be made before launch;
- optional choices, their defaults, and the effects of changing them;
- committed recommendations from developer authorization;
- value sources and effective precedence; and
- materialization, secret-delivery, mount, and host-access consequences.

Confirmation records developer-owned choices and the generated resolution,
then continues into execution. The GUI removes a separate command from the
ordinary workflow; it does not remove validation, explicit authorization, or
the inspectable plan. Noninteractive execution still requires complete inputs
and never infers authorization. The explicit resolution operation may remain
for automation, diagnostics, and CLI-preferring users.

### 7. Alternative environments must be conspicuous

The committed lock remains the supported project default. A future curated
local alternative may satisfy the same declared capabilities, but it must be
developer-owned, fully pinned, materialized under a distinct identity, and
shown as a deviation. `project run-image` remains the arbitrary-image expert
escape hatch and does not claim to reproduce the committed environment.

## Unanswered Questions

This proposal intentionally preserves questions that require further design or
human choice:

1. What project-registry cleanup command removes an obsolete or `missing`
   checkout record without touching source or persistent state?
2. Is `project checkout register NAME` the clearest spelling for assigning a
   workstation-owned name to an additional checkout?
3. What exact options and value syntax complete the accepted `config set`,
   `config bind`, and `config authorize` families, list missing choices, and
   reset a value to its default?
4. What is the exact existing-host-directory provider spelling for
   `config bind`, and how does the CLI display its mount and sharing effects?
5. How long should the old `state adopt` command remain as a compatibility
   alias, and what migration warning should it show?
6. Which later V1 secret providers and delivery channels are supported, and how are
   provider readiness, redaction, rotation, and noninteractive use tested?
7. What is displayed and acknowledged before acquiring a vendor component, and
   where is that acknowledgement recorded?
8. How are acquisition, digest verification, image-build progress, retry,
   cancellation, failure cleanup, and offline reuse presented?
9. Which inspection command explains every effective value, its source, its
   default, and whether it is a recommendation, authorization, or run-once
   choice?
10. How are curated local alternative environments pinned, displayed, shared,
    supported, and compared with the committed lock?
11. How is the DevCapsule client installed and updated before the clean-clone
    journey begins?
12. How is the reusable human/agent workflow offered and bootstrapped when a
    project adopts that mode?
13. How does the V2 local web application authenticate browser requests, bind
    only to an appropriate local interface, prevent cross-origin attacks,
    handle multiple checkouts, and terminate cleanly?
14. Does V2 open the GUI only when resolution is missing or stale, or also when
    the user explicitly asks to review otherwise valid choices?
15. How does V2 provide safe image and cache lifecycle management: ownership
    inspection, reclaimable-size reporting, dry-run removal, protection for
    running or lock-referenced images, and an explicit guarantee that project
    source, persistent state, credentials, and unrelated Docker resources are
    never removed?
16. Which SBOM, signing, attestation, vulnerability-policy, and provenance
    standards implement V2 artifact verification, how is publisher trust
    bootstrapped and rotated, and which failures block execution rather than
    warn?

## Rationale

The proposed split gives V1 a small, testable CLI surface without confusing
configuration changes with downloads and launch. It also creates the same
logical phases that a V2 GUI needs: discover choices, collect developer input,
validate and show an effective plan, confirm, materialize, and execute.

Treating state and secrets as typed configuration preserves one user mental
model without pretending all values have identical handling. A path adoption
needs filesystem validation; a secret needs late retrieval and redaction; a
host permission needs explicit authorization; an ordinary port may be a scalar.
They belong in one configuration experience but require different operations.

## Consequences

- V1 onboarding takes at least one explicit resolution command before the first
  run and whenever configuration inputs change.
- Checkout-scoped commands share the `project --path PATH` context and
  current-directory discovery rule instead of each defining its own selector.
- `project list` reads only the XDG developer-owned checkout registry; cloning
  or initializing source does not silently register a checkout.
- Routine launches remain one command while retaining stale-input detection.
- Clean managed state must be bootstrappable without legacy adoption.
- The CLI needs a coherent configuration command family rather than more
  unrelated top-level setters.
- Secret-provider and runtime-input contracts become necessary V1 schema work.
- V2 can improve interaction without weakening the underlying security model.
- The browser UI adds a meaningful local attack surface that must be designed
  and tested rather than treated as a cosmetic wrapper.
- Current dogfood and configuration-first commands remain transitional until
  compatibility and migration behavior are decided.

## Reopen If

- user testing shows the explicit V1 resolution checkpoint causes more errors
  than it prevents;
- a secure, inspectable `run` flow can combine V1 resolution without hidden
  mutation or authorization;
- projects cannot express real runtime inputs and state choices through the
  proposed typed configuration model;
- late secret retrieval cannot support required IDE and tool workflows; or
- the local graphical configuration experience cannot be secured or kept
  simpler than the CLI workflow it replaces.
