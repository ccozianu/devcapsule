---
status: confirmed
severity: minor
target: none
owner: website
opened: 2026-09-19
requirements: []
---

# Test publication accepts settings that cannot produce a candidate

## Symptom and impact

The parent Website workflow accepts an origin or base path incompatible with
its candidate job. It can deploy that build to the test Pages destination,
finish successfully, and skip candidate publication. The operator discovers
the mismatch only when trying to promote. The default artifact-only mode and
the label `production` for test deployment make this easier to misunderstand.

This is minor: the correct manual inputs are a working workaround, and an
earlier valid candidate is already serving production. No outage or corrupted
production artifact is claimed.

## Environment and evidence

Reviewed 2026-09-19 from the website workstream, synchronized with parent main
`d71559a`. GitHub-hosted Ubuntu runs `.github/workflows/website.yml`; the public
test destination is `test-devcapsule.mycodespace.ai`. No local Docker capability
or graphical environment is needed to reproduce this workflow defect.

Implementation: `deploy.if` checks production mode and main only; `candidate.if`
also requires the exact test origin and `/` base path. There is no earlier input
validation enforcing those extra requirements before deployment.

Live read-only observation: the test homepage and docs overview have production
canonical URLs (`https://devcapsule.mycodespace.ai/...`). Its build-info reports
`builtAt: 2026-09-18T00:57:09.533Z`, content
`5a4b35435ee3e1cb460b48d292f15e5efe5228be` and presentation
`0691956e3aa383b74c9fb87f4d46140136b8a0b6`. The exact inputs of that run were
not retrieved; the live metadata is consistent with the accepted wrong-origin
configuration. The code establishes the skipped-job path independently.

An earlier run, `35286178930`, built successfully on main but skipped Pages
upload, deploy and candidate. Its conditions indicate non-production mode;
the dispatch inputs were not directly retrieved. This is supporting evidence
of operator confusion, not proof of wrong-origin input in that earlier run.

## Reproduction (do not run against the live site merely to demonstrate it)

1. Inspect/run the workflow in an authorized test environment on main.
2. Select mode `production`, origin `https://devcapsule.mycodespace.ai`, base `/`.
3. The build and test Pages deployment are eligible; candidate is ineligible.

Expected: invalid deploy-test combinations fail before modifying the live test
site, with a clear explanation, or the action fixes the destination parameters
so such combinations cannot be selected.

Actual: the deployment and candidate conditions disagree; workflow-level success
does not imply that a promotable candidate was produced.

## Workaround and close criteria

Use main, mode `production`, origin `https://test-devcapsule.mycodespace.ai`,
and base path `/`; start a new dispatch to change inputs. A build-only run
intentionally creates no deployment or candidate.

Fix under W01 in the [website task list](../../wip/2026-09-16-website/CURRENT-STATUS.md#follow-up-tasks-2026-09-19).
Close after invalid inputs are rejected before deployment, intentional build-only
runs are clearly identified, and a normal default test deployment produces a
candidate. Validate wrong host/path/branch cases without republishing production.
Reopen if a new mode or destination restores inconsistent eligibility rules.
