---
description: Reviewing what an agent did before you keep it, and switching between agents on the same project without losing state.
weight: 5
updated: 2026-10-30
---
# Review and change agents

Autonomous agents move fast inside a capsule because tool-approval prompts are
off by default. Keep control over what enters your mainline branch by checking
every change with Git and your test suite—and feel free to combine or swap
agents as tasks change.

## Reviewing an agent's work before keeping it

1. **Start from a clean branch or checkpoint.** Commit or push your current
   branch to a remote before handing a large task to an agent. Because the
   working tree (including `.git`) is mounted read-write inside the capsule, a
   pushed remote branch—or a separate Git worktree ([Working in
   workstreams](../collaboration/working-in-workstreams.md))—gives you an
   untouched recovery point even if an agent runs `git reset` or rewrites local
   commits.
2. **Inspect every modified and untracked file.** Use your IDE's Git diff tool
   or run these checks in the terminal:

   ```bash
   git status --short
   git diff
   git diff --staged
   ```

   Watch for unintended edits to lockfiles, CI definitions, `.devcapsule/`, or
   skipped tests, plus stray scratch files left in the tree.
3. **Run the project's checks yourself.** Execute your unit tests, linter, and
   type checker in the capsule terminal rather than relying solely on the
   agent's summary—especially for newly added tests, which can mirror a flawed
   assumption in the implementation.
4. **Discard or refine cleanly.** Revert unwanted hunks with `git restore -p`
   (and remove untracked scratch files after previewing `git clean -nd`), or
   ask a second agent to review the diff before you commit and push.

## Running multiple agents or switching on a checkout

Claude Code (`claude`), OpenAI Codex (`codex`), and the Antigravity CLI
(`antigravity`) install into separate `/opt/...` prefixes and keep independent
persistent state directories (`~/.claude`, `~/.codex`, `~/.gemini`). You can
keep more than one enabled on the same checkout—for instance, implementing a
feature with one agent and asking another to critique the branch.

Manage your checkout's agents from a host terminal in the project directory (or
queue `add`, `omit`, and `restore` from the running session's [web
console](../sessions/web-console.md) for the next launch):

```bash
# Try an agent for a single launch without saving it to the checkout
devcapsule project run --with codex-agent

# Add an agent to this checkout's saved selection (shared manifest unchanged)
devcapsule project config add claude-code-agent

# Remove a checkout-added agent, or omit an agent offered by the project
devcapsule project config omit antigravity-agent

# Re-enable a project-offered agent that you previously omitted
devcapsule project config restore antigravity-agent
```

(Capability names and unambiguous component aliases—`claude-code`, `codex`,
`antigravity-cli`—both work on `add`, `omit`, and `restore`. Required
capabilities declared with `require` in `.devcapsule/devcapsule.toml` cannot be
omitted.)

### Your sign-in and settings stay intact when you switch

Running `devcapsule project config omit <agent>` removes that agent from your
next container image, **not** from your local storage. Its persistent slot
under your [configuration home](../configuration/home.md) keeps your OAuth
sign-in, session history, and custom settings file on disk, so adding or
restoring the agent later picks up right where you left off.
