# Owner-directed standing release practice: review AI agent versions

From: maintenance. To: project-management. Owner direction: 2026-09-27.

While maintenance was selected, the owner asked that every release try to
upgrade at least the AI agent CLIs to their then-current versions, noting
newer Codex and Claude clients support newer models. Applies from 0.2.15.
This is an accepted owner instruction to carry into the runbook you own,
not a request to resume project-management before 0.2.15 is released.

The 0.2.15 release overview now records all three current pins and directly
fetched vendor candidates: Codex 0.153.4 -> 0.157.1; Claude 2.1.261 -> 2.1.283;
Antigravity 1.1.24 -> 1.2.12. These have not yet been acquired/tested or pinned.

Proposed runbook text (insert as an Agent Freshness Review section and reference
it from preparation and final acceptance; base source is the release runbook
at 1d9a27f, whose policy is also on main):

For every release, review the supported AI agent CLIs against their current
generally available vendor releases. Record the date, vendor source, current
pin, candidate and disposition. Attempt upgrades and validate exact artifacts,
platform compatibility, configuration defaults, ordinary tool use and state
persistence before accepting new pins. Record a concrete reason and follow-up
for each holdback or unavailable feed. Keep checkout-selected versions and
acquisition permissions intact. Recheck before final acceptance; a new version
gets an adopt-or-hold decision, not silent replacement of an accepted candidate.
If adopted, make a new candidate and rerun relevant acceptance. Record tested
versions and holdbacks in release notes. A newer CLI alone is not proof that
an account has access to a particular model.

No changes to the generic WORKFLOW definition, no new agent product selection,
and no automatic upgrades of users' running capsules are requested. Maintenance
will execute this review for 0.2.15; please acknowledge the recurring runbook
update into the post-release coordination queue when you resume.
