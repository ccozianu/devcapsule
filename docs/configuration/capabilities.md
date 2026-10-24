---
description: Declare what a project requires and offers, recommend an IDE or a memory limit, then choose your own IDE and coding agents without changing the repository.
weight: 25
updated: 2026-10-24
---
# Project capabilities and personal choices

A DevCapsule configuration has two owners. The project declares the shared
contract: the tools every checkout must have, the tools it offers, the
environment inputs it needs, and what it recommends. Each developer chooses
their own IDE, coding agents and host permissions, on their own computer.
A task or workstream does not need its own environment declaration.

## What belongs where

| Choice | Owner | Meaning |
|---|---|---|
| Required tools and their SDK major | Project | Every usable environment supplies them. |
| Offered tools | Project | Enhancements present by default; a checkout can omit them. |
| Required and optional environment inputs | Project | Values the application needs, with the reason; the developer supplies them. |
| Recommendations: IDE, memory, CPUs, host access | Project | Applied unless you choose otherwise; a host access is a question, never a grant. |
| IDE, coding agents, omitted tools | Developer | Personal selections with local version pins. |
| Host access, values, directories, secrets | Developer | Explicit decisions, separate from installing tools. |

One contributor can choose PyCharm and Codex; another, Eclipse and Claude
Code. Neither choice changes what their collaborators install. There is no
implicit coding agent. Component names must be in the installed DevCapsule
catalog; naming a new provider does not install it.

## Create a project environment

From your project directory:

```sh
devcapsule project init --creator mailto:you@example.org \
  --require python=3 --offer browser-automation --ide python-ide --agent codex-agent
```

`--require` and `--offer` write the project's manifest,
`.devcapsule/devcapsule.toml`. In a folder named `sample`, it contains:

```toml
devcapsule-schema-version = 2

[project]
name = "sample"
slug = "sample"
creator = "mailto:you@example.org"
mount = "/workspace/sample"

[capabilities]
required = ["python"]
optional = ["browser-automation"]

[capabilities.sdk-major]
python = 3
```

DevCapsule generates the platform lock beside it, pinning the base image and
the project's tools. Commit both files. `--ide` and `--agent` are yours: they
go to your checkout record on your computer, never to the repository. Omit
`--ide` to leave the choice to each developer. An interactive `init` can ask
for it; otherwise the first `devcapsule project run` asks when no IDE is
selected or recommended. With an IDE selected, `init` can also ask for
per-checkout base consent. When no required answer remains, it ends ready to run.

Manifests of schema 2 need DevCapsule {{version}} or later. A manifest written
by an older launcher, with `capabilities.need`, stays readable: its tools stay
mandatory until the owner classifies them with the commands below, and the IDE
it named stays selected for that checkout.

## Change the shared contract

Tool edits update the manifest and regenerate the lock together.
Environment declarations and recommendations update the manifest only.
Use `--preview` on any owner command to inspect the change without writing:

```sh
devcapsule project config require tool postgresql-client --because "inspect the owner's database"
devcapsule project config offer tool browser-automation
devcapsule project config drop tool browser-automation
devcapsule project config require env POSTGRES_HOST POSTGRES_PASSWORD --because "the owner supplies the database"
devcapsule project config offer env SMTP_HOST --because "no email is sent in development"
devcapsule project config recommend ide frontend-ide
devcapsule project config recommend memory 6G --because "the test suite builds a 4 GB index"
devcapsule project config recommend network host --because "the dev server's ports"
```

`require tool NAME=MAJOR` pins an SDK major; `python=4` fails when no
supported base supplies it. At a terminal, `run` asks for missing required
environment inputs with a hidden prompt and saves the answers privately.
Without a terminal, missing required inputs produce status 3.
Optional inputs are listed but never prompted.
A recommended host access is a question for the developer.
A changed recommendation never widens access on its own.

## Make the checkout yours

```sh
devcapsule project config ide eclipse-ide
devcapsule project config agent add claude-code-agent
devcapsule project config agent remove codex-agent
devcapsule project config tool omit browser-automation
devcapsule project config tool restore browser-automation
```

These change your checkout record only, never the shared files and never
another developer's choices. Only an offered tool can be omitted; a
dependency a required tool needs stays installed even when an offered tool
also uses it. An omission hides a tool from your launches and keeps your
version pin for it; restoring brings that version back. The
[version commands](../updates/component-upgrades.md) manage updates
separately.

`devcapsule project run --ide frontend-ide --agent codex-agent` selects
those tools for one launch. Add `--save` to record those choices for the
checkout. Channel acceptance with `--trust` is a workstation choice and
persists without `--save`.

## See and check

```sh
devcapsule project config show
devcapsule project config check
```

`show` lists every choice with the value the next launch uses, where it
comes from, and what is pending, with the command that settles it. It writes
nothing. On the host, `check` validates the shared contract and lists pending
checkout decisions. It exits 3 when any decision is pending, including an
unanswered host recommendation. Noninteractive `run` can use the secure
default for that recommendation instead.

Neither inspection command downloads tools or contacts Docker.
`check --manifest FILE --lock FILE` validates only the candidate contract;
it does not assess checkout decisions. Inside a capsule, `check` cannot
assess current host decisions. Run it with the host launcher for that check.

If a shared edit is interrupted, readers name the recovery command:
`devcapsule project config capabilities --recover`.
This retained command repairs the manifest/lock transaction.
It refuses to overwrite files changed independently.

## When a contributor has a different launcher

A launcher that understands this contract omits an unknown offered tool with
a warning and runs without it. A failed optional download also permits a
reduced run; a checksum mismatch remains an integrity error. Required tools
and their dependencies have to be available. When a project adds a
requirement that a developer's saved version set cannot meet, `run` stops
with status 3 and names the remedies. Use `devcapsule project versions
follow-project --apply` to return to the shared lock. Alternatively, create
a compatible preview with `versions preview COMPONENT VERSION`, then use
`versions select PREVIEW` with its full preview identity.
The launcher never waives the requirement silently.

Launchers released before this contract cannot read schema 2. Upgrade them
before adopting it. When DevCapsule develops itself, validate the transition
with the identifiable running `devcapsule0` as well as the candidate
executable, and keep a known working host launcher and restart path.
