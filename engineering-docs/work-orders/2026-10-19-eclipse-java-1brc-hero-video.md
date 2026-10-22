# Work order: capture the Eclipse/Java “WOW factor” 1BRC hero demonstration video

Prepared 2026-10-19 as the follow-up to
[`2026-10-18-landing-page-why-devcapsule.md`](2026-10-18-landing-page-why-devcapsule.md)
(Deliverable 2 stretch goal). Intended repository home:
`engineering-docs/work-orders/2026-10-19-eclipse-java-1brc-hero-video.md`.

Human language governs this document. The executor may adapt the exact benchmark
input size, window choreography, and editing cuts using reasonable judgment,
while preserving factual accuracy, provenance disclosure, and the acceptance
checks below.

## Preamble: what is already built and ready to reuse

The baseline landing-page slice (`ws-maintenance/e2e_videos` and
`ccozianu/devcapsule-website` branch `landing-page-why-devcapsule`) completed
all contract, template, styling, accessibility, and media-processing
infrastructure needed to ship a hero demonstration video. **Do not rebuild or
rediscover any of the following from scratch:**

1. **Website Contract v1 and Hero Video Player (`website/` and `README.md`)**
   - `website/CONTRACT.md`,
     [`content-website-contract.md`](../specifications/product/content-website-contract.md),
     `website/scripts/content.mjs`, and `website/scripts/check.mjs` already
     support the `<!-- website:demo -->` section in `README.md`, self-hosted
     `.webm`/`.mp4` video assets copied into `/content-assets/<key>/...`, poster
     images, `<track kind="captions">` verification, and unit tests in
     `website/test/contract.test.mjs`.
   - `website/src/_includes/home.njk`, `website/src/assets/site.css`,
     `website/src/assets/site.js`, and `website/src/assets/session-demo.vtt`
     already implement the right-hand hero `<video>` player (`1152×720`,
     `16:10`, `preload="none"`, `playsinline`, `controls`, tilt removed), the
     `Expand ⤢` modal `<dialog>`, the `<details>` step transcript, and WebVTT
     captions passing WCAG 2.1 A/AA (`axe-core` `video-caption`).
   - Swapping in the new Eclipse/Java recording once captured requires only
     updating the asset links, caption prose, and step list under
     `<!-- website:demo -->` in `README.md` and the cue text in
     `website/src/assets/session-demo.vtt`.

2. **Proven In-Capsule Video Framing, Cropping, and Time-Compression Pipeline**
   - `ffmpeg` is not installed inside the DevCapsule container, and headless
     Chromium blocks `file://` `<video>` sources when loaded from `about:blank`
     (`page.setContent`).
   - To crop, frame, or time-compress a raw `1600×1000` noVNC recording into a
     crisp `1152×720` (`16:10`) hero excerpt inside the capsule:
     1. Serve the source `.webm` over a local Node `http.createServer` bound to
        `127.0.0.1:0` that implements HTTP `Range` (`206 Partial Content`)
        responses.
     2. Launch headless Chromium via `website/node_modules/playwright` with
        `browser.newContext({ viewport: { width: 1152, height: 720 }, recordVideo: { dir, size: { width: 1152, height: 720 } } })`.
     3. Render a `<video>` element framed to the active IDE region, play at the
        chosen `playbackRate` (or seek past idle waits), call
        `await context.close()` to flush the WebM, and call `process.exit(0)`
        after `await browser.close()` so the HTTP server does not keep Node
        alive.
     4. Extract and crop the matching `1152×720` PNG poster frame using Python
        `PIL` (`Pillow` in `devcapsule-src/.venv/bin/python`).

3. **Verified Eclipse Image Inventory (`devcapsule-local-eclipse:59ccaf413ce00f743fbc`)**
   - Inspection of the cached `devcapsule-local-eclipse:59ccaf413ce00f743fbc`
     image (`4.17 GB`) confirmed that the following tools are already installed
     offline:
     - **IDE:** Eclipse IDE for Java Developers `2026-09 R` at `/opt/eclipse`
       (with Ubuntu 24.04 `WebKitGTK 2.52.6` installed offline so internal
       browser views render cleanly).
     - **JDK & Flight Recorder:** OpenJDK `25.0.4+7` at
       `/opt/java/jdk-25.0.4+7` (`java`, `javac`, and `/opt/java/current/bin/jfr`).
     - **Build & Test Tools:** Apache Maven `3.9.16`
       (`/opt/maven/apache-maven-3.9.16`), Gradle Tooling API `8.9.0`, and
       JUnit Jupiter `5.14.4` / `6.1.3` (`junit-jupiter-api`,
       `junit-jupiter-engine`).
     - **Code Coverage UI:** EclEmma `3.1.12`
       (`org.eclipse.eclemma.core_3.1.12.202609021052.jar`,
       `org.eclipse.eclemma.ui_3.1.12.202609021052.jar`) and JaCoCo `0.8.15`
       (`org.jacoco.agent`, `org.jacoco.core`, `org.jacoco.report`) are bundled
       in `/opt/eclipse/plugins/` (*Coverage As → JUnit Test* highlights covered
       lines in green/yellow/red directly in the Eclipse editor).
     - **Browser Automation:** `/opt/playwright` with Chromium `153.0.8010.12`.

## Unblocking the two prerequisites before capture

The bounded inspection on 2026-10-19 stopped before launching a multi-step
capture because of two concrete environment gaps. Resolve both at pickup using
one of the options below:

### 1. Coding agent execution and authentication inside the Eclipse workspace

**Why it blocked the initial stretch pass:** In the primary DevCapsule
environments, all three coding agents (`codex` / `gpt-6-astra`, `claude` /
`claude-fable-5-1`, and `antigravity` / `gemini-4-argon`) use interactive SSO
sign-in rather than API keys. The existing `ide-smoke` harness
([`e2e-tests.md`](../development/e2e-tests.md)) creates a disposable child
project with `eclipse-ide` + `browser-automation` only (so no agent CLI binary
is materialized in `/opt` of the cached Eclipse image) and does not copy parent
SSO credentials into child IDE capsules.

**Unblocking options (select one with the product owner):**

- **Option A — Scoped API key for the bounded recording run:** Materialize the
  Eclipse capsule with an agent capability (`codex`, `claude-code`, or
  `antigravity`) and supply a temporary, narrowly scoped API key
  (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`) for the duration
  of the recording session. Ensure the key is never echoed in a terminal frame
  or committed to any file.
- **Option B — SSO agent driving the shared host-backed workspace directory:**
  Because a child capsule's `/workspace` is bind-mounted from a host-backed
  directory under the parent capsule's persistent home
  (`~/.devcapsule/e2e-workspaces/...`), an already SSO-authenticated agent in
  the parent capsule (or via `docker exec` with the parent's SSO state mounted
  read-only) can implement and optimize the Java project inside that exact
  workspace directory while the Eclipse capsule compiles, tests, covers, debugs,
  and profiles the same files live. If this hybrid arrangement is used, state
  it transparently in the provenance note, or mount the SSO credential slot into
  the child capsule so the agent CLI runs directly inside the Eclipse terminal.
- **Option C — Persistent SSO sign-in on a reusable demo project:** Initialize a
  dedicated demo workspace with `eclipse-ide` and the chosen agent capability,
  complete the one-time SSO sign-in in its persistent state slot, and run the
  automated Playwright/noVNC capture against that workspace.

### 2. Hotspot profiling visualization in Step 5

**Why it blocked the initial stretch pass:** While EclEmma code coverage
(`org.eclipse.eclemma.ui`) and OpenJDK's CLI Flight Recorder
(`/opt/java/current/bin/jfr`) are pre-installed in `devcapsule-local-eclipse`,
standalone GUI profiler plugins (`JDK Mission Control` / `org.openjdk.jmc.*` or
`VisualVM`) are not bundled in Eclipse IDE for Java Developers `2026-09 R`, and
image builds run with `--network none`.

**Unblocking options:**

- **Option A — JFR Flight Recording + interactive HTML Flamegraph in Eclipse's
  internal WebKitGTK browser (no image rebuild required):** Record the benchmark
  run with `-XX:StartFlightRecording=filename=1brc.jfr,settings=profile,dumponexit=true`,
  extract `jdk.ExecutionSample` stacks with `/opt/java/current/bin/jfr print --json --events jdk.ExecutionSample 1brc.jfr`,
  render a self-contained SVG/HTML flamegraph + hotspot table via a small script,
  and open it inside an Eclipse editor tab (which renders HTML/SVG natively via
  the pinned `WebKitGTK 2.52.6` runtime).
- **Option B — JFR CLI Hotspot Summary inside Eclipse's Terminal / Editor view:**
  Run `/opt/java/current/bin/jfr summary 1brc.jfr` and display the top hotspot
  methods in the Eclipse Terminal/Console view alongside the source editor before
  asking the agent for the focused optimization.

## Target scenario: Eclipse / Java One Billion Row Challenge-style aggregation

Capture a real DevCapsule session through the Playwright/noVNC approach where
outer automation operates the desktop through mouse and keyboard and a coding
agent implements and optimizes a One Billion Row Challenge-style temperature
aggregation project in Java:

1. **Create or import the Java project in Eclipse** through the real Eclipse
   workflow (Maven or standard Java/JUnit 5 project in `/workspace`).
2. **Autonomous agent implementation:** Ask the coding agent to implement the
   baseline weather-station aggregation (`min`/`mean`/`max` per station) and
   meaningful JUnit 5 tests, showing the agent working without per-step
   approval prompts.
3. **Run tests with EclEmma code coverage:** Run the JUnit suite under
   *Coverage As → JUnit Test* in Eclipse, showing green/yellow/red highlighted
   source lines and the Coverage view summary.
4. **Debug in the same environment:** Set a breakpoint in the aggregation loop
   or parser, run under the Eclipse debugger (*Debug As → JUnit Test*), inspect
   live variables in the Variables view, and step through the code.
5. **Profile hotspots and optimize:** Profile the aggregation on a larger sample
   input (e.g., 1–5 million rows so the run takes a few seconds), inspect the
   hotspot (such as `String.split` / `Double.parseDouble` allocation overhead),
   ask the agent for one focused optimization (such as custom integer/fixed-point
   scanning over a `MappedByteBuffer` or `byte[]`), and re-measure the speedup.
6. **Optional persistence check:** Stop and reopen the capsule (`devcapsule stop`
   / `devcapsule start`) to show the Eclipse workspace, open editors, and
   coverage/test history preserved.

## Deliverables and acceptance criteria

1. **Retained full recording and provenance note:**
   - Save the unedited (or minimally trimmed) full WebM recording and key PNG
     frames under `engineering-docs/implementation-notes/devcapsule/assets/`
     (or `engineering-docs/blog/assets/`) and document the exact executable
     version/commit, image tag, agent/model identity, and any time-compression
     cuts in an accompanying validation note indexed in `index.md`.
   - Verify that no API keys, OAuth tokens, personal email addresses, or private
     host paths appear in any frame.
2. **Hero excerpt and poster wired into the landing page:**
   - Produce a `1152×720` (`16:10`), ~20–35 second hero excerpt WebM and crisp
     PNG poster frame where IDE source text, coverage highlights, debugger
     variables, and benchmark numbers are legible inline on a `1366×768` laptop
     viewport.
   - Update `<!-- website:demo -->` in `README.md` and captions in
     `website/src/assets/session-demo.vtt`, keeping the full recording and
     validation note linked from the caption and expandable `<dialog>` modal.
3. **Validation gates:**
   - `npm test`, `CONTENT_DIR=.. npm run check:content`,
     `CONTENT_DIR=.. npm run build`, `CONTENT_DIR=.. npm run check`, and
     `scripts/browser-check.mjs` in `website/`.
   - `.venv/bin/python -m nox -s docs-contract` and
     `.venv/bin/pytest tests/ -k "doc"` in `devcapsule-src/`.
