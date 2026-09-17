# Workstream Current Status: Website

Mnemonic: `website`

Start date: `2026-09-16`

State: active; initial PRs merged and test site working; production promotion action prepared; final review remains open

Branch association: `website/initial-cut`; prefix `website/`

Integration target: DevCapsule `main`. Website PR #1 is merged into its `main`
at `b55ea0a`, with the same tree as previewed implementation `c508b91`.

Delivery method: reviewable SSH-pushed branches; the owner creates/merges PRs
and performs final GitHub backend wiring. The owner has now authorized making
the site live at `devcapsule.mycodespace.ai` before finishing the review.
No force-push or mainline implementation is needed.

## Task Contract And Current Stage

The [website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md)
is the contract. The owner explicitly selected this fresh-context experiment,
delegating design and implementation after initial setup. Implementation is
complete to a reviewable local preview; experiment success awaits owner judgment.
Do not expand or keep polishing before that review. The owner said the preview
looks good and chose to finish reviewing after publication at the actual domain.
That later instruction supersedes the work order's publication-after-final-review
sequence; it does not constitute final experiment acceptance.

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

Next step: the owner merges website `production-pages`, then parent
`website/initial-cut` with the updated website pin and test workflow. Squash
merges require selecting the merged website revision in the parent first.
Configure production Pages/DNS/HTTPS; no personal token or repository secret is
needed. Start a new parent Website run from updated main, review the test site,
then promote its public candidate release tag using the website production action.
See website PUBLISHING.md for the complete sequence.

The owner rejected personal-token renewal overhead and selected public GitHub
Release assets. The parent workflow publishes a candidate prerelease only after
successful test deployment, using built-in GITHUB_TOKEN with contents: write
only in the candidate job. Tags use website-candidate-RUN_ID-ATTEMPT and cannot
replace the latest CLI release. Production downloads public assets anonymously,
validates SHA-256/source metadata/archive paths and promotes without rebuilding.
The only generated-page changes are canonical origins and promotion provenance.
Releases remain available until deleted; Actions artifact/log retention is no
longer a promotion/rollback dependency. The former CANDIDATE_READ_TOKEN proposal
is superseded; do not ask the owner to create or renew it.

On 2026-09-17, both checkout HEADs matched fetched remote main (parent `8233dab`,
website `b55ea0a`). The parent integration is merged. The owner reports the test
site works well; HTTPS manifest and GitHub API independently confirm test run
`35187865183`, content `8233dab98bf85710bb73ebd3e66ef0b29880eaf4`, website
`b55ea0a378725080bc7cf13b2c78844b2d225c52`, with successful build and deploy.
Only `mycodespace.ai` is owned; all `codespace.ai` spellings were human typos.
Test is `test-devcapsule.mycodespace.ai`; production is `devcapsule.mycodespace.ai`.
Formal experiment acceptance and finalization remain open.

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
- Test-site Actions build/deploy success and HTTPS manifest independently verified
  on 2026-09-17. New public candidate publication and production deployment remain
  unverified; owner merges and dispatches are the agreed completion path.
- Release promotion: eleven website tests pass, covering credential-free downloads,
  archive corruption/unsafe paths, source validation and byte preservation.
  A clean build of the deployed sources passed packaging, simulated anonymous
  download, promotion and all 582 local links across 16 pages. Both workflows
  pass actionlint 1.7.12. No page appearance or parent runtime source changed.

The required parent `nox -s build` gate passed again, including all nine
packaging integration checks. Its dirty-tree policy skipped the public revision
PEX; the local PEX build and smoke checks passed.

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

- Awaiting human: website and parent PR merges, production domain/HTTPS and manual
  workflow runs. Start a new test run from updated main; old run 35187865183 has
  no public release assets and rerunning its old definition cannot create them.
- Chosen: public release candidates remove personal-token maintenance and allow
  promotion/rollback after Actions artifacts expire. Keep release assets for as
  long as rollback is required; owners can still delete or modify releases.
- Separate test noindex support remains outside this slice.
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
