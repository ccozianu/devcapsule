# Work Order: The DevCapsule Website, Seen From The Visitor's Chair

Date: 2026-09-28. Issued by `project-management` under the owner's grant of
2026-09-28 to run this independently and decide without asking. Executed in
the `devcapsule-website` repository, single-stream, from its own
`CURRENT-STATUS.md`. The producer-side companion is
[the visitor content work order](2026-09-28-visitor-content-and-producer-migration.md)
in DevCapsule. Both rest on
[the content–website contract, version 1](../wip/2026-08-09-project-management/2026-09-28-design-content-website-contract.md).

Status: open. Release: none; the site publishes on its own clock, and the
first publication after this order is the one that documents 0.2.15.

## 1. What The Visitor Wants, And What The Site Owes Them

Put yourself in the chair of someone who has landed on
`devcapsule.mycodespace.ai` from a search result, a journal link or a
friend's message. They have three questions, in this order, and they will
leave the moment one goes unanswered:

1. **Is this for me, and is it worth my time?** What it is in one sentence;
   who it is for; what it runs on; how mature it is. An honest "not yet" on
   macOS keeps the right people and loses only the ones who would have left
   angry later.
2. **What does it give me that I do not already have?** Not a feature list:
   the three or four things that change how a day of work feels. A real IDE
   in a capsule; agents at full speed behind a boundary the visitor controls;
   leave and come back with everything intact; a way for people and agents to
   share one repository without a tracker.
3. **How do I try it, and then learn it, with the least of my time?** A first
   session that ends in something running, in minutes, with no account; then
   a path from "I have a project" to "my agent is working in it"; then the
   reference when they need it, for the version they actually run.

Everything below serves those three questions. Anything that does not is
progressive disclosure: present, reachable in one click, out of the way.

## 2. The Design Judgment To Apply

The owner's reference for the feel is a site the agent produced elsewhere:
`https://smartgalati-test4.mycodespace.ai/`. Its subject is unrelated; what
transfers is the system, not the colours:

- **One idea per section, one action per idea.** The hero says one sentence
  and offers one primary action and one quiet secondary. Every later section
  is a summary with a single link deeper. Nothing competes.
- **Entry by intent, not by feature.** Three pillars right under the hero,
  each one a visitor's intent with a verb, each linking to the page that
  serves it. On the reference: first moves, training and tournaments,
  performance. Here: try it, bring your project, work with an agent.
- **Aerated, with a measure.** A spacing scale from 0.25rem to 6rem used
  consistently; sections padded at the large steps; prose capped at about
  70ch; cards in rows of three at most; alternating calm backgrounds so the
  eye rests between sections. Density is "just right" when a section fits
  in one screen with air around it and still says something.
- **A display face for headings, a hyperlegible face for body.** The
  reference pairs a variable serif with a body face designed for legibility.
  Use that pairing or an equivalent open pairing, self-hosted, no third-party
  font fetch. Type scale with `clamp()` so the hero headline is large on
  desktop and sane on a phone. Body at 1.0625rem, line-height 1.6.
- **A band at the top and a band at the bottom.** The header and hero sit on
  a coloured band; the closing call to action sits on another. Between them
  the page is paper. DevCapsule already owns a palette in this family
  (paper, ink, deep green, lime, a warm accent); keep it and tune contrast to
  WCAG AA.
- **Honesty is the brand.** DevCapsule's distinguishing claim is that every
  edge has a file. Every claim on the site links to its evidence: the
  journal, a release note, a guide, a bug record. No stock imagery, no
  superlatives, no counters that are not real.
- **Night mode.** The 2026-09-22 branch already carries a switch; keep it,
  and design both palettes from the same tokens.

## 3. Information Architecture

Top navigation, in this order: **Docs · Start here · Journal · Releases ·
GitHub**. "Start here" is the `getting-started` role resolved to the current
version, per the contract; it is the one link a first-time visitor needs and
it never goes stale.

| Route | What it is | Versioned |
|---|---|---|
| `/` | The home page, sections in section 4 | no |
| `/docs/` | The versions index: the owner's notice, the current version, every published version by status | no |
| `/docs/current/…`, `/docs/<version>/…` | The product documentation, per the contract | yes |
| `/journal/` (today `/blog/`) | The development journal; keep `/blog/` as an alias | no |
| `/releases/`, `/releases/<tag>/` | Release notes, one page per final tag, newest first; from `engineering-docs/releases/<tag>/notes.md` when the producer adopts that artifact, and until then from the notes block of each release overview | no |
| `/why/` | The long answer to "is it for me": the thesis, the comparison, the dogfood story; content from the README's longer sections and the comparison note | no |
| `/contribute/` | The contributor front door: how a stranger picks a bug, works it with an agent inside DevCapsule, and sends it back; content from the producer, "coming soon" until authored | no |

The docs sidebar is per version and built from front matter `weight`, with
the six roles of the contract surfaced as the first entries in this order:
overview, getting-started, your-project, agents, containment, windows. A
page marked `status: planned` renders as a stub with a "Coming soon" label
and sits greyed in the sidebar, so the ideal structure is visible before all
of it is written.

## 4. The Home Page, Section By Section

Every section's text comes from the producer through the contract's stable
identities (W07), never typed here. Section order is fixed; the producer
can change every word without a website change.

1. **Hero, on the band.** Eyebrow: "Pre-V1 · Linux x86-64 · Windows via
   WSL2". Headline: the README's essence headline. Lead: one sentence. Primary
   action: "Open your first workspace", the `getting-started` role, with the
   current version number rendered beside it from the manifest. Secondary:
   "See what you get", an in-page anchor. The health badges move to the
   footer; the hero has no badges.
2. **Three pillars.** *Try it in fifteen minutes* → getting-started. *Bring
   your own project* → your-project. *Let your agent work at full speed,
   safely* → agents. Each: a verb headline, two lines, one link.
3. **What you get.** Four cards at most: the IDE in a capsule; agents in YOLO
   mode behind a boundary you control; persistent state, leave and return;
   the workflow for people and agents on one repository. Each links to the
   guide that proves it, in the current version.
4. **Is it for you?** Two short columns: *Good fit today* and *Not yet*.
   Content-owned, honest, links to `/why/` for the long answer and to the
   comparison. This is where macOS and "expect edges, every edge has a file"
   live.
5. **Built with itself.** The three latest journal entries as cards, with
   one line explaining that DevCapsule is developed inside DevCapsule and the
   journal is the transcript. Link to `/journal/`.
6. **Releases strip.** "Current release 0.2.15, 2026-09-27" from the manifest
   and the notes; links to that release's notes and to all versions.
7. **Closing band.** "Start here" again, one action; beside it the quiet
   contributor invitation.

Sections 4, 6 and 7 are new; 1, 2, 3 and 5 restructure what exists. The
comparison section and the "philosophy" section of today's page fold into
`/why/`.

## 5. The Documentation Experience

- Per-version build, versions index, `current` copy, switcher and banners
  exactly as the contract specifies; the notice on the index verbatim from
  the manifest.
- Reading layout: sidebar left on wide screens, page table of contents right
  when the page has three or more headings, prose at the measure, code blocks
  with a copy button, tables scrollable. This mostly exists; align it to the
  tokens.
- Version tokens rendered; a typed version string fails the build.
- The status banners are calm, not alarming: one line, the status word, and
  the link to current. The unreleased banner for `devel` says so and nothing
  more.
- Search: not in this order. Good navigation first.

## 6. Sequence Of Slices, With What "Done" Means

Work in this order; each slice is a reviewable pull request in the website
repository with its checks green and the test site deployed for review.

1. **Take the 2026-09-22 delivery.** Merge branch
   `requests-from-devcapsule-2026-09-22` (contract request pointer, sitemap,
   night mode, installed workflow definition). Done: on `main`, sitemap
   served, night mode works, W00 keeps its priority for the owner's Search
   Console work, which this order does not block.
2. **Contract version 1.** Record the contract in this repository as the
   accepted interface, referencing the producer's design document. Implement:
   manifest parsing with the version check; front matter with the R-DOCS-003
   fields, `role` and the `planned` status; tokens and the typed-version
   check; the per-version build with once-only builds for immutable sources;
   the versions index; role resolution; the switcher and banners; shared
   fixtures and a `check` command the producer's gate can run. Done: the
   contract's acceptance section passes against the fixtures and against the
   producer's `main` at the pin.
3. **Design system.** Tokens, type pairing self-hosted, spacing scale,
   both palettes, bands, cards, pillars, banners; applied to base, docs and
   journal layouts. Done: every page uses only tokens; contrast AA in both
   modes; a phone at 360px and a desktop at 1440px both read well, checked
   with the browser check script and by eye.
4. **Home page.** The seven sections, from stable identities; `/why/` and
   `/contribute/` routes, the latter as a planned stub. Done: the three
   visitor questions each answered above the fold or one click below it;
   no typed content in templates.
5. **Releases.** `/releases/` and per-tag pages from the producer's notes.
   Done: 0.2.14 and 0.2.15 listed with their notes; the home strip reads
   the current one.
6. **Publication.** Test site deployment and candidate from the parent's
   workflow as today; production promotion stays the owner's single Actions
   run, per this project's rule that production publication needs explicit
   acceptance. Done: a candidate exists whose test deployment the owner can
   promote in one click, and the pin bump in the producer is prepared.

## 7. What The Executing Session May Decide, And What It May Not

Decide freely: type pairing among open faces, exact palette values within
the existing family, component shapes, copy of labels and banners, ordering
within a slice, Eleventy structure, test strategy. Do not: rewrite the site
in another generator; type product content into templates; publish to
production; change the contract without recording a version decision; take
work from the producer side of the companion order. When a producer change
is needed to proceed, record it in this project's status as a request to
DevCapsule and continue with what does not depend on it.

## 8. Evidence This Order Rests On

- Live site checked 2026-09-28: last published 2026-09-21, landing page
  says "as we prepare DevCapsule 0.2.14", first-session guide pins v0.2.12.
- Reference site tokens read 2026-09-28: `--font-display` variable serif,
  `--font-body` hyperlegible sans, `--fs-*` clamp scale, `--s-1` to `--s-9`
  spacing, `--w-prose: 70ch`, hero and support sections on bands, three
  pillars, alternating `section--alt`.
- Website repository at `c735ca2`: Eleventy, `home.njk` with hero, intro,
  features, boundary, comparison, philosophy, journal, closing sections;
  palette tokens paper, ink, green, lime, orange.
- Website backlog W00, W07, W08, W12; the unmerged branch of 2026-09-22.
