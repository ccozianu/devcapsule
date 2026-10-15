---
description: DevCapsule 0.2.14 fixes configuration recovery after an upgrade, records vendor-download consent once per checkout, adds the configuration review, and retires the legacy PyCharm launcher.
updated: 2026-09-28
---
# DevCapsule 0.2.14

Released 2026-09-25. [Download and checksums](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.14).
The first release intended for adopters outside the project.

- **Configuration recovery after an upgrade works again.** Upgrading to
  0.2.12 had broken the recovery of an existing checkout's configuration;
  0.2.14 fixes it and enforces the configuration contract from artifact
  admission through launch.
- **Vendor downloads ask once per checkout.** Earlier clients installed
  vendor downloads other than Claude Code without recording your consent.
  0.2.14 asks once for every vendor download. On such a checkout, `project
  config show` lists the decision with its reason; answer with
  `devcapsule project --path <checkout> config authorize antigravity-download true`,
  or `false` after removing the agent from the project's need, then
  `devcapsule project --path <checkout> config resolve`. This is the one-time
  exception the upgrade-compatibility requirement provides for.
- **Commands.** `project config list` is now a data listing with a `SOURCE`
  column naming the document each row comes from. The new `project config
  show` adds the files behind the resolution and the review: pending
  decisions with remedies, and whether resolving is needed. `project run
  --print-command` prints the Docker command instead of launching.
- **The in-capsule command is `devcapsule`**; repositories that develop
  DevCapsule itself may name it `devcapsule0` instead.
- **The legacy `pycharm run` is retired**; use `project run`.
- **The workflow ships as a component**: releases, the reserved
  `maintenance` workstream, bug frontmatter, `ws-` branches, the workflow
  declaration, the local workflow file, mail and published state on a
  coordination branch, and the session-start synchronization judgment.

**Deferred**, tracked in the release bug table: configuration discovery
from a directory outside the project inside a capsule, reuse of installed
IDE and component layers across formations, manual ecosystem setup for
fresh clones, the JetBrains X11 compositing and native-launcher warnings,
cleanup of exited recursive containers, and a flaky claim-lifecycle test.
