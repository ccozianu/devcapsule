# Review brief for the Codex + gpt-6-astra pair: PR250.1 on software approvals at launch

Same collaboration as the network-node review (#242), merged after one round. The first pair, Claude Fable 5.1 with the owner, has opened pull request 250 ("Launcher: software approvals at launch; project config approve; the software-approvals page"), branch `ws-maintenance/0.3.0-software-approvals`, against `release-0.3.0`, the active release branch of the 0.3.0 cycle. Your job is one improvement pull request against that branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/0.3.0-software-approvals-review`, branched from `ws-maintenance/0.3.0-software-approvals`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11 is the loop you are in), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the module docstring of `devcapsule/configuration/approvals.py` (the contract: what qualifies as a software approval and what does not), `devcapsule/commands/_software_approvals.py` (the launch-time offer), the `ConfigApproveCommand` and the first lines of `ProjectRunCommand._run` in `devcapsule/commands/project.py`, and the new page `docs/configuration/software-approvals.md`, which is what the user is promised. The owner's direction, 2026-10-22: when `project run` finds that the only pending decisions are new versions of vendor software the developer approved before, from the same vendors under the same terms, it offers the whole list with one y/n; on no, it names `project config approve` and the page.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/configuration/approvals.py` (new), `devcapsule/commands/_software_approvals.py` (new), `devcapsule/commands/project.py` (the approve command, the launch hook, the keypress helper moved), `tests/test_software_approvals.py` (new), two documentation pages linked and one new. The gate type-checks `tests/` too. Run `nox -s build` before your final push and report its result with counts; it takes about three minutes.

Do not build images and do not start capsules.

## The task

Review the diff of PR 250 against its base:

    gh pr diff 250

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: can `pending_software_approvals` ever return a list that includes something the user did not approve before, a denial, a missing consent, a component whose contract changed, a stale answer whose recorded value is not exactly `True`; is a checkout record with a malformed authorization table handled; does the launch hook run before anything that could write, and never in `--print-command`; after `y`, is the record written atomically and the resolution regenerated through the same path `config resolve` uses, and what happens if that resolution fails after the approvals were written (the user's state, the message); does `approve` by name with other approvals still pending leave the resolution untouched and say so; is the newest known-good record chosen by `last-success` and a broken record skipped; does `previous_versions` stay best-effort on every error; is the keypress read only when stdin is a tty, and is EOF on the keypress a refusal and not a crash; does `config approve` inside a capsule refuse for the capsule's own project as the other mutating commands do; does the quoted command print correctly for a path with spaces. Think about a user whose lock brings one new version and one newly added agent at once, and about an agent running `project run` in a script.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies".
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: the malformed record, the EOF on the keypress, the resolution failing after the write, the in-capsule refusal. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: software approvals as the module docstring defines them, the launch offer, the command and the page. Do not change the consent digest, the review's statuses or messages, or the run path beyond the hook. Do not widen what qualifies; if you believe the definition is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/0.3.0-software-approvals-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/0.3.0-software-approvals --head ws-maintenance/0.3.0-software-approvals-review`.
   Title: "Correctness, clarity and coverage review of #250 (PR250.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
