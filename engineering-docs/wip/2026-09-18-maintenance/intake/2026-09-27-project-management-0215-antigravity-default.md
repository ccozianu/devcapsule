# Third approved small addition to 0.2.15: Antigravity tool permissions

From: project-management. To: maintenance. Owner decision: 2026-09-27.

This supplements `2026-09-27-project-management-0215-xtras-info-scope.md`;
xtras, project info, the init fix and the guard-bug deferral remain as sent.
The owner now selects the third addition: set `toolPermission` to
`always-proceed` in `$HOME/.gemini/antigravity-cli/settings.json` so ordinary
agent tool use does not keep asking the user for approval.

Seed new managed Antigravity settings and add the property when missing from
existing managed settings. Preserve unrelated keys and explicit permission
choices; leave malformed files intact with a diagnostic. Preserve the existing
adopted-external-state boundary and document the manual one-key edit there.
The generic seed helper only creates absent files today, so it does not by
itself provide the missing-property behavior. Verify the vendor key/value in
the selected version and prove a tool action proceeds without prompting.

Codex already seeds approval_policy=never and sandbox_mode=danger-full-access
in v0.2.14; existing config files are not overwritten. No Codex change is needed.

Accept this into the release plan and validate it alongside the two earlier
additions before final acceptance. The permanent work order is updated on
ws-project-management/coordination at
engineering-docs/work-orders/2026-09-27-project-environment-discovery.md.
Implementation remains with maintenance; this handoff changes no runtime code
or live agent settings.
