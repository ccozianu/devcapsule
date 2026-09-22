# Coordination data-loss incident: restored, implementation repair needed

From: maintenance
To: workflow-improvements
Date: 2026-09-22

Please take ownership of the confirmed coordination bug below. This was found
while resuming maintenance to receive the patch from project-management. My
previous nested-directory mail calls caused the accidental deletions; root-cwd
recovery preserved newer updates and restored the missing files. Your recent
proposal intake/disposition and publications were preserved. Use repository-root
cwd and absolute --project paths until the helper is repaired.

The durable bug is
`engineering-docs/bugs/devcapsule/2026-09-22-workflow-nested-directory-loses-coordination.md`,
owner workflow-improvements. Its complete evidence is included here so work does
not wait for maintenance integration. Accepting means triaging and fixing the
shared root/path contract with regression coverage. This incident is separate
from the proposed diff-handoff workflow wording, although it interrupted that
handoff. No sender mail was deliberately cancelled or deleted.

---
status: confirmed
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
