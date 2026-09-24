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

## Root cause, corrected 2026-09-24 after inspecting the running capsule

The owner objected that antigravity is present in the capsule launched from
this very checkout, so the acquisition must have been approved and rc3 must
be failing to recognize a recorded approval. The records and the code say
otherwise, and the corrected cause is worse than a lost record.

Facts from the capsule and the host configuration directory, read-only:

- The capsule's mount source is the `devcapsule` checkout; its container was
  created on 2026-09-14 at 15:01 UTC; its runtime PEX is v0.2.12-rc6 at
  source `2916c4c`, the same source as the 0.2.12 final; antigravity is at
  `/opt/antigravity-cli/bin/antigravity`, installed 2026-09-14 13:47.
- The only records that existed on 2026-09-14 are the project-level
  `devcapsule.checkout.toml` (2026-07-25) and `devcapsule.resolved.toml`
  (2026-07-27). Neither has an `[authorization]` table; the resolution
  predates the antigravity component entirely.
- The checkout record `devcapsule-2nd-home.checkout.toml` and its resolution
  were written on 2026-09-19 by 0.2.12. They authorize claude-code-download,
  development-sudo, docker-daemon, host-x11 and network, and the base. They
  contain no `antigravity-download` entry, and the resolution's
  `[authorization]` table has none either.
- The rc2-written record for `devcapsule-2` does contain
  `antigravity-download = true` with a recommendation digest.

So no record of an antigravity approval exists for this checkout, and none
was lost: 0.2.12 never asked for one at launch. Its
`environment_realization.ensure_realized_environment` enforced acquisition
consent for exactly one component, Claude Code, by name; every other
component the lock formation listed, antigravity included, was materialized
without consulting any authorization. The 0.2.12 `config list` showed the
missing answer as `missing-recommended` and nothing downstream cared.

0.2.14 closed that gap: `AuthorizationDeclaration.required` in
`configuration/authorization.py` is true for `base-image` and for every
declaration of kind `acquisition`, introduced by `6709756` and `85bec27` on
2026-09-20. That is the correct product rule for vendor terms. Its
consequence is the report above: a checkout materialized under 0.2.12
without recorded consent now needs the decision, because the client changed.
R-COMPAT-001's corollary calls a client-triggered refusal a defect and its
statement provides the way out: a release that cannot honor the requirement
names the exception, its justification and the migration instruction in its
notes, once, for one release. The justification here is that the earlier
client materialized a vendor download without recording consent, and the
new client will not proceed on a consent it cannot see.

Owner follow-up, 2026-09-24: shell history shows an init that named the
antigravity need explicitly, `project init --need node --need pycharm --need
antigravity-agent --need claude-code-agent --need codex-agent --authorize
base-image mycodespaceai/devcapsule-base:v0.2.9 --regenerate`, run with a
local build in the v0.2.9 days. That init did ask for and persist an
antigravity consent, but for a different project: its need list matches no
manifest of this repository, whose need has never contained `node`, and the
only records on this host carrying `antigravity-download` are the
tictactoe sample (born 2026-09-05), the trading-research sample
(2026-09-06), the website (2026-09-23) and `devcapsule-2` (2026-09-24). This
repository's own need gained `antigravity-agent` by commit `9248b68` on
2026-09-06 ("the dogfood project runs all three agents"), which is how the
component reached this checkout's lock formation without any consent ever
being asked for this checkout. The owner's memory of approving antigravity
is right; the approval belongs to other projects. Which launcher path
started the 2026-09-14 container, `project run` or the retired legacy
`pycharm run`, is still to be read from the owner's `ps` output; both are
consistent with the records and neither gated the acquisition.

The `resolution  generated  stale  manifest` row in the same listing is
legitimate and separate: the repository's manifest changed on `main` after
the checkout last resolved, and a project change may require `config resolve`.

Owner confirmation, 2026-09-24: after reviewing the checkout's final
resolution, which lists claude-code-download, development-sudo,
docker-daemon, host-x11, network and the base and no antigravity decision,
the owner accepts the analysis: the lock declared the gate, 0.2.12 installed
without enforcing it, and 0.2.14 asks for the first time.

## Disposition needed from the owner

1. Keep the rule and record the R-COMPAT-001 exception in the 0.2.14 release
   notes: 0.2.12 materialized vendor downloads other than Claude Code without
   recording consent; 0.2.14 asks once, with the remedy
   `devcapsule project --path … config authorize antigravity-download true`
   followed by `config resolve`. Recommended: it is the only disposition
   that does not reintroduce an unconsented download.
2. Or grandfather checkouts whose records predate 0.2.14 by treating an
   unanswered acquisition as the recommendation with a visible notice. This
   reproduces 0.2.12's consent gap for exactly those checkouts and is not
   recommended.

Either way the 0.2.14 notes must say what an upgrading 0.2.12 user will see,
and `config list` should say why the decision is newly required rather than
implying the user forgot.

## Verification

- A checkout record written by 0.2.12 with the acquisition unanswered
  launches under the 0.2.14 client, or is refused with the documented remedy
  named in the release notes, according to the chosen disposition.
- `config list` output for that checkout matches the chosen disposition.
