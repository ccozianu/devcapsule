# Renderer Sandboxing For Chromium-Family Surfaces

Ruled 2026-09-02 by the product owner, superseding the 2026-08-31 setuid
ruling recorded in [vscode-sandbox-setuid.md](vscode-sandbox-setuid.md):
Chromium-family surfaces run with `--no-sandbox` under full container
hardening *for as long as we can*. Renderer sandboxing is retired from
every shipped surface; this note records the posture that replaced it and
what re-enabling would entail, so the return path is a documented decision
rather than an archaeology project.

## Why The 2026-08-31 Ruling Was Superseded

The setuid-helper posture kept Chromium's renderer sandbox at the price of
a narrow capability grant (`CAP_SETUID`, `CAP_SETGID`, `CAP_SYS_ADMIN`,
`CAP_SYS_CHROOT`, and dropping `no-new-privileges`). Three days of use
showed the price was higher than the analysis had it:

- **The grant and the development-sudo posture are incomparable sets.**
  Sudo launches run with Docker's default capabilities, which let the
  helper *start* (setuid succeeds) but not *sandbox* (namespace creation
  needs `CAP_SYS_ADMIN`), so the zygote aborts and the surface never
  comes up — the
  [2026-09-02 sudo-sandbox bug](../../bugs/devcapsule/2026-09-02-codium-setuid-sandbox-crashes-under-development-sudo.md),
  A/B-confirmed by the owner. Fixing it meant widening the sudo posture
  with `CAP_SYS_ADMIN` too, spreading the grant to every posture.
- **`CAP_SYS_ADMIN` in the bounding set is meaningful kernel attack
  surface**, and the setuid helper is invocable by any capsule process,
  not only by Chromium.
- **The special-casing leaked everywhere**: a per-surface hardening
  branch in the host launcher, a root-owned mode-4755 binary baked by the
  materialization recipe, a launch-time disclosure, and posture-specific
  tests — all for one surface's inner sandbox.

The owner weighed the uniform container posture above renderer-level
isolation and reversed the earlier call.

## The Posture As Ruled (2026-09-02)

- Container hardening is uniform across surfaces: no-sudo capsules run
  `--cap-drop ALL --security-opt no-new-privileges`; development-sudo
  capsules run Docker's default capability set with the sudo group added.
  No surface narrows or widens it.
- The codium runtime template carries `--no-sandbox` in
  `additional_arguments`. The flag travels as template data, not adapter
  logic, deliberately: the published v0.2.8 base's frozen runtime already
  appends `additional_arguments` verbatim, so the posture works on every
  base that can run codium at all.
- The materialization recipe no longer marks `chrome-sandbox` root-owned
  mode 4755 (`vscode-local-materialization` recipe version 2). Canonical
  images contain no setuid-root binary; under `--no-sandbox` the helper
  file is never invoked, and under `no-new-privileges` a setuid bit would
  be inert anyway.
- The runtime adapter refuses a template that declares
  `sandbox = "setuid-helper"`, and refuses a vscode-family template whose
  `additional_arguments` omit `--no-sandbox` — either mistake would
  otherwise surface as a cryptic zygote abort at launch instead of a
  plan-time error naming this note.
- The launch prints a disclosure that renderers run unsandboxed, the
  analogue of the JCEF disclosure on the JetBrains surface.

What this costs, stated plainly: renderer processes parsing untrusted
project content, Markdown previews, and third-party Open VSX extension
code run with the capsule user's full privileges — the mounted checkout,
the capsule-held credentials, and any separately authorized Docker
access. Docker's outer isolation is unchanged and remains the boundary
DevCapsule actually guarantees.

## What Re-Enabling Renderer Sandboxing Would Entail

Two mechanisms exist. Both are container-level decisions, not surface
tweaks.

### Route 1: unprivileged user namespaces (preferred if it becomes cheap)

Chromium's first choice needs no privileged helper: renderers isolate
via unprivileged user namespaces. The capsule's current seccomp
confinement denies their creation, which is why the setuid helper was
ever in play. Re-enabling this way entails:

- The base recipe permitting unprivileged user-namespace creation in the
  capsule seccomp profile (and whatever kernel sysctls the host needs),
  a `contained-display`-coordinated base change with its own security
  analysis — user namespaces are themselves kernel attack surface.
- Nothing at all on the surface side beyond removing `--no-sandbox` from
  the template: Chromium prefers user namespaces automatically, no
  setuid bit, no capability grant, `no-new-privileges` stays.

### Route 2: the setuid helper (the reverted 2026-08-31 mechanism)

Everything the grant entailed, plus the sudo-posture fix the bug record
scoped:

- Materialization: `chrome-sandbox` root-owned mode 4755 again — a
  recipe change with a version bump and a canonical-image rebuild.
- Template: the `sandbox = "setuid-helper"` declaration restored, and
  `--no-sandbox` dropped from `additional_arguments`.
- Host launcher, no-sudo posture: the narrow grant back — `--cap-drop
  ALL` plus `CAP_SETUID`, `CAP_SETGID`, `CAP_SYS_ADMIN`,
  `CAP_SYS_CHROOT`, without `no-new-privileges` — keyed on the
  declaration, with the capability disclosure printed at launch.
- Host launcher, sudo posture: Docker's default set plus
  `CAP_SYS_ADMIN` (default-caps lack it; that gap is exactly the
  2026-09-02 crash). This is the piece the 2026-08-31 implementation
  missed.
- Regression tests per posture, and a re-run of the base-vs-runtime
  compatibility check: a frozen runtime that predates the declaration
  vocabulary must reject, not mislaunch.

The 2026-08-31 implementation is in git history (removed 2026-09-02 with
this note's ruling) and in the superseded note's analysis.

## What Would End "As Long As We Can"

The ruling is explicitly provisional. Signals that should reopen it with
the product owner:

- A threat-model change that makes unsandboxed renderers unacceptable —
  e.g. leaning on Open VSX extensions from unvetted publishers as a
  normal workflow, or capsules routinely holding credentials whose blast
  radius exceeds the checkout.
- Route 1 becoming cheap: a base/kernel combination where unprivileged
  user namespaces are already permitted, making sandboxing a
  template-data change.
- Upstream Electron/Chromium refusing to run `--no-sandbox`.

## Boundaries

- The JetBrains surface is unchanged: JCEF's sandbox was disabled before
  either ruling, through IDE properties, with its own disclosure.
- Docker's outer isolation is the load-bearing boundary in every posture
  and is unchanged by this ruling.
