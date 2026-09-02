# Bug: Antigravity's State Is Wider Than The Analyzed Path, And The Nested Slot Walls It Off

Date opened: 2026-09-02

Status: open; fix applied on the workstream branch the same day (slot
widened to `~/.gemini`, contract and launcher guards per the
state-slots design note). The owner repaired the live checkout's
ownership by hand (`chown`) and the CLI then worked through the
2026-09-02 smoke; the widened slot and the launcher pre-creation get
their first live exercise on the next rebuild-and-run, which closes
this record

Requirements: R-PRODUCT-001

Related: the workstream's
[Antigravity license and redistribution analysis](../../wip/2026-08-30-component-catalog/antigravity-cli-license-and-redistribution-analysis.md)
(its state-location fact is corrected by this record).

## Symptom

First real use of the CLI inside the freshly launched capsule:

```
Error: project: failed to get/create default project: project: create projects dir /home/devcapsule/.gemini/config/projects: mkdir
     /home/devcapsule/.gemini/config: permission denied
```

## Mechanism (reproduced 2026-09-02 against the canonical image)

Two defects compound:

1. **The analyzed state footprint was too narrow.** The analysis
   recorded "state and credentials at `~/.gemini/antigravity-cli/`",
   and the component declared its checkout-scoped slot on exactly that
   path. In use, the CLI also keeps a project registry at
   `~/.gemini/config/projects` — a sibling of the slot, not inside it.
2. **A slot nested two levels beneath home walls off its siblings.**
   Docker materializes the mount point for
   `~/.gemini/antigravity-cli` by creating the intermediate
   `~/.gemini` parent — owned by root. The capsule user then cannot
   create anything else under `~/.gemini`. Reproduced directly: with
   the slot mounted, `~/.gemini` is `root:root` and
   `mkdir ~/.gemini/config` fails with exactly the reported error.
   Claude Code and Codex never hit this because their slots
   (`~/.claude`, `~/.codex`) are direct children of home: the mount
   point is the user-owned host directory itself.

So even a correctly-behaving tool writing *only* near the analyzed
path was one `mkdir` away from this failure; the wider footprint just
found it first.

## Fix (applied; owner re-smoke pending)

The slot covers `~/.gemini` whole — the same whole-directory pattern
Claude Code uses for `~/.claude`. The mount point is then the
user-owned host directory, and both `antigravity-cli/` and `config/`
live inside the persistent, credential-sensitive, checkout-scoped
slot. The runtime template change advances the component template
digest, so the canonical image identity changes with it (expected
pre-release).

The general hazard is now guarded (owner ruling, 2026-09-02, same
day): contract validation rejects overlay slots deeper than one level
beneath home and cross-component slot overlap, and the launcher
pre-creates home-overlay mount points as the invoking user — see the
[state-slots design note](../../design-notes/devcapsule/state-slots-home-overlay-and-ownership.md).

## Reproducibility

Always, before the fix: launch any formation with the antigravity
component and run any command that touches the project registry.

## Verification Target

- Automated test: the component's slot path is `~/.gemini` (direct
  child of home), and the template digest test pins the new identity.
- Manual validation: in the relaunched capsule, an antigravity prompt
  that previously failed creates `~/.gemini/config/projects`, and both
  it and `~/.gemini/antigravity-cli` persist across a relaunch of the
  same checkout.
