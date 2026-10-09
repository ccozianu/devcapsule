# Defect: `project info` names every checkout `default`

Sent: 2026-10-09

From: `capsule-webconsole`, to `maintenance`. A defect found while building
the console's home page, which shows what `project info` reports.

## What is wrong

`project info`, text and `--json`, reports `checkout.name` as `default` for
a named checkout, on the host and inside the capsule. The value comes from
`configured_information` in `project_information.py`:

```python
"name": checkout.get("checkout", {}).get("name", "default"),
```

No writer puts a `name` key under `[checkout]` in a checkout record; the
record carries `path` only. The name of a checkout is the record file's
stem, as `config list` shows it and as `registered_checkouts` derives it.
Inside a running capsule the value is captured at launch into the launch
context's `info` block, so a relaunch is needed after the fix.

## Evidence

This capsule runs the named checkout `devcapsule-2nd-home`. In it,
`devcapsule project config list --json` reports `"name": "devcapsule-2nd-home"`
and `devcapsule project info --json` reports `"name": "default"`.

## Suggested fix

Derive the name in `configured_information` from the record path with
`checkout_record_name` in `configuration.storage`, with the `named` flag the
#185 review added, and add a test with a named checkout. The console needs
no change; its home page shows what the command reports.
