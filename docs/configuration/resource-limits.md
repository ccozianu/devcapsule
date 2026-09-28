---
description: Give the capsule a hard memory limit when the project declares that value, and how declared values are set per checkout.
weight: 5
updated: 2026-09-28
---
# Resource limits

A project can declare ordinary values that shape the container, with their
type and a description. A memory limit is the common one:

```toml
[configuration.values."runtime.memory-limit"]
type = "memory-size"
runtime-effect = "docker.memory-limit"
description = "Hard memory limit applied to the checkout's project container."
```

When a project declares it, set it for your checkout:

```bash
~/.local/bin/devcapsule project config set runtime.memory-limit 8GiB
~/.local/bin/devcapsule project config resolve
```

`config set` accepts only names the project declares and validates the
value against its type; `config list` shows the result and its source. A
declared value never grants host access or a download; those are
authorizations, on [Granting and withdrawing](../containment/granting-and-withdrawing.md).
