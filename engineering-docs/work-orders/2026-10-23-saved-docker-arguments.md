# Saved Docker arguments for each checkout — 0.3.0

## Outcome and authority

The owner broadened PR #253 on 2026-10-23: persist general Docker options so
returning to ML or application development requires only `project run`.
This supersedes the env-file-specific storage and launch design in
[the original work order](2026-10-23-checkout-environment.md). Its host trust
boundary and checkout isolation remain binding. Execute on the same maintenance
branch into `release-0.3.0`; use Claude Code / Claude Fable 5.1 for another
implementation-review loop. R-PRODUCT-002 governs explicit host boundaries.

## Deliverables and done criteria

1. `project config set-extra-docker-args -- OPTIONS...` replaces one complete
   saved list. `list-extra-docker-args [--json]` reports it with inline environment
   values masked. `remove-extra-docker-args` clears it, idempotently.
2. Save literal tokens in a private JSON file under the host XDG configuration
   namespace, outside Git, mounted configuration, snapshots and resolutions.
   Keep 0700 leaf directories, 0600 files, atomic writes and serialized updates.
   No shell evaluation occurs. Preserve option ordering, spaces and values.
3. `project run` composes launcher options, saved options, then one-off options
   from `run -- ...`. Reuse the launcher-owned option refusal at save and launch.
   Docker validates other options and decides duplicate-option behavior. Do not
   silently merge mounts; Docker reports conflicting destinations. `--gpus all`
   and `--volume /absolute/host/path:/absolute/container/path:ro` must survive.
4. Keep the hidden-input `set-env` convenience and names-only `list-env` and
   `unset-env`, operating on the same saved list. Clearing or replacing the list
   also clears or replaces variables added through these conveniences.
5. Mask inline environment values in saved-list reports, normal run narration
   and `--print-command`, including split and attached long/short env spellings.
   Printed commands with redactions are previews: say to use `project run` for
   the actual launch. Actual arguments reach Docker unchanged, retaining its
   env precedence and supporting the user's general passthrough request.
6. Document scope, syntax, ordering, replacement, hidden input, path expansion,
   permissions, runtime visibility and the need to recreate containers.

## Binding scope decisions

The saved list is plaintext and private per checkout. Agents and processes
inside the capsule are trusted with supplied credentials. This slice prevents
routine disclosure through DevCapsule reports; it is not a vault or a defense
against inspecting Docker's arguments/environment. The caller must avoid
secrets in other option types, such as labels, whose meaning DevCapsule cannot
infer. Shell history still records explicit inline values; use the hidden prompt.

This unmerged feature has no released storage format to migrate. Replace its
experimental env-file store with the general store. Do not add a compatibility
reader or silently import host files. `--env-file` remains an ordinary Docker
option and is read by the Docker client. GPU runtime/drivers remain host setup;
accepting a GPU flag does not install or validate NVIDIA support.

No new approval system, shell interpreter, GPU provisioning, manifest schema,
lock format, or generalized Docker parser is in scope. The executing pair
chooses internal module boundaries and tests. Consult the owner if the chosen
semantics cannot be implemented without changing these contracts.

## Acceptance and handoff

Test real command dispatch, private token persistence and quoting, replacement
and removal, host-only routing, isolation, corrupt-file recovery, rejection of
launcher-owned options, no shell evaluation, environment convenience commands,
masking, and exact saved-before-one-off launch ordering. Keep the original
failure/atomicity/concurrency tests where their contracts remain relevant.
Run the full gate before delivery and after merging reviewer improvements.
Use fake credentials only. A small existing-image Docker probe can establish
non-GPU argument semantics; do not claim GPU execution without a hardware run.
Open no second implementation PR: update #253 around the final general feature.
The reviewer delivers improvements against it; the human merges #253.

## Evidence read

The original slice is `f1ad30f`, with review #254 merged. The saved env-file
adapter, real command dispatch, Docker-option refusal, command renderer and
configuration mount were inspected. `origin/release-0.3.0` remains the branch's
base; no synchronization or release-ref rewrite is needed for this extension.
