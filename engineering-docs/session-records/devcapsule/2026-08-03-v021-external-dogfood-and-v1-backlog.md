---
date: 2026-08-03
capture-mode: detailed
requested-by: user
scope: DevCapsule v021 external dogfood, V1 product decisions, and backlog
related:
  - CURRENT-STATUS.md
  - .devcapsule/devcapsule.linux-amd64.lock
  - engineering-docs/implementation-notes/devcapsule/2026-08-03-next-functional-dogfood-stage-plan.md
  - engineering-docs/bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md
  - engineering-docs/bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md
  - engineering-docs/bugs/devcapsule/2026-08-03-jcef-sandbox-container-preview.md
  - engineering-docs/bugs/devcapsule/2026-08-03-jbr-slow-x11-alpha-compositing.md
  - engineering-docs/bugs/devcapsule/2026-08-03-jetbrains-native-launcher.md
  - engineering-docs/bugs/devcapsule/2026-08-03-codex-acp-missing-home.md
---

# Session Record: v021 External Dogfood And V1 Backlog

This is a detailed, sanitized, agent-authored reconstruction of the working
session. It is not a verbatim transcript. Transient container identifiers,
personal identity values, and bulky logs were omitted; stable artifact
identities and representative diagnostic lines were retained where they are
needed to resume the work.

## Why This Session Mattered

The session moved the capability-first DevCapsule workflow from repository
tests into a second real checkout. The external checkout successfully used
`devcapsule project run` to realize and launch a v021-backed PyCharm
environment alongside the established v018 dogfood capsule.

The product owner found the new command substantially more comfortable than
the historical launcher and reported being almost ready to move active
development to the new checkout. This is strong product evidence, but not yet
final acceptance of the complete next dogfood stage: several runtime effects
and onboarding details remain open.

## Starting State

The active branch was `wip/local-pycharm-materialization`. Stages 0 through 2
of the active dogfood plan had already implemented:

- initializing configuration inspection and interactive acceptance of exact
  recommendations;
- shared canonical environment realization for `images build` and
  `project run`; and
- generation and external read-only delivery of a checkout runtime plan while
  preserving the image's generic PEX entrypoint.

The published v021 base was available as discovery tag
`mycodespaceai/devcapsule-base:ubuntu-24.04-v021` and immutable digest:

```text
sha256:cd1a0e713e515234ef438c0502786353ec1678d2efd67b61a0bae6baf9fdc51e
```

Inspection confirmed managed metadata version 1, base recipe version 2,
`ready` status, embedded PEX checksum, and source revision:

```text
5401ce3506c0a8a63bfef40f4f9ef18d2b987436
```

## Selecting v021 Correctly

The product owner first reported that `config authorize --all-recommended`
selected the old v019 digest. The important model was clarified:
`--all-recommended` accepts the exact value in the checkout's committed
platform lock; it does not choose a tag or discover the newest image.

The active branch lock and documentation were changed to v021 and committed:

```text
c4060d3 Select v021 dogfood base
```

The fast Nox gate passed against that committed revision with 161 tests and
80% aggregate coverage. An isolated `project config list` showed v021's exact
digest as the missing required base-image authorization.

The external clone nevertheless continued to show v019. Read-only inspection
through the host Docker daemon found that it was clean but still on `main` at
`a8a2f04`, whose committed lock selected v019. The v021 commit existed on
`origin/wip/local-pycharm-materialization`; it had not been applied to `main`.

The external checkout at the developer's existing second-clone path was
switched to a new local tracking branch for
`origin/wip/local-pycharm-materialization`. Verification then showed clean
HEAD `c4060d3` and the v021 digest in its committed lock. This corrected the
checkout/revision mismatch rather than overriding the developer-owned
authorization machinery.

## External Launch Result

The external checkout refreshed its recommendations, resolved its developer
configuration, realized canonical PyCharm 2026.2.0.1 environment
`devcapsule-local-pycharm:a996cbcd72a7db5e8081`, and launched successfully.
For part of the session it ran in parallel with the original v018 capsule,
which allowed direct comparison without modifying the original environment.

The new launch demonstrated that the v019 runtime mismatch—previously reported
as `JetBrains config mapping must name a declared state slot`—was not a Stage 2
runtime-plan serialization defect. The v021 PEX understands the namespaced
`pycharm/...` state slots and reached a usable IDE session.

The new container later exited and was automatically removed during the JCEF
setting/restart investigation. No claim was made that every Stage 3 or Stage 4
acceptance check had passed.

## Dogfood Finding 1: Node.js/npm Are Installed But Not Usable

The product owner reported that `node` and `npm` were absent from `PATH` in
both the new and established dogfood capsules, although earlier image
iterations had exposed them.

Inspection of v021 showed that the intended pinned tooling is present:

```text
/opt/node/current -> /opt/node/node-v22.23.1-linux-x64
/opt/node/current/bin/node --version -> v22.23.1
```

The runtime path was only the ordinary system directories. `command -v node`
and `command -v npm` returned nothing; even invoking npm by absolute path
failed because its `env node` interpreter could not resolve Node.

The accepted V1 backlog direction is generic, metadata-driven runtime
environment contribution. A selected base tool or worry-free add-on declares
ordered, validated container directories to add to `PATH`; the contribution
participates in formation identity and is applied by the generic runtime.
Node-specific launcher logic was explicitly rejected.

Canonical record:
[`2026-08-03-component-tooling-runtime-path.md`](../../bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md).

## Dogfood Finding 2: Fresh Checkouts Need Ecosystem-Aware Bootstrap

The new checkout was not immediately ready for its normal Python workflow. The
developer manually created `.venv`, activated it, and installed dependencies.
That is too much assumed ecosystem knowledge for the intended clone-and-run
experience.

The product owner and agent agreed that automation must differ across Python,
Java, Node.js, and other ecosystems rather than hiding Python commands behind
a generic name. The proposed V1 contract uses curated, versioned ecosystem
adapters selected during resolution. Bootstrap is inspectable, idempotent,
checkout-scoped, safely retryable, and configures the IDE/runtime so manual
activation is unnecessary.

Dependency installation and build initialization can execute project code, so
the first exact bootstrap plan requires explicit developer consent and does
not imply Docker, sudo, credential, network-namespace, or host-filesystem
authorization. Ambiguous repository shapes must request a choice instead of
guessing an arbitrary command.

This project-environment bootstrap is distinct from the existing command that
bootstraps reusable human/agent workflow documentation.

Canonical record:
[`2026-08-03-ecosystem-aware-project-bootstrap.md`](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md).

## Dogfood Finding 3: JCEF Markdown Preview Is Suspended

PyCharm displayed `Embedded Browser is suspended` for Markdown preview and
offered to install an AppArmor profile. Web research and live diagnostics
established the full chain:

- current Markdown preview uses Chromium-based JCEF;
- current JCEF wants an unprivileged user namespace for its inner Chromium
  sandbox;
- Ubuntu 24.04 uses AppArmor to restrict unprivileged user namespaces and
  JetBrains documents a per-binary `userns` profile;
- loading `/etc/apparmor.d` policy is a host-kernel operation and JetBrains'
  desktop installer is inappropriate inside an ordinary container;
- the dogfood host's immediate denial was Docker's default seccomp profile,
  not the Ubuntu-specific AppArmor sysctl JetBrains assumed; and
- the IDE log recorded `unshare failed: Operation not permitted`, then the
  in-container profile installation failed because JetBrains could not invoke
  a suitable privilege utility.

Controlled disposable-container probes showed:

- Docker default: user-namespace `unshare` denied;
- `seccomp=unconfined`: probe succeeded;
- `apparmor=unconfined` alone: still denied; and
- `SYS_ADMIN`: probe succeeded but was far broader than the feature warrants.

The PyCharm log also showed an upgrade from CEF major version 137 to 144 and
recorded JetBrains' fallback changing
`ide.browser.jcef.sandbox.enable=false`, followed by a noisy IDE restart.

### Accepted V1 Decision

The product owner decided that V1 will intentionally run the in-container JCEF
embedded browser without its inner sandbox. The rationale is that developers
already choose to execute more powerful project dependency and build logic;
embedded preview content is not treated as a stronger trust boundary for the
target V1 workflow.

This is a disclosed product tradeoff, not a claim of zero risk. User-facing
guidance must state that embedded content inherits the IDE user's project,
state, network, and separately authorized capabilities, including the host
Docker socket when granted. The embedded browser should not be advertised as a
general-purpose browser for untrusted sites.

Implementation must set the JCEF registry/property choice before IDE startup
so no user must follow the misleading AppArmor prompt. The outer Docker
security boundary remains unchanged: no ambient `SYS_ADMIN`, privileged mode,
unconfined seccomp/AppArmor, or in-container attempt to load host policy.
Sandboxed JCEF remains later hardening rather than a V1 blocker.

Canonical record and research links:
[`2026-08-03-jcef-sandbox-container-preview.md`](../../bugs/devcapsule/2026-08-03-jcef-sandbox-container-preview.md).

## Dogfood Finding 4: Development-Sudo Authorization Has No Runtime Policy

The external resolved TOML correctly contained:

```toml
[authorization]
development-sudo = true
```

Nevertheless, every `sudo` command prompted for a password. Inspection showed
that configuration and authorization work as designed, while runtime
activation is incomplete:

- v021 contains `/usr/bin/sudo` but no `NOPASSWD` entry under
  `/etc/sudoers.d`;
- the launcher turns the authorization into `ENABLE_SUDO=1` and supplementary
  group `44000`; and
- the generic PEX runtime does not consume that legacy environment flag or
  create a policy.

This is the already planned Stage 4 gap, not a new duplicate bug. Stage 4 must
generate a temporary narrow sudoers policy only when authorized, mount it
read-only, clean it after exit/failure, prove `sudo -n true` positively, and
prove no passwordless sudo without authorization. The base does not need to be
rebuilt for this change.

Canonical plan:
[`2026-08-03-next-functional-dogfood-stage-plan.md`](../../implementation-notes/devcapsule/2026-08-03-next-functional-dogfood-stage-plan.md).

## Dogfood Finding 5: JetBrains Runtime Slow-X11 Warning

The launch printed:

```text
[JetBrains Runtime] Detected slow X11, switched off alpha compositing of images.
Control with -Dremote.x11.workaround={true|false|auto}.
```

No visual or performance defect accompanied the warning. Containerized X11,
software Mesa rendering, and the no-MIT-SHM compatibility setting can
reasonably trigger JetBrains Runtime's heuristic. This is a low-priority review
and not currently a V1 blocker.

The chosen stance is to retain `auto` until a controlled comparison of all
three values demonstrates a user-visible reason to override it. The warning
must not be hidden merely for cleaner logs.

Canonical record:
[`2026-08-03-jbr-slow-x11-alpha-compositing.md`](../../bugs/devcapsule/2026-08-03-jbr-slow-x11-alpha-compositing.md).

## Dogfood Finding 6: PyCharm Prefers Its Native Launcher

PyCharm warned that it was started through `bin/pycharm.sh` and recommended
`bin/pycharm`. Inspection confirmed:

- the pinned archive's `product-info.json` declares `bin/pycharm`;
- the native executable is present as an x86-64 ELF binary; and
- DevCapsule materialization and tests deliberately require and select
  `bin/pycharm.sh`.

This is another low-priority review rather than a proven functional defect.
Any switch must preserve foreground ownership below `tini`, signal and exit
behavior, IDE restart, project argument handling, runtime properties,
automatic container removal, and canonical formation identity. It should use
validated component metadata rather than another launcher override.

Canonical record:
[`2026-08-03-jetbrains-native-launcher.md`](../../bugs/devcapsule/2026-08-03-jetbrains-native-launcher.md).

## Dogfood Finding 7: Codex ACP Rejects A Missing Explicit Home

JetBrains AI Assistant accepted and successfully tested the developer's OpenAI
API-key configuration, but Codex conversation startup failed because the local
ACP process exited before connecting. The exact error said that
`CODEX_HOME=/home/devcapsule/.codex` was explicitly selected but did not exist.

The current OpenAI Codex manual confirms that `CODEX_HOME` defaults to
`~/.codex` and that an explicitly set directory must already exist. DevCapsule
unconditionally adds that environment variable in the PyCharm Docker plan,
while its generic agent-neutral runtime creates only universal home/XDG/state
directories. Inspection confirmed the fresh persistent home had no `.codex`.

JetBrains' logs also proved this is separate from the missing system Node path:
AI Assistant provisioned managed Node.js `24.13.0`, prepended it for the ACP
process, and launched `@agentclientprotocol/codex-acp@1.1.9` before Codex
rejected the state-root override.

The preferred fix is to remove DevCapsule's ambient `CODEX_HOME` variable and
preserve `HOME=/home/devcapsule`, allowing Codex to use its documented default
under persistent home. Generic runtime must not gain an agent-specific
directory. A future explicitly selected Codex component may declare and create
a custom path without mounting host agent state.

For the current external revision, creating `$CODEX_HOME` mode `0700` inside
the running capsule is a safe persistent-home workaround before retrying ACP.
The product owner applied that workaround and confirmed that Codex ACP then
worked, manually validating the diagnosis.

Canonical record and official source:
[`2026-08-03-codex-acp-missing-home.md`](../../bugs/devcapsule/2026-08-03-codex-acp-missing-home.md).

### Installed Codex Stack License Verification

After the successful workaround, the product owner asked whether the
JetBrains-installed Codex stack was Apache 2.0 as stated by the GUI prompt.
Inspection of the exact installed package manifests and license files
confirmed:

- JetBrains `@agentclientprotocol/codex-acp` 1.1.9: `Apache-2.0`, with an
  Apache 2.0 LICENSE naming JetBrains as copyright holder;
- `@agentclientprotocol/sdk` 1.3.0: `Apache-2.0`;
- OpenAI `@openai/codex` 0.145.0: `Apache-2.0`; and
- the resolved OpenAI Linux x64 Codex package: `Apache-2.0`.

OpenAI's current manual identifies Codex CLI as an open-source component, and
the official `openai/codex` repository carries the Apache License 2.0. The GUI
statement was therefore accurate for the local ACP/Codex software inspected.

The conclusion is artifact-specific. It does not make JetBrains AI Assistant,
OpenAI's hosted models/API service, or every transitive npm dependency subject
to Apache 2.0. If DevCapsule later redistributes Codex as an optional
component, it must still pin and checksum artifacts, inventory all dependency
licenses, preserve required LICENSE/NOTICE material, and disclose separate
service/authentication terms.

Official references:

- [OpenAI Codex open-source components](https://learn.chatgpt.com/docs/open-source)
- [OpenAI Codex repository license](https://github.com/openai/codex/blob/main/LICENSE)

## Repository Changes During The Session

Committed checkpoint:

- `c4060d3` — select the immutable v021 dogfood base and update current
  dogfood documentation.

Uncommitted documentation/backlog work at session-record creation:

- updated `CURRENT-STATUS.md` with all external evidence and decisions;
- corrected `devcapsule-src/README.md` so it no longer claims authorized sudo is
  already effective;
- marked Stage 4 externally reproduced in the active dogfood plan;
- added the six canonical finding/review records linked above; and
- updated `index.md` for every added Markdown file, including this record.

No implementation code was changed while recording the external findings.
Documentation validation used `git diff --check` throughout.

## Rejected Or Deferred Alternatives

- Do not make Node/npm available through a hard-coded PyCharm launcher path;
  use generic selected-component runtime metadata.
- Do not treat all project bootstrap as Python virtual-environment setup; use
  ecosystem-specific adapters.
- Do not install host AppArmor policy from the IDE container.
- Do not grant `SYS_ADMIN`, privileged mode, or unconfined security profiles
  merely to satisfy JCEF.
- For V1, do not block the working embedded preview on a sandboxed-JCEF host
  integration; disclose and intentionally disable only JCEF's inner sandbox.
- Do not override JetBrains Runtime's slow-X11 `auto` heuristic without a
  visible problem and controlled comparison.
- Do not switch to the native PyCharm launcher without proving container
  foreground/restart/signal behavior.

## Handoff State And Next Steps

1. Commit the coherent documentation/backlog/session-record checkpoint before
   moving active work to the external checkout.
2. Update that checkout to the new commit so it carries the same canonical
   status and V1 backlog as this source tree.
3. Continue the active dogfood plan at Stage 3: inspect and close the remaining
   explicit runtime effects and negative authorization behavior.
4. Implement Stage 4's authorized temporary sudoers policy; this is the clearest
   externally reproduced functional gap in the current run path.
5. Implement the accepted V1 unsandboxed-JCEF component/runtime setting and
   disclosure without weakening Docker's outer isolation.
6. Prioritize generic component `PATH` metadata and ecosystem bootstrap for
   the clone-and-run V1 experience.
7. Review the X11 heuristic and native PyCharm launcher later unless a visible
   defect promotes either item.
8. Remove the unconditional `CODEX_HOME`, then prove one real Codex ACP
   exchange and persistent second launch without a host agent-state mount.
9. Rerun the clean committed gate and the aligned second-checkout dogfood
   script before declaring the next functional stage complete.

The product signal at handoff is positive: `devcapsule project run` is already
materially easier to start and use than the historical dogfood launcher. The
remaining work is now concrete runtime completion, onboarding automation, and
transparent documentation rather than uncertainty about the core workflow.
