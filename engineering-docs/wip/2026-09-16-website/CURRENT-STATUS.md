# Workstream Current Status: Website

Mnemonic: `website`

Start date: `2026-09-16`

State: active 2026-09-19; experiment accepted as successful with A−; follow-up task inventory requested by the owner, implementation not started

Branch association: `website/initial-cut`; prefix `website/`

Integration target: DevCapsule `main`. Website PR #1 is merged into its `main`
at `b55ea0a`, with the same tree as previewed implementation `c508b91`.

Delivery method: reviewable SSH-pushed branches; the owner creates/merges PRs
and performs final GitHub backend wiring. The owner has now authorized making
the site live at `devcapsule.mycodespace.ai` before finishing the review.
No force-push or mainline implementation is needed.

## Synchronization And Pause (2026-09-18)

The owner requested synchronization with main and a switch to project-management.
The clean website branch fast-forwarded to fetched main `042c094`; no conflicts
or implementation edits were required. Existing Open Threads below remain the
handoff: owner verdict, then closure records through the normal PR route.
Branch-name migration to `ws-website/` remains due before the next release
candidate under WORKFLOW-LOCAL.md's transition exception. No migration or
additional website work was requested in this synchronization task.

Validation: `nox -s build` passed, including all nine packaging integration
checks. The dirty-tree policy skipped the public revision-bearing PEX; the
local validation artifact passed. Pause records are sent separately through
`ws-website/outbox` for the owner to merge; production was not rechecked during
this Git-only task. The target project-management branch has divergent local
and remote histories; owner direction is pending before switching or merging
there.

## Task Contract And Current Stage

The [website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md)
is the contract. The owner explicitly selected this fresh-context experiment,
delegating design and implementation after initial setup. Implementation is
complete through hosted production. The owner accepted the experiment as
successful with A− and requested the follow-up inventory below. Publication
before final review was separately authorized; acceptance is now settled.
Further implementation awaits selection of a bounded follow-up slice.

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

Next step: review the prioritized follow-up tasks below with the owner, incorporate
his additional findings, then select one implementation slice. The current request
is to enumerate and preserve shortcomings, not to implement all of them or close
the workstream. Future website development remains expected.

Urgent exception authorized 2026-09-19: implement the W00 prerequisite to serve
Google's ownership verification file. Website branch `google-site-verification`
at `4a9ba02` adds the exact response at `/googledda808d7513923e5.html`, copies it
unchanged at build time, and lets validated verification files pass page checks
and promotion without canonical rewriting. The parent pins that implementation.
All 12 website tests, production-mode build, 582 link/asset checks and an exact
source/output comparison pass. The candidate round-trip test preserves the file.
No visual checks or container builds were needed. Public deployment and Search
Console verification are still pending; this does not close W00.
The existing required parent `nox -s build` integration gate also passed;
the dirty-tree policy skipped the revision-bearing PEX.

Immediate next step: owner merges the website fix, then this parent submodule
update. Run the parent Website workflow on main with mode `production`, origin
`https://test-devcapsule.mycodespace.ai`, base `/`; promote the new candidate
using the website's production workflow on main. Check the production root
verification URL before clicking Verify in Search Console. Retain the file in
future deployments; older candidates lack it. SSH-only delivery still applies.

The owner accepted the experiment as successful with an A−, explicitly valuing
the agent's recognition of shortcomings. That verdict is now recorded; do not
ask for it again. On 2026-09-19 the owner specifically requested task items in
this workstream. This supersedes the earlier plan to archive immediately and the
earlier limitation against keeping a parent workstream website backlog. Content
ownership is unchanged; execution may later move to the standalone website only
with the owner's direction.

Resume: clean checkout switched from project-management to the registered website
branch for this explicit continuation, then fast-forwarded to origin/main d71559a.
The older branch name remains covered by WORKFLOW-LOCAL.md's adoption exception.
Mail take with explicit --workstream website reported no mail; intake is empty.
No existing open bug record was owned by website at review start. No project-
management implementation or workstream state was changed.

Workflow synchronization, 2026-09-19: merged fetched main `3f573b5` into the
published working branch without rewriting history; reread AGENTS.md,
WORKFLOW.md and WORKFLOW-LOCAL.md under the declared `0.2.14.dev0` definition.
Mail take again found no website mail. The open website-owned bug is the W01
test-publication input defect linked below. Website source and deployments were
not changed or revalidated during this workflow-only task.

Inter-workstream items now use `devcapsule workflow mail` on `coordination`;
our own status, registry row and bug records still travel `ws-website/outbox`.
The existing unmerged records delivery is preserved. The new coordination
section conflicts with leftover main/outbox intake prose elsewhere in
WORKFLOW.md and AGENTS.md. Following the owner's explicit instruction and the
new section, use mail for delivery and working-branch commits for decisions.
Reported the contradictory guidance to `workflow-improvements` by mail as
`2026-09-19-website-mail-protocol-stale-guidance.md`; our intake README now
describes the new mechanism.

Validation after synchronization: `nox -s build` passed (633 tests, one expected
failure, and nine packaging integration checks). The local PEX passed; the
revision-bearing PEX was skipped under the gate's dirty-tree policy.

Final live check on 2026-09-18: production and test homepage, documentation,
first-session guide and journal all return HTTP 200 over validated HTTPS.
Production canonical URLs are correct and the visible build time is
2026-09-18T00:43:08.793Z. Its build-info records content
`5a4b35435ee3e1cb460b48d292f15e5efe5228be`, implementation
`0691956e3aa383b74c9fb87f4d46140136b8a0b6`, and candidate
`website-candidate-35292339140-1`. Anonymous public candidate metadata matches
production source revisions and archive checksum provenance. The previous
production TLS hostname mismatch is resolved.

The test site's newer 00:57 UTC build uses production canonical URLs. This is
servable but does not meet the current candidate packaging checks. Record input
simplification as maintenance; production's earlier valid candidate is correct.
Future candidate runs must retain the test origin and root base path.

All implementation and timestamp changes are on remote main. Final handoff
updates live on website `experiment-handoff` and parent `website/initial-cut`.
The workstream stays open for the owner-requested follow-up inventory.
Experiment acceptance is recorded above; no independent website session is claimed.

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
Experiment acceptance is successful, A−. Administrative finalization is deferred
while the owner is assembling follow-up tasks in this workstream.

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
- Hosted test deployment, public candidate metadata and production promotion/HTTPS
  are now independently verified on 2026-09-18; details are in continuation above.
- Release promotion: eleven website tests pass, covering credential-free downloads,
  archive corruption/unsafe paths, source validation and byte preservation.
  A clean build of the deployed sources passed packaging, simulated anonymous
  download, promotion and all 582 local links across 16 pages. Both workflows
  pass actionlint 1.7.12. No page appearance or parent runtime source changed.

The required parent `nox -s build` gate passed again, including all nine
packaging integration checks. Its dirty-tree policy skipped the public revision
PEX; the local PEX build and smoke checks passed.

Timestamp validation: all 11 unit tests, the build and 582 local links pass.
Twelve desktop/mobile browser audits pass without overflow or automated WCAG
A/AA violations. Additional desktop/mobile/320px checks without JavaScript
confirm that the visible timestamp matches the manifest; footer screenshots
were visually inspected. Existing promotion tests confirm builtAt is preserved.

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
website's [publication instructions](../../../website/PUBLISHING.md) give
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

## Inventory Validation (2026-09-19)

Read-only checks inspected both live sites' metadata/robots and discovery URLs,
and the current build/promotion implementation. No deployment or product source
was changed. Corrected pre-existing website-document relative links in this
status file while validating the records. Reviewed links resolve except the
unchanged index entry into an uninitialized sample-project submodule.
The required nox build gate passed, including nine packaging integration checks;
the dirty-tree policy skipped the public revision PEX, as expected. Mail and the
pre-existing website bug queue were empty. The confirmed publishing-input defect
is now recorded with owner website; follow-up details remain in this status file.

## Follow-up Tasks (2026-09-19)

All items below are **open; inventory only**. The owner designated **W00 as the
top priority (gating)**. The remaining priority order is proposed, not a
release commitment: **P1** removes publishing/verification traps; **P2** improves
maintainability and user understanding; **P3** is a useful enhancement to scope
with the owner. These are not retroactive reasons to revoke the accepted grade.
Requirements basis: the work order's repeatable updates, content ownership,
reading experience and reviewable publication; enhancements beyond that baseline
are identified explicitly. No paid service or automatic production publishing is
implied. Verification is a future task, not evidence claimed today.

Ownership clarified by the owner: DevCapsule owns authored content and content
decisions; devcapsule-website owns website functionality, appearance and
publishing. Website-owned items must migrate there; mixed items need linked
content and implementation tasks. This inventory remains here pending that
migration. W00 belongs to devcapsule-website. W09 remains unchanged and separate.

### W00 — Gating, top priority: Establish and verify Google search discoverability

- [ ] Diagnose and resolve production's absence from Google search results.
- Evidence: the owner reports no results for
  `+site:devcapsule.mycodespace.ai github`. Direct public checks on 2026-09-19
  found homepage and `/docs/` returning HTTPS 200 with production canonicals,
  no robots/Googlebot noindex meta or X-Robots-Tag header, and robots.txt allowing
  crawling. `/sitemap.xml` returns 404. These checks do not establish what Google
  has crawled or indexed; the missing sitemap alone does not establish the cause.
- Done means: inspect production in Google Search Console with the owner's
  verified access; distinguish discovery, crawling, indexing and canonical issues;
  fix identified barriers; provide and submit a production sitemap (shared
  implementation with W09 where appropriate), reference it in robots.txt, and
  request indexing of key pages. Keep staging excluded under W02. Obtain evidence
  of indexing and representative production search results before closing;
  a successful build or submission alone is insufficient. Google's timing and
  inclusion decisions are external; record pending status rather than promising
  a deadline or ranking.
- Verify: Search Console URL Inspection/Page Indexing evidence for the homepage
  and representative guide, sitemap retrieval/submission, and a repeat of the
  owner's query. Use URL Inspection to diagnose indexing; a site query alone is
  not an exhaustive index report. No Search Console access/result is claimed yet.
- Reopen if intended public pages become undiscoverable or publication changes
  introduce indexing barriers.

### W01 — P1: Make the test publication action hard to misuse

- [ ] Resolve the [confirmed input-validation bug](../../bugs/website/2026-09-19-test-publishing-accepts-inconsistent-settings.md).
- Evidence: parent `.github/workflows/website.yml` defaults to `preview`, labels
  test deployment `production`, and lets the origin/base path disagree with the
  candidate conditions. Wrong settings can yield a successful run with skipped
  jobs, or replace staging with a build that cannot be promoted.
- Done means: clear build-only/deploy-test choices; deploy-test is the owner-
  requested normal default; its host/base path are fixed or validated before
  deployment; intentional skips and invalid inputs are explicitly explained.
- Verify: default dispatch produces a test deployment and candidate; build-only
  is explicit; wrong host/path and wrong branch cannot quietly publish or skip.
- Reopen if new modes or destinations reintroduce incompatible combinations.

### W02 — P1: Distinguish staging and prevent accidental indexing

- [ ] Give staging a visible environment label and an explicit noindex policy,
  separate from the existing build-only/production rendering mode.
- Evidence: live test HTML on 2026-09-19 has no robots noindex meta, its robots.txt
  says Allow: /, and the shared layout has no test label. Its latest canonical
  URL points at production. This is observed configuration, not proof of indexing.
- Done means: visitors can identify staging; a chosen staging canonical policy and
  noindex directives are consistent; promotion deliberately removes staging-only
  metadata while preserving content. Update promotion's currently strict robots
  and canonical validation together, rather than patching the template alone.
- Verify: inspect staged and promoted HTML/robots, desktop/mobile label visibility,
  and a file-difference check limiting transformation to the agreed metadata.
- Reopen if a new host or rendering mode bypasses the staging policy.

### W03 — P1: Show what is being promoted and what is currently live

- [ ] Make candidate selection understandable without copying opaque tags between
  repositories and manually reading raw build-info JSON.
- Evidence: production accepts one free-text candidate tag; there is no comparison
  with deployed production, human-readable change summary, or publication timestamp.
  The footer's builtAt correctly preserves build time, including on rollback.
- Done means: the owner can see the selected candidate's content/presentation
  changes, source test run and comparison with current production before approval;
  current deployment/candidate identity and publication time are discoverable.
  Keep build time distinct. Decide how an older candidate is reviewed once the
  shared staging URL has advanced; do not imply that URL still shows the old one.
- Verify: two different candidates and an intentional rollback display the correct
  changes/identities; publication metadata does not rewrite original build time.
- Reopen if candidate selection becomes ambiguous again.

### W04 — P1: Validate website changes before the manual publishing run

- [ ] Add proportionate PR validation in both content and presentation repositories.
- Evidence: the website workflows are workflow_dispatch only. Publication runs
  unit/build/link checks; the existing browser/accessibility checks are absent
  from those workflows. Current browser evidence came from local agent execution.
- Done means: relevant content and website PRs run build/link/unit checks, with
  representative browser checks where appropriate, using the correct content and
  presentation revisions. PR checks produce reviewable output without deploying
  or exposing a write token to untrusted PR code.
- Verify: an intentionally broken link/layout fixture fails the appropriate check;
  a presentation PR builds its proposed version without first needing a parent
  submodule merge. Preserve manual production promotion.
- Reopen if a content/implementation path can merge without relevant validation.

### W05 — P1: Verify the public result after deployment

- [ ] Add bounded post-deployment checks before calling a test candidate or
  production deployment successful.
- Evidence: both workflows stop deployment verification at deploy-pages success.
  They do not fetch the custom domain, validate its TLS/canonical/robots policy,
  or compare the served build-info revision with the intended candidate.
- Done means: distinguish an API-accepted deployment from a verified served site;
  check homepage, representative deep link/assets and provenance with bounded
  cache/propagation retries; give a useful failure summary. Do not automatically
  roll back based on an ambiguous transient network failure.
- Verify: wrong revision/hostname and a broken deep link produce actionable failure;
  a normal delayed propagation succeeds inside the documented bound.
- Reopen if a hosting or caching change defeats served-revision verification.

### W06 — P2: Make rollback and candidate retention operationally reliable

- [ ] Document and rehearse restoration, protect needed candidates, and define
  retention/recovery for missing assets and partially published releases.
- Evidence: rollback is another dispatch with an older tag; no live rollback has
  been exercised. Candidate assets are mutable/deletable, with no archive policy.
  A checksum stored beside its archive detects inconsistency, not an independent
  provenance proof against an authorized rewrite of both. Candidate prereleases
  also accumulate in the same Releases list visitors use for the CLI download.
- Done means: identify the last known good candidate; preserve required assets;
  exercise recovery in staging before any separately authorized production drill;
  define cleanup that cannot remove deployed/rollback candidates and keep CLI
  downloads easy to find. Handle release-upload failure without falsely claiming
  the already deployed test site rolled back. Choose immutability/backups based
  on the owner's actual recovery requirement, not speculative security machinery.
- Verify: restore an older candidate with unchanged content/assets, exercise missing
  and corrupt assets, and confirm cleanup/recovery preserves known-good releases.
- Reopen if release storage or cleanup changes invalidate the recovery procedure.

### W07 — P2: Remove brittle coupling to README wording and paragraph order

- [ ] Define a resilient landing-content mapping without duplicating authored prose.
- Evidence: `website/scripts/content.mjs` matches literal English headings and
  assigns paragraphs[0], paragraphs[1], slice(2,4) to visual roles. A harmless
  heading rename fails the build; reordering/adding prose can misassign sections.
- Done means: explicit stable section identities or another owner-approved content
  contract; routine editorial changes preserve intended grouping or fail with a
  targeted author-facing explanation; new authored content is not silently lost.
- Verify: heading rename, inserted/reordered paragraph and new section examples
  reviewed for meaning, not merely passing a test derived from the implementation.
- Reopen if ordinary editing again requires changing presentation code.

### W08 — P2: Make content status and version explicit

- [ ] Decide which drafts/historical pages belong on the public site, and make
  current documentation's supported version and freshness understandable.
- Evidence: all Markdown under docs is imported; historical/draft status is inferred
  from `/product/` or `docker4pycharm` in the filename. Draft announcement pages
  are therefore public and indexable today, though visibly labeled. A fresh site
  build does not establish that an individual guide is current. The accepted
  v0.2.12 guide rewrite still belongs to user-docs, not this review.
- Done means: an explicit publication/status contract and version presentation,
  agreed with the content owner. Decide inclusion vs labeling vs noindex for
  drafts; preserve intentional historical links. Do not silently rewrite guides.
- Verify: representative current, draft and historical documents, plus a newly
  added file, receive the intended visibility/status/version and navigation.
- Reopen if path naming again becomes the only publication/status decision.

### W09 — P2: Improve discovery and link previews

- [ ] Add deliberate production metadata and a sitemap; fix redundant social titles
  and choose useful descriptions/social images for homepage, docs and blog entries.
- Evidence: production sitemap.xml returns 404; base.njk has og:title and og:type
  only, without og:url/image/description. Homepage og:title is
  `DevCapsule · DevCapsule`; its description is the first setup paragraph rather
  than a concise product explanation. No search-ranking penalty was measured.
- Done means: accurate, nonduplicated metadata and canonical URLs, a sitemap limited
  to intended public pages, and meaningful share cards without inventing claims.
- Verify: generated head/sitemap checks and actual share-card previews for the
  homepage, guide and article; staging/drafts follow W02/W08 decisions.
- Reopen if new page types inherit misleading generic metadata.

### W10 — P3: Help readers find answers and follow the journal

- [ ] Scope lightweight documentation search/topic navigation and an RSS/Atom feed.
- Evidence: sidebar/toc navigation exists, but there is no site-wide search or
  journal subscription link/template; live feed.xml returns 404. These are
  enhancements, not failures of an original search/feed requirement.
- Done means: a reader can locate a known topic across guides, distinguish current
  from historical answers, and subscribe to new articles. Keep ordinary reading
  usable without JavaScript; avoid adding a backend/service without need.
- Verify: representative novice search tasks, keyboard/mobile use and an independent
  feed reader. Agree relevance/navigation expectations before choosing a library.
- Reopen if corpus growth makes answer-finding or feed delivery unreliable.

### W11 — P2: Validate the experience with people and browsers beyond this setup

- [ ] Test an unfamiliar visitor's first-use journey, and fill the explicit browser,
  performance and standalone-environment evidence gaps proportionately.
- Evidence: current browser evidence is Chromium automation plus agent screenshots;
  no independent novice study, Firefox/WebKit/mobile-device checks, performance
  budget or graphical launch of the website's own capsule is recorded. This is
  missing evidence, not a claim those experiences are broken or slow. The hero
  illustrates a concept but does not demonstrate an actual DevCapsule session.
- Done means: choose a small user task and target-browser set with the owner;
  record where a newcomer gets stuck and fix prioritized findings. Measure before
  choosing performance work; assess whether an authentic screenshot/demo clarifies
  the product. Verify the advertised standalone setup rather than assuming it.
- Verify: documented task outcomes and targeted browser/device/environment evidence;
  thresholds and stop conditions agreed before expanding the test matrix.
- Reopen if new layouts/platform promises invalidate the tested user journey.

## Open Threads

- Owner has accepted the autonomy experiment: successful, A−. No further verdict
  request is pending. Workstream closure is deferred at his request for this task
  inventory; his additional shortcomings and priority corrections remain welcome.
- W00–W11 are inventoried here per explicit owner instruction; W00 is first.
  Website-owned tasks await migration to devcapsule-website under the agreed
  content/implementation split. No fix, feature,
  deployment, new service, live rollback or expanded test campaign was authorized
  merely by recording them. Select a bounded slice before implementation.
- Existing release/publication decisions stand: authoritative content here,
  presentation in the website repository, public release candidates, no personal
  deployment token, manual production approval.
- No allowance/reset telemetry exists; exact experiment expenditure is unknown.
  No paid purchase or anticipated budget overrun was identified.
- Full transcript, duplicate content and speculative implementation plans are not
  preserved. This is a task inventory and acceptance record, not a session export.

## Documents

- [Work order](../../work-orders/2026-09-16-website-autonomy.md)
- [Test publication input bug](../../bugs/website/2026-09-19-test-publishing-accepts-inconsistent-settings.md)
- [Website developer guide](../../../website/README.md)
- [Publication and exact final steps](../../../website/PUBLISHING.md)
- [Website independent handoff](../../../website/CURRENT-STATUS.md)
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)
