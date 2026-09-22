# Local Workflow: DevCapsule

This is the project's own half of the workflow. `WORKFLOW.md` beside it is the
generic definition and binds wherever it speaks; this file governs wherever it
is silent. See *The Project's Local Workflow* in `WORKFLOW.md`.

DevCapsule is also the project that develops the generic definition, so its
root `WORKFLOW.md` is the source of the packaged one rather than an installed
copy. That is recorded under *Exceptions* below; everything else here is what
any adopting project would record.

## Integration Branch

`main`, as the definition assumes.

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

## Blog Entries

When the human says "write a blog entry on topic X", write it:

- Create `engineering-docs/blog/YYYY-MM-DD-short-topic.md` in the flat blog
  directory. Use the date of writing; the website reads the date from the filename.
- Start with `# Title`, then plain Markdown prose. Use existing entries as
  examples. No frontmatter or website-specific markup is needed.
- Attribute quoted material and identify any editing of quotations. For links
  to repository evidence, use a mainline commit SHA so the reference stays stable.
- Add the entry to `engineering-docs/blog/README.md` and root `index.md`.

The website picks up these files. Its [publishing instructions](website/PUBLISHING.md)
define deployment. The human's request supplies the topic and occasion; there
is no separate blog proposal, schedule, or approval procedure. These instructions
are local to DevCapsule.

## Validation Commands

`nox -s build` from `devcapsule-src` is the local gate before a checkpoint
and before integration. The [developer brief](DEVELOPING.md) describes the
environment, the individual sessions, and the host-sensitive end-to-end runs
that are not part of the gate.

## Reasoning And Code Navigation

Start with the behavior's contract: ownership, inputs, preconditions, invariants
and postconditions. State what is known and the specific uncertainty the next
code read must resolve. Navigate from the responsible entry point through its
types, imports and calls, reading enough surrounding implementation to understand
the behavior. Use direct file navigation and exact-name lookup where needed.

Use regular-expression searches only as a last resort, when reasoned navigation
and literal lookup cannot locate the relevant implementation. Explain that gap
before searching. Search matches are navigation aids, never evidence that a
contract is satisfied; do not substitute repeated pattern searches for reasoning.

## Component Status Publication Ref

`component-status` is a project-owned generated publication branch. The
`component-status.yml` action may create and advance it through fast-forward
commits containing the compatibility feed and GitHub-rendered status page.
It is never selected as an editing workstream, merged into main, or force-pushed.
Authored policy and implementation follow ordinary workstream PR delivery.
See [service operations](component-status/README.md).

## Host Capabilities

The `[host.*]` tables in `.devcapsule/devcapsule.toml` declare what this
checkout needs from the machine, each with its justification: the Docker
socket to run peer DevCapsule instances during the full test suite, host
networking for host-bound development services, and development sudo. The
*Coordination Baseline* in root `CURRENT-STATUS.md` records the hosting
facts: the canonical repository and owner-operated pull-request delivery.
The GitHub integration rules below govern agent access and the UI handoff.

## GitHub Integration: Owner Through The UI

Owner direction, 2026-09-21: agents use ordinary Git operations with the
configured SSH remote for fetch and workstream-branch delivery. The `gh` CLI
is not an available integration tool. All other GitHub integration is performed
by the owner through the GitHub UI: opening/updating/merging pull requests,
dispatching workflows, and changing repository or publication settings.

This is the working arrangement even if a GitHub connector or API appears
available. Do not probe `gh` availability or connector credentials, or attempt
API-based integration, as part of delivery. Prepare and validate the concrete
change, commit and push the workstream branch over SSH, then give the owner a
concise UI handoff. A request to publish or integrate work follows this arrangement
unless the owner explicitly changes it. Do not substitute a direct push to main
for owner PR integration. Re-verify main through an SSH fetch after the owner
reports the merge. Keep this rule until the owner explicitly changes it.

## Commit Authorship

Owner direction, 2026-09-22: commits made with an agent retain the human's Git
author identity and add a `Co-authored-by` trailer for the contributing agent.
Pushing credentials and the person merging a PR do not replace commit authorship.
Before committing, check `git var GIT_AUTHOR_IDENT`; use the human's intended
name and GitHub-associated email, not an inherited container placeholder. Set
checkout-specific corrections with `git config --local user.name` and
`git config --local user.email`, leaving other developers' identities alone.

For Codex, the co-author display name is the actual model name followed by
`Codex`, using this project's attribution address `noreply@openai.com`:

```text
Co-authored-by: GPT-6 Astra Codex <noreply@openai.com>
```

That is an example, not a model pin. Read the active session's model identity;
do not infer it solely from a configured default or copy a prior session's name.
If the actual model cannot be established, ask the human for the displayed model
before claiming a specific identity. Credit only agents that contributed.
Separate trailers from the message body with a blank line and verify the saved
commit's author and trailers before pushing. Preserve trailers when composing a
squash commit. This applies to future commits; do not rewrite merged history to
add attribution. No change to SSH credentials or PR merge permissions is needed.

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
