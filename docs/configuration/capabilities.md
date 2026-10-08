---
description: Declare a project's required SDKs and optional tools, then choose your own IDE and coding agents without changing the repository.
weight: 25
updated: 2026-10-06
---
# Project capabilities and personal choices

A DevCapsule configuration describes the developer environment for a project.
It has two owners: the project defines the shared development contract, and
each developer chooses their personal tools and host permissions. A task or
workstream does not need its own environment declaration.

## What belongs where

| Choice | Owner | Meaning |
|---|---|---|
| Required capabilities | Project | Every usable environment must supply them. |
| SDK major | Project | Contributors use the same required SDK major. |
| Optional capabilities | Project | Enhancements offered by default; a checkout can omit them. |
| IDE, coding agents, extra tools | Developer | Personal selections with local version pins. |
| Host access, credentials and directories | Developer | Explicit decisions, separate from installing tools. |

For example, a Python project can require Python major 3 and recommend browser
automation. One contributor can choose PyCharm and Codex; another can choose
Eclipse and Claude Code. Neither choice changes what their collaborators install.
There is no implicit coding agent. Component names must be supported by the
installed DevCapsule catalog; naming a new provider does not install it automatically.

## Create a project environment

From your project directory:

```sh
devcapsule project init --creator mailto:you@example.org \
  --required python --sdk-major python=3 \
  --optional browser-automation --local python-ide codex-agent
```

The project manifest, `.devcapsule/devcapsule.toml`, records shared intent:

```toml
[capabilities]
required = ["python"]
optional = ["browser-automation"]

[capabilities.sdk-major]
python = 3
```

DevCapsule generates the platform lock alongside it. Commit both shared files.
The lock pins the base and project tools. Your IDE and agent selection is stored
in your workstation's checkout record, outside the repository. Its exact tool
versions stay local too.

Omit `--local` to leave the IDE choice to the developer. Before launching,
choose a supported IDE, review permissions and resolve the checkout:

```sh
devcapsule project config capabilities --local python-ide codex-agent
devcapsule project config resolve
```

`resolve` reports any outstanding authorization decisions and their commands.
Installing an optional tool does not grant Docker access, expose a host directory,
or accept a license. Answer those questions, resolve again, then run
`devcapsule project run`.

SDK-major constraints currently support Python and .NET. A requirement such as
`python=4` fails when no supported base supplies it. Unknown SDK majors and
unverifiable local base overrides cannot satisfy a mandatory guarantee.

## Change the shared contract

Use commands to author configuration. Each supplied flag replaces that list;
omitting a flag keeps its current value. Supplying a flag with no entries clears
its list. For example:

```sh
devcapsule project config capabilities --required python docker-cli \
  --optional browser-automation --sdk-major python=3 --preview
```

`--preview` validates the candidate without writing it. Repeat without
`--preview` to update the shared manifest and lock. Changes must keep SDK-major
constraints attached to required capabilities. IDE and agent choices belong in
`--local`, rather than new shared requirements.

Older manifests using `capabilities.need` remain readable. Their listed tools
remain mandatory until a project owner explicitly classifies them with the
command above. The legacy `init --need` interface remains available for that
representation; new required/optional projects use `init --required` and
`config capabilities` for subsequent edits.

## Make the checkout yours

```sh
devcapsule project config capabilities --local eclipse-ide claude-code-agent
```

This replaces your personal selection. It changes neither shared file nor
unrelated host decisions. Existing local version pins for retained tools survive
reselection. The [version commands](../updates/component-upgrades.md) manage
updates separately.

To skip the project's browser-testing enhancement on this workstation:

```sh
devcapsule project config capabilities --without browser-automation
```

To restore all project enhancements:

```sh
devcapsule project config capabilities --without
```

Only optional capabilities can be omitted this way. A dependency needed by a
mandatory capability remains installed even if it also supplies an optional one.
A local choice cannot waive the project's SDK major or remove a mandatory tool.

An omission hides a tool from your launches; it does not change what your
checkout has selected. Your version pins, including an explicit local version
set, keep the omitted tool's exact version, and restoring the enhancement
brings that version back. Selecting a tool the project already lists keeps the
project's pin rather than taking a newer one from the launcher's catalog.

## Validate and recover

```sh
devcapsule project config check
devcapsule project config check --manifest /path/to/candidate.toml \
  --lock /path/to/candidate.lock
```

`check` validates the shared capability contract offline. It does not register a
checkout, write a resolution, download tools, contact Docker or grant permissions.
It is not evidence that a container has launched successfully. Use `config resolve`
and the normal launch for checkout permissions and runtime acceptance.

Writers validate the starting documents and candidate before replacement.
Shared edits have a recovery journal: the manifest replacement commits the pair.
If a process stops between writes, readers refuse the intermediate state and give
the recovery command:

```sh
devcapsule project config capabilities --recover
```

Recovery restores the matching lock or completes its replacement. It refuses to
overwrite files changed independently while the transaction was pending.

## When a contributor has a different launcher

A reader that understands this capability contract can omit an unknown optional
tool with a warning. A failed optional download also permits a reduced run;
a checksum mismatch remains an integrity error. The warning names the missing enhancement. Required tools
and their dependencies still have to be available. The reader derives its usable
selection locally and leaves the shared manifest and lock intact.

Optional-only shared changes can be reconciled for the next launch when the
required environment, personal answers and permissions are unchanged. Changes to
the required environment or local answers still require explicit resolution.
Commands preserve opaque optional pins when they can do so safely; an unsafe
mutation is refused before replacing the existing documents.

Binaries released before this contract cannot acquire these semantics from a
configuration file. Upgrade those launchers before adopting the representation.
When DevCapsule develops itself, validate the transition with the identifiable
running `devcapsule0` as well as the candidate executable. Preserve a known working
host launcher and restart path; a configuration listing alone is not validation.
