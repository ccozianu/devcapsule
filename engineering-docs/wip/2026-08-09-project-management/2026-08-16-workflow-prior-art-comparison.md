# Prior-Art Survey: Open Source Human/Agent Workflow Frameworks vs. DevCapsule WORKFLOW.md

Date: 2026-08-15

Scope: Comparison of the WORKFLOW.md human/agent development protocol (as of
`main` on the date above) against the most popular open source projects
covering overlapping functionality.

> **Staleness warning.** This document is a dated snapshot of a fast-moving
> ecosystem. Star counts, feature sets, file formats, and even the existence
> of the projects surveyed here can drift within months. Several of the
> projects below reorganized their command surface or file layout at least
> once in the year preceding this survey. Treat this as a decision-support
> record for its date, not as living documentation. If a decision depends on
> a specific claim below, re-verify against the linked upstream sources
> first. It remains useful anyway: the *structural* comparison (which
> concerns each tool covers, and which it does not) changes far more slowly
> than the numbers.

## What WORKFLOW.md Actually Is

To pick the right comparables, the subject must be named precisely.
WORKFLOW.md is not primarily a spec-generation framework. It is a **durable
project memory and handoff protocol**:

- versioned markdown as the source of truth that survives model changes,
  IDE restarts, and future sessions;
- a workstream lifecycle bound to git topology (register on `main`, work on
  `<mnemonic>/` branches, finalize through pull-request or direct delivery,
  archive on success *or* failure);
- a requirements register with stable IDs and traceability lines;
- two-tier decision records (ceremonial immutable product decisions vs.
  lightweight reversible design notes);
- bug intake, completed-task archives, and session records with capture-mode
  semantics;
- turn-level choreography: slice sizing shapes, evidence-first reporting,
  escalation triggers, checkpoint triggers, and an explicit human/agent
  responsibility contract.

The open source field covers overlapping *subsets* of this. No single
project covers the whole.

## The Comparables

### GitHub Spec Kit

- Repo: <https://github.com/github/spec-kit>
- Scale at survey date: roughly 110–120k stars, MIT license, backed by
  GitHub; one of the fastest-growing developer tools of the period.
- Model: Spec-Driven Development in phases — specify → plan → tasks →
  implement — where each phase produces artifacts the next phase consumes.
  A "constitution" holds project-level principles (loosely analogous to
  AGENTS.md plus the Development Principles section). Ships as a CLI
  (`specify`) with 30+ agent integrations including Claude Code (which uses
  a skills-based integration).

**Covers from WORKFLOW.md:** requirements-before-code discipline,
task/slice decomposition, artifact-driven phases, project principles.

**Does not cover:** session handoff and recovery, the open-workstream
registry, decision-record ceremony, bug and completed-task archives, any
notion of resuming interrupted state. Spec Kit is per-feature and
forward-only; WORKFLOW.md is whole-project and memory-oriented.

### OpenSpec (Fission-AI)

- Repo: <https://github.com/Fission-AI/OpenSpec>
- Model: low-ceremony, markdown-filesystem-based spec workflow, explicitly
  brownfield-first, with no rigid phase gates. Each change gets its own
  folder (`proposal.md`, `specs/`, `design.md`, `tasks.md`) under
  `openspec/changes/<name>/`. On archive, a change's delta specs merge into
  `openspec/specs/`, the accumulating source of truth. Commands are
  `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`; MIT
  license; works across 20+ assistants.

**Structural correspondence to WORKFLOW.md is the closest of any surveyed
project:**

| OpenSpec | WORKFLOW.md |
| --- | --- |
| `openspec/changes/<name>/` | `engineering-docs/wip/<date>-<mnemonic>/` |
| archive merges delta into `specs/` | finalization promotes WIP into permanent categories + `archive/` |
| `specs/` = current truth, `changes/` = proposals | root `docs/` = current truth, workstream `docs/` = drafts/proposals |
| per-change `tasks.md` | active task format with done-means / verification / reopen-if |

**Does not cover:** the git-branch-to-workstream binding, the
open-workstream registry on `main`, session recovery, decision records, bug
intake, the responsibility contract, unsuccessful-completion archival.

**Risk note:** OpenSpec is young and its format churned recently (a rebuilt
"artifact-guided" workflow replaced the original command set). Pinning to
it means tracking a moving target, whereas plain-markdown WORKFLOW.md has
zero dependencies by construction.

### BMAD-METHOD

- Repo: <https://github.com/bmad-code-org/BMAD-METHOD>
- Scale at survey date: roughly 37k stars — second in the field behind
  Spec Kit.
- Model: the maximalist option. An ecosystem of role-based agents —
  analyst, PM, architect, developer, UX designer, technical writer — where
  each role's workflow produces documents that gate the next phase.
  Installed via `npx bmad-method install`; generates AGENTS.md and agent
  YAML for Claude Code, Cursor, and similar tools.

**Covers:** human-gated phase progression, heavy planning artifacts,
adversarial review.

**Philosophical mismatch:** BMAD simulates a whole agile team; WORKFLOW.md
formalizes one human/one agent iteration. It is also notoriously heavy —
one published comparison found the same task took 12 minutes with
OpenSpec, 90 minutes with Spec Kit, and 5.5 hours with BMAD, and reported
substantial token costs and documented brownfield friction.

### The Memory Bank Pattern (Cline canonical; Cursor/Windsurf forks)

- Docs: <https://docs.cline.bot/best-practices/memory-bank>
- Model: a documentation methodology, not a tool. Structured markdown files
  in a `memory-bank/` folder — `projectbrief.md`, `productContext.md`,
  `systemPatterns.md`, `techContext.md`, `activeContext.md`,
  `progress.md` — read at session start and updated at checkpoints, so the
  agent "remembers" the project across sessions. Version-controlled with
  the code. Widely forked (cursor-memory-bank, skill-memory-bank, etc.).

**Correspondence:** this is the closest analog to the `CURRENT-STATUS.md`
handoff specifically. WORKFLOW.md's single-stream mode is essentially a
more rigorous Memory Bank.

**Does not cover:** workstream concurrency, requirements traceability,
lifecycle, delivery policy, recovery — it is thin by design, which also
makes it trivially adoptable.

### Beads (Steve Yegge)

- Repo: <https://github.com/steveyegge/beads>
- Scale at survey date: roughly 18–19k stars; MIT; single Go binary;
  Claude Code plugin and MCP server available.
- Model: the interesting contrarian — it deliberately rejects WORKFLOW.md's
  core premise. A git-backed graph issue tracker giving agents persistent
  *structured* memory, explicitly marketed as replacing "messy markdown
  plans" with a dependency-aware graph. `bd ready --json` returns only
  unblocked tasks, which is more context-efficient than loading whole
  markdown files.

**Covers:** the active-task list, bug intake, and workstream tracking — as
queryable data instead of prose.

**Practitioner-reported caveats** that WORKFLOW.md's explicit core loop and
checkpoint triggers address head-on: agents do not proactively use it,
CLAUDE.md instructions fade by session end, and session handoff still needs
explicit prompting.

### Footnote: ADR / MADR

The Design Decision Records section of WORKFLOW.md is nearly a verbatim
restatement of the long-established Architecture Decision Record practice
(propose / accept / supersede-never-edit, minimum two real options,
immutability once accepted). MADR (<https://adr.github.io/madr/>) and
adr-tools provide mature templates and tooling. This portion has decades of
prior art and could be adopted wholesale.

## Coverage Matrix

Legend: ● covered, ◐ partial, — absent.

| WORKFLOW.md concern | Spec Kit | OpenSpec | BMAD | Memory Bank | Beads |
| --- | --- | --- | --- | --- | --- |
| Requirements/spec before code | ● | ● | ● | — | — |
| Change-unit lifecycle with archive | ◐ (per-feature dirs) | ● | ◐ | — | ◐ |
| Cross-session durable memory | — | ◐ | — | ● | ● |
| Git-topology workstream binding | — | — | — | — | ◐ (git-backed data) |
| Session recovery protocol | — | — | — | — | — |
| Unsuccessful completion as first-class outcome | — | — | — | — | ◐ (close-as-wontfix) |
| Decision records | ◐ (constitution) | — | ◐ | — | — |
| Bug intake with evidence | — | — | — | — | ● |
| Completed-task retrospective archive | — | ◐ | — | ◐ | ◐ |
| Turn-level choreography / reporting contract | — | — | ◐ | — | — |
| Session records with capture-mode semantics | — | — | — | — | — |
| Human/agent responsibility contract | — | — | ◐ | — | — |

## What Is Genuinely DevCapsule's

Found in none of the popular tools at survey date; these constitute
WORKFLOW.md's actual differentiation:

1. **The git-topology binding.** Every non-`main` branch belongs to exactly
   one registered workstream; registration is committed to `main` *before*
   branching; root `CURRENT-STATUS.md` is a registry, not a status; explicit
   rules exist for divergent `main`, invalid routing, and detached HEAD. No
   comparable project ties its process state to git mechanics this
   rigorously.
2. **The recovery protocol.** Enumerate worktrees after interruption; treat
   uncommitted files as recovery material, not canonical status; distinguish
   "pending integration" from "open workstream." Everything else in the
   field assumes happy-path sessions.
3. **Unsuccessful completion as a first-class outcome.** Archiving a failed
   workstream with its evidence and reconsideration conditions. Every other
   framework models only success.
4. **Turn-level choreography and the responsibility contract.** Slice-sizing
   shapes, evidence-first reporting order, escalation triggers, "the human
   chooses the hill to climb, the agent chooses the next safe foothold."
   Spec Kit and OpenSpec structure artifacts; none of the surveyed tools
   structure the *conversation*.
5. **Session records with capture-mode semantics** (detailed / summary /
   verbatim, redaction rules, never-canonical). No equivalent found
   anywhere.

## Adopt-and-Adapt Assessment

Full adoption of any single tool would forfeit the five items above, which
appear to be the point of the exercise. Partial adoption is viable, in
three tiers:

**Adopt outright.**

- MADR templates for the decision-record tier: mature, tool-supported,
  near-identical semantics to what WORKFLOW.md already specifies.
- Possibly OpenSpec's CLI and change-folder format as the concrete
  implementation of workstream WIP directories: markdown-filesystem based,
  no database dependencies, MIT (Apache-2.0 compatible), and its
  propose/apply/archive lifecycle could carry the mnemonic-directory
  convention with modest renaming. Weigh against the format-churn risk
  noted above.

**Adapt / interoperate.**

- Conform to Spec Kit at the vocabulary and file-format level
  (`spec.md` / `plan.md` / `tasks.md`, constitution) even without running
  it, because its star-count gravity means agents are increasingly trained
  on and tooled for its conventions. The requirements register could emit
  or consume its formats.
- Practitioners already layer these tools (e.g., BMAD for inception,
  Spec Kit for feature phases, OpenSpec for brownfield maintenance), so
  positioning WORKFLOW.md as the *session / memory / git layer beneath* a
  spec tool is a defensible niche rather than a redundant one.

**Keep as original work.** The branch-registry binding, recovery protocol,
failure archival, turn choreography, and session records. If the workflow
framework is spun out into its own repository, this subset is what
justifies its existence next to the incumbents; framing it explicitly as
"composes with Spec Kit / OpenSpec, replaces neither" is the strongest
pitch.

The stability-vs-ecosystem trade-off (zero-dependency plain markdown vs.
leverage from a moving upstream) is a real product decision and, per this
repository's own process, warrants a proposed decision record rather than a
default.

## Sources Consulted (as of 2026-08-15)

- <https://github.com/github/spec-kit> and
  <https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/>
- <https://github.com/Fission-AI/OpenSpec> (README, docs/concepts.md,
  docs/existing-projects.md)
- <https://github.com/bmad-code-org/BMAD-METHOD>
- <https://docs.cline.bot/best-practices/memory-bank> and
  <https://cline.bot/blog/memory-bank-how-to-make-cline-an-ai-agent-that-never-forgets>
- <https://github.com/steveyegge/beads> and
  <https://ianbull.com/posts/beads/>
- Comparative surveys: HackerNoon "The Spec-First Development Showdown"
  (2026-05), Reenbit "BMAD vs Spec Kit vs OpenSpec" (2026-05), ArceApps
  "SDD Frameworks Deep Dive" (2026-03), arXiv 2606.04967 "From Prompt to
  Process", specdriven.com landscape pages.

Star counts and version details above were reported by third-party trackers
and articles at survey time and are approximate.