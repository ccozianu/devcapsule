---
description: See which host access a project recommends, grant exactly what your work needs, grant it for one run only, and take it back.
weight: 2
updated: 2026-09-28
---
# Granting and withdrawing access

All commands run in your computer's terminal, from the project folder. A
change applies to the next launch: stop the capsule, change, resolve,
launch.

## See what is recommended and what is pending

```bash
~/.local/bin/devcapsule project config show
```

The listing shows every authorization with its state, `authorized`,
`recommended-but-missing`, `required-but-missing` or `stale`, and a `SOURCE`
column naming the document each row comes from: the project's manifest, the
lock, or your own checkout record. The review below the listing names the
pending decisions, their reasons, and the exact commands for each choice. A
recorded refusal is shown as a decision you can keep.

## Grant one thing

```bash
~/.local/bin/devcapsule project config authorize network host
~/.local/bin/devcapsule project config resolve
~/.local/bin/devcapsule project run
```

`authorize` records the exact value and a digest of the recommendation it
answers. If the project later changes its recommendation, the record is
`stale` and you are asked again: a committed change never widens access on
its own. To review every recommendation and accept all of them at once,
interactively:

```bash
~/.local/bin/devcapsule project config authorize --all-recommended
```

It prints every value and reason first and writes only when you press `y`.

## Grant for one run only

```bash
~/.local/bin/devcapsule project run --authorize network host
```

Run-once answers use the same grammar and are never recorded. Everything
after `--` goes verbatim to `docker run`; the options the launcher composes
itself, such as `--network` and `--memory`, are refused with the sanctioned
alternative named.

## Withdraw

```bash
~/.local/bin/devcapsule project config authorize host-x11 false
~/.local/bin/devcapsule project config resolve
```

A refusal is a recorded decision, kept until you change it. To forget a
decision and let the recommendation ask again, `config unset` its name.
Withdrawing does not reconfigure a running capsule; the next launch runs
without the access.

## The values, in one place

| Authorization | Values |
|---|---|
| `network` | `host`; omitted means the ordinary bridge |
| `docker-daemon` | `host-socket`; omitted means no daemon |
| `development-sudo` | `true`, `false` |
| `host-browser` | `true`, `false` |
| `host-x11` | `true`, `false`; never recommended by a project |
| `claude-code-download`, `antigravity-download` | `true`, `false` |
| `base-image` | `default` for the project's current recommendation, or an exact `@sha256:` digest |

What each opens is on [The boundary](the-boundary.md); the full node list
is in [Configuration nodes](../reference/configuration-nodes.md).
