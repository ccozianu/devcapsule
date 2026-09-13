# Intake: `config list` Renders By The Project's Configured Schema, And Only Mentions Updates

Delivered 2026-09-13 by `contained-display`, recording a product-owner
ruling given while reviewing how the new `host-x11` node surfaced in
`devcapsule project config list` on a checkout configured before the node
existed. It belongs with the upgrade-experience design already in this
queue (2026-09-03, *The Upgrade Experience Is A V1 Feature*) and is not a
decision for `contained-display` to make.

## The Ruling

`config list` should display a project's configuration according to the
schema version the project was configured with, not according to the
running tool's schema. Where the running tool knows a newer schema, the
listing should only *mention* that an update is available; it should not
present nodes, values, or statuses the project never configured as if they
were part of the project's state.

## What Prompted It

- A newer tool lists every workstation-capability node it knows
  (`docker-daemon`, `development-sudo`, `host-browser`, and now `host-x11`)
  on every checkout, including checkouts configured before a node existed,
  with status `available`. The developer did not configure those and cannot
  tell, from the listing, which are part of the project's recorded state.
- For an unanswered node the value column shows the *tool's* supported
  value (`host-x11 available true`), which reads as if passthrough were on.
  (A separate defect, where a recorded denial was also shown as the
  supported value, is fixed on main in PR #75/#76: recorded answers now
  render as recorded, with status `denied`.)
- The owner's framing: an authorization with `true`/`false` values making
  users opt in "one way or the other" is a side effect of implementation
  choices, not a product need; after the v0.2.12 flip an unanswered
  `host-x11` is simply the safe default and nothing needs answering. The
  listing should reflect that, not the tool's vocabulary.

## What This Touches

- The notion of a project's *configured schema version*: today the manifest
  and checkout record carry lock/format versions and recommendation
  digests, but no single "schema the developer configured against". The
  upgrade-experience design will need to name one.
- `_configuration_authorization_rows` and the value/status rendering in
  `commands/project.py`, and the `WORKSTATION_CAPABILITY_DEFAULTS` table
  that makes every known node appear everywhere.
- The obsolescence/update message the upgrade item already calls for: this
  ruling says where one of those messages goes.

## What Accepting Would Mean

Folding the ruling into the upgrade-experience design as a requirement on
`config list` (render by configured schema; mention updates only), and
sequencing the implementation with the rest of that feature. Nothing
blocks on it: the v0.2.12 candidates render recorded answers correctly and
the remaining oddity is cosmetic.
