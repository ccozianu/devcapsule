# Implementation brief for the Codex + gpt-6-astra pair: slice 1 of the capabilities and components work order

The roles are swapped from the rc4 reviews. You implement; Claude Fable 5.1 reviews, with the owner, Costin Cozianu, who merges. The work order is `engineering-docs/work-orders/2026-10-24-capabilities-and-components.md`, merged into `release-0.3.0` by the owner; it is the specification, and its Part 1 rulings and Part 5 decisions are settled. Where the order is silent, choose the smallest thing that keeps every Part 6 care point, and say what you chose in the PR body. Do not reopen the model.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-impl-1, on the branch `ws-maintenance/capabilities-1-model`, branched from `release-0.3.0` at the merge of the work order. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any other `/home/devcapsule/worktrees/*` worktree.

Read first, in this order: `AGENTS.md`; `WORKFLOW.md` topic 9.11; `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout*, *GitHub Integration*, *Validation Commands*); the work order, all of it, Part 6 twice; `engineering-docs/decisions/product/d-0014-entry-point-generalizes-the-ide-role.md` (tabled: the IDE owns the container's lifetime and uses the display; do not rename it); R-CONFIG-001 under `engineering-docs/requirements/product/`; then `devcapsule/resolution_matrix.py` (the catalog: `surface_capabilities`, `ancillary_capabilities`, `local_capabilities`, `sdk_major`, the base pins' `satisfies` and `sdk_majors`), `devcapsule/configuration/model.py`, `capabilities.py`, `capability_selection.py`, `derivation.py`, `operations.py` (`_split_tools`, `_elicit_identity`, `_elicit_owner_selection`), `owner_commands.py`, `fingerprints.py`, `manifest_document.py`, `file_formats.py`, and `devcapsule/images/tooling.py` (the base's pinned Node, Temurin and Maven).

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists with the source installed editable. Create `/opt/devcapsule-gate/pytest-codex-impl` with `mkdir -p` and run every pytest and nox invocation from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex-impl"`. The gate for this slice is the full one: `.venv/bin/python -m nox -s build`, which runs the version check, syntax, mypy, the unit tests, builds the test executable, runs the packaging integration against it and the web console session. The unit gate alone missed a stale expectation in rc4 (`fe886ad`); do not report a slice as gated on `nox -s tests` alone. Do not build images and do not start capsules.

## The task: slice 1 of three, "the catalog and derivation on one capability table, with the old commands still working on top of it"

The order's Part 6 names the three slices. This one changes the model underneath and leaves the command surface as rc4 shipped it, so that slice 2 can change the commands against a model that is already right. Concretely:

1. **One capability table in the catalog.** Replace `surface_capabilities`, `ancillary_capabilities` and `local_capabilities` with one table: capability name, its providing components in catalog order, and whether it is the IDE (the one role; exactly one IDE capability is selected per launch, as now). Base-supplied capabilities (`python`, `node`, `java`, `maven`, `docker-cli`) have no component; the base pin declares them with the version it supplies, read from the constants the image builds with (`images/tooling.py`) and Ubuntu 24.04's Python 3.12. Every `endswith("-agent")` test goes; `providers(name)[0]` survives only inside the one function that resolves a capability to its provider (the checkout's choice when slice 2 adds it, else the project's recommended resolution when slice 2 adds it, else the catalog's first provider; in this slice, the first provider).
2. **The matrix no longer refuses an agent in the shared contract.** `config require tool codex-agent` and `config offer tool codex-agent` write it like any other capability; the grandfathering code for schema-1 manifests goes with the refusal. The download consent and trust questions are unchanged and are asked per component, as now.
3. **The SDK major is removed, by the owner's ruling.** The `[capabilities.sdk-major]` table, the `TOOL=MAJOR` parsing, the base's `sdk_majors`, the major in the capabilities digest, and every reader and writer of them. A manifest that carries the table is still read: the reader ignores it with one note that names this change, and the next owner write drops it (R-CONFIG-001). A lock whose `capabilities-digest` was computed with the table is accepted as current for an unchanged manifest; an rc4 lock must not report a shared edit nobody made.
4. **A minimum version on a requirement.** `required = ["python>=3.14", "java>=21", "playwright>=1.21"]` is parsed from the manifest: one relation, `>=`; one comparator, dotted integers left to right, `25.0.4+7` read as 25.0.4, `v22.23.1` as 22.23.1, a prerelease or a non-numeric segment refused with a message that says the form is unsupported. Resolution narrows a capability's candidates, its providers' pinned versions and the base's supplied version, to those at or above the minimum, and refuses before any write when none remains, naming what exists: "no base supplies Python 3.14 or newer; the Ubuntu 24.04 bases supply 3.12". `config check` reports an unmet minimum as a contract error; `config show` prints the minimum beside the requirement. A checkout's own version set (D-0010) must meet the minimum as it must meet presence: `run` stops with status 3 and names `versions follow-project --apply`. In this slice the command line does not yet accept `>=` (slice 2); the manifest does, and a hand-written manifest is the test's input.
5. **The old commands keep working on the new model.** `config ide`, `config agent add|remove`, `config tool omit|restore`, `run --ide`, `run --agent`, `init --ide/--agent`, `require tool`, `offer tool` all behave as in rc4, implemented as selections and declarations of capabilities on the one table. Their renaming is slice 2; their deletion is slice 3. Existing tests that drive them must pass unchanged except where they asserted the refusal of an agent or the SDK major.

## The care the owner asked for (Part 6), as acceptance

- Fixtures from rc4 read with the same meaning: a checkout record whose `selected` names `*-agent` capabilities and `frontend-ide`; a schema-2 manifest with `optional` tools, `[recommendations] ide` and a `[capabilities.sdk-major]` table; an rc4 lock with `capability-providers` and the old digest; the trust record. Take them from `tests/` fixtures or write them by hand from the shapes in the order's Part 2; each derives the same launch, provider for provider, and the old lock reads as current.
- No kind survives by accident: `grep -rn 'endswith("-agent")\|local_capabilities\|surface_capabilities\|ancillary_capabilities\|sdk_major\|sdk-major' devcapsule/` returns nothing but the one reader that ignores the old table, and `providers(` indexed `[0]` appears once.
- Consent never widens: the rc4 tests that prove "a recommendation grants nothing" and "a changed recommendation keeps the answer" pass unchanged.
- Nothing is written before the last blocking decision; `--preview` on every owner command still shows the result and writes nothing.
- The owner's use case is a fixture: one manifest requiring `python>=3.14`, `java>=21`, `playwright>=1.21`; the Python refusal names 3.12; a manifest without the Python line resolves and pins Temurin 25.0.4 from the base and Playwright 1.63.0.
- The Hoare standard for the capability table: it is the one place the launcher learns what a capability is; its module docstring says so and says what each field means.

## What you must not do

- Do not change the command names, the run flags, the manifest's `[recommendations]` shape beyond reading, the checkout record's shape, or the documentation under `docs/`; those are slices 2 and 3. Do not rename the IDE role (D-0014 is tabled).
- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, or to any branch other than `ws-maintenance/capabilities-1-model`. Do not rebase or force-push.
- Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/capabilities-1-model`, each message naming the component, the change and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base release-0.3.0 --head ws-maintenance/capabilities-1-model`.
   Title: "Capabilities and components, PR1: one capability table; the SDK major removed; a minimum on a requirement".
   The body lists what changed by the five points above, the choices you made where the order was silent and why, what you considered and left alone, the fixtures and the grep of the acceptance, and the full gate's counts with what was skipped. End the body with `🤖 Generated with Codex`.
3. Print the PR URL as the last line of your output, or "NO PR" with the reason.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

The reviewer will read the diff, run the full gate, and post findings as comments on the PR and into your resumed session; expect up to three rounds. If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
