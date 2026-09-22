# Intake: Replace Mandatory Release Merges With Evidenced Fix Propagation

Delivered: 2026-09-22

From: `project-management`, on the product owner's explicit direction.

## Owner Decision

During release stabilization, fix release-blocking bugs and ensure that main
also has the correction, or establish that main does not have the bug. Main
must remain available to other workstreams. Prefer merging when it produces a
correct result; otherwise cherry-pick, adapt the fix's reasoning to main's
implementation, or provide evidence that main is unaffected. Agents should
choose the appropriate method using engineering judgment without asking for
fresh authorization for each choice.

A textual conflict alone does not rule out merging; clean Git ancestry or
patch equivalence alone does not prove the correction works. Record the
release revision, inspected main revision, disposition and proportionate
reasoning/validation with the bug. The same reasoning permits selective
backports of a main-first fix without importing unrelated development.

## Work Requested

Revise the generic Releases rule and corresponding agent instructions to
replace the blanket merge-before-every-candidate and no-cherry-pick mechanism
with this outcome obligation. Keep candidate tags immutable and release
branches unre-based. Do not require main to remain merge-compatible with an
older release line. Clarify where a selective/adapted mainline delivery belongs
under the existing workstream-routing rules; no autonomous workstream switch
is authorized by the choice of Git method.

The owner has changed the propagation methods, not explicitly the timing.
Project-management retained the existing requirement to resolve main's
disposition before each candidate. Do not infer permission to leave a known
main bug unresolved merely because a merge is difficult. Any timing change
remains a separate owner decision.

## Current Project Treatment And Evidence

Project-management has updated WORKFLOW-LOCAL.md with an owner-authorized
exception and the canonical release runbook at
engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md.
It also reconciled the earlier runbook-alignment intake with the current
release branch selection, driving workstream, and version rules.

The existing scripts/release-protocol.py candidate gate accepts ancestry or
patch equivalence. It cannot recognize an adapted correction or an unaffected
main. Its existing <tag>-integration-exception.json supports those ordinary
outcomes under the owner's standing direction: cite that direction in
`authorized-by`, exact main revision and evidence in `rationale`, responsible
workstream in `forward-port-owner`, and completed disposition in `follow-up`.
The runbook explains that these field names do not create unfinished work or
require fresh approval. Final promotion's `reviewed` integration method can
account for those same outcomes. No gate code changed in this slice.

Acceptance means that the generic rule and agent guidance allow the owner's
reasoned alternatives without a blanket prohibition; the local exception can
then retire. Keep any future gate-interface redesign separate unless needed
to make this rule usable.
