---
id: D-0008
title: Known-Good Checkout Configuration History
status: accepted
date-proposed: 2026-09-01
date-decided: 2026-09-01
decided-by: Costin Cozianu
requirements: []
supersedes:
superseded-by:
---

# D-0008: Known-Good Checkout Configuration History

## Context

A checkout's configuration — the developer-authored
`devcapsule.checkout.toml` and its generated `devcapsule.resolved.toml`
under the XDG config tree — is precious and unversioned. The project
directory is under git; the checkout's config tree is not. A user hit by a
DevCapsule bug or their own misconfiguration has no way back to a
configuration that previously worked.

Whatever mechanism records history must serve that rollback purpose
directly: the user browsing it is already in trouble, and every entry they
see must be safe to return to. The files involved are small TOML, written
`0600` — treated as potentially sensitive.

## Options Considered

### Option A: Piggyback on an RCS (git under the config tree)

Cost: sensitive history becomes immutable — purging a value from git
history is surgery, deleting a snapshot directory is `rm -rf`. A hidden
`.git` under `$XDG_CONFIG_HOME` is a trap for backup tooling and dotfile
managers that already git-manage `~/.config`. And the RCS's actual
strengths — merges, branches, distribution — have no use here: this
history is linear, per-machine, per-checkout.

### Option B: Snapshot on every configuration mutation

A stamped copy before each `config set`/`bind`/`authorize`/`resolve`.
Cost: it defeats the UX. The history fills with intermediate and broken
states — every typo, every experiment that never launched — and the user
rolling back must guess which entries were any good. The mechanism would
record what the user *typed*, not what *worked*.

### Option C: Snapshot only what actually ran successfully

Record a generation only when a launch succeeds, deduplicated by content.

Cost: configurations that were never launched leave no trace; that is the
point, not a loss.

## Decision

Option C. The launcher records the history:

1. When `devcapsule project run` completes with **exit code zero**, the
   launcher records the checkout's configuration — the checkout record and
   its generated resolution, copied verbatim — as a known-good generation.
2. A generation is created **iff no existing generation has identical
   content**: duplicate directories are never written. Content identity is
   recomputed from the copied files themselves, so hand-pruned or
   hand-edited history stays honest.
3. Generations live outside the config tree, under the XDG **state** home:

   ```
   ~/.local/state/devcapsule/config-history/<creator>/<slug>/<UTC-stamp>/
       devcapsule.checkout.toml
       devcapsule.resolved.toml
       snapshot.toml            # recorded-at, digest, source checkout path
   ```

   XDG semantics agree (config is current settings, state is history), and
   placement inside the config tree is ruled out mechanically: `project
   list` discovers checkouts by globbing for `devcapsule.checkout.toml`,
   so historical copies there would appear as phantom checkouts.
4. Directory names are sortable UTC stamps (`20260901T193000Z`); a
   same-second distinct-content collision appends a counter. Files keep
   the `0600` posture of their originals.
5. A failure to record never fails the successful run it describes; it is
   reported as a warning and the launch's exit code stands.

Restoring is, deliberately, an ordinary file copy: the generations are
plain directories a user can inspect and copy back by hand — the recovery
mechanism has no failure modes of its own. A guided
`project config history` / `restore` command surface is recorded as
follow-on work; when it arrives, its pre-restore backup of the current
(presumably bad) tree must not enter the known-good sequence.

## Rationale

The trigger is validation, not mutation: an entry exists because that
exact configuration demonstrably launched, so every entry is safe to
restore by construction — the property the rollback UX depends on.
Content dedup keeps the history a short menu of distinct proven
configurations rather than a diary. The scheme parallels the resolution
matrix's verified-combinations model (D-0007) at per-user scale: what has
actually been proven to work, append-only, with success as the only
authority that writes.

## Consequences

- Retention is naturally bounded: generations appear only when a *new*
  configuration proves itself, which is rare; kilobytes each. No pruning
  policy is needed yet; deleting a directory is a legitimate manual prune.
- The debug-oriented `project run-image` path does not record: it launches
  an explicit image override, so its success does not prove the checkout's
  ordinary configuration.
- Named checkouts of the same project share the project's history
  directory; their records differ in content (and recorded paths), so
  dedup keeps them distinct.

## Reopen If

Users need cross-machine or synchronized history (the linear-per-machine
assumption breaks), or the history grows into a decision input for
tooling rather than a rollback menu — either would justify richer
storage than plain stamped directories.
