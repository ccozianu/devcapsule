# Design Issue: The Documentation Is Current When A Release Drops

Date opened: 2026-09-28. Owner: `project-management`.
Status: **work in progress; accumulating problems**. This document defines
problems the owner and the agent are working through in conversation. It
records no decision and proposes no implementation until a problem is
agreed to be correctly stated. Solutions, where they appear, are marked as
candidates.

Requirements touched: R-DOCS-002, R-DOCS-003, R-COMPAT-001.

## The Occasion

0.2.15 was released on 2026-09-27, verified, and reopened on `main` at
0.2.16.dev0. The public website, `https://devcapsule.mycodespace.ai`, was
last published on 2026-09-21, before 0.2.14, and its landing page still says
"as we prepare DevCapsule 0.2.14". The owner calls this a drop, not a miss:
the release went first, knowingly, and the site was left for later. The
question this document works toward is what we would passionately be in
pursuit of such that, when the next release drops on the internet, the
documentation is already right.

The owner's framing, borrowed from Lexus: the passionate pursuit of
perfection. Not perfect software soon, but passion in the pursuit.

## Problems, As Stated So Far

Each problem has a statement, the evidence it rests on, and the decision it
forces if any. Numbering is order of discovery, not priority.

### P1. "Released" does not include the adopter-facing documentation

**Statement.** The project's definition of a release is artifacts,
acceptance evidence, a tag and notes. The release runbook, the candidate gate
and the final gate check the executable, the acceptance record and `main`
ancestry. None of them checks that the documentation describes the version
being released, and none names publishing the website as a step. A release
can therefore be complete by every rule we have while the first page an
adopter reads describes a version two releases old.

**Evidence.** The release runbook at
`engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md`
mentions neither `docs/` nor the website. The 0.2.15 acceptance record on
`main` lists seven Docker proofs, the init journey, `project info`, agent
defaults and vendor pointers; no documentation check. R-DOCS-003 already
says "maintain the manifest at each release: promote the released version,
demote the previous ones", and no runbook step carries that sentence.

**Decision it forces.** Whether documentation freshness and website
publication become part of what "released" means, checked by a gate, or
remain a post-release task with a named owner and a deadline.

### P2. The documentation on `main` is stale before the website is

**Statement.** Republishing the site today would not help. The first-session
guide on `main`, the page the README calls "start here", pins v0.2.12 in six
places including the download URL and the expected version output. Across
all of `docs/`, 0.2.15 appears in exactly two section headings that
maintenance added with the features it shipped. Nothing checks R-DOCS-002,
current docs show current interfaces, at any point in a release.

**Evidence.** Checked 2026-09-28 on `main` at the 0.2.16.dev0 reopening:

| Page | Front matter | 0.2.15 | 0.2.14 | 0.2.12 |
|---|---|---|---|---|
| `docs/guides/first-session.md` | no | 0 | 0 | 6 |
| `docs/guides/your-project.md` | no | 2 | 1 | 0 |
| `docs/guides/windows-wsl2.md` | no | 0 | 0 | 1 |
| `docs/guides/component-upgrades.md` | no | 0 | 1 | 0 |
| `docs/README.md` | no | 0 | 1 | 0 |
| `engineering-docs/blog/2026-09-21-why-try-devcapsule-before-v1.md` | no | 0 | 3 | 1 |

The live site's first-session page shows the same six v0.2.12 references.

**Decision it forces.** Who makes the release's `docs/` true for the release
before the final tag: the release driver, who is inside the release when the
facts are known, or `user-docs`, which owns the guides and is paused.

### P3. The versioned-documentation model is agreed and built by nobody

**Statement.** The project decided, in R-DOCS-003 on 2026-09-22, that
documentation takes the PostgreSQL shape: the version is in the URL,
`/docs/current/` is the canonical copy, `docs/versions.yaml` on `main` lists
every version with its source ref and one of four statuses, and every page
carries a switcher. Under that model 0.2.15's documentation is whatever
`docs/` holds on `release-0.2.15`, and publishing it is a manifest edit. None
of it exists on either side. The parent commits to adding front matter and
the manifest in the same change that pins the implementing website revision;
the website has not implemented it; each side is waiting on the other, and
no workstream is sequencing them.

**Evidence.** No file under `docs/` or the blog carries front matter;
`docs/versions.yaml` is absent from `main`. The website builder reads no
YAML and infers status from paths. In the website repository's backlog W12
is marked gating but its top priority is W00, search discoverability. The
`website` workstream handed its backlog to the submodule repository on
2026-09-19 and has published no state since; `user-docs` is paused waiting
for the website's implementing revision.

**Decision it forces.** Whether the website repository takes W12 ahead of
W00, a priority call in that project, and whether 0.2.16 waits for it.

### P4. Publication is manual, in two places, and owned by no process

**Statement.** Publishing the site takes two owner-operated Actions runs:
the parent's Website workflow, dispatch only, builds the test site and a
candidate tag; the website repository's Publish workflow promotes that tag to
production. No document says when to run them, and nothing runs them when a
release is tagged. The release and the site move on different clocks by
construction.

**Evidence.** `.github/workflows/website.yml` triggers on
`workflow_dispatch` only. `website/PUBLISHING.md` describes the two-step
promotion. DEVELOPING.md: "Website publication is manual and separate from
a CLI release." Live site `last-modified` 2026-09-21; `build-info.json`
records content revision `a989155`.

**Decision it forces.** Whether the final tag publishes the site, with the
manual runs kept as the rollback path, or publication stays a separate act.

### P5. The agreed model leaves three details open that a release forces

**Statement.** R-DOCS-003 settles routing and status. Three things it leaves
open become concrete the moment a release tries to follow it.

1. **The install command needs a version.** The contract says a page never
   states which release it documents. The first-session guide must print a
   download URL and an expected version string. Either the website
   substitutes a version token per built version, or the rule relaxes to "a
   page may name its own version" and a gate checks that every version string
   under `docs/` equals the release version. The stale 0.2.12 references are
   exactly what such a check would have caught.
2. **Documentation fixes on a closed release branch.** WORKFLOW.md,
   *Releases*: after the final tag nobody commits to the release branch.
   R-DOCS-003 anticipates docs-only fixes landing there, or pinning a
   version's `source` to a commit instead. One has to give; if the branch
   rule bends, that is a definition change routed to `workflow-improvements`.
3. **The lifecycle clock at a two-day cadence.** The contract holds at most
   one supported and one deprecated version. With 0.2.14 and 0.2.15 two days
   apart, 0.2.14 is deprecated now and unsupported at 0.2.16. Honest, but the
   owner should confirm it is what an adopter on 0.2.14 should read next week.

**Decision it forces.** All three, by the owner; the second may also need
`workflow-improvements`.

### P6. Three workstreams own a piece, none owns the release moment

**Statement.** `user-docs` owns the guides and is paused. `website` owns the
content contract and the parent integration, and handed implementation to
the submodule repository. `project-management` owns the runbook. Nobody owns
"the docs are right when the tag is pushed", so the obligation R-DOCS-003
already states has no resource, in the workflow's vocabulary: a task with
no one to perform it.

**Evidence.** Registry rows and published states read 2026-09-28: `user-docs`
paused 2026-09-22; `website` active in the registry but unpublished since
2026-09-19; the release driver's checklist has no documentation row.

**Decision it forces.** Same as P2 and P1: a named owner for the release
moment, most naturally the release driver, with `user-docs` owning quality
between releases.

## Candidate Direction, Not Decided

Recorded so it is not re-derived; the owner has not adopted it.

**The release is the stranger's first session, not the artifact.** A version
has dropped when someone who has never heard of us can go from the live
website to a working capsule on the exact bytes we tagged. Under R-DOCS-003
that decomposes into: the release driver makes `docs/` true for the version
on the release branch before the final tag, with a gate check for version
strings; the manifest promotes the version; the final tag publishes the
site; candidate acceptance follows the first-session guide literally from
the test site built from the candidate, so a guide that disagrees with the
candidate fails the candidate.

## Problems Not Yet Stated

The owner has signalled further problems. They are added here as they are
defined, each with its evidence, before any of them is solved.

## Related Records

- [R-DOCS-003](../../requirements/product/r-docs-003-website-content-carries-front-matter.md), the PostgreSQL-shaped contract.
- [How the website is published, and what it still lacks](../../implementation-notes/website/2026-09-22-website-publishing-contract.md).
- [Release runbook](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md).
- [Website workstream status](../2026-09-16-website/CURRENT-STATUS.md), retained producer tasks W07-C, W08-C, W12-C.
- [0.2.16 planning proposal](2026-09-27-0216-release-planning.md); this issue will become one of its candidates once the problems are agreed.
- Intake 2026-09-26, release notes as a release artifact, and intake 2026-09-15, first-session UX gaps.
