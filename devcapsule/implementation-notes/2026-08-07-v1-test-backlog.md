# DevCapsule V1 Test Backlog

Status: open

This file collects valuable hardening tests that are not closure criteria for
the recursive-dogfood Stage 3 clone and contributor-bootstrap protocols. They
remain V1 work and should be implemented when the corresponding production
orchestration is introduced or changed.

## Owned Workspace And Manifest

- Reject collisions, symlinks, mount-boundary changes, and path escapes.
- Verify restrictive modes for run directories, manifests, logs, and evidence.
- Exercise atomic state transitions and interruption between every transition.
- Prove cleanup and repair affect only the exact ownership-marked run.
- Prove human and JSON output redact host paths and secret-bearing values.

## Local Clone Edge Cases

- Reject the wrong project and unsupported required submodules, LFS smudging,
  or checkout filters before materializing files.
- Add focused failures for dirty or untracked source, abbreviated revisions,
  shared object alternates, hard-linked objects, and corrupt object storage.
- Keep the filesystem-local clone independent of the developer's configured
  `origin` URL.

## Retry And Corruption

- Resume only when revision, interpreter, dependency inputs, and completed
  outputs still match.
- Reject or repair a partial venv, changed lock digest, corrupt Git object
  database, incomplete manifest, stale PEX, and wrong interpreter.
- Preserve sanitized diagnostics and provide one exact recovery command.

## Isolation Failures

- Prove bootstrap never falls back to the developer's venv, ambient site
  packages, personal pip configuration, private indexes, or credentials.
- Cover offline and dependency-download failures without weakening isolation.
- Verify negative PEX cases: unknown or mismatched revision, stale artifact,
  incorrect executable mode, and checksum mismatch.

## Closure Rule

An item leaves this backlog when a focused automated test covers the public
CLI or process boundary and passes the ordinary repository gate. These items
do not reopen completed Stage 3 unless a regression breaks its accepted E2Es.
