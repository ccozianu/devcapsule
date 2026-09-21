# Try a component upgrade and recover

Available in the v0.2.14 development client. Run these commands from your project
checkout in a normal host terminal. Codex is the first component with an update
channel; base and IDE upgrades and DevCapsule self-update are separate work.

A **version set** contains the exact platform, base, components and recipe used
to build an environment. The project recommends one in its committed platform
lock. Your local selection belongs to your checkout configuration and stays
complete even if the project recommendation changes.

## Inspect and check

```sh
devcapsule project versions show
devcapsule project versions check
```

`show` is offline: it identifies your selection's origin, component versions,
DevCapsule validation evidence and locally recorded successful use. `check`
contacts the components' distribution channels. Availability, vendor withdrawal
or lack of support, DevCapsule validation and your own successful use are
separate facts. A failed check means metadata is unavailable; it does not mean
your installed version is current or broken. Components without channels explain
why their updates cannot be checked.

## Preview, then choose

For Codex, ask for an exact version or the registry's `latest` label:

```sh
devcapsule project versions preview codex latest
```

Preview resolves the label to an exact version and immutable package checksums,
without downloading executables or changing your selection. It shows what
changes, required artifacts, validation gaps and the recovery option, and prints
a full preview identity. Use that identity in the command it prints:

```sh
devcapsule project versions select PREVIEW_ID --unvalidated
```

`--unvalidated` is the explicit choice to try a set without complete DevCapsule
validation. It does not bypass platform, dependency, consent or integrity checks.
The selected component changes; other component versions and the base remain
fixed. An unsatisfied declared dependency is named for separate explicit
selection rather than silently upgrading another tool.

Selection downloads and verifies packages and builds the environment first.
Only successful preparation changes the next ordinary launch. Existing sessions
continue with their original versions. Failed preparation leaves your previous
choice active; resolve the reported download/build problem and retry the same
preview. If your selected software changed since preview, make a new preview.

```sh
devcapsule project run
```

When an ordinary session exits with code zero, DevCapsule records the exact set
that launched as locally known-good. This is evidence of successful use, not a
claim that every capability or account integration was tested. Closing a failed
session or merely preparing a set does not certify it.

## Roll back

```sh
devcapsule project versions history
devcapsule project versions rollback
devcapsule project run
```

Rollback selects the most recently successful **other** set. You can also supply
a full identity from `history` to choose a specific set or repeat a recovery.
If none exists, DevCapsule says so; configuration snapshots from earlier clients
do not contain enough information to invent an operational predecessor.

Exact downloaded artifacts are retained under the XDG state directory, separate
from disposable cache. Canonical images keep their distinct tags, and these
commands never prune them. If you manually remove both the retained artifacts
and the relevant image, recovery reports the missing resources and retains your
current choice. `rollback --reacquire` deliberately attempts the original exact
downloads; withdrawn vendor downloads may no longer be available. A missing base
image also requires that explicit reacquisition choice. A changed DevCapsule
launcher may rebuild the environment with identical outside/inside runtime bytes.

Rollback preserves current host permissions, state bindings, login files and
project work. It does not restore old Docker access or other revoked permissions.
It also **cannot undo vendor state/schema migrations** made by a newer agent.
Version sets retain software, not automatic backups of personal state.

## Follow the project again

```sh
devcapsule project versions follow-project
devcapsule project versions follow-project --apply
```

The first command shows the diff against today's recommendation. The second
prepares it and removes your local selection. Changed vendor acquisition questions still need explicit consent. The failure
names the target terms and the `--authorize NAME true` option to append to this
command. The same option is supported by `select` and `rollback` for target
acquisitions. It never grants Docker or other host access; denial leaves the
current choice intact. Upstream changes
are never merged silently into a local set; inspect the diff before applying.

## Optionally propose your successful choice upstream

After successfully running the local set:

```sh
devcapsule project versions propose component-upgrade.patch
git apply --check component-upgrade.patch
```

Review the patch, including any differences introduced by upstream changes.
An explicitly selected local base is named as a qualification; that run did
not prove the proposed project base. It qualifies the evidence as a local
zero-exit launch and carries unvalidated
combinations in the lock. Apply and contribute it through your project's normal
review process if you choose. DevCapsule does not edit the project lock, commit,
open a PR, publish or merge on your behalf. The patch must be written to a new
file; an existing file is never overwritten. A fixture's local download URLs
must be replaced with portable artifacts before any real contribution.

## Keep reminders quiet

```sh
devcapsule project versions defer
devcapsule project versions dismiss
```

Checks are explicit. Ordinary launches use only the last saved check and never
contact update services. A checked candidate is mentioned at most once per seven
days. `defer` starts a fresh seven-day quiet period; `dismiss` silences those
candidate versions permanently. A different candidate discovered by a later
check can be mentioned. Reminders describe their metadata as previously checked
and potentially stale. A selected candidate is no longer mentioned as an update.
These choices do not suppress notices owned by Codex or another vendor.

For commands outside the checkout, put `--path` before `versions`, for example
`devcapsule project --path /path/to/project versions show`.
