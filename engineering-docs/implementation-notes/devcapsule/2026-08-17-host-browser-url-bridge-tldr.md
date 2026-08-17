# Host Browser URL Bridge TLDR

Date: 2026-08-17

Status: proposed for human review; no implementation has started

## Problem

PyCharm runs as an X11 application inside a DevCapsule container. When the
user clicks an external hyperlink, Linux desktop integration invokes
`xdg-open` inside that container. The image has `xdg-utils`, but it has neither
a browser nor a route to the physical host's desktop URL opener, so `xdg-open`
exits with "no method available."

The current v026 image reproduces the boundary cleanly: `xdg-open` fails with
no browser configured, while setting `BROWSER=/bin/echo` makes it forward the
complete URL and exit successfully. The missing part is therefore a host
bridge, not another browser package in the image.

## TLDR

Add one narrow, explicit host capability:

```text
PyCharm hyperlink
  -> xdg-open inside the capsule
  -> BROWSER=devcapsule-host-open
  -> authenticated Unix socket mounted from the physical host
  -> host DevCapsule broker
  -> host xdg-open URL
  -> user's default system browser
```

The physical-host DevCapsule launcher owns the broker. A capsule receives only
the broker socket, its container-side path, and the `BROWSER` helper setting.
The helper sends one validated URL over the socket; the broker launches the
host opener with an argument vector and never through a shell.

For recursive dogfood, a launcher already inside a capsule must pass the same
inherited socket through to its successor. It must not start a second broker
inside the container or mistake the container's desktop tools for the physical
host. If no inherited bridge exists, the nested launcher and helper fail
clearly instead of inventing a broader fallback.

## Recommended V1 Boundary

- Use a Unix-domain socket under a mode-0700 host runtime directory. The socket
  is accessible only to the launching host user and is mounted at a fixed
  container path such as `/run/devcapsule-host-open.sock`.
- Export `DEVCAPSULE_HOST_OPEN_SOCKET` and set `BROWSER` to a packaged
  `devcapsule-host-open` helper. Continue to let PyCharm and `xdg-open` use
  their normal Linux integration path.
- Accept only absolute `http://` and `https://` URLs initially. Reject missing
  schemes, control characters, oversized requests, malformed protocol frames,
  and extra arguments.
- Invoke the host's opener as an argument vector, for example
  `xdg-open <exact-url>`, with no shell parsing. Do not log the full URL because
  query strings and fragments may contain credentials.
- Apply a bounded request size, timeout, and modest rate limit. Return a small
  success/error response so `xdg-open` receives a meaningful exit status.
- Treat the socket as an explicit host-UI capability in the runtime plan,
  launch summary, dry-run output, retained expected plan, and independent
  inspector. Redact the physical host socket source from retained/public
  evidence just like other host paths.
- The physical-host launcher owns broker startup, shutdown, and socket cleanup.
  A foreground root launch naturally bounds its lifetime. A detached root
  launch would require the desktop application or another durable host service
  to own it; it must not leave an anonymous background process behind.

Any process running as the capsule user can exercise a mounted socket. This
design does not pretend otherwise: enabling the bridge authorizes container
code to ask the host to navigate its browser. The narrow protocol, URL scheme
allowlist, filesystem permissions, and lack of shell execution keep that
authority substantially smaller than exposing the host desktop session bus.

## Recursive Propagation

The outer capsule already has machinery for recognizing host-backed mounts,
translating their sources for an external Docker daemon, staging launch files
on host-backed storage, and comparing the complete successor plan. Reuse those
seams:

1. A physical-host launch creates the broker and mounts its socket into the
   first capsule.
2. A recursive launch recognizes the inherited socket from the runtime plan
   and environment.
3. Bind-source translation resolves that inherited container path back to the
   physical-host source for the successor's `docker run`.
4. The successor receives the same fixed container path and environment, so
   no nesting-specific browser behavior is needed.
5. The expected-plan model and inspector verify the exact socket mount, mode,
   and non-secret environment values.

The current detached recursive successor remains viable while the original
physical-host IDE launch—and therefore its broker owner—is alive. Persistence
beyond that lifetime is a separate desktop-service lifecycle decision, not
something this bridge should solve implicitly.

## Deliberate Non-Solutions

- Do not mount the host D-Bus or desktop session bus. That grants unrelated
  desktop authority and is harder to inspect and propagate safely.
- Do not install or launch a browser inside the image. It would be another
  container application, not the user's system browser, and would add state,
  credentials, and sandboxing concerns.
- Do not expose a TCP listener. A filesystem-scoped Unix socket gives a
  simpler local authorization and lifecycle boundary.
- Do not accept arbitrary commands, filesystem paths, `file://`, `mailto:`, or
  custom schemes in V1. Additional schemes require separate threat and UX
  review.
- Do not silently fall back to a container browser or session bus when the
  bridge is missing.

These exclusions describe the native-X11 desktop integration targeted by this
slice. If a future DevCapsule GUI is delivered through noVNC, a browser-hosted
remote desktop, or a similar display transport, URL ownership may belong to
that client session instead of the physical host launcher. Revisit the routing
protocol for that deployment mode. It may be more coherent—and may be
necessary—to embed a browser in the DevCapsule image, provided its state,
credentials, sandboxing, and lifecycle are designed and authorized explicitly.
Do not carry the native-X11 host-browser choice into noVNC by accident.

## Smallest Implementation Slice

1. Add the host broker and container client protocol to the DevCapsule PEX.
2. Package the `devcapsule-host-open` helper and set the launch environment.
3. Add broker socket lifecycle and the launcher mount on physical-host runs.
4. Propagate the inherited bridge through recursive launch planning and source
   translation.
5. Extend runtime-plan, expected-plan, inspection, and redacted output models.
6. Add unit and integration coverage before the live GUI check.

This changes both the host launcher and the client executed inside the image,
so the accepted fix requires a newly built PEX and a matching rebuilt base
image. It should be included before declaring a v026 pair final if v026 is
expected to contain clickable-host-browser support.

## Acceptance Checks

- A fake host opener receives exactly one unchanged URL—including `&`, `%`,
  query strings, and fragments—with no shell interpretation.
- Unsupported schemes, malformed frames, control characters, oversized
  requests, missing sockets, timeouts, and broker failures return nonzero.
- The socket directory and socket have the intended ownership and permissions,
  and cleanup removes them after the owning launch exits.
- Launcher tests prove the mount and environment are present only when the
  capability is enabled; expected-plan tests reject missing, writable-relaxed,
  substituted, or extra mounts.
- A container integration test runs `xdg-open` and observes the fake physical
  host opener without requiring a browser in the image.
- Recursive integration proves a successor uses the same physical-host broker
  and does not create a container-local broker.
- Manual dogfood proves a clicked PyCharm hyperlink opens the user's default
  host browser and that closing the owning launch cleans up the bridge.

## Review Decision

Before implementation, confirm whether this narrow URL-only capability and
its lifetime are acceptable, and whether it should be enabled by default for
desktop-launched IDE capsules or require an explicit per-developer
authorization. That product-policy choice changes configuration and UX work,
but not the recommended socket architecture.
