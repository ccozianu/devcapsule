# Bug: Init And Run Answers Are Not Persisted As The Authorizations They Express

Date opened: 2026-09-02

Status: **closed 2026-09-03** — the owner exercised base selection with the
v0.2.9 CLI and signed off: "the UX is thoroughly as expected and no trace
of previous behavior". Originally reported by the product owner during the
successful tictactoe codium smoke on the v0.2.8 base. See *Closure* below.

Requirements: R-PRODUCT-001

Related: `2026-09-01-init-authorize-base-image-not-recorded.md` — same
family: an answer the user expressed reaches the tool but does not land in
the checkout record, and the remedy is a config-family command the user
should not have needed.

## Symptom A: init cannot authorize the base the user intends

The exact command line:

```bash
devcapsule-local.pex project --path . init --need node \
  --need frontend-ide --name "TypeScript Tictactoe 5-in-row" \
  --slug tictactoe-5inrow --creator https://github.com/ccozianu \
  --project-mount /workspace/tictactoe-5inrow \
  --authorize base-image "docker.io/mycodespaceai/devcapsule-base:v0.2.8"
```

did not leave the checkout authorized; a further
`devcapsule project config authorize base-image …` was required.

Mechanism (from code reading, revision `86b2fc4`): init's base-image
answer is validated by `_acquisition_validator`, which accepts only `yes`,
`no`, or **the exact reference of the lock init itself just generated** —
at the time, the embedded matrix's v026 digest. The user's intended base
(`:v0.2.8`, and in tag rather than digest form) is unrepresentable through
init: the flag can only *confirm* the matrix's choice, never express a
different one. Meanwhile the config family's `authorize base-image`
accepted the `:v0.2.8` tag (pinning by inspection), so the two paths also
disagree about reference strictness.

Note: the `embedded-3` matrix advance (2026-09-02) makes codium locks pin
the v0.2.8 base directly, so this *specific* detour disappears for
codium-only needs — but the general defect stands: a user who wants a
base other than the matrix pin cannot say so at init, and an
unsatisfiable `--authorize base-image` value should fail the init loudly
rather than leave an unauthorized checkout behind a completed-looking run.

## Symptom B: a prompted answer was accepted but not persisted

During the launch flow, a prompt offered network-mode selection and
"network host" was chosen — yet the project still required a further
explicit `authorize network host` (config-family) step before `run`
behaved as intended. An interactive prompt that accepts an answer and
does not record it as the corresponding authorization misleads twice:
the user believes the question is settled, and the eventual failure
points at configuration they remember providing.

## Expected

The two-action contract (D-record'd postcondition: `project init` then
`project run`) with every expressed answer — flag or prompt — either
persisted where the config family would persist it, or refused loudly at
the moment it is given.

## Fix Scope

After the current integration:

1. Base-image authorize carriers and prompts accept the same reference
   forms the config family accepts, and an unsatisfiable value fails init
   loudly instead of completing unauthorized.
2. Decide the design for expressing a non-matrix base at init (an
   explicit base override answer, or a documented lock-edit flow) —
   coordinate with the D-0007 matrix model, where an unverified base is
   deliberately not resolvable.
3. Audit the launch-path prompts (network mode confirmed; sweep for
   siblings) so every accepted answer is persisted through the
   config-family primitives, with regression tests in the pattern of the
   2026-09-01 fix.

## Closure (2026-09-03)

Both symptoms were resolved by the 2026-09-03 authorization-grammar
rework on `component-catalog/antigravity-cli`, and the owner validated
the base-selection path hands-on with the v0.2.9 CLI the same day.

Symptom A — closed by the base-selection rework
(`_base_answer_validator` / `_record_base_selection` in
`devcapsule/project_operations.py`): `init --authorize base-image` now
accepts the reserved keyword `default` (the matrix recommendation), a
reference-shaped selection naming a **daemon-local** image (tag or image
ID), or `no`. A local selection is inspected, its image ID, platform,
and `devcapsule.*` labels are presented, and informed consent is
solicited (`--less-pedantic` records the reviewed selection without the
confirmation); the recorded authorization binds trust to the inspected
image ID (D-0004), carrying `reference`, `lock-digest`, and `image-id`,
and `run` requires the local image to still match that ID. Any
unsatisfiable value fails init loudly, naming the accepted forms. This
also answers fix-scope item 2: a non-matrix base is expressible at init
as a daemon-local selection only — a *published* digest differing from
the lock recommendation is refused by design, because a different
published artifact requires its own project-reviewed metadata.

Symptom B — closed by construction rather than by persisting prompt
answers: the launch path no longer prompts at all. Run-once answers
travel the config grammar carriers (`--authorize NAME VALUE`,
`--set NAME VALUE`) under an explicitly declared never-persisted
contract (`_RUN_ONCE_AUTHORIZATIONS` in
`devcapsule/commands/project.py`), persistent recording belongs solely
to the config family, and refusals name the config-family remedy. The
misleading accept-and-drop prompt class no longer exists.

Owner validation, 2026-09-03: picked up a different base at init with
the current v0.2.9 CLI; the UX is thoroughly as expected with no trace
of the previous behavior.
