# Work Order Draft: Redesign The `project config` And `project run` Experience

Drafted 2026-10-24 during the 0.3.0 candidate cycle, from a review of the
command surface with the product owner. Status: **draft, awaiting the
owner's decisions in Part 5**. Once decided, this draft supplies two later
work orders: a specification, then its implementation. Nothing here is implemented.

Evidence: the initial review used source `85779f6` on 2026-10-24. The
review partner repeated the checks against `ac6421f`; the CLI implementation
matches that source. No check launched a container. Commands below omit the
common `devcapsule project --path SCRATCH` prefix. Every launch probe used
`run --print-command` and stopped before materialization. Source references
are relative to `devcapsule-src/devcapsule/` at that revision.

The bootstrap case uses the manifest and lock committed on 2026-10-22 at
`ccozianu/ai-learning-bootstrap@ed6b87e`. Its Node requirement could have
been declared with the existing CLI. Other gaps concern application inputs
and personal recommendations. The review PR separates repeated commands,
source inspection, historical records, and untested runtime claims.

## Outcome

A developer who clones a project that carries DevCapsule reaches a running
capsule with one command, `devcapsule project run`, answering only what
nobody else can answer for them. A developer who changes a personal choice
changes it with one command and launches. Every question DevCapsule asks is
one the user is competent to answer, is asked once, has a flag, and is
answerable from the web console once a capsule runs.

## Part 1: The deficiencies

### Behavior defects, with command or source evidence

1. **The listing shows the grantable value as the default.** After selecting
   an IDE on a fresh checkout, `config list` shows `network | available | workstation
   default (unanswered) | host`, and likewise `development-sudo true`,
   `docker-daemon host-socket`, `host-x11 true`. The secure fallbacks are
   bridge networking, no Docker socket, no sudo and the contained desktop.
   Today an unanswered display choice can still use host X11 on older bases
   (`commands/project.py:1590–1605`, also reported by `config resolve`).
   The column is filled with
   the value one *could* authorize. The product's promise is that the user
   knows exactly what the capsule can touch; this listing says the opposite
   of the truth.
2. **A fresh clone cannot inspect its pending choices before choosing an IDE.**
   On ai-learning-bootstrap: `run --print-command` refuses, "Choose a local IDE";
   `init --creator https://github.com/ccozianu`
   refuses, "this project uses required/optional policy"; `config show`,
   `config list` and `project info` all refuse with the IDE message, so the
   user must decide before seeing what they decide about; then
   `capabilities --local`, `resolve`, `authorize base-image default`,
   `resolve` again, `run`. The project's own README names four
   commands including `run`, plus the permission commands printed by
   `resolve`. It does not enumerate those answers. The V1 design distinguishes
   onboarding an existing repository from consuming an initialized clone;
   it does not prescribe `init` for the latter.
3. **The IDE message is hardcoded and its remedy is destructive.** The
   source names `python-ide` for every project; ai-learning is a Node
   project. The five choices are not listed. `capabilities --local`
   replaces the whole personal list: following the message after having
   chosen Codex drops Codex silently.
4. **A retry reports new capabilities but keeps the old files.** Without
   a terminal, `init --creator URL --need python-ide` writes the manifest
   and lock, then fails on base consent. A retry with `--need frontend-ide
   --authorize base-image default` prints "Honored existing", echoes the new capabilities, and leaves the
   old ones in the manifest and the old IDE in the lock.
5. **`config authorize` prints base-image wording for every node.**
   Authorizing `network bridge` ends with "This authorization applies to
   the exact recorded image, by digest or by local image identity", and
   labels the node's own description "Recommendation" although nothing
   recommended it.
6. **`--all-recommended` announces grants it cannot make without a terminal.**
   `config authorize --all-recommended` prints "The following authorizations
   will be granted" to stdout, then refuses on stderr. Buffered output can
   display the refusal first. Nothing is granted. From the code:
   `commands/project.py:2113–2137` checks the terminal after printing the list.
7. **A memory limit is not the user's to set.** `config set` accepts only
   names the project declares in its manifest. On ai-learning `config set
   memory 6g` is refused after selecting an IDE: "Configuration node
   'memory' is not declared". The implemented memory value requires project
   metadata, such as `runtime.memory-limit`; its accepted size spelling is
   `6GiB`. `config show` reports the workstation configuration layer as absent
   (`commands/project.py:636`).
8. **A change needs a second command.** After `config set`, `authorize`,
   `bind` or `unset`, `run` refuses with "resolution is stale" until
   `config resolve` is run. `init --need`, `config need` and a complete
   `config approve` resolve for the user; `init --required` does not (item 22).
   Saved Docker arguments need no resolution. The rule is a memory test.
9. **`--local` means two things and the same name is shared or personal
   depending on the manifest form.** The matrix defines eight personal
   names, the five IDEs and the three agents. `init --required python-ide`
   refuses, "belongs in --local"; `init --need python-ide` accepts the same
   name into the shared manifest. `init --local` seeds the owner's own
   checkout; `capabilities --local` replaces a collaborator's selection.
   `config need` works only on the `need` form and refuses on the
   required/optional form. However, `config capabilities --required node
   --preview` accepts a legacy `need` manifest and previews its conversion.
   The editing paths are asymmetric, not mutually exclusive.
10. **`versions show` prints a Python dict** for the base line.
11. **Nothing stops, lists or reconnects a session.** The default
    container name is `pycharm-isolated-<user>-<timestamp>` for every IDE;
    the launcher derives it from a timestamp rather than a checkout session
    identity (`launch/pycharm/_launcher.py:1021`). This does not provide
    reconnect semantics. Concurrent-launch behavior was not reproduced;
    PyCharm also has a configuration-directory lock check at line 844.
    The README's handoff excerpt quotes `devcapsule stop` and `devcapsule start`, the
    root status file names `workflow list`; neither exists. The command
    reference page and the several-projects page say "Coming soon".
12. **Exit codes do not separate usage from state.** A typo, a missing
    project and a pending decision all exit 2; a declined approval exits 1.
    An agent cannot distinguish those failures by status alone. The review
    reproduced the exit-2 cases. The decline path is source evidence from
    `commands/_software_approvals.py:148–162` and
    `commands/project.py:1552–1554`, not an interactive launch test.
13. **Launcher errors can reach the user as tracebacks** (from the code). The
    launcher's error class has 51 raise sites, is not a `CliError`, and the
    entry point catches `SystemExit` and `CliError`. The class is
    `PycharmRunError` (`launch/pycharm/_launcher.py:88`);
    `cli.py:26–38` does not catch it. This establishes a possible uncaught
    error path, not a reproduced failed capsule launch.

### Design tensions

14. **Launch is a chain of gates** (from the code). `run` can ask the
    approvals key, then an upgrade menu with up to four options and nested
    confirmations (`commands/project.py:1552–1579`;
    `commands/_upgrade_prompt.py:57–100`). An unanswered display choice
    also produces a host-X11 notice after base validation
    (`commands/project.py:1590–1605`). The actual fallback depends on the
    base's display support; this review did not exercise a launch.
15. **Three meanings of "force" are planned in the same release cycle.** `run --force`
    accepts a stale resolution once; the planned `run --force-config` skips
    configuration errors; the planned `resolve --force` previews and writes
    nothing. These are plans in maintenance's status at lines 1064–1072,
    not three implemented options; the changelog says later candidates.
16. **Audiences mix in one listing.** The legacy `pycharm` command, the
    container-internal `runtime` command, `project recursive-e2e` and
    `run --no-recursive-e2e` sit beside adopter commands. `images build
    --type`, `run --name`, `state adopt --from` and the `authorize`
    positionals have no help text; the help for `run` is a paragraph that
    breaks the group's table. `project --path` here, `--project` on
    `bootstrap`, `images` and `workflow` subcommands. `--unverified` on `init`,
    `--unvalidated` on `versions select`. `--less-pedantic` names a mood.
17. **D-0004 remains proposed; later records partly revise its split.**
    D-0004 is `status: proposed`, with no decision date. The V1 design also
    records the explicit resolution checkpoint; the proposal's status alone
    does not invalidate that later design. D-0010's 2026-09-21 launch
    refinement and the 2026-10-22 software-approval direction put specific
    decisions inside `run`. D-0010's 2026-10-01 refinement makes upgrades
    scheduling choices, with vendor trust handled separately;
    D-0011 accepts workstation trust in a verified channel, including
    DevCapsule's base channel; D-0012 limits host questions and preserves
    existing answers. Neither record removes validation or all consent.
    Item 2 is evidence for reconsidering D-0004's explicit checkpoint; it
    does not itself decide the proposal or replace its review boundary.

### The manifest, on the ai-learning-bootstrap case

The project is a TypeScript frontend and backend, Fastify with REST and
GraphQL, Prisma over a PostgreSQL the owner supplies. A developer working on the full application needs, among other things, an IDE for TypeScript with Node and npm to
build and run, the PostgreSQL credentials, and a handful of application
secrets. UI preview and build/test tasks need fewer inputs, as its README
explains. This is the manifest the agent produced, as committed:

```toml
"devcapsule-schema-version" = 1

["capabilities"]
"optional" = []
"required" = ["postgresql-client"]

["capabilities"."sdk-major"]

["project"]
"creator" = "https://github.com/ccozianu"
"mount" = "/workspace/ai-learning"
"name" = "AI Learning"
"slug" = "ai-learning"

[workflow]
definition = "devcapsule"
version = "0.3.0"
mode = "single-stream"
```

18. **The manifest omits an expressible Node need and cannot declare the
    application's secret-input contract.** `postgresql-client` supplies
    `psql`, not a database connection or credentials. The application's
    `scripts/db-apply.ts:1–20` uses Node's `pg` client for its manual migration.
    The manifest alone does not establish why its author selected `psql`.

    The README relies on Node 22 in the pinned base. That pin fixes the
    current base bytes, but the manifest does not require Node when the
    owner selects a future base. The CLI already knows `node`:
    `config capabilities --required node postgresql-client --preview`
    succeeds. Applying it and running `config check` also succeeds.
    `--sdk-major node=22` is refused: the selected lock provides an unknown
    major. Node presence is expressible; the application's `>=22.12 <23`
    range is not expressible through that SDK-major option.

    New IDE requirements are deliberately refused by the required/optional
    writer: `config capabilities --required frontend-ide --preview` prints
    "IDE/agent choices are local; use --local for frontend-ide."
    Legacy `need` manifests can contain IDEs; existing shared IDE selections
    are preserved on unrelated edits (`configuration/capability_commands.py:196–204`).
    Thus the schema can carry an IDE, but the supported new-policy authoring
    path leaves it personal under R-CONFIG-001's 2026-10-06 refinement.
    An optional project IDE recommendation remains a separate decision.

    `[configuration.values]` already declares required ordinary values,
    descriptions and recommendations (`configuration/values.py:38–98`).
    A required `db.host` string is listed as missing until
    `config set db.host db.example.invalid` supplies it. Ordinary values
    are inspectable inside the capsule through the read-only checkout mount
    (`runtime_configuration.py:131–164`). The `config --help` tree has no
    general declaration-writing command; `set` answers existing metadata.
    These values are not automatically exported
    as application environment variables. Only memory and the shipped command
    name have curated runtime effects (`configuration/values.py:22,235–241`).
    Ordinary values must not be used for application passwords.

    Secret-input declarations come from component code selected by the lock,
    not arbitrary secret tables in the lock or manifest
    (`configuration/bindings.py:90–110`). `set-env` supplies private values
    per checkout, but cannot declare which application inputs a project needs.
    The gap is project-declared environment delivery and secret requirements,
    not a total absence of required-value or Node vocabulary.
19. **Two manifest writers produce different presentations.** The
    required/optional writer serializes keys and table names with JSON
    quoting (`configuration/capability_commands.py:74–87` and
    `configuration/file_formats.py:122–160`). It emits the empty
    `sdk-major` table and `optional = []` in this example, and drops comments
    when it rewrites a document. Legacy `init --need` uses bare keys and
    preserves existing authored text (`configuration/operations.py:1411–1455`).
    The bootstrap writer appends the bare `[workflow]` table
    (`workflow_bootstrap.py:312–327`). The example therefore does not quote
    every key, and the quoting is not inherent in TOML.

    `mount` is an in-container path; `creator` and `slug` form project
    identity. `[workflow]` selects the project's workflow definition,
    version and mode (WORKFLOW.md topic 4.1). It is not base-build provenance.
    Its `version = "0.3.0"` need not match the lock's
    `build-mnemonic = "v0.2.12-rc5"`; those fields version different things.
    Removing or relocating that declaration needs an explicit decision.
20. **Two capability forms and two workflow-mode spellings coexist under
    schema version 1.** `need` and `required`/`optional` describe capabilities.
    `workflow-type` and `[workflow].mode` describe workflow selection.
    These are two independent migrations, not three capability vocabularies.
    Legacy `init --need` still writes the legacy form; the policy command can
    convert it (item 9). The bootstrap lock has no `[workflow]` table.
    Its `capabilities-digest` and `resolution-matrix-version` describe lock
    generation. The lock pins reviewed versions so collaborators do not
    regenerate them from different launcher catalogs (D-0001 section 6).
    Being generated does not make the lock redundant.
21. **Application setup remains in prose.** The README names three setup
    commands before `run`, then asks developers to answer the decisions
    printed by `resolve`. It also says "Do not launch a Docker PostgreSQL
    instance for this project". Node could have been declared, as item 18
    shows. The configuration surface cannot express that application-specific
    prohibition. Denying the Docker socket is narrower: it denies access to
    the host daemon, not every way to run PostgreSQL. Whether the launcher
    should enforce such a rule is an owner decision, not an established
    deficiency in enforcement. The evidence does not establish the earlier
    author's motive or what every adopter will do.

### Additional first-day gaps, reproduced during review

22. **A successful policy `init` does not leave the owner ready to run.**
    In an empty Git checkout, `init --creator https://github.com/ccozianu
    --required node --local frontend-ide` exits 0 and tells the user to resolve.
    The next `run --print-command` exits 2: "Local resolution is missing".
    This differs from successful legacy `init --need` and the postcondition
    in the V1 design's *Initializing A New Project* section.
23. **Inspection writes a generated file.** After selecting a local IDE on
    the bootstrap fixture, `config list` prints "Initialized resolution
    placeholder" and creates `devcapsule.resolved.toml`. It has not resolved
    the missing base consent. From the code, the same loader can create a
    checkout record too (`commands/project.py:646–675`). A user inspecting
    an unfamiliar project cannot assume that this command is read-only.

## Part 2: Principles, as ruled by the owner on 2026-10-24

1. **Consent is the only justification for a question.** The user must
   positively approve everything that will run on their system and every
   privilege it gets. Nothing else is a question. R-PRODUCT-002, D-0001,
   D-0011, D-0012.
2. **Derive, report, ask.** What follows from the project and the
   workstation is derived and shown. What encodes the user's intent is
   asked, once, in the settled order: command line, earlier answer,
   existing record, derivable default, and only then a prompt. Every
   question has a flag.
3. **One command.** `project run` is the first-contact command and the
   return-to-work command. A change to a personal choice is one command
   and then `run`; no derived file is the user's to refresh.
4. **Nearly everything is personal.** Required capabilities and the SDK
   major are the project's; a local choice cannot waive them
   (R-CONFIG-001). Everything else, the IDE, agents, optional tools, exact
   versions, memory and other container resources, host access, bindings
   and Docker arguments, is the checkout's, with a workstation default and
   a project recommendation where the project has one. Divergence from the
   recommendation is disclosed, never hidden (D-0010).
5. **The web console is where a running capsule's user reviews and
   decides.** The same review the terminal prints is a page; an answer
   given there is recorded for the next launch. The terminal remains for
   first contact and for scripts.
6. **Truthful listings.** Every row shows the effective value, its source,
   and whether a decision is pending. A missing answer is a row, not a
   refusal.
7. **Proposed, from the bootstrap case, not yet ruled:** the manifest
   states everything a developer must have to work on the project, in
   the project's words, and reads as a document. Toolchains the code
   needs, the IDE the project recommends, the environment the developer
   must supply, the host access the project asks for and why. What the
   project declares, the launcher lists and asks; what the project cannot
   declare ends up in a README, which is item 21.

## Part 3: The new experience, for the user

This is the proposed experience, conditional on the decisions in Part 5.

### 3.1 A project that already has DevCapsule

You cloned a repository that carries `.devcapsule/`. From its folder:

```bash
devcapsule project run
```

DevCapsule reads the project's manifest and lock, your workstation's
defaults, and anything you answered before for this checkout. It prints what
it derived, then asks only what it cannot derive, and launches.

For `ccozianu/ai-learning-bootstrap` as committed today, this is what you
**must** specify, and what you **can**:

| You must specify | Why | How |
|---|---|---|
| Which IDE | The project left it to each developer, and no secure default exists for an IDE | the prompt, or `--ide frontend-ide` |

After you accept DevCapsule's channel on this workstation, its pinned base
asks nothing further. A local image or a different channel still asks.
Host access asks nothing: the project recommends none,
so the capsule gets bridge networking, no Docker socket, no sudo, the
contained desktop (D-0012). If the project later recommends an IDE, this
list is empty.

With the manifest in section 3.6, the list changes:

| You must specify | Why | How |
|---|---|---|
| `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | the project declares them required; the owner supplies the database | the hidden prompt, or `--env NAME` to read your shell's value |
| `AUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | declared required, with the project's one-line reason for each | same |

The IDE is gone from the must-list because the project recommends
`frontend-ide`; Node is gone from the README because the project requires
it and DevCapsule guarantees its presence. Each value is recorded once per checkout
in the private store outside Git, as `set-env` records it today, and masked
in DevCapsule reports. Today Docker still receives the actual value; processes
that can inspect Docker can see it. `config show` lists each as a row, bound or pending.

| You can specify | Default if you do not | How, persistent | How, this run only |
|---|---|---|---|
| Coding agents | none | `config agent add codex` | `--agent codex` |
| Optional project tools to leave out | all the project offers | `config tool omit browser-automation` | |
| Container memory, CPUs, shared memory | workstation defaults; the project may recommend | `config set memory 6G` | `--memory 6G` |
| Host network, Docker socket, sudo, host browser, host X11 | the secure fallback of each | `config authorize network host` | `--authorize network host` |
| Where your capsule home and IDE state live | managed directories under your XDG data home | `config bind home host-directory:PATH` | |
| Component secrets, such as `codex/openai-api-key` | unbound; the tool asks you to sign in | `config bind codex/openai-api-key host-environment:OPENAI_API_KEY` | |
| Environment variables and extra `docker run` options | none | `config env NAME`, `config docker-args -- ...` | `run -- ...` |
| Exact component versions | the project's lock | `versions select` | |
| The container name | derived from project and checkout | `config set container-name NAME` | `--name NAME` |

Adding Codex asks one more question the first time on this workstation:
accepting the vendor terms and verified channel. D-0011 records that
acceptance per vendor product per user on the workstation. A changed terms
URL or departure from the channel asks again; a version change alone does
not. Vendor sign-in happens inside the capsule, with the vendor.

Your first `run` for the committed manifest, after workstation channel
acceptance:

```text
Project: AI Learning (creator https://github.com/ccozianu; slug ai-learning)
Requires: postgresql-client 16, supplied by the base ubuntu-24.04@9.
Base: docker.io/mycodespaceai/devcapsule-base@sha256:8837edd…, published by DevCapsule, trusted on this workstation.
Host access: none recommended; the capsule gets bridge networking, no Docker socket, no sudo, the contained desktop.
Memory: 4G (workstation default). Change: devcapsule project config set memory SIZE

The project leaves the IDE to you. Choose one:
  1. frontend-ide   VSCodium 1.126.04524
  2. python-ide     PyCharm 2026.2.0.1
  3. java-ide       IntelliJ IDEA 2026.2.3
  4. eclipse-ide    Eclipse 2026-09-R
  5. dotnet-ide     Rider 2026.2.3.1, with the .NET SDK
IDE [1-5]: 1
Recorded for this checkout. Change: devcapsule project config ide NAME

Materializing frontend-ide on ubuntu-24.04@9 …
Desktop: http://127.0.0.1:…/vnc.html?…
```

The bootstrap repository is `https://github.com/ccozianu/ai-learning-bootstrap`;
the manifest's creator and slug are an identity, not that repository URL.
Its pinned base `ubuntu-24.04@9` has no web console. To use the console,
you need a console-capable base.

Later launches print the first block in one line each and no question,
provided the inputs and required answers have not changed.

### 3.2 Changing something later

Every change is one command that validates the value, records it, and
derives the plan. There is no resolve step. The next `run` uses it:

```bash
devcapsule project config set memory 6G
devcapsule project run
```

Each command says what it recorded, where, and what it changes at the next
launch. `config show` prints the whole picture at any time, including while
a capsule runs:

```text
KIND      NAME            EFFECTIVE   SOURCE                   PENDING
ide       frontend-ide    codium      checkout
agent     codex           0.163.0     checkout (project lock)
memory    6G              6G          checkout
network   bridge          bridge      secure default           (project recommends nothing)
env       POSTGRES_HOST   set         checkout (private store)
env       SMTP_PASSWORD   unset       —                        optional: project says "no email in development"
secret    codex/openai-api-key  unbound  —                     optional: bind or sign in
```

The effective column is always the value the next launch uses. A value
that is the secure default says so; a value the project recommends and you
have not answered is a pending row with the project's justification beside
it, and `run` asks it.

### 3.3 When the project changes

You pull, and the manifest or lock moved. The next `run` reports the
difference and asks only for what is new:

- a new required tool or a new base: shown; no question, because both are
  DevCapsule-validated and published through the trusted channel;
- a new version of vendor software you approved before: the one-line list
  and one `y`;
- a new or changed host-access recommendation: the question, with the
  project's justification, offering this run, this checkout, or deny;
- an optional tool your launcher does not know: a warning naming it, and
  the launch continues (R-CONFIG-001);
- a required tool your launcher does not know: the launch stops and says
  which launcher version knows it.

Your own answers survive: a recorded `network host` stays until you change
it, a recorded `network bridge` stays even if the project now recommends
`host`, and the listing shows both.

### 3.4 Scripts and agents

Without a terminal, `run` asks nothing. Recorded answers and flags are the
only input. When something is missing, it fails once, listing every missing
answer with its flag, and exits with a code that means "a decision is
needed":

```text
devcapsule: the first launch of this checkout needs answers:
  IDE:   --ide frontend-ide | python-ide | java-ide | eclipse-ide | dotnet-ide
Nothing was written. Answer on the command line or in a terminal.
```

| Exit code | Meaning |
|---|---|
| 0 | the session ended normally |
| 1 | the launch or session failed; the log paths are printed |
| 2 | usage: the command was wrong |
| 3 | a decision is pending; the message names each with its flag |
| 130 | interrupted from the terminal |

Flags that answer a pending question are recorded, exactly as the prompt
would record them. Flags that override an answer already recorded apply to
this run only and say so on stderr. `--print-command` prints the plan and
writes nothing.

### 3.5 The web console

Once a capsule runs, its console has a configuration page showing the same
listing as `config show`, with the same pending rows. A decision answered
on that page is recorded for the next launch, with the same validation, and
the page says so. A host-access grant on the page shows DevCapsule's own
description of the exposure beside the project's justification, as the
terminal does. The page never changes the running capsule; it changes the
next launch, and says so.

### 3.6 For project owners

Owners declare the shared contract with commands that name what they do,
and the manifest the commands write is one an owner could have written by
hand. For ai-learning-bootstrap:

```bash
devcapsule project init --creator https://github.com/ccozianu --require node
devcapsule project config require tool postgresql-client --because "inspect the owner's database with psql"
devcapsule project config recommend ide frontend-ide
devcapsule project config require env POSTGRES_HOST POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD \
    --because "the owner supplies the database; do not start one in the capsule"
devcapsule project config require env AUTH_SECRET GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET --because "sign-in"
devcapsule project config offer env SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASSWORD SMTP_FROM --because "no email is sent in development"
devcapsule project config recommend memory 6G --because "the test suite builds a 4 GB index"
```

which writes, in shape:

```toml
devcapsule-schema-version = 2

[project]
name = "AI Learning"
creator = "https://github.com/ccozianu"

[requires]
tools = ["node", "postgresql-client"]
# inspect the owner's database with psql

[requires.environment]
POSTGRES_HOST = "the owner supplies the database; do not start one in the capsule"
POSTGRES_DB = "..."
AUTH_SECRET = "sign-in"

[offers.environment]
SMTP_HOST = "no email is sent in development"

[recommends]
ide = "frontend-ide"
memory = "6G"            # the test suite builds a 4 GB index
```

Keys are bare where TOML allows it. Every requirement and recommendation
carries the owner's reason, and that reason is what the developer reads when
asked. Nothing derived is in the file: no digest, no matrix version, no mount path, no
`[workflow]` table; what the launcher derives goes to the lock, and the
lock is generated by the launcher and committed with the project. `init`
creates the manifest and lock and the owner's own checkout, and ends with
the owner's own first `run` ready. A recommendation never grants anything;
it names the value the next collaborator is asked about, with the reason
they will read. One
manifest form remains; `need` and `required`/`optional` are read and
rewritten on the owner's next edit.

An owner who asks for host access supplies a justification, as today
through `init --authorize NODE VALUE JUSTIFICATION`. The proposed spelling is:

```bash
devcapsule project config recommend network host --because "..."
```

and an owner who wants the opposite enforced can say so: `config forbid
docker-daemon --because "the owner supplies the database"` makes the
`docker-daemon` row read `forbidden by the project` instead of a question.
That controls host-daemon access; it does not by itself enforce "no PostgreSQL
server".

### 3.7 The command tree, config and run only

```text
devcapsule project run [--ide NAME] [--agent NAME]... [--memory SIZE] [--authorize NODE VALUE]...
                       [--name NAME] [--print-command] [--no-update-check] [-- DOCKER-RUN-OPTIONS]
devcapsule project config show [--json]
devcapsule project config ide NAME
devcapsule project config agent add|remove NAME
devcapsule project config tool omit|restore NAME
devcapsule project config set NAME VALUE|default
devcapsule project config authorize NODE VALUE [JUSTIFICATION] | deny NODE | forget NODE
devcapsule project config bind RESOURCE PROVIDER:VALUE | unbind RESOURCE
devcapsule project config env NAME [VALUE] | env unset NAME | env list
devcapsule project config docker-args [-- OPTIONS...] | docker-args clear
devcapsule project config approve [NAME...|--all]
devcapsule project config check [--json]
devcapsule project config require tool|env NAME... [--because TEXT]      (owners)
devcapsule project config offer tool|env NAME... [--because TEXT]        (owners)
devcapsule project config recommend ide|memory|NODE VALUE [--because TEXT] (owners)
devcapsule project config forbid NODE [--because TEXT]                   (owners, if decided)
```

`config check` is the explicit preflight for automation: it validates
everything `run` would, writes nothing, and exits 3 with the same list when
a decision is pending. `config list` becomes `config show`; `resolve` is
gone, with a one-release alias that says so.

### 3.8 Cases the specification must complete after the owner decides

- **Two checkouts on one workstation.** Today a second path with the same
  creator and slug refuses `config capabilities --local frontend-ide` and
  names `checkout register NAME`. Part 5 item 14 asks how `run` handles that
  without inheriting another checkout's permissions.
- **No `.devcapsule/` directory.** Today `run --print-command` refuses with
  "No .devcapsule/devcapsule.toml found" and names `project init`.
  Part 5 item 15 asks whether the one-command promise includes this case.
- **An agent inside a running capsule.** D-0010's runtime refinement keeps
  host configuration read-only and distinguishes running from next-launch
  software. Part 5 item 16 asks what `config show` can report when current
  host inputs cannot be observed from inside the capsule.
- **An owner changes a mandatory need.** Part 3.3 does not cover a saved
  local version set that lacks a new required tool or SDK major. D-0010
  preserves local selection; R-CONFIG-001 forbids waiving mandatory needs.
  Part 5 item 17 asks how the developer chooses a compliant replacement.

## Part 4: What goes away

- `project config resolve`, `capabilities --local`, `capabilities
  --required/--optional/--sdk-major`, `config need`, `init --need`,
  `init --required/--optional/--local`, `--less-pedantic`.
- The separate `set-env`/`unset-env`/`list-env` and
  `set-extra-docker-args`/`list-extra-docker-args`/`remove-extra-docker-args`
  spellings, folded into `env` and `docker-args`.
- The host-x11 paragraph at every launch; the contained desktop is the
  secure default like the other fallbacks, and `host-x11` is answered like
  any other node.
- The per-checkout base-image and vendor-download authorizations, replaced
  by the workstation trust record of D-0011 for accepted channels. Departures still ask;
  their authorization scope must remain explicit.
- The quoted-key manifest writer, the empty `[capabilities.sdk-major]`
  table, and, subject to Part 5 item 18, the `[workflow]` table in the
  manifest. The bootstrap lock has no copy to remove.
  The manifest is written in the form an owner would write by hand; what
  the launcher derives goes to the lock only.
- `run --force` and `run --force-config`: when inputs changed and no
  decision is pending, `run` derives and continues; when a decision is
  pending, it asks; a launcher that does not know an optional tool warns
  and continues. There is nothing left to force.

## Part 5: Decisions required from the owner

These questions leave the owner's Part 2 rulings intact. Where a proposal
conflicts with a ruling or an accepted record, the question identifies it.

1. **How should the new flow replace D-0004's proposed V1/V2 split?**
   Adopt a revised D-0004 with terminal-first `run` and a read-only preflight,
   or record a replacement decision that leaves D-0004 as historical proposal?
   D-0004 is `proposed`, with no decision date. Its section 6 proposes a
   graphical flow and preserves review before execution; it does not already
   approve this terminal-first design.
2. **May a project recommend an IDE?** Permit an overridable recommendation,
   or keep IDE selection entirely personal with no project recommendation?
   R-CONFIG-001's 2026-10-06 refinement makes the selection personal. It does
   not expressly settle an optional recommendation. Item 18 demonstrates a
   refusal of a new shared requirement, not a prohibition in every legacy form.
3. **Must the new CLI release include D-0011 and D-0012?** Require both
   implementations before shipping, or stage the CLI with today's consent
   questions explicitly retained? Including D-0011 removes routine per-version
   approvals within an accepted channel. Part 3.3 proposes today's per-version
   one-`y` behavior; it cannot also remain the ordinary rule under D-0011.
   Changed terms and channel departures still ask. D-0012 preserves recorded checkout answers and limits new host
   questions; neither record currently names a release.
4. **Should unanswered host X11 silently use the contained desktop?** Keep
   D-0012's existing explicit-choice behavior, including today's notice, or
   remove the notice while still requiring explicit consent to host X11?
   Neither alternative makes host X11 a project-granted permission.
5. **Which command naming scheme should the specification use?** Adopt the
   proposed `ide`, `agent add|remove`, `tool omit|restore` and
   `require|offer|recommend` families, or retain a unified capability command
   with explicit project and checkout scopes? The tree omits SDK-major
   authoring. The chosen scheme must place it and use one identifier for each
   tool. Today the capability is `codex-agent`; `codex` is its component ID.
   Part 3 mixes them and leaves the consumer's `[JUSTIFICATION]` unsettled. The IDE versions in section 3.1 are the pins
   in `resolution_matrix.py:707–768`.
6. **Which resource values should the launcher own without project declarations?**
   Limit the initial set to memory, CPUs, shared memory and container name,
   or include other named values? State the additional names if selected.
   The specification must show how to edit their workstation defaults as
   well as checkout overrides; Part 3 currently shows only checkout editing.
   Section 3.6's 6G recommendation and index-size reason are illustrative,
   not established bootstrap requirements.
7. **Which host process should accept the console's configuration changes?**
   Use the attached launcher as proposed, or a separate launcher-side service?
   D-0010's runtime refinement permits read-only introspection today.
   Principle 5 requires console decisions; the missing decision concerns their
   host-side writer. Either option must validate next-launch changes and
   preserve the user's host-access decisions. First-launch console setup remains outside this work order.
   The console experience needs a console-capable base. The 0.3.0 changelog's
   candidate-1 correction confirms that recipe 9 has no console.
8. **Which release should carry the implementation?** Name a release after
   0.3.0 now, or leave it unassigned until the specification is accepted?
9. **Should projects declare application environment requirements?** Adopt
   proposed principle 7's required and optional environment inputs with reasons,
   or keep environment provisioning personal and outside the manifest?
   Ordinary required values already exist; automatic environment delivery and
   project secret declarations are the extension. A later specification must
   distinguish launching a workspace from running every application feature.
   The bootstrap can preview its UI without credentials, while password
   sign-in needs SMTP. Its README says only that installation, tests and
   schema generation send no email. Whether SMTP is optional for the intended
   development experience needs an owner answer. The seven-variable example
   is not a complete application contract. The `psql` use in section 3.6 is
   illustrative, not an established bootstrap requirement. Schema sequencing
   is a separate question in item 19.
10. **May a project forbid a personal host-access choice?** Allow an explicit
    project prohibition on a curated node, or retain principle 4's rule that
    host access remains personal? Denying `docker-daemon` does not enforce
    "never run a PostgreSQL server". This question concerns host access only;
    broader application-process enforcement needs a separately scoped proposal.
11. **Should generated manifests use the proposed human-readable presentation?**
    Require bare keys where valid and preserved descriptions and reasons, or
    retain the current serializer and improve explanatory listings instead?
    This is a writer-presentation choice. It does not decide schema migration
    or relocation of the workflow declaration. The lock remains generated by
    the launcher and reviewed with the project.
12. **What lifetime should a `run` flag have?** Keep every override run-once,
    with an explicit save mechanism, or persist answers to pending questions
    while treating overrides of recorded answers as run-once? Part 3.4 proposes
    the latter. It gives the same flag two effects based on hidden state.
    This conflicts with one meaning per flag and departs from D-0001 section 1
    and the V1 design's run-once carriers.
13. **What should resetting an ordinary value mean?** Follow the current
    project recommendation and workstation fallback dynamically, or copy the
    current effective default into the checkout as a fixed answer? The tree
    has `set NAME default` but no ordinary-value reset. Today `set NAME default`
    copies the recommendation; `config unset NAME` removes the answer.
    Host denial and forgetting an authorization must remain distinct actions.
14. **How should `run` register a second checkout of the same project?** Derive
    a distinct checkout name from its path, or ask for a name with a matching
    flag? Today a second path requires `checkout register NAME`. D-0004's
    checkout model and the V1 design require separate records and permissions.
    Neither option may silently inherit another checkout's authorization.
15. **What should `run` do when no manifest exists?** Guide explicit project
    initialization, or refuse with the exact owner-side initialization command?
    Today it refuses and names `project init`. Define whether the one-command
    promise applies only to repositories that already carry DevCapsule.
    Successful legacy `init --need` leaves the owner ready to run today;
    policy `init --required` does not (Part 1 item 22).
16. **How should in-capsule inspection report facts it cannot observe on the host?**
    Show recorded next-launch inputs with an explicit unknown or stale state,
    or obtain a fresh assessment through the launcher? Today runtime inspection
    reports recorded inputs, not the host-computed rows
    (`runtime_configuration.py:138–164`). Running software and next-launch
    selection must remain distinguishable under D-0010.
17. **How should a new mandatory project need affect an incompatible local version set?**
    Refuse with commands to select a compliant set, or guide that selection
    within `run` before launch? R-CONFIG-001 forbids silently waiving the need;
    D-0010 keeps a local selection until the developer explicitly changes it.
    Neither permits quietly replacing a saved selection on `git pull`.
18. **Where should the workflow declaration live?** Keep `[workflow]` in the
    manifest, or define a separate authored declaration and a coordinated
    migration? Its mode is a project choice, not a fact derivable from the
    runtime lock. WORKFLOW.md topic 4.1 currently requires the manifest table.
    Sections 3.6 and 4 cannot remove it without settling its replacement
    and readers.
19. **When should the new manifest vocabulary receive its schema version?**
    Extend the planned 0.3.0 schema-2 change before it ships, or assign this
    later redesign a later version? The changelog schedules schema 2 for the
    required/optional vocabulary, while this work order excludes 0.3.0.
    A writer must not silently rewrite every older representation on an
    unrelated edit. Section 3.6 proposes rewriting on the owner's next edit;
    that is not a settled writer rule. R-CONFIG-001 requires compatible output
    and preservation of unrelated and unknown optional declarations. Existing schema-1 readers
    reject schema 2 (`configuration/file_formats.py:60–74`).
20. **Does `--env NAME` save a value or bind a source?** Read and privately save
    the shell's current value, or record the variable name and retrieve its
    current value on each launch? Part 3.1 implies the former. Today's secret
    `bind ... host-environment:NAME` means the latter. The specification must
    state missing-source behavior and reflect the chosen spelling in the tree.
    Section 3.1 uses `--env NAME`, but section 3.7 omits it.
21. **Where should the first DevCapsule channel acceptance occur?** Offer it
    during launcher setup, or at the first launch that needs the channel?
    D-0011 requires an explicit workstation trust record and names the trusted
    origin and integrity method. Installation alone does not establish that
    the record exists. Part 3.1 assumes that acceptance has already occurred.
    D-0011 offers that trust once; a local image or a different channel
    still asks.
22. **Should configuration inspection have any write side effects?** Make
    `config show` and `config check` strictly read-only even before registration,
    or allow disclosed creation of local records? Item 23 reproduces today's
    placeholder write. Part 3.7 already proposes a write-free `check`.
23. **When a host recommendation changes, should a recorded answer be asked again?**
    Keep the answer and disclose the changed recommendation, or ask again while
    preserving the secure choice until answered? Part 3.3 says both "asks" and
    "stays until you change it". D-0012 exempts existing records from prompts
    caused by client upgrades, but names changed recommendations as a trigger.
24. **Which ordinary recommendations require an answer?** Derive their values
    and disclose the source, or ask the developer to accept each one before
    launch? Part 3.2 makes every unanswered recommendation pending, while
    principle 1 limits questions to consent. Item 2 separately asks about IDE
    recommendations. This question concerns ordinary values such as memory.

## Out of scope here, catalogued above for the next pass

Items 10 to 13 and 16: session lifecycle commands, exit-code mapping,
launcher error handling, the top-level listing and help texts, the
`images`, `bootstrap` and `workflow` trees. They are deficiencies of the
same surface and belong to the next pass, after the `config` and `run`
design above is decided. The provisional exit-code table in section 3.4 is
retained for that pass; this review does not settle it.
