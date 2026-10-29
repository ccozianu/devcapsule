# Work Order: Release 0.3.0

Issued 2026-10-18 by `project-management` at the product owner's decision of
the same day, recorded in
[the scope and cut decision](../wip/2026-08-09-project-management/2026-10-18-decision-release-0-3-0-scope-and-cut.md).
Recipient: `maintenance`, the release driver. Delivered by mail; this file
is the committed copy. Status: open.

## Outcome

DevCapsule 0.3.0 is published as a final release, from a candidate accepted
as downloaded, with its documentation and release notes, under the
[release runbook](../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md).
The headline: the capsule web console, persistent session diagnostics, and
a launcher that is honest about what it skips.

## Deliverables, and what done means for each

1. **The cut and candidate 0.** `release-0.3.0` cut from `main` at the
   integrated commit the driver selects; the branch's first commit sets the
   version to `0.3.0` with `nox -s bump -- 0.3.0`; the release overview
   under `engineering-docs/releases/v0.3.0/` written with the scope of this
   order and the exclusions; `v0.3.0-rc0` tagged and published by the
   workflow. Done when the published rc0 assets are downloaded, checksum
   and version verified, and the local proofs run against them.
2. **The dogfooding slices, during the cycle**, each as a maintenance
   slice with the implementor-and-reviewer loop, landing on the release
   branch by the owner's direction and merged to `main` before the next
   candidate tag:
   - the universal `network` authorization node: run-once and saved
     `network host` work on a project without a recommendation, bridge
     stays the default; done when the bug of 2026-10-05 closes on a
     candidate;
   - C10: a ready, stopped or error summary instead of streamed desktop
     diagnostics, and Ctrl+C ending with a result, not a traceback; the two
     bug records filed first; done when both close on a candidate;
   - forced configuration: `project config resolve --force` shows the
     configuration a launch would use with errors skipped, a component the
     launcher does not know skipped, a missing surface falling back to the
     IDE of last resort, writing no lock; `project run --force-config`
     launches that way and warns on every skip; mandatory needs split from
     optional ones; done when the capabilities page documents both and a
     fresh-workspace launch proves them;
   - the diagnostics snapshot and export command, the next slice of the
     [diagnostics work order](2026-10-08-persistent-session-diagnostics.md),
     requirement 4 there; done when it runs from another terminal against a
     broken session and its export is reviewed;
   - cleanup of obsolete images and cached files, the second half of the
     installed-IDE record, design agreed with the owner first; done when a
     command reclaims what it names and the record says what remains;
   - C20, release notes and documentation automation, last; done when the
     notes block and the manifest promotion need no operator step.
3. **The gates before the final tag.** The owner's eleven user-docs
   decisions taken; the documentation describing the accepted candidate,
   with `docs/versions.yaml` promoted after the final tag; a published base
   for the candidate; the six fixed bug records verified against a
   downloaded candidate; release notes under
   `engineering-docs/releases/v0.3.0/notes.md`.
4. **Records with the cut.** The ecosystem-bootstrap bug record retargeted
   to 0.9 per the decision of 2026-10-11; the maintenance plate and the
   registry row stating that the workstream drives `release-0.3.0`.

## Acceptance evidence

The runbook's: the candidate gate on a resolved main disposition for each
tag, downloaded-artifact smoke evidence, the acceptance record under
`engineering-docs/releases/`, and for each slice the gate on its branch and
the fresh-workspace end-to-end proof the e2e rules require.

## Decisions already taken that bind this work

The scope, driver, headline and exclusions of the decision record above;
the owner's rename of the release to 0.3.0 (2026-10-05); the release
runbook and the local version scheme; the e2e fresh-workspace rule of
2026-10-05; the configuration-writer rules of `WORKFLOW-LOCAL.md`; the
implementor-and-reviewer loop as practiced on the diagnostics slices.

## Decisions left to the driver, and to the owner

The driver: the cut commit; the order of the slices within the cycle,
network node and C10 first being the recommendation; what each candidate
carries; routine release-fix propagation under the standing exception.
The owner: every candidate's acceptance; the eleven docs decisions; the
image-cleanup design review; any scope change, by the reopen rule of the
decision record.

## Stopping points where the owner is consulted

Before each candidate tag; before the image-cleanup implementation; when a
slice proves larger than the cycle tolerates; before the final tag.

## Mainline evidence read before writing this order

`main` at the merge of PR #222 on 2026-10-18: the console's second
iteration (#192 to #206), the session logs (#207, #209), the comparison and
the pre-V1 backlog (#221); the open bug records by target; the release
proposal's candidate accounting; the maintenance, component-upgrades,
capsule-webconsole and workflow-improvements status files.
