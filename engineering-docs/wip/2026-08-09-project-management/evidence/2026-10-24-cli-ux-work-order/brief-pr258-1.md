# Review brief for the Codex + gpt-6-astra pair: PR258.1 on the CLI UX redesign work order

The first pair, Claude Fable 5.1 with the owner, has opened pull request 258 ("Work order: redesign the project config and project run experience (draft for the owner's decisions)"), branch `ws-project-management/cli-ux-work-order`, against `main`. It is the same loop as the network-node (#242) and software-approvals (#250) reviews, topic 9.11 of `WORKFLOW.md`, applied this time to a document and not to code. Your job is one improvement pull request against that branch.

The slice is one document: `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, a draft work order that the owner will decide on. It catalogues 21 deficiencies of `devcapsule project config` and `devcapsule project run` as released in 0.3.0 candidate 3, states the principles the owner ruled on 2026-10-24, describes the redesigned experience as a user would meet it, lists what goes away, and lists eleven decisions for the owner. Nothing in it is implemented; a specification and an implementation are two later work orders.

You have a particular standing here. Items 18 to 21 of Part 1 are about the manifest of `ccozianu/ai-learning-bootstrap`, written on 2026-10-22 by your pair, working inside this repository. The document says that manifest states one of the project's three needs. If the account is unfair or wrong, say so with evidence; if the manifest could have expressed more with the 0.3.0 vocabulary, show how, in the PR body, with the commands. You are the best witness of what the CLI let you express and what it refused.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/project-management-review, on the branch `ws-project-management/cli-ux-work-order-review`, branched from `ws-project-management/cli-ux-work-order`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex and do not touch /home/devcapsule/worktrees/project-management.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11 is the loop you are in), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), then the document under review in full, then the records it rests on: `engineering-docs/decisions/product/d-0004-configuration-resolution-and-guided-run.md`, `d-0001`, `d-0010`, `d-0011`, `d-0012` in the same directory, `R-CONFIG-001` in `REQUIREMENTS.md`, `engineering-docs/design-notes/devcapsule/v1-user-experience.md`, and the user pages `docs/configuration/capabilities.md`, `docs/configuration/project-versus-personal.md`, `docs/configuration/software-approvals.md`. The 0.3.0 changelog is `engineering-docs/releases/v0.3.0/changelog.md`.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable; the launcher under review is `devcapsule-src/.venv/bin/devcapsule`, at the source of this branch. Use a scratch directory under /opt/devcapsule-gate/pytest-codex for any project you create; create it with `mkdir -p`. The manifest and lock of `ai-learning-bootstrap` are private; fetch them with `gh api repos/ccozianu/ai-learning-bootstrap/contents/.devcapsule/devcapsule.toml --jq .content | base64 -d`, and the lock `devcapsule.linux-amd64.lock` the same way, into a scratch clone with a `.git` directory, since the launcher reads the checkout.

This PR changes no code, so there is no unit gate to run. The validation is the reproduction of the document's claims: every item of Part 1 names its command, its output and, where it says "from the code", the file and line. Repeat the ones you can without a container. Where a command could launch a capsule, `project run` first of all, use `--print-command`, or stop at the refusal the document describes; never let a bare `project run` reach Docker. Do not build images and do not start capsules.

## The task

Review the diff of PR 258 against its base:

    gh pr diff 258

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of what the document asserts. Ask: does each of the 21 items reproduce as written, with that command and that output, on this source; are the file and line references right; is every statement about a record right, its status, its date, what it allows and what it forbids, in particular D-0004's status, D-0011's and D-0012's scope, D-0010's owner refinements and R-CONFIG-001; are the statements about today's behaviour inside Part 3 right where it says "as today" or "as it does today"; does the transcript in 3.1 claim a version or a name that does not exist; is item 18's account of the manifest's vocabulary complete and fair, in particular the claims that a declared value reaches the capsule only through two runtime effects, that secret inputs are declared only by lock components, and that `--required frontend-ide` is refused; is item 19's account of the writer right. Fix a wrong fact in place, with the evidence in your PR body. Where a fact is right but overstated, state it exactly.
2. Clarity, read as the two readers the document names: the owner deciding Part 5, and the user reading Part 3. The standard is "obviously no deficiencies". Ask: can the owner decide each Part 5 item from what the document gives, and is each item one decision; does Part 3 ever contradict Part 2 or Part 4; is there a concept with two names or a flag with two meanings left in the proposed tree; does a sentence need a second reading. Do not change the wording of Part 2 items 1 to 6: they are the owner's rulings as recorded.
3. Coverage. Ask: is a deficiency of the `config` or `run` surface missing that an adopter meets on the first day; is a case missing in Part 3, two checkouts of one project on one workstation, a project with no `.devcapsule/` at all, an agent inside the capsule reading its own configuration, a project owner changing a requirement while collaborators have checkouts; does the design imply a decision that Part 5 does not list. Add a missing deficiency only with its reproduction; add a missing decision as a Part 5 item, phrased as a question with the alternatives, never as an answer.

Stay inside the document's scope: `project config` and `project run`, the manifest and the lock as the user meets them. The session-lifecycle, exit-code, help-text and `images`/`bootstrap`/`workflow` items are catalogued for the next pass; do not design them. Do not implement anything. Do not decide anything for the owner: a change to the design is a proposal in your PR body or a new Part 5 question, not an edit to Part 3 as if it were settled. Do not edit `CURRENT-STATUS.md` or `index.md`.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-project-management/cli-ux-work-order-review`, each message naming the part of the document and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-project-management/cli-ux-work-order --head ws-project-management/cli-ux-work-order-review`.
   Title: "Correctness, clarity and coverage review of #258 (PR258.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, and the command or file that proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement, the design proposals among them. State which Part 1 items you reproduced, with the commands, and which you could not and why. If you find nothing to change, say so in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a command you ran or a file and line you read.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
