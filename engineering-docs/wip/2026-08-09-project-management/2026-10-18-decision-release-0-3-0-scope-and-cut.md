# Release 0.3.0: Scope, Driver And Cut

Date: 2026-10-18
Decision: product owner, in the project-management session, after the
inventory of what the 0.3.0 plan still had unimplemented.
Status: accepted; the cut and the work are with `maintenance`.

## Decision

1. **Cut now.** The release branch `release-0.3.0` is cut from `main` at
   the integrated commit `maintenance` selects on pickup, and `v0.3.0-rc0`
   is tagged from it. The first commit on the branch sets the version to
   `0.3.0`, which makes the owner's rename of 2026-10-05 real; `main` stays
   at `0.2.16.dev0` until the final tag, then reopens at `0.3.1.dev0`
   unless the owner names another.
2. **Driver: `maintenance`**, as the prior recommendation and as for
   0.2.14 and 0.2.15.
3. **Headline:** the capsule web console, persistent session diagnostics,
   and a launcher that is honest about what it skips.
4. **In scope, implemented during the candidate cycle as dogfooding**, each
   a maintenance slice with the implementor-and-reviewer loop, landing on
   the release branch by the owner's direction and reaching `main` by the
   merge before each candidate tag:
   - the universal `network` authorization node (bug of 2026-10-05);
   - C10, the first-session terminal summary and Ctrl+C ending with a
     result, the two bug records to be filed first;
   - forced configuration, `project config resolve --force` and
     `project run --force-config`, with mandatory needs split from optional
     ones, the owner's correction of 2026-10-04 and 2026-10-05 and
     R-CONFIG-001;
   - the diagnostics snapshot and export command, the next slice of C21;
   - cleanup of obsolete images and cached files, the second half of the
     installed-IDE record;
   - C20, release notes and documentation automation, at the end of the
     cycle, when the notes exist to automate.
   Project-operation instructions, C17, stay assigned to
   `workflow-improvements` for 0.3.0 and gate the final tag; this
   repository's own instructions exist in `WORKFLOW-LOCAL.md`.
5. **Out of 0.3.0, named in the release overview:** consent and vendor
   trust (D-0010 to D-0013, `component-upgrades`), installed-IDE reuse
   with an empty launcher cache, browser evidence for diagnostics, and the
   web console's deliverable 6, materialized views. Their next home is
   0.3.1 or the next cycle, decided at that planning.
6. **Gates before the final tag**, unchanged: the eleven user-docs
   proposal decisions, the owner's gate of 2026-09-28; the documentation
   describing the accepted candidate, C16; a published base for the
   candidate, since the console needs recipe 11; the six fixed bug records
   verified against a downloaded candidate; release notes.

## Why

The owner's sequence of 2026-10-11 put consent and forced configuration
before any candidate. Neither had started by 2026-10-18, while the console,
the diagnostics, named build contexts, the in-capsule commands and IntelliJ
had reached `main` and the 0.2.15 documentation was live. A candidate of
what exists is worth validating now, and the cycle is the better place for
the remaining launcher work: 0.2.14 took real changes during its five
candidates under the owner's direction, and the runbook lets main's work
and the release's stabilization run concurrently. Consent stays out because
it is four decisions deep with no code yet, the kind of change that
multiplies candidates.

## What this changes in the records

- The release proposal's decision 1 is settled by this record; decision 5,
  the upgrade-design slice, is settled as none in 0.3.0.
- The ecosystem-bootstrap bug record still says target 0.3.0 on `main`
  although the owner moved it to 0.9 on 2026-10-11; `maintenance` corrects
  it with the cut. Two fixed records of other workstreams still say
  0.2.16 and are their owners' to retarget to 0.3.0.
- Features landing on a release branch during a candidate cycle are the
  owner's direction, with the 0.2.14 precedent; the release overview
  records it for this release. A standing local rule is
  `workflow-improvements`' to propose if it recurs.

## Reopen if

The candidate cycle shows that a scoped item is larger than a cycle
tolerates, in which case it moves out by the owner's word and the overview
says so; or a blocking defect in the console or the diagnostics changes
the headline.
