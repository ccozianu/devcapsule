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
Trust Anthropic to supply Claude Code from downloads.claude.ai, verified by the SHA-256 the launcher pins, under https://www.anthropic.com/legal/commercial-terms, every version, for every project on this computer.
Accept, once for this computer? [y/N]:
```

**y** records the channel in your computer's trust record, with your other
answers, and the launch continues. **N** stops the launch; nothing is
written, and the command that accepts later is printed. Without a terminal,
in a script or an agent's session, the launcher prints the statement and the
command and stops with status 3; it never accepts on your behalf.

The Antigravity CLI's origin is a bare Cloud Run host rather than a
Google-owned domain; the statement says so, because trusting that channel
is trusting that deployment.

## From the command line

```bash
~/.local/bin/devcapsule project config trust list
~/.local/bin/devcapsule project config trust accept claude-code
~/.local/bin/devcapsule project config trust withdraw claude-code
~/.local/bin/devcapsule project run --trust devcapsule-base
```

`trust list` names the channels this project's software comes through,
`devcapsule-base`, `claude-code`, `antigravity-cli`, and whether this computer
trusts each; `--json` adds the record's path. `accept` and `--trust` record
one; `withdraw` removes it, and the next launch that needs the channel asks
again. The record is `trust.toml` under your DevCapsule configuration
directory, yours and never the project's.

## What an acceptance is, and is not

- It is your trust in the vendor's channel: that vendor, those origins, those
  terms. A new origin or changed terms in a later lock is a new question.
  Every download is still checked against the lock's checksum.
- It is per computer, for every project and version. A checkout can still
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
