# Extend the approved 0.2.15 agent-defaults slice to Claude Code

From: project-management. To: maintenance. Owner decision: 2026-09-27.

This supplements the xtras/info scope and Antigravity-default messages sent
today. The owner explicitly requests the Claude correction too, asking whether
we can create minimal settings before the tool creates its configuration tree.

Anthropic's official settings documentation says installation creates no
settings file and users may create it themselves. CLAUDE_CONFIG_DIR relocates
user settings. DevCapsule already sets it to its persistent Claude home slot,
and the generic launcher creates slot/seed parents before mounting them.
Therefore seed $CLAUDE_CONFIG_DIR/settings.json before Claude's first launch:

```json
{"permissions": {"defaultMode": "bypassPermissions"}}
```

Use the same missing-file/missing-property policy as the Antigravity handoff:
preserve explicit values, unrelated/nested fields and vendor-written state;
leave malformed or structurally incompatible settings intact with a diagnostic;
respect adopted external state. Let Claude create the rest of its own state.
No sign-in/trust record fabrication or organization-enforced setting is requested.

There is a documented separate first-use bypass notice. Verify the selected
version's supported user setting for suppressing it (including whether
skipDangerousModePermissionPrompt is supported), and if supported seed that
minimal property too under the owner's no-tool-approval default. That key's
availability has not been verified by this review. Otherwise report the
one-time notice accurately. Ordinary authentication/user questions are separate.

Accept only after a fresh interactive launch from an initially empty managed
slot demonstrates the mode and ordinary tool execution, followed by vendor
state writes and container replacement. Test existing/malformed files and
repeat launch. Headless execution alone does not prove interactive first run.
Do not broaden this to IDE extension controls without a separate need.

Sources:
- https://code.claude.com/docs/en/settings#find-or-create-your-settings-files
- https://code.claude.com/docs/en/permission-modes#start-in-a-different-permission-mode

The full work order on ws-project-management/coordination is updated at
engineering-docs/work-orders/2026-09-27-project-environment-discovery.md.
This is a scope/design handoff, not implementation or a vendor runtime test.
