---
description: Require or offer capabilities, set a minimum, recommend a provider, and choose what this checkout uses.
weight: 25
updated: 2026-10-24
---
# Capabilities and components

A **capability** names what an environment supplies. A **component** is the
software that supplies it. For example, `browser-automation` is a capability
and `playwright` is its component. The catalog lists each capability's
providers. Each selected capability resolves to one provider.

The project requires or offers capabilities and can recommend an IDE and a
resolution. A requirement applies to every checkout. An offer is present
unless you omit it. A resolution recommendation names the provider the
project prefers. Your checkout can choose another provider from the catalog.

The **IDE** is the capability with a special launch role. Its component opens
the project and owns the container's lifetime: the container ends when the
IDE exits. The IDE can use the display. Coding agents are ordinary
capabilities whose components come through vendor channels.

## Create the shared configuration

From your project directory:

```sh
devcapsule project init --creator mailto:you@example.org \
  --require java --offer browser-automation --ide java-ide
```

`--require` and `--offer` write capability names to the manifest.
`--ide` records your checkout's choice. Use `config require` below to add
a minimum. The relevant manifest section is:

```toml
[capabilities]
required = ["java"]
optional = ["browser-automation"]
```

Initialization also writes the platform lock. Commit the manifest and lock
together. The lock pins the resolved components, not every possible provider.
Without an IDE choice, an interactive initialization can ask for one.
You can leave that decision for the first run.

## Require and offer capabilities

```sh
devcapsule project config require 'java>=21' --because "the build targets Java 21"
devcapsule project config require 'playwright>=1.21'
devcapsule project config offer codex-agent --because "the project uses Codex instructions"
devcapsule project config drop browser-automation
```

A minimum uses one relation: `NAME>=VERSION`, meaning that version or newer.
Quote it in a shell, where `>` redirects output. The launcher compares dotted
integers from left to right. It reads a leading `v` and build metadata, so
`v22.23.1` and `25.0.4+7` compare as `22.23.1` and `25.0.4`.
Prerelease minimums, upper bounds, ranges and exact constraints are unsupported.
The lock supplies the exact version pin.

`require 'java>=25'` replaces an earlier Java minimum. `drop java` removes
the requirement regardless of its minimum. An unmet minimum refuses before
writing. Today's catalog cannot satisfy `python>=3.14`; its bases supply
Python 3.12.

Capability edits update the manifest and lock together. Add `--preview` to
an owner command to validate and inspect its result without writing.
An offered capability can be unavailable on an older launcher; the launcher
warns and omits it. Required capabilities must be available.

Environment inputs keep the `env` word:

```sh
devcapsule project config require env POSTGRES_HOST POSTGRES_PASSWORD --because "the application connects to the database"
devcapsule project config offer env SMTP_HOST --because "email is optional in development"
```

These commands write declarations, not values. At a terminal, `run` asks for
missing required values with a hidden prompt and saves them privately.
Without a terminal, a missing required value stops launch with status 3.
Optional inputs are listed but never prompted.

## Recommend an IDE or resolution

```sh
devcapsule project config recommend ide frontend-ide
devcapsule project config recommend frontend-ide codium
```

The first command recommends the IDE capability. The second recommends its
provider, recorded separately:

```toml
[recommendations]
ide = "frontend-ide"

[capabilities.resolution]
frontend-ide = "codium"
```

A resolution takes no reason. The capability's requirement or offer can
already explain why it is needed. A resolution recommendation updates the
manifest and lock together. It does not select a capability by itself.
`recommend frontend-ide none` removes that provider recommendation.

Resource and host-access recommendations keep their own names:

```sh
devcapsule project config recommend memory 6G --because "the test suite builds a large index"
devcapsule project config recommend network host --because "the dev server uses host ports"
```

A host-access recommendation asks for your decision. It grants no access.
A provider recommendation also leaves vendor trust and consent in place.

## Choose for this checkout

```sh
devcapsule project config ide eclipse-ide
devcapsule project config add claude-code-agent
devcapsule project config omit codex-agent
devcapsule project config restore codex-agent
```

`add` selects a capability the project did not declare. `omit` leaves out an
offer or removes your addition. `restore` brings an offered capability back.
A required capability cannot be omitted. An omitted offer keeps its local
version pin; a required dependency remains installed.

`config use CAPABILITY COMPONENT` chooses a provider when the catalog lists
several. `config use CAPABILITY default` removes your choice. The launcher
then follows the project's recommendation, or the catalog's first eligible
provider. The current catalog has one provider per capability, so `use`
reports that no choice exists. A provider must meet the project's minimum.

Your choices and local pins stay in the checkout record. The
[version commands](../updates/component-upgrades.md) manage updates separately.
For one launch:

```sh
devcapsule project run --ide frontend-ide --with codex-agent
```

`--with` can repeat. `--use CAPABILITY=COMPONENT` chooses a provider for one
launch when alternatives exist. Add `--save` to record these choices.
Channel acceptance through `--trust` belongs to the workstation and persists
without `--save` after the required review succeeds.

## Inspect and recover

```sh
devcapsule project config show
devcapsule project config check
```

`show` lists effective choices, their sources, providers and pending decisions.
A requirement row includes its minimum and resolved version. `check` validates
the contract and reports pending host decisions with status 3. Neither command
downloads components or contacts Docker. Inside a capsule, inspection uses
the captured launch view; current host decisions need the host launcher.

`check --manifest FILE --lock FILE` validates a candidate contract only.
`config capabilities --recover` repairs an interrupted manifest/lock edit.
Recovery refuses to overwrite files changed independently.

A saved version set must still meet new project requirements. An incompatible
set stops `run` with status 3. `devcapsule project versions follow-project
--apply` returns to the shared lock. The launcher never waives a requirement.

## Existing files and older launchers

This launcher reads existing checkout selections, offers, IDE recommendations,
provider locks and trust records. It ignores the removed SDK-major table with
a note. The next owner write removes that table. An unchanged manifest keeps
its old lock current until the next shared edit.

Candidate 4 reads a resolution recommendation under `capabilities` and ignores
it. It uses the catalog's first provider, currently the only provider of each
capability. Candidate 4 cannot read requirements with minimums or component
aliases. Launchers before candidate 4 cannot read schema 2.
