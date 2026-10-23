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

## Saved Docker arguments

Save the extra Docker options you need once, from your registered checkout
on the launcher host:

```bash
devcapsule project config set-extra-docker-args -- \
  --gpus all \
  --volume "$HOME/.ssh/my_special_key:/home/devcapsule/.ssh/my_special_key:ro" \
  --env POSTGRES_DB=ai_learning
devcapsule project config list-extra-docker-args
devcapsule project run
```

`set-extra-docker-args` **replaces the complete saved list**. Quote each value
as you would in `docker run`; DevCapsule preserves the resulting argument tokens
and does not evaluate shell syntax. Your shell expands `$HOME` when you save
the command. Use absolute host and container mount paths; Docker does not
expand `~` in a container destination. GPU access still requires a suitable
GPU runtime and drivers on the host; this option does not install them.

`project run` puts saved arguments after its own options and before arguments
you supply after `run --`. Docker decides how repeated options combine: an
explicit `--env NAME=value` after a saved assignment replaces it, while
conflicting mount destinations can fail. DevCapsule refuses launcher-owned
options such as `--network` and `--memory`, in their attached and short
spellings too (`-m2g`, `-u1000`); use its configuration commands for those.
It delegates validation of other Docker options to Docker.

```bash
devcapsule project config remove-extra-docker-args
```

This clears the entire saved list, including environment variables added by
the convenience commands below. `list-extra-docker-args --json` reports the
path and argument array, with inline environment values masked in both formats.
There is no unmasked listing option.

### Credentials and environment conveniences

To keep a password out of shell history, omit VALUE for a hidden terminal prompt:

```bash
devcapsule project config set-env POSTGRES_PASSWORD
devcapsule project config list-env
devcapsule project config unset-env POSTGRES_PASSWORD
```

These commands edit or inspect environment options in the **same saved list**.
`set-env KEY [VALUE]` replaces that variable's saved env options in place, or
adds it at the front of the list, and preserves the other arguments.
`unset-env KEY` removes them. `list-env [--json]` shows names only.
DevCapsule does not carry Docker's option table, so an env-looking token
right after a bare option (`--label -eNAME=value`, `--label --env ...`)
may be that option's value, and the token after it is unsettled too.
Any such ambiguity in the saved list makes every convenience command
refuse, edits and listing alike, naming the argument's position, never
its text. Replace the complete list with `set-extra-docker-args`, placing
environment options first or after a value; the list itself launches
unchanged, and reports mask every value that might be one. The convenience input accepts literal single-line UTF-8 values,
including empty values. Use the prompt for values beginning with a dash.
The general Docker argument list can also include `--env NAME` to inherit an
exported variable on each launch, or `--env-file /private/path/file` to let
the Docker client read your own file.

The private JSON store is under `$XDG_CONFIG_HOME/devcapsule/docker-arguments/`
(normally `~/.config/devcapsule/docker-arguments/`), keyed by project and
checkout. `list-extra-docker-args` shows its exact path. It has owner-only
permissions, is outside Git and the mounted configuration directory, and is
not copied into configuration snapshots or resolutions. Each checkout has its
own list. No `config resolve` is needed after changing it. New containers use
the current list; restarting an existing container retains its old settings.
Removing a container or rolling back a version set does not clear the list.

DevCapsule masks inline environment values in launch narration, in the
launcher's session log and in printed commands too. A `--print-command` result containing `<redacted>` is a preview;
use `project run` to launch with the actual saved arguments. Docker receives
the original arguments, so their values remain visible to Docker and the
trusted processes that can inspect it. Other option types, such as labels,
are shown as supplied; do not put credentials in them.
