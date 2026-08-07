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

- `requirements/` — canonical engineering requirement records when they are
  migrated from the current structure.
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

## Current Migration State

This structure is scaffolded for the FastAPI demo and multiple-workstream
design effort. Existing requirements, specifications, decisions,
implementation notes, bugs, completed tasks, and session records remain in
their current locations until a deliberate migration can be performed without
disrupting the active recursive dogfood E2E work.

Creating this tree does not adopt the multiple-workstream proposal and does not
change the authority or meaning of `CURRENT-STATUS.md`, `WORKFLOW.md`,
`AGENTS.md`, or any existing requirement.

New documents should be placed according to their primary audience and
authority:

1. Stable product guidance for a DevCapsule user or adopter belongs in
   `docs/`.
2. Repository-wide startup and control documents remain at the root.
3. Contributor or agent engineering artifacts belong in this tree.
4. Within this tree, normative outcomes are requirements, normative technical
   behavior is a specification, adopted choices are decisions, unsettled
   proposals are design notes, and execution or validation evidence is an
   implementation note.
