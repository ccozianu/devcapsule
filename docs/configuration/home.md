---
description: Select one DevCapsule configuration home for settings, checkout records, persistent data, state and cache.
weight: 3
updated: 2026-10-28
---
# The configuration home

A DevCapsule home holds the settings shared by launches from that home.
You can use separate homes with the same executable. The executable's location
does not select the home.

By default, the configuration directory is `$XDG_CONFIG_HOME/devcapsule`,
or `$HOME/.config/devcapsule` when that XDG variable is empty or unset.
Data, state and cache keep their separate XDG directories:

| Purpose | XDG directory | Default |
|---|---|---|
| Configuration | `$XDG_CONFIG_HOME/devcapsule` | `$HOME/.config/devcapsule` |
| Persistent data | `$XDG_DATA_HOME/devcapsule` | `$HOME/.local/share/devcapsule` |
| State | `$XDG_STATE_HOME/devcapsule` | `$HOME/.local/state/devcapsule` |
| Cache | `$XDG_CACHE_HOME/devcapsule` | `$HOME/.cache/devcapsule` |

Set `DEVCAPSULE_CONFIG_HOME` to keep these together:

```sh
export DEVCAPSULE_CONFIG_HOME="$HOME/devcapsule-homes/learning"
devcapsule home show
devcapsule home trust accept devcapsule-base --yes
devcapsule home trust accept claude-code --yes
devcapsule home default memory 8GiB
devcapsule home default cpus 4
```

The named directory holds configuration. Its `data/`, `state/` and `cache/`
subdirectories hold the other three kinds of storage, including managed
checkout data. Explicit storage bindings still name the directories you chose.
An empty variable keeps the XDG defaults. A relative path starts from the
current directory. A leading `~` expands to your user home.

These commands need no project. `home show` prints the selected path and its
source. It also prints the format, minimum reader, defaults and accepted
channels. `home trust list` lists the accepted channels and their dates.
Neither command creates an empty home. The first write creates the home
with mode `0700` and its settings file with mode `0600`.

## One settings document

`settings.toml` holds resource defaults under `[defaults]` and accepted
channels under `[trust.channels]`. Each channel records its vendor, product,
origins, integrity method, acceptance date and terms URL when applicable.
Checkout records live separately under `projects/` in the same configuration
directory. Saved Docker arguments and console requests have their own stores.

Two header fields describe the settings file:

- `devcapsule-settings-schema-version` is the format number. This launcher reads format `1`.
- `minimum-devcapsule` is the lowest launcher release that can read the document.

A new file uses the launcher's release version without its candidate suffix.
An older launcher refuses the home before changing it. Its message names
the home, both versions and the release download location.
An unchanged write preserves the existing file and its modification time.

Earlier candidates used two separate settings records. This launcher ignores
those files and leaves them in place. Set defaults and accept channels again.
Released clients before this feature did not create those records.

## Inside a capsule

The capsule receives the settings file read-only. `home show` and
`home trust list` read that view. Mutating commands name the command to run
outside the capsule. Set `DEVCAPSULE_CONFIG_HOME` to a different writable
directory when you need a separate home for nested use.

[Vendor software and trust](software-approvals.md) explains channel acceptance.
[Resource limits](resource-limits.md) explains how defaults interact with project
recommendations and checkout choices.
