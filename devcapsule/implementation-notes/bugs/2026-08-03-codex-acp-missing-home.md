# Bug: Codex ACP Fails Because Explicit CODEX_HOME Does Not Exist

Date opened: 2026-08-03

Status: reproduced; root cause/workaround validated; component fix implemented, external validation pending

Requirements: R-DEV-001, R-STATE-001, R-FRAMEWORK-001

## Symptom

In the v021-backed PyCharm 2026.2.0.1 environment, the developer configured a
valid OpenAI API key in JetBrains AI Assistant. **Test connection** succeeded,
but starting a Codex conversation failed:

```text
Failed to initialize ACP session. Error: Codex process has exited with code 1:
WARNING: proceeding, even though we could not create PATH aliases: CODEX_HOME
points to "/home/devcapsule/.codex", but that path does not exist
Error: CODEX_HOME points to "/home/devcapsule/.codex", but that path does not
exist
```

The successful provider test and failed ACP startup exercise different layers:
the former validates API connectivity/credentials, while the latter starts a
local Codex process that first validates its state root.

## Confirmed Root Cause

OpenAI's current Codex environment-variable reference states:

- `CODEX_HOME` defaults to `~/.codex`; and
- when `CODEX_HOME` is explicitly set, that directory must already exist.

DevCapsule's PyCharm Docker launcher unconditionally injects:

```text
CODEX_HOME=/home/devcapsule/.codex
```

The generic runtime correctly creates the persistent home, `.ssh`, XDG roots,
runtime directory, and declared state slots. It deliberately does not create
an agent-specific `.codex` directory. Inspection of the preserved external
home confirmed that `/home/devcapsule/.codex` does not exist. Codex therefore
rejects the explicit override exactly as documented.

This is a DevCapsule environment-contract bug, not an API-key, network, ACP
download, or system-Node failure.

## Additional Evidence

JetBrains' ACP logs show that AI Assistant independently provisions:

- managed Node.js `24.13.0`; and
- `@agentclientprotocol/codex-acp@1.1.9` through its managed `npx` runtime.

It prepends that managed Node directory to the ACP process path. Consequently,
the separate V1 backlog item for `/opt/node/current/bin` does not fix this ACP
failure.

The logs list inherited `HOME=/home/devcapsule` and the DevCapsule-injected
`CODEX_HOME`, then reproduce the same non-recoverable exit on every retry.

## Immediate Dogfood Workaround

Inside the running capsule, before retrying the Codex conversation:

```bash
mkdir -p "$CODEX_HOME"
chmod 700 "$CODEX_HOME"
```

The directory is beneath the persistent container home, so it should survive
normal capsule exit and relaunch. This creates no credential value and does not
require sudo. It is a workaround for the current revision, not the preferred
product contract.

On 2026-08-03, the product owner ran this workaround in the external v021
capsule and confirmed that Codex ACP then worked. This manually validates the
missing-directory diagnosis while leaving the unconditional environment
override as the product bug to remove.

## Implemented V1 Fix

1. Remove the unconditional `CODEX_HOME=/home/devcapsule/.codex` Docker
   environment argument from the shared PyCharm launch path.
2. Preserve `HOME=/home/devcapsule`. When Codex is not selected, no Codex
   directory, mount, or environment variable is added.
3. Do not add `.codex` to the generic runtime's universal filesystem plan.
   That would encode one optional agent into every component-neutral capsule
   and conflict with the accepted agent-neutral-base direction.
4. The explicitly selected Codex component declares credential-bearing
   `codex/home` state at `/home/devcapsule/.codex` and a state-to-environment
   mapping for `CODEX_HOME`. Generic host planning creates and mounts the
   component directory before the process starts.
5. Do not mount a host Codex directory, bake authentication into the image, or
   put API keys/auth state in the runtime plan, resolution, logs, or committed
   configuration.

The component also contributes its checksum-pinned CLI to the locally
materialized environment at `/usr/local/bin/codex`; it remains absent from the
agent-neutral shared base. The component interface advertises
`OPENAI_API_KEY` as optional secret metadata but does not import it
automatically. Users may authenticate normally inside the capsule, with the
result retained in `codex/home`.

## Verification Target

1. Docker-plan tests prove normal project launch no longer exports
   `CODEX_HOME` merely because the interactive component is PyCharm.
2. Generic runtime tests continue to contain no agent-named directory or state
   field.
3. A fresh Codex-selected checkout starts with the declared component state
   mounted before ACP validates `CODEX_HOME`.
4. The configured API-key flow completes one real AI Assistant/Codex exchange
   in external dogfood.
5. A second capsule launch preserves the intended Codex/AI Assistant state in
   DevCapsule-managed component state without a broad host-agent-state mount.
6. Tests and log inspection prove that no credential value enters Docker
   arguments, runtime plans, resolutions, images, or diagnostics.

## Close Criteria

Close when a fresh v021-successor checkout can use JetBrains AI Assistant's
Codex ACP integration after successful provider configuration, no explicit
missing `CODEX_HOME` failure occurs, generic runtime remains agent-neutral,
state persists under container home, and the automated plus external checks
pass.

Reopen if a fresh persistent home requires a manual `.codex` directory again,
if DevCapsule restores an ambient agent-state variable/mount, or if the fix
moves credentials into an image or checkout-generated artifact.

## Official Source

- [OpenAI Codex environment variables: core locations](https://learn.chatgpt.com/docs/config-file/environment-variables#core-locations)
