---
id: R-DOCS-003
title: Website Content Carries Explicit Front Matter And A Versions Manifest
type: requirement
kind: concrete-requirement
status: proposed
priority: wanted
source_of_truth: repo
verification:
  - automated-build-check
  - doc-review
external_refs:
  - https://github.com/ccozianu/devcapsule-website/blob/main/BACKLOG.md#w12--gating-define-the-contentwebsite-contract
  - https://www.postgresql.org/docs/current/index.html
---

# R-DOCS-003: Website Content Carries Explicit Front Matter And A Versions Manifest

Proposed 2026-09-22 by `user-docs` as the producer side of the content–website
contract (website task W12, parent task W12-C). Agreed in principle with the
product owner the same day. It has two parts: per-page front matter, and a
versions manifest that gives the documentation the PostgreSQL shape, where the
version is in the URL, `current` is the canonical copy, and every page carries
a switcher. Landing-page section identities (W07) remain out of scope.

## Statement

1. Every Markdown file the website publishes from `docs/` and
   `engineering-docs/blog/` must begin with a YAML front matter block that
   states whether and how the page is published. `README.md` is exempt,
   because GitHub renders front matter as a table on the repository landing
   page.
2. The parent repository publishes `docs/versions.yaml`, the single authored
   statement of which documentation versions exist, where each is built from,
   which is current, and what support status each has.
3. The website builds `/docs/<version>/` for every listed version, taking
   only `docs/` from that version's source; the landing page and the journal
   always come from `main`. It must fail loudly on missing or malformed
   input and must not infer status from paths or versions from tags.

Versioning starts at 0.2.14, the first release intended for adopters outside
the project. Earlier releases appear only as `unsupported`, if at all.

## Part 1: Page Front Matter

Names follow the conventions shared by Hugo, Eleventy, Docusaurus, Astro
Starlight, Zola and MkDocs Material.

| Field | Required | Values | Meaning |
|---|---|---|---|
| `description` | yes | one sentence, at most 200 characters | Used for `<meta name="description">`, social cards, blog cards and the journal list. Replaces the excerpt the builder derives from the first paragraph today. |
| `draft` | no, default `false` | boolean | `true`: excluded from production builds, navigation, sitemap and candidates. Local preview renders it with a visible "Draft" label. |
| `status` | no, default `current` | `current`, `historical` | `historical`: published under the "Background, draft or historical material" notice, out of the guide sidebar, grouped separately. Replaces the `/product/` and `docker4pycharm` path test. |
| `aliases` | no | list of site-relative paths | Old URLs that keep working after a rename or move; the website emits a redirect page for each. |
| `weight` | no | integer | Sidebar order among current guides, lower first; unweighted pages follow in title order. Replaces the hard-coded navigation entries. |
| `updated` | no | `YYYY-MM-DD` | Last substantive revision, shown on the page. Blog entries keep their date in the file name. |

Rules:

- The first `# H1` remains the title; there is no `title` field.
- Unknown keys fail the build naming the file and the key.
- A missing block, or a block without `description`, fails the build naming
  the file.
- The block is stripped before rendering and never appears in a page body.
- A page never states which release it documents; the version is the URL.

## Part 2: The Versions Manifest

`docs/versions.yaml` on `main` is authoritative. Shape:

```yaml
current: "0.2.14"
versions:
  - version: devel
    source: main
    status: development
  - version: "0.2.14"
    source: release-0.2.14
    status: development
  - version: "0.2.12"
    source: a989155385026b2e5f80cedb5edc8e1e0f4a6bbd
    status: unsupported
    note: Its guides were written after the tag and never reached its release branch.
```

Fields:

| Field | Required | Meaning |
|---|---|---|
| `current` | yes | The version served as the full copy at `/docs/current/`, the canonical URL for every page that exists in it. Must name a listed version. Normally the newest `supported` version; during the bootstrap before 0.2.14 is final it names the version the owner chooses to present. |
| `version` | yes | The URL segment: a release version without the `v`, or `devel`. |
| `source` | yes | Any ref the parent repository resolves: a branch name, a tag, or a commit. The website checks out that ref and reads its `docs/` tree, nothing else from it. A version's documentation can therefore be fixed on its retained release branch after the final tag, or pinned to a commit when the branch never carried the guides. |
| `status` | yes | One of the four statuses below. |
| `note` | no | One sentence shown in that version's banner. |

The four statuses, in the order a version passes through them:

| Status | Meaning for a reader | Website behaviour |
|---|---|---|
| `development` | Unreleased. Describes candidates or `main`. | Banner "unreleased, may change"; `noindex`; canonical points to the same page in `current` when it exists there. Listed under "Development versions". |
| `supported` | Released, and the project fixes it. | Indexable; listed under "Supported versions"; the newest one is normally `current`. |
| `deprecated` | Released, still works, receives no further fixes. The project is small and its energy goes to `current`; move when you can. | Served with a banner saying so and naming `current`; canonical points to `current` when the page exists there; still listed under "Supported versions" with a deprecated marker so readers on it can find their way. |
| `unsupported` | The project no longer says whether it works. | Served with a stronger banner; `noindex`; listed only under "Unsupported versions". |

Default lifecycle, which the manifest may override explicitly: a version is
`development` from its release branch cut, becomes `supported` at its final
tag, becomes `deprecated` when the next final release ships, and becomes
`unsupported` one further release later. The project intends to hold at most
one `supported` and one `deprecated` version at a time.

Routing:

- `/docs/<version>/<path>/` for every version and every non-draft page.
- `/docs/current/<path>/` is a full copy of the current version and is the
  canonical URL; links from `README.md` and journal entries use it.
- `/docs/` lists the versions, grouped by status, like PostgreSQL's index.
- Every documentation page carries a switcher linking to the same path in
  each other version where it exists, otherwise to that version's index.
- Links inside a version resolve inside that version; links to files outside
  `docs/` resolve to GitHub permalinks at that version's source revision.

## Why This Exists

Today a page is public the moment it exists under `docs/`, and the site has
no notion of release. `main` already carries guides for the 0.2.14 client
while 0.2.12 is the latest final release; the next publication would show
both under one navigation with nothing telling a reader which client they
have. The 0.2.12 guides were themselves written after the 0.2.12 tag, so a
version's documentation cannot be defined as "the docs at the tag". Two
journal entries labelled drafts are live. Descriptions are the first long
paragraph of each page. Renaming a file breaks every inbound link. None of
this is a website defect; the content never said what it wanted.

## What The Producer Commits To

- Add a conforming block to every file under `docs/` and
  `engineering-docs/blog/`, and add `docs/versions.yaml`, in the same parent
  change that pins the website revision implementing this requirement, so no
  build ever sees half a contract. The parent's pin is what every build uses.
- Amend `engineering-docs/blog/README.md`: entries carry this front matter and
  nothing else framework-specific; the block is authored here.
- On migration, mark the two 2026-09-19 retrospectives `draft: true` until
  the owner releases them, and mark every page under `docs/product/` and the
  Docker4PyCharm guide `status: historical`.
- Keep `README.md` free of front matter and point its documentation links at
  `/docs/current/`.
- Maintain the manifest at each release: promote the released version, demote
  the previous ones, and record any deliberate deviation with a `note`.
- Decide, as a workflow matter, whether documentation-only fixes for a
  released version land on its retained release branch; if not, pin that
  version's `source` to a commit instead.

## What The Producer Asks Of The Website

- Parse the front matter with the field set and defaults above; fail on
  missing, malformed or unknown input naming the offending file.
- Read `docs/versions.yaml`, resolve each `source`, and build each version
  from its `docs/` tree only; fail naming the version when a source does not
  resolve or its build breaks.
- Drop the path-based historical test once every consumed file carries a
  block, and drop the hard-coded navigation once `weight` is honoured.
- Honour `draft`, `status`, `aliases`, `weight`, `updated`, the four version
  statuses, `current`, the switcher and the canonical rules as described. A
  field the website chooses not to render yet must still be accepted.
- Record the accepted field set and manifest shape as contract version 1 in
  the website repository, referencing this record, so either side proposes
  version 2 with a compatibility decision rather than a surprise build
  failure.

## Verification

Satisfied when:

- `./scripts/website.sh build` on `main` passes with every consumed file
  carrying a block and a valid manifest, and fails naming the file or version
  when a block is removed, given an unknown key, or a source does not resolve;
- a page marked `draft: true` is absent from a production-mode build and
  present, labelled, in preview;
- `/docs/current/` is byte-identical in content to the current version's
  pages apart from the canonical URL, and every other version's pages carry
  the specified canonical and robots behaviour for their status;
- the switcher on a page present in two versions links both, and on a page
  present in one links the other version's index;
- a page with `aliases` is reachable at each alias after promotion;
- the manifest's `current` names a listed version, and the website's check
  passes on both sides against shared example files.

## Related

- `R-DOCS-002`: version status and the switcher are how current docs declare
  what they describe.
- Website backlog W02, W07, W08, W09, W12; parent tasks W07-C, W08-C, W09-C,
  W12-C in the website workstream status.
- [How the website is published, and what it still lacks](../../implementation-notes/website/2026-09-22-website-publishing-contract.md)
- Retroactive build check, 2026-09-22: `docs/` at `main` commit `a989155`
  builds with the current website and holds the 0.2.12 guides; the
  `release-0.2.12` head holds none and its README fails the landing adapter,
  which is why versions take only `docs/` from their source.
