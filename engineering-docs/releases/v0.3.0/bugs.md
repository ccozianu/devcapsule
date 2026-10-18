# 0.3.0 — Bug Table

[Release overview](README.md)

Initial review: 2026-10-18 at the cut, `3c91183`; the console-link row added after the owner's rc0 launch the same day. The linked records own
status, severity, target, ownership and technical evidence; this table
mirrors those fields for review and records the release's disposition and
next action. Update the record and its row together; reconcile before each
candidate and record the reconciliation revision here.

## Records targeted at 0.3.0

| Record | Status | Severity | Owner | Disposition | Next action |
|---|---|---|---|---|---|
| [Runtime configuration inspection fails in the recursive session](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md) | fixed | major | maintenance | fixed on `main` before the cut | verify against a downloaded candidate; close |
| [Detached containers exit and are never cleaned up](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md) | fixed | minor | maintenance | fixed on `main` before the cut | verify against a downloaded candidate; close |
| [`project <unknown>` refused as launcher-only inside a capsule](../../bugs/devcapsule/2026-09-26-project-group-guard-hides-unknown-subcommand-in-capsule.md) | fixed | minor | maintenance | fixed on `main` before the cut | verify against a downloaded candidate; close |
| [The recursive successor cannot refresh its capsule-local resolution](../../bugs/devcapsule/2026-10-04-recursive-successor-cannot-refresh-its-capsule-local-resolution.md) | fixed | minor | maintenance | fixed on `main` before the cut; the fresh-workspace test proves it | verify against a downloaded candidate; close |
| [Unpacked archive cache can lose concurrent work](../../bugs/devcapsule/2026-10-08-unpacked-cache-publication-and-recovery.md) | fixed | minor | maintenance | fixed on `main` through PR #172 | verify against a downloaded candidate; close |
| [`project run --authorize network host` refused without a recommendation](../../bugs/devcapsule/2026-10-05-run-once-network-authorization-needs-a-recommendation.md) | confirmed | minor | maintenance | the universal `network` node, a cycle slice | implement on the release branch; close on a candidate |
| [The launcher prints a web console link on a base without the console](../../bugs/devcapsule/2026-10-18-console-link-printed-on-a-base-without-the-console.md) | confirmed | minor | maintenance | found by the owner on rc0; a release fix in this cycle, beside C10 | fix on the release branch; verify on a candidate against the recipe-9 and a recipe-11 base |
| [Installed IDE cannot be reused before archive acquisition](../../bugs/devcapsule/2026-09-24-installed-ide-docker-reuse.md) | confirmed | minor | maintenance | split: cleanup of obsolete images and caches is a cycle slice after the owner's design review; reuse with an empty launcher cache is out of 0.3.0 | design review with the owner; retarget the reuse half at the next planning |

## Records of other workstreams the decision names

Two fixed records still say 0.2.16 on `main` and are their owners' to
retarget to 0.3.0: [agents cannot discover how to build and test](../../bugs/devcapsule/2026-10-03-agents-cannot-discover-how-to-build-and-test.md)
(`workflow-improvements`) and [an unreleased Playwright breaks the checkout launch](../../bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md)
(`component-catalog`). They are verified against a downloaded candidate
once retargeted.

## Moved out with the cut

| Record | Status | Severity | Owner | Disposition |
|---|---|---|---|---|
| [Fresh clones require manual ecosystem bootstrap](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md) | confirmed | minor | maintenance | retargeted to 0.9 on 2026-10-18 by the owner's decision of 2026-10-11; project-type templating is the dependency |

## To be filed

The two C10 records, the first-session terminal summary and Ctrl+C ending
with a result, are filed first by the C10 slice and take their rows here.
