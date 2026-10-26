# Review brief for the Codex + gpt-6-astra pair: PR289.1 on the manifest's two schemas

The first pair, Claude Code with Claude Fable 5.1 and the owner, Costin Cozianu, has opened pull request 289 ("The manifest's two schemas as classes; init --regenerate migrates to schema 2"), branch `ws-maintenance/manifest-schemas`, against `release-0.3.0`. It implements the work order of 2026-10-26, a gate of the final 0.3.0 tag. No earlier review of this slice exists. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 289's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/manifest-schemas-review`, branched from `ws-maintenance/manifest-schemas`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any other `/home/devcapsule/worktrees/*` worktree.

Read first, in this order: `AGENTS.md`; `WORKFLOW.md` (topic 9.11); `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout*, *GitHub Integration*, *Validation Commands*); the work order `engineering-docs/work-orders/2026-10-26-manifest-schemas-as-classes.md`, whole; `engineering-docs/requirements/product/r-config-001-conservative-writers-tolerant-readers.md`; then the module whose docstring is the contract, `devcapsule-src/devcapsule/configuration/manifest_schemas.py`, and its neighbours `manifest.py`, `manifest_document.py` and `capabilities.py`; then the PR body, whose *Judgments for the owner* names four places where the implementation departs from the order's letter and why.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable from this worktree. Run every pytest, mypy and nox invocation from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`. The gate is `.venv/bin/python -m nox -s build`; it type-checks `tests/` too. Run it before your final push and report its counts. The documentation check is the website's content contract: from `/workspace/301e4208ef81-ChatGPT_Codex/website` (read it, do not edit it), `CONTENT_DIR=/home/devcapsule/worktrees/maintenance-review npm run check:content`.

This PR touches, in `devcapsule-src/devcapsule/`: `configuration/manifest_schemas.py` (new), `configuration/manifest.py`, `configuration/capabilities.py`, `configuration/file_formats.py` (`legacy_lock`), `configuration/capability_selection.py`, `configuration/fingerprints.py`, `configuration/freshness.py`, `configuration/model.py`, `configuration/storage.py`, `configuration/operations.py`, `configuration/owner_commands.py`, `configuration/capability_commands.py`, `configuration/authorization.py` (one message), `configuration/manifest_document.py` (docstring), `commands/_run_flow.py`, `commands/project.py`, `resolution_matrix.py` (messages); in `tests/`: `test_manifest_schemas.py` (new) and adjustments in eleven existing test modules; `docs/reference/cli.md` and `docs/configuration/capabilities.md`, two sentences each.

Do not build images, do not start capsules, do not pull the base. A scratch project under `/opt/devcapsule-gate/pytest-codex` with `HOME` and the `XDG_*_HOME` variables set there is the place to run the executable; the compat fixtures under `tests/resources/compat/` and the sample project manifest at `/workspace/301e4208ef81-ChatGPT_Codex/devcapsule-src/tests/resources/sample_projects/devcapsule-sample-trading-research/.devcapsule/` (copy it; it is a submodule, read-only for you) are the schema-1 inputs in evidence.

## The task

Review the diff of PR 289 against its base:

    gh pr diff 289

Read first inside the diff: `manifest_schemas.py` whole, then `manifest.py`, then the `initialize_project` and `_prepare_manifest` changes in `operations.py`, then `legacy_lock` and its three callers.

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Questions a careful engineer would ask:
   - Do `ManifestV1.read` and `ManifestV2.read` admit exactly what the order says and refuse the other schema's words by name? Is every field of each class either validated or carried verbatim, with nothing silently dropped? Does `document()` of a value read from a file reproduce that file's mapping (the environment table, the project table, extension tables, unknown capability keys, the retired table), so that `manifest_for` is lossless for schema-2 files?
   - Do the six upgrade laws hold on every schema-1 shape in evidence, including an IDE named by its component alias (`pycharm`), a name unknown to the catalog, duplicate names, `optional` beside `need`, `workflow-type` with and without `[workflow]`? Is the two-IDE refusal reachable and its remedy true? Can `upgrade` ever write, or mutate its input?
   - `init`: with `--regenerate` on a schema-1 file, is the migrated text exactly what the one writer renders from the upgraded mapping plus any host recommendation `init` appends, with the leading comment block kept, and is nothing written when a later answer fails? Without `--regenerate`, is a schema-1 file never written? With a schema-2 file and `--regenerate`, byte for byte? Is the "Migrated" report line true in every path, including a manifest that `init` also appends recommendations to? Is the pinned-IDE default (`pinned`) taken only for schema-1 files, and does it reach the owner's checkout record with its pins?
   - `legacy_lock`: is "no provider evidence, or a generation before embedded-27" the right translation of what `layered` gated in `usable_lock`, `resolution_source_digests` and `recommendation_lock_for`? Consider a composed lock (a checkout's pins laid over a legacy shared lock carry an evidence table but keep the legacy generation), a lock rendered by the matrix without evidence, a lock with a version string the rule does not parse. Does the new "keep the pinned IDE" step in `usable_lock` ever keep a component the lock does not actually contain, or hide a required capability's absence?
   - Freshness: `source_digest`. Does every production caller of `stale_resolution_inputs` that read the file pass it? Does `Configuration` compute it from the mapping as given, before the upgrade? Could a stale schema-1 checkpoint be accepted because the digest of the unchanged file matches while the in-memory reading changed (it cannot if the file is the only source; check that it is)?
   - The run flow: with the recommended IDE applied only when the lock pins none, does a migrated project with a regenerated lock and a developer's old checkout (no IDE selection) still launch the recommended IDE, and does a not-yet-regenerated schema-1 project launch its pinned IDE without writing its record or its manifest? The existing test `test_schema_one_ide_in_need_launches_without_rewriting_manifest` covers the second; write the first if it is missing.
   - R-CONFIG-001: is there any command other than an owner's edit and `init --regenerate` that now writes a schema-1 file? Any reader outside `manifest_schemas.py` that still knows a schema-1 word?
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies": every comment states a reason a reader could not infer; no sentence of a docstring is false after the change; names say what they hold (`pinned`, `legacy_lock`, `source_digest`, `NeedForm`, `RequiredForm`).
3. Test coverage of the new and modified lines. `tests/test_manifest_schemas.py` holds the laws; add tests where a branch is not exercised, in particular `document()` round trips for the lossless fields, the composed-legacy-lock case, the run-flow case above, and `init --regenerate` when a later answer fails. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the manifest's schemas, their migration, the readers that change with them, and `init --regenerate`. Do not change the lock format, the matrix, the owner commands' verbs or the console. Do not widen the contract of `manifest_schemas.py`; if you believe one of the four judgments in the PR body is wrong, say why in your PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, the release records, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, the sample-project submodules, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/manifest-schemas-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as. Never the words substrate, edge, gen1 or gen2.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/manifest-schemas --head ws-maintenance/manifest-schemas-review`.
   Title: "Correctness, clarity and coverage review of #289 (PR289.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
