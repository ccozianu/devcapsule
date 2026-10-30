---
description: How each agent signs in inside the capsule, the no-approval defaults DevCapsule seeds for it, where those settings live and how to change them.
weight: 2
updated: 2026-10-30
---
# Sign in and defaults

Agents authenticate from a terminal inside the running capsule using your own
provider account or API key. Each agent's state directory lives in a dedicated
mode-`0700` persistent slot for that checkout, so you sign in once per checkout
and keep that state across container replacements.

## Signing in interactively

| Agent | Command in the capsule terminal | Persistent slot inside the capsule |
|---|---|---|
| Claude Code | `claude` (follow the sign-in flow) | `/home/devcapsule/.claude` (`CLAUDE_CONFIG_DIR`, slot `claude-code/home`) |
| OpenAI Codex | `codex login` (or `codex login --device-auth`; check with `codex login status`) | `/home/devcapsule/.codex` (`CODEX_HOME`, slot `codex/home`) |
| Antigravity CLI | `antigravity` (follow its authentication flow) | `/home/devcapsule/.gemini` (slot `antigravity-cli/home`) |

When an agent prints or opens an OAuth URL:

- **Without `host-browser`:** copy the URL out through the desktop tab's left
  sidebar clipboard box, open it in your computer's browser, and paste any
  authorization code back the same way ([Clipboard, keys and
  browser](../everyday-development/clipboard-and-browser.md)).
- **With `host-browser` authorized** (`devcapsule project config authorize
  host-browser true` or one-run `devcapsule project run --authorize
  host-browser true`): links opened by the CLI open directly in your host
  browser through DevCapsule's URL-only broker.

Interactive sign-in tokens stay inside your local DevCapsule data directory on
your host (`projects/by-path/<checkout>/components/<agent>/home`), outside the
repository and out of Git.

## Binding API keys explicitly

DevCapsule never forwards `OPENAI_API_KEY`, `GEMINI_API_KEY`, or
`ANTHROPIC_API_KEY` from your host shell automatically. When you prefer API-key
billing or headless execution over interactive OAuth:

- **Codex (`OPENAI_API_KEY`):** bind the declared secret input to your host
  environment variable—or pipe a key once into `codex login --with-api-key`
  inside the capsule so it is stored in `~/.codex` rather than exported to all
  container processes:

  ```bash
  devcapsule project config bind codex/openai-api-key host-environment:OPENAI_API_KEY
  # Withdraw later with:
  devcapsule project config unbind codex/openai-api-key
  ```

- **Antigravity CLI (`GEMINI_API_KEY` for headless `gemini` provider flows):**

  ```bash
  devcapsule project config bind antigravity-cli/gemini-api-key host-environment:GEMINI_API_KEY
  ```

- **Other provider variables (such as `ANTHROPIC_API_KEY`):** store a literal
  per-checkout value with hidden input (`devcapsule project config env set
  ANTHROPIC_API_KEY`) or pass it for one run (`devcapsule project run --env
  ANTHROPIC_API_KEY`).

Keep in mind that any variable delivered through the container environment is
readable by every process running inside that capsule; interactive sign-in
inside the agent's `0700` state slot is the lower-exposure default.

## The defaults DevCapsule seeds

Before an agent's first launch in a checkout, DevCapsule seeds minimal settings
so tools run without interactive permission prompts inside the container:

| Agent | File in the capsule | Seeded settings |
|---|---|---|
| Claude Code | `~/.claude/settings.json` | `{"permissions": {"defaultMode": "bypassPermissions"}, "skipDangerousModePermissionPrompt": true}` |
| OpenAI Codex | `~/.codex/config.toml` | `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and `use_legacy_landlock = true` |
| Antigravity CLI | `~/.gemini/antigravity-cli/settings.json` | `{"toolPermission": "always-proceed"}` |

Claude Code also runs with `DISABLE_UPDATES=1` so the binary matches the
pinned artifact in your lock rather than self-updating inside the container;
update agents through DevCapsule ([Component
upgrades](../updates/component-upgrades.md)).

### Changing or opting out of seeded defaults

DevCapsule treats these files as initial defaults, never forced overrides:

- **Claude Code and Antigravity CLI:** on launch, DevCapsule merges only
  missing keys into a valid JSON file. Change `permissions.defaultMode` or
  `toolPermission` to another value and your choice stays; deleting the key
  restores the capsule default on the next launch. Malformed JSON files are left
  untouched with a warning.
- **OpenAI Codex:** `~/.codex/config.toml` is written **once**, only when the
  file does not exist yet. Edit or remove keys (including `use_legacy_landlock`
  if a newer Codex build marks it deprecated) freely. Keep any top-level keys
  you add **above the first `[table]` header**, because Codex appends `[...]`
  tables to the end of `config.toml` automatically.

Model entitlements and rate limits come from your vendor account; upgrading an
agent binary in DevCapsule does not by itself change which models your plan can
access.
