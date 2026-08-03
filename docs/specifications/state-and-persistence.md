# DevCapsule V1 State And Persistence Specification

Status: adopted supporting specification for D-0001.

## Purpose

DevCapsule must preserve useful developer state without teaching its core about
every IDE, agent, language tool, or database. It therefore provides a
persistent container home as the universal fallback and allows curated
components to declare additional named state locations when their lifecycle or
storage needs differ.

The developer's real host home is never mounted as the container home.
DevCapsule creates and manages a separate home for each local checkout by
default.

## Workstation Roots

DevCapsule follows the XDG base-directory split on Linux:

```text
configuration: $XDG_CONFIG_HOME/devcapsule
durable data:  $XDG_DATA_HOME/devcapsule
runtime state: $XDG_STATE_HOME/devcapsule
cache:         $XDG_CACHE_HOME/devcapsule
```

When an XDG variable is unset or empty, the defaults are:

```text
configuration: ~/.config/devcapsule
durable data:  ~/.local/share/devcapsule
runtime state: ~/.local/state/devcapsule
cache:         ~/.cache/devcapsule
```

Non-XDG platforms use their platform-appropriate user configuration, data,
state, and cache directories. `devcapsule config path` and
`devcapsule state roots` print the resolved locations.

Only DevCapsule configuration and developer-owned authorization records belong
under the configuration root. Mutable container homes, IDE state, extensions,
agent conversations, credentials stored by tools, and database files do not.
Keeping mounted payloads out of the configuration root prevents a large cache
or database from polluting configuration backups and prevents a container from
being given write access to DevCapsule's own policy files.

The repository's committed `.devcapsule/` directory is unrelated to these
workstation roots. It contains portable project declaration and lock files,
never personal state or credentials.

## Project And Checkout Namespace

All automatically managed state uses the canonical project identity and the
checkout identity already defined by D-0001. The default, normally sole
checkout needs no name; additional checkouts use workstation-owned names. The
examples below abbreviate either namespace as `{checkout}`.

```text
projects/<encoded-creator>/<encoded-slug>/<default-checkout-state>
projects/<encoded-creator>/<encoded-slug>/checkouts/<checkout-name>/<state>
```

The encoding and checkout record are shared with project-local configuration.
DevCapsule verifies the checkout's observed canonical path before using its
state. A clone or second worktree receives a different checkout namespace and
cannot inherit credentials merely by copying the committed project identity.

Developer-owned checkout input and generated resolution are stored under the
configuration root as `devcapsule.checkout.toml` and
`devcapsule.resolved.toml`. Additional checkout pairs use
`checkouts/<checkout-name>.checkout.toml` and
`checkouts/<checkout-name>.resolved.toml`. Adopted host paths and persistent
host-access decisions belong only in checkout input. The resolved file is a
regenerable effective view and never becomes another configuration layer.

## Persistent Home

Every normal V1 launch has a persistent, DevCapsule-managed home:

```text
host:      $XDG_DATA_HOME/devcapsule/{checkout}/home
container: /home/devcapsule
environment:
  HOME=/home/devcapsule
```

The container user owns this directory. DevCapsule repairs ownership only for
its own managed directory and never recursively changes ownership on a
developer-supplied external directory.

The persistent home is the compatibility mechanism for supported tools without
an explicit state contract. Codex, Claude Code, Antigravity, shell
configuration, and future supported tools may persist credentials,
conversations, and preferences in their normal locations beneath `HOME`
without special cases in the launcher.

No additional in-container home variable is defined. Programs already agree on
`HOME`, and introducing `DEVCAPSULE_HOME` would create two possible answers.
DevCapsule may expose informational variables such as
`DEVCAPSULE_PROJECT_ID` and `DEVCAPSULE_CHECKOUT`, but programs must use
standard `HOME` to locate personal state.

The default home is scoped to one checkout and may contain secrets. It is not
committed, copied into an image, or shared with another checkout. A developer
may select a named workstation profile to share a home deliberately. Because
that may expose credentials and conversations across projects, every checkout
must authorize the profile separately. A committed project declaration cannot
select it.

A developer-owned local setting may relocate the persistent home. For
transition from existing launchers, the host environment variable
`DEVCAPSULE_HOME_DIR` may provide the same developer-owned override. The local
setting wins over the environment variable, and an explicit run-once CLI value
wins over both. DevCapsule shows a warning and asks for approval before first
mounting an existing external directory. It never accepts this path from the
committed project declaration.

## Component State Contracts

A curated component may declare zero or more state slots. DevCapsule core does
not hard-code universal `ide-config`, `ide-plugins`, agent, or database mount
names. A slot is namespaced by its component and has this logical schema:

```toml
[[state]]
name = "extensions"
container-path = "/home/devcapsule/.local/share/codium/extensions"
kind = "durable"
sensitivity = "personal"
default-scope = "checkout"
storage = "directory"
concurrent = false
```

Each slot declares:

- a stable component identifier and component-local state name;
- one absolute container path;
- its lifecycle kind: `durable`, `state`, or `cache`;
- its sensitivity: `ordinary`, `personal`, or `credentials`;
- its default scope: `checkout` or `project`;
- its storage implementation: `directory` or `docker-volume`;
- whether concurrent attachment by more than one capsule is supported;
- expected container ownership and permissions;
- the effect of deleting it and whether it can be reconstructed.

Only trusted, versioned DevCapsule catalog metadata may define container paths
or storage behavior. A committed project may request the component capability,
but it cannot provide a host path or weaken the slot's sensitivity and sharing
rules.

Logical slot names look like:

```text
pycharm/config
pycharm/plugins
codium/user-data
codium/extensions
postgres/data
```

They are not a fixed list. An IDE that keeps all durable state correctly under
`HOME` need not declare any IDE-specific slots.

The versioned component runtime template is the authoritative interface. It
declares whether the component expects the persistent home and its standard
home-relative XDG roots, plus any exceptional component-local slots. For
example, a tool that stores everything conventionally declares `home =
"required"`, `xdg = "home-relative"`, and no slots. DevCapsule must not add a
tool-named field or mount to shared runtime code for such a component.

Component-local names become namespaced logical names only when plans are
combined: PyCharm's local `config` declaration becomes `pycharm/config`.
Adapter configuration refers to component-local names; generic planning owns
namespacing, lifecycle-root selection, container-path conflict checks, and
parent-before-overlay mount ordering. A slot below the persistent home must
explicitly declare that it is a home overlay.

The reusable component template contains no checkout paths. Developer-owned
checkout resolution binds `home` and the selected logical slots to managed or
explicitly adopted host storage, then generates the checkout-specific runtime
plan. The in-container runtime receives only the persistent container home,
the generic resolved slot names and container paths, and adapter
configuration; it neither chooses host storage nor recognizes component
names.

## Slot Storage

Directory-backed slots are allocated beneath the matching XDG root:

```text
durable: $XDG_DATA_HOME/devcapsule/{checkout}/components/<component>/<slot>
state:   $XDG_STATE_HOME/devcapsule/{checkout}/components/<component>/<slot>
cache:   $XDG_CACHE_HOME/devcapsule/{checkout}/components/<component>/<slot>
```

`durable` holds information whose deletion loses meaningful developer work or
requires reconfiguration, including IDE preferences, extensions, agent state,
and database contents. `state` holds persistent operational history such as
logs. `cache` holds reconstructable indexes, downloaded packages, and build
caches. Cleaning cache may make later work slower but must not remove source,
credentials, conversations, settings, extensions, or database records.

Docker-volume slots use a deterministic DevCapsule-owned volume name derived
from project identity, checkout, component, and slot. They are appropriate for
components such as PostgreSQL and MySQL whose ownership and filesystem
requirements make arbitrary host bind mounts unreliable. `devcapsule state
path` reports the volume name rather than pretending it is a portable host
path.

SQLite may use a directory-backed durable slot when its database is local
runtime data. A database file that is intentionally part of the project's
source or test fixtures remains in the project mount instead. This
specification defines persistence, not service orchestration; running database
sidecars is separate V1 or later service-model work.

## Mount Planning And Conflicts

Resolution combines the persistent home with the state contracts from all
selected components. The lock records the component and state-contract
versions. Before launch, DevCapsule produces a deterministic mount plan and
validates it before invoking Docker.

Two slots may not claim the same container path. Ancestor and descendant paths
also conflict unless the descendant is explicitly declared as an overlay of
the persistent home. This exception permits a component to isolate a sensitive
or independently disposable directory beneath `HOME`. More-specific mounts
are applied after their parent, and this ordering is recorded in the plan.

DevCapsule rejects incompatible ownership, storage, scope, or concurrency
requirements instead of choosing silently. A slot marked non-concurrent cannot
be mounted read-write by two running capsules. A component may provide an
actionable alternative, such as creating another named profile.

The effective plan distinguishes:

```text
project source       developer-owned and irreplaceable
persistent home      durable, checkout-scoped, potentially credential-bearing
component durable    meaningful component data with declared sensitivity
component state      persistent operational history
component cache      rebuildable and safely cleanable
```

## Authorization

Automatically created, empty, checkout-scoped directories beneath DevCapsule's
XDG roots are safe defaults and need no separate host-path approval. DevCapsule
owns their layout and exposes only the directories selected by the resolved
components.

The following require a developer-owned decision for the observed checkout:

- selecting a named home or component-state profile;
- mounting an existing external directory;
- sharing credential-bearing state with another checkout;
- changing a slot from its declared default scope;
- enabling a component integration that exposes an independent host resource.

Committed repository content may recommend one of these choices and explain
what it enables, but cannot authorize it. Noninteractive use never prompts or
grants access. It uses a previously recorded developer decision or fails with
an actionable command.

## Inspection, Relocation, Profiles, And Cleanup

V1 provides these state-management operations:

```text
devcapsule state roots
devcapsule state list [--project PATH]
devcapsule state path SLOT [--project PATH]
devcapsule state inspect SLOT [--project PATH]
devcapsule state adopt SLOT --from DIRECTORY [--project PATH]
devcapsule state move SLOT --to DIRECTORY [--project PATH]
devcapsule state clean --cache [--project PATH]
devcapsule state remove SLOT [--project PATH]
devcapsule state profile list
devcapsule state profile use NAME [--project PATH]
```

`home` is the reserved logical name for the persistent home; component slots
use their namespaced names. `list` shows host storage, container destination,
lifecycle, sensitivity, scope, size when available, and whether the slot is in
use. `inspect` also shows ownership and the consequences of deletion.

Mutating commands show their plan and require confirmation unless an explicit
noninteractive acknowledgement is supplied. `adopt` records an existing
developer-owned directory as the storage for a slot after verifying its path,
ownership, expected layout, and checkout authorization; it does not copy or
delete the directory. `move` refuses while the state is mounted, copies and
verifies before changing local configuration, and leaves the source intact if
verification fails. `clean --cache` touches only slots declared as cache.
`remove` warns more strongly for durable or credential-bearing state and does
not remove project source. Docker volumes are removed through Docker rather
than filesystem deletion.

## `run` And `run-image`

`devcapsule run` uses the persistent home and all state contracts pinned by the
project lock.

`devcapsule run-image IMAGE` is the legacy, compatibility, dogfood, and
recovery escape hatch. It may run with or without a project declaration and
does not infer component contracts from the project lock. When it discovers
`.devcapsule/devcapsule.toml`, it uses applicable values from that declaration
unless the operator overrides them on the command line. Effective ordinary
values follow D-0001's configuration hierarchy: workstation defaults, the
project declaration, developer-owned checkout configuration, and finally
command-line values. Validation occurs after overlay resolution; a value that
is required for the requested operation but has no safe default must be
provided by configuration or the command line, otherwise the command fails
with an actionable error.

Command-line host-access options are explicit authorization for that run only.
A committed recommendation does not grant access, and a command-line value
cannot override restrictive workstation policy. If the local image carries
valid DevCapsule state-contract labels or metadata, `run-image` uses them.
Otherwise it mounts only the project and the default persistent home. `--force`
may skip missing or incompatible image metadata but does not invent component
mounts, mount the developer's real home, reuse a profile without authorization,
or weaken any host-access rule. `run-image` never reads the project lock,
resolves capabilities, silently selects or pulls another image, updates, or
builds.

## Migration From The Current Launchers

The current PyCharm-specific `global-settings`, `ide-config`, `plugins`, and
`project-state` flags and the Codium `state` and `project-state` flags are
pre-V1 implementation details. Their data maps into persistent home or
component-declared slots during implementation of this specification; their
names do not define the V1 model.

Historical agent-specific direct host-state mounts are replaced by the
checkout-scoped persistent home by default. A developer who wants to share
supported agent login state may adopt it through a named profile or an
explicitly approved external state mapping.

## Dogfood Migration From The Current PyCharm Command

The current DevCapsule dogfood environment is launched with:

The developer supplies `MONOREPO_ROOT`, `HOST_PROJECT_ROOT`, and
`PROJECT_STATE`; no private host directory layout is committed here.

```text
./dist/devcapsule.pex pycharm run \
  --global-settings ~/.config/docker-pycharm-codex/state/ \
  --plugins ~/.config/docker-pycharm-codex/plugins \
  --project "$HOST_PROJECT_ROOT" \
  --project-state "$PROJECT_STATE" \
  --image mycodespace.ai/pycharm:debug-v017 \
  --docker \
  --dev-sudo
```

The V1 implementation should migrate this environment without treating the
old PyCharm option names as the new model. The best state mapping is:

| Existing host data | V1 state slot | Lifecycle |
| --- | --- | --- |
| `~/.config/docker-pycharm-codex/state/home` | `home` | Durable and potentially credential-bearing |
| `~/.config/docker-pycharm-codex/state/config` | `pycharm/config` | Durable IDE configuration |
| `~/.config/docker-pycharm-codex/plugins` | `pycharm/plugins` | Durable downloaded plugins |
| Existing project-state `system/` | `pycharm/system` | Rebuildable cache |
| Existing project-state `log/` | `pycharm/log` | Operational state |
| Existing project-state `home/.cache/` | `pycharm/cache` | Rebuildable cache |

The PyCharm component contract, not DevCapsule core, defines those five
`pycharm/*` slots and their container destinations. Other IDEs remain free to
use only the persistent home or to publish different slots.

First, the existing checkout adopts the capability-first project model:

```text
cd "$HOST_PROJECT_ROOT"
devcapsule init \
  --need python \
  --need python-ide \
  --need docker-cli
```

After `devcapsule init` creates `.devcapsule/`, a one-time in-place state
adoption is conceptually:

```text
devcapsule state adopt home \
  --from ~/.config/docker-pycharm-codex/state/home
devcapsule state adopt pycharm/config \
  --from ~/.config/docker-pycharm-codex/state/config
devcapsule state adopt pycharm/plugins \
  --from ~/.config/docker-pycharm-codex/plugins
devcapsule state adopt pycharm/system \
  --from "$PROJECT_STATE/system"
devcapsule state adopt pycharm/log \
  --from "$PROJECT_STATE/log"
devcapsule state adopt pycharm/cache \
  --from "$PROJECT_STATE/home/.cache"
```

These commands record developer-owned local mappings and approvals. They do
not write host paths into `.devcapsule/devcapsule.toml` or the lock. Existing
supported Codex, Claude, or other agent state may instead be copied beneath the
adopted home in its normal tool location. DevCapsule must not mount the real
host home merely to avoid that one-time migration.

The updated codebase has produced
`mycodespace.ai/pycharm:debug-v018` as the next locally constructed diagnostic
image. Because it is not selected by a project lock, the recurring launch uses
the expert path:

```text
devcapsule run-image mycodespace.ai/pycharm:debug-v018 \
  --project "$HOST_PROJECT_ROOT" \
  --project-mount /workspace/301e4208ef81-ChatGPT_Codex \
  --docker-daemon host-socket \
  --development-sudo
```

Images produced by the current Python PyCharm builder carry the legacy trusted
label `devcapsule.configuration=pycharm`. During this pre-V1 migration,
`run-image` uses that label to select the catalog's PyCharm state contract and
therefore mount the adopted `pycharm/*` slots. An unlabeled image receives only
the project and persistent home unless the developer creates an explicit local
DevCapsule alias that associates it with the PyCharm component contract.

The new launcher deliberately adapts this legacy image to the V1 home contract.
Instead of preserving the old `/ide-global-settings/home` mount, it mounts the
adopted home at `/home/devcapsule` and supplies `HOME=/home/devcapsule` plus the
corresponding XDG environment values. The PyCharm config, plugins, system,
logs, and cache directories remain separate component mounts at the paths
expected by the image entrypoint. This launcher-side transition lets the next
dogfood version verify the new model without requiring an intermediate image
rebuild solely to rename the home directory.

`--development-sudo` is a descriptive placeholder until the generic privilege
grammar is settled; it must not be implemented as an ambient image default.
The Docker-daemon and sudo decisions may instead be persisted in the
developer-owned checkout configuration, reducing the normal dogfood launch to:

```text
devcapsule run-image mycodespace.ai/pycharm:debug-v018 \
  --project "$HOST_PROJECT_ROOT" \
  --project-mount /workspace/301e4208ef81-ChatGPT_Codex
```

The target outcome is that state locations and recurring host permissions are
configured once and inspected when needed, rather than reconstructed in every
shell invocation.

The explicit project mount above is part of the in-place migration. Existing
PyCharm state records interpreters and workspace locations using the absolute
path `/workspace/301e4208ef81-ChatGPT_Codex`; changing that destination makes
valid saved paths such as the project's `.venv/bin/python` appear missing even
though PyCharm is still running inside Docker. New checkouts may use the normal
generated project mount, but adopted IDE state must retain its established
container path or be migrated deliberately.

### Resolved PyCharm License-Persistence Regression

The initial PyCharm 2026.1 dogfood launches appeared not to retain all
JetBrains license and agreement state even though the expected files existed
beneath the persistent home. The cause was an incomplete home-directory
migration rather than a missing state slot or unstable machine identity.

The launcher mounted and exported the new persistent home at
`/home/devcapsule`, but its generated `/etc/passwd` entry still declared the
container user's home as `/ide-global-settings/home`. Java preferences and IDE
filesystem probes consequently resolved the obsolete, unmounted account home.
The logs reported that the Java preferences directory could not be created and
showed a `NoSuchFileException` for `/ide-global-settings/home`.

Both `pycharm run` and `run-image` use the same launcher, so correcting the
generated account entry to `/home/devcapsule` fixed both paths. Restart
validation confirmed that the dogfood environment and JetBrains activation
then remained available across launches. The regression has an automated test
which verifies that the generated passwd home matches the mounted persistent
home.

This result reinforces the state contract: the container account database,
`HOME`, XDG paths, and the persistent-home mount must identify the same home.
DevCapsule must not mount the host's machine identity or broad host application
data as a licensing workaround. Persistence of DevCapsule-managed state does
not guarantee that every third-party server-side session remains valid, but no
additional JetBrains-specific mount is required for the validated dogfood
case.

The exact generic privilege acknowledgement syntax, implementation-constraint
syntax, and longer Dev Container rationale are deliberately deferred until
after this dogfood migration. The implementation should first validate the
persistent-home and component-slot model with the real PyCharm workflow. Those
deferred spellings do not change the state layout or weaken its authorization
rules.
