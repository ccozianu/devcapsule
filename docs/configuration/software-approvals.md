---
description: Vendor software is downloaded under the vendor's terms; you accept a vendor's channel once for your computer, every version and every project, and DevCapsule's base images the same way.
weight: 7
updated: 2026-10-24
---
# Vendor software and trust

Some of the software a capsule contains is downloaded from its vendor under
that vendor's terms, and DevCapsule never redistributes it: the coding agents
are the usual case. DevCapsule's own base images come from its published
repository, content-addressed by the digest the lock pins. Before the first
launch that needs either, DevCapsule asks you to trust the **channel**: the
vendor, the origins the lock names, the integrity method, and the vendor's
terms. You accept once, for this computer, and the acceptance covers every
version of that product in every project here.

## At launch

```text
Trust Anthropic to supply Claude Code from https://downloads.claude.ai, verified by the SHA-256 the launcher pins. Accept the terms at https://www.anthropic.com/legal/commercial-terms. This covers every version and every project for this OS user account on this computer. Anyone sharing this account uses this acceptance. Changed terms or a different channel require another decision.
Accept for this user account on this computer? [y/N]:
```

**y** stages the acceptance with your other answers; it is saved in your
account's trust record when every required answer is complete, and the
launch continues. **N** stops the launch; nothing is written, and the
command that accepts later is printed. Without a terminal,
in a script or an agent's session, the launcher prints the statement and the
command and stops with status 3; it never accepts on your behalf.

The Antigravity CLI's origin is a bare Cloud Run host rather than a
Google-owned domain; the statement says so: the trust applies to that
deployment and its publishing credentials, and the URL alone does not prove
Google owns it.

## From the command line

```bash
~/.local/bin/devcapsule project config trust list
~/.local/bin/devcapsule project config trust accept claude-code
~/.local/bin/devcapsule project config trust withdraw claude-code
~/.local/bin/devcapsule project run --trust devcapsule-base
```

`trust list` names the channels this checkout's software comes through,
`devcapsule-base`, `claude-code`, `antigravity-cli`, with their origins and
integrity method, and whether this account trusts each; a channel accepted
under other origins or terms is listed as not covered, with what was
accepted; `--json` adds the record's path. `accept` and `--trust` record
one; `withdraw` removes it, and the next launch that needs the channel asks
again. The record is `trust.toml` under your DevCapsule configuration
directory, yours and never the project's.

## What an acceptance is, and is not

- It is your trust in the vendor's channel: that vendor, those origins, that
  integrity method, those terms. A new origin or changed terms in a later
  lock is a new question; accepting again keeps the origins you accepted
  before. Every download is still checked against the lock's checksum.
- It is per OS user account on this computer, for every project and version;
  anyone sharing the account shares the trust. A checkout can still
  refuse a vendor's download, `config authorize claude-code-download false`, and the
  denial wins over the trust for that checkout.
- It grants no host access, selects no base and chooses no agent; those are
  separate decisions with their own commands.

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
versions of software you consented to per checkout and records them by
name or `--all`; a trusted vendor never reaches it. A checkout last launched
by an older DevCapsule keeps its per-checkout consents; they remain honored.

What each component brings is on [component upgrades](../updates/component-upgrades.md).
