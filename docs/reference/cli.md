---
description: The command tree of the devcapsule launcher, with one line of intent per command, as the executable prints it.
weight: 1
updated: 2026-10-24
---
# Command reference

Every command prints its own help with `--help`; this page is the tree, one
line of intent per command. Commands run on your computer, from the project
folder or with `--path PROJECT`. Inside a capsule, the read-only ones answer
from the capsule's own view; the others name the launcher command to run
outside.

## `devcapsule project`

| Command | Intent |
|---|---|
| `init` | Initialize the project: the manifest with what it requires and offers, the platform lock, your checkout record with your IDE and agents. |
| `run` | Derive the plan from the project, this workstation and this checkout, ask what nobody else can answer, and launch. |
| `config` | This checkout's choices and the project's contract: show what the next launch uses, change one thing, check. |
| `info` | Show project software, environment and persistent storage without changing state. |
| `list` | List the checkouts registered on this computer. |
| `checkout` | This local checkout: register its name, its notifications, its decisions. |
| `state` | Inspect and adopt checkout-scoped persistent state. |
| `versions` | Inspect, try and recover checkout-local component version sets. |

### `init`

```text
devcapsule project init [--require TOOL[=MAJOR]]... [--offer TOOL]... [--ide IDE] [--agent AGENT]...
                        [--name NAME] [--slug SLUG] [--creator CREATOR] [--project-mount PATH]
                        [--regenerate] [--unverified] [--set NAME VALUE]... [--authorize NAME VALUE]... [--bind NAME VALUE]...
```

`--require` and `--offer` are the project's; `--ide` and `--agent` are
yours, recorded in your checkout. New manifests use schema 2; rc3 and older
launchers cannot read them.

### `run`

```text
devcapsule project run [--ide IDE] [--agent AGENT]... [--memory SIZE] [--cpus N] [--env NAME[=VALUE]]...
                       [--trust CHANNEL]... [--authorize NAME VALUE]... [--set NAME VALUE]... [--save]
                       [--name NAME] [--no-update-check] [--print-command] [-- DOCKER-RUN-OPTIONS...]
```

Every configuration flag applies to this launch only; `--save` records the
IDE, agent, memory, CPU, environment and host-access answers as the config
commands would, after every required answer is complete. `--authorize` takes
a host access for one run; `--trust` accepts a channel for this computer.
Everything after `--` goes verbatim to `docker run`, except the options the
launcher composes (`--network`, `--memory`, `--cpus`, `--shm-size`), refused
with the config command named. Without a terminal, a pending decision ends
the command with status 3, naming each decision with its flag and its
command; nothing is written.

## `devcapsule project config`

Read-only:

| Command | Intent |
|---|---|
| `show`, `list` | Every choice of this checkout: the value the next launch uses, its source, what is pending, with the command that settles it. Writes nothing. |
| `check [--manifest FILE --lock FILE]` | Validate the contract and the checkout without writing or launching; exit 3 naming each pending decision, for scripts. |
| `env list` | This checkout's environment variables by name, never their values. |
| `docker-args list` | The saved `docker run` options, environment values masked. |
| `trust list` | The channels this project's software comes through and whether this computer trusts each. |
| `console list` | The console's requests that widen the next launch, awaiting your confirmation. |

Your checkout:

| Command | Intent |
|---|---|
| `ide IDE` | Choose this checkout's IDE: `python-ide`, `frontend-ide`, `java-ide`, `eclipse-ide` or `dotnet-ide`. |
| `agent add\|remove AGENT` | This checkout's coding agents: `codex-agent`, `claude-code-agent`, `antigravity-agent`. |
| `tool omit\|restore TOOL` | The project's offered tools in this checkout. |
| `set NAME VALUE\|default` | `memory` (`6GiB`, `6g`), `cpus` (`4`), or a value the project declares; `default` forgets your answer. |
| `authorize NAME VALUE` | Allow a recommended host access, or consent to an exact base outside DevCapsule's channel; `--all-recommended` reviews every recommendation at once. |
| `deny NAME` | Deny a host access for this checkout, recorded. |
| `forget NAME` | Forget your recorded answer; the default applies, or the recommendation asks again. |
| `approve [NAME...\|--all]` | Record new versions of software you consented to per checkout. |
| `env set NAME [VALUE] [--from-host]` | Save a variable privately, prompt hidden without a value, or pass the host's through at each launch. |
| `env unset NAME` | Remove it. |
| `docker-args set -- OPTIONS...` | Replace the saved `docker run` options. |
| `docker-args clear` | Remove them all, the environment variables among them. |
| `bind NAME PROVIDER:VALUE`, `unbind NAME` | Bind a declared state directory or secret input to your own provider, and return it to the managed default. |
| `console apply\|discard ID` | Run a console request as its command, or forget it. |

Your computer:

| Command | Intent |
|---|---|
| `default memory\|cpus VALUE\|none` | This workstation's default limit, for every project here unless the project recommends or the checkout sets another. |
| `trust accept\|withdraw CHANNEL` | Accept a vendor's or DevCapsule's channel once, every version, every project; or withdraw it. |

The project's, for its owners (they write schema 2):

| Command | Intent |
|---|---|
| `require tool TOOL[=MAJOR] [--because REASON]` | What every checkout must have. |
| `require env NAME... --because REASON` | An input the application needs; asked at the first launch, kept privately. |
| `offer tool TOOL`, `offer env NAME... --because REASON` | What a developer may take or leave. |
| `drop tool\|env NAME` | Remove a requirement or an offer. |
| `recommend ide\|memory\|cpus VALUE [--because REASON]` | An ordinary recommendation, applied unless the developer chooses otherwise. |
| `recommend network\|docker-daemon\|development-sudo\|host-browser VALUE --because REASON` | A host-access recommendation: a question each developer answers; `none` removes it. |

Each owner's command takes `--preview` to validate and show the result
without writing.

## Retired spellings

`config resolve`, `config capabilities`, `config need`, `config unset`,
`set-env`, `unset-env`, `list-env`, `set-extra-docker-args`,
`list-extra-docker-args`, `remove-extra-docker-args`, `init --need`,
`init --required`, `init --optional`, `init --local`, `run --force` and
`run --force-config` are gone from the help and from these pages. A launcher
of {{version}} still answers each with the command that replaced it, so an old
script fails loudly with the new spelling in the message, not silently.

## Other commands

`devcapsule version`, `devcapsule images build|list`, `devcapsule
workflow`, `devcapsule runtime` and `devcapsule pycharm` keep their own
help; they are not part of the project configuration.
