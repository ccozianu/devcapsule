# RC0 smoke campaign

Use **the published v0.2.14-rc0 executable**, ordinary project commands, and
real IDEs. This sequence is for the owner to run on Linux x86-64 or WSL2 with
working Docker/Buildx and a browser. It contains executable helpers plus the
human observations automation cannot certify. The scripts do not publish
anything, alter the installed DevCapsule, or clean up other Docker resources.

Start with the fresh project, then TypeScript, then Python. FastAPI's service
exercise and agent login are separate, longer steps. Stop at a failure, record
it, and follow the printed remedy; do not silently use `--force`, approve every
recommendation, or edit generated resolutions. Partial results are useful.
RC0 predates the `pycharm run` retirement; that removal is not an RC0 assertion.

## 0. Prepare the candidate and public projects

Run from the DevCapsule repository root on the machine running Docker:

```bash
SMOKE_SCRIPTS="$PWD/engineering-docs/releases/v0.2.14/smoke"
SMOKE_RUN="$HOME/devcapsule-rc0-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
bash "$SMOKE_SCRIPTS/00-prepare.sh" "$SMOKE_RUN"
```

The path must not already exist. When testing from inside an existing capsule,
choose a new directory on its **host-backed project mount**, not `/tmp` or a
container-only home: the host Docker daemon must be able to bind the projects
and generated state. Start each later host command with the same two variables.

To reuse the verified download, supply its path as the second argument:

```bash
bash "$SMOKE_SCRIPTS/00-prepare.sh" "$SMOKE_RUN" \
  "$PWD/devcapsule-src/dist/rc0-published/devcapsule.pex"
```

Use one preparation command, not both. It verifies the fixed RC0 SHA-256,
records executable identity and platform, clones public projects over HTTPS,
and creates `evidence/results.md` from the [results template](results-template.md).
No IDE is launched. A failed preparation retains its directory for diagnosis;
use a new directory for a clean retry.

| Case | Public source, pinned to this release's submodule revision | Purpose |
|---|---|---|
| `fresh` | Empty directory | No account needed: initialization, VSCodium, Node, edit/save/resume. |
| `tictactoe` | [TypeScript game](https://github.com/ccozianu/devcapsule-sample-typescript-tictactoe/tree/f1e2e6febf98b3058f4d35c209d06844c6c14dc4) | Existing project, Node/npm in the IDE terminal, tests, production build and UI. |
| `trading` | [Trading research](https://github.com/ccozianu/devcapsule-sample-trading-research/tree/687d245eba9ff461ddf6013aac7d80718ebc831f) | PyCharm, Python package/tests, Markdown preview and optional agent work. No market data or model API required for its unit tests. |
| `fastapi` | [FastAPI TODO app](https://github.com/ccozianu/devcapsule-sample-fastapi-webbapp/tree/31c86c4a5f7d73e5864fd3d9311ee26243140fbe) | Python + Node + PostgreSQL client, then optional real service use. |

Public sample declarations/locks are older than RC0. Originals are copied to
`evidence/CASE-original/`. The TypeScript README's `codium_with_claude run`
example is obsolete: use the sequence here. Only these disposable clones are
changed; no submodule pointers or upstream sample contents are changed.

All host helpers use the copied, checksum-checked candidate and a private XDG
root. `HOME` and Docker connection settings are preserved. IDE/agent state is
retained between launches. Installations consume disk/network on first use;
package registries and vendor availability can affect results. Defaults use the
published base; the local `devcapsule-base:0.2.14-rc0-local` is not substituted.

## 1. Fresh-user path: initialize, preview, launch

```bash
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" fresh
```

Answer the creator prompt with your identity. Decline the default agent for
this account-free case. Keep Docker, host network, development sudo and host
browser recommendations at `none`; review and approve the displayed base if
acceptable. The script explicitly denies host-X11 so this tests the contained
desktop. **Expected:** understandable prompts, initialized project, configuration
listing and successful resolution, without editing generated files.

```bash
bash "$SMOKE_SCRIPTS/02-preview.sh" "$SMOKE_RUN" fresh
bash "$SMOKE_SCRIPTS/03-launch.sh" "$SMOKE_RUN" fresh
```

Preview can download components and build an image; it must not launch the
project. It saves the command and preparation diagnostics in `evidence/` and
checks that the named project container was not created. Inspect the printed
Docker command: correct project mount, no host network/socket/X11 grant that
you declined. **Do not execute that saved command**: transient files may already
be gone. The subsequent normal `project run` is the launch under test.

Open the full printed desktop URL privately if the browser does not open.
In VSCodium, trust this test folder if prompted. Create **in the IDE**, save,
and reopen `hello.js` containing:

```javascript
console.log("Hello, RC0!");
```

In the **IDE terminal**, from the project root:

```bash
bash .rc0-smoke/04-inside.sh fresh
```

**Expected:** Node/npm on PATH, exact greeting, no host Node installation
required. Confirm `hello.js` is also visible in the host clone. Close the
browser tab and reopen the same URL: the running session should still exist.
Then exit through **File → Exit**, wait for the launcher to return, and record
its result. Closing a browser tab is not ending a capsule.

## 2. Public TypeScript project

First try the older project exactly as cloned:

```bash
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" tictactoe
```

Save any refusal and its offered remedy. Then explicitly refresh the project
lock for the current candidate (even if the old configuration was admitted):

```bash
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" tictactoe --regenerate
```

This deliberately tests adopting the RC0 tool selection, not running its old
base. Review acquisition terms for declared agents; approval to download does
not require signing in. Decline host Docker, host networking, sudo and host
browser for the account-free test. Unlike `fresh`, this sample already declares
agents. Review `evidence/tictactoe-config.diff`; the authored need should remain.

```bash
bash "$SMOKE_SCRIPTS/02-preview.sh" "$SMOKE_RUN" tictactoe
bash "$SMOKE_SCRIPTS/03-launch.sh" "$SMOKE_RUN" tictactoe
```

In the IDE terminal:

```bash
bash .rc0-smoke/04-inside.sh tictactoe
npm run dev -- --host 127.0.0.1
```

The workload uses the sample's actual `npm ci`, `npm test`, and `npm run build`.
Open Vite's printed URL **in the capsule's browser**, not the host browser;
bridge networking does not publish this port to the host. Play alternating
moves until one player has five in a row; verify the winning highlight, refusal
of further moves, and **Start new game**. Edit a visible label, save, and see
the browser update. Stop Vite with Ctrl+C in its terminal, then exit VSCodium.

## 3. Public Python project and actual agent work

Repeat configuration (first preserved lock, then explicit regeneration),
preview and launch with case `trading`. Deny the sample's broad host-access
recommendations for the deterministic workload; approve acquisitions only
under the displayed terms. Inside PyCharm:

```bash
bash .rc0-smoke/04-inside.sh trading
```

**Expected:** package installs in `.venv`, the sample's actual unittest suite
passes without model API calls. Select `.venv/bin/python` as PyCharm's project
interpreter; open a test, set a breakpoint and run/debug it from the IDE. Open
README.md's Markdown preview and confirm rendered text appears (JCEF check).
Record terminal-only success separately if interpreter/debug/preview fails.

For an agent check, use your chosen installed agent and sign in through its
ordinary UI. Ask it to add a small deterministic test for an existing pure
function, run the tests, and explain the resulting diff. Review the actual
file change and test output. Record IDE, agent, model, and whether this was
terminal CLI or IDE/ACP integration. A successful `--version` is not agent
acceptance; terminal success does not prove ACP. Keep login codes and tokens
out of evidence. Skip with **NOT RUN** if no account is available.

## 4. Public FastAPI project, then optional PostgreSQL journey

Repeat preserved-lock configuration, explicit regeneration, preview and launch
with case `fastapi`. Its SQLite-backed tests and frontend build do not need a
host Docker grant. Inside PyCharm:

```bash
bash .rc0-smoke/04-inside.sh fastapi
```

**Expected:** `psql`, Python and Node/npm are available, backend tests pass,
and frontend production assets build. This already covers useful work across
multiple toolchains without starting the database.

For the service exercise, exit PyCharm first. This sample documents host
Docker and host networking as its service setup; explicitly enable them only
for this case, then resolve and relaunch:

```bash
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" fastapi config authorize docker-daemon host-socket
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" fastapi config authorize network host
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" fastapi config resolve
bash "$SMOKE_SCRIPTS/03-launch.sh" "$SMOKE_RUN" fastapi
```

The upstream Compose file has a fixed container name and a default port 5432.
Use a uniquely named test database instead, from the **IDE terminal**:

```bash
SMOKE_DB="rc0-todo-$(date -u +%Y%m%dT%H%M%SZ)-$$"
printf '%s\n' "$SMOKE_DB" > .rc0-smoke/database-name.txt
docker run -d --name "$SMOKE_DB" -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=todo -e POSTGRES_PASSWORD=todo -e POSTGRES_DB=todo postgres:17-alpine
docker inspect --format '{{.Image}}' "$SMOKE_DB" > .rc0-smoke/database-image.txt
```

Use a free port if 55432 is occupied; change all URLs below accordingly. These
are disposable sample credentials. Record the resolved database image ID
because the upstream PostgreSQL tag is mutable. Check readiness with
`docker exec "$SMOKE_DB" pg_isready -U todo -d todo`; retry until ready, stopping
and inspecting `docker logs "$SMOKE_DB"` if it does not become ready within a
minute. Do not proceed on a failed readiness check.

From the project root, run the backend:

```bash
export DATABASE_URL='postgresql+psycopg://todo:todo@localhost:55432/todo'
(cd backend && ../.venv/bin/python -m uvicorn app.main:app --port 58000)
```

In a second IDE terminal:

```bash
(cd frontend && BACKEND_URL=http://localhost:58000 npm run dev -- --port 55173 --strictPort)
```

Open `http://localhost:55173` on the Docker host, or in the capsule browser.
Create a TODO, mark it complete and refresh. Confirm the same row in PostgreSQL:

```bash
psql 'postgresql://todo:todo@localhost:55432/todo' -c 'select * from todos;'
```

Stop the API/frontend via Ctrl+C, then stop/start only this test database with
`docker stop "$SMOKE_DB"` and `docker start "$SMOKE_DB"`. Wait for readiness,
restart the API/frontend and verify the TODO is still present. Retain this
container for evidence, or stop/remove that exact named container afterward.
Do not run Docker-wide prune or remove someone else's database to free a port.

## 5. Resume and configuration preservation

For each case, after a normal IDE exit, repeat the same `03-launch.sh` command.
**Do not initialize again.** Check saved files, IDE settings/interpreter, the
workload, and any chosen agent's login/conversation continuation. Record each
observation separately. Compare the fresh case with later warm launches;
record unexpected redownloads/rebuilds without presuming every rebuild is wrong.

For a small configuration persistence check on `trading`, while it is stopped:

```bash
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" trading config authorize host-browser false
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" trading config list
bash "$SMOKE_SCRIPTS/01-configure.sh" "$SMOKE_RUN" trading --regenerate
bash "$SMOKE_SCRIPTS/project.sh" "$SMOKE_RUN" trading config list
```

**Expected:** the explicit denial remains false after regeneration, even
though the manifest recommends true. Keep the before/after values in results.
This is a regeneration check, not proof of upgrading an existing running
v0.2.12 checkout; that release acceptance item remains separate.

## Evidence and stopping point

Update `SMOKE_RUN/evidence/results.md` as you go. Command/exit history is in
`commands.log`; preview diagnostics and configuration diffs live beside it.
Workload output stays in each clone's `.rc0-smoke/`. Interactive launch/login
output is deliberately not captured automatically; save only sanitized error
excerpts, never the desktop URL. No helper marks GUI or whole-release acceptance
as passed. Summarize confirmed observations in the [release checklist](../README.md).

Stop when these selected journeys give sufficient evidence; no full model/IDE
matrix is implied. Coordination corruption needs a separate isolated-remote
scenario, never destructive testing against the project's real coordination
branch. Preserve failed builds for the deferred image-composition bug if it
recurs. When finished, end IDEs, stop only the test service, and keep the run
directory until failures are triaged. Cleanup is deliberately manual.
