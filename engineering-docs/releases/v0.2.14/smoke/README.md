# RC0 validation

Start with [the stories and their contracts](stories.md). It lists every story
in this campaign, what must pass first, exactly which earlier files/state it
reuses, the responsible agent/program, steps, preconditions and postconditions.
Its implementation table distinguishes working automation from unfinished work.

The old manual walkthrough is superseded. Routine prompt answers, command
execution and bookkeeping belong to automation. The owner supplies personal
login/MFA when required and makes the final release decision.

## Run an existing project

From the repository root, with Python 3.11+ and Docker available:

```bash
python3 engineering-docs/releases/v0.2.14/smoke/runner.py launch --project website
```

Replace `website` with the root of any configured project. The default executable
is `devcapsule-src/dist/rc0-published/devcapsule.pex`; on another host, add
`--pex /path/to/devcapsule.pex`. Its checksum must match published RC0.
The project must be reachable by Docker; inside a capsule use its host-backed
project mount. This command starts the ordinary `project run` directly, using
your existing configuration. It does not run preview or regenerate configuration
first. Use `--state-from "$SMOKE_RUN"` only when deliberately testing a prepared
smoke directory's isolated configuration.

The runner prints its evidence directory before launch. Use the IDE normally
and close it when finished. It records the candidate checksum, project revision
and changed paths, configuration-file hashes, actual container/image/mounts,
launcher exit and container removal. It leaves product prompts and desktop URLs
in the terminal, without saving a transcript or container environment variables.
Review observations before sharing them; project paths and free-text notes are
local evidence, not a sanitized public report.

Use the printed directory for subsequent actions:

```bash
python3 engineering-docs/releases/v0.2.14/smoke/runner.py resume RUN_DIRECTORY
python3 engineering-docs/releases/v0.2.14/smoke/runner.py report RUN_DIRECTORY
python3 engineering-docs/releases/v0.2.14/smoke/runner.py note RUN_DIRECTORY \
  --story S07 --session 1 --outcome PASS --actor human \
  --text "Describe the IDE actions and actual results observed."
```

Both `launch` and `resume` accept `--network host` or `--network bridge`:

```bash
python3 engineering-docs/releases/v0.2.14/smoke/runner.py resume RUN_DIRECTORY --network host
```

This forwards the supported `project run --authorize network host` override
for that session only, without changing saved project permissions. Repeat the
option on each invocation that needs it; omitting it uses the project's saved
configuration, even if the previous session used an override. Each session
records the requested override and the observed Docker network mode.

`resume` reuses the executable, project and configuration directories, and
requires the same home and Docker daemon. It does not restore files: the point
is to inspect the state the earlier session left. A surviving named container
or unfinished RUNNING record requires investigation before resuming; the runner
never deletes it automatically. `report` shows every session and observation.

Automatic success is labelled `PROCESS_CHECKS_PASSED`, not an IDE-story PASS.
Missing container evidence, Docker query failures or a nonzero launcher exit
produce `NEEDS_REVIEW` and a nonzero runner exit. The GUI assertions in S07 and
state-preservation assertions in S10 still need their assigned actor. The runner
makes voluntary owner testing recordable; it does not replace those assertions
or claim desktop automation exists.

For the three fully automated CLI stories, one command prepares a run and
executes them without questions or Docker:

```bash
python3 engineering-docs/releases/v0.2.14/smoke/runner.py cli
```

Add `--pex PATH` for a different location of the same candidate, or `--run
PREPARED_DIRECTORY` to reuse existing smoke inputs. Results remain in the printed
run directory. See below for fixture preparation and individual CLI groups.

## Prepare

Run from the DevCapsule repository root on the machine running Docker:

```bash
SMOKE_SCRIPTS="$PWD/engineering-docs/releases/v0.2.14/smoke"
SMOKE_RUN="$HOME/devcapsule-rc0-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
bash "$SMOKE_SCRIPTS/00-prepare.sh" "$SMOKE_RUN"
```

Inside a capsule, use a new directory on its host-backed project mount instead
of a container-only home or `/tmp` if it will later host Docker launches. The
path must not already exist. For S02/S03/S17 alone, add `--cli-only` before
the run-directory argument; preparation then needs no Docker. To reuse the downloaded RC0, supply its path as
`00-prepare.sh`'s second argument instead of downloading it again.

Preparation verifies the fixed RC0 checksum and clones these exact public inputs:

| Case | Pinned repository revision |
|---|---|
| `tictactoe` | [TypeScript game](https://github.com/ccozianu/devcapsule-sample-typescript-tictactoe/tree/f1e2e6febf98b3058f4d35c209d06844c6c14dc4) |
| `trading` | [Trading research](https://github.com/ccozianu/devcapsule-sample-trading-research/tree/687d245eba9ff461ddf6013aac7d80718ebc831f) |
| `fastapi` | [FastAPI TODO](https://github.com/ccozianu/devcapsule-sample-fastapi-webbapp/tree/31c86c4a5f7d73e5864fd3d9311ee26243140fbe) |

## Run implemented CLI stories

The runner requires Python 3.11+ on the test machine. This is a test-harness
dependency; the DevCapsule executable itself remains self-contained.

```bash
python3 "$SMOKE_SCRIPTS/verify-cli.py" "$SMOKE_RUN"
```

This executes S02 (real prompts, accept/decline), S03 (unattended initialization
and missing-answer recovery), and S17 (workflow operations preserving unrelated
files). It starts no Docker container, contacts no provider, and uses only a
new filesystem-local Git remote for workflow checks. There are no questions to
answer. Select `--stories init` or `--stories coordination` to run one group.

Each attempt gets `evidence/cli-*/results.json`, command/exit logs, prompt
transcripts and Git-tree comparisons. Failure returns nonzero; a missing
prerequisite is BLOCKED. The CLI runner never marks unexecuted GUI stories passed.

## Configure a sample without answering questions

```bash
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" fresh
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" tictactoe --regenerate
```

The fixed fixture policy uses `smoke@example.invalid` for a new project,
selects no default agent, accepts the pinned base, denies host Docker/network/
sudo/browser/X11, and authorizes the pinned public samples' declared Claude
and Antigravity downloads. Download authorization supplies no provider login.
Existing authored identities/recommendations remain intact. The original
sample locks remain in `evidence/CASE-original/`; regeneration is explicit.
S04 additionally requires testing the original lock, preserving any refusal
and checking the actual remedy. A successful configuration alone is not S04 PASS.

Do not run preview before a first-launch story: it can download and build.
The retained `02-preview.sh`, `03-launch.sh`, `04-inside.sh` and `project.sh`
are building blocks, not implementations of every assertion in stories.md.
Desktop work requires desktop-control tooling; it is not automatically assigned
to the owner when the tooling is absent. See the story implementation table for
current gaps and the [results template](results-template.md) for recording them.
