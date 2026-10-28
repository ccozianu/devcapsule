---
description: See which host access a project recommends, allow exactly what your work needs, allow it for one run only, and take it back.
weight: 2
updated: 2026-10-24
---
# Granting and withdrawing access

All commands run in your computer's terminal, from the project folder. A
change applies to the next launch: stop the capsule, change, launch.

## See what is recommended and what is pending

```bash
~/.local/bin/devcapsule project config show
```

The listing shows each access, its effective value and its source.
The source can be the project, the lock, your checkout answer or the secure default.
Pending rows give the commands that settle them. A recorded denial is shown
as your decision.

## Allow one thing

```bash
~/.local/bin/devcapsule project config authorize network host
~/.local/bin/devcapsule project run
```

`authorize` records the exact value and a digest of the recommendation it
answers. When you run without having answered, `run` asks at the terminal,
with the project's reason and DevCapsule's own description of what the
access opens: allow for this checkout, allow once, deny for this checkout,
or not now, which launches with the secure default and asks again next
time. If the project later changes its recommendation, your answer is kept
and never asked again; `config show` says what changed beside it, and a
committed change never widens access on its own. To review every
recommendation and accept all of them at once, interactively:

```bash
~/.local/bin/devcapsule project config authorize --all-recommended
```

It prints every value and reason first and writes only when you press `y`.

## Allow for one run only

```bash
~/.local/bin/devcapsule project run --authorize host-browser true
```

Without `--save`, these flags apply only to this launch.
Add `--save` to record the answers for the checkout.
The launcher provides `network`, `docker-daemon`, `development-sudo`,
`host-browser` and `host-x11` on every project. They need no project
recommendation. `config show` lists the available authorizations.
Everything after `--` goes verbatim to `docker run`; the options the
launcher composes itself, such as `--network` and `--memory`, are refused
with an alternative named when one exists. Shared-memory size has no user setting.

## Deny and forget

```bash
~/.local/bin/devcapsule project config deny host-x11
~/.local/bin/devcapsule project config forget network
```

A denial is a recorded decision, kept until you change it. `forget` removes
your answer: the secure default applies, and a recommendation asks again.
Neither reconfigures a running capsule; the next launch runs without the
access.

## The values, in one place

| Access | Values |
|---|---|
| `network` | `host`, `bridge`; `bridge` is the default when unanswered; available on every project |
| `docker-daemon` | `host-socket`, `none`; `none` denies host-daemon access |
| `development-sudo` | `true`, `false` |
| `host-browser` | `true`, `false` |
| `host-x11` | `true`, `false`; never recommended by a project; the contained desktop is the default, and a base without one asks for your explicit consent |
| `base-image` | `default` or the exact digest currently pinned by the lock; a local image tag or ID selects a local base |

Home trust can cover vendor downloads and DevCapsule's published bases.
Per-checkout consents remain supported. See
[Vendor software and trust](../configuration/software-approvals.md). What
each access opens is on [The boundary](the-boundary.md); the full node list
is in [Configuration nodes](../reference/configuration-nodes.md).
