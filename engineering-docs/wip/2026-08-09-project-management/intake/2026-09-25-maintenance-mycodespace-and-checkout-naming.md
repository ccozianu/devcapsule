# Input: The mycodespace Design Note, And A Checkout-Naming Default

Sent: 2026-09-25

From: `maintenance`, forwarding two product-direction items that were
recorded in this repository but never delivered to the workstream that owns
product direction. Decisions are the owner's; adoption and sequencing are
yours.

## 1. The mycodespace design note

Written 2026-09-24 at the owner's direction while `user-docs` was paused:
`engineering-docs/design-notes/devcapsule/2026-09-24-mycodespace-lifetime-namespace-and-archive.md`,
status proposed. It specifies the larger product DevCapsule joins: a single
person's lifetime namespace of projects with one-action materialization, an
owned content-addressed archive, a "kept today stays runnable" guarantee,
a small Python tool over four universal primitives, and a workspace view
that replaces git submodules for independent co-located projects. It fixes
the budget envelope, one person and three agents on flat-rate subscriptions
plus a workstation with a browser and Docker, and names the open questions
for the owner. It also answers this repository's own submodule question
(section 8, migration of this repository). Ask: adopt or reject it as
direction, and register the first slice when the owner wants it started.

## 2. A checkout-naming default

Under D-0004 a second checkout of a project identity must take a
workstation-owned name, and nothing derives it from the directory. On the
owner's workstation this produced `devcapsule-2nd-home` for
`myProjects/devcapsule` and `dev-capsule-2` for `myProjects/devcapsule-2`,
because the default record slot is held by a July record whose path no
longer exists. The owner ruled this not a bug during 0.2.14 acceptance and
deferred a change. Proposed: default the name to the directory's last
component when unique among the identity's live checkouts; treat a default
record whose path is gone as not occupying the slot, while still listing it
as `missing`; print the directory-to-record mapping in `project checkout
list` and beside the checkout path in `config list`. Small, and a natural
companion to the catalog records above.
