---
id: D-0012
title: Host Access Is Asked Only When The Project Recommends The Less Secure Value; Existing Checkouts Are Grandfathered
status: accepted
date-proposed: 2026-10-01
date-decided: 2026-10-01
decided-by: Costin Cozianu
requirements: [R-PRODUCT-001, R-COMPAT-001]
supersedes:
superseded-by:
---

# D-0012: Host Access Is Asked Only When The Project Recommends The Less Secure Value; Existing Checkouts Are Grandfathered

## Context

The consent design issue of 2026-10-01 found the product's prompts
inverted: vendor downloads, which the user cannot judge, were asked
repeatedly, while host access, which the user can judge and which matters
to their machine, was defaulted. D-0011 settled the vendor side. This
record settles the host side.

The host capabilities are the curated set in
`devcapsule/configuration/authorization.py`: the Docker socket, host
networking, development sudo, the host browser, and host X11 passthrough.
Each has a secure fallback (no socket, bridge network, no sudo, contained
display) and a less secure supported value. A project's manifest, not the
client, declares which it recommends and why, with a justification string;
this repository recommends host networking "for temporary dogfood
compatibility". Host X11 is never a project recommendation. The code already
distinguishes a project-recommended value from a workstation default, and a
checkout's recorded denial outranks any workstation-level allow (owner
rulings of 2026-09-03).

## Decision

1. **The user is asked to approve a host capability only when the project
   recommends its less secure value.** A project that recommends nothing,
   or whose recommendation is the secure fallback, asks nothing: the
   capsule gets bridge networking, no Docker socket, no sudo, the contained
   display. The question, when asked, shows the manifest's justification.
   Host X11 stays as it is: never recommended, always an explicit choice.
2. **Existing checkouts are grandfathered.** A checkout with a recorded
   value keeps it silently; no launch of an existing checkout asks again
   because the client changed (R-COMPAT-001). Only a new checkout, or a
   changed recommendation in the manifest, asks.

## Rationale

The question is worth asking exactly when the project wants more than the
secure default, because that is when the user has something to decide and
the justification to decide it on. Asking in every other case is the cried
wolf again. Grandfathering follows from R-COMPAT-001: a prompt triggered by
a client upgrade rather than by a change the user or the project made is a
defect.

## Consequences

- Nothing changes for a checkout that exists today.
- A project owner who recommends a less secure value owes a justification
  the user will read; an empty one is a manifest defect.
- Open with the owner, not decided here: whether records should carry the
  client version that last wrote them. Today only a schema version exists,
  and the checkout record refuses unknown fields, so a stamp at its top
  level would make an older client refuse a newer client's record on a
  workstation running both. A stamp therefore belongs in records that
  older clients never read, such as the workstation trust record of
  D-0011, or waits for a schema step.
- Implementation belongs to `component-upgrades` with D-0011; no release
  carries it until the owner names one.

## Reopen If

A capability appears whose secure fallback is unusable for ordinary work,
so that "ask only when recommended" would silently degrade every project;
or the grandfathering hides a recorded value a later client cannot honor.
