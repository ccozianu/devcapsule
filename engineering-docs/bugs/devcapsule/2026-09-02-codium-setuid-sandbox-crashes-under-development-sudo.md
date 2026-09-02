# Bug: The Codium Setuid Sandbox Crashes Under The Development-Sudo Posture

Date opened: 2026-09-02

Status: fixed on the branch 2026-09-02, by ruling rather than by either
option in the fix scope below — the owner superseded the 2026-08-31
sandbox ruling entirely: renderers run `--no-sandbox` under uniform full
hardening for as long as we can, recorded in the
[renderer-sandboxing design note](../../design-notes/devcapsule/renderer-sandboxing.md).
The setuid helper, the narrow grant, and the recipe's 4755 step are
removed (codium recipe version 2, matrix `embedded-5`), so no posture
exists in which the helper can crash. Regression test:
`test_sudo_launches_grant_no_capabilities_beyond_dockers_default`.
Closes on the owner's next sudo-enabled relaunch (the rebuild also
first-exercises the widened `~/.gemini` slot from the antigravity-state
record). Diagnosis had been confirmed by the product owner's A/B the
same day (sudo posture crashes at surface start; the hand-forced
no-sudo posture launches with the narrow-grant disclosure printed).

Requirements: R-PRODUCT-001, R-PRODUCT-002

Related: the
[setuid sandbox design note](../../design-notes/devcapsule/vscode-sandbox-setuid.md)
(this bug falsifies its development-sudo boundary paragraph);
`2026-09-02-authorization-grammar-cannot-expressF-denial.md` (found
while trying to downgrade out of this crash — the owner ultimately had
to hand-edit the generated resolution to express the no-sudo posture).

## Symptom

The first codium launch with development sudo enabled (the v0.2.9
antigravity smoke, `init --regenerate` adding `antigravity-agent`)
dies at surface start:

```
Failed to move to new namespace: PID namespaces supported, Network namespace supported, but failed: errno = Operation not permitted
[34:0902/145321.838093:FATAL:content/browser/zygote_host/zygote_host_impl_linux.cc:207] Check failed: . : Invalid argument (22)
```

The message reads like a component-installation failure but is
Chromium's *setuid sandbox helper* (`chrome-sandbox`, root via its
4755 bit) failing `clone(CLONE_NEWPID|CLONE_NEWNET)`, and the zygote
host aborting when the helper dies. Antigravity is uninvolved: its
role was making this the first codium × sudo launch.

## Mechanism (code-read and empirically verified 2026-09-02)

`append_sudo_or_restrictions` (`configurations/pycharm/_launcher.py`)
has three postures:

- no-sudo + `sandbox = "setuid-helper"` surface: `--cap-drop ALL` plus
  CAP_SETUID, CAP_SETGID, **CAP_SYS_ADMIN**, CAP_SYS_CHROOT — the
  2026-08-31 narrow grant; the helper works.
- no-sudo, other surfaces: full hardening (`--cap-drop ALL
  --security-opt no-new-privileges`).
- **sudo: `--group-add` only — Docker's default capability set.** That
  set contains SETUID, SETGID, and SYS_CHROOT but **not SYS_ADMIN**,
  and no-new-privileges is absent. The helper is therefore privileged
  enough to *start* (the setuid transition succeeds) but not to
  *sandbox* (namespace creation needs CAP_SYS_ADMIN in the bounding
  set) — the worst of both postures, and precisely the printed error.

Verified against the canonical codium image: as uid 0 with Docker's
default capabilities, `unshare --pid --net` fails EPERM; under the
narrow grant it succeeds. `chrome-sandbox` in the image is correctly
root-owned mode 4755, so materialization is not implicated. The
`dind` mode (`--privileged`) is unaffected.

The design note's boundary paragraph — "Development-sudo launches
already run without this hardening" — assumed the sudo posture was at
least as capable as the grant. It is not: the sudo posture and the
narrow grant are incomparable sets, and the helper needs a capability
only the grant carries.

## Expected

A surface that declares the setuid helper launches under every
supported posture; enabling development sudo must not silently break
the renderer sandbox harder than the hardened default.

## Fix Scope (amends the 2026-08-31 ruling, so the owner decides)

1. Preferred: when `enable_sudo` and the surface declares
   `setuid-helper`, keep the sudo posture and add
   `--cap-add SYS_ADMIN`. The resulting bounding set is a strict
   superset of the already-accepted narrow grant, and sudo launches
   deliberately trade hardening for administration. (The alternative —
   narrow grant plus sudo group — would leave sudo'd root four
   bounding capabilities and break development administration.)
2. Correct the design note's development-sudo paragraph to describe
   the chosen posture.
3. Regression test: the rendered docker args for a sudo +
   setuid-helper launch include SYS_ADMIN (or whatever posture is
   ruled), alongside the existing narrow-grant coverage.

## Reproducibility

Always: any codium-surface launch with development sudo enabled and
docker mode other than `dind`.

## Verification Target

(Updated for the 2026-09-02 ruling; the original target assumed a
sandboxed-renderer fix.)

- Automated test:
  `test_sudo_launches_grant_no_capabilities_beyond_dockers_default` —
  sudo launches compose Docker's default capability set plus the sudo
  group, with no per-surface capability grants.
- Manual validation: the failing smoke checkout, sudo re-enabled,
  launches codium cleanly where the zygote previously aborted; the
  unsandboxed-renderer disclosure prints.
