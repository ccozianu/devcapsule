# Confirmed intake dispositions: upgrade presentation and release scope

From: project-management. To: component-upgrades. Date: 2026-10-09.
Authority: the owner confirmed the 23-item disposition table in this session.

The two contained-display rulings are accepted requirements within the broader
upgrade experience. Reconcile them against the integrated configuration/base
contract when you next scope that design slice; this does not place them ahead
of the current consent slice or create a new 0.3.0 gate.

- Render a checkout's configuration by its configured schema. Only mention a
  newer schema; do not show newly known nodes as recorded configuration.
- Offer the project's pinned base, a newer known recommendation and the current
  local choice, with an override clearly identified and supported actions named.
  Explain at launch when an override selects a different base. Preserve outcomes
  rather than obsolete command spellings.

The original messages, retained in Git at 967e9f9a3622d3b84c42eec6df004267a1abf143:
- engineering-docs/wip/2026-08-09-project-management/intake/2026-09-13-contained-display-config-list-renders-by-configured-schema.md
- engineering-docs/wip/2026-08-09-project-management/intake/2026-09-14-contained-display-config-offers-the-recommended-base.md

Two existing commitments are acknowledged without another adoption vote:
D-0011 through D-0013 were assigned by the owner to the next release, now named
0.3.0 unconditionally by the 2026-10-05 ruling. R-UPGRADE-002 remains your
accepted wanted V1 follow-up, not a new release gate; its operational choices
belong to its design slice. Project-management retains release scope and cut.

The coordination backlog and intake-dispositions log record the handoff. Source
integration is not claimed to complete candidate or host-restart acceptance.
