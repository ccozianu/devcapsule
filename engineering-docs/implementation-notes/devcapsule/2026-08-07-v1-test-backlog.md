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

## `devcapsule project run` Interface And Documentation

- Inventory every current and intended `devcapsule project run` command-line
  parameter, including its type, default, safe default, source of truth,
  precedence, persistence, validation, conflicts, and effect on the generated
  runtime and Docker plans.
- Reconcile the implementation with D-0001 and the state-and-persistence
  specification. In particular, distinguish ordinary run-once values,
  checkout-owned bindings, explicit host-access authorization, restrictive
  workstation policy, recovery-only `run-image` options, and internal
  recursive-E2E controls.
- Correct any option that can grant Docker, network, sudo, filesystem, secret,
  or other host access beyond the resolved checkout authorization or a
  restrictive workstation policy. `--force` must never become an authorization
  bypass.
- Review option symmetry and composability: enabling and disabling forms,
  conflict detection, safe downgrade behavior, the absence of ambient grants,
  and whether missing generic run-once value or binding syntax should be added
  or deliberately rejected.
- Define and test the exact overlay order among workstation configuration,
  committed project declaration, checkout configuration, generated resolution,
  and run-once arguments. Tests must cover both escalation attempts and
  deliberate least-privilege downgrades through the public CLI and final Docker
  plan.
- Review human and JSON output so every effective deviation is conspicuous,
  security-sensitive choices are summarized without exposing secrets or host
  paths, and users can inspect the final plan before launch where appropriate.
- After corrections are accepted, publish high-quality user documentation for
  `devcapsule project run`. It must document every supported parameter, defaults
  and precedence, persistent versus run-once behavior, authorization and policy
  boundaries, incompatible combinations, security implications, common
  examples, safe least-privilege recipes, troubleshooting, and the distinct
  roles of `project run`, `run-image`, and recursive-E2E engineering commands.
- Add a documentation conformance check so CLI help, examples, and the
  implemented option inventory cannot silently drift apart.

## Closure Rule

An item leaves this backlog when a focused automated test covers the public
CLI or process boundary and passes the ordinary repository gate. These items
do not reopen completed Stage 3 unless a regression breaks its accepted E2Es.
