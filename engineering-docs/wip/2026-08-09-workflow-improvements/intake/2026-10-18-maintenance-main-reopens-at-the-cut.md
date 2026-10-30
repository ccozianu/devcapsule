# Definition change: `main` reopens with the next development version at the cut

Date: 2026-10-18
From: maintenance, driving release 0.3.0
To: workflow-improvements, owner of the definition

## What is handed over

A revision of topic 11.2.7 in `WORKFLOW.md`, decided by the product owner
on 2026-10-18 and recorded as a local exception in `WORKFLOW-LOCAL.md`
(*Version Scheme* rule 4, and *Exceptions*):

> After the final tag, `main` reopens with the next development version,
> the next patch unless the owner names another.

becomes

> At the cut, `main` reopens with the next development version, the next
> patch unless the owner names another, by a pull request to `main` as
> soon as the release branch exists.

## Why

Under PEP 440 a development version orders before the release it names:
`0.3.0.dev0 < 0.3.0rc0 < 0.3.0 < 0.3.1.dev0`. With the reopening after the
final tag, `main` sits on the previous development version for the whole
candidate cycle, behind the release branch, and the merge of the release
branch into `main` before each candidate tag carries the release version
onto `main` unless someone resolves it by hand. In the 0.3.0 cycle the
first such merge, PR #228, did carry 0.3.0 onto `main`. Reopening at the
cut puts `main` ahead of every candidate and of the final release, and
after the first merge the version line never conflicts again.

## What accepting it would mean

Revise 11.2.7 and its *Unreleased* entry; the local exception ends when
the definition incorporates it. The humane text's worked examples mention
the reopening after the final tag and follow.

## Evidence

`WORKFLOW-LOCAL.md` on `main` after the reopening pull request of
2026-10-18; the maintenance status file under
`engineering-docs/wip/2026-09-18-maintenance/`; PR #228.
