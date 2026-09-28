---
description: What survives when a capsule stops, where each persistent directory lives on your computer, and what is deliberately temporary.
weight: 2
updated: 2026-09-28
---
# What persists

The container is disposable. Everything you would miss lives outside it, in
directories on your computer that DevCapsule mounts into every session of
this checkout. `project info` prints the exact list with the backing path
of each; this is what it contains.

| In the capsule | Kind | What it holds |
|---|---|---|
| The project folder | source | Your files, shared with your computer as they are |
| `/home/devcapsule` | durable | The capsule user's home: shell history, tool configuration, `xtras` |
| `/opt/xtras` | durable | Alias of `~/xtras`; [extra tools](../configuration/extra-tools.md) |
| `~/.claude`, `~/.codex`, `~/.gemini` | durable | Each agent's configuration and sign-in |
| The IDE's configuration and plugins | durable | Settings, extensions, keymaps |
| The IDE's log and system directories | state, cache | Reconstructable; caches may be cleared |
| `~/.cache` | cache | Reconstructable |
| `/tmp` and the container's own filesystem | temporary | Gone when the container is removed |

Durable and state directories live under your local DevCapsule storage, per
checkout, in the XDG data, state and cache locations of your user. A second
checkout of the same project gets its own set; binding a directory
explicitly, as [Configuration nodes](../reference/configuration-nodes.md)
describes, shares or relocates it.

Persistence is not backup. It keeps a session's state on one computer; it
does not copy anything to another machine and it does not replace Git for
your source.
