# How DevCapsule checks component freshness

This describes the v0.2.14 development implementation. It checks vendor metadata
for six curated components and offers maintained guidance when those checks
fail. The operational improvements described at the end are intended for V1;
they are not guarantees of the current service.

## What an update check establishes

DevCapsule keeps these facts separate:

| Fact | What it tells you |
|---|---|
| Available version | A vendor source advertises a release for your platform. |
| Support or withdrawal | The source explicitly reports support, deprecation or absence from its registry. |
| Security notice | A channel supplies an explicit notice; version age alone is insufficient. |
| DevCapsule validation | We have evidence about a particular version set. A vendor release does not supply that evidence. |
| Local successful use | Your ordinary session exited successfully with that exact set; this does not test every feature. |
| Observation age | When the check actually ran, and when it last succeeded. Old evidence remains old after a network failure. |

A newer version does not by itself make your version unsupported or unsafe.
Conversely, no reported update does not certify security. There is currently no
independent vulnerability feed. Read the explanation alongside a status label:
`available` is not a security endorsement, and `unknown` can mean that support
was not assessed even when a newer release was discovered.

## Where the signals come from

These are interfaces our adapters consume, not a universal vendor commitment to
keep them stable. DevCapsule does not operate a registry in which vendors must
publish component lifecycle information.

| Component | Source consumed by the adapter | Meaning and limits |
|---|---|---|
| PyCharm | [JetBrains release JSON](https://data.services.jetbrains.com/products/releases?code=PY&latest=true&type=release) | Latest release and platform download/checksum links; no general support or security verdict. |
| VSCodium | [GitHub latest-release JSON](https://api.github.com/repos/VSCodium/vscodium/releases/latest) | Stable, non-draft release with the expected platform archive. |
| Codex | [npm package metadata](https://registry.npmjs.org/@openai%2fcodex) | `latest`, exact versions and vendor deprecation. A changed `latest` tag is a candidate, not necessarily a numerically newer version. Absence means unlisted, not that installed software cannot run. |
| Claude Code | [Vendor latest-version pointer](https://downloads.claude.ai/claude-code-releases/latest) and that version's `manifest.json` | The `latest` channel and a platform artifact; not the separate stable channel. |
| Antigravity CLI | [Vendor platform updater manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json) | The platform manifest's version and download metadata. |
| PostgreSQL client | [PostgreSQL version JSON](https://www.postgresql.org/versions.json) | Latest minor and upstream support/end-of-life for the selected major. |

The discovery-only adapters compare dotted numeric versions where appropriate.
They fetch metadata, not installers. PostgreSQL deserves particular care: the
current base lock records only the major version. It cannot establish the
installed minor or distribution security backports, so it does not manufacture
a minor-upgrade candidate. Updating that client requires base delivery work.

Only Codex currently supports preparation and selection through the component
upgrade interface. Other components report discovery and delivery limits; there
is no command that installs all discovered upgrades.

## What to do as a user

From your project checkout on the host:

```sh
devcapsule project versions show
devcapsule project versions check
```

`show` is offline. It also works inside a capsule relaunched with the updated
launcher, where it distinguishes running software from the next-launch selection.
`check` needs the launcher context and contacts vendor sources. Interactive
launch also attempts a daily check; noninteractive launch does not. Skipping
the automatic check with `--no-update-check` leaves cached notices available.

For a Codex candidate, follow the [preview, selection and recovery guide](component-upgrades.md#preview-then-choose).
An explicit critical notice brings a decision into interactive launch; it does
not silently replace your tools. Discovery-only components cannot be installed
by accepting a Codex-style upgrade prompt.

If a check is inconclusive, inspect its explanation and last-successful time.
DevCapsule consults the compatibility feed automatically and links to the
[maintained component status page](https://github.com/ccozianu/devcapsule/tree/component-status).
A matching diagnosis can recommend a
released CLI fix or link to a known issue and workarounds. Updating DevCapsule
to repair discovery does not itself upgrade the affected component.

Without current matching guidance, status stays unknown. Retry after a transient
network problem; if it persists, consult the linked issue or report the component,
CLI version, platform, check time and sanitized error. A timeout alone does not
prove that a vendor changed its interface. Existing software remains selected
and ordinary offline launch remains possible.

## How the maintained fallback works

Each shipped discovery adapter has an identity. On a vendor exception, HTTP error
or unexpected metadata shape, the client fetches one fixed versioned feed and
matches diagnoses to its adapter, CLI version and platform locally. No project
configuration or installed-version query is sent. Clients predating this feature
need a normal CLI upgrade before they can use it.

The backend action probes the current adapters daily and publishes a status page
and feed together on the `component-status` branch. Observations record what
happened; diagnoses are reviewed explanations authored by maintainers. A failed
probe neither invents a diagnosis nor erases the last success. A successful probe
of today's adapter does not certify every older installed adapter.

Feed expiry and diagnosis review expiry are independent. Cached guidance keeps
its original timestamps; downloading or republishing it does not renew a
diagnosis. Stale or malformed metadata cannot authorize an upgrade recommendation.
The feed never installs software, replaces adapter URLs or changes selections.

Contributors should preserve these contracts when changing parsers and bump the
adapter identity when its endpoint or interpretation changes. Keep older affected
identities in maintained diagnoses and preserve the v1 endpoint for older clients.
See the [service contract and operator runbook](../../component-status/README.md)
for schema, review and publication details.

## Operating today and the V1 objective

The initial publication happens after owner merge to main and a successful
**Component update status** action. A workflow file on main enables the configured
triggers; no separate action installation is required. Repository permissions
must still allow publication. The owner verifies the generated public resources.

| Concern | Current implementation | Intended V1 outcome |
|---|---|---|
| Freshness | Daily publication; feed expires after 72 hours. | Public, usable status with an observation for each supported component no older than 48 hours. |
| Vendor check failure | Published as inconclusive with history; does not fail the action. | Bounded retries, maintainer notification for persistent failure, and maintained user guidance. |
| Publication failure | Fails the action; previous feed remains until expiry. | An actionable notification with an owner and recovery procedure. |
| Job never runs, or public resource breaks | Readers can notice old timestamps; no independent monitor. | A monitor outside the publishing system detects missing, stale or unusable resources before the deadline. |
| Alert delivery | No verified owner email or other alert route configured by this change. | Independently verified detection and notification paths, exercised by failure drills. |

The 48-hour objective concerns fresh observations, including truthful failure
observations. A fresh report of a broken vendor interface satisfies reporting
freshness but still requires incident response. Merely advancing the feed's
generation time while retaining old observations is insufficient.

These are service-level objectives we intend to implement and measure, not a
contractual SLA or a claim of current operational coverage. GitHub job failures
alone do not establish that the repository owner receives email, and a job that
never starts cannot report its own failure. The goal is that one failure cannot
both break the service and silently suppress detection. Monitor provider, alert
destinations, escalation thresholds and the supported older-client window remain
decisions for the V1 work, recorded in
[R-UPGRADE-002](../../engineering-docs/requirements/product/r-upgrade-002-status-operational-reliability.md).
