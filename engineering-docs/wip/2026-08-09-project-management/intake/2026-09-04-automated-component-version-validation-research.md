# Intake: Research/Design — Automated Validation Of New Component Versions

Delivered 2026-09-04 by `component-catalog`, at the product owner's
direction: "we need a brief research/design to discover whether we can
validate new component versions with automated tests for each
component. But presumably this should be part of the updating story. It
seems to me this is becoming important for V1, as running with obsolete
or even potentially CVE-marred versions is not a great user
experience."

## What Is Being Handed Over

A brief research/design task: for each curated component (today —
pycharm, codium, codex, claude-code, antigravity-cli,
postgresql-client), discover whether an automated test can stand as the
verification evidence (or a substantial part of it) behind a matrix
edge when a new version appears, instead of every advance waiting on an
owner-bound manual smoke.

Questions the research should answer, per component:

1. What can be validated headlessly and deterministically —
   download/checksum against the vendor's manifest, archive shape,
   binary execution (`--version`), launch into a formation, a scripted
   interaction? The 2026-09-03/04 pin advances already automate the
   first three by hand; the open question is how far past "the binary
   runs" automation can carry the evidence.
2. What residue genuinely requires a human smoke (GUI rendering,
   login/credential flows, vendor-backend behavior), so the owner's
   time is spent only there?
3. Where does the automated evidence live — CI, a `nox` session, a
   dedicated verb — and how does it connect to the matrix's evidence
   strings and the provisional-edge convention?

## This Belongs Inside The Updating Story

The owner presumes, and `component-catalog` agrees, that this is a
strand of the upgrade-experience intake already in this queue
(2026-09-03, *The Upgrade Experience Is A V1 Feature*): its third
strand — "the project of upgrading: who verifies, what evidence gates
the advance" — is exactly where automated validation slots in. This
item sharpens that strand rather than opening a parallel one; disposing
of the two together is the natural move.

## Why It Is Becoming Important For V1 (Owner's Framing)

Running with obsolete — or potentially CVE-marred — component versions
is not a great user experience. Timely pin advances are therefore a
security posture, not a convenience, and today their pace is bounded by
owner availability:

- In the two days 2026-09-03/04, all three agent CLIs drifted:
  claude-code 2.1.236 (vendor stable) vs 2.1.260 (latest), codex
  0.153.0 → 0.153.2 within a day of its own update notice, antigravity
  1.1.24 → 1.1.26 on a latest-only channel. Each advance is a manual
  re-curation ladder (resolve, download, checksum, pin, provisional
  edges), and each new version's edges then wait on a manual smoke.
- The verification matrix (D-0007) deliberately refuses unverified
  combinations; the slower verification is, the more often users meet
  refusals or run `--unverified` — the escape hatch becoming routine
  would defeat the matrix's point.
- Antigravity's official channel serves latest-only: users who follow
  the vendor are *always* ahead of a slow pin.

## What Accepting Would Mean

Scoping and sequencing the brief research/design inside the
upgrade-experience feature: a per-component inventory of what
automation can attest, a proposed evidence model connecting automated
runs to matrix edges, and the boundary where owner smokes remain. The
existing per-component ladders (checksum-against-vendor-manifest,
archive-member verification, hands-on binary execution) recorded in the
`component-catalog` handoff are the raw material. Sequencing against
the rest of V1 is the receiving workstream's judgment, per protocol.
