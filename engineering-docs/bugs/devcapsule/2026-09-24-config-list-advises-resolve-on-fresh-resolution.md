---
status: fixed
severity: minor
target: 0.2.14
owner: maintenance
opened: 2026-09-24
requirements: [R-DOCS-002]
---

# `config list` advises an explicit resolve even when the resolution is fresh

Reported by the owner from v0.2.14-rc3 on 2026-09-24. In a checkout whose
resolution row reads `generated  fresh`, with every authorization answered
and no problem listed, `project config list` still ends with:

```text
Configuration review: ready to resolve.
base-image: authorized; recorded: …; recommended: v0.2.12-rc5 — …
After settling your configuration choices, resolve explicitly: devcapsule project --path … config resolve
```

`project run` then launches without any resolve, which surprised the owner:
the historical behavior was that `run` refused until the configuration was
resolved. The launch is correct; the message is wrong.

## Root cause

`ConfigurationReview.render()` in `configuration/review.py` appends the
resolve instruction unconditionally, and always prints the base-image line,
whatever the freshness of the generated resolution. The review object does
not know about freshness at all: `ready` means "no problems and every
authorization decided", and the resolution row's `fresh`/`stale` state is
computed separately in `configuration/freshness.py`. `config list`
(`commands/project.py`, the `print(review_configuration(...).render(root))`
call) prints the review after the table without consulting that state.

`project run` is right because `ExecutionConfiguration.load` checks
readiness and staleness itself: a fresh, ready configuration launches; a
stale one refuses unless `--force`, which prints the one-time warning. The
two commands therefore disagree only in what they tell the user.

## Fix

Render the trailer from the same facts the run path uses: when the
resolution is fresh and the review is ready, say so and give no resolve
instruction; when stale, name what went stale and the resolve command; when
decisions are required, keep today's text. Keep the base-image line, which
the owner uses to see what will execute. A contract test that a fresh, ready
checkout's `config list` contains no resolve instruction.

## Verification

- `config list` on a fresh, ready checkout ends with a ready statement and no
  resolve command; on a stale one it names the stale input.
- `project run` behavior is unchanged in both cases.

## Fix, 2026-09-24

Owner direction the same day widened the fix: `project config list` is a
data listing with no advice, and a new `project config show` prints the
listing followed by the review. `ConfigurationReview.render` takes the
generated resolution's state; a ready review over a fresh resolution says
"ready; the generated resolution is fresh" and gives no resolve instruction,
a ready review over a stale one names the stale inputs with the command,
and unresolved decisions keep the earlier text. Acquisition decisions that
are newly required say so. The upgrade-recovery test that expected remedies
in the listing now reads them from `show`; a contract test covers the
listing's silence and `show`'s three states. The guide and the source README
describe both commands.
