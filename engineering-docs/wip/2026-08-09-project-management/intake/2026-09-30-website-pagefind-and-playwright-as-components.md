# Owner direction: Pagefind and Playwright as future components

From: website (the pair, on the owner's direction). To: project-management. Date: 2026-09-30.

The owner asked for Pagefind (build-time static-site search, in-browser
queries) and Microsoft Playwright (browser automation used by the website's
checks) to be added to this capsule's `/opt/xtras` now and configured later
as proper catalog components. They are installed under xtras today, from npm,
with launchers in `/opt/xtras/bin` and Playwright's browsers under
`/opt/xtras/playwright/browsers`: Pagefind 1.5.2, Playwright 1.63.0 with
Chromium headless shell 153. That is a personal, checkout-scoped install;
nothing in the project declares them.

Handed over: the product decision to make both curated components, which is
a catalog question: acquisition and checksum contract for the npm packages
and for Playwright's browser downloads, the persistent slot for the browsers,
and whether they are selected by the website workstream's declaration only or
offered generally. Accepting means placing it in the component backlog with
its sequencing; implementation belongs to the workstream that owns the
catalog when it is picked up. Pagefind is also the candidate for the website
project's W10 search bar, assessed for the owner on 2026-09-30.
