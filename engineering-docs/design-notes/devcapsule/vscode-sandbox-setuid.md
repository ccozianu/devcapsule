# The VS Code-Family Setuid Sandbox Helper

Decided 2026-08-31 by the product owner during the `component-catalog`
workstream: the materialized codium image keeps Electron's `chrome-sandbox`
helper setuid root (`root:root`, mode `4755`). Referenced from the codium
entry in `devcapsule/materialization.py` (`SURFACE_MATERIALIZATIONS`).

## The Problem

Chromium-based applications isolate renderer processes — the ones parsing
untrusted web content, extension code, and Markdown previews — inside a
sandbox. On Linux the preferred mechanism is user namespaces, but inside a
DevCapsule container unprivileged user namespaces are typically unavailable:
the container's own seccomp/apparmor confinement denies `clone(2)` with
`CLONE_NEWUSER`. Chromium then falls back to its legacy mechanism, a small
setuid-root helper (`chrome-sandbox`) that creates the isolation namespaces
with privilege and immediately drops it. If neither mechanism works, the
application refuses to start unless launched with `--no-sandbox`.

So the real choice for VSCodium in a capsule is:

1. **Setuid helper** (chosen): ship `chrome-sandbox` root-owned with mode
   `4755` in the materialized image.
2. **`--no-sandbox`**: launch flag; renderers run unsandboxed with the
   developer's full container privileges.

## The Trade-Off

Cost of the setuid bit: a root-privileged binary exists inside the capsule,
and setuid binaries are classic privilege-escalation surface. Mitigations
that keep the cost small:

- The helper is Chromium's purpose-built sandbox bootstrap, a few hundred
  lines of audited privilege-drop code, not a general-purpose tool.
- It ships pinned inside the checksum-verified VSCodium archive; the
  materialization recipe never patches or replaces it.
- Its blast radius is the capsule container, which is the boundary that
  DevCapsule already treats as the unit of exposure (`R-SCOPE-001`).

Cost of `--no-sandbox`: every renderer — including ones executing untrusted
project content and third-party extensions from Open VSX — runs with full
container privileges. That silently removes a defense-in-depth layer exactly
where DevCapsule's threat model cares most: code the developer did not write
running against a mounted checkout. It also normalizes a flag that users
would then carry into environments with weaker boundaries.

A privileged helper with a narrow, audited job beats an unsandboxed browser
engine with a broad one. The retired `codium_with_claude` image build made
the same call (`chown root:root && chmod 4755` at build time), so this is
also the proven-in-use configuration, not an experiment.

## Boundaries

- The JetBrains surface is unaffected; its JCEF browser sandbox is disabled
  through IDE properties, a decision that predates this note.
- If a future base image enables unprivileged user namespaces inside
  capsules, Chromium prefers them automatically and the setuid bit becomes
  inert; it can then be dropped in a recipe-version bump.
