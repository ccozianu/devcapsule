# DevCapsule 0.3.0 — Release Work

Updated: 2026-10-18. Stage: **cut; candidate 0 in preparation**.
Driver: **maintenance**. Product owner: Costin Cozianu.

[Bug table](bugs.md) ·
[Work order](../../work-orders/2026-10-18-release-0-3-0.md) ·
[Scope and cut decision](../../wip/2026-08-09-project-management/2026-10-18-decision-release-0-3-0-scope-and-cut.md) ·
[Runbook](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)

Update this file as decisions and evidence arrive. Chat highlights changes
and questions; the bug records remain authoritative for individual status,
ownership and technical evidence; the maintenance status file links here
for resumption.

## Headline

The capsule web console, persistent session diagnostics, and a launcher
that is honest about what it skips.

## Scope And Owner Decisions

- **Cut now**, decided 2026-10-18 after the inventory of what the plan still
  had unimplemented: a candidate of what exists is worth validating, and
  the candidate cycle is the better place for the remaining launcher work,
  with 0.2.14 as the precedent. `main` stays at `0.2.16.dev0` until the
  final tag, then reopens at `0.3.1.dev0` unless the owner names another.
- **Dogfooding during the cycle.** Six items are implemented during the
  candidate cycle, each a maintenance slice with the implementor-and-reviewer
  loop, landing on the release branch by the owner's direction and reaching
  `main` by the merge before each candidate tag: the universal `network`
  authorization node; C10, the first-session terminal summary and Ctrl+C
  ending with a result; forced configuration, `project config resolve
  --force` and `project run --force-config`, mandatory needs split from
  optional ones; the diagnostics snapshot and export command; cleanup of
  obsolete images and cached files, design reviewed with the owner first;
  C20, release notes and documentation automation, last. Features landing
  on a release branch during a candidate cycle are the owner's direction
  for this release, as the decision asks this overview to record; a
  standing local rule is `workflow-improvements`' to propose if it recurs.
- **Out of 0.3.0:** consent and vendor trust (D-0010 to D-0013,
  `component-upgrades`); installed-IDE reuse with an empty launcher cache;
  browser evidence for the diagnostics; the web console's deliverable 6,
  materialized views; ecosystem-aware project bootstrap, retargeted to 0.9
  on 2026-10-11 and applied with the cut. Their next home is 0.3.1 or the
  next cycle, decided at that planning.
- **Gates before the final tag:** the owner's eleven user-docs proposal
  decisions, the gate of 2026-09-28; the documentation describing the
  accepted candidate, C16; a published base for the candidate, since the
  console needs recipe 11; the fixed bug records verified against a
  downloaded candidate; the release notes as `notes.md` beside this file.
  Project-operation instructions, C17, stay assigned to
  `workflow-improvements` for 0.3.0 and gate the final tag.
- **Stopping points where the owner is consulted:** before each candidate
  tag; before the image-cleanup implementation; when a slice proves larger
  than the cycle tolerates; before the final tag. Scope changes go by the
  decision record's reopen rule.
- Routine release-fix propagation to `main` follows the runbook's *Release
  Fixes And Main* under the owner's standing direction of 2026-09-22.

## What `main` Carried At The Cut

Integrated between `v0.2.15` (final 2026-09-27) and the cut commit, by the
merges on `main`'s first parent:

- The capsule web console, first iteration (#184, #190) and the second
  (#192 to #206, delivered through #201 on `main`), with the notifications
  and decisions groups under `project checkout`.
- Persistent session logs: one file per component, a WARNING baseline, a
  host-backed directory per session (#207); in-process rotation and one
  budget per checkout (#209, #216).
- Maintenance after 0.2.15 (#164, #168, #169, #172): the fresh-workspace
  recursive test, the in-capsule project-command fix, named build contexts,
  the unpacked-cache corrections.
- IntelliJ IDEA and the configuration contract commands from
  `component-catalog` (#163 to #173).
- The user documentation of 43 pages, the website producer migration and
  the versioned documentation live on the site (#151 to #158), the landing
  page identity and the comparison (#219, #221, #222).
- Workflow and coordination records from `project-management` and
  `workflow-improvements` (#159, #162, #176 to #183, #214, #215, #220).

## Agent Freshness Review

Owner direction of 2026-09-27, applied to every release: try to upgrade the
supported agent CLIs to their current generally available versions. The
vendor pointers were read on 2026-10-18 at 12:59 UTC, with the sources the
0.2.15 review used.

| Agent | Current pin | Vendor current | Source consulted | Disposition |
|---|---|---|---|---|
| Codex | 0.157.1 | 0.163.0 | [OpenAI npm latest](https://registry.npmjs.org/@openai/codex/latest) | candidate; upgrade attempt is the next step |
| Claude Code | 2.1.283 | 2.1.302 | [Vendor latest channel](https://downloads.claude.ai/claude-code-releases/latest) | candidate; upgrade attempt is the next step |
| Antigravity CLI | 1.2.12 | 1.4.2 | [Vendor Linux amd64 manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json) | candidate; upgrade attempt is the next step |

Every vendor is ahead of the pin. The attempt follows the 0.2.15 practice:
acquire the exact artifacts through the trusted component mechanisms,
verify checksums and platform compatibility, regenerate the golden locks,
and validate configuration defaults, an ordinary tool action and state
persistence on the selected versions before accepting new pins; record a
reason and a follow-up for every holdback. Whether rc0 ships the new pins
or the current ones is the owner's word before the tag; the pointers are
rechecked before final acceptance, and a version that appears meanwhile
gets an adopt-or-hold decision here, never a silent replacement.

## Preparation And Publication

- Release branch `release-0.3.0` starts at the preparation baseline
  `3c91183ffd2130f6c7b40d2f9e3fd41588f977eb`, `main` at the merge of PR
  #223, selected by the driver: nothing of maintenance was unmerged, and
  the commit carries the decision and the work order. Version 0.3.0 at
  `6965c5e`, the branch's first commit, by `nox -s bump -- 0.3.0`.
- [x] Cut, version, the work order acknowledged, the bootstrap record
  retargeted, the registry row and the status file on the release branch.
- [x] Full gate on the release branch at the version commit: distribution
  version, syntax, mypy clean over 214 files, 1584 unit tests passed, CLI
  smoke, test PEX built and smoked, packaging integration 17 passed; the
  documentation contract passed after the manifest's release-branch line
  (`source-version: "0.3.0"` on the `devel` entry, a judgment recorded in
  the status file and mailed to project-management as a contract gap); the
  web console session mypy clean over 8 files, 293 tests.
- [ ] Agent freshness upgrade attempt; dispositions in the table above.
- [ ] Push the release branch; pull request to `main`; the owner merges;
  ancestry verified on remote `main`.
- [ ] On the owner's word, tag `v0.3.0-rc0` on the release branch's tip;
  backend run; the three assets downloaded, checksum and version verified.
- [ ] Local proofs against the download: clean machine, component cache,
  runtime session on the pinned base.
- [ ] The dogfooding slices, each merged to `main` before the next
  candidate tag; the bug records closed on candidates.
- [ ] The gates before the final tag; `notes.md`; the acceptance record;
  the final tag; delivery verified; `docs/versions.yaml` promoted on `main`.

## Candidates

### RC0 — in preparation

Not yet tagged. The gate on the release branch and the freshness attempt
precede the pull request to `main`; the tag waits for the owner.

## Release Notes Preparation

Write `notes.md` beside this file before the final tag: plain Markdown for
adopters, what changed for them, compatibility exceptions with remedies,
the tested agent versions and holdbacks from the freshness review, the
deferred items. C20, the last slice of the cycle, makes the notes block and
the manifest promotion need no operator step.
