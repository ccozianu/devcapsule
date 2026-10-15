---
description: DevCapsule 0.2.15 makes project setup and everyday environment adjustments easier, upgrades the three agents, and lets agents work without approval prompts by default.
updated: 2026-09-28
---
# DevCapsule 0.2.15

Released 2026-09-27. [Download and checksums](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.15).

DevCapsule 0.2.15 makes project setup and everyday environment adjustments
easier.

- `project init` catches a misspelled configuration name before asking any
  question or writing any file, and suggests the correct name. Correcting a
  typo no longer costs the answers you just entered.
- Install additional tools under `/opt/xtras` without sudo. It points to the
  persistent `$HOME/xtras`, so existing installations stay available, and
  `/opt/xtras/bin` is on `PATH` for IDEs, agents and terminals. The storage
  belongs to the checkout by default and follows an explicitly bound home.
  You manage these tools and their updates.
- `devcapsule project info` shows component versions, the environment
  variables DevCapsule provides with their purpose, and persistent and
  temporary storage. It works on your computer from the project folder or
  any folder beneath it, and anywhere inside the capsule. Inside, it
  separates the running software from the next launch's selection. `--json`
  is for agents and scripts; secret values are omitted.
- Claude Code and the Antigravity CLI start with tool approvals off, like
  Codex already did: DevCapsule seeds the smallest settings before their
  first launch, adds only missing properties to existing valid settings, and
  leaves explicit choices, malformed files and adopted external state alone.
- Updated agent recommendations: Codex 0.157.1, Claude Code 2.1.283 and
  Antigravity CLI 1.2.12, each verified against its vendor's published
  checksums. Existing project locks and selected version sets stay as they
  are until you choose to update them.

Authentication and model access still use your own provider account; a
newer agent does not by itself grant access to a newer model. Tools under
`/opt/xtras` are not installed on another machine and not recorded in the
component lock. The broader in-capsule project-command diagnostic issue
remains deferred.

**Upgrading.** Installing the new launcher grants no new host permission.
A checkout created by a client older than 0.2.14 may be asked once for the
vendor-download consent those clients did not record.
