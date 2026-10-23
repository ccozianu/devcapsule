---
description: Which choices belong to the project and travel in Git, which are yours and stay on your computer, and what happens when the project changes.
weight: 2
updated: 2026-10-06
---
# Project versus personal

Two kinds of decision shape a capsule, and they live in two places.

## The project's, in Git

`.devcapsule/devcapsule.toml` is the **manifest**: what the project needs,
the values it declares, the host access it recommends and why. Beside it the
**platform lock** pins the exact component versions and the base image that
satisfy the shared requirements and optional enhancements. Both are committed.
[Capabilities and personal choices](capabilities.md) explains how to declare
required SDKs and their major versions, recommend optional tools and keep IDE
and agent selections local. Use `project config capabilities` for those choices.

## Yours, on your computer

Your checkout record holds your IDE, agent and extra-tool selections, plus the authorizations you
granted or refused, the values you set, the directories you bound, and the
base image you consented to. Beside it, DevCapsule-managed directories hold
the capsule's persistent home, the IDE's settings and plugins, and each
agent's sign-in. None of this is in the repository, and none of it is shared
with another checkout of the same project by default;
[What persists](../sessions/what-persists.md) lists the directories.

A **recommendation** is the bridge: a project can recommend an
authorization or a value, with its reason; `config list` labels such rows
`project-recommended`; and you accept it, once, per checkout. A value you
set with `config set NAME default` follows the recommendation; `config
unset NAME` forgets your answer and follows it again.

## When the project changes

A project that changes its manifest or lock can make your recorded choices
stale: the base moved, a recommendation changed, a new tool needs consent.
`project run` asks you to resolve changes to the required environment or personal
answers. An optional-only shared change can be reconciled when the required
environment and permissions are unchanged. Inspect pending choices with:

```bash
~/.local/bin/devcapsule project config show
~/.local/bin/devcapsule project config resolve
```

`show` names each pending decision with the commands for its alternatives;
choose one per decision, not all of them. To accept the project's current
base recommendation, for example:

```bash
~/.local/bin/devcapsule project config authorize base-image default
~/.local/bin/devcapsule project config resolve
~/.local/bin/devcapsule project run
```

`default` accepts the current pin and nothing more: no host access, no
future versions. Editing several choices is a sequence of edits and one
`resolve`; a refused resolution leaves the previous plan intact. Installing
a newer DevCapsule does not change any of this: your lock and your choices
stay until you change them.

## Application environment and credentials

Save application variables on the launcher host, from your registered checkout:

```bash
devcapsule project config set-env POSTGRES_DB ai_learning
devcapsule project config set-env POSTGRES_PASSWORD
devcapsule project config list-env
devcapsule project run
```

Omit the value to enter it at a hidden terminal prompt. This keeps a password
out of shell history and command arguments. Supplying a value is supported
for scripts and ordinary settings. `list-env` shows names and the managed
file's path, never values; `list-env --json` provides the same data as JSON.
Use `config unset-env POSTGRES_PASSWORD` to remove a saved variable.

The file lives under `$XDG_CONFIG_HOME/devcapsule/environments/` (normally
`~/.config/devcapsule/environments/`), with the same project and checkout
identity as its record. It has owner-only permissions and is outside Git.
Each registered checkout has its own file. DevCapsule passes it to Docker
automatically; you do not need to remember its location or run `config resolve`.
The Docker client reads it locally, including with a remote daemon. The
file itself is not mounted into the capsule.

Values are literal single-line text: spaces, quotes, dollar signs and equals
signs are preserved, and an empty value is allowed. There is no shell expansion.
Docker's explicit `--env` options, including variables set by DevCapsule,
take precedence over this file. A raw `--env-file` supplied after `run --`
is applied after the managed file. Existing component secret bindings still
require their declared variables to be exported on the launcher host.

Changes apply to new containers created by `project run`. Restarting an
existing container retains its original environment. Removing a container
keeps the saved file; changing or rolling back a version set does not change
its values. New checkout registrations do not copy credentials automatically.

Storage is plaintext with restricted permissions. The application and agents
inside the capsule are trusted with the environment. DevCapsule keeps these
saved values out of configuration reports, snapshots and launch arguments.
Raw inline Docker arguments are still printed: do not put secrets there.
