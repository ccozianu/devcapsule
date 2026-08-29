# Workflow Invariants As Pre-Commit Hooks

Written 2026-08-29 by `project-management`, fleshing out a product-owner idea
raised while dispositioning the intake-staleness item: the workflow's
mechanical invariants should be guarded by the `pre-commit` framework, offered
to the user as an installable check rather than left to diligence.

Status: proposed design; the disposition that adopts the invariant as the
mechanism is decided, the implementation shape below awaits ratification.

## The Tool

[`pre-commit`](https://pre-commit.com) is a Python-packaged git-hook manager:
a repository declares its checks in `.pre-commit-config.yaml`, and a developer
opts in with `pre-commit install`, after which the declared hooks run against
staged changes on every commit. `pre-commit run --all-files` runs the same
checks over the whole tree, which is what a CI gate calls.

It fits this product unusually well: DevCapsule already requires Python 3.12+
to run at all, so the framework adds no runtime burden an adopter does not
already carry.

## The Shape: Local Hooks Calling The Product, Not Remote Hook Repos

`pre-commit`'s usual distribution model — pointing the config at a remote
hooks repository that it clones on install — is off-thesis: it introduces a
network fetch and an implicit dependency into a product positioned on explicit
boundaries and offline-present context.

The proposed shape instead:

- DevCapsule grows a CLI surface, working name `devcapsule workflow verify`,
  that checks the invariants below against the repository it runs in. It is
  offline, reads only the tree and the Git index, and exits non-zero with a
  plain-language explanation of the violated invariant.
- The seeded `.pre-commit-config.yaml` uses `repo: local` with
  `language: system` entries invoking that command — no clone, no network, no
  version skew between the workflow definition and its checker, because both
  ship in the same DevCapsule distribution.
- `devcapsule bootstrap project` seeds the config file alongside the workflow
  files and **offers** `pre-commit install` rather than performing it. Opt-in
  installation matches the product's consent posture; a hook is code that runs
  on the user's future actions.

## The V1 Invariant Set

All mechanically checkable from the tree plus the staged diff, no history
walk, no network:

1. **The intake exclusive-or.** Every delivered item is in exactly one of its
   workstream's `intake/` or that workstream's `intake-dispositions.md` —
   never both, never neither. Per-commit form: a commit deleting a file from
   an `intake/` must append a row naming it to that workstream's disposition
   log in the same commit, and no log row may name a file still present.
2. **Disposition logs are append-only.** A staged change to any
   `intake-dispositions.md` may only add rows; edits or deletions of existing
   rows fail the check.
3. **Intake naming.** New intake files match
   `YYYY-MM-DD-<sender-mnemonic>-<slug>.md` and the sender mnemonic is a
   registered workstream.
4. **The WIP carve-out (restriction 11).** A commit may add files to another
   workstream's `intake/`, but may not modify or delete anything else under
   another workstream's `engineering-docs/wip/` directory. Requires the
   committing workstream's identity, taken from the branch mnemonic.
5. **Registry agreement.** Every `engineering-docs/wip/<date>-<mnemonic>/`
   directory appears in the root `CURRENT-STATUS.md` registry and vice versa —
   the check the readiness assessment found missing when the registry was
   stale three ways at once.

Deliberately excluded, per the 2026-08-29 disposition: any staleness signal.
The invariant says where an item is, not how long it has sat; the release gate
remains what catches rot.

Candidate later additions, not V1: requirement-record frontmatter validation
(id/status/type against the documented vocabulary), and cross-reference
integrity for `R-`/`D-` identifiers.

## Enforcement Tiers

- **Adopter projects:** opt-in local hooks, seeded by bootstrap, as above.
- **This repository:** the Nox gate gains a session running
  `devcapsule workflow verify --all` so the invariants hold even when a
  contributor has not installed hooks. This achieves what the rejected
  checkpoint-sweep option wanted — the checker is not the delinquent party —
  without a manual sweep obligation.

## Evidence Of Need

On 2026-08-29 this workstream itself violated invariant 1: commit `3873356`
removed three intake files without writing the log, and nothing mechanical
caught it — the correction is `df36750`, noticed only because a pending intake
item happened to describe the convention. The V1 readiness assessment's
standing finding says the same thing at scale: 258 tests guard the Python
distribution and nothing guards durable project memory.

## Routing

Product implementation in `devcapsule-src` (the CLI surface, the bootstrap
seeding) recorded as a coordination-backlog entry, unowned until picked up per
the 2026-08-29 unowned-rows ruling. It shares its delivery path with the
open initialization-tooling intake item — the same bootstrap that must learn
to seed the multiple-stream workflow is the one that would seed this config —
so whichever workstream picks up one should expect the other.
