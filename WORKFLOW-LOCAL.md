# Local Workflow: DevCapsule

This is the project's own half of the workflow. `WORKFLOW.md` beside it is the
generic definition and binds wherever it speaks; this file governs wherever it
is silent. See *The Project's Local Workflow* in `WORKFLOW.md`.

DevCapsule is also the project that develops the generic definition, so its
root `WORKFLOW.md` is the source of the packaged one rather than an installed
copy. That is recorded under *Exceptions* below; everything else here is what
any adopting project would record.

## Version Scheme

PEP 440. Between releases the source carries the development form of the
release it works toward, `X.Y.Z.dev0`, as pip and NumPy carry on their main
branches; the suffix stays `dev0`, since the commit identifies the build. The
release branch's first commit sets the release version `X.Y.Z`, or confirms
it when the product owner has already set it. After the final tag, `main`
reopens with the next development version, the next patch unless the owner
names another. Candidate builds are stamped `X.Y.ZrcN` from their tags and
local builds carry a local marker; neither is ever authored in the source.

The single authored copy is `[project] version` in `devcapsule-src/pyproject.toml`.
The frontmatter of `WORKFLOW.md` and of the packaged definition mirror it.
The command that sets all three, run from `devcapsule-src`:

```text
.venv/bin/python -m nox -s bump -- <major|minor|patch|X.Y.Z[.devN]>
```

`nox -s build` runs the check that the copies agree.

## Release Policy

The [operator guide for releasing a new version](engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md),
owned by `project-management`, is this project's release policy. It uses the
default ref spelling, `release-X.Y.Z` with `vX.Y.Z-rcN` and `vX.Y.Z` tags;
builds and publishes candidates through GitHub Actions; gates each candidate
on mainline integration by ancestry, with a documented exception record for a
maintenance release that cannot merge; requires downloaded-artifact smoke
evidence for acceptance; and keeps the acceptance record under
`engineering-docs/releases/`.

## Validation Commands

`nox -s build` from `devcapsule-src` is the local gate before a checkpoint
and before integration. The [developer brief](DEVELOPING.md) describes the
environment, the individual sessions, and the host-sensitive end-to-end runs
that are not part of the gate.

## Host Capabilities

The `[host.*]` tables in `.devcapsule/devcapsule.toml` declare what this
checkout needs from the machine, each with its justification: the Docker
socket to run peer DevCapsule instances during the full test suite, host
networking for host-bound development services, and development sudo. The
*Coordination Baseline* in root `CURRENT-STATUS.md` records the hosting
facts: the canonical repository, and that pull requests are opened and
merged by the product owner because the agent environment has no GitHub API
access.

## Exceptions

- **The root `WORKFLOW.md` is the source, not an installed copy.** The
  packaged definition under `devcapsule-src/devcapsule/assets/project_workflow/definition/`
  is derived from it and need not be byte-identical; the asset README says
  which differences are justified. Ends if the definition is ever extracted
  to its own repository.
- **Two adoption exceptions in the registry.** `project-management` started
  one day after the mode was initialized, and `maintenance` was created on
  2026-09-18 under the adoption exception the definition provides. Both are
  recorded in root `CURRENT-STATUS.md`. Neither ends.
- **Branch names outside the `ws-` vocabulary.** Open workstreams registered
  before 2026-09-18 keep their old branch names until they rename them, which
  each does before the next release candidate is tagged. Ends then.
