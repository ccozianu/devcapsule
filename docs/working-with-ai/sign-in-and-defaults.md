---
description: How each agent signs in inside the capsule, the no-approval defaults DevCapsule seeds for it, where those settings live and how to change them.
weight: 2
updated: 2026-09-28
---
# Sign in and defaults

Agents sign in from a terminal inside the running capsule, with your own
provider account. Their configuration and sign-in state live in a
per-checkout persistent slot, so you sign in once per checkout.

## Signing in

| Agent | Command | Where the state lives |
|---|---|---|
| Claude Code | `claude`, then follow the sign-in it prints | `~/.claude` in the capsule, `CLAUDE_CONFIG_DIR` |
| OpenAI Codex | `codex login`, check with `codex login status` | `~/.codex` in the capsule, `CODEX_HOME` |
| Antigravity CLI | `antigravity`, then follow its authentication | `~/.gemini` in the capsule |

When an agent prints a sign-in URL, the browser is on your computer, not in
the capsule: copy the URL out through the desktop tab's clipboard panel and
open it there, then paste any code back the same way;
[Clipboard and browser](../everyday-development/clipboard-and-browser.md)
shows the panel. The resulting sign-in is stored in the slot above and
survives container replacement. It is a credential: it lives in your local
DevCapsule storage on this computer, not in the project, and it never
travels with the repository.

Codex can also take an API key: bind the same-named host environment
variable explicitly, as [Configuration nodes](../reference/configuration-nodes.md)
describes. DevCapsule never reads it ambiently, and the listing warns that an
environment variable is visible to every process in the capsule. The
interactive sign-in is the lower-exposure default.

## The defaults DevCapsule seeds

Before an agent's first launch in a checkout, DevCapsule writes the smallest
settings that make it work without tool approvals:

| Agent | File in the capsule | Seeded setting |
|---|---|---|
| Claude Code | `~/.claude/settings.json` | `permissions.defaultMode: bypassPermissions`, and the property that suppresses the one-time bypass notice |
| OpenAI Codex | `~/.codex/config.toml` | `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and a legacy sandbox flag so a sandboxed mode still works if you turn one on |
| Antigravity CLI | `~/.gemini/antigravity-cli/settings.json` | `toolPermission: "always-proceed"` |

Claude also runs with `DISABLE_UPDATES=1`: it uses the version the project
lock selected, and updates arrive through the project, not through the agent
updating itself.

These are defaults, not overrides. For Claude and Antigravity, a launch adds
only missing keys to an existing valid settings file; your explicit choices
and unrelated settings stay. To opt out, set a different permission mode in
the file; deleting the key restores the capsule default at the next launch.
An invalid file is left alone with a diagnostic. For Codex, the file is
seeded once, only when absent; edit or delete it freely, and keep any keys
you add above the first `[table]` header, because Codex appends tables to the
same file.

Authentication, workspace trust and model selection follow each vendor's
own flow. A newer agent version does not by itself give your account access
to a newer model; that is between you and the vendor.
