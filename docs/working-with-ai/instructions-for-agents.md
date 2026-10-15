---
description: Give every agent the same durable context with an instructions file at the project root, and what belongs in it.
weight: 3
updated: 2026-09-28
---
# Instructions for agents

An agent that starts every session from zero repeats your explanations. A
short instructions file at the project root, committed with the code, gives
every agent and every session the same starting knowledge.

## One file, read by all three

Codex and the Antigravity CLI read `AGENTS.md` at the project root. Claude
Code reads `CLAUDE.md`. Keep one source of truth: write `AGENTS.md`, and make
`CLAUDE.md` a one-line pointer to it.

```markdown
Read your instructions from AGENTS.md; this project keeps nothing in
agent-specific files.
```

## What belongs in it

- What the project is, in two sentences, and where the longer brief lives.
- How to set up, build and test, as the exact commands.
- What must not be done without asking: the files that are generated, the
  branches that are protected, the data that is real.
- How you want work reported: what a finished change includes, what a
  commit message says.
- Where decisions and status are recorded, so the agent reads them before
  acting and writes to them when done.

Keep it short and current; an instructions file that lies is worse than
none. DevCapsule's own repository uses this pattern with a workflow that
records status, decisions and next steps in files, so that any agent, or any
person, can resume cold; [Collaboration](../collaboration/working-in-workstreams.md)
describes it, and you can adopt it or not.
