---
description: Add Claude Code, OpenAI Codex or the Antigravity CLI to your checkout in one command, and let it work at full speed inside the capsule's boundary.
role: agents
weight: 1
updated: 2026-10-25
---
# Choose an agent

DevCapsule supports three coding agents. Choose agents for your checkout.
DevCapsule acquires them on the next launch and keeps their sign-in state between sessions.

| Agent | Add it to your checkout | Start it in the IDE terminal |
|---|---|---|
| Claude Code | `~/.local/bin/devcapsule project config add claude-code-agent` | `claude` |
| OpenAI Codex | `~/.local/bin/devcapsule project config add codex-agent` | `codex` |
| Antigravity CLI | `~/.local/bin/devcapsule project config add antigravity-agent` | `antigravity` |

Run the `config add` command in your computer's terminal, from the
project folder. It changes your checkout's selection and local version pins.
It does not change the shared manifest or lock. Save your work, stop the
capsule, then use `project run` to acquire the agent and start another session.
Read any vendor terms before accepting them. See
[Vendor software and trust](../configuration/software-approvals.md) for
consent commands and the current limit on trusting personally selected agents.

Use your own provider account and plan. DevCapsule does not include an AI
subscription and never imports a sign-in from your computer. How each agent
signs in, and what its defaults are inside a capsule, is on
[Sign in and defaults](sign-in-and-defaults.md).

## Why agents run at full speed here

Every agent starts with tool approvals off: it edits files, runs tests and
uses the terminal without asking you for each step. That posture is safe
because the capsule is the sandbox. An agent can change your project folder,
which Git protects, and its own persistent state. It cannot reach your home
directory, your credentials, your Docker daemon or your desktop unless you
granted that access explicitly; [Containment](../containment/the-boundary.md)
lists what is shared and what is not. If you prefer approvals, turn them on
in the agent's own settings; the setting is yours and survives launches.

## A first request

Try something small and reviewable in the IDE terminal:

> Explain how this project runs, then suggest one small improvement and a
> way to check it. Wait for me before changing files.

Read the result, run the project's checks, commit what you keep. Give the
agent durable context with an instructions file at the project root; see
[Instructions for agents](instructions-for-agents.md).

## Subscriptions and choice

Whichever your subscription covers. All three read a project instructions
file, run inside the same boundary, and keep their sign-in per checkout. You
can select more than one, and you can switch in a later session
without losing anything; see [Review and change agents](review-and-change-agents.md).
