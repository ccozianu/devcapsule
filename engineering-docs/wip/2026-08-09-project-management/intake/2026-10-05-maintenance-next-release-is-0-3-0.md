# Owner decision: the next release is 0.3.0, not 0.2.16

Sender: maintenance. Recipient: project-management. Date: 2026-10-05.

## Decision

During the maintenance bug triage of 2026-10-05 the owner decided that the
next release, planned and registered as 0.2.16, is named **0.3.0**. The
owner's words: a marketing decision reflecting the big jump forward from
0.2.15. This firms up the intent recorded on 2026-10-03 (0.3.0 if 0.2.16
delivered its full planned scope); it is now unconditional.

## What it changes for project-management

- The release registration and scope for the next release carry the name
  0.3.0. `main` stays at 0.2.16.dev0 until the release branch's first
  commit sets the version, as the local version scheme in
  `WORKFLOW-LOCAL.md` says; maintenance does not touch `pyproject.toml`
  for this.
- The version scheme's text may want the owner's expectation written down:
  0.3.x next, then a jump to 0.9 for V1's betas and release candidates.
  Maintenance keeps it in its status file until then.
- Bug records: maintenance retargeted its own four records from 0.2.16 to
  0.3.0 (recursive successor stale resolution, detached successors,
  runtime configuration inspection, project group guard). Two records
  owned by other workstreams still say 0.2.16 and are theirs to retarget:
  `2026-10-03-agents-cannot-discover-how-to-build-and-test.md`
  (workflow-improvements, fixed) and
  `2026-10-04-intellij-relaunch-stale-directory-lock.md`
  (component-catalog, closed). Forward or relay as you see fit.

## Scope the owner put into 0.3.0 at the same triage

For the plate, so sequencing is one picture: the recursive-successor test
on a fresh workspace (option D of its record) and the general rule that
every end-to-end test runs on a fresh clone with best-effort cleanup; the
installed-IDE reuse and reaping design review with the owner, named build
contexts first, the "optimized way of building Docker images"; the
in-capsule project-command fix already decided on 2026-10-01; and, last on
the plate, ecosystem-aware project bootstrap, which the owner ruled stays a
bug (onboarding in minutes is an implicit promise) rather than leaving for
the V1 scope ledger.
