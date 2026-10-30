# Owner decision: project-operation-instructions-030

Date: 2026-10-11
From: project-management
To: workflow-improvements

## Handoff

Implement the owner's 0.3.0 requirement in the workflow definition: agents must
know and maintain the project's build, test, run and debug operations, including
separate unit/integration/e2e tests, selective tests and debugger attachment.
The generic obligation belongs in WORKFLOW.md; actual project instructions
belong in WORKFLOW-LOCAL.md. The agent works with the human to supply missing
or correct stale instructions even when all execution is delegated.

This belongs to workflow-improvements because it owns the generic definition
and its adoption instructions. Accepting means implementing the rule and its
required humane explanation, keeping affected bootstrap guidance/templates
consistent under the normal definition-delivery policy, and recording
validation. Do not change installed workflow declarations without authority.
Use the current local file as a dogfood check; send any project-specific
operational gaps to project-management rather than inventing commands.

The required content and acceptance below are owner decisions, not a request
to reconsider inclusion. This does not select which tests gate commits or
releases, their budgets, or a bootstrap engine. The separately received
testing-policy reconciliation stays with project-management.

## Evidence: Complete Owner Decision

Canonical PM record: engineering-docs/wip/2026-08-09-project-management/2026-10-11-decision-project-operations-and-bootstrap.md (this checkpoint; full text follows so delivery does not wait on integration).

# Project Operations For 0.3.0; Ecosystem Bootstrap For 0.9

Date: 2026-10-11
Decision: product owner, during the project-management release-scope review.
Status: accepted; implementation and recipient acknowledgement remain.

## Ecosystem Bootstrap: Target 0.9

Move [ecosystem-aware project bootstrap](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md)
from 0.3.0 to **0.9**. Keep it a confirmed minor bug owned by maintenance;
this decision changes its timing and direction, not its classification.
It is excluded from 0.3.0. Revisit during 0.9 planning, with the project-type
templating dependency made explicit; do not repeatedly raise it in 0.3.0 work.

Bootstrap depends on a way to express the project type or ecosystem the user
intends, through project templating. Examples are Java + Maven, Scala + sbt,
Python + nox (this repository), Node + npm, and Node + Yarn. Discover tooling
from that intended project type. These examples do not silently select a
template format or commit to implementing every ecosystem in one slice.

The environment should be bootstrapped so the project's tools are available
on PATH by default throughout the capsule. This is availability to the
developer, IDE, terminals and agent processes, not a requirement to install
project dependencies into a host-global or shared system package environment.

For project types that require it, an explicitly documented exception is an
activated shell. Inside the capsule, `devcapsule project shell` opens a shell
whose PATH and environment provide the project's required utilities. This
command belongs to the 0.9 direction; it is not promised to exist in 0.3.0.

The prior bug record's versioned-adapter design and Python/non-Python proof
remain design input for the later slice, not a 0.3.0 implementation obligation.
Maintenance must update the bug target and its plate with this owner ruling.
Project-management retains sequencing of the templating dependency; its
implementation owner and design are not selected by this decision.

## Project Operation Instructions: Required For 0.3.0

The human and agent must have a durable, project-specific account of how to
perform the project's ordinary development operations. At every point during
project work, the agent/LLM is responsible for knowing where these instructions
are and keeping its understanding current. The instructions belong in the
project's **WORKFLOW-LOCAL.md**. The generic obligation belongs in
**WORKFLOW.md** and is assigned to workflow-improvements for 0.3.0.

The project-specific instructions must cover:

1. Building the project.
2. Running unit tests, integration tests and end-to-end tests separately.
3. Selecting individual tests and, where needed, categories such as tags.
4. Running the project's default entry point or main program.
5. Running it under a debugger, including how the human attaches that debugger.

Record the actual invocation and the working directory, environment preparation
and prerequisites needed to make it usable. Where an operation or test tier
does not apply or is not yet available, say so and resolve the gap with the
human; do not invent a command or imply that an unverified command works.

If the human has not supplied adequate instructions, the agent must work with
the human to establish correct instructions and persist them in WORKFLOW-LOCAL.md.
Maintain them when the project changes. This obligation still applies when
the human delegates all building, development, debugging and testing to the
agent. The human must retain the option to request any applicable project
operation through the agent without reconstructing its setup from chat history.

Acceptance: the workflow states this continuing responsibility, and its local
instructions support a resuming pair in finding and performing each applicable
operation, including selective tests and debugger attachment. Missing or stale
instructions trigger reconciliation with the human. Existing workflow ownership
and delivery rules apply to any cross-workstream correction.

This decision does not require a template engine, automatic dependency setup
or a new project-shell command for 0.3.0. It also does not decide which test
tiers gate commits, PRs or releases, nor their time or storage budgets. Those
questions remain in the separately received testing-policy intake.

## Delivery

Send the bootstrap retargeting to maintenance and the 0.3.0 generic workflow
requirement to workflow-improvements through coordination mail. This PM record
is the release-scope decision; implementation belongs to the receiving
workstreams. Their acknowledgements and delivery are followed in published state.
