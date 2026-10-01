---
status: confirmed
severity: untriaged
target: 0.2.14
owner: contained-display
opened: 2026-09-24
requirements: [R-PRODUCT-001, R-PRODUCT-002]
---

# Website links fail with xdg-open and no available browser handler

## Symptom and environment

Owner reports clicking `http://127.0.0.1:8080/` inside the website capsule
produces:

```text
xdg-open: no method available for opening 'http://127.0.0.1:8080/'
```

Read-only inspection on 2026-09-24 of the live website container
`pycharm-isolated-costin-1790207368` confirms RC0 runtime bytes/version,
image `devcapsule-local-codium:939b4bc8cedc2b3440f9`, and host networking.
The IDE environment has DISPLAY=:11, but no BROWSER or
DEVCAPSULE_HOST_OPEN_SOCKET. `xdg-open` and `sensible-browser` exist;
Firefox, Chromium, chromium-browser and google-chrome are absent from PATH.
No host-browser bridge is configured. No additional click was injected and
no credentials or complete process environments were collected.

## Expected and actual behavior

A frontend development environment needs a usable way to view its local app.
A click should use an available authorized browser path, or give a clear
explanation and supported remedy when none is configured. A raw xdg-open
failure leaves the user stranded.

Host networking makes loopback services reachable; it is not authorization
for the capsule to control the host browser. The defect must not be fixed by
silently enabling the separately denied/unselected host-browser bridge.

## Diagnosis and remaining decision

The observed environment has neither a supported browser executable on PATH
nor the host-open integration configured. This explains the missing opener;
it does not establish a defect in an enabled host-open broker. The shared
host-open implementation sets BROWSER to the delivered runtime's `host-open`
command only when the bridge is authorized.

Contained-display owns desktop integration and should decide the supported
no-bridge experience and its diagnostic. Determine whether a capsule-local
browser is intended to be included, or whether the launcher should explain
how to opt into host opening and how to open the address manually. Check the
IDE's actual link-opening path rather than relying only on Python browser APIs.
The owner explicitly marked the separate missing CLI bug blocking; this
record's independent release severity still needs triage.

## Reproduction and close criteria

- Use the website/front-end capsule with host networking, no host-browser
  grant and no local browser; click a local preview URL in the IDE terminal.
- Verify a useful supported outcome/remedy without an implicit grant.
- Separately enable the host-browser integration explicitly and verify an
  actual IDE click reaches the host browser; also cover nested launches.
- Check a configured capsule-local browser, if that is the chosen supported
  alternative. Preserve private network/host boundaries and record which
  network/display combination was exercised.
- Add automated coverage at the opener boundary and actual desktop acceptance;
  a running IDE alone does not establish this contract.
