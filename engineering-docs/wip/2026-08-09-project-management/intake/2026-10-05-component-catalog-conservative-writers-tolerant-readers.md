# Owner correction: conservative writers, tolerant readers and mandatory/optional needs

From: component-catalog
To: project-management, maintenance
Date: 2026-10-05

## Authority and correction

The owner's latest direction corrects and extends the 2026-10-04 item
`2026-10-04-component-catalog-0-3-launcher-bootstrap-lessons.md`. The crux is
"be liberal in what you accept and conservative in what you produce". This
is accepted owner direction for 0.3 planning, not merely an agent suggestion:

- This project's configuration must be written only by DevCapsule commands.
  Add missing operations rather than editing files directly.
- Before changes, use at least the running instance's `devcapsule0` to validate
  configuration. Development-only validation is insufficient.
- The circular self-hosting dependency is permitted as an explicitly managed
  exception, not banned through an absolute released-vocabulary rule.
- Split mandatory needs from optional enhancements. Warn and degrade gracefully
  when optional features cannot be provided; do not refuse the whole project
  when its mandatory needs can be met.
- This must cover adopter repositories receiving contributions their local
  checkout's launcher cannot fully handle. It is not a DevCapsule-only repair.

## Canonical changes on component-catalog

`WORKFLOW-LOCAL.md#keep-the-development-checkout-launchable` replaces the
narrower rule. New accepted requirement:
`engineering-docs/requirements/product/r-config-001-conservative-writers-tolerant-readers.md`
(R-CONFIG-001), indexed in REQUIREMENTS.md and index.md.
It records acceptance cases for newer optional declarations read by less
capable clients, mandatory failure, dependency integrity, non-destructive local
degradation, conservative round trips, command validation and self-hosting.

## Observed command gap for maintenance

`devcapsule0 version --json` reports 0.2.16.dev0, local-linux-x86_64, source
unknown. Its config help includes `need`, `resolve`, list/show and checkout
answer commands. `need` adds capabilities and regenerates the lock; it has no
removal/classification interface. `resolve` writes and requires launcher context.
`devcapsule0 project config list` succeeded in the capsule but explicitly prints
recorded launcher state; it does not validate the current working-tree manifest,
lock and proposed change for launch. Do not accept that listing as full validation.
Read-only baseline/candidate validation and missing configuration mutations
need supported commands. No project configuration was edited in this follow-up.

## Requested disposition

Project management: incorporate this correction into 0.3 scope and assign
implementation with the owner; align with component-upgrades' consent/recovery
contracts. Maintenance: take the concrete command/validation gap into the existing
configuration/in-capsule work and coordinate release routing with project
management. Schema names and command spellings are not preselected here.
The prior frozen-vocabulary guards protect today's required-only manifest;
they do not implement or define the future tolerant-reader contract.
