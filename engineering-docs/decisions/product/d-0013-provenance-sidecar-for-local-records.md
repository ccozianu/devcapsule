---
id: D-0013
title: A Provenance Sidecar Beside Each Checkout Records Which Client Wrote It And Which Questions It Knew
status: accepted
date-proposed: 2026-10-01
date-decided: 2026-10-01
decided-by: Costin Cozianu
requirements: [R-COMPAT-001, R-PRODUCT-001]
supersedes:
superseded-by:
---

# D-0013: A Provenance Sidecar Beside Each Checkout Records Which Client Wrote It And Which Questions It Knew

## Context

No local record says which DevCapsule client last wrote it. The checkout
and resolution records carry only a schema version, fixed at 1, and the
checkout record refuses unknown fields, so a version stamp added to it
would make an older client refuse a newer client's record on a
workstation running both. Meanwhile a future client that introduces a new
security-sensitive question cannot tell, from an old record, whether the
answer is missing because the user was never asked or because the user
left the default on purpose. The owner's framing: be liberal in what you
accept and conservative in what you produce, and find a way forward that
breaks no existing checkout.

## Options Considered

### Option A: a client-version field in the checkout record

Cost: older clients refuse the record. Requires a schema step and a
release of unknown-field tolerance first, so nothing can be learned about
today's records.

### Option B: a version number alone, in a sidecar

Cost: safe for older clients, but a version implies a table in every
future client of which questions existed in which release, carried
forever, and it cannot describe a project's own declared values.

### Option C: a self-describing sidecar, with the question names

Cost: one more small file per checkout and a digest to keep it honest.

## Decision

Option C. Beside `<name>.checkout.toml` and `<name>.resolved.toml`, in the
same directory, the client writes `<name>.provenance.toml`:

```toml
devcapsule-provenance-schema-version = 1

[[record]]
file = "<name>.checkout.toml"
written-by = "0.2.16"
written-at = "2026-10-01T14:12:09Z"
content-sha256 = "<digest of the record as written>"
questions-known = ["base-image", "network", "docker-daemon", "development-sudo",
                   "host-browser", "host-x11", "claude-code-download", "..."]
```

- **Conservative in what we produce.** The checkout and resolution records
  keep their schema-1 shape with no new fields. The sidecar is the only
  new thing, and older clients never open it. It lives in the directory
  the capsule already mounts read-only, so it is visible inside as well.
- **Liberal in what we accept.** A newer client admits any schema-1 record
  whether or not a sidecar exists. The sidecar never gates admission; it
  changes only how silence is read.
- **How silence is read.** An answer absent from the record and its name
  absent from `questions-known` was never presented: the property's own
  policy decides, and a new security-sensitive property may mandate an
  answer. An answer absent but its name present was left unanswered
  knowingly, default applied: grandfathered under D-0012. No sidecar, or
  a `content-sha256` that no longer matches the record on disk, means a
  client predating this wrote or rewrote the record: an unknown writer,
  for which every newer question counts as never presented.
- **Why names, not a version.** The list makes the record self-describing
  and can include the project's own declared values and secret inputs,
  which no release number encodes.
- The workstation trust record of D-0011 carries the same `written-by`
  line at its top, since no older client reads it either.

## Rationale

The digest is what keeps the sidecar honest on a workstation running two
launcher versions: when the older one rewrites the record, the stamp stops
matching and the newer client falls back to the conservative reading
instead of trusting a stale description. Everything else follows from
R-COMPAT-001: the newer client learns more about old records without
asking anything of them, and the older client sees nothing new.

## Consequences

- Target release: **0.2.16**, by owner direction, in the
  `component-upgrades` slice with D-0011 and D-0012.
- The first newer client to touch an existing checkout writes the sidecar
  on its next write of the record, not on read; reads never mutate records.
- A later schema step may add unknown-field tolerance to the main records;
  by then the sidecar says which clients wrote what.

## Reopen If

The sidecar's per-record digest proves too fragile under concurrent
launchers, or a record kind appears that cannot be described by a list of
question names.
