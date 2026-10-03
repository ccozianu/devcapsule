# Information Model

*For humans.* This file explains; the rules are in `WORKFLOW.md`. An agent
skips it in ordinary work and reads it when the question is what kind a
thing is.

The big picture of the workflow, for people. `WORKFLOW.md` beside this file
holds the rules an agent works under and is long by necessity; this file is
short by design and says what kinds of thing the workflow stores, how they
relate, and how a thing moves from one kind to another. Nothing here is a
rule that `WORKFLOW.md` does not also state or point at; a reader who wants
the marching orders reads that file, a reader who wants to understand them
reads this one first.

The model is written in the spirit of the higher-order entity-relationship
model of Thalheim and Schewe, chosen because it describes records like ours
without forcing them into tables. You need none of the theory to read what
follows, only its five words. An *entity* is one thing the workflow stores,
such as this bug record; an *entity type* is the kind it belongs to, such as
bug record. A *relationship* connects entities, and a *relationship type*
says which kinds it connects and how many of each, such as "owns, over
(workstream, bug record), exactly one workstream per bug." A relationship
may be *higher-order*: one of the things it connects is itself a
relationship, such as a release delivering a work order's scoping of a
requirement to a workstream. Everything below is said in those terms, in
plain sentences, and the diagrams, when they come, will be drawn from the
text rather than the other way round.

```text
            a wish, a report, a hand-over
                        │
                   intake item ──── forward ──► project-management
                        │
        ┌───────────────┼───────────────────┐
        ▼               ▼                   ▼
  backlog entry     bug record         task, in a status file
   (priority)     (severity, target, owner)
        │               │
        │ accepted      │ threatens
        ▼               ▼
   requirement ◄────────┘
        │ explained by a decision record
        ▼
    work order ──► workstream ──► deliverable ──► release record
                                                  (acceptance evidence, notes)
```


Everything the workflow stores is one of a small number of kinds. Each kind
has one home, controlled fields where a question must be answerable from the
fields alone, and a fixed set of things it may point at. This section is the
map: the kinds, how a thing moves from one kind to another, and the test
that tells a bug from a feature. A document that fits no kind is a project
document, and the local workflow file names its kind. The *Glossary* in
`WORKFLOW.md` defines the words; this file defines the relations.

## The Kinds

| Kind | Home | Controlled fields | May point at |
|---|---|---|---|
| Requirement | `engineering-docs/requirements/`, `R-<AREA>-###` | `status`, `priority` | decision records that explain it; bug records that threaten it; the tasks and work orders that implement or validate it |
| Decision record | `engineering-docs/decisions/`, `D-####` | `status`, dates, `decided-by`, `supersedes` | the requirements it serves; the records it supersedes |
| Bug record | `engineering-docs/bugs/` | `status`, `severity`, `target`, `owner`, `opened`, `closed`, `requirements` | the requirements it threatens; the release it targets; the completed-task record that holds its evidence |
| Backlog entry | a living list named for what it is, under `project-management`'s open-work directory: a backlog, a ledger | `priority`; an owner once assigned | the requirement it will become or serve; the work order that takes it |
| Work order | `engineering-docs/work-orders/`; an optional kind a project may leave unused | the recipient workstream; finish criteria | the requirements, decisions and backlog entries it scopes |
| Intake item | a workstream's `intake/`, then its decision log | none; its decision is a log row | whatever it hands over |
| Status file and records | the open-work directory | `state`, the next task | everything above, by link |
| Release record | `engineering-docs/releases/` | version, tag, evidence, notes | the bug records whose `target` names it; the work orders it delivered |
| Exception | the local workflow file, or the record it concerns | the reason; the condition that ends it | the rule it departs from |

## How A Thing Moves

- **An intake item ends as exactly one thing**: a bug record, a backlog
  entry, a requirement, a task in the recipient's status file, or a forward
  to `project-management`. Never two, never none; see *Workstream Intake*.
- **A backlog entry** becomes a requirement when the product owner accepts
  it, or a work order when a workstream is to build it. A backlog entry
  never becomes a bug record.
- **A bug record** ends `closed` or `retired`. It never becomes a feature:
  when the fix would need behavior the product never promised, the record
  is retired with that reason and a backlog entry is opened in its place,
  pointing back at it.
- **A requirement** moves through its statuses; a decision record says why
  it reads as it does. A requirement is never a queue of work: the tasks
  are in status files, the wishes are in the backlog.
- **A release** owns no records of its own beyond the release record. Its
  content is named from the outside: bug records by `target`, requirements
  by `priority` relative to it, work orders by the release they are cut for.

## Bug Or Feature

The test is by field, so that the question is never a matter of taste. A
**bug record** needs a requirement it threatens, or a documented behavior
the product promises, that is observed wrong or unsafe; its `requirements`
field names the former and its symptom section the latter. When no
requirement is violated and no promised behavior is wrong, the thing is a
**backlog entry**, however large the gap it describes; "feature" is the
everyday word for it. `severity` belongs to bug records and `priority` to
backlog entries and requirements; neither is used for the other, and a
backlog entry with a `target` is a planning statement, not a gate.

The test applies at filing and at triage alike. A bug queue that holds
wishes hides both: the wishes get no priority and the defects get no
attention. The filer who is unsure files a backlog entry; `project-management`
can always open the bug record when the requirement turns up.

## Validation

The validation kinds in `WORKFLOW.md`'s *Glossary*, environment, unit, integration,
end-to-end, smoke, gate, candidate gate and acceptance evidence, are not
records. They are declared, per project, in the local workflow file's
*Validation commands*: for each kind, the command runnable as written, or
`none` with the reason, so that silence is never ambiguous. The gate names
which kinds run before a checkpoint and before integration; the candidate
gate names which run on a candidate; the release record keeps the
acceptance evidence. A checkpoint that introduces or changes how any kind
runs updates that section in the same commit, which is what lets the next
agent, on any project and in any ecosystem, build the software and prove
it runs without guessing.
