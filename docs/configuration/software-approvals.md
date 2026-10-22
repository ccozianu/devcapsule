---
description: When a project's lock brings a new version of vendor software you approved before, the launcher asks once for the whole list; how to answer, and how to approve from the command line.
weight: 7
updated: 2026-10-22
---
# Software approvals

Some of the software a capsule contains is downloaded from its vendor under
that vendor's terms, and DevCapsule never redistributes it: the coding agents
are the usual case. Before the first download of such a component, DevCapsule
asks you to approve it, by name and version, and records your answer in your
checkout's own configuration. The project's lock pins the version.

When the project's lock changes, usually because you synchronized your
checkout with the project's remote and the project moved to newer agents,
the pinned versions change with it. Your earlier approval named the earlier
version, so the new version is a new question, one per component.

## At launch, one question for the whole list

When the only decisions pending for your checkout are of that kind, new
versions of software you approved before, from the same vendors under the
same terms, `project run` shows the list and asks once:

```text
The project's lock brings new versions of software you approved before; the vendors and their terms are unchanged:
- Claude Code <previous> to <new>, downloaded from Anthropic under https://www.anthropic.com/legal/commercial-terms (claude-code-download)
Approve all of them? Press y; any other key cancels:
```

The version you last launched is shown when a record of a successful launch
exists; the version the lock pins now is always shown.

- **y** records every approval in your checkout and regenerates the resolution.
  If resolution succeeds, the launch continues. It does not ask for those approvals again.
- **Any other key, or end of input** stops the launch, writes nothing, and
  prints the command that approves later, below.

Without a terminal, in a script or an agent's session, the launcher prints
the list and the command and stops; it never approves on your behalf.

Anything else pending in the list takes you out of this path: a component
you never approved, one you denied, a changed host-access recommendation,
a base to select. Those are decided one by one, as
[granting and withdrawing](../containment/granting-and-withdrawing.md)
describes, and `project config resolve` lists them with their commands.

## From the command line

```bash
~/.local/bin/devcapsule project config approve
~/.local/bin/devcapsule project config approve --all
~/.local/bin/devcapsule project config approve claude-code-download
```

The first lists what is pending and changes nothing. The second approves
every pending software update; the third approves the named ones only, by
the authorization name shown in the list. If other software approvals remain,
the command names them and leaves the resolution unchanged. Approve the
remaining updates to regenerate it.

If resolution fails after you approve, your approvals remain saved. The
error names the problem and the `project config resolve` command to retry.
Resolve the problem and run that command before you launch again.

An interrupted activation must finish recovery before software approvals
can be inspected. `config approve` names `project config resolve` for recovery.
At launch, the approval check defers to the launcher's existing recovery path.

Run `config approve` with the launcher outside the project's capsule.
Inside that capsule, the command refuses and prints the launcher command.

## What an approval is, and is not

- It is your consent to download that vendor's software, at the pinned
  version, under the terms the list names, into capsules of this checkout.
  Every download is checked against the lock's checksum regardless.
- It is per checkout, like every personal answer in
  [project versus personal](project-versus-personal.md).
- It grants no host access and selects no base; those are separate
  decisions with their own commands.
- Declining is not a denial. A denial is `config authorize NAME false`,
  recorded until you change it; declining the launch question leaves the
  earlier approval in place, for the earlier version, and the launch waits.

What each component brings is on [component upgrades](../updates/component-upgrades.md).
