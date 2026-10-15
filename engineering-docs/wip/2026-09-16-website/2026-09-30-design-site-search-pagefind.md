# Design Idea: Site Search With Pagefind

Date: 2026-09-30. Owner: `website`. Status: **saved, deferred** by the owner:
not part of 0.2.16; picked up only if time is left, then as the website
project's backlog item W10. Nothing here is scheduled.

## The Idea

Search built at build time, queried in the browser, no service and no
third-party fetch. Pagefind, an open-source Rust CLI with a JavaScript
client, runs after Eleventy over the built `_site/`, writes a chunked index
and its small UI beside the pages, and the browser loads only the chunks a
query needs. Tried on 2026-09-30 in this capsule with the copy under
`/opt/xtras`: 180 pages indexed in 0.14 seconds, 1.6 MB of index.

## Why It Fits This Site

- It is a step of the website's own `npm run build`, so it runs the same way
  locally, in the parent's **Website** workflow on the GitHub runner, and
  therefore inside the candidate that is promoted to production. The npm
  package installs the platform binary; the workflow file does not change.
- It indexes exactly what the contract publishes and nothing else, and it
  knows about versions if we tell it: `data-pagefind-body` on the article,
  `data-pagefind-ignore` on planned stubs and legacy trees, or a `version`
  filter on every page with the search box defaulting to current.
- Its UI takes the design tokens through CSS variables and is self-hosted,
  which keeps the site's rule of no external script or style.

## What The Consumer Would Do

1. Add `pagefind` as a dependency and one command after Eleventy in
   `npm run build`; the index lands in `_site/pagefind/`.
2. Mark the article body, the ignored pages and the version filter in the
   layouts, per the contract's statuses and versions.
3. A search field in the header opening Pagefind's UI, styled with the
   tokens; a `/search/` page for the no-JavaScript case that says search
   needs JavaScript and links the versions index.
4. Let the link checker accept `/pagefind/` and confirm promotion leaves the
   index untouched; it holds site-relative URLs and no host.
5. Browser check: a query for "xtras" finds the extra-tools page in current
   and not the 0.2.12 tree; a query at 360px is usable.

## Alternatives Considered

Google Programmable Search Engine: one script tag, but it searches only what
Google has indexed, which lags every release and is empty today; the free
tier shows ads; it injects Google's script and styling; it knows nothing
about versions. Lunr, Elasticlunr, FlexSearch, MiniSearch, Fuse.js, Orama,
Stork: client-side libraries or WebAssembly indexes where the index build
and the UI are ours to write; Pagefind is the one that does build-time HTML
indexing, chunked loading and the UI as one package.
