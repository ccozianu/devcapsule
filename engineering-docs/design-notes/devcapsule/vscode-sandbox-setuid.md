# The VS Code-Family Setuid Sandbox Helper

**Superseded 2026-09-02** by the product owner's ruling in
[renderer-sandboxing.md](renderer-sandboxing.md): shipped surfaces run
`--no-sandbox` under full container hardening, and the narrow grant, the
`setuid-helper` declaration, and the recipe's 4755 step described below
are removed. The
[2026-09-02 sudo-sandbox bug](../../bugs/devcapsule/2026-09-02-codium-setuid-sandbox-crashes-under-development-sudo.md)
falsified this note's development-sudo boundary paragraph and prompted
the reversal. The analysis below is kept as the record of the 2026-08-31
ruling and of what the setuid route entails if it ever returns.

Ruled 2026-08-31 by the product owner during the `component-catalog`
workstream, after a live launch surfaced the collision described below: the
codium surface keeps Chromium's setuid renderer sandbox, and the host
launcher narrows the capsule's hardening exactly enough to let the helper
work.

## The Problem

Chromium-based applications isolate renderer processes — the ones parsing
untrusted web content, extension code, and Markdown previews — inside a
sandbox. On Linux the preferred mechanism is unprivileged user namespaces,
which a capsule's seccomp confinement denies; Chromium then falls back to a
small setuid-root helper (`chrome-sandbox`, root-owned, mode `4755`) that
creates the isolation namespaces with privilege and immediately drops it.
Without either mechanism the application only runs with `--no-sandbox`.

The first live launch showed the two protections collide. DevCapsule's
default capsule hardening is `--cap-drop ALL --security-opt
no-new-privileges`, and under it the setuid helper is inert twice over:
`no-new-privileges` vetoes the setuid transition itself, and an empty
capability bounding set leaves even a uid-0 helper unable to chroot or
create namespaces. The real choice is therefore:

1. **Setuid helper with a narrow capability grant** (chosen): keep the
   renderer sandbox; run the capsule without `no-new-privileges` and with
   `--cap-drop ALL` plus exactly `CAP_SETUID`, `CAP_SETGID`,
   `CAP_SYS_ADMIN`, and `CAP_SYS_CHROOT` added back.
2. **`--no-sandbox` under full hardening**: keep `--cap-drop ALL
   --security-opt no-new-privileges`; renderers run unsandboxed with the
   developer's full container privileges. (Verified working in the same
   live test before the ruling.)

## The Trade-Off

Choosing 1 accepts container-level exposure to keep process-level defense:

- Cost: any capsule process can invoke the setuid helper, and the granted
  bounding capabilities — `CAP_SYS_ADMIN` in particular — are meaningful
  kernel attack surface if a process reaches uid 0 through the helper. The
  grant is bounded: the helper is Chromium's purpose-built, audited
  privilege-drop bootstrap, it ships pinned inside the checksum-verified
  VSCodium archive, the materialization recipe never patches it, and the
  four capabilities are a bounding set, not ambient — non-root processes
  still hold no capabilities.
- Benefit: renderer processes executing untrusted project content and
  third-party Open VSX extensions stay namespace-isolated from the mounted
  checkout and the developer's credentials inside the capsule — exactly
  where DevCapsule's threat model cares most.

Choosing 2 would have kept the stricter container posture and given every
renderer the developer's full capsule privileges. The owner weighed
renderer-level isolation above the capability-surface cost.

Docker's outer isolation is unchanged either way, and the launch prints a
disclosure naming the granted capabilities whenever the grant is active.

## Mechanics

- The codium component declares `sandbox = "setuid-helper"` in its runtime
  configuration; the host launcher keys the capability grant on that
  declaration, so surfaces that do not declare it keep full hardening.
- The materialization recipe makes `chrome-sandbox` root-owned mode `4755`
  in the canonical image — the retired `codium_with_claude` image build did
  the same, so the binary-level configuration is proven in use.
- Development-sudo launches already run without this hardening; the grant
  only changes the default (no-sudo) posture for declaring surfaces.

## Boundaries

- The JetBrains surface is unaffected; its JCEF browser sandbox is disabled
  through IDE properties, a decision that predates this note, and its
  capsules keep `--cap-drop ALL --security-opt no-new-privileges`.
- If a future base image enables unprivileged user namespaces inside
  capsules, Chromium prefers them automatically; the setuid bit becomes
  inert and the capability grant can be retired with a recipe-version bump.
