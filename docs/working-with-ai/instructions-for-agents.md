---
description: Give every agent the same durable context with an instructions file at the project root, and what belongs in it.
weight: 3
updated: 2026-10-30
---
# Instructions for agents

An agent that starts every session cold either guesses your conventions or
spends time rediscovering how to build and test the repository. A concise
instructions file at the project root—committed alongside your source
code—gives every agent and every contributor's capsule the same starting facts.

## One source of truth for all three agents

OpenAI Codex and the Antigravity CLI automatically read `AGENTS.md` at the
repository root. Claude Code reads `CLAUDE.md`. Keep all project rules in
`AGENTS.md` and commit a two-line `CLAUDE.md` pointer beside it so the two
files never drift apart:

```markdown
Read and follow AGENTS.md at the repository root. This project keeps shared
agent instructions in AGENTS.md rather than duplicating them per tool.
```

## What belongs in `AGENTS.md`

Keep `AGENTS.md` concrete and verifiable:

- **Purpose and layout:** two sentences on what the software does and where key
  packages, entrypoints, and architecture docs live.
- **Exact build, lint, and test commands:** the commands that run inside the
  capsule terminal (for example, `pytest -q`, `npm test`, `mvn verify`) so the
  agent checks its own changes without guessing flags.
- **Boundaries Requiring Human Confirmation:** generated files not to hand-edit,
  migrations or public contracts not to break silently, and branches never to
  push directly.
- **Commit and review expectations:** how changes should be scoped, tested, and
  described in commit messages or pull requests.
- **Where active state lives:** any status or decision log the agent should
  read at session start and update before stopping.

Keep instructions short and delete stale rules promptly—an outdated command in
`AGENTS.md` misleads every session until fixed. Remember also that instruction
files guide cooperating models rather than enforcing security: enforce hard
limits on files, network access, and credentials through the capsule boundary
([The boundary](../containment/the-boundary.md)).

DevCapsule's own project workflow ships a structured `AGENTS.md`, `WORKFLOW.md`,
and status-file convention so humans and different coding agents can hand work
off cleanly across branches; see [Working in
workstreams](../collaboration/working-in-workstreams.md) if you want to adopt
it in your repository.
