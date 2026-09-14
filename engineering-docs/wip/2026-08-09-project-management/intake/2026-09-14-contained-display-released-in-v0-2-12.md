# Intake: The Contained Display Shipped In v0.2.12

Delivered 2026-09-14 by `contained-display`.

## What Is Being Handed Over

Facts for the project-wide records `project-management` owns:

- **v0.2.12 is released** (final tag at the accepted rc6 commit `2916c4c`;
  promotion record `engineering-docs/releases/v0.2.12.json`, reviewed
  method). The base is `mycodespaceai/devcapsule-base:v0.2.12`, recipe 9,
  digest `sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c`.
- **The V1 ledger row *Contained Display And Desktop Integration*** can move
  from `proposed` to ratified: the required outcome holds (no host X socket,
  credential or `xhost` grant; loopback-only endpoint on a per-run port;
  per-run token in the run manifest; passthrough opt-in behind `host-x11`
  with its trade-off stated), and the owner has worked in the contained
  desktop since 2026-09-13, accepting the recipe-9 desktop shape on
  2026-09-14. The bug record
  `2026-08-16-x11-passthrough-grants-full-session-credential.md` is marked
  resolved in v0.2.12.
- **Release-process lessons for the guide** (already applied in
  `2026-09-01-release-and-validation-process.md` on main): the baseline
  version bump at branch cut; candidates gated on mainline integration or
  a documented exception; the base built by a candidate executable and
  pinned by the next candidate.

## Items This Bears On, Already In This Queue

- *Upgrade experience* (2026-09-03): the two rulings sent on 2026-09-13
  and 2026-09-14 (`config list` renders by the configured schema; `config`
  offers the recommended base) came out of this release.
- *Windows/WSL2* and the tutorial note went to `user-docs`.

## What Accepting Would Mean

Recording the ratification and the release in the ledger and the
portfolio; nothing blocks on it.
