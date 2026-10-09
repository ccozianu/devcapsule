# Local Workflow: DevCapsule

This file is the project's own half of the workflow. `WORKFLOW.md` binds
wherever it speaks. This file binds wherever `WORKFLOW.md` is silent. See topic
4.2 in `WORKFLOW.md`. The reasons for the rules below are in
[`WORKFLOW-LOCAL-humane.md`](WORKFLOW-LOCAL-humane.md), which is *for humans*.

DevCapsule develops the generic definition. Its root `WORKFLOW.md` is the
source of the packaged one, not an installed copy. See *Exceptions*.

## Integration Branch

`main`.

## Version Scheme

1. Versions follow PEP 440.
2. Between releases the source carries `X.Y.Z.dev0`, the development form of
   the release it works toward. The suffix stays `dev0`.
3. The release branch's first commit sets the release version `X.Y.Z`, or
   confirms it when the product owner has already set it.
4. After the final tag, `main` reopens with the next development version: the
   next patch, unless the owner names another.
5. Candidate builds are stamped `X.Y.ZrcN` from their tags. Local builds carry
   a local marker. Never author either in the source.
6. The single authored copy is `[project] version` in
   `devcapsule-src/pyproject.toml`. The frontmatter of `WORKFLOW.md` and of the
   packaged definition mirror it.
7. Set all three with one command, from `devcapsule-src`:

   ```text
   .venv/bin/python -m nox -s bump -- <major|minor|patch|X.Y.Z[.devN]>
   ```

8. `nox -s build` checks that the copies agree.

## Release Policy

1. The [operator guide for releasing a new version](engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md),
   owned by `project-management`, is the release policy.
2. Refs use the default spelling: `release-X.Y.Z`, `vX.Y.Z-rcN`, `vX.Y.Z`.
3. GitHub Actions builds and publishes candidates.
4. Each candidate is gated on a resolved main disposition: ancestry, patch
   equivalence, or the documented evidence record the guide describes.
5. Acceptance requires downloaded-artifact smoke evidence.
6. The acceptance record lives under `engineering-docs/releases/`.
7. Since 2026-09-28 a release includes its documentation. The guide's
   *Documentation Is Part Of The Release* names the obligations. Documentation
   is published per [the content–website contract, version 1](engineering-docs/specifications/product/content-website-contract.md).
   `docs/versions.yaml` on `main` is the authored list of documented versions.
   Promote it after every final tag.

## Documentation Refs

Owner grant of 2026-09-28, exercised by `project-management`.

1. The project declares one ref kind of its own: `docs-<version>`.
2. Fork a `docs-<version>` branch from the final tag `v<version>`.
3. Commit only documentation changes to it: changes under `docs/` and nothing
   else.
4. Never merge it anywhere. Never rebase it.
5. Name it in `docs/versions.yaml` as that version's `source` for as long as
   it exists. Without it, the version's source is its final tag.
6. The candidate gate does not apply to it. The website's build check does.
7. Anyone may commit to it on the owner's or `project-management`'s direction.
   `user-docs` normally authors the corrections.

## Blog Entries

When the human says "write a blog entry on topic X":

1. Create `engineering-docs/blog/YYYY-MM-DD-short-topic.md`. Use the date of
   writing. The website reads the date from the filename.
2. Begin with the front matter block the blog README describes: `description`
   and, until the owner releases the entry, `draft: true`. Then `# Title` and
   plain Markdown prose. Use existing entries as examples. Add no other
   website markup.
3. Attribute quoted material. Identify any editing of quotations. Link
   repository evidence by a mainline commit SHA.
4. Add the entry to `engineering-docs/blog/README.md` and to root `index.md`.

The website picks up these files. Its [publishing instructions](website/PUBLISHING.md)
define deployment. There is no blog proposal, schedule, or approval procedure.

## Validation Commands

Every command runs from `devcapsule-src`. The environment is the virtual
environment under `devcapsule-src/.venv`. `nox`, `pytest`, `mypy`, and the
package's dependencies live there and nowhere else on the machine, inside a
capsule as well as on a host. The kinds are the definition's; see *Validation*
in [`INFORMATION-MODEL.md`](devcapsule-src/devcapsule/assets/project_workflow/definition/INFORMATION-MODEL.md).

- **Environment**: if `.venv` is absent, create it:

  ```text
  cd devcapsule-src
  python3.12 -m venv .venv
  .venv/bin/python -m pip install -r dev-requirements.txt
  .venv/bin/python -m pip install -e . --no-deps
  ```

  Inside a capsule `/tmp` is a 2 GB tmpfs that the gate's scratch overflows.
  Run with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest"` or
  another directory with room.
- **Unit tests**: `.venv/bin/python -m nox -s tests`, with coverage. One
  module while working: `.venv/bin/python -m pytest -q tests/<module>.py`.
  See [unit tests](engineering-docs/development/unit-tests.md).
- **Integration tests**: `.venv/bin/python -m nox -s integration`. It runs
  the built executable and subprocesses without Docker. `nox -s typecheck`
  and `nox -s docs-contract` are integration checks too. See
  [integration tests](engineering-docs/development/integration-tests.md).
- **End-to-end tests**: `.venv/bin/python -m nox -s e2e`, plus
  `pex_clean_machine`, `recursive_dogfood_e2e`, and `ide-smoke`. Each needs
  Docker and is opt-in. Evidence lands under
  `devcapsule-src/dist/e2e-evidence/`. See
  [end-to-end tests](engineering-docs/development/e2e-tests.md).
- **Smoke test**: `.venv/bin/python -m nox -s smoke` starts the built
  executable and proves its commands answer. `nox -s ide-smoke` launches each
  IDE surface in a fresh project and proves from the outside that the IDE
  comes alive: the desktop URL answers and the IDE owns a window.
  Rider: `nox -s ide-smoke -- --display --surface rider --component-browser`
  builds and runs a package-free C# fixture with the selected SDK and retains
  noVNC pixels. `--agent` additionally requires a saved edit and visual
  recognition. It fails if Rider licensing prevents editor access.
  Eclipse: `nox -s ide-smoke -- --agent --surface eclipse --component-browser`
  requires a noVNC editor save, checks the saved file independently, and keeps
  the Playwright movie. Use `--display` instead of `--agent` for startup only.
- **Gate**: `.venv/bin/python -m nox -s build`, before a checkpoint and
  before integration: distribution version, Python and shell syntax, type
  check, unit tests, CLI smoke, the executable built and smoked, packaging
  tests, the documentation contract. The end-to-end suites are not in it. The
  [developer brief](DEVELOPING.md) says when they run.

## Reasoning And Code Navigation

1. Start with the behavior's contract: ownership, inputs, preconditions,
   invariants, and postconditions.
2. State what is known and the specific uncertainty the next code read must
   resolve.
3. Navigate from the responsible entry point through its types, imports, and
   calls. Read enough surrounding implementation to understand the behavior.
   Use direct file navigation and exact-name lookup.
4. Use regular-expression searches only as a last resort, when reasoned
   navigation and literal lookup cannot locate the implementation. Explain
   that gap before searching.
5. A search match is a navigation aid. It is never evidence that a contract is
   satisfied. Do not substitute repeated pattern searches for reasoning.

## Component Status Publication Ref

1. `component-status` is a project-owned generated publication branch.
2. The `component-status.yml` action may create it and advance it by
   fast-forward commits that contain the compatibility feed and the
   GitHub-rendered status page.
3. Never select it as an editing workstream. Never merge it into `main`. Never
   force-push it.
4. Authored policy and implementation follow ordinary workstream PR delivery.
   See [service operations](component-status/README.md).

## Host Capabilities

1. The `[host.*]` tables in `.devcapsule/devcapsule.toml` declare what this
   checkout needs from the machine, each with its justification: the Docker
   socket, to run peer DevCapsule instances during the full test suite; host
   networking, for host-bound development services; development sudo.
2. The *Coordination Baseline* in root `CURRENT-STATUS.md` records the hosting
   facts: the canonical repository and owner-operated pull-request delivery.
3. The GitHub integration rules below govern agent access and the UI handoff.

### Dogfooding CLI Selection

Owner direction, 2026-09-24.

1. This project's configuration recommends
   `runtime.devcapsule-command = "devcapsule0"`.
2. A newly materialized development capsule exposes the shipped runtime as
   `devcapsule0` and leaves `devcapsule` for the development installation.
3. Use the shipped command deliberately when testing its released behavior.
   Use the development CLI or an explicit built PEX for current work.
4. Do not fall back silently to the shipped CLI when development setup is
   missing.
5. Other projects keep the standard command unless they opt into this
   exception. See `DEVELOPING.md` for checkout overrides and resolution.

### Keep The Development Checkout Launchable

Owner correction, 2026-10-05: be liberal in what we accept and conservative in
what we produce. Compatibility is a contract between contributors with
different launchers. It is not a rule that one frozen release must understand
every shared declaration. This supersedes the narrower 2026-10-04 rule.

1. DevCapsule commands are the only writers of this project's configuration:
   the shared manifest, platform locks, checkout configuration, and generated
   resolutions. Do not edit them with an editor, a script, a TOML library, or
   Git-file restoration. Use the DevCapsule command. Add a supported command
   when the operation is missing. Keep manifest, locks, and resolutions
   consistent through that operation. This rule covers the working project,
   not test fixtures.
2. Before any configuration change, identify the writing executable. Run
   configuration validation with at least `devcapsule0` from the running
   instance. Record its path, `version --json`, the validation command, and
   the result.
3. Check the proposed result before you apply it to the working project. Then
   validate the written result.
4. Also validate against the intended next-launch host executable when it is
   available. The in-capsule check is a minimum. It does not prove which
   executable the host will use.
5. Do not substitute validation with the code under development alone.
6. An inspection command is not automatically a validator. In the current
   runtime, `devcapsule0 project config list` reports recorded launcher
   configuration, and `config resolve` writes a resolution and requires the
   launcher context. Neither is a read-only candidate validation inside the
   capsule.
7. If the required validation or mutation operation is absent, implement it
   through the owning workstream before changing the working configuration.
   Record the gap. Do not bypass it with direct file edits. Do not call an
   inspection a successful check.
8. Self-hosting is a managed exception. DevCapsule may develop inside
   DevCapsule with a newer development executable. Keep the known working
   `devcapsule0` baseline identifiable. Validate the transition with it.
   Record any compatibility gap and the explicit development-build exception.
   Retain an independent host restart and recovery path. A development build
   must not validate away its own bootstrap dependency or replace the user's
   host launcher.
9. For 0.3, [R-CONFIG-001](engineering-docs/requirements/product/r-config-001-conservative-writers-tolerant-readers.md)
   requires mandatory needs to be distinguished from optional enhancements. An
   unavailable optional capability produces a warning and a usable reduced
   local environment. An unmet mandatory need produces an actionable refusal.
   Degradation preserves the shared declaration and the guarantees of
   mandatory capabilities. Conservative writers preserve unrelated choices and
   compatible representations. This applies to adopter repositories that
   receive newer contributions, not only to self-hosting. Until that behavior
   is implemented, keep the current required-only checkout compatible. The
   existing vocabulary guards are an interim regression defense.

### Local Launch Networking

Owner direction, 2026-09-24.

1. Always use host networking for this project's local development and
   release-validation launches, including launches from inside a DevCapsule:
   the RC runner's `--network host`, or
   `devcapsule project run --authorize network host`.
2. This is standing authorization for those launches. Do not ask for it
   repeatedly.
3. Prefer the run-once option over rewriting a checkout's saved configuration.
4. A test that exercises bridge networking, denied host access, or network
   isolation keeps its declared network mode.
5. If host networking cannot be used, record the concrete reason and the
   fallback. Do not substitute bridge networking silently.
6. This is a local operating rule, not a change to product defaults or to
   other projects' permissions.

## GitHub Integration: Owner Through The UI

Owner direction, 2026-09-21.

1. Agents use ordinary Git operations with the configured SSH remote for fetch
   and workstream-branch delivery.
2. The `gh` CLI is not an available integration tool. The owner performs all
   other GitHub integration through the GitHub UI: opening, updating, and
   merging pull requests; dispatching workflows; changing repository or
   publication settings.
3. Do not probe `gh` availability or connector credentials. Do not attempt
   API-based integration as part of delivery, even if a connector or API
   appears available.
4. Prepare and validate the change. Commit and push the workstream branch over
   SSH. Give the owner a concise UI handoff.
5. Do not substitute a direct push to `main` for owner PR integration.
6. Re-verify `main` through an SSH fetch after the owner reports the merge.
7. Keep this rule until the owner explicitly changes it.

## Commit Authorship

Owner direction, 2026-09-22.

1. A commit made with an agent keeps the human's Git author identity and adds
   a `Co-authored-by` trailer for the contributing agent. Pushing credentials
   and the person who merges a PR do not replace commit authorship.
2. Before committing, check `git var GIT_AUTHOR_IDENT`. Use the human's
   intended name and GitHub-associated email, not an inherited container
   placeholder. Set checkout-specific corrections with
   `git config --local user.name` and `git config --local user.email`.
3. For Codex, the co-author display name is the actual model name followed by
   `Codex`, with this project's attribution address `noreply@openai.com`:

   ```text
   Co-authored-by: GPT-6 Astra Codex <noreply@openai.com>
   ```

   That is an example, not a model pin. Read the active session's model
   identity. Do not infer it from a configured default or a prior session. If
   the model cannot be established, ask the human for the displayed model.
4. Credit only agents that contributed.
5. Separate trailers from the message body with a blank line. Verify the saved
   commit's author and trailers before pushing. Preserve trailers when
   composing a squash commit.
6. This applies to future commits. Do not rewrite merged history to add
   attribution.

## Integration Method

Merge commits, as the definition prescribes since 2026-10-03: one merge per
reviewed deliverable, `main` read by first parent, pushed branches synchronized
by merging `main` in. The hosting platform's merge method is set accordingly.
The earlier ruling that `ws-workflow-improvements/v1` rebases onto `main` is
retired. That branch merges like the others. The engineering source is
[merge strategy and commit identity](engineering-docs/implementation-notes/workflow/2026-08-17-merge-strategy-and-commit-identity.md).

## Workflow Definition Changes

Owner direction, 2026-10-09, after the controlled-language edition merged.

1. Every change to `WORKFLOW.md` or to this file follows the same scheme as
   that edition: one rule per sentence, imperative, at about 80% ASD-STE100,
   placed in the topic the rule belongs to.
2. Put no reason, example, or history in the rule file. Put them in the humane
   companion, `WORKFLOW-humane.md` or `WORKFLOW-LOCAL-humane.md`, in the
   section with the same number or name, as a paragraph that repeats the
   rule, states its intended effect, and gives its motivation.
3. Change the rule and its companion paragraph in the same commit. A rule
   without a companion paragraph, or a paragraph without a rule, is a defect.
4. Add or amend the *Unreleased* entry under `### Changes` in `WORKFLOW.md`
   for every rule that changes meaning. Keep the entry's bold-title form, which
   the brief parses.
5. Keep the frontmatter and the `## Validation Commands` heading as the
   tooling expects them.
6. Regenerate the packaged definition under
   `devcapsule-src/devcapsule/assets/project_workflow/definition/` from the
   root files when a release is cut, or earlier on `workflow-improvements`'
   decision.
7. Use the section map at the end of `WORKFLOW-humane.md` when a record cites
   a section name from before this edition. Do not rewrite old records.

## Exceptions

- **Release-fix propagation uses engineering judgment.** Owner direction,
  2026-09-22. It supersedes the generic release rule's blanket merge-only and
  no-cherry-pick restrictions. `main` stays open to other workstreams. Merge a
  release fix when that produces a correct result on `main` without holding
  unrelated work back. Otherwise cherry-pick it, adapt its reasoning to
  `main`'s implementation, or establish with evidence that `main` does not
  have the bug. A conflict alone does not prove that merging is unsuitable.
  Ancestry alone does not prove that the fix works. Record the main
  disposition and its evidence with the bug. Routine method selection needs no
  new owner approval. The
  [release runbook](engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)
  describes the gate's evidence paths. Ends when the generic definition
  incorporates this decision; its revision is routed to
  workflow-improvements.
- **The root `WORKFLOW.md` is the source, not an installed copy.** The
  packaged definition under
  `devcapsule-src/devcapsule/assets/project_workflow/definition/` is derived
  from it and need not be byte-identical. The asset README says which
  differences are justified. Ends if the definition is extracted to its own
  repository.
- **Two adoption exceptions in the registry.** `project-management` started
  one day after the mode was initialized. `maintenance` was created on
  2026-09-18 under the adoption exception the definition provides. Both are
  recorded in root `CURRENT-STATUS.md`. Neither ends.
- **Branch names outside the `ws-` vocabulary.** Open workstreams registered
  before 2026-09-18 keep their old branch names until they rename them. Owner
  direction, 2026-09-22, defers the former pre-candidate deadline through the
  0.2.14 release: publish 0.2.14, then complete the migration before
  substantive work on the next release. RC0 and later 0.2.14 candidates are
  not held for it. Each workstream owns its rename. Ends when the renames are
  complete.
