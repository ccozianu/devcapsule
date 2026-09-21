# Component distribution and local version-set implementation

Requirements: R-UPGRADE-001, R-COMPAT-001, R-PRODUCT-002.
Decision: [D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md).

## Add a channel

`ComponentDefinition.distribution_channel()` returns a trusted installed adapter
implementing `DistributionChannel` in `components/channels.py`. No metadata
response is executed as Python, shell or npm installer code.

- `check(current, platform)` returns the source, current version/status and
  candidates. Status is availability/support, never DevCapsule validation.
  Raise `CliError` with the unavailable resource and a useful retry action.
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

Additional adapters requiring vendor consent must retain the ordinary acquisition
contract. Selection does not infer acceptance of a changed acquisition question.
The first implemented update channel is freely redistributable Codex.
`select`, `rollback`, and `follow-project --apply` accept explicit candidate
`--authorize NAME VALUE` acquisition answers. They apply the ordinary typed
contract to the target metadata and refuse host-permission nodes. Missing/stale
or denied acquisition answers cannot trigger preparation without explicit consent.

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

## Validation

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
