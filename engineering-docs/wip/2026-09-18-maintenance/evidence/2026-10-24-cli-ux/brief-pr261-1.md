# Review brief for the Codex + gpt-6-astra pair: PR261.1 on the manifest's schema 2 and the owner's commands

The first pair, Claude Fable 5.1 with the owner, has opened pull request 261 ("CLI UX redesign, PR1: the manifest's schema 2, the owner's commands, init on the required form"), branch `ws-maintenance/cli-ux-1-manifest`, against `ws-maintenance/cli-ux-0-work-order`, the base of a stack of six slices that implement the CLI UX redesign work order for 0.3.0 rc4. It is the same loop as #242, #250 and #259 (you reviewed the work order itself there), topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 261's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-1-manifest-review`, branched from `ws-maintenance/cli-ux-1-manifest`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex and do not touch /home/devcapsule/worktrees/maintenance-cli-1.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), then the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, in particular Part 1 items 18 to 21, principle 7, and Part 5 answers 9, 11, 18 and 19, which this slice implements; then the module docstrings of `devcapsule/configuration/manifest_document.py` (the contract of the writer and the two new readers), `devcapsule/configuration/owner_commands.py` (the owner's verbs), the `initialize_project` docstring in `devcapsule/configuration/operations.py` (the one init path), and `promote` in `devcapsule/configuration/capability_commands.py`. The maintenance status, `engineering-docs/wip/2026-09-18-maintenance/CURRENT-STATUS.md`, section "The CLI UX redesign in rc4", lists the six slices; this is slice 1, and slices 2 to 6 are not yours to anticipate.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/configuration/manifest_document.py` (new), `devcapsule/configuration/owner_commands.py` (new), `devcapsule/configuration/operations.py` (init rewritten), `devcapsule/configuration/capability_commands.py` (promote, the second init path removed, tool-name parsing), `devcapsule/configuration/file_formats.py`, `manifest.py`, `values.py`, `devcapsule/commands/project.py` (init flags, the owner command group, retired spellings); tests `test_manifest_document.py` (new), `test_owner_commands.py` (new), and the rewritten `test_project_init.py`, `test_capability_policy.py`, `test_upgrade_recovery.py`, `test_project_commands.py`, `tests/configuration/`. The gate type-checks `tests/` too. Run `nox -s tests` and `mypy devcapsule tests` before your final push and report the counts; the test session takes about two minutes.

Do not build images and do not start capsules. `project run` is not part of this slice; `--print-command` is the farthest a launch probe goes.

## The task

Review the diff of PR 261 against its base:

    gh pr diff 261

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: does `render_manifest` produce valid TOML for every key the readers accept, including a value name with dots (`configuration.values."db.url"`), a key with characters TOML's bare keys refuse, a nested empty table, and a string with quotes or newlines; does `manifest_preamble` keep exactly the leading comment block and nothing else; does an owner's edit of a schema-1 `need` manifest convert it correctly, keep the leading comment, and leave an unrelated command (`check`, `capabilities --local`, `config list`) never rewriting it; does `promote` with no lock keep the lock file's bytes exactly, and does `recover` still work on the journal it writes; can `require tool` introduce an IDE or an agent by any spelling (a component id, a capability name, `TOOL=MAJOR`); does `drop tool` remove the SDK major and the reason; is an SDK major on an offered tool refused in every path; does `recommend ide` accept only surfaces this launcher knows, and `recommend memory` store the canonical size for every Docker spelling; does `recommend NODE none` remove exactly that recommendation and leave the others; does the new `initialize_project` write nothing when a noninteractive init batch-fails (manifest, lock, checkout record), honor an existing `need` manifest with the IDE inside without asking the IDE question, and refuse a bad mount before the first write; does `_init_selection` map every rc3 spelling correctly, including `--sdk-major python=3` and `--local` with an agent and an IDE; what happens when `--ide` names a component id (`pycharm`); is `_refresh_own_checkout` safe when the owner's checkout has no IDE or a pending consent. Think about a project owner on rc4 editing a manifest their collaborators read with rc3.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies". The help texts of `init`, `config require|offer|drop|recommend` are what a user reads first.
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: the writer's quoting edge cases, `promote` with no lock under recovery, `drop tool` of an offered tool, `recommend` of each host node and its removal, the legacy flag mapping, init with `--ide pycharm`, the batch failure writing nothing. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the manifest's schema 2 and its writer, the owner's commands, the one init path, the retired spellings. Do not add the checkout verbs of slice 2 (`config ide`, `agent add`, `env`), do not touch `project run` or `config resolve`, do not change the lock format or the checkout record's schema. If you believe a contract is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to `ws-maintenance/cli-ux-0-work-order`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-1-manifest-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-1-manifest --head ws-maintenance/cli-ux-1-manifest-review`.
   Title: "Correctness, clarity and coverage review of #261 (PR261.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
