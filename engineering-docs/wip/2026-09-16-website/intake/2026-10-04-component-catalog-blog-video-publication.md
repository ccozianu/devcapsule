# Journal video assets: native publication support

From: component-catalog
To: website
Date: 2026-10-04

The owner requested a blog entry about the IntelliJ/Playwright delivery and
links to the graphical test movies, and asked whether movie files copied into
the content tree would survive publication. The entry and original recordings
are on `ws-component-catalog/intellij-idea`:

- `engineering-docs/blog/2026-10-04-an-ai-takes-intellij-for-a-test-drive.md`
- `engineering-docs/blog/assets/2026-10-04-intellij/first-session.webm`
- `engineering-docs/blog/assets/2026-10-04-intellij/after-restart.webm`

The two movies total 14,976,211 bytes, run 166.28 and 66.48 seconds, and decode
and play in the installed Chromium. They are byte-for-byte original recordings.

At the current mainline website pin, `scripts/content.mjs` treats only image
extensions as copied assets and rewrites `a[href]` and `img[src]` only. A relative
WebM link becomes a GitHub blob permalink; `<video>`/`<source>` URLs are not
resolved or copied. `scripts/preview.mjs` has no WebM MIME mapping either.

The blog works within that contract: linked screenshot posters and relative
movie links with `?raw=true`, rendered as revision-pinned repository downloads.
The preview build and link checks pass. Native embedding is not claimed.
No website source or parent gitlink was changed.

Please decide native video support for authored content. It belongs here because
this workstream owns the publishing consumer and the website pointer. Acceptance
would define supported Markdown/media markup, copy and rewrite movie/poster paths
with the site's base path, serve appropriate MIME types, retain fallback download
links, and verify playable output survives candidate packaging and promotion.
It should account for draft exclusion and local-link validation. The existing
recordings provide a real fixture; prioritization and timing remain yours.
