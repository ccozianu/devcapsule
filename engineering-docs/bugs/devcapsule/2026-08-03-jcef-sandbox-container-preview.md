# Bug: JetBrains Embedded Browser Is Suspended In The Container

Date opened: 2026-08-03

Status: V1 workaround implemented and automated; external GUI validation pending

Requirements: R-ENV-001, R-DEV-001, R-SCOPE-001, R-DOCKER-001

## Symptom

In the v021-backed PyCharm 2026.2.0.1 dogfood environment, Markdown preview is
replaced by:

```text
Embedded Browser is suspended
```

The **Enable Browser…** action explains that an AppArmor profile must be
installed. Its installation action fails inside the container, and its other
offered action disables the Chromium/JCEF sandbox and restarts the IDE.

This is distinct from the retired Skiko/OpenGL Markdown-preview issue. The
current failure happens before JCEF rendering because JetBrains refuses to
start its sandboxed Chromium processes.

## What Changed And Why

PyCharm's Markdown preview uses the Chromium-based JetBrains Chromium Embedded
Framework (JCEF). Chromium separates renderers, network handling, and utility
work into restricted processes; on Linux, JetBrains' current sandbox path
requires an unprivileged user namespace.

Ubuntu introduced AppArmor-mediated restrictions for unprivileged user
namespaces and enabled them by default in Ubuntu 24.04. JetBrains responded by
failing closed when its user-namespace probe fails. Its documented desktop
choices are:

1. install a per-Java-binary AppArmor profile granting `userns` (recommended);
   or
2. set `ide.browser.jcef.sandbox.enable=false` and run JCEF unsandboxed.

That desktop guidance is not container-aware. AppArmor is enforced and loaded
by the host kernel. Writing `/etc/apparmor.d` inside an ordinary container and
running `apparmor_parser` there is neither sufficient nor an acceptable
implicit host-policy change.

The upgrade plausibly exposed the issue: the persistent log records PyCharm
2026.2.0.1 build `PY-262.8665.369` and a JCEF/CEF update from major version 137
to 144. The root cause in this environment, however, is the container security
boundary rather than a missing Markdown plugin.

## Accepted V1 Product Direction

On 2026-08-03, the product owner selected an unsandboxed embedded browser for
V1. DevCapsule will intentionally disable the JCEF sandbox inside the
container so Markdown and other embedded previews work without host AppArmor
installation, extra namespace privileges, or relaxed Docker seccomp policy.

The accepted rationale is that the V1 developer already chooses to execute
substantially more powerful project-controlled code, including dependency
installation and build logic from a cloned repository. Embedded preview
content is not treated as a stronger trust boundary than that project code for
the target V1 workflow. This is a deliberate product tradeoff, not a claim
that unsandboxed HTML or JCEF is risk-free.

The choice applies only to JetBrains' in-container embedded browser. It does
not justify weakening Docker's seccomp/AppArmor profile, adding capabilities,
running the container privileged, disabling isolation for a host browser, or
silently broadening any project authorization.

## Live Evidence

The v021 dogfood log records:

```text
JCEF-sandbox is enabled
Unprivileged user namespaces check failed:
unshare: unshare failed: Operation not permitted
```

The same log shows the AppArmor installation action failing:

```text
Cannot `sudo` on this system - no suitable utils found
at com.intellij.ui.jcef.JBCefAppArmorUtils.installAppArmorProfile(...)
```

It also shows the fallback changing persistent IDE configuration and
restarting:

```text
Registry value 'ide.browser.jcef.sandbox.enable' has changed to 'false'
```

That restart emitted additional JetBrains disposal/threading errors. After
restart, JCEF starts without logging that its sandbox is enabled.

Host/container probing narrows the immediate denial:

- AppArmor is enabled on the host kernel;
- the Ubuntu-specific
  `/proc/sys/kernel/apparmor_restrict_unprivileged_userns` control is absent on
  this host;
- an unprivileged `unshare -Ur true` fails under Docker's default security
  profile;
- the same probe succeeds with `--security-opt seccomp=unconfined`;
- `--security-opt apparmor=unconfined` alone does not change the failure; and
- `--cap-add SYS_ADMIN` also permits it, but is far broader than this feature
  should require.

Docker's official seccomp documentation confirms that its default allowlist
blocks `unshare`/new-namespace operations. JetBrains treats the resulting
generic `EPERM` as the Ubuntu AppArmor case and presents the wrong remedy for
this container.

## Security Impact

Silently disabling the JCEF sandbox is not a harmless UI preference. Embedded
web content and preview rendering then run with the full authority of the IDE
user, including access to project source, persistent state, and every
separately authorized capability. In dogfood, that may include the host Docker
socket, which can confer broad host control.

For V1, the product owner accepts that exposure in exchange for a working
preview and a simpler portable container contract. DevCapsule must disclose
it prominently enough that developers understand the embedded browser is not
sandboxed and should not use it as a general-purpose browser for untrusted
sites or content.

The accepted choice still must not add `SYS_ADMIN`, use
`seccomp=unconfined`/`apparmor=unconfined`, run a privileged container, or
install a host AppArmor policy. Those broad workarounds weaken additional
security boundaries without benefit once JCEF sandboxing is deliberately off.

## Implemented V1 Direction

1. Set `ide.browser.jcef.sandbox.enable=false` deterministically through the
   PyCharm component/runtime contract before JCEF initializes. Do not depend
   on a developer clicking JetBrains' fallback or mutating persistent settings
   by hand.
2. Keep Docker's existing seccomp and AppArmor profiles, capabilities, and
   privilege mode unchanged. Disabling JCEF's inner sandbox is the complete V1
   compatibility choice, not a reason to relax the outer container boundary.
3. Expose the effective choice in inspectable component/runtime metadata and
   configuration status so it cannot be mistaken for JetBrains' default.
4. Print a concise first-run or launch disclosure and document the choice in
   current user-facing security/runtime guidance. State that embedded content
   inherits project, persistent-state, network, and separately authorized
   socket access.
5. Avoid the misleading AppArmor installation prompt by applying the setting
   before the IDE probes user namespaces.
6. Keep a sandboxed JCEF mode as later hardening work rather than a V1 blocker.
   A future mode must solve Docker seccomp and host AppArmor requirements
   explicitly and must not change the documented V1 behavior retroactively.

The PyCharm component now declares the policy twice through one trusted
component contract: as the generated JetBrains property
`ide.browser.jcef.sandbox.enable=false`, and as the JVM startup option
`-Dide.browser.jcef.sandbox.enable=false`. The latter preserves compatibility
with v021's embedded runtime parser, while newer runtimes also write the
property into the generated PyCharm properties file before launching the IDE.
The launcher prints an explicit security disclosure. No capability, privileged
mode, host mount, AppArmor override, or seccomp override was added.

The combined dirty-tree full Nox gate passed with clean Python and shell
compilation, clean mypy over 73 source files, 171 fast tests at 80%
statement/branch coverage, source and local-PEX command smokes, PEX
construction, and all three packaging integrations. External GUI validation
remains open because the automated gate does not launch the real IDE.

## Verification Target

1. Component/runtime tests prove the V1 PyCharm plan explicitly disables JCEF
   sandboxing before IDE startup.
2. Docker command-plan tests prove the change adds no capability, privilege,
   host mount, AppArmor override, or seccomp override.
3. Inspection and user documentation disclose the unsandboxed embedded
   browser and its effective project/state/network/authorized-socket access.
4. PyCharm/JCEF logs no longer show the suspension or AppArmor installation
   prompt, and they show the sandbox-disabled setting as intentional.
5. Markdown and SVG preview render in the external dogfood capsule, including
   after a fresh configuration rather than only after persisted UI state.
6. Tests prove unrelated IDE configuration remains persistent and that the
   compatibility setting does not silently disable any outer container
   isolation.

## Close Criteria

Close this item when DevCapsule intentionally configures the V1 PyCharm
component with an unsandboxed JCEF browser before startup; users can inspect
and are warned about that choice; no outer container security relaxation is
added; and Markdown/SVG preview passes in a fresh external dogfood capsule.

Reopen if an IDE update suspends JCEF again, if enabling preview requires the
user to follow JetBrains' in-container AppArmor prompt, if the unsandboxed
state becomes hidden or undocumented, or if the implementation broadly
unconfines the container in addition to disabling JCEF's inner sandbox.

## Research Sources

- [JetBrains: Restricted unprivileged user namespaces / Embedded Browser is suspended](https://youtrack.jetbrains.com/articles/JBR-A-11)
- [Ubuntu: Restricted unprivileged user namespaces](https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces)
- [Ubuntu 24.04 LTS release notes: unprivileged user namespace restrictions](https://discourse.ubuntu.com/t/ubuntu-24-04-lts-noble-numbat-release-notes/39890#unprivileged-user-namespace-restrictions-15)
- [Docker: Seccomp security profiles for Docker](https://docs.docker.com/engine/security/seccomp/)
