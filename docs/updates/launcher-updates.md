---
description: How the launcher checks for newer DevCapsule releases, how to install one, and what stays untouched when you upgrade.
weight: 2
updated: 2026-10-30
---
# Launcher updates

Once a day, `devcapsule project run` checks whether a newer DevCapsule release
exists and notifies you interactively. Pass `--no-update-check` to skip the
network check for one launch; any cached critical notice still stops and asks
before continuing. Installing a newer release uses the same steps as
[Install DevCapsule](../getting-started/install.md) with the new release's
download URL. It replaces the single-file executable and nothing else.

Upgrading the launcher preserves every project's lock, every checkout's
recorded choices, and your [configuration home](../configuration/home.md)
(`settings.toml` defaults and accepted channels). It grants no new host
access. Existing per-checkout approvals and home channel acceptances stay
valid while they still match the selected software.

If a project updated its manifest or lock in the meantime, or a newly selected
component requires a channel acceptance or checkout approval, the next launch
stops and asks, as
[Project versus personal](../configuration/project-versus-personal.md#when-the-project-changes)
describes. When a newer launcher writes `settings.toml`, it also records its
release in `minimum-devcapsule` so an older launcher refuses to modify that
home rather than misreading newer settings.
