# 0.2.15: Extra tools, project information and agent defaults

Status: implemented and accepted on downloaded 0.2.15 RC1, 2026-09-27;
final promotion and publication pending. See the
[release overview](../releases/v0.2.15/README.md) for evidence and remaining gates.

Release: 0.2.15. Driver: maintenance, with these three bounded slices to its
release scope explicitly approved by the owner. Project-management owns this
scope decision; this does not make maintenance a general feature workstream.

## Owner decision and purpose

The owner successfully used 0.2.14 for a website prototype and installed
gcloud under `$HOME/xtras/gcloud`. It survived subsequent runs, as intended,
but the persistence contract was not discoverable. The owner approved both
a supported `/opt/xtras` installation location and `devcapsule project info`.
The location matters even though persistent home can provide its storage.

This supersedes the 2026-09-26 restriction that 0.2.15 contain only the init
answer-loss fix. That fix remains required. The owner subsequently selected a third small slice: agent permission
defaults, initially Antigravity and then explicitly extended to Claude Code. Previously deferred cleanup,
optimization, IDE surfaces and release-notes automation remain outside 0.2.15.

## Persistent `/opt/xtras`

- Available and writable by the capsule user without sudo.
- Contents survive stopping, removing and recreating the capsule for the
  same local checkout, including ordinary subsequent project runs.
- Storage is checkout-scoped by default, following the existing persistent
  home's explicitly selected storage and sharing rules. A fresh independent
  checkout does not automatically receive these installations.
- `/opt/xtras/bin` is on PATH for IDEs, agents and terminals.
- Backing it with `$HOME/xtras` is permitted and preferred for the small
  slice. Existing `$HOME/xtras/gcloud` must remain usable without manual
  migration. Choose the link or mount mechanism after checking root-filesystem
  writability, existing destinations and startup ownership; do not overwrite
  existing content to establish the mapping.
- DevCapsule preserves files; the developer manages tool installation and
  updates. Persistence is not a claim of reproducibility on another machine
  or binary compatibility with every future base.

## Read-only `devcapsule project info`

One discoverable overview for the user and their agent:

- Project and checkout identity, and whether the report describes host-side
  configuration or the running capsule.
- Selected components and versions. Inside a capsule, report running software
  from launch evidence and distinguish a changed next-launch selection.
  Do not infer running versions from a subsequently edited project lock.
- DevCapsule-provided environment variables, their values and purpose.
  Omit secret values. Host output describes the capsule's configured
  environment, not the host shell's unrelated environment; label unavailable
  runtime-only facts rather than inventing them.
- Persistent container paths and their backing storage, scope and lifecycle,
  including project source, home, `/opt/xtras` and declared component slots.
  Explain that managed state may live outside the Git checkout.
- Temporary locations and what is lost when the container is removed.

Discover the project from its root or a descendant on the host. Inside a
running capsule, the command must identify its project even when invoked from
outside the source tree, such as `/opt`. Honor explicit project selection
without confusing another nested project with the containing capsule.
Inspection must not initialize, resolve, repair or otherwise mutate records.
It must not require new host privileges to inspect its own running context.

Arbitrary installed-tool inventory and version probing are outside this
slice. gcloud under xtras is covered by the persistence explanation, not
misrepresented as a catalog component. No new component publication flow,
package manager or cross-machine synchronization is requested.

## Antigravity tool-permission default

The owner's third addition, approved 2026-09-27, is:

```json
{"toolPermission": "always-proceed"}
```

in `$HOME/.gemini/antigravity-cli/settings.json`. Apply it for the selected
Antigravity CLI component inside the capsule. This is the default agent
posture intended by DevCapsule's isolated-workspace model.

- Seed the setting for new managed Antigravity state.
- For existing managed settings lacking the key, add only this default,
  preserving other settings. Retain an explicit user-selected permission
  mode; never reset the whole file on launch. Repeated launches are idempotent.
- Keep malformed settings intact and provide an actionable diagnostic rather
  than silently replacing them. Preserve the existing rule against silently
  seeding developer-adopted external state; document the one-key edit for it.
- Verify the exact key and value with the selected Antigravity version and
  demonstrate an ordinary tool action without a permission prompt. This
  record captures the owner's requested setting, not a completed vendor test.

Codex already has this posture in v0.2.14: its component seeds
`approval_policy = "never"` and `sandbox_mode = "danger-full-access"` in
`$HOME/.codex/config.toml` only when that file is absent in managed state.
Existing files and adopted state remain untouched. No Codex behavior change
is requested. The current generic seed mechanism creates missing files only;
adding a missing JSON property to an existing Antigravity settings file needs
an explicit, bounded implementation rather than assuming file seeding does it.

## Claude Code permission default

Owner direction, 2026-09-27: include Claude in the agent-default correction.
Do not wait for a first run to create the configuration tree. Anthropic's
[settings documentation](https://code.claude.com/docs/en/settings#find-or-create-your-settings-files)
says installation creates no settings file and users may create it themselves;
`CLAUDE_CONFIG_DIR` relocates the user settings directory. DevCapsule already
sets that variable to its persistent Claude slot at `/home/devcapsule/.claude`.
The launcher creates that slot and missing seed parent directories before
mounting it. There is no need to manufacture Claude's complete state tree.

Seed `$CLAUDE_CONFIG_DIR/settings.json` (normally `$HOME/.claude/settings.json`)
with the minimum supported mode setting:

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

Anthropic documents this user-scope default in
[permission modes](https://code.claude.com/docs/en/permission-modes#start-in-a-different-permission-mode).
Let Claude create its remaining session, authentication and preference state.
Do not seed sign-in or project-trust records or use an organization-managed
policy to impose the default. This concerns the CLI component; changing IDE
extension-specific controls is not implicitly included.

Use the Antigravity defaulting rules: create missing managed files, fill only
missing properties in existing valid settings, preserve explicit permission
choices and unrelated fields, leave malformed files intact with a diagnostic,
and retain the adopted-external-state boundary. A conflicting non-object
`permissions` value is not an empty object to replace silently. Repeated
launches must preserve settings written by Claude itself.

The documented CLI has a separate first-use bypass confirmation. Maintenance
must check the selected release version's supported setting for suppressing
that notice, including whether `skipDangerousModePermissionPrompt` is supported
in user settings; its availability was not established by this source review.
If supported, include the smallest such property under the owner's requested
no-tool-approval default, preserving explicit choices. Otherwise report the
remaining one-time notice accurately rather than stamping unrelated onboarding
state or claiming fully prompt-free startup. Authentication and deliberate
user-interaction questions remain separate from ordinary tool approvals.

Acceptance starts with an empty managed Claude slot, before Claude has ever
run: the launcher seeds it; a fresh interactive CLI session loads the mode;
an ordinary file/shell tool action needs no approval; Claude can write its
remaining settings; after a container replacement those settings survive.
Also exercise an existing file missing the mode, an explicit alternative mode,
unrelated nested permission fields, malformed settings and idempotent relaunch.
A print/headless invocation alone cannot establish interactive first-run
behavior. Documentation supports the seed design; selected-version runtime
acceptance is still pending.

## Accepted deferral

The owner can live with the general in-capsule `devcapsule project <command>`
failure for 0.2.15. The report says it occurs regardless of working directory;
that breadth has not been independently reproduced in this coordination slice.
The existing [guard bug](../bugs/devcapsule/2026-09-26-project-group-guard-hides-unknown-subcommand-in-capsule.md)
establishes the narrower unknown-subcommand diagnostic defect. Keep it open,
outside the 0.2.15 gate, for later maintenance triage. No fixed later release
is assigned by this decision.

This deferral does not waive the new `project info` contract. Its own runtime
dispatch and discovery must work; a general repair of other subcommands is
not required for this release.

## Acceptance and delivery

1. Preserve the init fix's candidate acceptance. Do not publish the former
   fix-only tree as the accepted final scope after this decision.
2. Start with an existing `$HOME/xtras` installation; expose it through
   `/opt/xtras`, add an executable through its bin directory, replace the
   container and prove both data survival and command discovery. Check a
   fresh checkout's default isolation and ordinary no-sudo operation.
3. Run `project info` from a host project directory and descendant, then
   inside the capsule from the project and `/opt`. Check the actual persisted
   paths and component versions against the report. Exercise a next-launch
   configuration change and verify that it does not relabel running software.
4. Verify Antigravity fresh defaults, an existing file missing the key,
   preservation of unrelated settings and an explicit permission choice,
   malformed-file preservation and repeat launches. Prove an ordinary tool
   action proceeds without approval using the selected vendor CLI.
5. Run the Claude fresh-state interactive acceptance described above, including
   its first-use notice disposition and preservation of vendor-written state.
6. Cover read-only behavior and secret omission with focused regression
   checks; run the required release gate and downloaded-candidate acceptance.
   Update CLI help, user documentation and release notes alongside delivery.
7. Maintenance records implementation and main disposition under the existing
   release policy, and updates its release overview before the next candidate.

## Evidence informing the scope

- Owner's successful `$HOME/xtras/gcloud` persistence on 0.2.14.
- [State and persistence specification](../specifications/product/state-and-persistence.md):
  persistent home is the fallback for tools without component state contracts.
- The v0.2.14 shared launcher mounts persistent home at `/home/devcapsule`.
- Main at `0cb4b0a` has configuration inspection and launch-context/version
  reporting foundations, but no `project info` command. This is inspection
  evidence, not proof of the new feature or an implementation estimate.
