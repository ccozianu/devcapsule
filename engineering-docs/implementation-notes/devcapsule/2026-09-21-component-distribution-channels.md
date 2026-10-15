# Component distribution and local version-set implementation

Requirements: R-UPGRADE-001, R-COMPAT-001, R-PRODUCT-002.
Decision: [D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md).

## Add a channel

Read-only availability can precede installation support: definitions may override
`discovery_channel()` with a `DiscoveryChannel` that implements only `check`.
The default returns `distribution_channel()`. PyCharm, VSCodium, Claude Code,
Antigravity CLI and PostgreSQL now use read-only vendor discovery; Codex retains
its complete channel. Discovery-only candidates are visible in explicit checks
but never offered as executable upgrade choices or preview reminders.

`discovery_adapter_id()` identifies the shipped metadata contract independently
of the CLI version. Override/bump it when changing parsing, endpoint or semantics
so maintained diagnoses can address older adapters precisely. Generic check
failures consult the fixed DevCapsule compatibility feed once per check and keep
last-successful evidence. Backend probes use the same component declarations.
The [service contract](../../../component-status/README.md) defines this maintained
v1 API, publication and operator responsibilities.

`ComponentDefinition.distribution_channel()` returns a trusted installed adapter
implementing `DistributionChannel` in `components/channels.py`. No metadata
response is executed as Python, shell or npm installer code.

- `check(current, platform)` returns the source, current version/status and
  candidates. Status is availability/support, never DevCapsule validation.
  Raise `CliError` with the unavailable resource and a useful retry action.
- `ChannelVersion.notices` optionally carries typed `ChannelNotice` values:
  stable advisory identity, `security` or `end-of-support`, and the vendor's
  explanation. The report's source and check time are retained for launch.
  Adapters own applicability to the exact current version. Change the notice
  identity for a new issue; do not classify from version age or free-form
  keyword guesses. Candidates carrying notices are not offered as remedies.
- `select(version_or_label, platform)` returns a `ChannelSelection`: exact
  component lock metadata, applicable platforms, optional exact companion
  requirements, supported base families and distribution status. Preserve the
  component's installation contract. It must resolve labels now, never at launch.
- Artifact tables carry `url` and `sha256`, or `url` and a SHA-512 npm SRI
  `integrity`. Preparation feeds both through the existing acquisition engine;
  SRI verification additionally records SHA-256 before activation. Preview may
  read metadata but must not download or execute payloads.
- Companion requirements are constraints, not solver instructions. A mismatch
  refuses with the required version named. Base-family mismatches refuse as
  outside the component-upgrade slice. Missing accumulated coupling validation
  is disclosed and may be accepted explicitly under D-0007.
- A definition with no channel overrides `channel_omission_reason()` with an
  intelligible reason. The curated-catalog test fails if both are absent. This
  friction is for contributors: old project configurations remain readable.

`NpmChannel` implements the meta-package plus exact platform-alias pattern used
by Codex. It checks package identity, exact platform dependency, Node requirement,
OS/CPU, registry HTTPS URLs and SHA-512 integrity. A changed dependency/engine
contract requires a reviewed adapter update. It installs no package while
checking metadata. The ordinary materializer retains offline npm installation
with scripts disabled. Distribution details live in the adapter/component;
`version_sets.py` has no Codex-specific branch.
The npm adapter maps its existing vendor-deprecation support status to a typed
notice and preserves the vendor wording. Missing versions and unsupported
platforms do not invent support/security notices. It has no independent security
advisory feed; no security coverage is implied by a successful registry check.

Additional adapters requiring vendor consent must retain the ordinary acquisition
contract. Selection does not infer acceptance of a changed acquisition question.
The first implemented update channel is freely redistributable Codex.
`select`, `rollback`, and `follow-project --apply` accept explicit candidate
`--authorize NAME VALUE` acquisition answers. They apply the ordinary typed
contract to the target metadata and refuse host-permission nodes. Missing/stale
or denied acquisition answers cannot trigger preparation without explicit consent.
The launch flow supplies an optional acquisition-authorization callback to the
same selection engine, using `Elicitor`. The callback receives only pending
acquisition reviews and cannot grant host permissions. Decline/EOF never downloads
the candidate. Successfully elicited consent is stored only with activation.

## Critical notices during launch

`commands/_upgrade_prompt.py` handles presentation and uses the shared `Elicitor`.
`version_sets.launch_notices` performs a best-effort check once per day per
effective version set on interactive launch. `--no-update-check` disables that
refresh; noninteractive launches never refresh. Checks retain previously known
notices on channel failure, bound to component/current version/platform with the
original timestamp. A successful report may clear a notice. Old check files with
no notices remain valid. No network success is required to launch.

Explicit later/keep decisions live beside existing reminders, keyed by the notice
and remedy rather than the check time. They do not suppress newly reported issues.
Noninteractive warnings do not consume a future interactive decision. Ordinary
reminders exclude candidates already covered by an applicable critical notice.
No replacement means no upgrade choice, but the user can defer, keep or stop.

After preview, a separate affirmative answer accepts the exact set and disclosed
validation gaps. Preparation reuses `select`; failures ask before continuing.
`project run` reloads admission after this flow, then captures the chosen inputs
before launch so zero-exit history certifies the set actually used. Multiple
notices for a version already upgraded are skipped. No general unattended update
policy or independent vulnerability service is introduced.

## Selection, activation and history

The optional `[version-set]` extension in format-1 checkout input contains its
own `format = 1`, complete lock TOML text, and the digest of the project
recommendation when local selection began. It is an input owned by the developer,
not a floating override and not a generated resolution. `storage.lock_for` is the
shared effective-selection boundary; `recommendation_lock_for` explicitly reads
the project's recommendation. Existing checkout documents need no migration.
Unknown extension versions are refused intact.

Selection prepares a `ResolvedProject` from the chosen lock and **current**
checkout answers, using the existing `Configuration` value API and
`realize_environment`. Explicit software selection renews formation/base trust;
it never renews a host grant or a changed vendor license answer. Local base
identities also participate in version-set identity and known-good records;
rollback selects the recorded immutable ID even if its old tag moved. Matrix
evidence for a project base is not attributed to a local base override, and
proposal export explicitly qualifies that difference.

After preparation, `activate_configuration` journals the before/after checkout
and resolution, writes resolution, then atomically replaces checkout as the
commit point. Readers recover an interrupted transaction according to which
checkout bytes are present. An unexpected later edit causes refusal; recovery
cannot overwrite it with an old authorization. This is bounded recovery under
the existing serialized-access precondition, not a general concurrency or
power-loss durability guarantee. Journal and configuration files are private.

`project run` captures checkout/resolution bytes and the loaded effective lock
before launch. Exit zero records these inputs even when a newer selection was
prepared while the session ran. Configuration-only D-0008 history remains
readable; new operational known-good records live under
`$XDG_STATE_HOME/devcapsule/version-sets/<checkout-path-hash>/known-good/`.
They contain software metadata, the chosen base, and last successful use, never
personal-state contents. Failures and preparation never enter this sequence.

Exact downloads used by a successful or prepared set are copied from the
verified acquisition cache into the same state tree. Distinct canonical image
tags retain the executable environment; no cleanup is introduced. Rollback
restores retained artifact bytes to cache and uses the ordinary materializer's
identity checks. Without `--reacquire`, missing base/resources stop recovery
before activation; with it, exact original URLs/digests may be attempted.
A vendor removing a download does not defeat retained local recovery. Manual
Docker/state deletion and vendor state migrations remain explicit limits.

The embedded resolution matrix exposes evidence queries without replacing or
removing existing verification records. Artifact/installation identity, base
family and declared coupling evidence are checked independently; provisional
entries retain their original qualified evidence text. Local zero-exit history
is never promoted into matrix validation automatically.

## Runtime inspection

`runtime_configuration.py` captures a launch descriptor from the admitted
`ResolvedProject`, and reads runtime configuration through a separate adapter.
Ordinary `project run` passes that capture to the launcher, which mounts its
private JSON file at `/etc/devcapsule/launch-context.json` and the record's parent
directory at `/etc/devcapsule/checkout`, both read-only. Directory mounting follows
the launcher's atomic file replacements; a file bind would pin the old inode.
The existing shared layout can expose sibling checkout records in that directory.
Host paths in configuration are disclosed metadata; their referenced resources
are not mounted by this feature.

The descriptor identifies creator/slug, the exact record filename, host/runtime
checkout paths, and the running lock/origin/base/version-set identity. The runtime
reader checks those identities without resolving the host path in the container,
and without invoking `load_checkout`'s recovery writes. A present activation
journal makes next-launch state temporarily unavailable; the running snapshot
remains inspectable. `config list` presents records without attempting host
filesystem readiness checks. Host loader admission/recovery stays unchanged.

Project command dispatch refuses unsupported runtime operations before effects
and supplies a shell-quoted launcher command. Explicit recursive-dogfood commands
retain their contract, and a separate project remains eligible for nested launcher
use. Capsules predating the mount receive relaunch guidance. Global registry
listing in older/nested launcher capsules retains its existing behavior.

## Validation commands

Run `tests/test_distribution_channels.py` and `tests/test_version_sets.py`, then
`nox -s build`. The latter includes old released-input fixtures and packaging.
The ordinary CLI cases use real configuration, acquisition and materialization;
only Docker image operations and the launched process are controlled.

The opt-in `scripts/smoke-component-upgrades.py` runs a bounded real Codex
upgrade and rollback with an isolated checkout/XDG tree and tiny fixture IDE.
Use a new root on a host-backed filesystem if Docker runs outside the capsule:

```sh
.venv/bin/python scripts/smoke-component-upgrades.py \
  --pex dist/devcapsule-local.pex \
  --root dist/component-upgrades-review \
  --candidate EXACT_CODEX_VERSION
```

It leaves exact artifacts and images for inspection, does not use real accounts,
and redacts transient display tokens from its command log. Its executable probe
is evidence of delivery and recovery, not interactive IDE/account acceptance.
The workstream's validation record states the observed result and exact artifact.
