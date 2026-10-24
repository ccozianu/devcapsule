---
description: Which choices belong to the project and travel in Git, which are yours and stay on your computer, which are your computer's, and what happens when the project changes.
weight: 2
updated: 2026-10-24
---
# Project versus personal

Three kinds of decision shape a capsule, and they live in three places.

## The project's, in Git

`.devcapsule/devcapsule.toml` is the **manifest**: what the project
requires and offers, the environment inputs it needs, and what it
recommends, with the reasons. Beside it the **platform lock** pins the
exact component versions and the base image that satisfy them. Both are
committed. [Capabilities and personal choices](capabilities.md) explains
the owner's commands: `config require`, `offer`, `drop` and `recommend`.

## Yours, on your computer

Your **checkout record** holds your IDE, your agents, the offered tools you
omitted, the host access you allowed or denied, the values you set, the
directories you bound and the secrets you bound. Beside it, private files
hold your saved Docker arguments and environment variables, and
DevCapsule-managed directories hold the capsule's persistent home, the IDE's
settings and plugins, and each agent's sign-in. None of this is in the
repository, and none of it is shared with another checkout of the same
project by default. Explicit directory bindings can share storage.
[What persists](../sessions/what-persists.md) lists the directories.

A **recommendation** is the bridge. An ordinary recommendation, the IDE, a
memory limit, a CPU count, applies unless you choose otherwise, and `config
show` says so in its `SOURCE` column. A host-access recommendation is a
question: `run` asks it at your terminal with the project's reason and
DevCapsule's own description of the exposure. You can allow it once,
record an allowance or denial, or defer it.
`config set NAME default` forgets a value and follows the recommendation again.
`config forget NAME` removes an access decision, so a recommendation can ask again.

## Your computer's

Two records belong to the workstation, for every project on it. `config
default memory 8GiB` and `config default cpus 4` set the limits every
capsule here gets unless a project recommends or a checkout sets another.
These defaults live in `$XDG_CONFIG_HOME/devcapsule/workstation.toml`,
normally `~/.config/devcapsule/workstation.toml`.
The **trust record** holds the vendors and channels you accepted once, for
every project and version, as [Vendor software and trust](software-approvals.md)
describes.

## When the project changes

A project that changes its manifest or lock changes what the next launch
derives. `devcapsule project run` derives the plan every time, from the
project, your computer and your checkout, and asks only what nobody else can
answer: an IDE you never chose, an input the project requires, a channel you
have not trusted, a host access the project recommends and you never
answered. Without a terminal, a missing required answer stops the review
with status 3 before it saves answers. The message names each blocking
decision and its flag or command. Unanswered host recommendations use their
secure defaults instead. To inspect first:

```bash
~/.local/bin/devcapsule project config show
~/.local/bin/devcapsule project config check
```

`show` prints every choice with the value the next launch uses, its source
and what is pending; `check` exits 3 when something is. A host answer you
recorded under an earlier recommendation is kept, never asked again; `show`
says what changed beside it. Installing a newer DevCapsule changes none of
this: your lock and your choices stay until you change them.

## Saved Docker arguments

Save the extra Docker options you need once, from your checkout on the
launcher host:

```bash
devcapsule project config docker-args set -- \
  --gpus all \
  --volume "$HOME/.ssh/my_special_key:/home/devcapsule/.ssh/my_special_key:ro"
devcapsule project config docker-args list
devcapsule project run
```

`docker-args set` **replaces the complete saved list**. Quote each value as
you would in `docker run`; DevCapsule preserves the argument tokens and does
not evaluate shell syntax. Use absolute host and container mount paths. GPU
access still needs a suitable runtime and drivers on the host.

`project run` puts saved arguments after its own options and before
arguments you supply after `run --`. Docker decides how repeated options
combine. DevCapsule refuses options that it controls, including `--network`,
`--memory`, `--cpus` and `--shm-size`. It names an alternative when one exists.
Shared-memory size comes from the IDE's runtime template and has no user setting.
`docker-args clear` removes the whole list, including environment variables.
`docker-args list --json` reports the file's path and tokens, with recognized
environment values masked.

## Environment variables

```bash
devcapsule project config env set POSTGRES_PASSWORD
devcapsule project config env set POSTGRES_HOST db.example.org
devcapsule project config env set AWS_PROFILE --from-host
devcapsule project config env list
devcapsule project config env unset POSTGRES_PASSWORD
```

Without a value, `env set` prompts for it hidden, out of shell history, and
keeps it in the private list on your computer; `--from-host` passes your
shell's variable through at each launch instead, without storing its value.
Without a terminal, supply a value or use `--from-host`.
`env list` shows names and whether each value is saved or comes from the host.
At a terminal, `run` asks for a missing required value with a hidden prompt.
A missing host variable also needs an answer when the project requires it.
Without a terminal, that required input stops launch with status 3.
For one launch, use `run --env NAME=VALUE` or `run --env NAME`.
Add `--save` to record the assignment or host-variable binding.

These commands edit the same list as `docker-args set`.
Replacing or clearing that list also removes its environment entries.
Environment helpers refuse ambiguous option tokens, such as `--label --env`.
Replace the list with unambiguous arguments, with environment options first.
Use separate `--env NAME=VALUE` tokens. Short-option clusters such as
`-te NAME=value` are not recognized or masked by these helpers.

The private store is under `$XDG_CONFIG_HOME/devcapsule/docker-arguments/`
(normally `~/.config/devcapsule/docker-arguments/`), keyed by project and
checkout, with owner-only permissions, outside Git and outside anything
mounted into a capsule. DevCapsule masks inline environment values in launch
narration, in the session log and in printed commands; Docker receives the
originals. Processes with Docker inspection access can see those values.
Other options, such as labels, are shown as supplied; keep credentials out of them.

## From the console

The configuration page needs a console-capable base, recipe 11 or later,
and an attached launcher that supports configuration requests.
It shows the listing captured at launch, with its timestamp.
It also shows later requests and their results; these do not update the snapshot.
Inside the capsule, `devcapsule project config show` reports the same view.

The launcher validates console requests with the corresponding CLI command.
It can record IDE and agent choices, tool omissions, values, environment
variables with a literal value, denials and removed bindings.
It can also withdraw workstation trust or clear saved Docker arguments.

Authorization grants, trust acceptance, bindings, replacement Docker
arguments, forgotten answers and host-variable bindings need confirmation
on the host: a forgotten denial can restore workstation trust, and a host
binding exposes a variable. Inspect them with:

```bash
devcapsule project config console list
devcapsule project config console apply ID
devcapsule project config console discard ID
```

Replace `ID` with a listed request ID. Apply or discard each request as appropriate.
An interactive `run` also offers these choices. A noninteractive run keeps
unconfirmed requests pending and continues without applying them.
The console cannot edit the shared manifest or set workstation resource defaults.
No request reconfigures the running capsule.
