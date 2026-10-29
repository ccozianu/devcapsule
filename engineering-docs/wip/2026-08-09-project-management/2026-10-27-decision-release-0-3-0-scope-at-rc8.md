# Release 0.3.0: The Scope Rechecked At Candidate 8

Date: 2026-10-27
Decision: product owner, in the project-management session, after the
agent reconciled candidate 8 against the scope decision of 2026-10-18 and
the final-tag gates the release overview records.
Status: accepted; the work is with `maintenance` on `release-0.3.0`.

## The occasion

On 2026-10-26 the owner ruled, in the maintenance session, that candidate
8 becomes 0.3.0 unless a showstopper appears. On 2026-10-27 the owner
asked project-management to check that ruling against what the 0.3.0 plan
still carried. The check found three in-scope dogfooding slices in no
candidate, the diagnostics snapshot, image and cache cleanup and C20; six
fixed bug records not yet verified on a downloaded candidate; the
release notes not written; the eleven user-docs proposals and the C17
generic half still open with their owners paused; and the
workstation-commands record awaiting the owner's choice of home.

## Decisions

1. **Image and cache cleanup leaves 0.3.0**, tentatively for 0.3.1, under
   the reopen rule of the 2026-10-18 decision. The installed-IDE record's
   two halves are now both out of 0.3.0 and go to the next planning
   together.
2. **Workstation-scoped commands stay in 0.3.0.** Their API shape is
   designed with the owner in chat, later in this session or the next;
   the implementation is a maintenance slice before the final tag. The
   owner's assumption that the code exists and only the wiring moves was
   checked: it holds for `default memory|cpus` and `trust withdraw`,
   which read nothing from the project; it does not hold for `trust
   accept`, whose channel, the vendor, the origins, the integrity method
   and the terms, is derived from the project's lock. A project-less
   acceptance needs a source for that definition, and that source is a
   design choice of the API shape, not wiring. The project's view of its
   channels, `trust list`, needs the project and may stay where it is.
3. **VS Code joins 0.3.0** as a second provider of `frontend-ide`.
   VSCodium stays the default. VS Code carries an acquisition contract,
   Microsoft as vendor with its terms, so that the download comes from
   Microsoft at the developer's request and is never redistributed by
   us, and so that it is a trust channel under D-0011. The owner's words:
   we cannot run much longer without supporting the most distributed IDE.
   The slice is a maintenance slice for the next candidate; it is the
   first IDE capability with two providers, which is where its risk sits.
4. **C20 is scoped for 0.3.0 and ordered** as
   [the work order of 2026-10-27](../../work-orders/2026-10-27-release-documentation-automation.md),
   merged into `main` by PR #292: the helper `release-docs.py`, the
   final-tag path of the release workflow that checks before it
   publishes and dispatches the test-site build after, the website
   workflow's guard against a version without a download, and the rule
   changes they carry. The pair: Codex, gpt-6-astra, implements; Claude
   Code, Claude Fable 5.1, reviews; dispatched from this session on the
   owner's merge.

## Settled later the same day

- **The diagnostics snapshot and export command is in 0.3.0**, delivered
  by PR #293 on `release-0.3.0` at `0514d50`, merged by the owner on
  2026-10-27 after the Codex, gpt-6-astra review in PR #295 was accepted
  without a round. It implements Deliverable 4 and the manual
  browser-evidence contract of Deliverable 5 of the 2026-10-08 session
  diagnostics order: `devcapsule project diagnose`, the bounded in-capsule
  probe, the sanitized export. Two reviewer proposals stay with the owner,
  as PR #293 lists them: a deadline budget across the runtime probes, and
  a distinct schema value for an unlimited cgroup limit. All three
  dogfooding slices the check found undelivered now have a ruling: C20
  merged by PR #294, diagnostics by PR #293, cleanup out.
- **The workstation commands' API shape is designed and ordered**, later
  the same day, as
  [the work order of 2026-10-27](../../work-orders/2026-10-27-configuration-home-and-the-home-commands.md):
  one configuration home named by `DEVCAPSULE_CONFIG_HOME`, defaulting
  to the XDG path as today; a `devcapsule home` group holding `trust
  accept|withdraw|list`, `default` and `show`, with the three mutating
  spellings deleted from `project config`; one `settings.toml` with a
  schema integer and a `minimum-devcapsule` field, the first instance of
  the owner's 2026-10-22 requirement; the word "workstation" removed.
  The owner's reasoning, nothing the launcher depends on is global, after
  Bracha's Newspeak, is recorded in the order. The same pair implements
  and reviews.
  Implemented on 2026-10-28 as PR #299 to `release-0.3.0`, reviewed in
  PR #300 (accepted without a round, merged at `e83c0881`); awaiting the
  owner's merge. One rule of the order changed under review and is
  listed for the owner in the pull request: inside a capsule the home
  commands write the capsule's own home instead of refusing, because the
  capsule's own state must stay writable for a launcher run inside it.

## Amendment: October 25 documentation proposals move to 0.3.1

Owner decision, 2026-10-29: postpone the new documentation proposals in
[the October 25 work order](../../work-orders/2026-10-25-documentation-orientation-and-concepts.md)
to **0.3.1**. Both Part A and Part B now have that target. The new
orientation, concepts/glossary, persistence explanations, recipes,
background-agent guidance and site proposals do not gate 0.3.0.
Maintenance remains the work order's owner and retains it for 0.3.1 planning.

The separate October 24 language review remains a condition of 0.3.0,
as does C16: documentation must describe the accepted candidate. This
decision does not postpone those obligations or C20 release automation.
Existing documentation stays; this is a scheduling decision, not a rollback.

Glossary and recipes, items 5 and 6 of the September 28 proposal list,
remain accepted through the October 25 order, now for 0.3.1. The other
nine proposal decisions remain open. This decision does not settle them.

Maintenance receives the decision by coordination mail to update the work
order, release overview and its own plan on the release branch.

## Still open from the same check, for the owner

- Who performs the documentation language review, which pages, in what
  order, and under which reviewer loop; the mail of 2026-10-24 in this
  workstream's intake.
- The remaining nine user-docs proposal decisions and delivery of the C17
  generic half; both remain final-tag obligations while `user-docs` and
  `workflow-improvements` are paused.
- Who verifies the six fixed bug records on the rc8 download, two of
  them from inside a capsule, three with Docker.
- Provider acceptance of the new agent pins on a downloaded candidate,
  listed as awaiting the owner since rc3; not confirmed in the records.

## What this changes in the records

- The release overview's *Scope And Owner Decisions* gains the rulings
  above; the bug table's installed-IDE row says both halves are out; the
  workstation-commands row says the home is designed in chat and the
  slice is in the cycle. `maintenance` writes these on the release branch.
- The 2026-10-18 decision's list of in-scope slices is amended by this
  record: cleanup out, VS Code and the workstation commands in, C20 as
  ordered.
- The content-contract mail of 2026-10-18 is closed by the C20 order,
  which makes the `source-version` line on the `devel` entry the
  documented practice.

## Reopen if

A further candidate shows VS Code or the workstation commands larger than
the cycle tolerates, in which case either moves out by the owner's word
and the overview says so.
