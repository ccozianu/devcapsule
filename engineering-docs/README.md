# Engineering Documentation

This tree contains contributor- and agent-facing artifacts used to design,
implement, validate, and coordinate the project. It is separate from `docs/`,
which is intended for stable product documentation consumed by DevCapsule
users and adopters.

The root control files remain at the repository root because every contributor
and agent must discover them immediately:

- `AGENTS.md` — mandatory repository instructions;
- `CURRENT-STATUS.md` — authoritative current handoff under the presently
  adopted workflow;
- `REQUIREMENTS.md` — root requirement overview and index;
- `WORKFLOW.md` — authoritative human/agent workflow; and
- `index.md` — repository-wide Markdown documentation index.

## Structure

- `requirements/product/` — canonical repository-wide product requirement
  records.
- `requirements/devcapsule/` — canonical requirements for the active Python
  CLI/framework implementation.
- `specifications/` — normative technical contracts, schemas, protocols, and
  invariants.
- `decisions/` — durable accepted, rejected, deferred, or superseded design
  decisions.
- `design-notes/` — proposals, alternatives, design research, and unsettled
  architecture.
- `implementation-notes/` — execution plans, milestone plans, checklists,
  implementation investigations, and validation exercises.
- `workstreams/` — independently resumable workstream handoffs if the proposed
  multiple-workstream workflow is adopted.
- `bugs/` — active or recently investigated defect evidence and closure
  criteria.
- `completed-tasks/` — retrospective evidence for completed or retired work.
- `session-records/` — explicitly requested, sanitized historical session
  captures that supplement rather than replace canonical artifacts.

Scope-specific subdirectories such as `devcapsule/` and `docker4pycharm/`
separate active implementation records from historical prototype evidence.
These are documentation scopes, not source-tree paths; the active Python
distribution project lives at `devcapsule-src/`. Repository-wide records use
the `product/` scope where a category needs to distinguish them from
implementation-specific material.

## Placement Rules

Place documents according to their primary audience and authority:

1. Stable product guidance for a DevCapsule user or adopter belongs in
   `docs/`.
2. Repository-wide startup and control documents remain at the root.
3. Contributor or agent engineering artifacts belong in this tree.
4. Within this tree, normative outcomes are requirements, normative technical
   behavior is a specification, adopted choices are decisions, unsettled
   proposals are design notes, and execution or validation evidence is an
   implementation note.

Historical records retain their original claims and dates, but links and path
references should point to the current repository location. Moving a record
does not change its status, authority, or validation result.

The `workstreams/` directory remains scaffolded while the multiple-workstream
workflow proposal is evaluated. Its existence does not by itself adopt that
proposal or change the authority of `CURRENT-STATUS.md`, `WORKFLOW.md`, or
`AGENTS.md`.
