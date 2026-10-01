# User Documentation Improvements For 0.2.16 And Soon After

Date: 2026-09-28. Owner: `user-docs`. Status: **proposed; deciding on this
list blocks 0.2.16** by the owner's direction of 2026-09-28, delivered to
`project-management` by mail the same day. The owner returns with more
detail; nothing here is accepted until the owner decides each item.

Written at the owner's request while the owner worked in the website
repository, after the 0.2.15 documentation tree landed on `main` in
PR #151. Ordered by value for adopters against cost.

1. **The documentation of the running version travels inside the capsule.**
   Ship `docs/` in the executable, expose it at a fixed path in the capsule
   and through `devcapsule docs`, and point the seeded agent instructions at
   it. An agent then reads how DevCapsule works from the version it is
   running in, never a stale site. Product work for maintenance or a
   feature workstream; the content side is free once the tree exists.
2. **The command reference generated from the executable.** A gate session
   renders every `--help` tree into `docs/reference/cli.md` at release; the
   gate fails when the file is stale. Right by construction, and it removes
   the largest planned stub.
3. **Known issues generated from the bug records.** A page built at release
   from the frontmatter under `engineering-docs/bugs/`: open bugs by area,
   severity and target, each linking to its record. "Every edge has a file"
   becomes a page adopters can check before reporting.
4. **The AI-first first session on a real sample, UD-001.** A second
   getting-started path: clone the FastAPI sample, add one agent, ask it for
   one useful change, run the tests, commit. The pairing and the sample are
   the owner's call; this is the release-worthy WOW step.
5. **A glossary.** Capsule, checkout, manifest, lock, base, component,
   authorization, binding, slot, formation: one page, one definition each,
   linked from every first use. Cheap; removes most "what does this word
   mean" moments.
6. **Recipes.** Task-shaped pages beside the areas: run a database beside
   the app, use an API key with Codex, share IDE settings across checkouts,
   work on two checkouts of one project, reach a dev server from the
   browser. Each verified in a real session before it is published.
7. **Screenshots and one short recording.** The browser desktop, the panel,
   the clipboard box and the IDE terminal are unfamiliar in words; four
   images and a sixty-second first session would carry the guide. Needs the
   contract's image handling, which exists.
8. **Executed documentation.** Tag the shell blocks of the getting-started
   guides with their expected outcome and run them against the downloaded
   candidate during acceptance, so a guide that stops working fails the
   release. The runbook already requires the guide to be true; this makes
   the check mechanical.
9. **A welcome page in the capsule.** On first launch the IDE opens a short
   page: what is in this capsule, which agents, where the docs are, how to
   stop. Product work; content here.
10. **A feedback link on every page**, prefilled with the page and version,
    into the issue tracker, plus a docs-bug template. Website side, small.
11. **Windows as a first-class path**, UD-004, once the owner's WSL2 findings
    are in hand.

Fits 0.2.16 with the current cadence: 2, 3, 5, and the content half of 1;
4 if the owner chooses the sample and pairing early. Soon after: 6, 7, 8,
9, 10. The rest as evidence arrives.


## What A Decision Looks Like

For each item: in 0.2.16, soon after, or not; and for items 1, 2, 3, 8 and
9, which workstream implements the product half, since `user-docs` owns
only the content. Item 4 needs the sample and the agent pairing named.
Once decided, `user-docs` records the accepted items as UD tasks in its
status file in the decided order.
