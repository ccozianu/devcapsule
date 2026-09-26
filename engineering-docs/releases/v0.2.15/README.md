# DevCapsule 0.2.15 — Release Work

Updated: 2026-09-26. Stage: **cut from `v0.2.14`; candidate 0 pending**.
Driver: **maintenance**. Product owner: Costin Cozianu.

## Scope And Owner Decisions

- 2026-09-26: the owner rated the init answer loss a show stopper and ruled
  that 0.2.15 ships with its fix and nothing else; everything else planned
  for 0.2.15 moves to 0.2.16. No fourth version number.
- The one change: [`project init` discards every interactive answer when a
  `--authorize` name is unknown](../bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md).
  Fixed on `main` in PR #143 at `3acc460`; carried here as a cherry-pick of
  `74bc4aa` with its origin recorded.
- Cut source: the `v0.2.14` tag, not `main`. Judged by lines touched: the fix
  is 97 insertions and 15 deletions in two source files; `main` since the tag
  is 496 and 60 across seventeen, the rest being the base-contract naming and
  the images package move, which are 0.2.16 material. The runbook's
  maintenance-patch path applies; the candidate gate's exception record
  beside this directory names the release-only commits.

## Preparation And Publication

- Release branch `release-0.2.15` at `abb785d` (`v0.2.14`), fix `9a0567c`,
  version `c601fb8`.
- Candidate gate: exception record `../v0.2.15-rc0-integration-exception.json`.
- [x] Full local gate on the release branch at `4f28a12`: 1068 passed, 20 deselected, 1 xfailed, 1 xpassed; mypy clean on 169 files; exact-revision PEX built and nine packaged checks passed (2026-09-26).
- [ ] Tag `v0.2.15-rc0`, backend publication, downloaded assets verified.
- [ ] Owner acceptance: the failing `project init` command line of 2026-09-26
  rerun on a fresh directory with the downloaded candidate, first with the
  typo, then corrected, reaching `project run`.
- [ ] Local proofs against the downloaded assets per the runbook.
- [ ] Acceptance record, integration to `main`, final tag `v0.2.15`.

## Candidates

None yet.

## Release notes for the GitHub release body

DevCapsule 0.2.15 is 0.2.14 with one fix. `project init` no longer discards
the answers you gave at its prompts when a `--authorize`, `--set` or `--bind`
name on the command line is misspelled: the name is checked before the first
question, nothing is written, and the message suggests the likely spelling
(`docker` → `docker-daemon`). The R-COMPAT-001 exception of 0.2.14 is
unchanged: earlier clients installed vendor downloads without recording
consent; 0.2.14 and later ask once per checkout.
