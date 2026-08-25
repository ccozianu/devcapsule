# DevCapsule V1 User Experience

Status: product design draft; this is not current CLI usage documentation

Audience: developers creating, evaluating, or adopting a DevCapsule-enabled
project

Baseline: every claim in this document about what the tool does today — each
gap, hole, defect, and file:line reference — was verified against `main` at
commit `489642e` (2026-08-22), during the design sessions of 2026-08-23. The
ideal experience specified here is compared against that snapshot and no
other. As implementation catches up, those present-tense observations become
historical notes about `489642e`, not statements about the current tree; they
are deliberately left un-updated so the record of what was wrong, and why each
decision was taken, survives the fix.

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

## Proposed V1 Command Shape

The two principal workstation resource trees are intentionally regular:

```text
devcapsule
├── project [--path PATH]
│   ├── list
│   ├── init
│   ├── checkout register NAME
│   ├── config set|bind|authorize|resolve ...
│   ├── state ...
│   ├── lock ...
│   ├── run ...
│   └── run-image IMAGE ...
└── images
    ├── list
    └── build --type base|environment ...
```

The `project` tree owns declarations, registered checkouts, developer
configuration and state, locks, and execution. This includes the expert,
lock-independent `run-image` path because it still operates on project source,
state, and host choices. The `images` tree owns the workstation's managed image
inventory and image formation.

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

### Where developer configuration is written

The three persistent V1 configuration operations write the developer-owned
checkout input. They never modify the cloned repository:

```text
$XDG_CONFIG_HOME/devcapsule/projects/<encoded-creator>/<encoded-slug>/devcapsule.checkout.toml
```

If `XDG_CONFIG_HOME` is unset or empty, DevCapsule uses `~/.config`, making the
usual location:

```text
~/.config/devcapsule/projects/<encoded-creator>/<encoded-slug>/devcapsule.checkout.toml
```

The file records the decoded project identity and canonical checkout path so
it remains understandable and recoverable. It is created with mode `0600` and
must never contain secret values. Additional clones or worktrees use their
accepted named-checkout files beneath the same project-identity directory so
one checkout cannot inherit another checkout's permissions.

DevCapsule documentation and successful configuration mutations show the
actual path written. Users may edit ordinary values and non-secret provider
references in this file directly. The adjacent `devcapsule.resolved.toml` is
generated output and is never edited as configuration input.

## The First Run: Cases And Properties

Every first run is the same act: bring the four items in *Four Things With
Different Owners* into existence, in owner order. The cases differ only in
which of them already exist and who authors the rest.

Three cases are canonical, accepted by the product owner on 2026-08-23:

| Case | The user's position | Manifest | Platform lock | Checkout configuration | Materialized image |
| --- | --- | --- | --- | --- | --- |
| **New project** | an idea, no code yet | authored here | authored here | authored here | built here |
| **Existing project** | code exists, not onboarded | authored here, against existing code | authored here | authored here | built here |
| **New checkout** | the project already carries DevCapsule settings | given | given | authored here | built or reused |

Related situations are sub-cases of these three, not additional cases. They are
recorded because the common story must survive them, and because each one
currently reaches a question this narrative does not answer:

- **No platform lock for the user's platform.** The lock is per-platform and
  the filename says so; the client derives the alias from the host
  (`platform_alias()`, `project_configuration.py:599`). A user on a platform
  the project has never locked has a complete and correct project half and
  still cannot run. A sub-case of *New checkout*.
- **A second checkout of the same project on one workstation.** Named checkout
  files live under the same project-identity directory precisely so that one
  checkout cannot inherit another's permissions. Some settings for this project
  demonstrably exist on this machine and are deliberately withheld; what may be
  offered and what must be re-answered is unstated. A sub-case of *New
  checkout*.
- **A fork or template instantiation.** Manifest and lock are inherited, but
  project identity must not be: `creator` and `slug` key the checkout
  directory. Looks like *New checkout*, must behave like *New project* on
  exactly those fields.
- **An evaluator** who wants to know what a run will do to their machine before
  authorizing it. A display and acknowledgement question inside *New checkout*.
- **A learning or course project**, named as the third adoption moment in
  `docs/product/v1-announcement.md`. Many disposable checkouts of one upstream
  project, by users who are not its owners.
- **An existing project that already carries an environment definition** — a
  devcontainer, a Dockerfile, a virtualenv recipe. This changes what
  initialization may infer, not the shape of the case. A sub-case of *Existing
  project*.

### Properties The First-Run Story Must Satisfy

1. **A first run reaches a running capsule in the documented minimum for its
   case**, and that minimum is stated for each of the three cases. Today no
   document states it: four sources describe mutually inconsistent first-run
   flows, and none of them is the implemented one.
2. **An upgraded client requires nothing of the user.** See `R-COMPAT-001`.
   This property is not about the first run of DevCapsule on a project; it is
   about every later run, and it constrains the same code the first run
   exercises.

### Non-Interactive Runs Are Handled Elsewhere

Runs with no human present — scripted, automated, or agent-driven, whether the
first run or a later one — are deliberately outside this narrative. They are
not deferred: the product owner ruled on 2026-08-23 that they block the V1
release. The item was delivered to `project-management` on that date for
ownership and sequencing.

The two properties above and the three cases still apply to them. What does not
apply is every interaction this narrative uses to satisfy those properties:
vendor-acquisition acknowledgement, authorization prompts, and any question
asked at a terminal.

### What This Narrative Does Not Yet Settle

The common story itself is open work. Known holes, each verified against the
current tree:

- **The platform lock is authored by nobody** — settled 2026-08-23: `init`
  authors it as part of its postcondition; see *Initializing A New Project*.
- **`devcapsule project lock` cannot author a V1 lock.** It is a dogfood stub
  that requires an existing local image reference and writes neither a pinned
  base nor component digests nor a materialization recipe. Generation now
  belongs inside `init`; settled 2026-08-24: no standalone regeneration
  command survives — the stub is retired and `init --regenerate` is the
  deliberate regeneration spelling. Locks the stub already wrote remain
  readable per `R-COMPAT-001`.
- **The four first-run flows disagree.** `D-0001` section 9,
  `docs/product/v1-announcement.md`, and the implementation still describe
  sequences that the specification below supersedes for the first case, and
  the announcement's verbs do not exist in the CLI. The second and third
  cases are not yet written.

*Initializing A New Project* below is now the settled specification for the
first case. *Starting From An Existing Repository* remains the partial
pre-existing account of the third case, preserved until that case is written,
and should be read as evidence rather than specification.

## Initializing A New Project

Settled with the product owner on 2026-08-23. This section is the
specification for the first canonical case; the sequence and option spelling
may be refined, but the postcondition, the three entry states, and the
derive/ask discipline are decided.

### The Postcondition

A successful `devcapsule project init` leaves the project **fully
initialized and runnable by its owner**: a valid `.devcapsule/devcapsule.toml`
and at least one usable platform lock exist, the owner's checkout record is
registered, and a fresh resolution stands. `init` achieves the last two by
internally invoking `config resolve` once its own questions are answered, so
`devcapsule project init` followed by `devcapsule project run` is the entire
first-run experience for a project owner. There is no separate mandatory lock
step, and no path on which the tool later interrupts ordinary work to demand
one. The old flow —
`init`, then a printed instruction to generate the lock by other means — is
retired; it documented a dead end, because the standalone lock command cannot
author a V1 lock.

"At least one" is deliberate. A project locked for one platform is complete;
a missing lock for the current platform is the collaborator sub-case of *New
checkout*, not an incomplete initialization, and growing another platform's
lock is always an explicit act rather than something inferred from a platform
mismatch.

### The Lock Is A Record, Not A Mandate

The platform lock is the durable record of one resolution: the version set
and property defaults that the resolution matrix derived from the normalized
capability set and the target platform. Committing it is what makes the
project optimally consumable by collaborators — reproducible, reviewable in
Git, and free of first-run surprises — and producing it is therefore an
owner-side obligation attached to `init`, the one moment the tool knows with
certainty that the user is the owner.

It is not a permission gate. During normal usage the tooling must never
refuse ordinary work with an instruction to run a lock-generation command;
the checkout-side resolution layer, whose source digests exist for exactly
this purpose, is where drift is detected and remedied. A present lock is
always honored, never silently ignored; an absent one is a shareability gap
for the owner to close, not a reason to stop a consumer.

### Three Entry States

1. **Nothing is initialized.** `init` creates the declaration and the
   platform lock in one action.
2. **Partially initialized.** A manifest without a lock, an orphan
   `.devcapsule/` directory, the debris of an interrupted `init` — the
   command completes what is missing and honors what exists. No flag is
   required; repair is `init`'s own job. This replaces the current
   create-only refusal, under which a crashed `init` produces a project that
   can never be initialized and an error message pointing at a file that may
   not exist.
3. **Fully initialized.** `init` fails loudly, stating that the project is
   complete and naming `--regenerate` as the deliberate way forward.

A hand-authored or copied `devcapsule.toml` is the ordinary form of state 2,
not an error: the owner may have written it in an editor or carried it over
from a reference project. `init` honors it and generates what follows from
it.

### Derive, Report, Ask

The line between what `init` decides and what it asks is fixed, because
"best effort plus a message" is exactly how silent decisions are born:

- **Derive and report** what follows from the user's declaration: component
  versions, digests, and the materialization recipe from the resolution
  matrix; name, slug, and mount from the directory and defaults, overridable
  by flag. These are facts the user can inspect but is never asked about.
- **Ask** what encodes intent the tool cannot derive: the security-sensitive
  host-access recommendations — network mode, docker daemon,
  development sudo. The manifest schema already requires a `justification`
  alongside each recommended value, so the interactive prompt collects
  precisely what the format demands.

What `init` collects from the owner are the project's **recommendations**.
Every consumer still authorizes their own checkout; the owner's answers at
`init` spare consumers nothing on the security tier, so no checkout ever
inherits a permission through the project.

Every question has a flag, and interaction happens only where flags are
absent — the `ssh-keygen` model. A fully-flagged invocation is therefore
noninteractive by construction, which is the down payment on the
non-interactive operation item delivered to `project-management`.

### Offline And The Embedded Matrix

The client ships a minimal embedded resolution matrix with base digests
pinned, so `init` resolves entirely from local data: it is a pure
file-producing command that requires no network and no host capability. In
particular it never probes the container daemon — the daemon is exactly the
capability that requires explicit authorization, and creating a project must
not depend on it. When `init` resolves offline it says so, warning that the
embedded matrix was used without checking for updates. Whether the locked
base image is actually present locally is `run`'s discovery, made at run
time with its own remedy.

The `resolution-matrix-version` recorded in the lock is informational,
per `R-COMPAT-001`. A newer client's matrix changes what would be generated
next time, never the validity of the lock that stands. No code may compare
the recorded matrix version against the client's and refuse.

### `--regenerate`

`--regenerate` rewrites the derived and keeps the authored: it re-runs
resolution against the current matrix and rewrites the platform lock, and it
does not discard the manifest the owner wrote. Git sees an ordinary
modification; `init` never runs git commands on the user's behalf.

It deliberately does not touch the developer-owned checkout records under
the configuration root. The digest bindings do that work with precision: a
regenerated lock changes the digest the base-image authorization accepted,
so that acceptance goes stale and is re-asked, while authorizations bound to
unchanged recommendation subtrees remain valid. Invalidation lands exactly
where regeneration touched, and a project-side command never deletes a
developer-owned record.

A truly blank slate — removing `.devcapsule/` from the tree and the
project's directory under the configuration root — is a burdensome,
error-prone, cross-tree cleanup, and a partial one is dangerous: re-creating
a project under a surviving checkout record would let the old project's
authorizations attach to the new one. `--regenerate` exists so users are
never pushed toward attempting it by hand.

### Every Node Has One Name

Every node in the configuration tree that can need user input is addressable
on the command line by the same canonical name the `config` family uses.
`init` does not invent a parallel flag vocabulary: the spelling accepted by
`config set`, `config bind`, and `config authorize` is the spelling `init`
accepts, so the prompt and the flag are guaranteed to agree, and anything the
tool can ask can also be pre-answered.

#### The settled grammar (2026-08-24)

Settled with the product owner on 2026-08-24, answering open questions 2 and
7 of *Questions This Narrative Must Settle*; this is intended to be the last
redesign of the configuration argument syntax.

The governing principle: **flags name mechanics, nodes name content.** A
datum that would appear in the manifest, lock, checkout record, or resolution
is a node, addressed by its one canonical name through the regular grammar on
every command; flags are reserved for facts about the invocation itself
(`--path`, `--json`, `--force`, `--regenerate`, container `--name`). Adding a
component, capability, or host boundary therefore adds registry rows, never
syntax.

Every configuration mutation is `VERB NAME VALUE`:

```text
devcapsule project config set        NAME VALUE
devcapsule project config bind       NAME PROVIDER:VALUE
devcapsule project config authorize  NAME VALUE [JUSTIFICATION]
devcapsule project config unset      NAME
```

- The three verbs remain distinct because the security tiering is
  intentional; `unset` is the one reset spelling for every family.
- `bind` values carry their provider in the value (`host-directory:PATH`,
  `host-environment:VARIABLE`), split on the first colon against the node's
  closed provider set, so new providers are new value prefixes rather than
  new flags.
- The optional trailing `JUSTIFICATION` token exists for recommendation
  authoring at `init`; a consumer authorizing an already-declared
  recommendation never supplies one, because an answer's justification lives
  with the question in the manifest.
- `init` and `run` carry the same spellings through repeatable carrier
  options: `--set NAME VALUE`, `--bind NAME PROVIDER:VALUE`,
  `--authorize NAME VALUE [JUSTIFICATION]`. The scope of an answer comes
  from the command: `init` persists into the owning artifact, `run` applies
  once, echoes the deviation, and writes nothing.
- `run [RUN-OPTIONS] -- DOCKER-RUN-OPTIONS` hands everything after the first
  standalone `--` verbatim to `docker run` (settled 2026-08-24): DevCapsule
  stops modeling docker's option surface; raw options are conspicuously
  reported as a deviation from the resolved plan. The bespoke run flags
  (`--docker-daemon`, `--development-sudo`, `--host-browser`) are dropped
  from `run`; `run-image` keeps its dedicated flags because it deliberately
  reads no lock and therefore has no node registry.
- `host-browser`, `docker-daemon`, and `development-sudo` are proper
  authorization nodes (settled 2026-08-24) that exist on every project as
  workstation capabilities: denial stays the default, a project
  recommendation merely attaches its justification and rebinds the answer's
  digest, and `--all-recommended` never includes an unrecommended
  workstation capability. `host-browser` gains the recommendation path
  `[host.browser.host-open.recommended]` and is now persistable, closing the
  gap where it existed only as a per-launch flag. Host networking is
  deliberately not a workstation default: its run-once form is the docker
  passthrough, and its persistent relaxation remains a project-recommended
  decision.
- Uniqueness of node names is enforced by construction in the node registry
  (`devcapsule/configuration_nodes.py`); a name that means two things would
  make the grammar and the prompt ambiguous.

Two subsidiary decisions of the same date: the CLI parses with a small owned
framework over stdlib `argparse` (variable-arity carriers are exactly what
Click cannot declare through public API), superseding the Click architecture
brief in `click-based-cli-parsing-brief.md`; and a noninteractive `init`
records no recommendation for an unflagged host-recommendation intent
question — the same answer as pressing Enter — while acquisitions with no
safe omission (`base-image`, `claude-code-download`) batch-fail with
copy-pasteable remedies.

### One Elicitation: Init Ends Resolved

Settled with the product owner on 2026-08-23. For any node, the value is
sought in one fixed order, and a prompt is only ever the last resort:

1. the command line;
2. an answer already given earlier in the same flow;
3. an existing record — manifest, lock, or checkout configuration;
4. a derivable default;
5. otherwise, if the node is mandatory: prompt, `ssh-keygen` style.

Asking a question whose answer exists upstream of step 5 is a defect. When
`init` invokes `resolve` internally, the user is never asked the same thing
twice — not by special-case plumbing, but because each answer is written
immediately into the artifact that owns it: a recommendation with its
justification into the manifest, an authorization or checkout value into the
developer-owned checkout record. The internally invoked `resolve` then reads
those records exactly as a standalone `resolve` would, and finds every
question answered. There is no separate answer cache; a persistent one would
be a fifth artifact with no owner in *Four Things With Different Owners*, and
a second source of truth that can drift from the first.

For the project owner at `init`, one prompt legitimately serves two acts:
answering "network mode: host, because ..." records the project's
recommendation and, in the same stroke, the owner's own checkout
authorization. The two remain distinct artifacts with distinct owners; they
merely share an elicitation for the one person who is both. No other checkout
inherits anything from it.

In a noninteractive context, a mandatory node that reaches step 5 is a clean
failure that lists **all** missing nodes at once with their canonical names —
batch mode, not death at the first missing answer. A fully specified command
line therefore never prompts and ends resolved, which is the noninteractive
first run by construction.

### The Scoped-Digest Principle

Every derived artifact records digests of exactly the inputs it derives
from, and nothing more. The manifest-digest failure was a violation of
precisely this: the lock derives from the capability set and the platform,
but recorded a digest of the entire manifest, so a workflow-protocol field —
an input to nothing the lock contains — could invalidate it fatally.

Project identity is an **address, never an input**: `creator` and `slug`
locate records, and no derived artifact's validity may depend on them, so
renaming a project invalidates nothing.

Still open in this specification: relocation of checkout records when project
identity changes.

### Change Arriving From The Project Remote

Settled with the product owner on 2026-08-23. A `git pull` can change the
project's half of the configuration tree under a consumer's feet. This is the
situation the retired whole-manifest digest gate was defending against, and it
is handled by the machinery above without new mechanism — which is the test
the machinery was designed to pass. What arrives is one of three kinds of
thing:

1. **A new demand** — a mandatory node this checkout has never answered. Under
   the elicitation order this is indistinguishable from a first-run unanswered
   node: the value is absent everywhere upstream of the prompt, so the next
   `resolve` or `run` asks it, once. The consumer meets a new project
   requirement exactly the way the owner met it at `init`.
2. **A changed question** — a recommendation whose value or justification
   moved. The checkout's authorization is bound to that recommendation
   subtree's digest, so it goes stale — correctly, because an answer must not
   outlive its question. Exactly that node is re-asked. This is what the
   retired gate got right in kind and wrong in everything else: right that a
   changed input demands attention; wrong in scope (a whole-file hash), wrong
   in remedy (a command that could not help), and wrong in fatality (blocking
   even inspection).
3. **Changed derived facts** — a new platform lock from the owner: a new base
   digest or bumped components. The base-image acceptance is bound to the old
   lock digest and goes stale; one re-acceptance shows old and new. Nothing
   else in the checkout is touched, because nothing else derived from what
   changed.

A change to project identity or to workflow protocol fields invalidates
nothing, because identity is an address and no derived artifact consumes those
fields. The failure that motivated this section is structurally impossible
here.

Three properties keep the choice with the user:

- **Show the diff, not the demand.** Every re-ask displays what changed, from
  what to what, and the upstream justification. The user is deciding, not
  complying.
- **Declining is an answer.** A "no" is recorded like any other answer and is
  not re-asked at every run. What a decline means is graded per node: a
  declined base-image acceptance may mean continuing on the previously
  accepted formation as an explicit, recorded deviation (see *Select a
  different environment explicitly*); a declined new mandatory demand may mean
  the project genuinely cannot run for this checkout. The tool states which
  consequence applies; it never bare-refuses.
- **Inspection never gates.** `config list` and every other read-only command
  work in every drift state and display the pending questions. The state the
  user must reason about is the state the tool must show.

Drift is detected when the tool reads — at `resolve` and `run` — never by
watching the repository; the pull is git's business. The experience is: pull,
`run`, and `run` reports "the project changed these things" and walks exactly
those nodes. Whether that walk happens inline in `run` or by directing to
`resolve` is the V1/V2 seam recorded in *V2 direction: configuration inside
`devcapsule project run`*.

## Starting From An Existing Repository

The developer first installs the released DevCapsule client, then clones a
project that already carries its declaration and platform lock:

```bash
git clone "$PROJECT_GIT_URL" "$CHECKOUT"
cd "$CHECKOUT"

devcapsule project config resolve
devcapsule project run
```

That is the shortest path when all required choices have safe defaults. A
project or developer may require zero or more configuration operations before
resolution. For example:

```bash
# Ordinary checkout-owned value; validate the size before recording it.
devcapsule project config set runtime.memory-limit 8GiB

# Use an existing host directory for a declared PyCharm state slot.
devcapsule project config bind pycharm/system --host-directory "$PYCHARM_SYSTEM"

# Explicitly allow this checkout to use the host Docker daemon.
devcapsule project config authorize docker-daemon host-socket

devcapsule project config resolve
devcapsule project run
```

The names and option spelling are the V1 design target and may be refined
before the interface is released. Their different meanings are intentional:
`set` records an ordinary value, `bind` selects a developer-owned provider for
a declared logical resource, and `authorize` permits a security-sensitive host
capability.

The project is already initialized. An ordinary adopter does not run
`devcapsule project init`, generate a new shared lock, build a base image, find
an IDE archive, or invoke a product-specific image build.

### Selecting the checkout

DevCapsule normally discovers the checkout by searching from the current
directory upward for `.devcapsule/devcapsule.toml`. The user may run commands
from the checkout root or any directory beneath it.

Working from elsewhere must also be supported. The `project` subtree accepts
one optional context path before its subcommand:

```bash
devcapsule project --path /path/to/checkout config resolve
devcapsule project --path /path/to/checkout run
```

This is especially useful for scripts, IDE integrations, and workstations with
multiple clones or worktrees of the same portable project identity. The path
selects the concrete checkout and therefore its developer-owned configuration,
state, and authorization. DevCapsule never chooses among known checkouts by
project identity alone.

If that portable identity already has a default checkout registered at another
canonical path, the developer assigns the new checkout a workstation-owned
name once. The manually accepted second-checkout dogfood flow used:

```bash
devcapsule project --path /path/to/second/checkout \
  checkout register costin3-devcapsule
```

This creates the distinct
`checkouts/costin3-devcapsule.checkout.toml`/`.resolved.toml` pair. Later
commands select it from the observed path without repeating the name. The
operation must fail rather than overwrite or inherit the first checkout's
state and host authorization.

The user is not required to change directories merely to operate on another
checkout. Conversely, an explicit path or discoverable `.devcapsule/` tree is
required for normal checkout-scoped commands. The V1 public spelling is
`devcapsule project --path PATH SUBCOMMAND`; internally, the resolved path
identifies the observed checkout. The optional positional form `project .` is
not supported because it is ambiguous with subcommand names.

### Listing registered projects and checkouts

DevCapsule maintains a developer-owned registry beneath:

```text
$XDG_CONFIG_HOME/devcapsule/projects/
```

With the normal XDG default, that is `~/.config/devcapsule/projects/`.

```bash
devcapsule project list
```

The command enumerates valid checkout records from this registry. It does not
scan Git repositories, home directories, or mounted filesystems for source
trees. Merely cloning a DevCapsule-enabled repository—or running `project init`
to create a declaration—does not register that checkout. It first appears
after a persistent `project config set`, `bind`, `authorize`, or `resolve`
operation creates its developer-owned checkout record.

The list identifies the portable project, checkout name when applicable,
canonical checkout path, and status. A registered checkout whose source path
has disappeared remains visible as `missing` so cleanup is deliberate rather
than silent.

### V1: why `project config resolve` and `project run` are separate

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
devcapsule project config resolve
```

This command is the explicit “my configuration choices are complete” signal.
It validates that every required choice has an effective value, applies
documented defaults for optional choices that were left unset, and produces
the final inspectable local resolution. If required decisions are still
missing or contradictory, it fails with actionable CLI or TOML instructions
instead of partially resolving or launching.

`devcapsule project config resolve` is the local planning and review phase. It:

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

Each preceding `set`, `bind`, or `authorize` operation performs the strongest
useful local validation before writing the checkout input. For example, a
memory limit must parse and satisfy applicable policy; a host-directory binding
must name a suitable existing directory and expose its mount consequences; and
host Docker authorization must display the risk of control over the host
daemon. `project config resolve` then performs the holistic validation that no
single operation can: completeness, cross-field consistency, project and lock
compatibility, policy, source digests, and the combined host-exposure plan.

`devcapsule project run` is the realization and execution phase. It:

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
resolution produces an actionable instruction to run `devcapsule project
config resolve`; it is not regenerated implicitly as a side effect of launch.

The cost is one explicit command for a new checkout and after configuration
inputs change. The normal return-to-work experience remains one command:

```bash
devcapsule project run
```

That is the “launch in one command” product promise. Resolution is setup and
change review, not a step repeated before every session.

### V2 direction: configuration inside `devcapsule project run`

In V2, `devcapsule project run` becomes the main user mechanism and subsumes the
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

The explicit `project config resolve` operation may remain available in V2 for
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
devcapsule project state adopt home --from "$LEGACY_STATE/home"
devcapsule project state adopt pycharm/config --from "$LEGACY_STATE/config"
devcapsule project state adopt pycharm/plugins --from "$LEGACY_PLUGINS"
devcapsule project state adopt pycharm/system --from "$PROJECT_STATE/system"
devcapsule project state adopt pycharm/log --from "$PROJECT_STATE/log"
devcapsule project state adopt pycharm/cache --from "$PROJECT_STATE/home/.cache"

devcapsule project config resolve
```

Those commands do not install or configure PyCharm. They tell DevCapsule to
mount six existing host directories instead of allocating fresh managed state.
They are required for that migration test's continuity criteria, not for an
ordinary clean clone.

The current implementation makes this distinction awkward because its
top-level `config resolve` requires a developer checkout file and top-level
`state adopt` is the implemented path that creates one. V1 must add
clean-checkout bootstrap so a user accepting managed defaults can reach
`project config resolve` without performing a fictitious adoption.

The V1 replacement models those migrations as resource bindings. The first
clean-clone dogfood milestone only needs the existing-host-directory provider:

```bash
devcapsule project config bind home --host-directory "$LEGACY_STATE/home"
devcapsule project config bind pycharm/config --host-directory "$LEGACY_STATE/config"
devcapsule project config bind pycharm/plugins --host-directory "$LEGACY_PLUGINS"
devcapsule project config bind pycharm/system --host-directory "$PROJECT_STATE/system"
devcapsule project config bind pycharm/log --host-directory "$PROJECT_STATE/log"
devcapsule project config bind pycharm/cache --host-directory "$PROJECT_STATE/home/.cache"
```

Managed state is the safe default and requires no binding command. The exact
compatibility lifetime of `state adopt` and the reset-to-managed spelling
remain migration details to settle before release.

### What can be bound

A binding connects a logical resource declared by the project or one of its
components to a developer-owned provider. It is not a generic spelling for all
Docker options.

The next dogfood milestone supports one provider:

- **Existing host directory:** persistent component state such as `home` or
  `pycharm/system`. DevCapsule validates the path and explains that it will be
  exposed to the container before recording it.

Potential later providers include:

- a host file for non-secret configuration or a certificate;
- an environment variable, narrowly scoped secret file, operating-system
  keychain, or password-manager entry as a secret source;
- a local agent socket such as an SSH or GPG agent endpoint;
- a named developer profile whose state contract is known to DevCapsule; and
- another persistent storage backend, such as a named Docker volume, when its
  lifecycle and portability rules are specified.

These are candidates, not current V1 commitments. Every added provider needs a
readiness check, container delivery contract, inspection behavior,
noninteractive semantics, and redaction rules where secrets are involved.
Devices, Docker-daemon access, host networking, privilege changes, and port
publication are authorizations rather than generic bindings.

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

`project config resolve` then verifies that every required ordinary value has
an effective value and every required secret has a valid binding. Its
generated plan records the secret's logical name, provider reference, delivery
method, and readiness status, but never the secret value. A missing required
binding blocks resolution. Optional inputs use their documented defaults or
remain disabled.

At `project run`, DevCapsule retrieves each secret as late as practical,
injects it only through the declared channel, redacts it from output, and does
not allow it to affect the materialized image or Docker build cache. Rotating
a value behind an unchanged binding therefore does not require a new project
lock or image.

Database configuration may also imply a separate host-boundary decision. For
example, reaching a database bound only to the host may require an explicit
network choice. Supplying database credentials does not implicitly authorize
that network exposure, and authorizing the network does not supply the
credentials.

## What Happens On The First Run

`devcapsule project run` discovers the project and uses the committed lock. If
the completed local image is absent, DevCapsule:

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

Closing the IDE ends the container. A later `devcapsule project run` reuses the
cached artifact and completed image when the locked identities have not
changed, and reuses the checkout's persistent home and component state.

### Local image names and developer builds

Materialized images have a stable, advertised local naming contract:

```text
devcapsule-local-<component>:<materialization-identity>
```

For the initial PyCharm environment this is:

```text
devcapsule-local-pycharm:<materialization-identity>
```

The identity comes from immutable formation inputs, not from the project name.
Projects using identical base, component artifact, and recipe identities can
therefore reuse the same image while retaining separate source mounts, state,
configuration, and authorization.

#### How several projects share one materialized image

Each project lock selects inputs; it does not create a project-owned copy of
the image. DevCapsule forms a versioned canonical descriptor from the target
platform, immutable base-image identity, every component artifact identity and
digest, the materialization recipe and its formation parameters, and the
generic component runtime-template digest. It computes the full SHA-256 of
that descriptor.

Project identity, the lock-file digest itself, checkout paths, source, local
resolution, project mounts, developer UID/GID choices, state, credentials,
authorization, and aliases are excluded. Consequently:

```text
Project A lock ─┐
                ├─ identical formation descriptor
Project B lock ─┘              │
                               ▼
          devcapsule-local-pycharm:<identity>
```

When Project B reaches materialization, DevCapsule computes the same full
identity, parses the canonical formation descriptor stored in the image
metadata, verifies that its hash is the full identity, and reuses the image
only when its base, recipe, and complete component identities match. An
identity label without the matching descriptor is insufficient. A malformed
or conflicting canonical tag causes an actionable failure rather than silent
use or replacement. No sharing declaration or project-to-project reference is
needed.

The committed base input uses a globally resolvable, digest-pinned OCI
distribution reference such as
`docker.io/ORGANIZATION/devcapsule-base@sha256:DIGEST`. It does not use a
workstation-local image ID, daemon-local tag, mutable tag, or `docker://` URI.
Those local forms remain available only as explicit developer-owned
overrides. The committed platform lock is therefore the reviewed default that
a fresh checkout can obtain on another compatible workstation, subject to
registry reachability and workstation policy.

Projects cannot force reuse when formation inputs differ. They receive
distinct content-addressed images even if a human assigns similar aliases.
This preserves each project's lock contract while still deduplicating the
common case automatically.

The shared image contains only immutable component formation and a generic
runtime template. At `project run`, DevCapsule supplies the checkout-specific
launch plan read-only from outside the image. Project source, actual mount
paths, developer identity, state directories, authorizations, and secrets
therefore remain separate for every run.

Ordinary users never need to invent this name or build the image directly.
After configuration resolution, `devcapsule project run` reports the expected
name, reuses it when present, and otherwise performs locked materialization
before launch.

DevCapsule developers have two explicit operations:

```bash
# Build the JetBrains-free generic runtime base from the current PEX.
scripts/build-pex.sh
devcapsule images build \
  --type base \
  --recipe ubuntu-24.04 \
  --pex dist/devcapsule.pex \
  --source-revision "$(git rev-parse HEAD)" \
  --network host \
  --tag devcapsule-base:debug-v020

# Materialize this project's required components onto a local or registry base.
devcapsule images build \
  --type environment \
  --project "$CHECKOUT" \
  --base devcapsule-base:debug-v020 \
  --alias devcapsule-local-pycharm:debug-v020
```

The second command still creates the canonical content-addressed image first.
The optional alias is a local debugging convenience and is never presented as
the reproducible identity. A registry base uses the same operation with an
immutable reference, for example:

```bash
devcapsule images build \
  --type environment \
  --project "$CHECKOUT" \
  --base docker.io/ORGANIZATION/devcapsule-base@sha256:DIGEST
```

`images build --type environment` acquires, verifies, and assembles without
launching. It
shows the selected base identity, component artifact identities, recipe, and
canonical output name. An explicit base override is displayed as a deviation
from the project's lock and does not silently become the supported project
default.

V1 deliberately supports two base-trust paths. A developer may build a managed
base locally with `images build --type base` and select that inspected image
explicitly through `--base`. Or the developer may authorize the exact
digest-pinned registry base recommended by the project after reviewing its
release information, published checksum, and basic security scan. The lock is
a recommendation and cannot authorize its own executable artifact. Persistent
authorization belongs to the developer-owned checkout record and is scoped to
one immutable digest or inspected local image ID, never to a mutable tag,
repository, organization, or future digest.

V1 checksum publication proves byte identity, and its basic scan reports known
findings at one point in time; neither proves source equivalence or absence of
malicious behavior. Signed SBOMs, build provenance/attestations, artifact
signatures, and automated trust-policy verification are explicit V2 work.

#### What `images build --type base` produces

`devcapsule images build --type base` creates one reusable OCI
development-runtime image. It
does not create a complete project environment and does not launch anything.
The initial Linux contract includes:

- Ubuntu 24.04 as the default root image;
- Python 3.12, pip, virtual-environment and development-header support;
- Git, OpenSSH, compiler/build tools, GDB/LLDB, and common process, filesystem,
  shell, and network diagnostics;
- Docker CLI, buildx, Compose, and daemon binaries;
- X11/GTK, font, audio, and Mesa libraries needed by later GUI components;
- `tini`, `gosu`, and `sudo` without granting sudo or Docker access;
- the recipe-selected Node.js/npm language-tooling baseline; and
- the selected DevCapsule PEX at
  `/opt/devcapsule/bin/devcapsule.pex` with an inspectable SHA-256 identity.

Users do not have to infer this inventory from a published image. The
repository-owned Python plan is intentionally auditable:

- [`base_image.py`](../../../devcapsule-src/devcapsule/base_image.py) defines the base
  recipes, root images, labels, embedded PEX, and generic OCI process contract.
- [`_image_build.py`](../../../devcapsule-src/devcapsule/configurations/pycharm/_image_build.py)
  currently contains `BASE_APT_PACKAGES`, the exact shared Ubuntu package
  baseline. Its transitional location does not add PyCharm to the base.
- [`image_tooling.py`](../../../devcapsule-src/devcapsule/image_tooling.py) contains
  the pinned Node.js/npm acquisition and verification plan.
- [`image_build.py`](../../../devcapsule-src/devcapsule/image_build.py) renders the
  Python component plan into the Dockerfile/build context used by buildx.
- [`container_runtime/`](../../../devcapsule-src/devcapsule/container_runtime/)
  contains the generic runtime shipped inside the embedded PEX.

In plain language, the default is Ubuntu 24.04 plus Python 3.12, native build
and debugging tools, Git/SSH, shell/process/filesystem/network diagnostics,
Docker client/buildx/Compose/daemon binaries, desktop runtime libraries,
`tini`, `gosu`, non-authorized `sudo`, pinned Node.js/npm tooling, and the
DevCapsule PEX. The base is deliberately IDE- and agent-neutral and contains no
project, personal state, credentials, host access, or vendor license
acceptance.

The base builder exposes two curated recipes:

```text
ubuntu-24.04       default; Ubuntu 24.04 plus the developer baseline above
nvidia-cuda-devel  WIP; NVIDIA CUDA 12.8.1 development image for Ubuntu 24.04
                   plus the same developer baseline
```

The CUDA recipe does not authorize or expose a host GPU. Runtime device access
is a separate developer-owned authorization. The recipe is intentionally
marked WIP in command output and image metadata until the V1-blocking NVIDIA
host E2E task proves the CUDA compiler/runtime, positive GPU launch, negative
launch without device authorization, and a small real CUDA workload.

The public-tool recipe selects Node.js `v22.23.1`; npm is the version bundled
by that verified Node.js distribution. No AI-agent CLI is installed in the V1
default base. Agent CLIs change on an independent cadence and may carry
different terms, authentication, state, and trust implications, so they belong
to explicit optional components rather than the ambient runtime. The build
report and component inventory remain the authority for exact installed
versions in a particular image.

Gemini CLI is not a supported DevCapsule component. It is not installed,
selected, configured, or supplied with state by active V1 workflows. A check
that it is absent guards the agent-neutral inventory; it is not a supported
feature test.

The PEX contains both the host CLI and the generic in-container runtime. The
base starts that runtime through:

```text
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]
CMD ["/etc/devcapsule/runtime-plan.json"]
```

The base deliberately does not provide the referenced runtime plan. A bare
base therefore reports a missing-plan error. `images build --type environment`
supplies a generic component runtime template together with the selected IDE
or other component. At launch, `project run` supplies the checkout-specific
plan read-only at the runtime-plan path; that plan is never baked into the
shared image.

The base contains none of the following:

- PyCharm, another IDE, vendor archives, or a product-specific entrypoint;
- project source, `.devcapsule/` project files, or checkout configuration;
- developer home/state, credentials, secrets, or agent login data;
- host mounts, Docker-daemon authorization, host networking, devices, or sudo
  authorization; or
- vendor EULA or license acceptance.

Installing Docker and sudo binaries is not authorization to use them. Runtime
access remains controlled by the project's resolved plan and explicit
developer-owned decisions.

`--recipe` defaults to `ubuntu-24.04`; `--from` accepts a local or registry
root-image reference and overrides that recipe's default root. DevCapsule
reuses the selected image from the local Docker store when present and
otherwise obtains that reference from its registry. When DevCapsule is itself running
from a PEX, that PEX is the default embedded artifact; `--pex PATH` selects one
explicitly. `--tag` is the requested local output name. The PEX embeds its
source repository, full revision, and canonical public commit URL when
packaged. `--source-revision` asserts that embedded revision rather than
supplying a second independent value. Public source is mandatory by default;
`--allow-local-source` is the explicit dirty/unpublished development escape
hatch and records an unknown revision.

`--network` accepts `default`, `host`, or `none` and is forwarded to Docker
buildx. The default uses Docker's normal build network. `none` disables build
networking. `host` is an explicit build-time isolation relaxation for builds
that require services or routing available through the host network; DevCapsule
also supplies BuildKit's required `network.host` entitlement. This choice
affects only image construction and grants no host networking to a later
capsule run.

The build may still use network access for declared package and tooling
installation. DevCapsule records the immutable base identity actually used, so
later materialization does not confuse two different images that happened to
use the same mutable tag. A digest-pinned project base is never silently
replaced by different registry content.

On success, the command reports:

- the requested output tag and immutable local image ID;
- resolved root-image identity and base-recipe version;
- source revision and embedded PEX SHA-256;
- selected public-tool versions; and
- the package/component inventory needed for inspection and licensing.

A local debug build may start from a convenience tag such as `ubuntu:24.04`,
but its resolved immutable image ID becomes part of the later materialization
identity. A publishable base requires pinned formation inputs and complete
license/inventory evidence.

#### How `images list` identifies DevCapsule images

`devcapsule images list` reads the local Docker image store and shows only
images carrying the V1 managed-image marker. Names are not used as proof: an
image remains recognizable after retagging, while an unrelated image does not
become managed merely because somebody names it `devcapsule-local-something`.

Every V1 DevCapsule image carries:

```text
devcapsule.image.managed=true
devcapsule.metadata.version=1
devcapsule.image.kind=base|materialized
```

Base images additionally identify their recipe, embedded PEX digest, source
repository, full revision, and commit URL through DevCapsule and standard OCI
metadata. Materialized environment images identify their full formation
identity, base identity, recipe, primary component and artifact digest, and
canonical `devcapsule-local-<component>:<short-identity>` name.

The default display has one row per immutable local image ID, even when the
image has several tags. It shows:

```text
KIND  CANONICAL NAME  ALIASES  IMAGE ID  COMPONENT  RECIPE  CREATED  SIZE
```

Unknown metadata versions remain visible as `unsupported-metadata`; malformed
label sets appear as `invalid-metadata`. Listing is classification rather than
a security decision, so launch and reuse still verify the platform lock and
formation identities.

The earlier `devcapsule.configuration=pycharm` label is legacy metadata and is
not sufficient for the default list. Developers may inspect those transitional
images explicitly with:

```bash
devcapsule images list --include-legacy
```

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
devcapsule project run --docker-daemon host-socket
```

The recommendation alone must never mount the Docker socket.

Persistent authorization examples in the V1 design are:

```bash
devcapsule project config authorize docker-daemon host-socket
devcapsule project config authorize network host
devcapsule project config authorize development-sudo true
```

The first permits broad control of the host Docker daemon, the second relaxes
network isolation for this checkout, and the third permits the declared
development-sudo behavior. DevCapsule must validate each value, explain its
specific security effect, show the checkout file receiving the decision, and
respect more restrictive workstation policy. The exact released option and
value spelling remains subject to the D-0004 review.

### Select a different environment explicitly

Changing the IDE or toolchain is different from changing a preference. It
changes the realized development environment. The committed platform lock is
the project's supported default and must not be silently reinterpreted.

A future local-alternative experience may offer curated components that still
satisfy the declared capabilities. Such a choice must be developer-owned,
fully pinned, materialized under a distinct identity, and shown conspicuously
as a deviation from the committed default. The representation and support
contract for local alternatives remain an open V1 design question.

`devcapsule project [--path PATH] run-image IMAGE` remains the expert escape
hatch for an arbitrary local image. It does not claim to reproduce the
committed environment and does not read the project lock. When a declaration
is discoverable, it may use declared project defaults; otherwise the selected
path or current directory is used directly as the source directory.

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

- the `project [--path PATH]` subtree for `list`, `init`, named checkout
  registration, `config resolve`, `state adopt`, `lock`, `run`, and
  `run-image`, with no top-level compatibility aliases;
- XDG registry listing with `ready`, `missing`, and `uninitialized` status;
- clean-checkout creation of the default developer record during the first
  `project config resolve`;
- committed capability declaration and Linux platform lock;
- developer-owned checkout resolution and adopted persistent state;
- explicit Docker and development-sudo choices;
- foreground PyCharm lifecycle;
- generic Python runtime entrypoint foundation;
- tested base-image and checksum-verified local-materialization primitives;
- a formation-input platform lock for the current PyCharm dogfood checkout;
  and
- explicit `images build --type environment` with a canonical descriptor,
  strict metadata-verified reuse, concurrent artifact/cache protection, and
  optional local aliases.

Not yet available as the complete clean-clone experience:

- a published redistributable default base;
- the `config set`, `config bind`, and `config authorize` V1 command families;
- existing-host-directory binding through the new configuration surface;
- automatic materialization invoked by `devcapsule project run`;
- external delivery of the checkout-specific runtime plan at launch;
- the vendor-notice interaction; and
- a defined local-alternative environment workflow.

The browser-based configuration experience and `run`-owned interactive
resolution are V2 direction, not V1 implementation scope.

Until those items are implemented and validated, current executable commands
and workarounds remain documented in `devcapsule-src/README.md`.

The workstation-specific executable acceptance script was retired after the
product owner manually accepted sustained work from the configured second
checkout. Its portable intent is deferred to a later V1 multi-project E2E
orchestrator that creates exact-revision checkouts and isolated XDG roots under
a temporary directory, exercises `set`, `bind`, `authorize`, `resolve`, and
`run`, inspects the live containers, and cleans only test-owned resources. The
closure evidence and future task are maintained in
`../../implementation-notes/devcapsule/2026-08-03-next-functional-dogfood-stage-plan.md`.

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
7. What exact option and reset syntax completes the accepted `config set`,
   `config bind`, and `config authorize` families?
8. Which later secret providers support late retrieval, redaction, rotation,
   and noninteractive use after host-directory binding proves the model?

These questions are part of the product surface. They should be answered in
the user experience before their answers become accidental CLI behavior.
