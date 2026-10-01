# How the website is published, and what it still lacks

Written 2026-09-22 in the `user-docs` workstream, from reading the parent
integration (`scripts/website.sh`, `.github/workflows/website.yml`), the
website submodule at pin `78b7b7f` (`website/scripts/content.mjs`,
`website/PUBLISHING.md`, `website/.github/workflows/publish.yml`), the
website backlog, and the live sites on that date. It is written for a human
who wants to change the landing page, a guide, a blog entry or an
announcement and see it on the website, without reverse-engineering the
builder. Where this note and `website/README.md` disagree, the website
repository is authoritative for the mechanism; this note is the parent-side
explanation and the gap analysis the owner asked for.

## 1. Where the site is, and what is live today

| Site | URL | Purpose |
|---|---|---|
| Production | `https://devcapsule.mycodespace.ai` | Public site, indexable |
| Test (staging) | `https://test-devcapsule.mycodespace.ai` | Reviewed before promotion; currently also indexable |
| Local preview | `http://127.0.0.1:8080/` | Watches content and presentation; `noindex`, no canonical |

There is no `devcapsule.website.ai`; that name does not resolve. The only
owned domain is `mycodespace.ai`, hosted on GitHub Pages from two repositories.

As of 2026-09-22 both hosted sites serve the same build: content revision
`a989155` (DevCapsule `main` of 2026-09-21), website revision `78b7b7f`, built
2026-09-21 12:13 UTC, promoted from candidate `website-candidate-35598312155-1`.
Since then `main` gained three guides that are therefore **not yet on the
website**: `docs/guides/component-freshness.md`,
`docs/guides/component-upgrades.md`, `docs/guides/working-in-workstreams.md`,
plus the matching rows in `docs/README.md`. This branch builds them cleanly
(22 pages, 855 links checked), so the next publication run will include them.

Every page footer links `/build-info.json`; it records the content SHA, the
website SHA, whether either was dirty, the build time, the mode, and after
promotion the source run and candidate release. That file is the way to answer
"what exactly is live?" without trusting anyone's memory.

## 2. Two repositories, one boundary

| Repository | Owns | Never contains |
|---|---|---|
| `ccozianu/devcapsule` (this one) | All authored prose: `README.md`, `docs/**`, `engineering-docs/blog/**`; the submodule pin; the test-publication workflow | Layouts, CSS, navigation code |
| `ccozianu/devcapsule-website` (submodule `website/`) | Eleventy build, layouts, styles, navigation order, link checks, candidate packaging, production promotion workflow, the website backlog W00–W13 | A second copy of any authored Markdown |

The parent pins one website commit. That pin is what both local preview and
the hosted workflow build with. Changing text here never requires touching the
website repository. Changing appearance requires a website commit, a merge
there, and then a pin bump here (`git -C website checkout <sha>; git add
website; commit`). The current pin `78b7b7f` has the same tree as website
`main` (`c735ca2`), so nothing is waiting on a pin bump today.

## 3. What gets published: the content contract as implemented

The builder (`website/scripts/content.mjs`) reads exactly three sources from
the parent checkout and nothing else:

| Source file | Website route | Notes |
|---|---|---|
| `README.md` | `/` | Landing page, parsed into sections (see §4) |
| `docs/**/*.md` | `/docs/<path-without-.md>/` | Every Markdown file below `docs/`, recursively; `docs/README.md` becomes `/docs/` |
| `engineering-docs/blog/YYYY-MM-DD-slug.md` | `/blog/YYYY-MM-DD-slug/` | The blog `README.md` is read for link resolution but not published; `/blog/` is a generated index |

Nothing under `engineering-docs/` other than the blog is published. Links from
a published page to any other file in the repository become GitHub permalinks
at the exact content SHA that was built. `docs/index.html` is ignored.

Rules an author has to know, because they fail the build or change the output:

- **Every relative link must resolve on disk.** A link to a missing file or a
  missing image stops the build with `Broken source link in <file>: <href>`
  or `Missing image: <path>`. Links that escape the repository root also fail.
- **Heading anchors are GitHub-style slugs.** `#5-stop-and-come-back` works on
  both GitHub and the website. The link checker verifies every anchor.
- **The first `# H1` is the page title** and is removed from the body. Exactly
  one H1 per page; more than one fails the check.
- **The description and excerpt are derived**: the first paragraph longer than
  40 characters, cut at 210 characters. That is what appears in the `<meta
  name="description">`, the blog card and the journal list. Write the first
  paragraph as if it were the summary, because it is.
- **Reading time** is word count divided by 220 per minute.
- **Images** referenced from a page are copied to `/content-assets/<path>` and
  must have alt text; an image without `alt` fails the check.
- **Tables** get a scrollable wrapper; code blocks are highlighted by
  `highlight.js` when the fence names a language it knows.
- **HTML in Markdown is allowed** (`html: true`) and `linkify` turns bare URLs
  into links.
- **Draft/historical status is inferred from the path**: any file whose path
  contains `/product/` or `docker4pycharm` is labeled "Background, draft or
  historical material" with a warning box, is removed from the docs sidebar,
  and is listed in a separate "background" group. It is still published and
  indexable. There is no other way to mark a page as a draft. **A new file
  under `docs/` is public the moment `main` is published.**
- **Docs navigation order** is fixed in code for four pages (`docs/README.md`
  "Overview", `first-session.md` "Your first session", `your-project.md` "Your
  own project & AI", `windows-wsl2.md` "Windows & WSL2"). Every other current
  guide follows automatically, in directory walk order, labeled with its H1.
  Reordering or renaming a navigation label is a website change.
- **No front matter is read.** The builder does not parse YAML; a front matter
  block would render as a table or text. Blog conventions already forbid it.

## 4. The landing page: what `README.md` must keep

The landing page is not the README rendered as-is. The adapter picks named
sections and paragraphs and places them into a designed layout. These literal
headings must exist, or the build stops with `README landing headings changed;
update the presentation adapter in scripts/content.mjs`:

| Heading in `README.md` | Role on the landing page |
|---|---|
| `## Why DevCapsule?` | Section heading of the "Ready when you are" block |
| `### For the really, really curious…` (any heading starting `For the really`) | Body of that block |
| `### The essence of why DevCapsule: <headline>` | The text after the colon is the hero headline. Its paragraphs are assigned by position: 1st = hero lead, 2nd = motto, 3rd and 4th = the two feature cards ("The workspace", "The coding partner"), 5th onward = the "boundary you control" block |
| `## Aim for engineering excellence. Keep the fun.` | "The longer game" section |
| `### But is it really needed?` | Comparison section (optional; omitted if absent) |

All `<img>` links in the README become the health badge strip. The hero
buttons, platform line ("Linux x86-64 · Windows via WSL2 · Open source"),
eyebrows and the closing call to action are hard-coded in
`website/src/_includes/home.njk`, not authored here.

Practical consequence: editing words inside a paragraph is safe. Inserting a
paragraph before the fourth one in the "essence" section silently moves the
feature cards. Renaming a heading breaks the build until the adapter is
updated. This brittleness is website task W07 and parent task W07-C; the
agreed fix is stable section identities, not yet designed.

## 5. Blog entries and announcements

A blog entry is one file `engineering-docs/blog/YYYY-MM-DD-slug.md`. The date
in the file name is the displayed publication date and the sort key (newest
first); the title is the H1; the excerpt is the first long paragraph. Add the
entry to `engineering-docs/blog/README.md` and `index.md` by convention, but
the website does not need either list. A file is live as soon as it is on the
published content revision; there is no draft state. Both "draft for owner
review" retrospectives from 2026-09-19 are therefore public today.

"Announcements" have no dedicated channel. The v1 announcement, the LinkedIn
draft and the press release live under `docs/product/` and are published as
labeled historical pages. A release note or news item today can only be a blog
entry, a README edit, or a GitHub release.

## 6. Preview locally

```sh
git submodule update --init website      # once per checkout
./scripts/website.sh install             # once, or after the pin changes
./scripts/website.sh preview             # http://127.0.0.1:8080/, watches both trees
./scripts/website.sh build               # one-off build + full link/structure check
```

Node 22 or newer is required. The preview uses this checkout's working tree,
uncommitted edits included, and the footer marks it "Local preview". `build`
is the same command the hosted workflow runs, so a green local build is the
strongest pre-merge evidence available today.

## 7. Publish to the website: the exact manual sequence

Nothing publishes automatically. Merging content to `main`, tagging a CLI
release, or merging in the website repository changes no hosted site.

1. Land the content on DevCapsule `main` through the ordinary PR.
2. In `ccozianu/devcapsule` open **Actions → Website → Run workflow** on
   branch `main` with mode `production`, origin
   `https://test-devcapsule.mycodespace.ai`, base path `/`. These are the
   defaults except the mode, whose default is `preview`; `preview` only uploads
   a seven-day artifact and deploys nothing. Any other origin or base path
   builds and deploys the test site but skips candidate creation, so the run
   is green and unpromotable.
3. Wait for jobs `build`, `deploy` and `candidate`. The test site now shows
   the new content. The run summary and the Releases page carry a prerelease
   `website-candidate-<run>-<attempt>` with `website.tar.gz` and
   `candidate.json`.
4. Review the test site.
5. In `ccozianu/devcapsule-website` open **Actions → Publish production
   website → Run workflow** on `main` and paste the candidate tag. It downloads
   the public assets anonymously, verifies the SHA-256 and source metadata,
   rewrites only the canonical origin, re-runs the link check and deploys.
6. Check `https://devcapsule.mycodespace.ai/build-info.json`; the `promotion`
   block names the run and release just used.

Rollback is step 5 with an older tag. Candidates are ordinary GitHub
prereleases: retained until someone deletes them, and listed on the same
Releases page as the CLI downloads.

Only a person with Actions dispatch rights on both repositories can publish;
there is no token to keep. Total elapsed time is a few minutes.

## 8. What the current mechanism is missing

Grouped by what a modern product site, open source included, is expected to
do in 2026. Items already tracked in `website/BACKLOG.md` carry their W-number;
the rest are new observations from this reading. Nothing here is decided.

### Publication pipeline

- **No publish on merge.** Content is stale until a human runs two workflows
  in two repositories. Today `main` is three guides ahead of the site.
- **The test-publication inputs are a footgun** (W01, confirmed bug): the
  default mode publishes nothing, and a wrong origin silently disables
  promotion.
- **No validation before merge** (W04, W04-C). A broken link in a docs PR is
  discovered at publication time, by the owner, not by the author in CI. The
  parent `tests.yml` does not run the website build.
- **No per-PR preview.** Reviewers read Markdown diffs, not rendered pages.
- **No post-deployment verification** (W05). "Deployed" means the Pages API
  accepted the artifact, not that the domain serves the intended revision.
- **Staging is a public duplicate of production** (W02): same content,
  `Allow: /`, no `noindex`, canonical pointing at production. Search engines
  may index or conflate it.
- **Promotion identity is an opaque tag** (W03) copied by hand between
  repositories; no diff against what is live.
- **Rollback is untested** and candidates are mutable and clutter the CLI
  Releases page (W06).

### Discoverability and sharing

- **Not indexed yet** (W00, top priority). Google verification succeeded on
  2026-09-19; indexing evidence is still pending, Bing not started.
- **No `sitemap.xml`** (404 today) and no feed (`feed.xml` 404) (W09, W10).
- **Weak metadata** (W09): `og:title` reads "DevCapsule · DevCapsule", no
  `og:description`, `og:image`, `og:url`, Twitter card or structured data, so
  shared links render as bare URLs. The homepage description is "Start here:
  open your first workspace…" rather than what the product is.
- **No RSS/Atom** for the journal, and **no search** (W10).

### Content model

- **No page metadata at all.** Status (draft, current, historical), supported
  release, author, last-reviewed date, tags and description are either
  inferred from the path or absent. A fresh build date in the footer is not a
  per-page freshness signal (W08, W08-C, W12).
- **Drafts are public.** Anything under `docs/` ships. The only draft marker
  is a path containing `/product/`.
- **No documentation versioning.** Guides describe one release (currently the
  v0.2.12-era journey plus the 0.2.14 component guides) with no per-version
  routing, version switcher, or "this page describes vX" banner.
- **No redirects.** Renaming or moving a Markdown file changes its URL and
  breaks every inbound link; GitHub Pages offers no server-side redirects, so
  a redirect mechanism would have to be generated (meta refresh or a
  redirect page list).
- **No release notes, changelog or news page** on the site. Releases are only
  on GitHub. There is no announcement channel other than a blog entry.
- **Landing coupled to README wording** (W07): paragraph position and literal
  heading strings drive the hero layout.
- **The content contract is undocumented as a contract** (W12): the README
  section in the website repo describes behavior; nothing is versioned, and
  an incompatible content change produces a build failure rather than a
  compatibility decision.

### Reader experience

- **Light theme only** (`color-scheme: light`); no dark mode.
- **No search**, no tags, no series navigation for the journal.
- **Browser coverage is Chromium automation only** (W11); no Firefox, WebKit
  or real-device evidence, no performance budget.
- **No "last updated" per page**, no author byline on entries, no "edit this
  page" (there is "Read the source on GitHub", which is close).
- Comments are excluded by decision, which is fine for the audience.

### Operations

- **No analytics or basic traffic evidence** (W13, accepted as second stage).
- **No uptime, broken-external-link or TLS-expiry monitoring.**
- **Bus factor of one** for publication, and every step is a browser click
  sequence rather than a command.
- **GitHub Pages constraints**: no custom headers (CSP, caching), no
  server-side redirects, one deployment per repository. Adequate today; a
  ceiling to know about.

### Suggested order, for the owner to decide

Update, later on 2026-09-22: the owner chose the PostgreSQL documentation
model, versions in the URL with a `current` copy and a switcher, and the
front-matter contract. Both are specified in
[R-DOCS-003](../../requirements/product/r-docs-003-website-content-carries-front-matter.md);
the order below predates that decision.

1. Publish the test site automatically on every merge to `main`, keep
   production promotion manual, and add the website build and link check to
   the parent's PR checks (closes the stale-site and late-breakage problems;
   overlaps W01, W04).
2. Sitemap, `noindex` on staging, proper Open Graph and description
   metadata, feed (W02, W09, W10). Cheap, and prerequisite for W00 to succeed.
3. A minimal front-matter or sidecar contract: `status`, `description`,
   `describes-release`, optional `redirect-from`. This is the W12/W08 work and
   it unblocks drafts-in-public, versioning and redirects at once.
4. Search and dark mode, then analytics (W10, W13).

Items 1 and 2 are website-owned implementation with a parent pin bump; item 3
needs the content owner's agreement first and is where user-docs has a say.
