# Recursive Dogfood E2E Stage 2 Execution Checklist

Date: 2026-08-06

Milestone: `Recursive Dogfood E2E — Build And Launch A Successor From Inside
DevCapsule`

Branch: `milestone/recursive-dogfood-e2e`

Stage 2 is the bootstrap handoff from the current v023 dogfood container to a
locally built v024 container carrying the new recursive machinery. It is not
yet the full recursive E2E.

Follow this order.

## 1. Implement The Minimum Orchestrator

Add the explicit Nox entry point:

```bash
cd devcapsule
python -m nox -s recursive_dogfood_e2e
```

Initially it must only:

- run Stage 0 preflight;
- construct the Stage 1 host-daemon launch context;
- generate a collision-safe run ID;
- create ownership-marked staging;
- print a sanitized dry-run plan;
- clean staging after success or failure; and
- perform no clone, image build, or container launch yet.

## 2. Test Through Public Interfaces

Cover:

- successful dry-run composition;
- preflight rejection before mutation;
- unique run ownership;
- redaction of host paths and sensitive staged paths;
- cleanup after orchestration failure; and
- explicit `--keep-on-failure` behavior.

Tests must invoke the Nox, CLI, or orchestrator public interfaces rather than
internal helpers or implementation details.

## 3. Run The Complete Repository Gate

```bash
cd devcapsule
python -m nox -s build
```

## 4. Commit The Orchestrator Checkpoint

Confirm the tree is clean and capture its exact revision:

```bash
git status --short
git rev-parse HEAD
```

This commit becomes the v024 source identity.

## 5. Build A Revision-Bearing PEX

The clean Nox gate should produce:

```text
devcapsule/dist/devcapsule.pex
```

Verify it from the repository root:

```bash
devcapsule/dist/devcapsule.pex version --json
```

Its reported source revision must exactly match `git rev-parse HEAD`.

## 6. Build The Local v024 Managed Base From Inside v023

Use the revision-bearing PEX and the explicitly authorized host Docker daemon.
Give the base a unique local v024 discovery tag; do not overwrite or retag
v023.

The orchestrator must ensure that any build inputs passed to the host daemon
use verified translated host paths.

## 7. Strictly Verify The v024 Base

Check:

- managed-image metadata and base kind;
- exact v024 source revision;
- embedded PEX source/revision agreement;
- embedded PEX SHA-256;
- expected Ubuntu recipe and tool inventory;
- generic OCI entrypoint and command; and
- absence of ambient Codex, Claude, or Gemini CLIs, project source,
  credentials, state, and a baked runtime plan.

Record the immutable Docker image ID, not merely its tag.

## 8. Authorize That Exact Local Base

Use the existing developer-owned override:

```bash
devcapsule/dist/devcapsule.pex project \
  --path /workspace/301e4208ef81-ChatGPT_Codex \
  config authorize base-image LOCAL_V024_TAG

devcapsule/dist/devcapsule.pex project \
  --path /workspace/301e4208ef81-ChatGPT_Codex \
  config resolve
```

Replace `LOCAL_V024_TAG` with the unique local tag selected by the run. This
must not modify `.devcapsule/devcapsule.linux-amd64.lock`; that lock continues
to select the published v023 base.

## 9. Materialize The Canonical v024 Environment

Use normal production realization, not a mutable debug environment:

```bash
devcapsule/dist/devcapsule.pex images build \
  --type environment \
  --project /workspace/301e4208ef81-ChatGPT_Codex
```

Verify its canonical identity, managed metadata, selected v024 base image ID,
PyCharm/Codex components, and source lineage.

## 10. Launch v024 And Perform The One Manual Handoff

Launch the canonical v024 environment from inside v023 using the verified path
translation and staging machinery. Do not stop v023 automatically.

The user then:

1. confirms that the v024 IDE opens and works;
2. moves to the v024 IDE/Codex session; and
3. closes the old v023 IDE when ready.

## 11. Verify The Resumed Environment

From the new session, prove:

- the current container uses the canonical v024 environment;
- its base is the recorded immutable v024 image;
- `/opt/devcapsule/bin/devcapsule.pex version --json` reports the exact
  checkpoint revision; and
- recursive preflight succeeds from the embedded PEX.

## 12. Record The Evidence

Update `CURRENT-STATUS.md` with:

- checkpoint Git revision;
- PEX SHA-256;
- v024 tag and immutable image ID;
- canonical materialized-image identity and ID;
- validation results;
- user handoff confirmation; and
- resumed-container/PEX verification.

Then commit the status update.

Do not publish v024 and do not claim full recursive acceptance. Stage 3 begins
the clean-clone workflow.
