# Intake: `project config` Offers The Recommended Base The Tool Knows About

Delivered 2026-09-14 by `contained-display`, recording a product-owner
ruling given while preparing the v0.2.12 release: "project config should
have a submenu for the recommended base image the pex knows about". It
belongs with the upgrade-experience design already in this queue
(2026-09-03) and with the 2026-09-13 ruling that `config list` renders by
the project's configured schema and only mentions updates.

## What Happened

The owner restarted the dogfood capsule from the published v0.2.12-rc6
executable expecting the shipped desktop, and got the old one without the
panel. The lock pinned the published recipe-9 base, but the host checkout's
developer-owned `base-image` authorization still named a local recipe-8
twin recorded days earlier by the hands-on script's `select` step. A local
override outranks the lock's pin by design; nothing at `config` or at
launch said "your override predates what the lock now recommends", and the
launcher's only hint was the runtime's one line about the base having no
panel. The owner looked for the recommended base under `project config` and
found no way to pick it.

Two checkout records were involved, which sharpened the confusion: the
host's record (used by the host launcher) and the persistent-home record
inside the capsule (used by launches from inside) had diverged.

## What Exists Today

- `devcapsule project config authorize base-image default` already accepts
  the lock's recommended base without pasting a digest (reserved keyword,
  owner ruling 2026-09-03). It is undiscoverable: nothing lists it.
- `config list` shows the current authorization only. It does not show the
  lock's recommendation beside it, whether the current value is a local
  override, or that the running tool's matrix knows a newer base than the
  lock pins.
- `project init --regenerate` is the project-owned way to move the lock to
  the tool's newest base; it is not surfaced from `config` either.

## The Ruling, As A Requirement

`project config` presents the base as a choice, not a digest field:

1. the lock's pinned base (the project's recommendation) — acceptable in
   one action (`default` today);
2. the newest base the running executable's matrix knows, when it is newer
   than the pin — shown as an available update, with the project-owned
   action (`init --regenerate`) named, per the 2026-09-13 ruling that the
   listing mentions updates rather than presenting them as state;
3. the checkout's current value, marked plainly when it is a local override
   or predates the pin.

And the launch says, once, when it runs a base other than the lock's pin
because of a checkout override.

## What Accepting Would Mean

Folding these into the upgrade-experience design and sequencing them with
the `config list` rendering work. `contained-display` records the incident
and the `default` shortcut in its handoff; the release proceeds on the fixed
checkout.
