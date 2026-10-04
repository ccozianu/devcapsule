# IntelliJ, Playwright and parameterized graphical smoke validation

Date: 2026-10-04. Workstream: `component-catalog`. Target: 0.2.16.

Implements the accepted [work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md).
The [repeatable commands](../../development/e2e-tests.md#ai-driven-graphical-acceptance)
and their prerequisites live in the E2E guide.

## Delivered behavior

- `java-ide` selects IntelliJ IDEA 2026.2.3, the unified vendor distribution,
  using the shared JetBrains runtime adapter and independent `intellij/*`
  persistence slots. PyCharm's existing declaration is preserved through the
  extracted template. Java development tools come from the ordinary base;
  the IDE uses its bundled JetBrains Runtime.
- `browser-automation` adds Python Playwright 1.63.0, its four pinned wheels,
  Chromium/headless shell 153.0.8010.12 and FFmpeg. Every acquired artifact is
  SHA-256 checked; wheel installation is offline in an isolated `/opt/playwright`
  environment. ZIP extraction rejects traversal, links and special files.
  This pin targets Ubuntu 24.04, x86-64 and CPython 3.12. The repository's
  development manifest now selects it. No manual `/opt/xtras` install is
  needed by a newly materialized component-equipped capsule.
- One graphical scenario owns browser actions, the saved-file witness and
  visual recognition. Provider adapters select Codex/`gpt-6-astra` by default
  or Claude/`claude-fable-5-1`; the recognizer is independently configurable.
  Both CLIs receive images and return constrained decisions with their tools
  disabled. Only Playwright applies the decisions to the IDE desktop.
- Component-browser mode starts the child's installed Playwright server on
  loopback with a random endpoint path. The parent retains AI authentication;
  the child supplies the actual browser for screenshots, interaction and video.
  A bounded IntelliJ relaunch check changes editor font size to 17 through
  Settings and verifies that preference and the saved edit survive.

The vendor's [unified-distribution description](https://www.jetbrains.com/help/idea/intellij-idea-single-distribution.html)
describes free core functionality and paid features. The smoke uses the free
editor without signing in, starting a trial or purchasing a license.
The [Playwright browser documentation](https://playwright.dev/python/docs/browsers)
explains the matching package/browser requirement. Wheel hashes were checked
against PyPI metadata; browser hashes came from the version-specific URLs
shipped by Playwright 1.63.0. IntelliJ's archive hash matched its vendor checksum.

## Observed runs

Evidence is retained locally under
`devcapsule-src/dist/e2e-evidence/ide-smoke/<run>/`. It contains executable
identity, image/container identity, independent HTTP/window facts, screenshots,
WebM, model input/output and usage, selected/reported identities, saved-marker
results and cleanup records. Raw desktop URLs in launcher/server logs contain
ephemeral access tokens; this report omits them.

| Run | Surface | Action driver and recognizer | Result |
|---|---|---|---|
| `20261004T002250Z-01def7` | VSCodium | Claude / Fable 5.1 | Passed, 4 browser actions then final recognition |
| `20261004T002435Z-d44b57` | IntelliJ | Codex / GPT-6 Astra | Passed, 11 browser actions then final recognition; child component browser also launched and rendered HTML |
| `20261004T003322Z-b53949` | PyCharm | Claude / Fable 5.1 | Passed, 10 browser actions then final recognition |
| `20261004T005804Z-c554e8` | IntelliJ, then relaunch | Codex / GPT-6 Astra | Passed, 18 actions initially and 6 after relaunch; both browsers supplied by child component |

The first three runs used executable source `ada153c00637ab6561b7f4a13ea33321fb17b8ab`,
SHA-256 `5444230fb6f46b24e6faf619565565c947ae177a197551c97bde7a0a2d69a018`.
Each child runtime's executable checksum matched. All three test containers
were confirmed absent afterward; their unique workspaces and project records
were removed. Acquired artifacts and materialized images remain reusable cache.

The actual parent CLIs were `codex-cli 0.153.4` and Claude Code `2.1.261`.
Codex JSONL does not report a server model identifier: the explicit
`--model gpt-6-astra` invocation is recorded, without inventing a returned id.
Claude reported `claude-fable-5-1` in model usage. Both providers interpreted
screenshots; recognition reviewed chronological frames from the browser
session, with the complete movie retained. No direct video-input support is
claimed for either CLI. Usage is recorded where exposed; no exact cost is inferred.

## Component repeat and persistence

The repeat uses executable source `0a928cfa8cc1adcd5cfbaed9d6ff0ffeff6a3183`,
SHA-256 `f1f679ec383d32e2efd59244662523ea653f424fd070202362f4eb26a669a935`,
and the shared browser-connection harness at `59ccae8`.
Its Nox binding comes from wheels exported from the verified component image.
The parent's browser path is deliberately nonexistent, so the browser proof
must come from the child's component. Run `20261004T003852Z-d50716` passed
the component-browser interaction, but screenshot review found `Start Failed`
on relaunch despite the initial deterministic assertion passing. That result
is rejected as persistence acceptance. The [stale-directory-lock bug](../../bugs/devcapsule/2026-10-04-intellij-relaunch-stale-directory-lock.md)
records the evidence, targeted adapter recovery and strengthened criterion.
The corrected repeat `20261004T005804Z-c554e8` passed at runtime source
`d6d356670ce34c7fb57f5b03a2344bf20eac2f0a`, executable SHA-256
`7a109dcddaa6197e9f5ec79d046b2f36092431dd7ab44b48eb493933ca4ecf9d`,
and harness `c5e0535`. Its relaunch log records recovery of the stale socket
under exclusive profile ownership. Font size remained 17, the first marker
remained on disk, and a second Codex/Astra interaction saved and visually
confirmed a new marker. Both browser sessions ran in the child component;
the parent still had no usable browser path. Both containers were removed,
and every path in the removed-project-record list was independently confirmed
absent. The defect is closed by that validation.

![IntelliJ after relaunch with both saved markers](assets/2026-10-04-intellij-relaunch.png)

The implementing agent also reviewed the retained final screenshot: it shows the working
editor with both markers. The script-launcher and Java-options notifications
are visible; neither prevented the tested interaction.

## Blog recordings

The owner-requested [blog entry](../../blog/2026-10-04-an-ai-takes-intellij-for-a-test-drive.md)
preserves the two original `agent-desktop.webm` files from accepted run
`20261004T005804Z-c554e8`, with the final screenshot of each phase. Copies
under `engineering-docs/blog/assets/2026-10-04-intellij/` are byte-identical
to the retained evidence; no trimming, transcoding or speed adjustment occurred.
Chromium decoded both movies at 1600×1000 and sampled frames were reviewed.

| Blog file | Source within the run's `intellij/` directory | Duration | Bytes | SHA-256 |
|---|---|---|---|---|
| `first-session.webm` | `agent-desktop.webm` | 166.28 s | 10522080 | `c42eb8a0282e9dc035ee88cc61f65ec9ce752f3cbd96f03368d9c5c9ea356614` |
| `after-restart.webm` | `relaunch/agent-desktop.webm` | 66.48 s | 4454131 | `ff85e95f6cccc0fd7ea32f3e99224877b8feeb073c08b38503ff48da827a3724` |

The pinned website consumer copies image assets but does not copy WebM or
rewrite `<video>` sources. The entry therefore uses ordinary Markdown linked
posters and movie links with `?raw=true`. The builder turns these into GitHub
blob links pinned to the content revision; the query requests the raw file.
Production builds from main will pin the links to that mainline commit.
The movies remain repository-hosted downloads rather than embedded site assets.
The draft is included in preview and excluded from production until owner release.
Native video publishing is handed to the website workstream; its implementation
and the website gitlink are unchanged here.

Publication checks on 2026-10-04: `scripts/website.sh build` passed (186 HTML
pages, 13,529 local links/assets/anchors). Chromium loaded the draft and both
posters, verified the two distinct rendered movie URLs, and played each copied
WebM without a media error. A production content build excluded the draft.
This validates preview rendering and the download-link construction, not an
embedded player or a deployed website. The website mail is
`2026-10-04-component-catalog-blog-video-publication.md`, coordination commit
`ad17bb1d3605`. The documentation addition also passed the required full
`nox -s build` gate: 1,117 tests and nine packaging tests, with the existing
expected-failure/expected-pass results. Log: `.git/intellij-blog-build.log`.

## Gates and boundaries

`nox -s build` passed at `d6d3566`: syntax, mypy, 1,117 passing tests,
the existing one expected failure and one expected-pass result, executable
smokes, nine packaging integration tests and the website content contract.
The final harness path correction also passed targeted type checking and
focused tests, and is included in the successful corrected repeat. The scratch root is `/opt/devcapsule-gate`, outside the source
tree and fixture-mocked home paths, with enough space for the gate.

An initial smoke stopped before launch because this CLI rejects the local
workflow's suggested run-once `--authorize network host`. The test instead
records host networking through supported initialization of its disposable
project. The generic command/documentation mismatch was mailed to maintenance
as `2026-10-04-component-catalog-network-run-once-mismatch.md`; no generic
launcher change is hidden in this component slice.

The website gitlink stays at main's pointer. No release is cut or published.
Branch delivery uses SSH Git; the owner opens and merges the PR through the
GitHub UI under the repository's integration policy.
