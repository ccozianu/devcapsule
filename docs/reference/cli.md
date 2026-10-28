---
description: The command tree of the devcapsule launcher, with one line of intent per command, as the executable prints it.
weight: 1
updated: 2026-10-28
---
# Command reference

This page lists the command tree. Use `--help` on a command to see its
arguments and options. `pycharm check-runtime` is an exception: it runs its
checks even with `--help`.

Project commands run from the project folder. To select another folder,
put the path before the subcommand: `devcapsule project --path PROJECT config show`.
Inside a capsule, supported inspection commands use the capsule's view.
Commands that need host state name the launcher command to run outside.

## `devcapsule home`

These commands run from any directory. They need no project or `--path`.
The [configuration home](../configuration/home.md) holds their settings.

| Command | Intent |
|---|---|
| `show` | Show the home's path and source, format and minimum reader, defaults and accepted channels. |
| `trust list` | List this home's accepted channels, with vendors, products, origins and acceptance dates. |
| `trust accept CHANNEL [--yes]` | Show the channel and terms, then ask for acceptance; `--yes` skips the question. |
| `trust withdraw CHANNEL` | Remove acceptance; report success if the channel was not accepted. |
| `default memory\|cpus VALUE\|none` | Set a resource default for this home, or remove it with `none`. |

Inside a capsule, `show` and `trust list` read the mounted settings.
Commands that change those settings name the command to run outside.

## `devcapsule project`

| Command | Intent |
|---|---|
| `init` | Initialize the project: the manifest with what it requires and offers, the platform lock, your checkout record with your IDE and capabilities. |
| `run` | Derive the plan from the project, this home and this checkout, ask what nobody else can answer, and launch. |
| `config` | This checkout's choices and the project's contract: show what the next launch uses, change one thing, check. |
| `info` | Show project software, environment and persistent storage without changing state. |
| `list` | List the checkouts registered in this home. |
| `checkout` | This local checkout: register its name, its notifications, its decisions. |
| `state` | Inspect and adopt checkout-scoped persistent state. |
| `versions` | Inspect, try and recover checkout-local component version sets. |
| `recursive-e2e` | Run DevCapsule's own recursive validation; this is a project development tool. |

### `init`

```text
devcapsule project init [--require NAME[>=VERSION]]... [--offer CAPABILITY]... [--ide IDE] [--with CAPABILITY]...
                        [--name NAME] [--slug SLUG] [--creator CREATOR] [--project-mount PATH]
                        [--regenerate] [--unverified] [--set NAME VALUE]... [--authorize NAME VALUE]... [--bind NAME VALUE]...
```

`--require` and `--offer` declare project capabilities. `--require` accepts
the same `NAME>=VERSION` minimum as `config require`; quote it in the shell.
`--ide` records your checkout choice. Repeat `--with` to add personal capabilities.
New manifests use schema 2. Candidate 3 and older launchers cannot read them. `--regenerate` rewrites the
platform lock and migrates a schema-1 manifest to schema 2, keeping its leading comment block; a schema-2
manifest is left as it is. With an IDE selected, initialization can still
ask for per-checkout base or vendor consent. For scripts, supply the
`--authorize NAME VALUE` answers it requests. `--set`, `--bind` and
`--authorize` also accept one quoted justification after the value.

### `run`

```text
devcapsule project run [--ide IDE] [--with CAPABILITY]... [--use CAPABILITY=COMPONENT]... [--memory SIZE] [--cpus N] [--env NAME[=VALUE]]...
                       [--trust CHANNEL]... [--authorize NAME VALUE]... [--set NAME VALUE]... [--save]
                       [--name NAME] [--no-update-check] [--no-recursive-e2e] [--print-command] [-- DOCKER-RUN-OPTIONS...]
```

IDE, capability, provider, memory, CPU, environment and host-access flags apply to one launch.
`--save` records those answers after the required review and plan validation
succeed. `--trust` accepts a channel for this home without needing
`--save`. A missing required answer prevents that acceptance from being saved.
`--set` supports only memory and CPUs, including a declared memory alias.
Use `config set` to record other declared values.

`--name` changes the container name for this launch. `--no-recursive-e2e`
disables this project's recursive-validation readiness for this launch.
`--no-update-check` skips the daily distribution refresh; cached critical
notices can still require a decision.

Arguments after `--` go to `docker run`, except options the launcher controls.
These include `--network`, `--memory`, `--cpus` and `--shm-size`.
The error names an alternative when one exists.

Without a terminal, missing required answers stop the review with status 3.
The message gives each blocking decision's flag or command.
Unanswered host recommendations use secure defaults; deferred console requests
stay pending. `config check` reports both kinds as pending with status 3.

`--print-command` does not launch a capsule or save configuration answers.
It can still download components, materialize images and write caches.
Use `config show` or `config check` for inspection without those effects.
Printed environment values are redacted; the printed command is a preview.

## `devcapsule project config`

Read-only:

| Command | Intent |
|---|---|
| `show` | Every choice of this checkout: the value the next launch uses, its source, what is pending, with the command that settles it. Writes nothing. |
| `check [--manifest FILE --lock FILE]` | Validate without writing or launching. On the host, exit 3 for pending checkout decisions. Candidate-file options check only the candidate contract. |
| `env list` | This checkout's environment variables by name, never their values. |
| `docker-args list` | The saved `docker run` options, environment values masked. |
| `trust list` | The channels this checkout's selected lock names and previously accepted channels, with their trust status. |
| `console list` | The console's requests that widen the next launch, awaiting your confirmation. |

Your checkout:

| Command | Intent |
|---|---|
| `ide IDE` | Choose this checkout's IDE: `python-ide`, `frontend-ide`, `java-ide`, `eclipse-ide` or `dotnet-ide`. |
| `add CAPABILITY` | Add a capability the project did not declare. |
| `omit CAPABILITY` | Omit an offered capability or remove a personal addition. |
| `restore CAPABILITY` | Restore an offered capability. |
| `use CAPABILITY COMPONENT\|default` | Choose a provider, or follow the project or catalog again. |
| `set NAME VALUE\|default` | `memory` (`6GiB`, `6g`), `cpus` (`4`), or a value the project declares; `default` forgets your answer. |
| `authorize NAME VALUE [JUSTIFICATION]` | Record host access or per-checkout software consent. `--all-recommended` reviews recommendations interactively. |
| `deny NAME` | Deny a host access for this checkout, recorded. |
| `forget NAME` | Forget your recorded answer; the default applies, or the recommendation asks again. |
| `approve [NAME...\|--all]` | Without arguments, list pending software updates. Names or `--all` record approval for eligible updates. |
| `env set NAME [VALUE] [--from-host]` | Save a variable privately, prompt hidden without a value, or pass the host's through at each launch. |
| `env unset NAME` | Remove it. |
| `docker-args set -- OPTIONS...` | Replace the saved `docker run` options. |
| `docker-args clear` | Remove them all, the environment variables among them. |
| `bind NAME PROVIDER:VALUE`, `unbind NAME` | Bind a declared state directory or secret input to your own provider, and return it to the managed default. |
| `console apply\|discard ID` | Run a console request as its command, or forget it. |

The project's, for its owners (they write schema 2):

| Command | Intent |
|---|---|
| `require 'CAPABILITY>=VERSION'... [--because REASON]` | What every checkout must have. |
| `require env NAME... [--because REASON]` | An input the application needs; asked at the first launch, kept privately. |
| `offer CAPABILITY... [--because REASON]`, `offer env NAME... [--because REASON]` | What a developer may take or leave. |
| `drop [env] NAME...` | Remove a requirement or an offer. |
| `recommend CAPABILITY COMPONENT\|none` | Recommend a resolution, or remove it; no reason applies. |
| `recommend ide\|memory\|cpus VALUE [--because REASON]` | An ordinary recommendation, applied unless the developer chooses otherwise. |
| `recommend network\|docker-daemon\|development-sudo\|host-browser VALUE --because REASON` | A host-access recommendation: a question each developer answers; `none` removes it. |

Each owner's command takes `--preview` to validate and show the result
without writing. Capability edits and resolution recommendations update the
manifest and lock together. Environment declarations and other recommendations
update only the manifest. Required capabilities accept an optional minimum.
`recommend NAME none` removes any supported recommendation.
Capability-edit commands also accept `--unverified` for an unverified combination.

`show`, `check`, `env list`, `docker-args list`, `trust list` and
`console list` accept `--json`.
For trust scope, see
[Vendor software and trust](../configuration/software-approvals.md).
For console permissions and snapshot limits, see
[Project versus personal](../configuration/project-versus-personal.md#from-the-console).

## Other project commands

Each command below follows `devcapsule project`.

| Command | Intent |
|---|---|
| `info [--json]` | Inspect the project's environment and persistent storage. |
| `list` | List registered checkouts in this home. |
| `checkout register NAME` | Give an unregistered checkout a name; it does not rename a registered checkout. |
| `checkout notifications list` | List checkout notifications. |
| `checkout notifications post` | Post a notification to the checkout. |
| `checkout notifications read` | Mark a notification read. |
| `checkout notifications dismiss` | Dismiss a notification. |
| `checkout decisions from-table` | Build a decision document from a table. |
| `checkout decisions check` | Check a decision document. |
| `checkout decisions hand-off` | Print decision text for chat and the available console link. |
| `state adopt` | Adopt persistent state into this checkout. |
| `versions show` | Inspect the effective version set, its origin and validation evidence. |
| `versions history` | List exact version sets with successful local launches. |
| `versions check` | Check upstream component freshness. |
| `versions preview` | Preview a component-version selection without activating it. |
| `versions select PREVIEW` | Prepare a preview identity and select it for the next launch. |
| `versions follow-project [--apply]` | Compare with the project lock; `--apply` prepares and selects it. |
| `versions rollback` | Restore a known-good local version set. |
| `versions propose` | Export an upstream lock patch after successful local use. |
| `versions defer` | Silence checked candidates for seven days. |
| `versions dismiss` | Silence checked candidate versions until different candidates appear. |
| `recursive-e2e preflight` | Check readiness for DevCapsule's recursive validation. |
| `recursive-e2e run` | Run that validation. |
| `recursive-e2e launch-successor` | Launch its successor capsule. |
| `recursive-e2e inspect-successor` | Inspect that successor's result. |

See [Component upgrades](../updates/component-upgrades.md) for version-set examples.

## Retired spellings

Old configuration commands and launch flags refuse with status 2, write
nothing, and name their replacement in one line. Update scripts to use that
replacement. `config capabilities --recover` remains available to repair an
interrupted manifest/lock edit.

## Home and development commands

Each command below follows `devcapsule`.

| Command | Intent |
|---|---|
| `version [--json]` | Show launcher identity and build provenance. |
| `images build` | Build an image from a packaged recipe. |
| `images list` | List local DevCapsule images and their labels. |
| `bootstrap`, `bootstrap project` | Install project workflow files and initialize project memory. |
| `workflow brief` | Show selected workstream context and validation instructions. |
| `workflow status` | Show published workstream states. |
| `workflow claim` | Announce or release a work claim. |
| `workflow publish` | Publish workstream records to the coordination branch. |
| `workflow mail check` | List waiting workstream mail. |
| `workflow mail send` | Deliver an intake item. |
| `workflow mail take` | Take mail into the receiving workstream's intake. |
| `runtime PLAN.json [-- COMMAND ...]` | Run a capsule runtime plan; used by the launcher. |
| `pycharm build` | Build the legacy PyCharm environment. |
| `pycharm check-runtime` | Check an existing PyCharm runtime; requires that environment. |
