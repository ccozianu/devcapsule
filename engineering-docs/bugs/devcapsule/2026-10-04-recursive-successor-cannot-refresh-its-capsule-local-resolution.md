---
status: confirmed
severity: minor
target: 0.2.16
owner: maintenance
opened: 2026-10-04
requirements: [R-PRODUCT-001, R-COMPAT-001]
---

# The recursive successor cannot be launched: its capsule-local resolution is stale and nothing inside the capsule may refresh it

## Symptom

Inside this repository's own capsule (released 0.2.15, checkout
`devcapsule-2nd-home`, host Docker granted), the recursive dogfood's
`launch-successor` exits with status 2 before any launch:

```text
devcapsule: Local resolution is stale (manifest, platform-lock); run 'devcapsule project config resolve'.
```

The remedy it names is refused in the same capsule:

```text
$ devcapsule project --path /workspace/301e4208ef81-ChatGPT_Codex config resolve
devcapsule: This command needs launcher-owned configuration or state. Inside this capsule that
configuration is read-only. Run outside the capsule: devcapsule project --path /home/costin/... config resolve
```

Running it outside the capsule, as advised, does not help: it refreshes
the host's record, which is not the one the recursive launch reads.

Found on 2026-10-04 by the new end-to-end test
`tests/e2e/test_recursive_successor_attached_launch.py`, which failed fast
with the first message. The recursive preflight reports `ready: true` for
the same capsule, so the preflight does not cover this condition either.

## Expected behavior

`launch-successor` launches, or the preflight says why it cannot and names
a remedy that works where the operator is.

## Cause

Two rules that are each right on their own meet badly:

1. **Stage 5 isolates HOME for checkout-local configuration.** The recursive
   launch resolves the checkout through `fresh_resolved_project(checkout)`,
   which reads the checkout record and resolution under the capsule's own
   XDG configuration root, `/home/devcapsule/.config/devcapsule/projects/.../devcapsule/`.
   That copy was written on 2026-09-14 and is stale against the platform
   lock of 2026-09-27; `ExecutionConfiguration.load` refuses stale inputs
   and points at `config resolve`.
2. **Inside a capsule, mutating `project` commands are launcher-only.** The
   guard in `ProjectCommand.make_context` refuses `config resolve` whenever
   the project is the capsule's own, and the remedy it prints targets the
   host record, which the recursive flow never reads.

So the capsule-local copy can go stale and nothing is allowed to refresh
it. Before the guard existed (0.2.14), the operator refreshed it by hand;
since then the recursive dogfood has been unrunnable from a capsule whose
lock moved, and nobody ran it to notice.

## Fix options, for the owner's design review

- **A. The recursive launch resolves its own copy.** `launch_successor` calls
  `resolve_checkout(checkout)` under the isolated HOME before loading the
  resolution. The record it writes is the dogfood's own, in the capsule's
  home, not the launcher-owned host state the read-only rule protects; the
  guard stays as it is for users. One call, plus the preflight reporting
  staleness as a named check. This is the fix the agent proposed on
  2026-10-04; the owner asked for the record first.
- **B. The guard admits `config resolve` for the capsule-local copy** when
  the recursive environment variable is set. Wider than needed, and it
  reopens the question the 2026-09-24 inspection record settled.
- **C. The recursive launch reads the mounted read-only runtime context**
  instead of a capsule-local copy. The cleanest in principle, but it changes
  Stage 5's isolation and the plan the inspector compares against.

Option A is the recommendation. Whichever is chosen, the preflight gains a
check for a stale capsule-local resolution with the remedy that works.

## Verification target

`tests/e2e/test_recursive_successor_attached_launch.py` passes inside a
capsule whose lock moved after launch; `recursive-e2e preflight` names the
stale resolution before the fix and reports clean after it. Unit coverage
for the preflight check.

## Close criteria

The end-to-end test passes in this repository's capsule on a 0.2.16
candidate, and the 2026-08-15 detached-successor record closes on the same
run.
