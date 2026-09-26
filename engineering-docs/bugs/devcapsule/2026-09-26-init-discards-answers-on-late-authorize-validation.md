---
status: fixed
severity: blocking
target: 0.2.15
owner: maintenance
opened: 2026-09-26
requirements: [R-PRODUCT-001, R-DOCKER-001, R-SCOPE-001]
---

# `project init` discards every interactive answer when a `--authorize` name is unknown

The owner started a brand-new project with the released 0.2.14 launcher,
answered every recommendation and vendor-download prompt, and then saw the
command fail on the last step because one command-line flag named a
configuration node that does not exist (`docker` instead of `docker-daemon`).
The manifest and lock were written; the checkout record was not. Every
answer given at the prompts and every valid `--authorize` given on the
command line was lost, and `project run` refused to start until each decision
was re-entered one command at a time. The owner rated this a show stopper for
the first-session experience: the very first command an adopter runs must
not throw away the consent it just asked for.

## Environment

- Host: the owner's workstation, Pop!_OS, released launcher
  `DevCapsule v0.2.14 (package 0.2.14)`, source revision `abb785d`.
- Fresh directory `~/work.provisional/costin3/myProjects/chessclub-website`,
  no prior DevCapsule files.
- Interactive terminal.

## Reproduction

```text
devcapsule project init --name chessclub-website --need frontend-ide --need node \
  --creator https://github.com/ccozianu --need frontend-ide --need antigravity-agent \
  --need claude-code-agent --need codex-agent \
  --authorize base-image default --authorize network host --authorize docker host
```

The command prompts for the docker-daemon, network, development-sudo and
host-browser recommendations with their justifications, then for the
Antigravity CLI 1.1.24 and Claude Code 2.1.261 download consents. All were
answered. It then exits with:

```text
devcapsule: Configuration node 'docker' is not declared by this project and lock;
declared nodes: antigravity-cli/gemini-api-key, antigravity-cli/home, antigravity-download,
base-image, claude-code-download, claude-code/home, codex/home, codex/openai-api-key,
codium/cache, codium/extensions, codium/user-data, development-sudo, docker-daemon, home,
host-browser, host-x11, network.
```

Afterwards:

```text
$ devcapsule project run
devcapsule: Local resolution is missing; run 'devcapsule project config resolve'.
$ devcapsule project config resolve
devcapsule: Configuration review: decisions required.
antigravity-download: missing-required; recorded: unanswered; recommended: true
base-image: missing-required; recorded: unanswered; recommended: v0.2.12-rc5 — ...
claude-code-download: missing-required; recorded: unanswered; recommended: true
Display: no host-x11 decision is recorded. ...
```

The full transcript is preserved in the maintenance intake item that
delivered this record; the excerpt above is verbatim.

## Expected behavior

1. A misspelled or undeclared `--authorize`, `--set` or `--bind` name is
   rejected before the first prompt, with the declared names listed and,
   where one is close, the likely intended name (`docker` → `docker-daemon`).
   The user corrects the command line and runs again; nothing has been asked
   or written yet.
2. If a late failure does occur, the answers already given are not lost:
   either the checkout record is written with what was answered and the
   report says which answer was rejected, or nothing at all is written, the
   report says so, and the manifest is not left behind half-initialized.
3. `init` keeps its stated postcondition: when it exits successfully,
   `project run` starts the environment. When it fails, it says what state
   it left and what one command repairs it.

## Actual behavior

The prompts run to completion, the manifest and platform lock are written,
and only then is the unknown node name detected. The checkout record, which
holds every answer the prompts collected and every command-line
authorization, is never written. The project is left with a manifest and
lock and no local decisions.

## Evidence in the source at `abb785d` (unchanged on `main` at `f4949aa`)

`initialize_project` in
`devcapsule-src/devcapsule/configuration/operations.py` runs, in order:
`_elicit_identity`, `_elicit_recommendations`, `_write_manifest`, lock
generation and `atomic_write(lock_path, ...)`, `_elicit_acquisitions` (the
two vendor-download prompts), `_elicit_host_answers`, then
`_elicit_extra_answers`, and only after that `record.write()`.

`_elicit_extra_answers` is the first place the supplied `--authorize` names
meet the node registry: `registry.answerable(supplied_answer.name, ...)`
raises `ProjectConfigurationError` for an undeclared name, from
`NodeRegistry.node` in `devcapsule/configuration/nodes.py`. Its docstring
says "Families are checked before any local write"; by then the manifest and
lock are on disk and the collected answers exist only in memory.

Two smaller observations from the same transcript, recorded here rather than
lost, for maintenance to keep or split:

- `--need frontend-ide` given twice is accepted silently. Harmless, but a
  duplicate `--need` is more likely a typo than an intent.
- `--authorize network host` was accepted and lost with the rest, and
  `config resolve` does not list `network` as missing because it is not
  required. The owner would only discover the lost network authorization at
  launch. Whatever fix is chosen must cover optional answers too.

## Hypothesis

Order of operations, with high confidence from the code read above. Command-
line answers can be validated against the declared node names as soon as the
lock exists, and the lock's node set for a given capability list is known
before any prompt. The smallest correct fix validates every supplied answer
name against the registry immediately after the lock is generated or loaded
and before `_elicit_acquisitions`; a stricter one builds the registry from
the would-be lock before writing anything. The near-miss suggestion is a
separate nicety.

## Verification target

A test under `devcapsule-src/tests/` that drives `initialize_project` with a
scripted interactive stream, one valid and one undeclared `--authorize`
answer, and asserts: the error names the undeclared node; no prompt was
consumed from the input stream; and either no manifest was written or the
checkout record holds every answer that was given. Then the owner's
one-command check on a fresh directory: the corrected command line runs to a
successful `project run`.

## Fix (2026-09-26, `ws-maintenance/post-0.2.14`)

`initialize_project` now derives the lock in memory right after the identity
questions and checks every supplied answer name against the node registry
before the first recommendation prompt and before any write
(`_reject_undeclared_answers` in `operations.py`). A curated host name the
project does not recommend yet, such as `network`, is admitted because the
recommendation question of the same invocation declares it. The registry's
undeclared-name error names the closest declared spelling: `'docker'` gets
"Did you mean 'docker-daemon'?". The repeated-init path checks names the
same way before eliciting. Identity questions the command line leaves open,
such as the default-agent offer, still precede the check, because their
answers change which nodes exist.

Tests: `test_undeclared_authorize_name_fails_before_any_prompt_or_write`
(no prompt written, no input consumed, nothing on disk, hint present),
`test_wrong_family_answer_fails_before_any_prompt_or_write`, and
`test_curated_host_authorization_is_admitted_before_the_recommendation_exists`
in `devcapsule-src/tests/test_project_init.py`. The duplicate `--need` and
the optional-answer visibility observations are not changed by this fix.

## Close criteria

Status `closed` when the test above passes on `main`, the release runbook's
first-session acceptance journey includes a misspelled-flag attempt, and the
owner confirms on a fresh directory with a 0.2.15 candidate.
