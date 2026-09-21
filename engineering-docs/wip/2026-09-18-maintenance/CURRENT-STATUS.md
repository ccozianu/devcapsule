# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused; fixes merged; owner-requested pre-V1 positioning handoff prepared for project-management

Integration target: `main`

Delivery method: pull request

Designated integration branch: `ws-maintenance/triage`. Published branches absorb
`main` by merge; the owner opens and merges the GitHub PR. The agent pushes the
branch only, as explicitly requested on 2026-09-21.

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own the defects that no open workstream covers, on `main` and maintained release
lines, and drive maintenance releases. See *The Reserved `maintenance`
Workstream* in `WORKFLOW.md`.

## Branch Association

Current branch: `ws-maintenance/triage`, fast-forwarded to `origin/main` at
`7d1df73` on 2026-09-21. PR #117 merged the fixes at `d2386bb`; no maintenance
implementation commits remain unintegrated. Live records use `workflow publish`.

## Adoption Exception

The repository adopted multiple streams on 2026-08-08. The reserved maintenance
workstream was defined and created on 2026-09-18 under the workflow's adoption
exception; that is its immutable start date.

## Queue

Read the authoritative queue from bug records with `owner: maintenance`, status
neither `closed` nor `retired`. There are 14 open records at this checkpoint.
The two selected upgrade-recovery/configuration-contract records are `fixed`,
not closed or released. Severity and release targets remain untriaged. The owner
selected this correction ahead of general triage.

## Current State

2026-09-21 owner-requested positioning handoff: saved the
[pre-V1 adopter/contributor assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md),
including the owner's correction that Windows through WSL2 and Docker works;
macOS is untested. The owner tentatively considers a blog entry and assigns
that decision to project-management. Managed agent updates remain a high-priority
owner concern, but making them a 0.2.14 gate has not been accepted. Mail delivery
is the current handoff task; no blog publication is authorized.

Acknowledged the workflow transition notice. Current main and the changed
definition were read, mail was taken, and live publication is part of this
checkpoint. Remaining retired-outbox cleanup is accepted after this handoff;
check that every record landed before deleting any ref. No further workstream
is selected by this acceptance.


2026-09-21 integration handoff: the owner reports that we are now running with
the fixes and that they worked well, and explicitly requests a branch push for
the owner to merge on GitHub. This supersedes the pending primary-dogfood
acceptance next step below at the level of reported successful live use; it
does not establish exact host configuration bytes or exhaustive condition coverage.
The branch absorbed current main without conflicts. No source changes were
needed for this delivery. The maintenance workstream remains open.

Validation after synchronization: `nox -s build` passed with **915 tests**, one
existing expected failure and 18 host-sensitive cases deselected, mypy, source
CLI smoke, local PEX construction and **nine packaged-executable tests**.
Log: `/tmp/maintenance-integration-build.log`. The gate built the local validation
artifact; revision-bearing packaging was skipped because handoff records were
being updated. `git diff --check` passed. No additional GUI run was needed for
this records-only handoff beyond the owner's live-use confirmation.

2026-09-21 graphical acceptance complete: the owner confirmed, "Yes, everything
went fine." Independent Docker inspection records the exact successor as
`exited`, code **0**, `OOMKilled=false`, zero restarts, finished
`2026-09-21T00:16:49.505703772Z`. The separate `docker wait` observer also
returned **0**. No agent stop/kill was issued. The original 0.2.12 control remains
running. The graphical 0.2.12-configuration → 0.2.14.dev0 successor scenario is
accepted; the stopped test container and owned run remain as evidence, including
`candidate-gui-acceptance.json`. This acceptance does not claim that the primary
host checkout has been migrated or that remaining unit-coverage gaps vanished.

2026-09-20 scope correction: the owner requested the graphical recursive
successor, not only the preliminary Nox suite. Calling that earlier subset
"recursive E2E passed" overstated completion. The component-catalog acceptance
record already documents this distinction; future runs must include the existing
`launch-successor` and independent `inspect-successor` continuation.

**The graphical successor launched and passed independent inspection; GUI acceptance and normal exit are now verified above.**
Used the existing owned local-clone protocol to create an independent clean
checkout at `a785a332b05d7e25685f46d47a68b0545810488c`, without local origin,
credentials or copied developer environment. Bootstrapped a fresh contributor
venv and passed the complete clean-clone `nox -s build` gate (910 tests, one
existing xfail, 18 deselected, mypy and nine packaging tests), including creation
of the exact-revision 0.2.14.dev0 PEX.

The actual embedded **0.2.12** CLI authored and resolved the run's isolated
checkout decisions and bindings. The new **0.2.14.dev0** CLI then admitted,
materialized and launched those files directly. Both predecessor files remain
byte-identical after launch and inspection. Home, IDE and agent state are fresh,
run-owned directories; no personal profile or credentials were copied. The
explicit recursive scenario decisions enable Docker, host networking, development
sudo, the inherited host-browser bridge and native X11. No host-global
configuration was changed. The pinned recipe-9 base was reused per D-0009;
the materialized environment contains the new launcher's exact executable bytes.

Retained evidence and identity:

- Run `c2c487f429e3403740ebc66f182293eb` beneath
  `~/.local/share/devcapsule/e2e-workspaces/`.
- Container `devcapsule-e2e-c2c487f429e3403740ebc66f182293eb-successor`, ID
  `95b72194b80389b46af6496b8f3289ca24351623e77f5b0f8ac13cc3f517cbb6`.
- Image `sha256:2eaf3ae53b6b37cd3642c6cdc2bb5f6bc7f3417506ba596980ec1ffb6f5f14e4`;
  canonical formation `0e6cbaeff005e1db0f58dae5977d4cea5e814ec1d5e5188a02228e9914f6eb3c`.
- Base `sha256:8221b27a44acbf44e9fb8be74bfaf7d533e80e696b5fff9c81e508a322e5306d`;
  the committed registry digest remains unchanged.
- New launcher and embedded runtime SHA-256 both
  `e74d5fdebba1cfdaa197119ae537292c6aba2e173913552869c5cfb2600e406f`.
- Public independent inspection passed exact image/formation/container identity,
  mounts, environment, security/resource/restart settings, supervised PyCharm,
  runtime-plan read-only mount and digest, run ID and installed tool versions.
  Additional probes verified the embedded version/revision/checksum, Docker
  daemon access, noninteractive sudo, and stable identity with zero restarts in
  a second sample ten seconds later. The original 0.2.12 control remains running.

The owned run retains `candidate-command.py` and its private environment for
repeat public inspection, the owner marker/manifest/expected plan, predecessor
snapshots, build/configure/materialization/launch/inspection logs and
`candidate-runtime-evidence.json`. `gui-exit-code` is written by an independent
`docker wait` observer and now contains `0`. The stopped container, run/state
and staging are retained as acceptance evidence. Manual visibility/usability and
normal GUI exit are complete; no primary dogfood migration is claimed.
This is a real 0.2.12-generated test checkout, not a copy of the unavailable
host-owned configuration. The broader unit-coverage qualification below remains.

### Earlier preliminary-suite checkpoint

2026-09-20 recursive acceptance requested by the owner: ran
`nox -s recursive_dogfood_e2e` against clean source
`85bec27a9bc79d1334b6ce04218afa666cc1373c`. **Passed: 2 tests, 7 deselected**
in 95.96 seconds, after successful preflight and staging dry run. These tests
prove contributor bootstrap in a disposable base container and independent
local cloning; this session does not launch an upgraded IDE or test migration
of the host's saved configuration. The disposable container and owned workspaces
were cleaned by the tests. Log: `/tmp/maintenance-recursive-e2e.log`.

The focused configuration/recovery rerun passed **290 tests**. Existing full-gate
coverage measures **92% combined statement/branch coverage across configuration/**;
model, review, resolution, fingerprints and history have 100%, while authorization,
ordinary/binding validation, serialization, persistence and edit orchestration
still contain uncovered paths. The documented law/case map is valuable evidence,
but does not justify the owner's requested whole-configuration "fully tested"
assurance. Log: `/tmp/maintenance-configuration-check.log`; coverage detail:
`/tmp/maintenance-configuration-coverage.json`. No source changes in this slice.
The final required `nox -s build` also passed: 910 tests, one existing expected
failure, 18 deselected, mypy, CLI smoke and nine packaged-executable tests.
Log: `/tmp/maintenance-recursive-checkpoint-build.log`. This gate rebuilt only
the local PEX because these records were dirty; the separately built exact-revision
`dist/devcapsule.pex` remains unchanged.

Built `devcapsule-src/dist/devcapsule.pex`, reporting **0.2.14.dev0** and the exact
source revision above. SHA-256:
`04bd75e63d88e7feaec0cd26bda54075bb619cd5083c47609a7dc1197d295bb9`.
The current embedded runtime reports **0.2.12**, revision
`2916c4c09aee13eeed85276c1a32889515ce7b19`. It remains running; no successor was
launched and no base was repinned. The host's checkout/resolution files are not
mounted here. A `config list` probe found no capsule-local registration and
created two empty placeholders; their exact empty contents were verified and
both files removed. Existing host choices were neither read nor changed.

### Earlier source-layout checkpoint

2026-09-20 source-layout follow-up: configuration now lives under
`devcapsule/configuration/`, with an explicit value API and separate domain,
assessment, resolution, storage, execution and lifecycle modules. The former
1,477-line `project_configuration.py` is split by responsibility. Internal
configuration imports are acyclic; the core does not import storage/lifecycle
adapters or launch machinery. The former `configurations/pycharm` package is
now `launch/pycharm`, with its CLI grammar under `commands/_pycharm.py`.
Configuration tests are grouped under `tests/configuration/`; two architecture
checks guard the dependency direction and absence of cycles, including local
imports. The developer brief documents the resulting hierarchy and public API.

Validation: **`nox -s build` passed: 910 tests, mypy over 153 source files,
CLI/PEX smoke and nine packaged-executable tests**. Eighteen host-sensitive
cases remain deselected and the unrelated expected failure remains. The 30 ADT
laws and two architecture checks also passed after consolidating the ADT tests'
public imports. Structural comparison found all 112 moved configuration
functions/classes unchanged apart from imports. Historical fixture bytes are
unchanged. All 66 qualified test references and maintenance document links were
checked. Gate log: `/tmp/configuration-layout-build.log`.

The stray initial test-file character had already been removed by the owner's
undo before source edits began; no independent user edits were discarded.
This is a first logical package boundary, not a claim that every remaining
root-level module has already been reorganized.

### Earlier ADT review checkpoint

2026-09-20 owner-review follow-up: replaced the launch-mechanics compatibility
claim with an admission/resolution ADT and semantic laws. `Configuration` owns
its input snapshot; `Resolution` owns the derived plan. Both the real resolve
operation and execution adapter use this boundary. The distinction between
plan meaning and freshness is explicit (`same_meaning_as` is not object equality).
Thirty ADT cases cover predecessor admission/meaning, repeated derivation,
observation and ownership, dependency scope, security-question changes, force,
unsupported representations and plan integrity. They invoke no CLI or launcher
mocks. File-byte preservation is separately checked through the CLI adapter.
Set/bind/authorize/unset remain the existing edit API; this follow-up does not
claim to encapsulate those operations in the new ADT.

Validation: final `nox -s build` passed: **907 tests, mypy over 143 source files,
source CLI smoke, PEX build and nine packaged-executable tests**; 18
host-sensitive tests deselected and one pre-existing expected failure. The
final ADT module rerun passed **30 cases**, including the additional absent-base
observation case added after gate collection. Combined coverage is 100%
statements/branches for `configuration.py`, `configuration_documents.py`,
`configuration_review.py` and `configuration_resolution.py` (345 statements,
112 branches). This is not proof of the entire configuration implementation.
Logs: `/tmp/configuration-adt-build.log` and `/tmp/configuration-adt-laws.log`.
The updated proof map separates semantic laws, representation checks and adapter
checks. Historical 0.2.11 data is still interpreted by current source; no test
executes original 0.2.12 or reconstructs the incident's unavailable inputs.

### Earlier refactor checkpoint

2026-09-20: completed the owner's instruction to carry the full configuration
contract through into implementation, rather than stop at the audit. The owner
explicitly supplies serialized access to the underlying configuration files
within and between processes. No cooperative lock is needed under that condition.
This instruction supersedes the consent-conflating portion of the earlier interim
init behavior; project ownership of manifest/lock regeneration is unchanged.

The refactor establishes:

- common artifact admission, supported-format and checkout-identity checks;
- a whole-document checkout writer that preserves unrelated answers, refuses
  unsupported structure, and uses private staging with atomic replacement;
- one registry for node names/effects, shared set/bind operations for init and
  individual edits, and separate identity/configuration elicitation namespaces;
- complete node assessment and a pure generated-plan projection;
- typed effective host decisions, including legacy decisions and run-once
  precedence, with no permission resurrection through unset or stale output;
- one execution admission boundary and a lower launcher that cannot add ambient
  legacy privileges, credential sources or host paths to a project plan;
- scoped manifest freshness and compatible interpretation of released unscoped
  fingerprints, without repinning or rewriting standing user choices.

At that checkpoint all nine audit gap families were fixed. The original audit module has 45 passing
cases, with all ten expected-failure markers removed. The new invariant module
has 128 passing cases, including the related composition consequences identified
while implementing the contract. The recovery journeys remain, with client-only semantics now tested by the ADT laws.

Validation: `nox -s build` passed with **877 tests, mypy, source CLI smoke, PEX
construction and nine packaged-executable tests**. Eighteen host-sensitive tests
were deselected; one unrelated pre-existing expected failure remains. Separately
measured statement/branch coverage is 100% for `configuration_documents.py`
(69 statements/42 branches), `configuration_review.py` (149/34), and
`configuration_resolution.py` (57/26; its impossible missing-selection guard is
excluded). This is not a claim that all CLI code has 100% coverage. The full
[correctness argument](configuration-correctness.md) maps the contract's condition
partitions to tests and states assumptions and external acceptance limits.
Changed document links and all 64 named test references were verified.

Historical checkpoints: `6709756` implemented the bounded upgrade recovery;
`4f5091e` recorded the complete contract/audit. The current continuation repairs
that audit and replaces its intentionally failing obligations with passing tests.
The selected status and document revisions supersede the audit-only handoff.

## Planned Next Step

Project-management decides whether and when to turn the delivered assessment
into a blog entry or adopter invitation. In maintenance's next selected slice,
reconcile the two fixed records with merged implementation and live-use
acceptance, triage remaining bugs, and finish retired-outbox cleanup. Broader
configuration coverage and the 0.2.14 update-feature gate remain undecided.

## External State And Risks

The recursive session created its Nox environment and a disposable contributor
container using an existing base; the tests removed their container and owned
workspaces. That preliminary run launched no successor; the subsequent graphical run above
now retains its stopped successor and owned state after accepted normal GUI exit. The existing `devcapsule-src/.venv`
also ran 290 focused tests and built the revision-bearing local contributor PEX
recorded above; it is not a published release artifact.
The implementation and earlier records delivery are integrated into remote
`main`; PR #117 is verified at `d2386bb`. This checkout fast-forwarded to
`7d1df73` for the changed workflow definition before preparing the handoff. Mail retrieval found no maintenance mail;
intake contains only its README. The new live list initially had no published
workstream state, so the fetched mainline registry supplied the routing fallback.
No mail was sent.

## Open Threads

### Awaiting The Product Owner

- Project-management decides on the tentative blog and adopter invitation.
  The owner has not decided whether managed updates gate 0.2.14. Successful
  live use is owner-reported; exact host configuration bytes remain unavailable.
- Severity/release triage for the remaining queue, including ownership of fixes
  from workstreams approaching closure.

### Weighed And Unresolved

- The full configuration contract is still an engineering document. Making it
  canonical developer-user documentation needs an editorial/publication pass;
  the preceding review identified that work but did not publish it.
- This source-layout slice groups configuration and distinguishes launch/CLI
  adapters. Other top-level subsystems retain their existing locations.
- General workstation policy/default overlays, lockless-consumer UX, identity
  relocation and a comprehensive historical recipe policy are future product
  boundaries explicitly separated from this V1 correction.
- Concurrent configuration access is excluded by the owner's precondition;
  do not add a locking protocol without a concrete need to change that condition.
- Exact incident-era inputs/build logs remain unavailable; real predecessor
  fixtures and complete recovery journeys provide the recorded unit evidence.

### Deliberately Not Preserved

No verbatim transcript was requested. The owner explicitly requested saving
the adopter/contributor opinion; the linked assessment preserves that discussion
and the Windows correction. The contract, tests and bug records retain the
implementation evidence.

## Workstream Document Index

- this status file;
- [pre-V1 adopter/contributor assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): open for the owner-requested project-management/blog decision;
- [upgrade recovery contract](upgrade-recovery-contract.md);
- [configuration lifecycle contract](configuration-contract.md);
- [configuration correctness and test map](configuration-correctness.md);
- [intake dispositions](intake-dispositions.md); and
- the adjacent `intake/` directory.

Bug records remain under `engineering-docs/bugs/`, indexed in root `index.md`.
