# DevCapsule V1 User Experience

Status: product design draft; this is not current CLI usage documentation

Audience: developers evaluating or adopting a project that already contains a
committed `.devcapsule/` directory

## The Promise

A DevCapsule-enabled project should open as a complete, reproducible
development workspace without asking each developer to reconstruct the IDE,
toolchain, agent tools, or safe launch command from setup notes.

“Batteries included” describes the user outcome. It does not require every
component to be redistributed inside one published image. When a component
such as PyCharm must come directly from its vendor, DevCapsule should acquire,
verify, and assemble it automatically on the developer's workstation before
launch.

The project supplies a tested default. The developer retains control of
personal state and every meaningful exposure of the workstation.

## Four Things With Different Owners

| Item | Owner | Purpose |
| --- | --- | --- |
| `.devcapsule/devcapsule.toml` | Project | Declares portable capabilities, project identity, safe settings, and host-access recommendations. |
| Platform lock | Project | Pins the exact supported base, components, artifact digests, and materialization recipe for one platform. |
| Checkout configuration and state | Developer | Records this checkout's path, persistent state choices, and explicit host authorizations. |
| Materialized image and caches | Workstation | Realizes the locked environment locally and is reused while its identity remains valid. |

The committed lock is a reproducibility contract, not a container registry and
not a grant of host access. It makes environment changes visible in Git and
prevents a normal run from silently selecting newer or different components.
It does not contain PyCharm, credentials, personal settings, cache paths, or
the local completed-image ID.

## Starting From An Existing Repository

The developer first installs the released DevCapsule client, then clones a
project that already carries its declaration and platform lock:

```bash
git clone "$PROJECT_GIT_URL" "$CHECKOUT"
cd "$CHECKOUT"

devcapsule config resolve
devcapsule run
```

The project is already initialized. An ordinary adopter does not run
`devcapsule init`, generate a new shared lock, build a base image, find an IDE
archive, or invoke a product-specific image build.

### Selecting the checkout

DevCapsule normally discovers the checkout by searching from the current
directory upward for `.devcapsule/devcapsule.toml`. The user may run commands
from the checkout root or any directory beneath it.

Working from elsewhere must also be supported. A global context option selects
the checkout once for the whole command:

```bash
devcapsule --project /path/to/checkout config resolve
devcapsule --project /path/to/checkout run
```

This is especially useful for scripts, IDE integrations, and workstations with
multiple clones or worktrees of the same portable project identity. The path
selects the concrete checkout and therefore its developer-owned configuration,
state, and authorization. DevCapsule never chooses among known checkouts by
project identity alone.

The user is not required to change directories merely to operate on another
checkout. Conversely, an explicit path or discoverable `.devcapsule/` tree is
required for normal checkout-scoped commands. The V1 public spelling is
`--project PATH`; internally, the resolved path identifies the observed
checkout.

### V1: why `config resolve` and `run` are separate

The commands separate deciding what may run from performing the consequential
work of building and launching it.

In V1, configuration is an iterative CLI-driven process. DevCapsule shows the
choices that must be made before this project can run, distinguishes them from
optional choices that have safe defaults, and provides commands for recording
developer-owned decisions. A developer may also inspect and edit the local
checkout TOML directly when that is more convenient. Editing generated
`devcapsule.resolved.toml` is never a supported input mechanism.

After making the required choices and any desired optional changes, the
developer runs:

```bash
devcapsule config resolve
```

This command is the explicit “my configuration choices are complete” signal.
It validates that every required choice has an effective value, applies
documented defaults for optional choices that were left unset, and produces
the final inspectable local resolution. If required decisions are still
missing or contradictory, it fails with actionable CLI or TOML instructions
instead of partially resolving or launching.

`devcapsule config resolve` is the local planning and review phase. It:

- combines the committed declaration and platform lock with workstation
  defaults and this developer's checkout-owned choices;
- establishes safe convention-based checkout state when this is the first
  resolution;
- validates schemas, source digests, project identity, paths, policy, and host
  authorization without starting a container;
- writes an inspectable `devcapsule.resolved.toml` whose source digests reveal
  when any input later becomes stale; and
- reports recommendations that remain denied or need an explicit developer
  decision.

Resolution does not download vendor artifacts, build an image, mount project
or personal state into a container, grant a recommendation, or start the IDE.
It is therefore safe to run as a preflight and useful in review,
troubleshooting, and noninteractive automation.

`devcapsule run` is the realization and execution phase. It:

- requires a present, fresh generated resolution and refuses an unexplained
  change of inputs;
- applies any conspicuous run-once choices without persisting them;
- acquires and materializes the exact locked environment when necessary;
- constructs the final mount, permission, and container plan; and
- launches the foreground development surface.

Keeping these phases separate creates a review point before network downloads,
image construction, host-resource exposure, or process launch. It also means
that typing `run` cannot silently rewrite developer-owned configuration or
turn a changed project recommendation into authorization. A missing or stale
resolution produces an actionable instruction to run `devcapsule config
resolve`; it is not regenerated implicitly as a side effect of launch.

The cost is one explicit command for a new checkout and after configuration
inputs change. The normal return-to-work experience remains one command:

```bash
devcapsule run
```

That is the “launch in one command” product promise. Resolution is setup and
change review, not a step repeated before every session.

### V2 direction: configuration inside `devcapsule run`

In V2, `devcapsule run` becomes the main user mechanism and subsumes the
separate resolution command for ordinary interactive use. When configuration
is absent, stale, or incomplete, `run` opens a graphical configuration
experience, expected initially as an embedded local web application displayed
in the user's browser.

The graphical experience presents:

- required choices that must be completed before the project can run;
- optional choices, their effective defaults, and the consequences of changing
  them;
- project recommendations separately from developer authorization;
- the source and effect of each effective value; and
- the resulting materialization and host-access plan before execution.

After the user completes and confirms the choices, `run` performs the same
logical resolution, records the developer-owned decisions and generated plan,
then continues into materialization and launch. V2 therefore removes the
command-level interruption, not the security and review boundary between
configuration and execution. Noninteractive use must still require a complete,
fresh resolution and must never infer missing authorization.

The explicit `config resolve` operation may remain available in V2 for
automation, diagnostics, and users who prefer CLI workflows, but it is no
longer the primary interactive path.

On a clean checkout, configuration resolution should:

1. validate the project declaration and matching platform lock;
2. identify the observed checkout without inheriting another checkout's
   permissions or personal state;
3. create the developer-owned checkout record and convention-based persistent
   state roots when they are absent;
4. preserve safe defaults for every unresolved host-access recommendation; and
5. write an inspectable generated resolution for the subsequent run.

Adopting an existing home, IDE settings, plugins, or other state is an explicit
migration choice. It must not be required for a developer starting fresh.

### Fresh state versus adopted state

State selection illustrates the V1 iterative configuration model:

- A fresh user accepts checkout-scoped managed defaults and runs no
  `state adopt` commands.
- A returning dogfood user who wants to preserve existing state explicitly
  maps each existing directory before resolving.
- A user may adopt only selected slots and use managed defaults for the rest,
  when the component state contract permits that combination.

For example, the earlier PyCharm dogfood migration test intentionally runs:

```bash
devcapsule state adopt home --from "$LEGACY_STATE/home"
devcapsule state adopt pycharm/config --from "$LEGACY_STATE/config"
devcapsule state adopt pycharm/plugins --from "$LEGACY_PLUGINS"
devcapsule state adopt pycharm/system --from "$PROJECT_STATE/system"
devcapsule state adopt pycharm/log --from "$PROJECT_STATE/log"
devcapsule state adopt pycharm/cache --from "$PROJECT_STATE/home/.cache"

devcapsule config resolve
```

Those commands do not install or configure PyCharm. They tell DevCapsule to
mount six existing host directories instead of allocating fresh managed state.
They are required for that migration test's continuity criteria, not for an
ordinary clean clone.

The current implementation makes this distinction awkward because
`config resolve` requires a developer checkout file and `state adopt` is the
implemented path that creates one. V1 must add clean-checkout bootstrap so a
user accepting managed defaults can reach `config resolve` without performing
a fictitious adoption.

### Project runtime values and secret bindings

Other projects will require configuration that cannot be committed or safely
defaulted. A development database is a typical example. The project may need a
database host and name, a complete `DATABASE_URL`, or credentials for an
existing developer-owned service before its development experience can work.

DevCapsule distinguishes three kinds of input:

1. **Ordinary values** such as a database hostname, port, database name, or
   feature choice. A developer may record these in checkout-owned TOML or
   through the corresponding CLI commands.
2. **Secret bindings** that identify where a required secret will come from,
   such as an explicitly named environment variable, password-manager entry,
   or narrowly scoped secret file. The binding may be developer-owned
   configuration; the secret value may not.
3. **Secret values** such as passwords, tokens, private keys, or a database URL
   containing credentials. These are obtained from the selected provider at
   launch and are never written to the committed manifest, platform lock,
   checkout TOML, generated resolution, image, build context, or diagnostic
   output.

The project declares the input contract: the names and purposes of required
and optional values, whether an input is sensitive, any safe default, and the
container-side delivery form such as an environment variable or mounted file.
It does not provide the developer's value or choose a credential source on the
developer's behalf.

During the V1 configuration loop, DevCapsule reports which required ordinary
values and secret bindings are missing. The user supplies them through CLI
operations or, for non-secret values and secret references, through the local
checkout TOML. The exact input and secret-binding command grammar remains to be
specified; secret values must never be accepted into the TOML merely because
manual editing is supported.

`config resolve` then verifies that every required ordinary value has an
effective value and every required secret has a valid binding. Its generated
plan records the secret's logical name, provider reference, delivery method,
and readiness status, but never the secret value. A missing required binding
blocks resolution. Optional inputs use their documented defaults or remain
disabled.

At `run`, DevCapsule retrieves each secret as late as practical, injects it only
through the declared channel, redacts it from output, and does not allow it to
affect the materialized image or Docker build cache. Rotating a value behind an
unchanged binding therefore does not require a new project lock or image.

Database configuration may also imply a separate host-boundary decision. For
example, reaching a database bound only to the host may require an explicit
network choice. Supplying database credentials does not implicitly authorize
that network exposure, and authorizing the network does not supply the
credentials.

## What Happens On The First Run

`devcapsule run` discovers the project and uses the committed lock. If the
completed local image is absent, DevCapsule:

1. ensures the exact locked, redistributable base is available;
2. explains that PyCharm is a JetBrains product that will be downloaded
   directly from JetBrains under JetBrains's terms;
3. downloads the exact locked archive on the host and verifies its pinned
   SHA-256 digest;
4. stops without building or launching if verification fails;
5. builds a deterministic workstation-local image named
   `devcapsule-local-pycharm:<materialization-identity>`; and
6. launches the completed image with the project and declared persistent state
   mounted.

The container entrypoint does not download or install PyCharm just in time. It
initializes the already-completed environment and starts the foreground IDE.
JetBrains EULA acceptance, licensing, and login remain interactions between
the developer and JetBrains.

Closing the IDE ends the container. A later `devcapsule run` reuses the cached
artifact and completed image when the locked identities have not changed, and
reuses the checkout's persistent home and component state.

## Batteries Included Without Taking Away Choice

The project default must work without requiring the developer to make product
or version selections. Choices remain available at distinct levels:

### Personalize the workspace

IDE preferences, plugins, agent logins, conversations, shell settings, and
other comfort state persist outside the image. These choices do not change the
locked environment and do not require rebuilding it.

### Choose host integration deliberately

The presence of a tool inside the capsule does not grant it access to the
workstation. Docker-daemon access, host networking, credentials, devices,
privilege changes, external directories, and shared profiles remain
developer-owned choices.

A project may recommend access and explain the feature it enables. Denial is
the default. The developer may deny it, allow it once, allow it for this
checkout, or be prevented from allowing it by workstation policy.

For example, this repository recommends host Docker-daemon access for its full
test suite. An explicit run-once authorization is conceptually:

```bash
devcapsule run --docker-daemon host-socket
```

The recommendation alone must never mount the Docker socket.

### Select a different environment explicitly

Changing the IDE or toolchain is different from changing a preference. It
changes the realized development environment. The committed platform lock is
the project's supported default and must not be silently reinterpreted.

A future local-alternative experience may offer curated components that still
satisfy the declared capabilities. Such a choice must be developer-owned,
fully pinned, materialized under a distinct identity, and shown conspicuously
as a deviation from the committed default. The representation and support
contract for local alternatives remain an open V1 design question.

`devcapsule run-image` remains the expert escape hatch for an arbitrary local
image. It does not claim to reproduce the committed environment.

## Human And Agent Work Resume Together

The environment is only one half of the experience. A project may also adopt
the reusable human/agent workflow: requirements, decisions, known bugs,
validation evidence, current status, and the planned next step live in the
repository rather than only in chat history.

When that mode is present, the first agent session reads the project's brief
and handoff before changing code. Human and agent then work in narrow,
verifiable slices and update the durable handoff at meaningful checkpoints.
The intended result is that opening the capsule restores both the tools and
the project's working context.

## Current Availability

This document deliberately distinguishes the V1 experience being designed
from the transitional implementation.

Available in the current dogfood path:

- committed capability declaration and Linux platform lock;
- developer-owned checkout resolution and adopted persistent state;
- explicit Docker and development-sudo choices;
- foreground PyCharm lifecycle;
- generic Python runtime entrypoint foundation;
- tested base-image and checksum-verified local-materialization primitives.

Not yet available as the complete clean-clone experience:

- a published redistributable default base;
- a platform lock that pins base and PyCharm materialization inputs instead of
  the old completed dogfood image tag;
- clean-checkout creation of safe developer configuration without legacy state
  adoption;
- automatic materialization invoked by `devcapsule run`;
- the vendor-notice interaction; and
- a defined local-alternative environment workflow.

The browser-based configuration experience and `run`-owned interactive
resolution are V2 direction, not V1 implementation scope.

Until those items are implemented and validated, current executable commands
and workarounds remain documented in `devcapsule/README.md`.

## Questions This Narrative Must Settle

Writing the user journey exposes product decisions that implementation alone
would otherwise hide:

1. How does a new user install and update the DevCapsule client?
2. What exactly is displayed and acknowledged before vendor acquisition?
3. How are download, verification, build progress, failure, retry, and offline
   reuse explained?
4. How does a developer inspect what came from the project, the lock, local
   configuration, and run-once choices?
5. Can a developer select a curated alternative environment, and if so, how is
   that deviation pinned, displayed, shared, and supported?
6. How is the reusable human/agent workflow bootstrapped into an adopter's
   repository when they choose it?
7. What is the V1 grammar and provider contract for ordinary runtime inputs,
   secret bindings, late secret retrieval, redaction, and noninteractive use?

These questions are part of the product surface. They should be answered in
the user experience before their answers become accidental CLI behavior.
