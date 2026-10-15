# Design Discussion: The Workflow's Open Issues, And A Structure For Its Size

Kind: design discussion, draft. Opened 2026-09-21 by `workflow-improvements`
at the product owner's direction. Decisions here are proposals until the
owner rules; each ruling is recorded in the status file and the proposal
below is updated or struck.

## Why This Document Exists

On 2026-09-21 the owner asked what the workflow is still missing, then asked
for the answer to be kept as a design discussion rather than a conversation,
together with a concern that had been lower on the list: the size of the
non-code part of the source tree, and the context an agent must load before
it can act. The two are one problem. Size is manageable if a structure is
imposed on it that makes information reachable on demand, so that a reader,
human or agent, loads what the task needs and nothing else.

## The Size, Measured

Word counts on 2026-09-21, on `ws-workflow-improvements/v1` level with `main`.

| Area | Words |
|---|---|
| `engineering-docs/wip/` (nine open workstreams) | 91,846 |
| `engineering-docs/implementation-notes/` | 37,419 |
| `engineering-docs/design-notes/` | 26,948 |
| root markdown (`WORKFLOW.md`, `AGENTS.md`, `WORKFLOW-LOCAL.md`, `README.md`, `CURRENT-STATUS.md`, `index.md`) | 25,326 |
| `engineering-docs/bugs/` | 20,610 |
| `engineering-docs/decisions/` | 15,314 |
| `engineering-docs/session-records/` | 11,313 |
| `engineering-docs/archive/` | 9,416 |
| `docs/` | 8,871 |
| `engineering-docs/blog/` | 8,149 |
| `engineering-docs/requirements/` | 6,299 |

The status files alone: this workstream's is 14,748 words, component-catalog's
10,892, project-management's 10,512; the other six are between 1,500 and
4,600. The definition is roughly 18,000 words and the root agent file 2,300.

**What an agent loads at session start today**, in this workstream: the agent
file, the definition, the local file, and the status file, about 36,000
words, near 48,000 tokens, before reading a single file it will change. The
same session in a young workstream costs about 23,000 words, almost all of it
the definition. Neither number is a defect of any one document. Each is the
sum of documents that were each reasonable to write.

## The Structure Proposed

Four layers, each read for a different reason, with one rule between them:
a document points down to the layer below it and never up, so that reading
stops where the task stops.

1. **Always read.** What every session needs before acting: the agent file,
   the definition's core, the local file, and the selected workstream's
   status file. Target: under 10,000 words in total, which is a fifth of
   today.
2. **Per operation.** Loaded when the session performs that operation and
   otherwise not: releasing, pausing and resuming, deciding intake,
   completing and integrating, initializing the mode, beginning a
   workstream. The definition names each with a one-line "read this when"
   pointer and the condition to check.
3. **Per topic.** A workstream's dated documents, the design notes, the
   implementation notes, the bug records, the decision records: opened when
   the task is about that topic, found through an index that says when to
   open each.
4. **History.** Archives, session records, shed task narratives, the blog:
   never loaded for work, kept for retrospection, and reachable through the
   same index.

The layers already exist in outline: the engineering-docs README classifies
by authority, `index.md` lists everything, and the status file has a document
index. What is missing is the discipline that keeps each document in its
layer, and the pointers that make a reader stop.

## The Rules That Would Impose It

Each is small. Together they are the structure.

- **The status file is bounded and sheds history.** It holds what the
  workstream is, its state, its branch, the current task, the next task, open
  threads, and an index of its documents; roughly what a person reads in ten
  minutes. Task narratives move verbatim into a dated record at each pause.
  This workstream's status file is the counter-example and goes first.
  Written into the definition as *The Open-Work Directory* on 2026-09-21.
- **Dated documents by kind, one per topic**, `YYYY-MM-DD-<kind>-<slug>.md`,
  with a small set of kinds and one index line each saying when to open it.
  Same section, same date.
- **The definition splits into a core and per-operation files**, after the
  experiment that tells us which conditional phrasing the four agents we
  ship actually honor. The core is layer 1; the files are layer 2. Strategic
  item 5 below.
- **The index says when, not only what.** Every entry in `index.md` and in a
  status file's document index carries the condition under which a reader
  opens it. An index that only lists is a table of contents; one that says
  when is a map.
- **History has a home and stays there.** Session records, shed narratives,
  and the blog are layer 4 by definition; nothing in layers 1 to 3 may
  depend on reading them.
- **Tooling prints the start context.** `devcapsule workflow status` already
  shows every workstream's next step; a `brief` verb that prints exactly the
  layer-1 set for the selected workstream, and nothing more, would make the
  budget visible and enforceable.

## The Open Issues, Prioritized

Recorded from the 2026-09-21 exchange with the owner, who called the list
right. Two levels, each in priority order.

### Strategic

1. **The verifier.** One session-start command that reports unpublished
   state, waiting mail, an old branch name, an intake item missing from the
   log, a bug record without frontmatter, a declaration disagreeing with the
   definition. Every rule written this month depends on someone remembering
   it; this is what makes them hold. On `project-management`'s backlog,
   needing a home.
2. **Adoption across the other eight workstreams.** Publish once, rename
   branches, retire outboxes, decide stranded items. Cheap each; until done
   the live list has one row.
3. ~~**Soft claims.**~~ Built 2026-09-21 with `brief`; `status` and `brief`
   surface them.
4. **What Adopters Inherit, phase 1**, starting by refreshing the three
   sample projects: the first real test of versioning, migration entries, and
   the local file, and most of the review's evidence.
5. **A definition an agent can afford to read**: the core-plus-on-demand
   split, after the phrasing experiment. Should be settled before the
   review's structure phase, which it shapes.
6. **The next release under the new release rule.** Project-management's
   runbook edit and maintenance's triage are the inputs; not this
   workstream's work, but the deadline that tests half of what was written.
7. **Human explanation in user docs** against the glossary under the drift
   rule. In user-docs' mailbox; that workstream is paused.

### Implementation

1. **The status-file rule, applied to this workstream first.** Done 2026-09-21
   for the rule; the shedding follows in the same round.
2. ~~**Age on the live list**: when each workstream last published.~~ Done
   2026-09-21.
3. **Branch protection on `coordination`**: no force-push, pushes open.
   Owner's to set; unknown whether done.
4. **The table on `main` rendered from published state** at integration, or
   reduced to a pointer.
5. **Review the mechanical requirement-priority mapping** of 2026-09-19.
6. **The adopter-facing merge-strategy page in `docs/`**, the oldest backlog
   item.
7. **The two retained successor containers** on the owner's host, kept for a
   Stage 7 that no longer exists. Project-management's entry.
8. **Packaged-versus-root definition drift** beyond the sections edited
   together, to be listed by the review's phase 1.

## V1 Items Added 2026-09-21

The owner asked what would add to the workflow's appeal for V1 and took the
proposals as items on this workstream, backlog items 4 to 10: `brief`, soft
claims shown live, `ask`, `digest`, `doctor`, the live board, and agent
review of pull requests. They share one property: each makes something the
workflow already does visible in one motion, and each keeps the whole thing
git and markdown all the way down. The headline pairing is `brief` and the
board: any agent or human runs one command and knows what to do, and anyone
opens a page and watches the team do it, both from the coordination branch.

## Open Questions For The Owner

- Whether the 10,000-word target for layer 1 is the right order of magnitude,
  or whether it should be stated in tokens per agent.
- Whether kinds beyond design, note, and record are wanted in the definition,
  or left to each project's local file.
- Whether `index.md` should be reorganized by layer now, or after the
  review's structure phase, which will propose a document map anyway.
- Whether the `brief` verb is worth building before the definition split, as
  a measurement, or after it, as enforcement.
