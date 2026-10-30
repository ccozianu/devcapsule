---
description: Add Claude Code, OpenAI Codex or the Antigravity CLI to your checkout in one command, and let it work at full speed inside the capsule's boundary.
role: agents
weight: 1
updated: 2026-10-30
---
# Choose an agent

DevCapsule supports three coding agents. Select one or more for your checkout;
DevCapsule materializes them on the next launch and preserves their sign-in
state and settings across container restarts.

| Agent | Add it to your checkout | Start it in the IDE terminal | Download trust channel |
|---|---|---|---|
| Claude Code | `devcapsule project config add claude-code-agent` | `claude` | `claude-code` (`claude-code-download`) |
| OpenAI Codex | `devcapsule project config add codex-agent` | `codex` | npm package (`@openai/codex`, SHA-256 verified) |
| Antigravity CLI | `devcapsule project config add antigravity-agent` | `antigravity` | `antigravity-cli` (`antigravity-download`) |

Run `devcapsule project config add <agent>` in a host terminal from your
project directory (or request `add` from the running session's [web
console](../sessions/web-console.md)). It updates your local checkout record
and per-checkout component pins without changing `.devcapsule/devcapsule.toml`
or the shared lock. Save your work, exit the IDE, and run `devcapsule project
run` to materialize the updated environment.

Claude Code and Antigravity CLI are proprietary binaries downloaded directly
from Anthropic and Google on your machine and verified by SHA-256. Trust a
channel once across all projects in your configuration home (`devcapsule home
trust accept claude-code` or `devcapsule home trust accept antigravity-cli`),
or approve it for this checkout only (`devcapsule project config authorize
claude-code-download true` / `antigravity-download true`) after reviewing the
vendor's terms; see [Vendor software and
trust](../configuration/software-approvals.md).

Bring your own provider account, subscription, or API key—DevCapsule does not
bundle an AI plan and never imports credentials from your host automatically.
See [Sign in and defaults](sign-in-and-defaults.md) for authentication and
seeded settings.

## Why agents run without step-by-step prompts here

DevCapsule seeds each agent to run without interactive tool-approval prompts so
it can read code, edit files, and run builds and tests autonomously. That
posture relies on the container boundary rather than per-command dialogs:

- Your host home directory, SSH keys, browser profile, other repositories, and
  host desktop are unmounted by default ([The
  boundary](../containment/the-boundary.md)).
- Inside the capsule, the agent has full write access to the mounted repository
  (`/workspace/<slug>`, including `.git`) and to this checkout's persistent
  state. Push clean commits to a remote or keep an independent backup before
  large autonomous runs, because local Git history inside a writable `.git`
  directory can be modified by any process in the capsule.
- Prefer step-by-step confirmation? Change the permission mode in the agent's
  own settings file inside the capsule; DevCapsule preserves your explicit
  setting across launches.

## A first request

Start with a small, verifiable task in the IDE terminal:

> Explain how this project builds and runs its tests, then propose one small
> improvement and how to verify it. Wait for my go-ahead before editing files.

Inspect the diff, run the test suite, and commit what you want to keep. Give
every agent durable repository context with an instructions file at the project
root; see [Instructions for agents](instructions-for-agents.md).

## Using multiple agents or switching later

All three agents read your project instructions file, share the same checkout
working tree, and store their credentials in separate per-checkout state slots
(`~/.claude`, `~/.codex`, `~/.gemini`). You can install two or all three in the
same checkout—for example, using one to implement and another to review—or
switch later without losing saved sign-ins; see [Review and change
agents](review-and-change-agents.md).
