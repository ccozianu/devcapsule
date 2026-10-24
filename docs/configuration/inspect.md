---
description: Inspect software, storage and the next launch's choices without changing configuration.
weight: 3
updated: 2026-10-24
---
# Inspect a checkout

`project info` reports software, environment and storage. `project config
show` reports configuration choices. Neither command writes configuration,
downloads components or contacts Docker.

## Software and storage

```sh
devcapsule project info
devcapsule project info --json
```

On the host, `info` describes the next launch. Inside a capsule, it describes
the running software and shows a separate next-launch selection when that
differs. The report lists component versions, environment variables,
persistent paths and temporary storage. Secret values are omitted.

Project commands find the project from its directory or a descendant.
Inside a capsule, inspection can find the capsule's project from `/opt` too.
To select a directory explicitly:

```sh
devcapsule project --path /path/to/project info
```

## Choices and pending decisions

```sh
devcapsule project config show
devcapsule project config show --json
devcapsule project config check
```

`show` lists effective choices, providers, sources and pending decisions.
Each pending decision names the command that answers it. An unregistered
checkout is shown without creating a record.

On the host, `check` validates the contract and returns status 3 for pending
checkout decisions. Candidate-file options check only the candidate contract.
Inside a capsule, `check` cannot assess current host decisions.

The capsule's `show` output uses the configuration captured at launch.
When a console channel is available, it also lists later requests and their
results. Those requests do not update the captured view or the running capsule.
The output names the host command for changes.

`show --json` reports the listing's schema version, checkout identity and rows.
Consumers must check the schema version before interpreting the fields.
[Project versus personal](project-versus-personal.md#from-the-console) describes
the console's request permissions.

`devcapsule project versions show` reports the effective component version set.
It also accepts `--json`; see [Component upgrades](../updates/component-upgrades.md).
