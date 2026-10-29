# Owner direction: a language review of the user documentation before 0.3.0

Date: 2026-10-24
From: maintenance
To: project-management

## Handoff

The owner read the CLI UX stack for candidate 4 (PRs #260 to #269 into
`release-0.3.0`) on 2026-10-24 and accepted the code. On the documentation
the owner directed a final review round before 0.3.0 and asked that it be
booked with project-management. In the owner's words:

> Documentation is full of LLM English; however we will have a final round
> of reviewing the docs before 0.3.0.

> Most documentation written or modified needs substantial language changes
> to make it clear and understandable to humans, for example the
> configuration directory. It should have started with an index.md which
> outlines what a configuration for DevCapsule is, conceptually, after which
> to go into the weeds with capabilities, IDEs, and so on.

> Everywhere you open a .md, even though the outer structure of the docs is
> lacking, the inner stylistic pulse is atrocious; you can just tell it was
> made by an LLM, be it a frontier LLM.

This item is the booking. It carries the owner's direction and the evidence;
it assigns no owner, no sequence and no method. The owner placed it before
0.3.0; project-management records that placement.

## What the owner found

1. **The prose.** Pages written or rewritten by agents read as machine
   prose: the cadence, the sentence shapes, the habit of naming a thing and
   then restating it. The owner's standard is text a human would write for
   another human, clear on first reading.
2. **The structure of a section.** `docs/configuration/` has no entry page.
   The documentation index (`docs/README.md`) sends the reader to
   `configuration/inspect.md`, a how-to, and the section's other pages
   (`capabilities.md`, `project-versus-personal.md`, `software-approvals.md`,
   `resource-limits.md`, `ide-preferences.md`, `extra-tools.md`,
   `local-base.md`) each start in the details. The owner wants an
   `index.md` that says what a DevCapsule configuration is, as a concept,
   before any page goes into capabilities, IDEs, approvals or limits. The
   same check applies to every section under `docs/`.
3. **Breadth.** The finding is not limited to the fifteen pages the
   candidate-4 stack changed. The owner's reading is that most of the
   documentation written or modified by agents needs the same treatment.

## Evidence

- The candidate-4 stack's documentation slice, PR #269, and its review
  PR #271, both accepted on the executable's behaviour; neither reviewed
  the prose as prose. The slice changed fifteen pages under `docs/`
  (`git diff --stat release-0.3.0..ws-maintenance/cli-ux-6-docs -- docs/`),
  five of them wholesale: the four configuration pages named above,
  `containment/granting-and-withdrawing.md` and the command reference
  `reference/cli.md`.
- `docs/` holds 47 pages; no section has an `index.md`. The section entry
  points are the pages `docs/README.md` names in its question table.
- The open design issue of 2026-09-28, *The Documentation Is Current When
  A Release Drops*, and C16, the documentation describing the accepted
  candidate, already gate the final 0.3.0 tag. This review is a further
  condition on the same gate: the documentation must describe the accepted
  candidate and read as human writing.
- The website's content contract (`npm run check:content` in the website
  checkout) checks the pages' structure and references, not their
  language; it passed on the slice-6 tip and catches none of this.

## What accepting this means

Project-management books the review as a condition of the final 0.3.0 tag,
by the owner's direction, and decides who performs it and how: which pages,
in what order, whether the owner reads every page or samples, and which
reviewer loop applies. The configuration section's conceptual `index.md`
is the owner's named first case. Maintenance records the gate in the 0.3.0
release overview and does not begin the rewrite until project-management
assigns it.
