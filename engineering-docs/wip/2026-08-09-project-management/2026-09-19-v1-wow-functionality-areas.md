# Design Issue: V1 Completeness And The WOW Experience

Date: 2026-09-19
Status: open design issue; discussion and proposed grouping preserved at the
owner's request. This is not a new set of approved V1 feature commitments.
Owner: project-management
Requirements: R-PRODUCT-001, R-PRODUCT-002, R-PRODUCT-003, R-PRODUCT-004,
R-DOCS-002, R-COMPAT-001

## The Question

What would deliver a WOW experience for a V1 adopter, with nothing important
missing? The owner feels the product still has gaps and asked to group work
into general functionality areas for both user documentation and management
of requirements/items.

The immediate example was a working X11 session demonstrated to a friend,
followed by a launcher upgrade and a sequence of configuration failures.
The [confirmed upgrade bug](../../bugs/devcapsule/2026-09-19-upgrade-config-recovery-rejects-its-own-remedy.md)
preserves the terminal evidence and recovery. This design issue captures the
broader concern: independently working features and locally reasonable checks
can still fail to form a complete, understandable adopter experience.

The owner's earlier Hoare-standard direction remains relevant: configuration
should be simple enough to reason about its correctness, rather than merely
appear free of obvious deficiencies. The older directive is preserved in the
[recursive-e2e record](../../archive/2026-08-06-recursive-e2e/CURRENT-STATUS.md),
under the remediation of `project_configuration.py`.

## Existing Direction

The [V1 scope ledger](v1-scope-ledger.md) already records the owner's
workspace-and-containment thesis and maximal-WOW release direction: a useful
workspace in which agents can work freely inside an honest, explicit boundary.
The former twelve-week window is not the release criterion. The first-session
direction is AI-first, with useful work as the outcome; the current no-AI
exercise is accepted interim documentation, not the agreed V1 introduction.

This discussion proposes organizing that existing intent around what an
adopter wants to accomplish. It does not reopen settled commitments or infer
that every capability mentioned below must ship in V1.

## Proposed Functionality Areas

Use the same areas for documentation navigation and for organizing requirements,
bugs and tasks. Each area is phrased in the adopter's terms.

| Area | Adopter's question | Contents to examine |
|---|---|---|
| Getting started | How quickly can I do something useful? | Prerequisites, installation, supported platforms, a first useful project with AI, examples to explore. |
| Preparing a project | How do I bring my project here? | New projects, existing repositories, third-party projects, environment declarations, dependencies, language tooling and supporting services. |
| Everyday development | Can I comfortably do my normal work? | IDEs, terminals, Git, running and debugging, tests, application previews, ports, clipboard and browser integration. |
| Working with AI | How do I get effective help? | Agent selection, authentication, hosted or local models, project instructions, autonomous work, reviewing results and changing agents. |
| Configuration and personalization | How do I make this workspace suit me? | Inspecting and changing configuration, project defaults versus personal choices, IDE preferences, plugins, profiles and resource limits. |
| Containment and access | What can this workspace and its agents touch? | Files, credentials, secrets, networking, Docker, devices, host integration, granting and withdrawing access, understandable boundaries. |
| Sessions and continuity | Can I leave and come back without rebuilding my working life? | Start, stop, reconnect, persistent state, concurrent projects, multiple IDEs, recovery after interruption and moving between machines. |
| Project knowledge and collaboration | Can another person or agent pick up the work? | Briefs, requirements, decisions, bugs, handoffs, workstreams, messaging, shared project setup and optional workflow adoption. |
| Updates and maintenance | How do I stay current without breaking working projects? | Launcher, image and component updates; recommendations; compatibility; migrations; validation evidence; rollback and supported versions. |
| Troubleshooting and cleanup | When something goes wrong, can I understand it and regain control? | Status, diagnostics, actionable errors, logs, retries, repair, selective reset, disk usage, removing obsolete resources and uninstalling. |

For item management, the proposal is one primary area per item, with links to
related areas. Existing requirement identifiers and workstream ownership can
stay intact. These areas describe functionality, not new workstreams or another
backlog. For example, the upgrade bug primarily belongs to Updates and maintenance,
with connections to Configuration and personalization, Containment and access,
and Sessions and continuity.

The grouping has not yet been applied to the documentation tree or requirement
records. No file moves or new classification fields are prescribed here.

## Pressure Points Identified In The Discussion

1. **A compelling first success.** The user-docs status explicitly leaves the
   intended AI-first introduction unfinished. Agree a small project, useful
   result and IDE/agent pairing rather than letting an easy-to-test example
   choose the product experience.
2. **Complete everyday development.** Opening an IDE is only the beginning.
   Walk through building, testing, previewing and debugging a realistic
   application. This is an area to assess, not a claim that all those functions
   are currently absent.
3. **Continuity through change.** The recorded upgrade incident demonstrates
   that a working environment can become a configuration puzzle. The whole
   transition needs to work, including the resulting display and state.
4. **Understanding and recovery.** Users should see what they have, what will
   change and how to recover. Success must not depend on learning internal
   architecture through successive error messages.

These are starting points drawn from the records and the owner's experience,
not the results of a fresh implementation audit. Older ledger entries can be
stale and must be reconciled with delivered work before declaring a gap open.

## Proposed WOW Assessment

Follow one realistic project through an ordinary life:

**Start it → accomplish something useful → personalize it → leave → return →
hand it over → update it → recover from a failure.**

Use the functionality areas to ask what the adopter needs at each step and
where the transition between steps breaks. The purpose is to expose missing
connections that a feature inventory and isolated checks can overlook.

The project, scenarios and depth of assessment remain to be chosen with the
owner before a substantial experiment. Do not treat this note as authorization
to install components, launch environments or start an exhaustive test campaign.
Passing self-authored tests alone does not establish a satisfying experience.

## Next Discussion

Refine the grouping with the owner, then use it to map existing documentation,
requirements and open items without duplicating their authoritative records.
Identify genuine gaps and propose their V1 scope and ownership for decision.
In particular, distinguish missing behavior from missing documentation and
missing validation of behavior already delivered.

The expected result is a coherent account of what an adopter can accomplish,
which transitions still fail, and what must be completed to earn V1 acceptance.
No new release deadline, feature priority, workstream assignment or final
acceptance decision was made in this discussion.

## References

- [V1 scope ledger and proposed acceptance](v1-scope-ledger.md).
- [V1 user-experience design](../../design-notes/devcapsule/v1-user-experience.md).
- [User-docs direction and remaining first-session work](../2026-09-12-user-docs/CURRENT-STATUS.md).
- [Current user-documentation map](../../../docs/README.md).
- [Root requirements index](../../../REQUIREMENTS.md).
- [Coordination backlog](coordination-backlog.md).
