# Try a component upgrade and recover

Available in the v0.2.14 development client. Run these commands from your project
checkout in a normal host terminal. Update discovery covers PyCharm, VSCodium,
Codex, Claude Code, Antigravity CLI and PostgreSQL client. Codex currently supports
preparation/selection through this interface; other components explain their
delivery limits. Base and IDE upgrade delivery and DevCapsule self-update remain
separate work.

For the meaning of freshness, support and unknown status, the six vendor sources,
and current operational limits, read [How DevCapsule checks component freshness](component-freshness.md).

## When update checks fail

`devcapsule project versions check` reads vendor release metadata. Those interfaces
can change independently of your installed DevCapsule version. When a check is
inconclusive, DevCapsule also consults its maintained compatibility feed and
[component status page](https://github.com/ccozianu/devcapsule/tree/component-status).
It can identify a released CLI fix, or point to a known issue and workarounds.
This restores guidance without changing your selected software.

A failed check does not mean your component is healthy, unhealthy or current.
The last successful result, when available, is labelled historical. If our
status service is unavailable, cached guidance retains its original timestamp;
expired metadata cannot recommend an upgrade. Without a matching current
diagnosis, the CLI says status remains unknown. Ordinary offline launch still
works. `--no-update-check` and noninteractive launch make no automatic status
requests. The feed receives no project configuration or installed-version query.

Updating DevCapsule to repair a check does not itself update the component.
PostgreSQL is supplied by the pinned base: major-version support dates can be
reported, but the current major-only lock cannot tell whether the installed minor
is behind upstream or carries distribution backports. Clients predating this
fallback need a normal CLI upgrade before they can consult it.

A **version set** contains the exact platform, base, components and recipe used
to build an environment. The project recommends one in its committed platform
lock. Your local selection belongs to your checkout configuration and stays
complete even if the project recommendation changes.

## Inspect from inside the capsule

Inside a capsule launched with the updated client, these commands work without
registering another checkout in the container's home:

```sh
devcapsule project versions show
devcapsule project config list
```

`versions show` distinguishes the **running session's version set**, captured
when it launched, from the **current selection for the next launch**. Changing
the selection outside the capsule does not change its running software.
`config list` shows the launcher's recorded configuration; host paths and
permissions are not reinterpreted as container paths or current-session grants.

The launcher mounts the directory containing the selected checkout's local
configuration read-only. The existing layout can place sibling checkout records
in that directory; those records are readable too, but the CLI selects only the
checkout identified by the launcher. The mount is not your entire user
configuration tree, and directory/credential references in the records do not
mount their targets. A separate read-only launch snapshot preserves the session's
software identity. Directory mounting makes atomic host-side replacements visible.

Commands that change configuration, select software, or need launcher-owned
upgrade history/cache give an outside-the-capsule command with the correct
launcher checkout path. They do not create competing configuration inside the
runtime. A different project can still be managed by a nested launcher.

Existing running capsules lack these mounts. **Relaunch from outside the capsule
with the updated launcher** to enable introspection; replacing the executable
inside an existing capsule cannot add its missing mounts. If host activation is
unfinished or a record is unavailable, `versions show` still reports the captured
running set and explains why the next-launch selection cannot be read. Runtime
inspection never repairs the launcher's records.

## Decide about a critical upgrade when launching

Run `devcapsule project run` as usual. In an interactive terminal, the launcher
checks component channels at most once per day for the selected version set.
An explicit security or end-of-support notice brings the decision into launch:

```text
Security notice for tool 1.0.0: <vendor explanation>
Source: <distribution channel>
Last checked: <date and time>; cached metadata may be stale.
Choose upgrade (review first), later (seven days), keep (silence this notice), or stop launch [later]:
```

This example illustrates a channel-reported security notice, not a current
advisory about Codex. Codex's npm channel currently supplies vendor deprecation
notices; DevCapsule shows their wording under end-of-support/vendor deprecation.
It does not query an independent vulnerability database or infer vulnerabilities
from age, registry removal or deprecation wording.

Choose `upgrade` to see the exact changes, downloads, validation gaps and recovery
options. Confirm to prepare the candidate and use it **in this launch**. Missing
DevCapsule validation is disclosed in that confirmation. Any new vendor
acquisition consent is asked separately; neither question grants host access.
An available candidate is not automatically proof of a security fix.

`later` (also Enter) keeps your current version and asks again after seven days.
`keep` silences this notice for this version and candidate; a new notice, revised
explanation or new candidate can prompt again. `stop` or end-of-input cancels
launch. Declining the preview defers the notice for seven days. If preparation
fails, the launcher explains the failure and asks before continuing with the
selected set. With no available replacement, it explains that limit and offers
later, keep or stop. Recovery still requires a previously successful set.

Network failure does not prevent ordinary launch. A failed refresh retains a
previously reported notice with its original check time. To skip refresh for a
launch, use `devcapsule project run --no-update-check`; cached notices can still
prompt. Noninteractive launches do not refresh, read answers or select upgrades:
they report any unsilenced cached critical notice and use the selected set.
Ordinary new-version notices remain quiet, remembered reminders.

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

`check` refreshes immediately; interactive launch also performs the daily check
described above. An ordinary checked candidate is mentioned at most once per
seven days. `defer` starts a fresh seven-day quiet period; `dismiss` silences the
checked candidates and critical notices. A different candidate or critical
notice can be surfaced later. A critical decision suppresses the duplicate
ordinary reminder. Previously dismissing an ordinary update does not silence a
new security/support notice. Cached metadata is labelled with its limits; a
selected candidate is no longer mentioned as an update. These choices do not
suppress notices owned by Codex or another vendor.

For commands outside the checkout, put `--path` before `versions`, for example
`devcapsule project --path /path/to/project versions show`.
