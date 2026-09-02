# Bug: The Authorization Grammar Cannot Express Denial

Date opened: 2026-09-02

Status: open; reported by the product owner during v0.2.9 smoke
triage, while trying to downgrade a checkout to the no-sudo posture

Requirements: R-PRODUCT-002 (explicit host boundaries), R-PRODUCT-001

Related: `2026-09-02-init-and-run-answers-not-persisted-as-authorizations.md`
— same family: an answer the developer expresses through the config
grammar is not honored as the decision it plainly is.

## Symptom

```
devcapsule-local.pex project config authorize development-sudo false
devcapsule: Project recommendation 'development-sudo' is exactly True, not False.
Authorizing a different value requires distinct reviewed metadata.
```

The developer is trying to *reduce* privilege — record that this
checkout must not enable development sudo — and the tool refuses,
telling the developer that saying no requires "distinct reviewed
metadata."

## Mechanism (from code reading, branch revision `46afdf0`)

`normalize_authorization_value` (`project_configuration.py`) accepts
exactly one value per authorization node: the declaration's
`recommended_value`. Anything else raises. Every authorization carrier
routes through it:

- persistent: `project config authorize NAME VALUE`;
- run-once: `project run --authorize NAME VALUE`
  (`_run_once_answers` in `commands/project.py`).

So the whole authorization vocabulary is "yes to the recommendation" or
silence. An explicit *no* is unrepresentable — persistently and even
for a single launch. The only paths to the deny posture are
`project config unset NAME` (expressing denial as absence, with no
pointer to it in the refusal message) and, incidentally,
`run --no-recursive-e2e`, whose name has nothing to do with sudo.

Two aggravations:

1. The message misattributes the source. For `development-sudo` the
   declaration may come from `WORKSTATION_CAPABILITY_DEFAULTS`, not from
   any project recommendation, yet the refusal says "Project
   recommendation … is exactly True" — naming a recommendation the
   project never made and implying the value was reviewed when it is a
   built-in default.
2. The message inverts ownership. Per the owner-settled 2026-08-24
   model, quoted in the code beside those defaults: "Denial is the
   default. The developer may deny it, allow it once, allow it for
   this checkout." The developer's denial is theirs to record and
   needs no reviewed metadata; only *recommendations* carry review.

## Why It Surfaced Now

The codium × development-sudo launch failure (the setuid sandbox helper
lacks CAP_SYS_ADMIN under the sudo posture — separate record pending
confirmation) made downgrading to no-sudo the natural next step, and
the natural spelling of that step is exactly the refused command.

## Expected

- `config authorize NAME false` (bool nodes) records an explicit,
  persistent denial: prompts stop asking, the recommendation does not
  re-apply it, resolution and `run` see the node as denied.
- `run --authorize NAME false` downgrades that one launch.
- Whether explicit denial and `unset` (absence) remain distinct states
  is a design decision to record; today only absence exists.
- Until then, the refusal must at least name the working remedy
  (`project config unset NAME` + `config resolve`) and must not call a
  workstation default a project recommendation.

## Reproducibility

Always; any bool authorization node with a recommendation or
workstation default (`development-sudo`, `host-browser`,
`docker-daemon` with its string value behaves the same way).

## Verification Target

- Automated test: authorizing `false` on a bool node persists a denial
  the resolver honors (and `run --authorize NAME false` overrides one
  launch); a workstation-default refusal message names no project.
- Manual validation: on a sudo-authorized checkout,
  `config authorize development-sudo false` then `run` launches in the
  hardened posture without touching `--no-recursive-e2e`.
