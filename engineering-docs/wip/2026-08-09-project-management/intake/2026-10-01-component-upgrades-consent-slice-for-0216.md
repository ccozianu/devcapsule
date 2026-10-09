# 0.2.16 candidate: the consent slice, owned by component-upgrades

Sent: 2026-10-01

From: `component-upgrades`, to `project-management`. The owner named the
release in this checkout; the proposal that carries the release scope is
on your branch.

## What is handed over

A new 0.2.16 candidate, owned by `component-upgrades`, decided by the
owner on 2026-10-01 in three records on `ws-component-upgrades/v1`:

- D-0011: vendor terms and trust given once per workstation, bound to a
  verified channel; DevCapsule's own base image is a channel anchored at
  the website.
- D-0012: host access asked only when the project recommends the less
  secure value; existing checkouts grandfathered.
- D-0013: a provenance sidecar beside each checkout, recording the client
  that wrote it and the questions it knew, so silence in old records is
  read correctly. Breaks no existing checkout.

The owner's words: "we shall act on it in time for 0.2.16."

## Why it belongs to you

Release scope and sequencing are yours; the candidate list and the cut
trigger live in your proposal. Implementation stays here.

## What accepting means

Add the candidate to the 0.2.16 proposal with `component-upgrades` as
owner; note that it touches the in-capsule read path of C8 (the
workstation record rides the read-only mount) and that the website gains
a small obligation, a page listing the published base digests, which is
`user-docs` or `website` content and not a gate. The consent design issue
on your branch can point at the three records as its outcome; two of its
questions remain open with the owner.
