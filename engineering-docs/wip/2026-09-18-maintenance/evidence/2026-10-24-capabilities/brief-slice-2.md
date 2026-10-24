# Implementation brief for the Codex + gpt-6-astra pair: slice 2 of the capabilities and components work order

Same loop as slice 1: you implement; Claude Fable 5.1 reviews, with the owner, Costin Cozianu, who merges. The work order is `engineering-docs/work-orders/2026-10-24-capabilities-and-components.md`; its Part 1 rulings and Part 5 decisions are settled. Slice 1 is PR #276 on `ws-maintenance/capabilities-1-model`, accepted after one review round; this slice stacks on it. Where the order is silent, choose the smallest thing that keeps every Part 6 care point and say what you chose in the PR body. Do not reopen the model.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-impl-2, on the branch `ws-maintenance/capabilities-2-commands`, branched from `ws-maintenance/capabilities-1-model` at its accepted tip. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any other `/home/devcapsule/worktrees/*` worktree.

Read first: the work order, Part 3 (the experience after the change), Part 4 and Part 5 items 1, 2, 4, 5 and 10; then the slice-1 result you implemented: `devcapsule/resolution_matrix.py` (the capability table, `resolve_provider`, `component_closure`, `supplied_version`), `devcapsule/configuration/capabilities.py`, `capability_selection.py` (`selection_catalog`, the rc4 adapter this slice replaces), `derivation.py`, `owner_commands.py`, `manifest_document.py` (`Recommendations`, `render_manifest`), `listing.py`, `commands/project.py` (the `config` command tree, the retired-spelling pattern of rc4 that prints a replacement) and `commands/_run_flow.py` (`RunFlags`, `_settle`, `with_selection`); `docs/reference/cli.md` for the rc4 spellings you retire, read only, not edited.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists with the source installed editable. Create `/opt/devcapsule-gate/pytest-codex-impl-2` with `mkdir -p` and run every pytest and nox invocation from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex-impl-2"`. The gate is the full one, `.venv/bin/python -m nox -s build`, before your final push. Do not build images and do not start capsules.

## The task: slice 2 of three, "the commands, the run flags, the manifest table and the checkout record"

Slice 1 put the model underneath; this slice puts the owner's and the developer's words on it, as the order's Part 3 and Part 5 decide. Concretely:

1. **The owner's commands take capabilities.** `config require CAPABILITY... [--because]`, `config offer CAPABILITY... [--because]`, `config drop CAPABILITY...`; the `tool` sub-word goes, `require env`, `offer env` and `drop env` keep the `env` word. `require` accepts the minimum, `config require 'python>=3.14' 'java>=21'`, the same string the manifest holds (Part 5 item 10); `drop python` removes the requirement whatever its minimum; a second `require 'python>=3.15'` replaces the minimum. An IDE capability is still refused in `require` and `offer` with the pointer to `recommend ide`; agents are ordinary capabilities, as slice 1 made them.
2. **The project recommends a resolution.** `config recommend CAPABILITY COMPONENT [--because]` writes `[recommendations.resolution]`, a table from capability to component, beside `[recommendations]`; `recommend CAPABILITY none` removes it; a component the catalog does not list for that capability is refused before anything is written; `recommend ide NAME` stays as it is. The rc4 launcher reads the new table as an unknown recommendation it warns about and ignores; the schema stays 2 (Part 5 item 4).
3. **The developer's commands.** `config add CAPABILITY` for a capability the project did not mention, `config omit CAPABILITY` for an offered one, `config restore CAPABILITY`, `config use CAPABILITY COMPONENT|default` for the provider where the capability has more than one, `config ide NAME` unchanged. `use` on a capability with one provider is refused with the provider named; `use ... default` returns to the project's resolution or the catalog's. The checkout record gains one table, the chosen providers by capability; `selected` and `without` keep their shape and meaning.
4. **The run flags.** `run --with CAPABILITY` repeatable in place of `--agent`; `run --use CAPABILITY=COMPONENT` repeatable; `--ide` kept; `--save` records them as it records the IDE today.
5. **Derivation and the lock.** For every capability in play, the provider is the checkout's choice, else the project's recommended resolution, else the catalog's first provider, in that order, inside the one resolver slice 1 left; a minimum narrows first. The lock pins the resolved provider only (Part 5 item 5); a developer's different choice is pinned in the checkout record, as the IDE is today. `config show` gains a `PROVIDER` column: the component and its source, `catalog`, `project recommends` or `checkout`; `--json` carries the same fields. `check` reports a recommended resolution the catalog cannot satisfy as a contract error.
6. **The rc4 spellings become retired spellings.** `config agent add|remove`, `config tool omit|restore`, `config require tool`, `offer tool`, `drop tool`, `run --agent`, and `selection_catalog`'s three agent names as command vocabulary: each still executes and prints its replacement once, by the rc4 rule in `commands/project.py`; their deletion, with the rc4 aliases, is slice 3 (Part 5 item 6). Existing tests that drive the old spellings pass unchanged except for the printed note.

## The care the owner asked for (Part 6), as acceptance

- rc4 and slice-1 files read with the same meaning: a checkout record without the provider table derives as before; a manifest without `[recommendations.resolution]` derives as before; a manifest with it, read by code that ignores the table, still derives the catalog's first provider, which for every capability today is the only one.
- Consent never widens: a recommended resolution grants nothing; a `use` that selects a vendor component meets trust or consent as a first acquisition; the rc4 tests "a recommendation grants nothing" and "a changed recommendation keeps the answer" pass unchanged and are extended to resolutions.
- Nothing is written before the last blocking decision; `--preview` on every owner command, `recommend` included, shows the result and writes nothing; `run --with`/`--use` without `--save` write nothing.
- The owner's Part 3 example is a fixture: the manifest of section 3.1 written by the commands of 3.1, byte for byte as the order shows it (bare keys, table order), and the developer's commands of 3.2 against it. Since no capability has two providers today, add a synthetic two-provider capability to a test matrix to prove `use`, the resolution recommendation and the precedence; do not add one to the shipped catalog.
- No kind returns: the grep of slice 1 still holds; no new list of names by kind appears outside the retired-spelling adapter.
- The Hoare standard for the resolver: one function, documented precedence, every branch tested.

## What you must not do

- Do not delete any spelling; do not edit the documentation under `docs/` or the changelog; those are slice 3. Do not rename the IDE role (D-0014 is tabled). Do not change the catalog's capabilities or providers.
- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to `ws-maintenance/capabilities-1-model`, or to any branch other than `ws-maintenance/capabilities-2-commands`. Do not rebase or force-push.
- Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/capabilities-2-commands`, each message naming the component, the change and the evidence, ending with `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/capabilities-1-model --head ws-maintenance/capabilities-2-commands`.
   Title: "Capabilities and components, PR2: the owner's and the developer's commands, the resolution recommendation, the provider choice".
   The body lists what changed by the six points above, the choices you made where the order was silent and why, what you considered and left alone, the fixtures and the grep, and the full gate's counts with what was skipped. End the body with `🤖 Generated with Codex`.
3. Print the PR URL as the last line of your output, or "NO PR" with the reason.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

The reviewer will read the diff, run the full gate, and post findings as comments on the PR and into your resumed session; expect up to three rounds. If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
