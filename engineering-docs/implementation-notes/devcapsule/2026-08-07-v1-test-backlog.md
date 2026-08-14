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

## Authorization-Negative Launch Plan

This obligation was explicitly transferred from recursive-dogfood Stage 5 when
the product owner accepted that stage as complete on 2026-08-12. Its absence
does not reopen Stage 5.

- Create a separate run-owned checkout configuration and fresh resolution that
  retain only the base-image and Claude Code acquisition authorizations needed
  for materialization while omitting Docker-daemon, host-network, and
  development-sudo grants.
- Through the public project-run planning boundary, prove that absence of those
  grants yields bridge networking, no host Docker socket or `DOCKER_HOST`, no
  development-sudo group or policy, and no equivalent privilege escalation.
- Exercise a small non-GUI container probe against the resulting plan; a second
  PyCharm GUI launch is not required.
- Contrast this absence-of-authorization result with the explicit
  `--no-recursive-e2e` least-privilege downgrade. The latter is useful coverage
  but is not sufficient evidence for the former.
- Preserve sanitized plan/probe evidence and cover the behavior with focused
  public-CLI tests in the ordinary repository gate.

## Modest Sample-Project Experience Improvements

Requested by the product owner on 2026-08-14 after the first sample project.
A full service-dependency model is explicitly **out of scope for V1**: it would
expand implementation, verification, and automated testing considerably. V1
instead assumes a sample may rely on a database the developer already runs, or
on documented instructions for starting one in a container, and may reasonably
assume host networking. This item collects the smaller changes that would
measurably improve that experience without building a service model.

- Decide what a project may state about services it expects without DevCapsule
  managing them, so a developer reads one declaration instead of prose. Even a
  documented, non-enforced declaration is useful.
- Give samples a supported way to express required host ports, or a convention
  that avoids collisions. The first sample collided immediately with an
  unrelated PostgreSQL already listening on the host's port 5432.
- Provide a documented least-privilege alternative to host networking for
  samples that only need a database and a browser-reachable dev server, so the
  host-network recommendation is a convenience rather than the only route.
- Assess which further redistributable clients or tools belong in the base by
  the same reasoning applied to `postgresql-client`, and which should stay out.
- Add a check that a sample's `.devcapsule` declaration and lock resolve
  through the public CLI, so a sample cannot silently rot as the schema evolves.

Each accepted item leaves this backlog under the closure rule below.

## Mainline Change Propagation To The Remote Repository

Requested by the product owner on 2026-08-14 while registering the
`sample-projects` workstream. Today the mechanism by which project changes on
`main` reach the canonical remote is conventional rather than specified, and it
has repeatedly become a coordination cost: agent environments have lacked
publication credentials, local `main` has diverged from `origin/main` while
already-merged commits survived locally under different SHAs, and workstream
registration depends on a `main` commit that the agent may be unable to publish.

- Specify how a change committed on `main` is expected to reach the canonical
  remote, including whether direct push or a pull request is authoritative, and
  who performs it when the working environment holds no publication credential.
- Specify how a stale or diverged local `main` is detected and reconciled
  without discarding unpublished work, distinguishing commits already merged
  upstream by content from genuinely unpublished ones.
- Specify how a workstream's immutable start date is determined when its
  registration commit reaches `main` later than it was authored.
- Extend the rule to submodule pointers: define when a parent-repository
  pointer update may be committed relative to publishing the corresponding
  sample-repository commit, so `main` never advertises an unreachable pointer.
- Implement whatever check or tooling the specification requires, and verify it
  with a focused automated check in the ordinary repository gate.

## Closure Rule

An item leaves this backlog when a focused automated test covers the public
CLI or process boundary and passes the ordinary repository gate. These items
do not reopen an explicitly completed milestone stage unless a regression
breaks that stage's accepted evidence.
