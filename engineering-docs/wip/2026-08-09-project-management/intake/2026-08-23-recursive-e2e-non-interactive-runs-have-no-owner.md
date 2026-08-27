# Intake: Non-Interactive DevCapsule Runs Have No Owner

Delivered: 2026-08-23

From: `recursive-e2e`

## What Is Being Handed Over

Running DevCapsule with no human present — scripted, automated, or agent-driven
— has no owning workstream, no requirement, and no documented behavior. This
covers every run, not only the first one on a project.

On 2026-08-23 the product owner ruled that this blocks the V1 release. It is
delivered here for ownership and sequencing, not for a verdict on whether it is
wanted.

## Why It Belongs Here

`recursive-e2e` surfaced it while settling the first-run user experience, and
explicitly scoped it out of that narrative: the first-run story is being written
around a human at a terminal, and non-interactive operation is a different
story that constrains the same code. It is not within `recursive-e2e`'s
registered goal, and it is not obviously within `sample-projects`,
`workflow-improvements`, or `contained-display` either. Deciding whether it
joins an existing workstream, opens a new one, or attaches to the V1 scope
ledger is a routing and lifecycle decision.

## Evidence

- `engineering-docs/design-notes/devcapsule/v1-user-experience.md`, section
  *The First Run: Cases And Properties*, subsection *Non-Interactive Runs Are
  Handled Elsewhere*, records the scope-out and points here.
- The same document specifies `project config resolve` as *"safe to run as a
  preflight and useful in review, troubleshooting, and noninteractive
  automation"* — the only existing statement about non-interactive use, and it
  covers one command.
- Section *What Happens On The First Run* requires an explanation and
  acknowledgement of vendor acquisition before a JetBrains archive is
  downloaded. `config authorize` is likewise specified as a deliberate human
  act that must display the risk of control over the host daemon. Neither has a
  defined non-interactive form: an unattended run cannot satisfy them, and no
  document says whether it should fail, use a pre-recorded authorization, or
  proceed.
- No requirement under `engineering-docs/requirements/` states an outcome for
  unattended operation.

## What Accepting It Would Mean

Deciding, at minimum:

- whether V1 supports unattended runs or explicitly refuses them with a clear
  message, since those are different implementations and the difference is
  user-visible;
- how a pre-recorded authorization or acknowledgement is expressed, if the
  answer is support rather than refusal, without weakening the host-boundary
  guarantees in `R-PRODUCT-002` and `R-SCOPE-001`;
- whether this becomes a requirement record, a V1 scope ledger row, or both;
- which workstream carries the implementation, and by which release.

The sender assigns no priority, sequence, or release target. The product
owner's release-blocking statement is reported as evidence, not as a schedule.
