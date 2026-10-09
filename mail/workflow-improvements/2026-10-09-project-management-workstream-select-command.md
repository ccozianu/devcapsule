# Make selecting a workstream one fast, deterministic command

Sent: 2026-10-09

From: `project-management`, to `workflow-improvements`. Owner observation and
design direction taken in this checkout on 2026-10-09.

## What happened

Switching this checkout to `project-management`, a routine step, took about
seventeen agent tool calls and roughly ten minutes of wall clock. Three calls
did the work (checkout and fast-forward, mail take, merge and publish). The
rest discovered what the protocol requires but the tooling does not provide:

- The brief lists definition changes by headline, not text; the agent found
  the `Definition read:` blob stamps and diffed them by hand, getting the
  hash kind wrong once.
- The brief does not list the bugs the workstream owns; the agent scanned
  every bug record on `main` with `git show`.
- The brief says "must synchronize" but not whether the merge is clean; the
  agent ran a dry-run merge to find out.
- The status file is 479 lines, 30 KB, read in full; most of it is history
  that *Active Tasks Versus Historical Context* says should not be there.
- The owner's 2026-10-01 decision names `devcapsule project workflow
  --select <name>` as the selection command; it does not exist yet, so
  checkout, fast-forward, take, brief and synchronization are five steps.

## Owner direction

Both scenarios are to be supported: a human runs the selection at the
terminal, and an agent runs it as a tool. The owner also raised a third:
DevCapsule itself invoking an agent when the switch hits a conflict. The
design below serves the first two with one command and leaves the third as
a hook the project can configure, so that who drives the command never
changes what it does.

## What accepting means

1. **One deterministic command**, `devcapsule workflow select <name>`
   (reachable under `project workflow --select` inside a capsule, per the
   2026-10-01 decision), performing in order: refuse on a dirty tree that
   carries workstream state, naming the files; check out the branch and
   fast-forward it to origin; take mail and stage it; merge `main` in when
   the synchronization rule says it must or should; print the brief; publish.
   Every step is idempotent or already recoverable, so a rerun after any
   failure converges. This is the property the companion item
   `2026-10-09-project-management-protocol-state-transitions.md` asks to
   review; the two should be designed together.
2. **Three stop states**, each left consistent and reported in a structured
   form (`--json` or equivalent) as well as prose, so an agent does not parse
   sentences to learn what happened:
   - *merge conflict*: the merge stays in progress with git's markers and
     the conflicted paths are listed; resolution is content judgment and
     belongs to a human or an agent, not the command;
   - *dirty tree with workstream state*: refused before anything is touched;
   - *routing mismatch*: the branch is not the one the workstream list
     names, or the list on `main` and the local copy disagree; refused, both
     shown.
3. **The brief prints**, for the selected workstream, the definition text
   added since its stamp (the *Unreleased* entries are the natural unit),
   the open bugs it owns from `main`, and whether a merge from `main` is
   clean.
4. **A length budget for status files**, surfaced at checkpoints or by a
   doctor-class finding, pointing at the archive procedure.
5. **Agent-on-conflict as a deferred hook**, not built into the command: an
   `--on-conflict <command>` option or a handler declared in the local
   workflow file, receiving the structured stop report. Reasons to keep it
   out of the command itself: the rules make a workstream change the human's
   decision and forbid an agent changing workstreams autonomously, so a
   handoff the human sees first keeps that line; a launcher would have to
   know which agent, model and credentials apply on each host, which is not
   portable; and a deterministic command with stated end states is testable
   with the interruption tests the companion item proposes, while one that
   spawns an agent is not. The hook lets this repository try the idea with
   the Codex harness it already has, and lets adopters choose.

## Why it belongs to you

The brief, the selection command, the status-file rules and the definition
text are the packaged definition's; the sender has no implementation remit.
Project-management records the owner's direction above as the decision and
will register the slice when you scope it.
