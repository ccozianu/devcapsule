# Workstream Current Status: Website

Mnemonic: `website`

Start date: `2026-09-16`

State: active; initial implementation ready for owner review; production not published

Branch association: `website/initial-cut`; prefix `website/`

Integration target: DevCapsule `main`, after the website project's reviewed
`initial-cut` branch reaches its own `main`.

Delivery method: reviewable SSH-pushed branches; the owner creates/merges PRs
and performs final GitHub backend wiring. Production publication follows review.
No force-push or mainline implementation is needed.

## Task Contract And Current Stage

The [website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md)
is the contract. The owner explicitly selected this fresh-context experiment,
delegating design and implementation after initial setup. Implementation is
complete to a reviewable local preview; experiment success awaits owner judgment.
Do not expand or keep polishing before that review.

The site presents the root README substance, current user guides, and all three
development-blog articles. Other engineering/developer references lead to GitHub.
Current v0.2.12 guides remain the accepted interim content; their V1 rewrite is
still user-docs work. No product requirement or source-content rewrite was made.

## Review And Continuation

Preview: **http://127.0.0.1:8080/**, running on loopback in this host-networked
capsule. The owner confirmed localhost access and authorized trying subsequent
ports if occupied. The development server watches content and presentation;
refresh the browser after it reports a rebuild. This is a local preview, not a
hosted deployment.

Restart from this checkout's root:

```sh
git submodule update --init website
./scripts/website.sh install
./scripts/website.sh preview
```

Use the printed URL if 8080 is occupied. `PORT=8090` changes the starting port.
Build/check on demand: `./scripts/website.sh build`.

Next step: the owner reviews the landing page, a guide and a journal entry.
If accepted, prepare final document/status moves under `WORKFLOW.md`, integrate
website then parent by PR, and complete the prepared Pages/DNS wiring. If the
owner requests changes, keep them in this workstream and record the review
outcome. Do not claim integration or final experiment success before it happens.

## Delivered Structure

- Public `ccozianu/devcapsule-website`, included as Git submodule `website/`,
  owns Eleventy 3.1.6, styles/layouts, navigation, build/import/preview scripts,
  tests, and its own developer instructions and single-stream handoff.
- Content remains authoritative here: root README, `docs/**/*.md`, and blog
  articles under `engineering-docs/blog/`. No manually maintained content copy
  was introduced in the website repository.
- Root `scripts/website.sh` is the small parent build/update interface.
  `.github/workflows/website.yml` prepares manual artifact builds and explicit
  owner-triggered Pages publication. Content merges and releases do not deploy.
- Standalone website development consumes an explicit `CONTENT_DIR` or an
  ignored, nonrecursive DevCapsule checkout. No parent gitlink update is needed
  to work independently on the website.
- Each output records content/implementation revisions, dirty indicators, a
  consumed-content digest, mode and base path in `build-info.json`. Relative
  links/anchors become local routes; engineering references use the content SHA.
- The website's DevCapsule manifest selects Node/VSCodium and includes a
  generated Linux platform lock. Host networking is recommended for preview
  and subject to developer authorization. No host Docker access is requested.
- Independent future presentation work belongs in that project. The initial
  submodule implementation is part of this workstream, as the work order allows;
  no second workstream was opened and no independent pair transition is claimed.

## Validation Evidence

- Parent `./scripts/website.sh build`: 16 HTML pages and 582 local
  links/assets/anchors checked, plus document headings, image labels and
  revision metadata. Passed.
- Four focused routing/rendering tests: relative links, GitHub permalinks,
  missing targets, heading slugs, literal template syntax, subpath deployment.
  Passed.
- Chromium desktop (1440px) and mobile (390px): 12 representative page/viewport
  audits passed without automated WCAG A/AA violations, page overflow or JS
  errors. Keyboard skip link, section anchors, and no-JavaScript navigation pass.
- Inspected desktop homepage, guide and mobile rendered screenshots. A separate
  320px reflow check passed; clipboard output exactly matched the code example.
  These checks inform review; they do not establish owner satisfaction.
- Clean standalone clone: `npm ci`, build and link check passed. A paragraph
  change reached generated output and changed its content digest; a CSS change
  reached output without changing content or its digest. `/devcapsule/` link
  checks and production canonical/robots metadata passed. No parent submodules
  were initialized in that test.
- Website DevCapsule manifest and lock generated/validated using this repo's
  resolver and configuration validators. A separate capsule launch was not run.
- Required parent gate: `devcapsule-src/.venv/bin/python -m nox -s build` passed,
  including compilation, shell syntax, type checks, tests, CLI/PEX smoke and
  nine packaging integration checks. The dirty-tree gate intentionally skipped
  the public revision-bearing PEX; its local PEX passed. No runtime source changed.
- GitHub Actions execution, hosted Pages/DNS/TLS, and production deployment are
  untested and deferred by owner authorization; local script execution is the
  agreed validation for the update mechanism. npm audit reported no known
  dependency vulnerabilities at installation.

## Setup, Access And Budget

The starting checkout was clean. Accepted `origin/main` was `02eb470`; local
main was strictly behind (0 local-only, 102 remote-only). Registration, work
order, and empty intake were verified there. The published website starting
branch fast-forwarded from `6e87fc7` without rewriting history. Its preparation
from user-docs was the narrow exception already documented in the work order.

The owner created `ccozianu/devcapsule-website` with initial README commit
`ed4c18eebb96994966f3f98e1822878e0e723f75`. SSH clone and push dry run succeeded.
The owner instructed SSH-only operation without app access; do not request
GitHub app credentials again. He explicitly accepts running build/trigger
scripts by hand and defers final GitHub backend wiring to delivery. The
website's [publication instructions](../../../../website/PUBLISHING.md) give
the exact final sequence, including submodule handling after a squash merge.

No paid hosting, API usage purchase, cloud provisioning, model download, or
production publication was performed. Node dependencies, Playwright Chromium,
and the checkout-local Python validation environment were installed for the
required checks. Expected Pages/standard public-runner hosting cost is $0;
no paid services are enabled by this work.

The agreed account ceiling remains the subscription-month allowance and three
reported resets. The tools expose no allowance/reset balance or reset control;
actual remaining allowance is unknown. This chat is the stated exceptional
warning channel; no other contact was supplied or used. At rendering, browser
validation and delivery milestones, remaining work appeared feasible inside
the authorized ceiling. No anticipated overrun or reset need was identified.
An abrupt platform cutoff invisible to the agent cannot guarantee warning.

## Open Threads

- Awaiting human: first review of the visible site; final PR merges and
  Pages/DNS/TLS wiring after acceptance. This is the agreed review boundary.
- Weighed: GitHub Pages plus local review avoids cloud provisioning, tokens,
  DNS or mainline merges as implementation prerequisites. No hosted preview
  was needed; the owner confirmed localhost access.
- Deliberately unverified: a separate graphical launch of the website capsule;
  its configuration and clean standalone Node preview are verified.
- Deliberately not preserved: a full chat transcript, a second content copy,
  a website implementation backlog in DevCapsule, or speculative future features.

## Documents

- [Work order](../../work-orders/2026-09-16-website-autonomy.md)
- [Website developer guide](../../../../website/README.md)
- [Publication and exact final steps](../../../../website/PUBLISHING.md)
- [Website independent handoff](../../../../website/CURRENT-STATUS.md)
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)
