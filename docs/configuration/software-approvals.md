---
description: Vendor software is downloaded under the vendor's terms; you accept a vendor's channel once for your computer, every version and every project, and DevCapsule's base images the same way.
weight: 7
updated: 2026-10-25
---
# Vendor software and trust

Some of the software a capsule contains is downloaded from its vendor under
that vendor's terms. DevCapsule does not redistribute those downloads.
Coding agents are capabilities; their components declare their own channels
and consent requirements. DevCapsule's own base images come from its published
repository, content-addressed by the digest the lock pins.
When a launch lacks matching consent, DevCapsule can ask you to trust a
**channel**. The statement names its vendor, origins, integrity method and
terms. Acceptance belongs to your user account on this workstation.
It covers later versions of that product with the same vendor and terms,
provided their origins are within the accepted set.

## At launch

For a checkout without base consent, the published base asks:

```text
Trust DevCapsule to supply the base images from docker.io/mycodespaceai/devcapsule-base, https://devcapsule.mycodespace.ai, verified by the SHA-256 digest the launcher pins. This covers every version and every project for this OS user account on this computer. Anyone sharing this account uses this acceptance. Changed terms or a different channel require another decision.
  A launcher you downloaded already carries these digests; this makes the trust explicit. You trust the ccozianu/devcapsule GitHub account and the mycodespaceai Docker Hub account.
Accept for this user account on this computer? [y/N]:
```

**y** stages acceptance with the other answers. The launcher saves them
when the required review and plan validation finish. **N** stops this review
with status 3 and prints the command to accept later.
Without a terminal, missing consent produces status 3 instead of a prompt.
Existing matching per-checkout consents still work; they do not automatically
become workstation trust. In particular, `init --ide` can ask for base consent
and record it only for that checkout.

The Antigravity CLI's origin is a bare Cloud Run host rather than a
Google-owned domain; the statement says so: the trust applies to that
deployment and its publishing credentials, and the URL alone does not prove
Google owns it.

## From the command line

```bash
~/.local/bin/devcapsule project config trust list
~/.local/bin/devcapsule project config trust accept devcapsule-base
~/.local/bin/devcapsule project config trust withdraw devcapsule-base
~/.local/bin/devcapsule project run --trust devcapsule-base
```

`trust list` shows the channels this checkout's software comes through,
`devcapsule-base`, `claude-code`, `antigravity-cli`, with their origins and
integrity method, and previously accepted channels. A channel accepted under
other origins or terms is listed as not covered, with what was accepted.
Both text and JSON output give the trust record's path.
`accept` records the named channel immediately.
`run --trust` records it after the required review succeeds, even without `--save`.
`withdraw` removes that workstation acceptance. A matching per-checkout
consent can still permit the software afterward.
The record is `$XDG_CONFIG_HOME/devcapsule/trust.toml`, normally
`~/.config/devcapsule/trust.toml`.

Channels come from the checkout's selected lock. A capability added with
`config add` brings its component's channel into that list when consent applies.
Codex has no separate vendor-download consent in this launcher.

## Acceptance scope

An acceptance covers a vendor, origins, an integrity method and terms.
A new origin or changed terms requires another decision. Accepting again
keeps the origins you accepted before. Every download is checked against
the lock's checksum.

The acceptance belongs to your OS user account on this computer. Anyone
sharing that account shares its trust. A checkout can refuse a vendor
download with `config authorize claude-code-download false`. That denial
wins over workstation trust for the checkout.

Trust grants no host access. It does not select a base or add a capability.
Those choices have their own commands.

## Departures still ask, per checkout

A base outside DevCapsule's repository, a base you built on your computer
([Build and select a local base](local-base.md)), or a vendor whose channel
you have not trusted, is a per-checkout consent as before:

```bash
~/.local/bin/devcapsule project config authorize base-image default
~/.local/bin/devcapsule project config authorize claude-code-download true
~/.local/bin/devcapsule project config approve
```

`authorize base-image default` consents to the exact image the lock pins,
by digest, and stays valid while the lock pins it. `approve` lists the new
versions of software you consented to per checkout. Use
`config approve claude-code-download` or `config approve --all` to record them.
With no arguments, it only lists pending updates.
It refuses when other authorization decisions also need attention.
A matching channel acceptance normally removes that update question.
A checkout last launched by an older DevCapsule keeps its matching
per-checkout consents.

What each component brings is on [component upgrades](../updates/component-upgrades.md).
