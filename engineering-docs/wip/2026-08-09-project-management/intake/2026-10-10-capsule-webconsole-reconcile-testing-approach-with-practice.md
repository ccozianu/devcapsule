# Reconcile the project's approach to testing with current practice

Date: 2026-10-10
From: capsule-webconsole, at the product owner's request
To: project-management
Status: a decision to take and record; no implementation proposed here

## What is handed over

A reconciliation of this project's testing approach, the tiers, what gates
a pull request and a merge to `main`, the time and scratch budget of the
gate, and the hermeticity rule for tests, against the practice the owner
summarized on 2026-10-10:
<https://share.gemini.google/z6OXUKUkkvgL> ("Integration Tests in CI/CD
Gates"). The owner asked for this item after a day in which the gate's
scratch filled a capsule's 2 GB `/tmp` and the question "should the
integration tests be in `nox -s build`?" had an answer in the documents
but no recorded reasoning.

## The summary's substance, briefly

The summary distinguishes narrow integration tests, which cross a real
local boundary such as a subprocess or a local container, from broad or
end-to-end tests, which cross live networks or external services, and
argues both sides of gating:

- For gating: an always-deployable trunk (Humble and Farley, *Continuous
  Delivery*, 2010, chapter 5, the commit stage); the author fixes an
  integration failure while the context is fresh (Winters et al.,
  *Software Engineering at Google*, 2020, pre-submit testing); a lower
  change-failure rate (Forsgren, Humble and Kim, *Accelerate*, 2018).
- Against gating everything: commit-stage feedback should take 5 to 10
  minutes, and slower suites belong in a later pipeline stage (Fowler,
  *Continuous Integration*); non-deterministic tests in a gate destroy
  trust in it (Fowler, *Eradicating Non-Determinism in Tests*, 2011); keep
  broad tests few and off the blocking path (Vocke, *The Practical Test
  Pyramid*, 2018); pipeline bottlenecks lengthen lead time (DORA reports).
- The consensus architecture it recommends: fast narrow integration tests
  gate the pull request within 5 to 10 minutes; impacted-only integration
  tests may gate selectively; broad and end-to-end tests run after the
  merge or on a schedule, with a failure rolled back or fixed at once.

## Where the project stands today, from its own documents

- `WORKFLOW-LOCAL.md`, Validation Commands, "Gate": `nox -s build` runs the
  distribution version, syntax, the type check, the unit tests, the CLI
  smoke, the built executable and its smoke, the packaging tests, the
  documentation contract, then the web console session; "the end-to-end
  suites are not in it."
- `DEVELOPING.md`, Testing: the integration suite is "`nox -s integration`,
  inside `build`"; the hosted runner runs the unit suite only, with no
  Docker, by the owner's standing rule.
- `engineering-docs/development/integration-tests.md`: an integration test
  "crosses a packaging or process boundary and still runs without Docker",
  and "the gate runs all of them". The line is drawn at Docker, not at
  time or at breadth.
- No decision record states why. The build session has included the
  packaging tests since 03c2050 (2026-08-07); R-python-mvp-001 only notes
  that `nox -s build` became the gate on 2026-07-08.
- Measured on 2026-10-10 inside a capsule, after PR #205: a plain
  `nox -s build` takes 2 minutes and leaves 175 MB under `/tmp/pytest-of-<user>`,
  36 MB from the unit suite, 134 MB from three clean-revision executable
  builds in the integration session, 7 MB from the console session. Before
  #205 the unit suite alone wrote 3.7 GB per run, because test fixtures
  read the developer's real artifact cache; the fix is a hermeticity rule
  enforced by one autouse fixture, with no written policy behind it yet.

## Why it belongs to project-management

The gate's composition, its time budget and the rule that tests are
hermetic are project-wide choices that bind every workstream and the
release process. They are not this workstream's to decide, and the
documents that would carry the decision, `WORKFLOW-LOCAL.md`,
`DEVELOPING.md` and the development notes, are project-management's or
the owner's to change. The sender assigns no priority, sequence or
release target.

## Evidence and documents

- The owner's report of 2026-10-10 and the diagnosis in the
  capsule-webconsole status file, "PR11", with the measurements and the
  dates of the code involved.
- PR #205 and its review #206: the fixture, the regression test, the
  measurements before and after.
- `WORKFLOW-LOCAL.md` (Validation Commands), `DEVELOPING.md` (Testing),
  `engineering-docs/development/unit-tests.md`,
  `integration-tests.md` and `e2e-tests.md`.
- `devcapsule-src/noxfile.py`, the `build` session and `run_packaging_tests`.

## What accepting would mean

Taking the decision and recording it where the gate is defined:

1. Name the tiers the project has, unit, integration without Docker,
   end-to-end with Docker, and for each say what gates a pull request,
   what gates a merge to `main`, and what runs after a merge or on a
   schedule, with the reasoning, as a decision record or a dated section
   of the development notes.
2. Set the gate's budget: a time the gate must stay under, and a scratch
   footprint it must stay under, so that a plain run fits a capsule's
   `/tmp`; say where the budget is measured and how often.
3. State the hermeticity rule in words: tests neither read nor write the
   developer's real homes and caches, except the build tools'
   content-addressed caches, which stay shared; the fixture in
   `tests/conftest.py` then implements a rule rather than standing in for
   one.
4. Decide whether the three clean-revision executable builds of the
   integration session, 134 MB and most of its time, stay in every gate,
   run once per gate instead of three times, or move to the release
   acceptance where `DEVCAPSULE_PEX_UNDER_TEST` already points them at a
   candidate.
5. Update `WORKFLOW-LOCAL.md` and `DEVELOPING.md` to match, and remove the
   sentence that the gate's scratch overflows `/tmp` once it no longer does.


## Appendix: the summary as retrieved from the share, verbatim

Retrieved on 2026-10-10 by rendering <https://share.gemini.google/z6OXUKUkkvgL> in a headless browser and copying the page's text. The page's title is "Integration Tests in CI/CD Gates", created with 3.8 Flash on October 10, 2026. Only the site's navigation and cookie banner are left out; the table came through as tab-separated lines.

```text
Can you research whether or not integration tests (as opposed to unit tests) should be part of the d…

Can you research whether or not integration tests (as opposed to unit tests) should be part of the default build and gates triggered by PR or merge to main in software projects ? Give me some arguments and references pro and cons

Scientific consensus (based on peer-reviewed DevOps research and industry-standard continuous delivery engineering literature; specific trade-offs vary depending on deployment architecture, test execution times, and infrastructure reliability).

Whether integration tests should gate a pull request (PR) or merge to the main branch depends on how the test suite is scoped, its execution latency, and its environmental determinism.

Modern continuous delivery practices distinguish between narrow integration tests (which test integration points against real local boundaries like an in-memory DB or a localized container) and broad/end-to-end integration tests (which interact across live distributed networks or external services).

Key Arguments and Trade-offs
Dimension	Pro-Gating (Include in PR / Merge Gate)	Anti-Gating (Decouple or Run Post-Merge)
Defect Detection	Catches boundary mismatches, contract breaks, and serialization bugs before polluting main.	Unit tests and type checkers catch most logical defects; synthetic contract testing (e.g., Pact) catches boundaries faster.
Cycle Time & Feedback	Guarantees that code passing CI is safe to deploy immediately (true Continuous Deployment).	Long-running suites (>10 minutes) block PR iterations, reduce developer focus, and increase context switching.
Reliability / Flakiness	Enforces accountability: authors must fix integration failures while context is fresh.	Flaky network calls or slow databases produce false positives, leading to pipeline retries and test fatigue.
Resource Cost	Prevents broken rollbacks and hotfixes downstream.	Ephemeral environments and parallelized containers for every PR push drive up compute and runner costs.
Arguments and References: Pro-Gating

Guaranteed "Always Deployable" Mainline

Argument: Continuous Delivery requires that every commit landing on the trunk represents a viable release candidate. Relying solely on unit tests permits integration mismatches (e.g., schema drift, query syntax bugs, HTTP status discrepancies) to land on main, shifting the burden of debugging to later stages or to other developers.

Reference: Jez Humble & David Farley, Continuous Delivery (2010). Chapter 5 details the commit stage, emphasizing that the gate must build artifacts and run fast integration checks that provide high confidence before merging.

Immediate Developer Accountability

Argument: When an integration failure blocks a PR, the author has full working context and can fix the issue in minutes. If integration runs asynchronously post-merge or nightly, discovering the root cause among multiple merged PRs takes significantly more time.

Reference: Google Engineering, Software Engineering at Google (Titus Winters et al., 2020), specifically the "Testing Overview" and "Continuous Integration" chapters, which document how pre-submit testing gates maintain trunk health at scale.

Reduction in Change Failure Rate (CFR)

Argument: Preventing integrated defects from reaching main directly lowers production incident rates and rollback frequencies.

Reference: Nicole Forsgren, Jez Humble, & Gene Kim, Accelerate: The Science of Lean Software and DevOps (2018). DORA research identifies automated testing and comprehensive CI as key technical capabilities driving both high throughput and low change failure rates.

Arguments and References: Anti-Gating (or Tiered Execution)

The Fast Feedback Loop Threshold

Argument: CI gates must provide fast feedback (ideally under 5 to 10 minutes). Broad integration suites spinning up external services or seeded databases often exceed this budget. Slow PR gates lead to infrequent commits, batching of large PRs, and merge queues that stall throughput.   
Martin Fowler

Reference: Martin Fowler, Continuous Integration (martinfowler.com, 2006/2024 updates). Fowler establishes that commit-stage feedback must be fast. If a test suite takes longer, it should be isolated into a secondary deployment pipeline stage rather than holding up the initial commit feedback.   
Martin Fowler

Flakiness and False Failures

Argument: As integration tests grow, non-deterministic behaviors (timeouts, race conditions, external resource contention) increase mathematically. When flaky tests gate PRs, developers lose trust in the pipeline, often re-running builds without modifying code to get a "green" pass.

Reference: Martin Fowler, Eradicating Non-Determinism in Tests (2011). Fowler points out that non-deterministic tests in a gating pipeline ruin the value of the suite and cause teams to ignore CI signals.

Reference: Ham Vocke, The Practical Test Pyramid (Martin Fowler's bliki, 2018). Advocates keeping broad integration tests minimal and off the critical PR blocking path if they introduce external fragility.

Impact on Lead Time for Changes (LTTC)

Argument: Running exhaustive integration suites against every commit pushed to a PR branch lengthens the overall PR lifecycle. Teams spend disproportionate engineering hours waiting for builds to complete before approval.

Reference: DORA (DevOps Research and Assessment) State of DevOps Reports. The research shows that while automated testing is necessary, pipeline bottlenecks directly impair Lead Time for Changes.   
Gitmore

Recommended Industry Consensus Architecture

Most high-performing teams avoid an absolute "all or nothing" approach by splitting the suite into tiered boundaries:

Fast, Narrow Integration Tests (Gated on PR): Tests using localized boundaries (e.g., Testcontainers for a single PostgreSQL instance, wiremocked HTTP boundaries, contract verification) that run under 5–10 minutes are retained as default PR blocking gates.

Selective / Impacted Integration (Gated on PR): Using Test Impact Analysis (TIA) or path-based CI triggers to run integration tests only against the specific microservice or module altered by the PR diff.

Broad / End-to-End Integration Tests (Post-Merge / Scheduled): Tests involving multi-service orchestrations, real cloud infrastructure, or large data migrations run immediately post-merge on main before production promotion, or in parallel secondary pipeline stages. If this stage fails, the commit is automatically rolled back or flagged for an immediate fix.
```
