# Work Order Draft: Redesign The `project config` And `project run` Experience

Drafted 2026-10-24 during the 0.3.0 candidate cycle, from a review of the
command surface with the product owner. Status: **draft, awaiting the
owner's decisions in the last section**. Once decided, this document is the
input to two work orders: this one, the specification, and a second one,
the implementation of that specification. Nothing here is implemented.

Evidence: every deficiency below was reproduced on 2026-10-24 against the
source checkout at `85779f6` on `release-0.3.0`, on a scratch project and on
the manifest and lock of `ccozianu/ai-learning-bootstrap`, without launching
a container, except where a line says "from the code". The manifest of
`ai-learning-bootstrap` is itself evidence: it was written on 2026-10-22 by
a capable agent working inside this repository, with the whole of DevCapsule
in front of it, and it still says almost nothing of what that project needs.
Part 1 ends with that case; an adopter with none of that context has less
chance than the agent had.

## Outcome

A developer who clones a project that carries DevCapsule reaches a running
capsule with one command, `devcapsule project run`, answering only what
nobody else can answer for them. A developer who changes a personal choice
changes it with one command and launches. Every question DevCapsule asks is
one the user is competent to answer, is asked once, has a flag, and is
answerable from the web console once a capsule runs.

## Part 1: The deficiencies

### Behavior defects, reproduced

1. **The listing shows the grantable value as the default.** On a fresh
   checkout `project config list` shows `network | available | workstation
   default (unanswered) | host`, and likewise `development-sudo true`,
   `docker-daemon host-socket`, `host-x11 true`. The effective defaults are
   bridge, none, false and the contained desktop. The column is filled with
   the value one *could* authorize. The product's promise is that the user
   knows exactly what the capsule can touch; this listing says the opposite
   of the truth.
2. **A fresh clone of a shared project is refused six times.** On
   ai-learning-bootstrap: `run` refuses, "choose a local IDE";
   `init`, which the documentation prescribes for an existing repository,
   refuses, "this project uses required/optional policy"; `config show`,
   `config list` and `project info` all refuse with the IDE message, so the
   user must decide before seeing what they decide about; then
   `capabilities --local`, `resolve`, `authorize base-image default`,
   `resolve` again, `run`. The project's own README prescribes four
   commands and still misses the base consent.
3. **The IDE message is hardcoded and its remedy is destructive.** The
   source names `python-ide` for every project; ai-learning is a Node
   project. The five choices are not listed. `capabilities --local`
   replaces the whole personal list: following the message after having
   chosen Codex drops Codex silently.
4. **A failed `init` leaves project files, and a retry keeps them
   silently.** Without a terminal, `init` writes the manifest and lock and
   then fails on the base consent. A retry with a different `--need`
   prints "Honored existing", echoes the new capabilities, and leaves the
   old ones in the manifest and the old IDE in the lock.
5. **`config authorize` prints base-image wording for every node.**
   Authorizing `network bridge` ends with "This authorization applies to
   the exact recorded image, by digest or by local image identity", and
   labels the node's own description "Recommendation" although nothing
   recommended it.
6. **`--all-recommended` without a terminal refuses, then announces
   grants.** The refusal line comes first, then "The following
   authorizations will be granted". Nothing is granted.
7. **A memory limit is not the user's to set.** `config set` accepts only
   names the project declares in its manifest. On ai-learning `config set
   memory 6g` is refused. Only two manifests in this tree declare a memory
   value. There is no launcher-owned value at all; the workstation layer
   D-0001 names is "absent" in every listing.
8. **A change needs a second command.** After `config set`, `authorize`,
   `bind` or `unset`, `run` refuses with "resolution is stale" until
   `config resolve` is run. `init`, `config need` and `config approve`
   resolve for the user; saved Docker arguments need no resolution. The
   rule is a memory test.
9. **`--local` means two things and the same name is shared or personal
   depending on the manifest form.** The matrix defines eight personal
   names, the five IDEs and the three agents. `init --required python-ide`
   refuses, "belongs in --local"; `init --need python-ide` accepts the same
   name into the shared manifest. `init --local` seeds the owner's own
   checkout; `capabilities --local` replaces a collaborator's selection.
   `config need` works only on the `need` form and refuses on the
   required/optional form; `capabilities --required` is the reverse.
10. **`versions show` prints a Python dict** for the base line.
11. **Nothing stops, lists or reconnects a session.** The default
    container name is `pycharm-isolated-<user>-<timestamp>` for every IDE;
    a second `run` on the same checkout starts a second container on the
    same persistent home and IDE directories, undetected. The README's
    handoff excerpt quotes `devcapsule stop` and `devcapsule start`, the
    root status file names `workflow list`; neither exists. The command
    reference page and the several-projects page say "Coming soon".
12. **Exit codes do not separate usage from state.** A typo, a missing
    project and a pending decision all exit 2; a declined approval exits 1.
    An agent cannot tell "fix the command" from "a human must decide".
13. **Launcher errors reach the user as tracebacks** (from the code). The
    launcher's error class has 51 raise sites, is not a `CliError`, and the
    entry point catches only usage and `CliError`.

### Design tensions

14. **Launch is a chain of gates.** `run` may ask the approvals key, then
    the upgrade menu with four options and a nested yes/no, and prints the
    host-x11 paragraph on every launch while that choice is unanswered,
    although the contained desktop is the secure default.
15. **Three meanings of "force" land together in rc4.** `run --force`
    accepts a stale resolution once; the planned `run --force-config` skips
    configuration errors; the planned `resolve --force` previews and writes
    nothing.
16. **Audiences mix in one listing.** The legacy `pycharm` command, the
    container-internal `runtime` command, `project recursive-e2e` and
    `run --no-recursive-e2e` sit beside adopter commands. `images build
    --type`, `run --name`, `state adopt --from` and the `authorize`
    positionals have no help text; the help for `run` is a paragraph that
    breaks the group's table. `project --path` here, `--project` on
    `bootstrap`, `images` and `workflow`. `--unverified` on `init`,
    `--unvalidated` on `versions select`. `--less-pedantic` names a mood.
17. **The separate resolve step rests on a proposal that was never
    decided.** D-0004 is `status: proposed`, with no decision date. Its
    premises have since been removed by accepted records: D-0010's owner
    refinement and the 2026-10-22 direction put decisions inside `run`;
    D-0011 retires the base-image question for the recommended base;
    D-0012 retires host-access questions for projects that recommend
    nothing. D-0004's own reopen clause, "the explicit resolution
    checkpoint causes more errors than it prevents", is met by item 2.

### The manifest, on the ai-learning-bootstrap case

The project is a TypeScript frontend and backend, Fastify with REST and
GraphQL, Prisma over a PostgreSQL the owner supplies. A developer working in
a capsule needs three things: an IDE for TypeScript with Node and npm to
build and run, the PostgreSQL credentials, and a handful of application
secrets. This is the manifest the agent produced, as committed:

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

18. **The manifest states one of the three needs, and that one by
    accident.** `postgresql-client` is a command-line tool; the project
    needs a database connection, not `psql`. Node is not required: the
    README says "Node 22 is supplied by the pinned base", which is true of
    `ubuntu-24.04@9` and guaranteed by nothing; a base that drops Node, or a
    developer who selects another base, launches a capsule in which
    `npm ci` fails and DevCapsule said nothing. The IDE is not in the
    manifest because the manifest cannot hold it: `capabilities --required
    frontend-ide` is refused with "IDE/agent choices belong in --local",
    so the agent put `capabilities --local frontend-ide codex-agent` in the
    README, where DevCapsule cannot read it. The credentials are in
    `.env.example` and six README paragraphs, because the manifest has no
    vocabulary for "this project needs these environment variables, and
    each developer supplies the values": `[configuration.values]` declares
    strings, but a declared value has no effect on the capsule except
    through two runtime effects, the memory limit and the command name, so
    a string value never reaches the environment; secret inputs exist, but
    only as declarations by components in the lock, never by the project.
    `set-env` fills the gap on the personal side, invisibly to the project.
    The one thing DevCapsule could have enforced, Node, it does not know
    about; the three things the developer must do, it cannot list.
19. **The manifest does not read as a document.** Every key is quoted,
    including the table names, because the writer renders keys with a JSON
    string encoder; `["capabilities"."sdk-major"]` is an empty table left
    behind to say nothing; `"optional" = []` says nothing; `mount` is an
    absolute path inside a container the reader has not seen; `creator` is
    a URL. The `[workflow]` table is DevCapsule's own provenance, not the
    project's intent, and its `version = "0.3.0"` sits next to a lock that
    pins a base built by `v0.2.12-rc5`. There is no comment, no description,
    no line a project owner would write by hand. Compare DevCapsule's own
    manifest, written by hand, with unquoted keys, a `description` on every
    value and a `justification` on every recommendation: the generated form
    is a different dialect of the same file.
20. **Three vocabularies coexist in one schema version.** `need`,
    `required`/`optional`, and the top-level `workflow-type` beside
    `[workflow] mode`, all under `devcapsule-schema-version = 1`; readers
    accept all three, writers emit the newest, and `config need` edits only
    the oldest. The lock duplicates the manifest's `[workflow]` table, adds
    `capabilities-digest` and `resolution-matrix-version`, and is committed
    although every byte of it is derived.
21. **The owner's prose does the launcher's job.** The README prescribes
    four commands before `run` and warns "Do not launch a Docker PostgreSQL
    instance for this project"; both are things a manifest should say and
    a launcher should enforce. The agent wrote them in prose because the
    manifest could not carry them. Every adopter will do the same.

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

That is the whole list. The base image asks nothing: you trusted DevCapsule
when you installed the launcher, and the project pins the base DevCapsule
publishes (D-0011). Host access asks nothing: the project recommends none,
so the capsule gets bridge networking, no Docker socket, no sudo, the
contained desktop (D-0012). If the project later recommends an IDE, this
list is empty.

With the manifest the project should have had, section 3.6 below, the
list is different and honest about the work:

| You must specify | Why | How |
|---|---|---|
| `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | the project declares them required; the owner supplies the database | the hidden prompt, or `--env NAME` to read your shell's value |
| `AUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | declared required, with the project's one-line reason for each | same |

The IDE is gone from the must-list because the project recommends
`frontend-ide`; Node is gone from the README because the project requires
it and DevCapsule guarantees it. Each value is recorded once per checkout
in the private store outside Git, as `set-env` records it today, and never
printed. `config show` lists each as a row, bound or pending.

| You can specify | Default if you do not | How, persistent | How, this run only |
|---|---|---|---|
| Coding agents | none | `config agent add codex` | `--agent codex` |
| Optional project tools to leave out | all the project offers | `config tool omit browser-automation` | |
| Container memory, CPUs, shared memory | workstation defaults; the project may recommend | `config set memory 6G` | `--memory 6G` |
| Host network, Docker socket, sudo, host browser, host X11 | the secure fallback of each | `config authorize network host` | `--authorize network host` |
| Where your capsule home and IDE state live | managed directories under your XDG data home | `config bind home host-directory:PATH` | |
| Secrets the project declares, such as `codex/openai-api-key` | unbound; the tool asks you to sign in | `config bind codex/openai-api-key host-environment:OPENAI_API_KEY` | |
| Environment variables and extra `docker run` options | none | `config env NAME`, `config docker-args -- ...` | `run -- ...` |
| Exact component versions | the project's lock | `versions select` | |
| The container name | derived from project and checkout | `config set container-name NAME` | `--name NAME` |

Adding Codex asks one more question the first time on this workstation:
accepting OpenAI's terms for the download. It is asked once per vendor
product per workstation, never again per project, checkout or version
(D-0011). Vendor sign-in happens inside the capsule, with the vendor.

What the first `run` prints on this project, interactively:

```text
Project: AI Learning (https://github.com/ccozianu/ai-learning)
Requires: postgresql-client 16, supplied by the base ubuntu-24.04@9.
Base: docker.io/mycodespaceai/devcapsule-base@sha256:8837edd…, published by DevCapsule, trusted on this workstation.
Host access: none recommended; the capsule gets bridge networking, no Docker socket, no sudo, the contained desktop.
Memory: 4G (workstation default). Change: devcapsule project config set memory SIZE

The project needs 7 environment variables from you. Values stay on this computer, outside Git, and are never shown.
  POSTGRES_HOST: the owner supplies the database; do not start one in the capsule
  POSTGRES_HOST [hidden]:
  POSTGRES_DB: same
  POSTGRES_DB [hidden]:
  …
Recorded for this checkout. Change: devcapsule project config env NAME

The project leaves the IDE to you. Choose one:
  1. frontend-ide   VSCodium 1.126.04524
  2. python-ide     PyCharm 2026.2.3
  3. java-ide       IntelliJ IDEA 2026.2.4
  4. eclipse-ide    Eclipse 2026-09
  5. dotnet-ide     Rider 2026.2.5, with the .NET SDK
IDE [1-5]: 1
Recorded for this checkout. Change: devcapsule project config ide NAME

Materializing frontend-ide on ubuntu-24.04@9 …
Desktop: http://127.0.0.1:…/vnc.html?…
Console: http://127.0.0.1:…/?token=…
```

Later launches print the first block in one line each and no question.

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
  and one `y`, as today;
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
devcapsule project config require postgresql-client --because "psql against the owner's database for the manual migration"
devcapsule project config recommend ide frontend-ide
devcapsule project config require env POSTGRES_HOST POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD \
    --because "the owner supplies the database; do not start one in the capsule"
devcapsule project config require env AUTH_SECRET GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET --because "sign-in"
devcapsule project config offer env SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASSWORD SMTP_FROM --because "no email is sent in development"
devcapsule project config recommend memory 6G --because "the test suite builds a 4 GB index"
```

which writes:

```toml
devcapsule-schema-version = 2

[project]
name = "AI Learning"
creator = "https://github.com/ccozianu"

[requires]
tools = ["node", "postgresql-client"]
# psql against the owner's database for the manual migration

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

The shape is illustrative; the properties are not. Keys are bare where
TOML allows it. Every requirement and recommendation carries the owner's
reason, and that reason is what the developer reads when asked. Nothing
derived is in the file: no digest, no matrix version, no mount path, no
`[workflow]` table; what the launcher derives goes to the lock, and the
lock is the launcher's. `init` creates the manifest and lock and the
owner's own checkout, and ends with the owner's own first `run` ready, as
it does today. A recommendation never grants anything; it names the value
the next collaborator is asked about, with the reason they will read. One
manifest form remains; `need` and `required`/`optional` are read and
rewritten on the owner's next edit.

An owner who asks for host access says why, as today:

```bash
devcapsule project config recommend network host --because "..."
```

and an owner who wants the opposite enforced can say so: `config forbid
docker-daemon --because "the owner supplies the database"` makes the
`docker-daemon` row read `forbidden by the project` instead of a question.
Whether a project may forbid a local choice is for the owner to decide,
Part 5.

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
  by the workstation trust record of D-0011.
- The quoted-key manifest writer, the empty `[capabilities.sdk-major]`
  table, the `[workflow]` table in the manifest, and the lock's copy of it.
  The manifest is written in the form an owner would write by hand; what
  the launcher derives goes to the lock only.
- `run --force` and `run --force-config`: when inputs changed and no
  decision is pending, `run` derives and continues; when a decision is
  pending, it asks; a launcher that does not know an optional tool warns
  and continues. There is nothing left to force.

## Part 5: Decisions required from the owner

1. **Supersede D-0004's V1 split formally.** `run` is the first-contact
   command, deriving, reporting and asking in the settled order; `config
   check` is the preflight for scripts. D-0004 section 6 already allows
   this; the record needs a decided status.
2. **May a project recommend an IDE?** The 2026-10-06 refinement makes the
   IDE each developer's. A recommendation keeps it theirs and makes the
   must-list empty for most collaborators. Item 18 is the cost of the
   current answer: the IDE went into the README because the manifest
   refused it.
3. **D-0011 and D-0012 move into the release that carries the new CLI.**
   Without them `run` still asks the base and host questions this design
   removes.
4. **The host-x11 exception in D-0012** ("always an explicit choice"):
   keep, or let the contained desktop be the silent default.
5. **The verbs.** `ide`, `agent add|remove`, `tool omit|restore`,
   `require|offer|recommend` are proposals. The two things to hold are one
   name per concept and no flag that means two things.
6. **Launcher-owned values.** `memory`, `cpus`, `shm-size`,
   `container-name` at least, with workstation defaults and project
   recommendations. Which others.
7. **The console writes through the launcher.** A capsule cannot write the
   host's checkout record (D-0010 refinement). The launcher, attached for
   the whole session, owns the console's configuration endpoint. The
   console before the first launch is out of scope: first contact is the
   terminal.
8. **Where this lands.** Not 0.3.0. The implementation work order names the
   release.
9. **The manifest's vocabulary.** Proposed principle 7: the manifest
   declares required and offered tools, required and offered environment
   variables with the owner's reason, and recommendations, each a thing
   the launcher lists and asks. The values of environment variables are
   personal and private, as `set-env` keeps them today. This is schema
   version 2, which rc4 already plans; the question is whether version 2
   carries this vocabulary or only renames `need`.
10. **May a project forbid a local choice?** The ai-learning owner wants no
    Docker PostgreSQL in the capsule. Today this is a README sentence.
    `forbid` would make it a row. It is the first case where the project
    narrows a personal choice beyond required capabilities and the SDK
    major, so it needs a ruling against principle 4.
11. **The manifest is a document.** Bare keys, a reason on every line that
    asks something of the developer, nothing derived in it. This changes
    the writer and the schema, not the readers, which stay tolerant
    (R-CONFIG-001).

## Out of scope here, catalogued above for the next pass

Items 10 to 13 and 16: session lifecycle commands, exit-code mapping,
launcher error handling, the top-level listing and help texts, the
`images`, `bootstrap` and `workflow` trees. They are deficiencies of the
same surface and belong in the specification, after the `config` and `run`
design above is decided.
