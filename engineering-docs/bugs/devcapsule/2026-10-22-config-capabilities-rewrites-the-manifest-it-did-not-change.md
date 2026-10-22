---
status: confirmed
severity: minor
target: none
owner: maintenance
opened: 2026-10-22
requirements: [R-CONFIG-001, R-COMPAT-001]
---

# `config capabilities` rewrites the manifest it did not change

## Symptom

On 2026-10-22, regenerating this repository's shared lock on a fresh clone
of `release-0.3.0` with

```text
devcapsule project --path <clone> config capabilities --required antigravity-agent claude-code-agent codex-agent docker-cli python python-ide
```

wrote the lock as intended, on matrix embedded-27, and also rewrote
`.devcapsule/devcapsule.toml` although the capability set it was given was
the one the manifest already declared. The rewrite serialized the whole
manifest in canonical quoted-key TOML, dropped every comment, including the
block explaining the `runtime.devcapsule-command` recommendation, reordered
the tables, and replaced `[capabilities] need = […]` with `required = […]`
and `optional = []`.

## Cause

Not yet read in the implementation; the observation is of the command's
output on the clone, whose `git diff` shows the whole-file rewrite. The
lock's capabilities digest did not change, so the command had nothing new
to say about the manifest.

## Why it matters

- [R-CONFIG-001](../requirements/product/r-config-001-conservative-writers-tolerant-readers.md):
  a writer is conservative; a manifest that did not change is not written.
- The vocabulary change shuts older clients out: the released 0.2.15 reads
  `need`; a shared checkout rewritten to `required` by one contributor's
  newer launcher stops launching for the others, the failure
  [R-COMPAT-001](../requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md)
  forbids and the shared-checkout rule in `WORKFLOW-LOCAL.md` guards.
- The comments are the humans' part of the file; a command that drops
  them is editing what it does not own.

## Expected

`config capabilities` writes the manifest only when the declared set
changes, and then edits the capability table in place, keeping the file's
comments, order and spelling; it writes `required`/`optional` only when
the set given needs the distinction, and says so, since that is a
vocabulary an older client cannot read. The lock is written whenever the
matrix or the set changed, as now.

## Verification target

A unit test: `config capabilities` with the set the manifest already
declares leaves the manifest byte-identical and writes the lock; with a
changed set it edits the table in place and keeps every comment.

## Close criteria

The test passes on a release; the owner's requirement item of the same
day, configuration files declaring their minimum DevCapsule, decides how
the vocabulary change is announced to older clients.
