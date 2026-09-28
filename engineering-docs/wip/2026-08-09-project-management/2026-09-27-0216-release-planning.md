# Release 0.2.16: Planning Proposal

Date: 2026-09-27. Owner: `project-management`.
Status: **proposed**; every scope, driver and sequencing item below awaits
the product owner's decision. Nothing here registers 0.2.16, opens a
workstream, or commits a release date.

Prepared at the owner's direction while `maintenance` releases 0.2.15 from
another checkout. It answers one question: what is reasonable to implement
for 0.2.16, given what `main` already carries, what 0.2.15 leaves behind,
and what the intake queue has been asking for.

## Starting Position

Facts checked on 2026-09-27 against `origin/main` at `0cb4b0a`,
`origin/release-0.2.15` at `8028a11`, and the live coordination state.

1. **0.2.15 is in flight, cut from the `v0.2.14` tag, not from `main`.** Its
   accepted scope is the init fix, persistent `/opt/xtras`, read-only
   `project info`, Claude and Antigravity permission defaults, and the
   owner-directed attempt to upgrade the three agent CLIs. Only the init fix
   is on `main` today; the rest lives on `release-0.2.15` until maintenance
   arranges its main disposition. See the
   [0.2.15 overview](https://github.com/ccozianu/devcapsule/blob/8028a114a4ef2df4a1d70ef25c8e4c0720dd0d14/engineering-docs/releases/v0.2.15/README.md) on that branch.
2. **`main` since `v0.2.14` already carries work that 0.2.16 ships by
   construction**, because an ordinary release is cut from `main`:
   - base images named by their contract, consent bound to the image, and
     a compatibility report in `config show` (`5051f4f`), which also
     retires the `v0.2.12-rc5` label that confused the first-session guide
     and the 0.2.14 close-out;
   - the image modules moved into `devcapsule.images` (`3692950`);
   - the init fix (`74bc4aa`, PR #143) and two bootstrap bug records.
   None of this has had downloaded-candidate acceptance. 0.2.16 is the
   release that validates it.
3. **Bug inventory:** 13 nonterminal records. Seven owned by `maintenance`
   carry no target; the in-capsule command-guard bug was explicitly deferred
   out of 0.2.15 for later triage. One record, the website-link opening bug
   owned by `contained-display`, still names target `0.2.14`, which has
   shipped; its target needs correcting by its owner.
4. **Intake:** 25 undecided items in this workstream. The ones that bear on
   0.2.16 are mapped to candidates below; the rest are decisions, not
   release content.
5. **The ledger's release direction stands:** V1 is a workspace-and-containment
   release judged against a candidate, not a calendar. 0.2.16 is a step
   toward it, not V1.

## Candidates

Size is a reasoned estimate from the records, not a measurement. "Owner if
accepted" names the workstream that would implement, following the rule that
`maintenance` fixes defects and drives releases but does not build features.

| ID | Candidate | Source | Size | Owner if accepted | Recommendation |
|---|---|---|---|---|---|
| C1 | Candidate acceptance of the base-contract naming and consent binding already on `main` | `5051f4f`, `3692950` | validation only | release driver | **In**, by construction; the first acceptance obligation of the release |
| C2 | 0.2.15's additions reach `main` before the cut: xtras, `project info`, agent defaults, agent pins | 0.2.15 overview; rc0 exception record | merge or port, small | `maintenance` | **In**, as the cut's prerequisite; without it 0.2.16 would regress 0.2.15 |
| C3 | Agent freshness review as a standing runbook section, executed for every release | intake 2026-09-27 (owner direction) | runbook edit: hours; execution: per release | `project-management` writes it; the driver executes | **In**; acknowledged today as a task of this workstream |
| C4 | Release notes as a release artifact: `releases/<tag>/notes.md` required by the final gate, passed to the GitHub release body, 0.2.14 backfilled; the website page later through W12 | intake 2026-09-26 | gate and backend: days; notes: hours | `maintenance` for gate and backend; `user-docs`/website for the page | **In** for gate, backend and backfill; page deferred to the website contract |
| C5 | Named build contexts so a launcher change no longer transfers 4.8 GB | 0.2.15 plan item 1; installed-IDE reuse bug | days, bounded | `maintenance` | **In**; the owner's daily rebuild cost, root cause recorded |
| C6 | `v0.2.12-rc5` mnemonic shown as the base's name | 0.2.15 plan item 2 | none | none | **Covered by C1**; verify at acceptance, no separate work |
| C7 | Choosing the newer recommended base per checkout from `project config`, and `config list` rendering by the configured schema | 0.2.15 plan item 3; intake 2026-09-13 and 2026-09-14 | unknown until C1 is inspected | `component-upgrades` under R-UPGRADE-001 | **Not committed**; inspect what C1 already answers, then decide the remainder |
| C8 | In-capsule `project <unknown>` guard diagnostic | bug 2026-09-26, minor, deferred from 0.2.15 | small | `maintenance` | **In** |
| C9 | Triage the seven untargeted `maintenance` bugs so severity and target mean something | early-adopter input, item 1 | an owner afternoon | `maintenance` with the owner | **In**, before the cut; decides which of the seven join C8 |
| C10 | First-session UX: a concise ready/stopped/error summary instead of streamed desktop diagnostics; Ctrl+C ends with a result, not a traceback | intake 2026-09-15, items 2 and 3 (item 1 is closed by C1) | small each | `maintenance`, as bug records | **In**; file both as bugs with target 0.2.16 |
| C11 | Checkout-naming default: the directory's last component when unique; a vanished default record does not hold the slot | intake 2026-09-25, item 2 | small | `maintenance` | **In if adopted**; the owner ruled the current behavior not a bug, so this is a product choice |
| C12 | IntelliJ IDEA as a second JetBrains surface on the existing adapter | 0.2.15 plan, owner's surface wish | days | a feature workstream, not `maintenance` | **Owner's option**; the one surface that fits a short release. VS Code, Eclipse and the Antigravity IDE are out of 0.2.16 |
| C13 | Managed agent-CLI updates and the upgrade experience (messages, obsolescence, pin advance) | intake 2026-09-03, 2026-09-21 adopter story ("utmost importance") | design first; implementation is V1-sized | `component-upgrades` | **Out of 0.2.16 implementation**; propose a bounded design slice to start in parallel, so 0.2.17 can carry the first piece |
| C14 | mycodespace direction and this repository's submodule migration | intake 2026-09-25, item 1 | decision | owner | **Decision, not release content** |
| C15 | Legacy launch capabilities L1-L13 and the configuration-free-directory question | work order 2026-09-22; V1 gate | decision session first | owner, then assigned | **Decision session, not 0.2.16 implementation** unless the session selects a slice |
| C16 | Refresh the first-session guide, still pinned to v0.2.12, to the released versions | guide; early-adopter input item 2 | hours to a day | `user-docs` | **In** as the release's documentation; no code |
| C17 | Workflow doctor, review policy, adopter inheritance | `workflow-improvements` plate | that workstream's pace | `workflow-improvements` | **No gate**; ships if merged before the cut |
| C18 | Repository hygiene: retired branches | 0.2.15 plan item 5 | none remote | none | **Done** on the remote (`f1254e9`); local leftovers are each checkout's own |
| C20 | Release tooling for the documentation obligations now in the runbook: the backend takes `releases/<tag>/notes.md` as the release body and refuses a final tag without it; the final tag triggers the website's test deployment and candidate | design issue 2026-09-28, runbook *Documentation Is Part Of The Release* | days | `maintenance` | **In**; the runbook obligations are operator steps until this lands. Subsumes the gate and backend half of C4 |
| C19 | Early-adopter invitation, contributor front door, README wording, blog entry | intake 2026-09-21 (two items) | positioning | owner | **Decision**; 0.2.16 is a plausible release to invite on, which is a reason to keep its scope short |

## Recommended Scope

**0.2.16: what `main` already carries, made releasable, plus the bounded
cleanup 0.2.15 set aside.** Concretely C1 through C5, C8 through C10, and
C16, with C11 and C12 as the owner's options.

Why this shape:

- The base-contract change is on `main` and cannot be left unreleased for
  long without every later change riding on unvalidated ground. Releasing it
  soon keeps the gap between `main` and the shipped launcher small, which the
  0.2.14 cycle showed matters: released clients broke on this repository's
  own manifest because `main` had moved.
- The cleanup items have recorded root causes and small blast radius. They
  were ruled out of 0.2.15 only to keep that release to a fix, not on merit.
- The release-notes artifact closes a gap the owner has now met twice, and
  lands the runbook obligation before the release that would be the first
  to invite outsiders.
- Nothing on the list opens a new design surface. The three large questions,
  upgrade experience, mycodespace and the legacy capabilities, are decisions
  the owner makes; putting any of them into 0.2.16 as implementation would
  make it a V1-sized release rather than the next step.

Rough size: about one to two weeks of pair time after 0.2.15 is final,
counting acceptance; IntelliJ adds days on top if chosen. The uncertainty is
mostly in C4 and C5, neither of which has been designed in code yet.

## Driver And Cut

- **Driver: `maintenance`**, for continuity with 0.2.14 and 0.2.15 and
  because the headline, base-contract validation and cleanup, is its
  subject. Under *Taking A Release Over*, a feature headline would name a
  feature workstream instead; if the owner makes IntelliJ the headline, the
  surface workstream drives and maintenance contributes the fixes.
- **Cut from `main`**, as an ordinary release, after C2 has landed. This
  release does not repeat 0.2.15's cut-from-tag exception, so its candidate
  gate passes by ancestry.
- **Cut trigger:** when C2 and C5 are on `main` and C9 is done, not a date.
  If the owner wants a calendar bound, one to two weeks after 0.2.15's final
  tag is consistent with the estimate above.
- **IntelliJ, if chosen,** is built on its own workstream branch and merged
  to `main` before the cut, like any other content. The cheapest home is a
  bounded `ide-surfaces` workstream that absorbs the registered but unscoped
  `eclipse-surface`; opening one is a lifecycle decision for the owner.

## Decisions Asked Of The Owner

1. Adopt the recommended scope, C1 to C5, C8 to C10 and C16, or amend it.
2. C11, the checkout-naming default: adopt the proposal or keep today's rule.
3. C12, IntelliJ: in or out of 0.2.16; if in, whether to open a bounded
   `ide-surfaces` workstream for it, folding `eclipse-surface` in.
4. Driver: `maintenance`, or a feature workstream if IntelliJ is the headline.
5. C4 and C20: the notes artifact is adopted as content under the owner's
   2026-09-28 grant and the runbook now requires it before a final tag; the
   decision left is the release-tooling automation in C20 for 0.2.16.
6. C13: start a design slice for managed agent updates in `component-upgrades`
   now, in parallel, without a 0.2.16 commitment.
7. Schedule the two decision sessions that are not release content: the
   legacy capabilities L1-L13 (C15) and mycodespace (C14).

Once decided, this workstream registers 0.2.16 in the registry, delivers the
scope to the driver by mail as a work order, files the C10 bug records, and
dispositions the intake items each decision settles.

## Intake Items This Plan Touches

Each is decided only when the owner's decision above lands, and recorded in
the disposition log then, not now.

| Intake item | Candidate |
|---|---|
| 2026-09-27 recurring agent release review | C3, acknowledged 2026-09-27 |
| 2026-09-26 release notes artifact | C4 |
| 2026-09-25 mycodespace and checkout naming | C14, C11 |
| 2026-09-22 V1 legacy launch capabilities | C15 |
| 2026-09-15 first-session UX | C10 |
| 2026-09-14 config offers the recommended base; 2026-09-13 config list schema | C7 |
| 2026-09-03 upgrade experience; 2026-09-21 component status reliability; 2026-09-21 pre-V1 adopter story | C13, C19 |
| 2026-09-21 release and early-adopter input | C9, C16, C19 |
| 2026-09-18 and 2026-09-22 branch migration; 2026-09-21 definition-changed notice | overtaken by the 2026-09-25 migration and this workstream's publication; to be acknowledged as done |

## Addendum 2026-09-28

The documentation-currency design issue and the two work orders of
2026-09-28 changed two things here: C20 was added, and C4's decision
narrowed to automation. The website publication that documents 0.2.15 is
not gated on 0.2.16; 0.2.16 is the first release whose runbook carries the
documentation obligations, so its driver should budget for them.

## What This Proposal Does Not Decide

V1 acceptance criteria, the ledger's undecided rows, the WOW assessment,
and the R-UPGRADE-002 operational objectives. They remain in the
coordination queue in the order the status file records.
