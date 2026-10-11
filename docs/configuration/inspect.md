---
description: See what a checkout will run and what it is running, with project info and the configuration listing, without changing anything.
weight: 1
updated: 2026-10-09
---
# Inspect a checkout

Two read-only commands answer "what do I have here?": one for the software,
environment and storage, one for the recorded configuration choices. Neither
initializes, resolves, repairs or writes anything.

## Software, environment, storage

```bash
~/.local/bin/devcapsule project info
~/.local/bin/devcapsule project info --json
```

On your computer, run it from the project folder or any folder beneath it;
it describes the **next launch**. Inside a running capsule, `devcapsule
project info` works from anywhere, including `/opt`, and describes the
**running** capsule from the evidence captured at launch, with the next
launch's selection shown separately when it differs. The report has four
parts:

- **Components** and their versions: the IDE, the agents, and, inside a
  capsule, a *next launch* block when the project has moved on.
- **Environment**: every variable DevCapsule provides, with its value and
  its purpose, secret values omitted. This is what tells an agent where its
  configuration lives and what `PATH` contains.
- **Persistence**: every persistent path in the capsule with the directory
  on your computer that backs it, whether it is source, durable, state or
  cache, and whether it belongs to this checkout.
- **Temporary**: what disappears when the container is removed.

Use `--json` when an agent or a script is the reader. To pick a project
explicitly, `~/.local/bin/devcapsule project --path /path/to/project info`;
a project nested inside another keeps its own identity.

## The recorded choices

```bash
~/.local/bin/devcapsule project config list
~/.local/bin/devcapsule project config list --json
~/.local/bin/devcapsule project config show
```

`list` is data: every declared value, binding and authorization with its
state and its `SOURCE`, the document it comes from. `show` adds the files
behind the resolution and the review: pending decisions with their remedies,
your recorded base beside the project's current recommendation, and whether
resolving is needed. Inside a capsule both are read-only views of the next
launch, and the output names the launcher command to change anything. They
find the capsule's project from any directory, `/opt` included; a command
that would change the configuration answers with that launcher command
instead. A project nested inside the capsule keeps its own identity.

`list --json` is the same table as a document: `schema-version`, the
project and checkout identity, and one object per row with the table's
columns as keys. Inside a capsule the document carries the mounted record
instead of rows, and names the launcher command. The shape is a contract,
read by the capsule web console; a reader can rely on `schema-version` 1.
On a host, either format creates missing checkout records. With `--json`,
initialization notices go to standard error.

Running versions, as opposed to the next launch's selection, are also on
`~/.local/bin/devcapsule project versions show`, with `--json` under the same
contract; see [Component upgrades](../updates/component-upgrades.md).
