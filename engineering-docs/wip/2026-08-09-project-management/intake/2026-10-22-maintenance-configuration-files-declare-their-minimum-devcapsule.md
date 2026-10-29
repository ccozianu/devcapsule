# Requirement from the owner: configuration files declare their format and the minimum DevCapsule that reads them

Date: 2026-10-22
From: maintenance
To: project-management

## Handoff

The owner stated a product requirement on 2026-10-22, after the regeneration
of this repository's shared lock on the release branch showed `project
config capabilities` rewriting the manifest into a newer vocabulary
(`required` and `optional` in place of `need`): for future upgrades of the
TOML files, a manifest must state its format and the minimum DevCapsule it
requires, so that an out-of-date client fails with a meaningful message. In
the owner's words: "we ought to have a manifest stating our format and the
minimum devcapsule required so that an out of date client fails with a
meaningful message."

This item is the requirement for planning; it carries no target and no
implementation owner. Project-management records it and sequences it; the
0.3.0 cycle does not take it.

## What exists today

- Every configuration file carries one integer, `devcapsule-schema-version`
  for the manifest, `devcapsule-lock-format-version` for the lock, and the
  checkout and resolution equivalents; `validate_file_format` in
  `devcapsule/configuration/file_formats.py` accepts only `1` and refuses
  anything else as "an unsupported schema version".
- Nothing states which DevCapsule a file needs. A schema-1 file written by
  a newer client with new vocabulary reads as schema 1 in an older client,
  which then fails on the unknown field, or reads past it, with a message
  about the field rather than about the client.
- [R-CONFIG-001](../../requirements/product/r-config-001-conservative-writers-tolerant-readers.md),
  conservative writers and tolerant readers, and
  [R-COMPAT-001](../../requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md),
  client upgrades require no user action, govern the compatibility of
  files between clients; the shared-checkout rule in `WORKFLOW-LOCAL.md`
  keeps this repository's own files readable by the latest release.

## The requirement, as the owner stated it and as the records suggest it be met

1. Each configuration file DevCapsule writes states its format and the
   minimum DevCapsule version able to read it, beside the schema integer it
   already has.
2. A client older than that minimum refuses the file with a message that
   names the version the project needs and how to get it, before any other
   diagnosis and before any write.
3. A writer raises the declared minimum only when it writes vocabulary an
   older reader cannot honour, and says so when it does; an unchanged file
   is not rewritten, which is the conservative-writers rule already.
4. The declaration itself must be readable by every client that predates
   it, which is the hard part: a client that does not know the field must
   still fail meaningfully, so the field's placement, or the schema
   integer's use, is a design question for the implementing workstream.

## Evidence

- The regeneration of 2026-10-22 on the release branch, recorded in the
  maintenance status file: the lock taken, the manifest rewrite declined
  because `required`/`optional` would shut the released 0.2.15 client out
  of the shared checkout.
- The bug record filed alongside this item, the rewrite of an unchanged
  manifest: `engineering-docs/bugs/devcapsule/2026-10-22-config-capabilities-rewrites-the-manifest-it-did-not-change.md`.
- The 2026-09-24 record of released launchers rejecting the repository
  manifest over an unknown attribute, the same failure shape.

## What accepting this means

Project-management records the requirement, assigns its home among the
product requirements and its implementing workstream, and sequences it;
the owner named no target. Nothing is asked of maintenance.
