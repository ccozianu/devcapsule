---
date: 2026-09-11
capture-mode: detailed
requested-by: user
scope: project-management decisions, workflow assignment, and pause
related:
  - ../../wip/2026-08-09-project-management/CURRENT-STATUS.md
  - ../../decisions/product/d-0009-launcher-delivers-identical-runtime.md
  - ../../requirements/devcapsule/r-runtime-001-launcher-runtime-identity.md
  - ../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md
---

# Session Record: Project Management Decisions And Workflow Review

This is a detailed, sanitized, agent-authored account, not a verbatim
transcript. The user explicitly requested saving context before stopping for
the evening and returning the next day. Decisions and next steps remain in
their canonical documents; this record preserves the discussion connecting them.

## Starting Point

The user asked which workstream and task were active. Repository inspection
confirmed `multiple-streams` mode and the clean checkout on
`project-management/coordination`. The latest handoff recorded the earlier
switch from component-catalog after v0.2.11. Component-catalog was to remain
open but paused, despite stale mainline registry wording about closure.

The planned task was to reconcile eight intake items with shipped v0.2.11
behavior and owner decisions, then prioritize further work. The user clarified
the purpose of project management: make go/no-go decisions, choose order,
assign existing or new workstreams, and clarify poorly defined work.

The review grouped three related intakes around upgrades: the user experience,
automated validation of new component versions, and learning from successful
experiments. Other intakes covered init/config semantics, internal naming, a
development blog, release candidates, and inside/outside runtime identity.
The broader portfolio also contains Eclipse, contained display, remaining V1
scope and acceptance, and safety/cleanup decisions. These are not all new
go/no-go questions; several already have accepted scope and need sequencing.

## Release Process: Adopt The Successful v0.2.11 Procedure

The user selected the release-candidate item first and directed project
management to handle it here rather than delegate it to the workflow stream.
The instruction was to have one easy-to-find release document and make the
successful v0.2.11 procedure the process for subsequent versions.

An existing guide was found under implementation notes. It was retained as
the [canonical release guide](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md),
retitled *Releasing A New DevCapsule Version*, and made prominent through the
root README, CLI README, engineering welcome page, and documentation index.
This avoided creating two competing release procedures.

The guide now begins with the operator sequence: prepare a committed slice,
publish an immutable candidate, test the downloaded candidate, record exact
acceptance, integrate through the repository's PR policy, tag the accepted
source for the final release, and verify the final download. It includes
maintenance-release and retry handling and the actual v0.2.11 reference:
`v0.2.11-rc3` and `v0.2.11` both identify source commit
`94e798f1d1a7aaab93ae3e47d9636471448a8e66`.

The [acceptance record](../../releases/v0.2.11.json) remains the evidence of
what was accepted. Its release/build scope does not claim fresh GUI/login or
provider acceptance. The broader matrix-learning policy is still an open
intake and was not adopted implicitly by documenting release promotion.

## Workflow Assignment: One Workflow, Many Projects

The user then requested an assignment to the existing workflow workstream:
review experience from DevCapsule and satellite samples, compare it with
workflow documentation, determine what applies across projects and is installed
for adopters, distinguish project-specific content, and make the structure
easy for humans and agents to navigate.

The resulting assignment is
[One Workflow, Many Projects](../../wip/2026-08-09-workflow-improvements/intake/2026-09-11-project-management-one-workflow-many-projects.md).
It asks for an evidence/gap inventory, a reusable/conditional/project-specific
boundary, an installation/update contract, a concrete document structure with
human and agent reading paths, walkthroughs across both workflow modes and
contrasting samples, and ordered implementation slices.

Inspection found that packaged assets already separate reusable definitions
from rendered project-memory instances. Older handoffs still describe previous
bootstrap arrangements. The review must reconcile actual implementation,
documented policy, accepted decisions, and installed sample behavior rather
than assume one copy is current. It must also distinguish missing rules from
stale rules, poor discoverability, and failures to follow sound rules.

The assignment connects existing information-model, optional workflow
component, storage/transport, and human-readable documentation work. It does
not silently close those older items. Initial scope is review and concrete
design; broad migration and new policy choices follow owner review. The
checkout stayed in project management. DevCapsule's PEX/GitHub/base-image
release runbook stays project-specific; only general workflow lessons from it
are inputs to the review.

## Runtime Identity: A Continuing Design Decision

After relisting the queue, the user settled item 7: unless explicitly
overridden by user choice, the CLI takes its corresponding base and installs
itself inside the container so the outside launcher and inside runtime support
are identical.

This is recorded as accepted
[D-0009: One Executable Outside And Inside The Container](../../decisions/product/d-0009-launcher-delivers-identical-runtime.md),
with [R-RUNTIME-001](../../requirements/devcapsule/r-runtime-001-launcher-runtime-identity.md).
Identity means the same executable bytes. A corresponding base is the base
selected by applicable project/platform resolution, not necessarily a base
with the same release number as the CLI. Materialization identity must include
the runtime artifact so a stale image cannot silently substitute older bytes.

The alternative of relying on an independently released embedded runtime was
recorded with its compatibility and release-coupling costs. It is not the
default. An explicit user override does not change the product default.

No new override command was invented or implemented. The requirement records
the existing interface accurately: source-form launches may select a built PEX
with `DEVCAPSULE_RUNTIME_PEX`; packaged execution selects itself ahead of that
variable. D-0004 and D-0007 gained pointers to the current runtime policy, while
D-0007's historical body and accepted decision/rationale were preserved.

## Verification And Delivery

The session changed documentation and coordination records, not runtime code.
The guide was checked against the release workflow and promotion scripts. Git
confirmed RC3/final source identity and mainline ancestry against the acceptance
record. Existing runtime selection and materialization tests were inspected as
evidence for the recorded design; no new runtime test pass is claimed. Relative
file links, heading anchors, and the final changes' whitespace were checked.

Git pushes succeeded. GitHub connector PR creation failed with HTTP 403,
`Resource not accessible by integration`, including the explicit attempt to
open the workflow-assignment outbox PR. Read access and reported repository
permissions did not establish permission for that connector operation.

Pending content is preserved in two pushed branches:

- `project-management/coordination`: release guide, D-0009, R-RUNTIME-001,
  document links, this session record, and current project-management records.
- `project-management/outbox`: both intake acknowledgments with their matching
  deletions, the workflow-review assignment, project-management handoff, and
  pause registry update. It contains no release guide, decision, requirement,
  or session-record deliverable.

The documentation branch must integrate first because the outbox handoff
references new permanent files. Neither a push nor an intake file on an
unmerged branch counts as receipt on main. Recheck remote main and open PRs
on resume rather than assuming the access problem or pending state persists.

Earlier unmerged outbox content was preserved before each reset from main and
reapplied with the new send. Log entries and removals remained together. This
addresses the immediate risk of repeating the known lost-mail failure; the
protocol gap is recorded in the handoff and is evidence for the workflow
review, not a silently implemented replacement transport.

## Remaining Decisions And Tomorrow's Starting Point

The user asked for the list again after the two decisions. Six intake topics
remain, with no further choice made before stopping:

1. Upgrade experience: V1 scope, warnings/previews, updates, artifact retirement,
   priority, and owning workstream.
2. Automated component validation: scope research into automation versus human
   testing and sequence it within upgrades.
3. Learning from successful experiments: evidence submission, acceptance, and
   when it gates catalog changes.
4. Init/regenerate versus config: shared/local configuration boundaries, flag
   semantics, authorization persistence, and implementation ownership.
5. Internal naming: remaining writing conventions for commits and records;
   older base-generation cleanup is already implemented.
6. Development blog: destination, review/correction process, scope, cadence,
   and ownership.

The agent suggested taking the first three together as an upgrade discussion,
with init/config closely related. That suggestion was not a user-selected next
implementation task. The portfolio decisions remain separately in the
[V1 ledger](../../wip/2026-08-09-project-management/v1-scope-ledger.md) and
[coordination backlog](../../wip/2026-08-09-project-management/coordination-backlog.md).

The user ended the session for the evening, requesting context preservation
and continuation tomorrow. Project management is paused deliberately, with
the same checkout selection retained. No containers, ports, releases, or
sample-project changes were created by this session. Temporary outbox
checkouts were removed after pushing. Canonical resume instructions and the
bounded Open Threads are in the
[project-management handoff](../../wip/2026-08-09-project-management/CURRENT-STATUS.md).

## Capture Limits

Spelling errors, repeated status lists, bulk tool output, and transient
verification-script mistakes are not reproduced. No verbatim export was
provided. No secret values or hidden agent reasoning are included. The pending
six topics have not been decided beyond what their existing records already
state, and the workflow review has not yet been performed.
