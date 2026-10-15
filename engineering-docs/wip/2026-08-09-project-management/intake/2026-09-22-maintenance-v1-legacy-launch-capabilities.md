# Owner-directed V1 gate: legacy launch capability decisions

From: maintenance
To: project-management
Date: 2026-09-22

The owner explicitly requested a future-release work item blocking V1 that
preserves the capabilities potentially lost by retiring pycharm run. This is
an owner-assigned gate, not a priority or release target invented by the sender.

Please acknowledge it into your V1 scope ledger and scheduling. Assign the
implementation workstream(s) when selected work starts; maintenance remains
on release-0.2.14 and is not reopening another workstream. The owner says we
are currently our only users and everyday dogfood already uses project run.

Acceptance of this handoff means tracking the mandatory per-capability product
decisions, the unresolved project-run versus image-run versus drop choice,
and delivery/acceptance for the selected V1 scope. No image-run command is
approved, no blanket feature parity is required, and no current-release
implementation is added. Do not request the owner to restate this V1 gate.

Canonical work item, being delivered on release-0.2.14:
engineering-docs/work-orders/2026-09-22-legacy-launch-capability-disposition.md

Full work item below so scheduling does not wait for release-branch integration.

---

# Work Item: Decide The Future Of Legacy Launch Capabilities Before V1

Status: open; product decisions and resulting implementation pending.
Created: 2026-09-22, at the product owner's explicit direction.
Release gate: **blocks V1**; schedule in future release work, not as a new
0.2.14 implementation commitment.
Coordination owner: `project-management`; implementation workstream(s) to be
assigned when the chosen work is scheduled. Prepared by `maintenance`.

## Required Outcome And Owner Direction

Before V1, decide which user capabilities exposed by legacy `pycharm run`
belong in the supported product, where they belong, and which should be
deliberately dropped. Implement and validate the capabilities selected for V1.
The decision itself is mandatory; retaining every legacy capability is not.

The owner reports that we are currently our only users and that everyday
dogfood has used plain `devcapsule project run` for a long time. Do not invent
an installed-user migration burden to justify preserving a second launch
interface. Evaluate usefulness to future adopters instead. Preserve the
inventory below so retirement does not silently erase potentially useful
product capabilities from consideration.

The owner explicitly leaves open whether selected capabilities should move
under `project run`, whether a separate **`image run`** should support a
directory with no DevCapsule configuration, or whether they should be dropped.
`image run` is illustrative spelling, not approved CLI grammar; the existing
image command family is `images`. Do not interpret this item as approval to
create a new command or automatically restore the retired `project run-image`.

This work item does not itself remove `pycharm run`. At the evidence revision
it remains present; the retirement implementation and release timing are
separate from preserving these future decisions. The shared launcher is still
used by modern project launch and must not be deleted with the legacy adapter.

## Evidence And Limits

Source inspected during 0.2.14 triage: RC0 `d078b87`; the runtime source is
unchanged at maintenance record commit `fbda246`. This is an implementation
inventory, not fresh end-to-end proof that every legacy option works.
Recheck the code and current requirements before implementation.

- [Legacy grammar and adapter](../../devcapsule-src/devcapsule/commands/_pycharm.py):
  `PycharmRunCommand.configure` and `run` expose and translate the old options.
- [Project launch](../../devcapsule-src/devcapsule/commands/project.py):
  `ProjectRunCommand` admits configuration, selects the environment, and
  calls `run_pycharm` directly with explicit effective options. It does not
  invoke `PycharmRunCommand`.
- [Shared launcher](../../devcapsule-src/devcapsule/launch/pycharm/_launcher.py):
  implements both callers' Docker planning and state preparation. Modern
  project launch sets `inherit_legacy_configuration=False`.
- [Configuration bindings](../../devcapsule-src/devcapsule/configuration/bindings.py)
  and [authorization](../../devcapsule-src/devcapsule/configuration/authorization.py)
  provide the modern state and host-access mechanisms.
- [Host daemon selection](../../devcapsule-src/devcapsule/host_daemon.py) and
  [current CLI documentation](../../devcapsule-src/README.md) supply additional
  evidence for socket selection, bindings and legacy examples.

A CLI probe replacing only `run_pycharm` confirmed that legacy `pycharm run`
passes `network_mode='host'` without an explicit network selection. Its option
type also defaults to host-X11 transport. Configured project launch supplies
reviewed choices instead. These are reasons to consolidate policy, not
capabilities that should be preserved as defaults.

## Capability Inventory To Decide

“No dedicated equivalent” below does not mean impossible through manual setup
or raw Docker options. Distinguish a supported, discoverable product feature
from an expert assembling it outside the resolved configuration.

| ID | User purpose and legacy surface | Current project path / actual retirement effect | Decision still needed |
|---|---|---|---|
| L1 | Open an arbitrary directory in a compatible prebuilt PyCharm image: `--project`, `--image`, without DevCapsule project metadata. | Project launch requires initialization/configuration and selects a materialized environment. Selecting a local **base** is not equivalent to launching any prebuilt final IDE image. This shortcut would disappear. Legacy compatibility with arbitrary OCI images is not established. | Require project initialization, add an explicit configured-image choice, offer an image-oriented launch, or drop this use case. Decide what image contract is supported. |
| L2 | Start a separate Docker daemon inside the capsule: `--docker-in-docker` / `--dind`. | Modern project launch selects host-socket or no daemon; it has no managed inner-daemon mode. This is a functional difference, not just a flag rename. It requires a suitable image/runtime and lifecycle behavior. | Is an isolated daemon useful enough to support? If so, define authorization, storage, startup/readiness, privilege requirements and cleanup in the project model. |
| L3 | Reuse a host SSH agent for repository access: `--ssh-agent`. | Project launch has no dedicated agent-forwarding control. Authentication inside persistent capsule state remains possible; manual socket mount/environment passthrough is not an equivalent first-class feature. | Support scoped, explicit forwarding through project configuration, another interface, or intentionally require capsule-local authentication. |
| L4 | Supply an HTTPS Git token through a host file or environment variable, with username/host restrictions: `--git-token-file`, `--git-token-env`, `--git-token-user`, `--git-token-host` and GitHub aliases. | Legacy adapter feeds the launcher's token/askpass helpers. Project component-secret bindings do not automatically provide this Git-specific interface. Existing agent API-key delivery is not Git-token delivery. | Decide whether to expose a Git credential contribution, use normal in-capsule credential tools, or drop the host injection convenience. Specify allowed hosts, lifetime, persistence and diagnostic redaction if retained. |
| L5 | Select commit identity or control host import per invocation: `--git-user-name`, `--git-user-email`, `--git-identity-from-host`, `--no-git-identity-from-host`. | Modern launch still reaches shared automatic Git identity import, and ordinary Git configuration remains available in the capsule. Dedicated per-launch overrides/import refusal are not exposed equivalently. Git identity and credential forwarding are separate concerns. | Decide whether explicit identity/import control belongs in developer configuration; do not claim basic Git use disappears. |
| L6 | Choose named profiles, shared/project/custom IDE state and explicit state roots: `--profile`, `--global-settings` / `--state`, `--home`, `--project-state`, `--project-state-root`, `--config-mode`, `--ide-config`, `--project-config`, `--shared-config`, `--plugins`. | Bindings already support `home` and PyCharm config/plugins/system/log/cache directories. Persistence and custom locations survive. The profile shorthand, automatic directory-layout conventions and one-shot switches do not have exact equivalents. | Are named reusable profiles a useful new-adopter abstraction, or are explicit bindings sufficient? Preserve concurrency and ownership semantics for shared IDE state. |
| L7 | Request native-debugging permissions with `--debug-native`. | Legacy switch adds ptrace/seccomp options. Project launch has raw Docker-option passthrough, so retirement removes a convenience/policy bundle rather than establishing that native debugging is impossible. | If supported, define the debugger need and explicit configuration contract; decide whether expert passthrough is adequate for V1. Verify the actual debugger, not just emitted flags. |
| L8 | Make the image root writable independently of other choices: `--writable-root`. | Modern development-sudo authorization already implies a writable root. There is no equivalent dedicated switch for writable-root-without-sudo; raw Docker options are a separate expert surface. | Is independent writability a supported need, a declared runtime choice, or intentionally outside the ordinary model? Do not conflate it with granting sudo. |
| L9 | Override project mount path with `--project-mount`. | Modern launch takes the project mount from project configuration. The capability survives; the per-launch spelling differs. | Confirm the existing declaration is sufficient; avoid duplicating it unnecessarily. |
| L10 | Use a non-default host Docker socket with `--docker-socket`. | Shared socket selection still supports `HOST_DOCKER_SOCKET` / Unix `DOCKER_HOST`; project authorization controls whether host-daemon access is granted. The dedicated legacy switch disappears. | Confirm discoverability and supported daemon configuration; a missing switch is not proof the capability is lost. |
| L11 | Bypass a stale IDE configuration-lock check with `--ignore-config-lock`. | Project launch does not expose that shortcut; its isolation/bindings and recovery path must be considered. | Prefer an actionable recovery story; retain a bypass only if an adopter scenario requires it and its concurrency contract is explicit. |
| L12 | Host daemon or no daemon, development sudo, browser integration, host-network/X11 choice, container naming and extra Docker arguments. | Modern project launch already exposes the relevant authorizations, `--name`, and arguments after `--`. Some launcher-owned Docker options are deliberately refused with a sanctioned alternative. Ambient host-network/X11 defaults are not required functionality. | Verify and document existing equivalents; preserve effective grants/denials. Do not duplicate legacy options or restore ambient host authority for parity. |
| L13 | Configure legacy launches through `PYCHARM_*`, `DOCKER4IDES_*` and related environment variables. | Modern project launch intentionally filters legacy configuration; declared project/developer inputs govern instead. Selected host observations remain available. | Record deliberate removal of ambient configuration as a contract choice, not an accidental omission; migrate only specific useful settings through explicit inputs. |

All L1–L13 dispositions are **undecided**. Rows describing an existing modern
equivalent still need a recorded “already covered” decision and evidence,
not automatic reimplementation.

## The Non-DevCapsule Directory Question

Evaluate concrete adopter journeys before choosing a command shape: trying an
IDE/agent on an existing repository without modifying it; opening a scratch
directory; testing a locally built IDE image; or starting a reproducible team
workspace. These are candidate needs, not evidence of user demand.

| Direction | Reasons for it | Costs and questions |
|---|---|---|
| Require/init a project and use `project run` | One configuration, consent, persistence and reproducibility model; fewer divergent paths to support. | Is initialization cheap enough for scratch/third-party directories? Must it write project files? Can a developer-only setup cover the need without altering the repository? |
| Add `image run` (spelling undecided) | Makes direct image selection explicit; could serve scratch directories and image testing without project metadata. | Risks duplicating launch policy or becoming a thin Docker wrapper. Must define supported image/runtime metadata, image trust, permissions, state, user identity, display, cleanup and reproducibility with no project lock. |
| Drop direct-image launching | Smallest supported surface; consistent capability-first product; experts retain Docker itself. | Less convenient experimentation and potentially higher first-use friction. Explain the intended alternative and explicitly accept this tradeoff. |

If an image-oriented mode is chosen, it must share the launch contract and
implementation where appropriate. Decide whether it accepts only DevCapsule
derived images, another declared interface, or truly generic images. Do not
silently assume any image contains PyCharm, the runtime, an inner Docker daemon
or the current launcher executable. The earlier removal of `project run-image`
and adoption of `project run --print-command` remain relevant precedents;
command inspection is not a replacement for a configuration-free launch.

## Deliverables And V1 Exit Criteria

1. Record an owner-reviewed disposition for every inventory row: **already
   covered**, **migrate into project configuration/run**, **provide through an
   explicitly designed image-oriented mode**, or **drop**. Each decision names
   the adopter need, rationale, interface/alternative and acceptance evidence.
   An item deliberately left beyond V1 needs an explicit owner-approved
   deferral and tracked destination; “decide later” cannot clear this gate.
2. Settle the configuration-free-directory question explicitly, including
   whether an image-oriented command is justified. Do not spend a release
   implementing it before this product choice is made.
3. Assign implementation owners and release slices for capabilities retained
   in V1. Implement them with documented, unit-testable contracts for inputs,
   effective authorization, state ownership and lifecycle; avoid another set
   of implicit defaults spread across adapters.
4. Demonstrate the selected user journeys with focused contract tests and
   appropriate end-user acceptance. For example, retained SSH forwarding must
   work for an authorized Git operation and be absent when unselected; retained
   inner Docker must actually start, serve a build and follow its decided
   cleanup policy. Credential values must not enter committed configuration,
   generated images or diagnostics. Test only the features actually retained.
5. Reconcile help, user documentation, diagnostics and source/PEX smoke checks
   with retirement. Existing shared-launcher messages still recommend
   `pycharm run`; `noxfile.py` and `tests/test_cli.py` still exercise its help
   or dispatch. Decide the old invocation's error behavior without preserving
   an unsafe hidden launch path. Keep normal `project run` working.
6. Review legacy-only residue, including the utility of `pycharm build` and
   `check-runtime`, as separate explicit scope decisions. Removing `run` does
   not automatically authorize deleting those commands or the shared backend.
7. Project-management records the decisions and completed acceptance in the
   V1 scope ledger. **V1 cannot be accepted while this work item is unresolved.**

The gate requires deliberate product disposition and delivery of the chosen
V1 scope, not feature parity for its own sake. The owner's only-users context
removes the assumed historical migration burden; it does not settle which
features would be valuable to future users.

## Related Records And Resumption

- [0.2.14 bug review](../releases/v0.2.14/bugs.md): retirement discussion and
  current release dispositions; this item does not reopen closed config bugs.
- [Legacy networking defect](../bugs/devcapsule/2026-07-23-pycharm-ambient-host-network.md)
  and [X11 exposure](../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md).
- [V1 scope ledger](../wip/2026-08-09-project-management/v1-scope-ledger.md):
  project-management owns registration, sequencing and the V1 gate.
- [Git identity/credential requirement](../requirements/devcapsule/r-git-001-git-identity-and-credentials-without-host-credential-mounts.md),
  [Docker capability profiles](../requirements/devcapsule/r-docker-001-explicit-docker-capability-profiles.md),
  [persistence](../requirements/devcapsule/r-state-001-persistent-ide-state-and-plugins.md),
  and [upgrade compatibility](../requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md).

Resume by reading the owner direction and inventory, checking whether retirement
has since landed, and reconciling the still-current requirements. Bring the
consequential choices to the owner before implementation. Do not reconstruct
this assessment from vanished CLI switches or assume historical tests establish
today's user experience.
