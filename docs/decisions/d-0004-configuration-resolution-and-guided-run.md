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

D-0002 and D-0003 remain reserved in the handoff for agent autonomy and Gemini
CLI policy respectively, so this discussion is recorded as D-0004.

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
choices. `devcapsule config resolve` is the user's explicit completion signal
and produces an inspectable generated plan. `devcapsule run` requires that plan
to be fresh, materializes the locked environment if necessary, and launches it.

V2 makes `devcapsule run` the main interactive mechanism. Missing, stale, or
incomplete configuration opens a graphical configuration experience, initially
envisioned as an embedded local web application displayed in the browser. The
user sees required choices, optional choices and defaults, recommendations,
authorization effects, and the resulting plan before confirming. Run then
performs the same logical resolution and continues to launch.

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

Adopt Option B as the working direction, subject to human review of the open
questions below.

### 0. The observed project checkout is the CLI context

Most commands operate on one observed checkout: a concrete local directory
containing a project's committed `.devcapsule/` tree. The portable project
identity may have several clones or worktrees on one workstation, so identity
alone is not enough to select developer-owned configuration, state, or
authorization. The canonical checkout path disambiguates them.

The CLI should not require the user's shell to be at the checkout root. It uses
one context-selection rule:

1. a global explicit project path, when supplied; otherwise
2. discovery from the current directory upward to the nearest directory
   containing `.devcapsule/devcapsule.toml`.

The intended forms are:

```text
# From the checkout root or any descendant directory
devcapsule config state use pycharm/system --existing-directory PATH
devcapsule config resolve
devcapsule run

# From anywhere, or when a script/IDE must select one checkout explicitly
devcapsule --project /path/to/checkout config state use pycharm/system --existing-directory PATH
devcapsule --project /path/to/checkout config resolve
devcapsule --project /path/to/checkout run
```

`--project PATH` is a global context option and therefore precedes the command
object. It accepts the checkout root or a path within it, resolves the nearest
containing manifest, canonicalizes the checkout root, and verifies the matching
developer-owned checkout record before applying local decisions. Explicit
selection wins over current-directory discovery. Commands must reject
conflicting legacy command-local selectors rather than guessing precedence.

If neither mechanism finds a declaration, checkout-scoped commands fail with
an actionable message: run from within a DevCapsule checkout or supply
`--project PATH`. They do not search a registry of known project identities and
silently choose one checkout.

Commands whose purpose is to create a declaration, operate only on
workstation-global resources, or use the lock-independent `run-image` expert
path may define a different or optional context. Those exceptions must be
explicit; they do not weaken the normal checkout-selection rule.

The V1 public name is `--project`. It preserves the current user vocabulary and
is clear when followed by a filesystem path. Internally it selects an observed
checkout. `--checkout` is not the primary spelling because it is less familiar
to ordinary users and can be mistaken for a Git operation. The compatibility
period for existing command-local `--project` options remains open.

### 1. V1 configuration is iterative and ends explicitly

V1 presents required choices separately from optional choices with documented
defaults. Users record decisions through CLI operations. Direct editing of the
developer-owned checkout TOML remains available for ordinary values and
non-secret references; generated `devcapsule.resolved.toml` is never an input.

After completing the required choices and any desired optional changes, the
user runs:

```text
devcapsule config resolve
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

### 2. V1 `run` realizes a fresh resolution

`devcapsule run` requires a present, fresh resolution. It may apply explicit
run-once choices without persisting them, acquire and materialize the exact
locked environment, retrieve secrets through declared bindings, construct the
container plan, and launch the foreground development surface.

A missing or stale resolution produces an instruction to run `devcapsule
config resolve`; normal V1 launch does not regenerate it implicitly. Routine
return to an unchanged project remains one command.

### 3. Configuration values have different security and lifecycle semantics

The configuration experience distinguishes at least:

- ordinary values, which may be stored in developer-owned checkout TOML;
- state bindings, which select managed state or an existing external directory;
- secret bindings, which identify a developer-owned provider or source without
  containing the secret value;
- host authorization, which permits a specific workstation exposure; and
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

### 4. State bindings belong to configuration; lifecycle remains a state concern

The current `devcapsule state adopt` syntax is transitional. Choosing managed
or existing storage for a component state slot belongs under the configuration
experience. A candidate direction is:

```text
devcapsule config state use pycharm/system --existing-directory PATH
devcapsule config state managed pycharm/system
```

Inspection and lifecycle operations remain state commands:

```text
devcapsule state list
devcapsule state inspect pycharm/system
devcapsule state move pycharm/system --to PATH
devcapsule state clean --cache
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

When the completed image is absent, the client downloads the locked PyCharm
archive directly from JetBrains on the host, verifies it, builds a deterministic
`devcapsule-local-pycharm:<materialization-identity>` image from the locked
base, and launches that completed image. The container entrypoint performs no
just-in-time component download.

### 6. V2 combines the interaction but preserves the boundary

In V2, `devcapsule run` becomes the primary interactive mechanism and subsumes
ordinary `config resolve` interaction. The graphical flow must distinguish:

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
shown as a deviation. `run-image` remains the arbitrary-image expert escape
hatch and does not claim to reproduce the committed environment.

## Unanswered Questions

This proposal intentionally preserves questions that require further design or
human choice:

1. How should existing command-local `--project` options be deprecated, and
   should supplying both global and local forms always be an error?
2. What exact V1 commands list missing choices, set ordinary values, bind
   secrets, authorize host access, and reset a value to its default?
3. Should `config state use` be the public spelling, should state use a generic
   `config bind` grammar, or is another model clearer?
4. How long should the old `state adopt` command remain as a compatibility
   alias, and what migration warning should it show?
5. Must a fresh user explicitly confirm managed state defaults, or is the safe
   convention sufficient unless the project marks a state choice required?
6. Which V1 secret providers and delivery channels are supported, and how are
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
- Checkout-scoped commands share one global selector and current-directory
  discovery rule instead of each defining its own project-path option.
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
