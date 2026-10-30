---
description: The capsule's memory limit and CPU count, for a checkout, for your configuration home, or as a project's recommendation, and the values a project declares.
weight: 5
updated: 2026-10-28
---
# Resource limits

The launcher owns two limits of every capsule: its memory and its CPU count.
For each limit, the launcher uses the first available value in this order:
the run flag, the checkout answer, the project recommendation, then the
home default. If none supplies a value, DevCapsule sets no limit.

```bash
~/.local/bin/devcapsule project config set memory 8GiB
~/.local/bin/devcapsule project config set cpus 4
~/.local/bin/devcapsule home default memory 8GiB
~/.local/bin/devcapsule project config recommend memory 6G --because "the test suite builds a 4 GB index"
~/.local/bin/devcapsule project run --memory 12g
```

- `config set` records the value for this checkout; `config set memory
  default` forgets it.
- `home default` records the home's value, used by every project
  launched from it that recommends none; `home default memory none` removes it.
- `config recommend`, the project owner's, writes the manifest with the
  reason; it applies to every checkout that set nothing.
- `run --memory` and `run --cpus` apply to one launch; `run --save` records
  them for the checkout.

Memory accepts sizes such as `6g`, `6GiB` and `6144m`.
The listing normalizes these to `6GiB` or `6144MiB`.
CPUs must be a positive integer; fractional values such as `1.5` are refused.
`config show` prints each value and its source.

Other supported Docker options use the
[saved Docker arguments](project-versus-personal.md#saved-docker-arguments).
Some options remain reserved. For example, the IDE's runtime template fixes
shared-memory size; raw `--shm-size` cannot change it.
Use `run --name NAME` to change the container name for one launch.

## Values a project declares

A project can declare other values with their type and a description:

```toml
[configuration.values."build.workers"]
type = "integer"
description = "Parallel build jobs; the integration suite needs at least 4."
```

Set them the same way, `config set build.workers 4`; `config set` accepts
the two launcher values and names the project declares. It validates each
value against its type. Declared values grant no host access or downloads.
Those need authorizations, on [Granting and withdrawing](../containment/granting-and-withdrawing.md).
Older manifests can declare a memory value under a name such as
`runtime.memory-limit`, with `runtime-effect = "docker.memory-limit"`.
The launcher still reads its recommendation and any saved answer as `memory`.
To change it, use `config set memory SIZE`.
`config set runtime.memory-limit SIZE` now refuses and names that replacement.
`config set memory default` clears the old answer and follows defaults again.
