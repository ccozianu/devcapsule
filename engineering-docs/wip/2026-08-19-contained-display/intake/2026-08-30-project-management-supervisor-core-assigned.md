# Intake: The Capsule Supervisor Core Is Assigned To This Workstream

Delivered: 2026-08-30

From: `project-management`, recording a product-owner decision made the same
day.

## What Is Being Handed Over

The capsule supervisor core — decided `in-v1` on 2026-08-29 as the ledger row
*Capsule Supervisor And Multi-IDE Sessions* — is assigned to
`contained-display`, by the product owner, on 2026-08-30. This workstream now
owns both halves of one sequenced effort: the supervisor first, then the
contained display as its first consumer.

## Why One Workstream

The contained display is not one process but a tree: a virtual X server, a
window manager, the noVNC bridge, the `xdg-open` shim, and the IDE as their
client. The current container model — the IDE execs as the entry process and
the capsule dies with it — cannot host that tree, so a display built first
would be forced to invent a throwaway process manager. The supervisor is that
manager, built once and transport-agnostic: it runs usefully under host X11
today and anchors the contained display when the transport lands.

## The V1 Scope Cut, Recommended Not Ratified

The supervisor's V1 scope is the lifecycle anchor only, per the ratified
split: PID-1 duties (signal forwarding, child reaping), a declarative child
list, an explicit session end, and a headless mode with no GUI children —
which is the decided mechanism for the release-blocking non-interactive-runs
item. The desktop-integration layer (tray, one-click secondary IDEs,
multi-IDE sessions) is post-V1 and not part of this assignment. The ledger
row's cost warning stands: constant pressure on "minimal" is the main risk.

## What Rides On This Assignment

- **Non-interactive runs** (release-blocking, decided 2026-08-23/29): the
  supervisor with no GUI children. The pre-recorded authorization and
  acquisition-acknowledgement shape is design work this workstream now hosts.
- **Reaping semantics**: the coordination backlog's external-resource entry
  is revised by supervised cleanup; coordinate before closing it.
- **The display's own sequencing**: the full-day ratification test of the
  display transport should run atop the supervisor, validating both at once.
- **The VSCodium surface** (`codium-surface`, unowned) is decided to shape
  inside the supervisor model; expect its scope to consult this work.

## References

- Ledger rows: *Capsule Supervisor And Multi-IDE Sessions*,
  *Contained Display And Desktop Integration* (release target restated
  2026-08-30), *The Release Thesis: Workspace And Containment* in
  `engineering-docs/wip/2026-08-09-project-management/v1-scope-ledger.md`.
- Backlog: *Non-Interactive Runs* in the same directory's
  `coordination-backlog.md`.

## Delivery Note, Recorded Latitude

This item references ledger rows that exist on
`project-management/coordination` and not yet on `main`. Per the precedent
recorded at the 2026-08-27 pause — the target lands no later than the
reference — it travels on that branch and reaches `main` with the ledger
through the branch's next pull request, rather than alone through the outbox
ahead of the rows it cites.

Priority and sequencing within the assignment are this workstream's judgment.
