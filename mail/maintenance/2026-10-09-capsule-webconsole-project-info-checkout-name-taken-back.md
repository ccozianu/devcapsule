# Supersedes: the `project info` checkout-name defect is fixed by `capsule-webconsole`

Sent: 2026-10-09

From: `capsule-webconsole`, to `maintenance`. This item supersedes
`2026-10-09-capsule-webconsole-project-info-checkout-name.md`, sent earlier
today. The owner directed the fix into `capsule-webconsole` on 2026-10-09,
as the fourth stacked slice of the web console's first iteration.

## What to do with the earlier item

Nothing. Dispose of both items together as superseded. The fix derives the
name from where the record lives through one helper,
`checkout_name_for` in `configuration.storage`, used by `config list`,
`project info`, the launch context and the checkout registry; the text
report of `project info` gains a `Checkout name:` line; inside a capsule the
name comes from the mounted record, so a context captured by an older
launcher reports it right too.
