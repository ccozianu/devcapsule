# One Workflow, Many Projects

Review what experience has taught us, define what adopters inherit, and make
the workflow easy for humans and agents to navigate.

Date: 2026-09-11

Sender: `project-management`, at the product owner's explicit direction.

Recipient: `workflow-improvements`.

## Assignment

Review the workflow as it is practiced in DevCapsule and its satellite sample
projects, compare that experience with the workflow we document and install,
and define a coherent structure separating reusable workflow mechanisms from
each project's own rules and records. A human or agent arriving in a project
must be able to find the relevant instruction, decision, and current task
without knowing DevCapsule's development history or reading every document.

This is assigned to the existing workflow workstream. Start with an evidence
review and a concrete design; identify bounded implementation slices after
the model and structure are clear. This delivery does not switch the sender's
checkout, resume all of the recipient's backlog, or authorize an unrelated
rewrite. Take it at the next workflow review, before further redesign of the
reusable definition or installation layout. Existing V1 commitments stand;
this item does not set a new release date.

## Questions To Answer

1. **What have we learned, and what do our documents actually say?** Gather
   concrete successes, failures, owner rulings, and recurring ambiguities from
   DevCapsule development and the sample projects. Compare the root workflow,
   shipped definitions/templates, and installed copies. Distinguish a missing
   rule, a stale or contradictory rule, a rule that is hard to find, and a
   sound rule that the tools or participants fail to follow. Preserve evidence
   and separate accepted decisions from proposals and historical statements.
2. **What is reusable, and under what conditions?** Identify the small common
   core and mechanisms conditional on workflow mode, project needs, or host
   capabilities. Test applicability beyond this repository: single-stream and
   multiple-stream projects, applications, libraries, research projects, and
   projects with different build, release, and hosting arrangements. State why
   a mechanism belongs in the installed workflow. DevCapsule's own complexity
   is not evidence that every adopter needs it.
3. **What belongs to the adopting project?** Define where its purpose,
   requirements, decisions, current work, validation commands, release policy,
   domain-specific documents, and explicit local exceptions live. Distinguish
   project-owned policy from generated initial state and reusable definitions.
   Explain authority and conflict resolution when local instructions and the
   common workflow interact; make intentional differences visible.
4. **What exactly does installation add or update?** Give a file/mechanism
   inventory for a fresh adoption and an existing project: copied definition,
   rendered template, optional tool/configuration, or project-owned content.
   State who maintains each, how an update is recognized and applied, and how
   project work and customizations survive refresh. Review actual bootstrap
   behavior before proposing changes; do not infer it from old handoffs.
5. **How does either audience find the right thing?** Design a short entry
   path for humans and a precise entry path for agents, a small shared
   vocabulary, and a document map with clear authority. Explain what must be
   read at start/resume and what is loaded for a particular operation. Shared
   rules should have one authoritative home; introductions, examples, and
   project instructions should point there instead of duplicating them.

## Deliverables And Acceptance

- **Evidence and gap inventory.** For each material finding, record the source
  project and revision, observed behavior or owner decision, current canonical
  text, packaged/installed behavior, and recommended action: retain, clarify,
  generalize, make conditional, keep local, or retire. Include positive
  evidence; record inaccessible or unverified sample history as an evidence
  gap rather than reconstructing conversations as fact.
- **Boundary and installation table.** Classify each retained mechanism and
  document as common, conditional, or project-specific, with its owner,
  installation/update behavior, and authoritative location. Explain both
  workflow modes and adoption without the optional workflow component.
- **Proposed document structure.** Provide a concrete directory/file map,
  human and agent reading paths, links between common rules and local policy,
  and a migration map from existing files. Explain how definitions, project
  policy, live coordination state, and historical evidence remain distinct.
- **Walkthroughs.** Show how a new human and a fresh agent find the project
  brief, current task, applicable rule, local exception, test instructions,
  release instructions, and a past decision. Exercise a fresh installation
  and an update of an existing project without replacing its requirements,
  decisions, or handoff. Cover both workflow modes and at least two contrasting
  sample contexts; identify what is demonstrated versus still proposed.
- **Implementation plan.** Order the required documentation, template,
  installer, and validation changes; identify dependencies and decisions still
  requiring the owner. Reconcile overlapping intake items individually in the
  recipient's handoff/log so that this umbrella review does not hide or silently
  close earlier assignments. Present the structure for owner review before
  broad migration or new policy choices.

Use plain language suitable for non-native English readers. Success means a
reader can locate the answer and tell which document governs it, and an
installation inherits justified reusable mechanisms while retaining its own
project facts. A larger manual by itself is not acceptance evidence.

## Starting Evidence And Related Assignments

Repository paths below are starting points, not claims that their historical
status remains current. Read accepted mainline and record the revisions used.

- Root `AGENTS.md`, `WORKFLOW.md`, `README.md`, `REQUIREMENTS.md`, `index.md`,
  and `engineering-docs/README.md`; the product workflow requirements
  `R-PRODUCT-003` through `R-PRODUCT-006`.
- `devcapsule-src/devcapsule/assets/project_workflow/README.md`, its
  `definition/` and `templates/` directories, bootstrap implementation and
  packaging tests. The asset README already separates reusable definitions
  from project-memory instances and documents explicit definition refresh.
  Root and packaged definitions need not be byte-identical; determine which
  differences are justified and which are drift.
- `engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md`, the
  three sample repositories registered in `.gitmodules` (FastAPI web app,
  trading research, and TypeScript tic-tac-toe), their workflow documents,
  accepted decisions, and recorded findings. Use their own history as well as
  reports returned to DevCapsule; inspect without modifying sample state.
- The recipient's existing information-model, workflow-component ownership,
  outbox-mechanism, registry-ownership, bug-vocabulary, coordination-storage,
  off-main-mail-transport, and release-branch-naming intake items. Also read
  the project-management V1 ledger's human-readable documentation and optional
  workflow rows, including later amendments that supersede earlier questions.
- `engineering-docs/wip/2026-09-09-eclipse-surface/2026-09-09-outbox-reset-loss-record.md`
  and the project-management handoff's recovery evidence: recurring loss of
  undelivered work must inform the review, not become a new anecdote without
  a disposition. The custody record's location does not make Eclipse its owner.

The already-ratified boundary between durable records on main and coordination
state off main is a design input, with its later transport proposal; do not
mistake the still-operative outbox protocol for the final adopted direction.
Keep existing rules operative until an explicit migration is ready. The
release-candidate checkpoint now has concrete v0.2.11 evidence to review.

**Release example and ownership boundary.** Project management has just adopted
DevCapsule's successful v0.2.11 release procedure in
`engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md`.
Keep that concrete PEX/GitHub Actions/base-image runbook project-specific.
Review which concepts behind it are reusable (for example accepted evidence,
release refs versus workstream selection, and finding a project's release
policy) without installing DevCapsule's release commands into unrelated
projects. This assignment does not hand the release-process task back to the
workflow workstream.
