# Work Order: DevCapsule Website Autonomy Experiment

Agreed with the product owner, Costin Cozianu, on 2026-09-16. Prepared in
`user-docs` for execution by a fresh-context agent in `website`. This document
is the task contract; the new agent does not need the preceding conversation.

## Outcome

Give DevCapsule a small, clean, professional website that is interesting and
engaging to read and presents the project better than GitHub's Markdown view.
A visitor should quickly understand what it offers, decide whether to try it,
and find usable starting instructions. Deliver a reviewable preview ready to
be made live, with a straightforward local preview for future development.

The agent chooses the information architecture, visual design, implementation,
framework, navigation, and publishing mechanism. Use that freedom to deliver a
coherent result, not to turn this into a larger product than the brief requires.

## Required Content And Reading Experience

- The equivalent of the current root `README.md` landing page, preserving its
  substance, project identity, and visible project-health information.
- Readily accessible user documentation, with meaningful navigation and links
  that work as naturally as the existing Markdown links.
- The development blog currently under `engineering-docs/blog/`, readable and
  discoverable on the website. No user comments or comment database.
- Links back to the GitHub repository for developer and engineering material;
  those collections need not be published as website pages. The development
  blog is an explicit exception to the engineering-document exclusion.
- Comfortable typography, readable code examples, mobile layouts, accessible
  navigation, and working internal links.
- Clear distinctions between available behavior and the intended v1 experience.
  Preserve the engaging pitch without inventing product capabilities.

The current v0.2.12-specific guides are explicitly accepted as an interim
mainline experience. Their redesign is a separate user-docs backlog. Building
this website must not wait for, or silently take over, that redesign.

## Content And Website Ownership

The DevCapsule repository remains the authoritative home of the landing page,
user documentation, and development-blog content. Keep authoring those here.
Do not introduce a second manually maintained copy in the website repository.
Generated copies or rendered output are acceptable build artifacts.

Create a separate website project under `github.com/ccozianu/`, included as a
Git submodule in DevCapsule. Choose an appropriate name and submodule path.
The website project owns the structure and presentation machinery: styles,
JavaScript if needed, layouts, navigation definitions, build configuration,
robots directives, and similar assets. First development happens from this
DevCapsule environment. Before delivery, equip the website repository with its
own DevCapsule configuration and sufficient instructions/project state for a
future pair to develop it independently.

After the initial cut, presentation work and website-specific additions such
as demo videos should happen in that project. DevCapsule should retain content
ownership and the small integration needed to publish it, without accumulating
the website's implementation or maintenance backlog. Existing blog articles
remain here even though the website presents them.

## Repeatable Updates

Implement a mechanism through which DevCapsule triggers website updates: a
script, GitHub Actions workflow, or another suitable reproducible approach.
The agent chooses and documents the triggering conditions. Manual owner
publication, relevant content merged to main, and release-driven publication
are all acceptable possibilities; implement the choice rather than merely
describe it.

Keep the source content revision and website implementation revision
identifiable. Make the content-consumption contract usable both by automation
and by developers previewing the separate website project. Avoid circular
requirements for developing the website versus updating its parent submodule.

Two practical acceptance checks:

1. Changing a paragraph in DevCapsule can reach the preview/published site via
   the documented update mechanism without manually editing the website repo.
2. Changing website styling requires no changes to documentation content, and
   the website's own development setup supports that change and local preview.

## Hosting, Domains, And Human-Supplied Resources

Choose between GitHub-hosted static hosting and hosting backed by a cloud
storage account. Google Cloud Storage is easiest for the owner to provide;
AWS or Azure is also possible if justified. No dynamic database unless the
agent identifies a real need and obtains explicit owner approval.

The owner controls `mycodespace.ai`. The likely production address is
`devcapsule.mycodespace.ai`; an optional hosted preview can use
`test-devcapsule.mycodespace.ai`. A working local preview is mandatory even if
a hosted preview is available. The agreed finish is a reviewable result ready
for production, not an unreviewed production launch. Resolve preview access,
DNS/TLS needs, and final deployment steps during the initial setup checkpoint.

Available resources include the owner's approximately $200/month OpenAI
subscription and existing GitHub/Docker credentials in the environment.
Verify actual access; do not infer permissions from the presence of credentials.
The owner can create the chosen repository under `ccozianu` and provide cloud
and DNS access. This environment previously lacked `gh` and GitHub PR
creation/merge rights; Git push worked. Do not assume those limits disappeared.
Never put credentials in source, generated public pages, or progress records.

## Initial Human Setup Checkpoint

The owner will not remain available to monitor frequent prompts. Before the
autonomous implementation run:

1. Read the task and relevant repository contracts. Choose the proposed hosting
   and development approach sufficiently to identify its prerequisites.
2. Make one consolidated request for the needed repository creation, credentials,
   permissions, cloud/DNS setup, expected hosting costs, deployment authority,
   and any other foreseeable human actions. Include how exceptional warnings
   can reach the owner and how any required final merge will be handled.
3. Verify the supplied access before declaring the autonomous run ready. Resolve
   known prerequisites here. Anything deliberately deferred, such as production
   DNS activation, needs an agreed completion path that doesn't block review.

The agent may investigate enough to prepare this request, but must not choose
a stack, begin a long build, and repeatedly discover predictable missing access.
After this checkpoint, make routine design and implementation decisions
independently. Record nonblocking questions and continue useful work around
partial blockers. Interrupt only for an anticipated budget overrun or a genuinely
unforeseen issue requiring the human, including an unavoidable scope exception.

## Scoped Autonomy Exception

For this experiment the owner explicitly delegates consequential website
design and implementation choices normally discussed with the owner under
`AGENTS.md`. After initial setup, use independent judgment and carry the task
through to the reviewable deliverable. Do not request repeated design approvals.

This exception applies to the website work order only. It does not waive the
content ownership boundary, Git/workstream routing, credential handling,
required checks, explicit host access, or budget reporting. It does not authorize
unrelated DevCapsule features, changing product requirements, a database, or
unreviewed production publication. Resource-conscious reasoning still applies.

The initial website submodule implementation is part of this one workstream;
it is not a second independently active workstream in this checkout. Establish
its independent future development workflow as a deliverable. Record any later
human/agent transition explicitly.

## Budget And Stop Conditions

The owner permits effort up to a whole subscription month's allowance and the
three usage-limit resets reported available when the experiment was agreed.
This is an account-allowance ceiling, not a promise of a known token quantity,
API credit balance, or a month-long elapsed-time assignment. The agent should
spend less when sufficient. Verify any visible allowance/reset information at
setup and record what cannot be observed; request the owner's action if a reset
requires it. Do not promise automatic reset control or exact remaining usage.

Estimate feasibility at the initial checkpoint and reassess at meaningful
milestones, using available usage information, progress, and remaining work.
If the agent judges that completion needs more than the authorized budget,
warn the owner before exhausting it, with completed work, what remains, the
reason for the estimate, and viable scope/budget options. Preserve a resumable
checkpoint and headroom for delivery or handoff. An avoidable budget exhaustion
without prior warning counts as failure. An abrupt platform cutoff invisible
to the agent cannot carry a guarantee of advance notice; acknowledge this
limitation rather than inventing telemetry.

Conclude the implementation run when the preview, update mechanism, independent
website development setup, and proportionate validation are ready for review.
Do not keep polishing indefinitely. Report blockers and partial results honestly.

## Review And Success

The owner is the first judge. If satisfied, the experiment succeeds. If not,
the owner explains the reasons. The agent may accept them, recording failure
or partial success, or explain why it disputes their fairness/objectivity and
invoke assessment by three developer friends of the owner. That assessment is
final. The human arranges their participation; no independent outreach is
implied. If needed, agree a simple scoring/decision procedure before that review.

Give the reviewer the preview URL or local command, what is ready, known gaps,
relevant validation evidence, budget status, and exact steps remaining to make
it live. Include practical checks of navigation, mobile/accessibility behavior,
content updates, and local preview, chosen proportionately to the implementation.
Passing self-authored tests alone is not evidence of a satisfying user experience.

## Fresh-Context Start

The current user-docs session defines and delivers this work order and the new
workstream's registration only. Website implementation begins after the human
uses `/new` and explicitly selects `website/initial-cut`.

Read the root startup instructions, the accepted-main workstream registry, and
`engineering-docs/wip/2026-09-16-website/CURRENT-STATUS.md` plus its intake. Then
read this work order and perform the consolidated setup checkpoint. No need to
reconstruct the previous chat or treat the blog's fictional dialogue as policy.

The owner authorized preparing the starting branch from the current user-docs
branch so it carries this brief. This is a narrow exception for branch
preparation before mainline registration; implementation still waits for the
work order and registration to reach main. The current pair does not start that
implementation, choose the website stack, or request its cloud credentials.
