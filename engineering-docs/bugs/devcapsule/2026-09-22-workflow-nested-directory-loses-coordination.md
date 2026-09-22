---
status: fixed
severity: untriaged
target: none
owner: workflow-improvements
opened: 2026-09-22
requirements: [R-PRODUCT-006]
---

# Nested-directory coordination commands discard unrelated files

## Symptom and evidence

Running workflow mail commands from `devcapsule-src/` with the default project
path reported successful delivery but omitted unrelated files from the next
coordination tree. The source was main `20336d8`; the sender checkout was on
project-management. Commit `93d794a41882` delivered the maintenance patch but
removed 20 unrelated files. `f0b43c6da0c8` delivered the workflow proposal but
removed that maintenance patch. Neither operation was a recipient taking mail.
The problem was discovered when maintenance resumed and found an empty mailbox.

The mail content survived in Git history. Recovery commit `0bf1bc785774` added
back 16 still-missing files from the destructive commits' parents, preserving
all newer published state and the legitimate taking of the workflow proposal.
The explicitly released project-management claim was not restored. Maintenance
then took both restored messages normally and committed them at `6c6f08f`.
No coordination reset or force-push was used for recovery.

## Contract and cause

Sending one message must preserve every other mailbox, published state and claim.
In `workflow_coordination.py`, `_Git` uses the supplied directory as Git's cwd.
`_tree_entries` calls `git ls-tree -r -z COMMIT` without `--full-tree`, so Git
limits the result to the current subdirectory. The sender rebuilds and pushes a
tree from that incomplete listing. This also threatens publish, take and claim
operations that share the helper. This causal trace is implementation evidence;
the two mail commits above are the observed destructive executions.

A related observed failure: `workflow publish --project ..` from devcapsule-src
finds the workstream but passes a relative file path to `hash-object` with another
cwd, producing a missing-file error. Root/path normalization needs a coherent
contract across read and mutation operations, not only a patched mail command.

## Workaround and verification target

Until repaired, execute coordination commands from the repository root and use
an absolute `--project` path. Do not reproduce against the shared remote. Test
with disposable local bare remotes: send/take/publish/claim from nested and
relative project paths, asserting unrelated mail/state/claims remain byte-identical
and that the intended operation alone changes the tree. Check retries too.

Workflow-improvements owns the implementation. Severity and release targeting
remain its triage decision; restoration of this incident is not a code fix.

## Fix

Fixed 2026-09-22 on `ws-workflow-improvements/nested-cwd-fix`: `_Git` resolves the
repository top level from any directory and runs every command there; the
tree listing is `--full-tree`; `publish` and `take` locate the workstream
directory from that top level. A regression test sends, publishes, claims, and
takes from a nested directory against a bare remote and asserts every
pre-existing entry survives. Validation pending: the owner's next session from
a nested directory against the shared remote, or the release candidate.
