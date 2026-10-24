---
description: The capsule's memory limit and CPU count, for a checkout, for your whole computer, or as a project's recommendation, and the values a project declares.
weight: 5
updated: 2026-10-24
---
# Resource limits

The launcher owns two limits of every capsule: its memory and its CPU count.
They are set in three places, and the most specific one wins:

```bash
~/.local/bin/devcapsule project config set memory 8GiB
~/.local/bin/devcapsule project config set cpus 4
~/.local/bin/devcapsule project config default memory 8GiB
~/.local/bin/devcapsule project config recommend memory 6G --because "the test suite builds a 4 GB index"
~/.local/bin/devcapsule project run --memory 12g
```

- `config set` records the value for this checkout; `config set memory
  default` forgets it.
- `config default` records your computer's value, used by every project
  here that recommends none; `config default memory none` removes it.
- `config recommend`, the project owner's, writes the manifest with the
  reason; it applies to every checkout that set nothing.
- `run --memory` and `run --cpus` apply to one launch; `run --save` records
  them for the checkout.

Memory takes Docker's spellings, `6g`, `6GiB`, `6144m`. `config show` prints
the value the next launch uses and its source: the checkout, the project's
recommendation, or the workstation default. Anything else about the
container goes through the saved Docker arguments on
[Project versus personal](project-versus-personal.md#saved-docker-arguments).

## Values a project declares

A project can declare other values with their type and a description:

```toml
[configuration.values."build.workers"]
type = "integer"
description = "Parallel build jobs; the integration suite needs at least 4."
```

Set them the same way, `config set build.workers 4`; `config set` accepts
only names the project declares and validates the value against its type. A
declared value never grants host access or a download; those are
authorizations, on [Granting and withdrawing](../containment/granting-and-withdrawing.md).
A manifest written before {{version}} that declared a memory limit under its own
name, such as `runtime.memory-limit`, keeps working: `config set` under that
name records the launcher's `memory`, and `config show` lists it as
`memory`.
