---
status: confirmed
severity: untriaged
target: 0.2.14
owner: maintenance
opened: 2026-09-24
requirements: [R-COMPAT-001]
---

# A client upgrade turns an unanswered acquisition into a required decision

Reported by the owner from v0.2.14-rc3 on 2026-09-24, in a checkout that had
only ever been launched by 0.2.12 clients and had been working. Under rc3,
`project config list` reports:

```text
authorization  antigravity-download  missing-required  true
Configuration review: decisions required.
antigravity-download: missing-required; recorded: unanswered; recommended: true
  An explicit decision is required before this environment can run.
```

The owner did not run `project run` there, to protect the checkout; the
review says it would refuse. The same checkout under the published 0.2.12
lists the same decision as `missing-recommended` and launches.

## Root cause

`AuthorizationDeclaration.required` in `configuration/authorization.py`
returns true for `base-image` and for every declaration of kind
`acquisition`, with the comment "a selected executable and vendor
acquisition require a decision before realization". That rule arrived after
0.2.12, in `6709756` ("Fix upgrade recovery with shared configuration
assessment", 2026-09-20) and `85bec27` (the configuration reorganization of
the same day). In 0.2.12, `commands/project.py` classified an unanswered
acquisition as `missing-recommended` when the project recommended it, and
the launch proceeded.

So a checkout that needed nothing from its user under 0.2.12 needs a
decision under 0.2.14 because the client changed, not because the user or
the project changed. That is the corollary of R-COMPAT-001 verbatim: a
refusal triggered by a change in the client is a defect, whether the
trigger is a version gate or a new required field. Requiring explicit
consent to a vendor's download terms may well be the right product rule;
R-COMPAT-001 then requires the release to name the exception, its
justification and the one-command remedy in the 0.2.14 notes, and says such
an exception is justified once, for one release.

The same listing also shows `resolution  generated  stale  manifest`. That
one is legitimate: the repository's manifest changed on `main` after the
checkout last resolved (the 0.2.14 runtime-command declaration and its
compatibility fix), and a project change may require `config resolve`.

## Disposition needed from the owner

1. Restore 0.2.12's behavior for an unanswered acquisition: treat it as the
   recommendation with a visible notice, and require the explicit decision
   only for a checkout initialized by 0.2.14 or later; or
2. keep the rule and record the R-COMPAT-001 exception in the 0.2.14 release
   notes with the remedy
   `devcapsule project --path … config authorize antigravity-download true`
   followed by `config resolve`.

Either way the 0.2.14 notes must say what an upgrading 0.2.12 user will see.

## Verification

- A checkout record written by 0.2.12 with the acquisition unanswered
  launches under the 0.2.14 client, or is refused with the documented remedy
  named in the release notes, according to the chosen disposition.
- `config list` output for that checkout matches the chosen disposition.
