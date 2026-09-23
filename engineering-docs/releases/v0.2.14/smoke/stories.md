# RC0 validation stories

This is the test specification. It replaces the old walkthrough's assignment
of routine terminal work to the owner. A story passes only when its stated
postconditions have evidence. A script's existence is not a passed story.
Scope: the published Linux x86-64 RC0, VSCodium and PyCharm, the three pinned
public samples, one selected agent through CLI and PyCharm ACP, upgrade from
0.2.12, configuration, component selection and workstream coordination. WSL2
repeats the same applicable stories on WSL2; Linux results do not cover it.
Contract sources: [usable IDE environments](../../../requirements/product/r-product-001-batteries-included-ide-environments.md),
[explicit host boundaries](../../../requirements/product/r-product-002-explicit-host-boundaries.md),
[state and persistence](../../../specifications/product/state-and-persistence.md),
[configuration lifecycle](../../../wip/2026-09-18-maintenance/configuration-contract.md),
[component version sets](../../../requirements/product/r-upgrade-001-component-version-sets.md),
and [workstream coordination](../../../requirements/product/r-product-006-multiple-workstream-coordination.md).
The checks below make those promises measurable; they do not add new product features.

GPU bases, legacy launcher parity and every possible IDE/agent pairing are out
of this campaign. `pycharm run` retirement belongs to RC1, not RC0.

## People, agents and programs

- **Test agent:** the maintenance Codex session. It verifies prerequisites,
  runs scripts, reads evidence, diagnoses failures, and updates results. It
  must not turn a failed assertion into a pass by changing the expected answer.
- **Runner:** deterministic programs invoked by the test agent. They type fixed
  answers, run commands, inspect files/containers, compare results, and retain
  logs. They do not ask the owner to copy commands or calculate expected values.
- **Desktop agent:** an agent with screen inspection and keyboard/mouse tools,
  assigned the exact IDE/browser actions below. It is not the coding agent
  being tested. This session currently exposes no browser/desktop-control tool;
  graphical execution is BLOCKED until that facility exists. That is an
  execution dependency, not a claim that GUI actions inherently require a human.
- **Coding agent under test:** the lock-selected Codex installed inside the capsule. It is
  given a fixed edit/test task; its success is independently checked by the
  runner and desktop agent. CLI and ACP results are separate.
- **Owner:** supplies account authentication only where the provider requires
  personal login/MFA, decides genuinely new access/terms choices, and accepts
  or rejects the release after reading results. Fixed fixture answers and
  previously agreed choices are automated. The owner is not the test runner.

No additional agents have been started by writing this specification.

## Dependencies and fixture ownership

**Pass first** means only the earlier result is needed; no mutable files or
running processes are carried over. **Reuse** means the named output must be
used, including its state. A failed or blocked prerequisite blocks dependent
stories. It does not block independent stories. Every candidate story reuses
S00's checksum-verified RC0 executable; that common dependency is implicit in
the table. Immutable sample snapshots can be copied; never copy an existing
checkout's generated resolution and call that a fresh checkout.

| ID / user story | Pass first only | Reuse from earlier story | Main executor |
|---|---|---|---|
| S00 I obtain the correct executable | — | — | Runner |
| S01 I obtain the public example projects | — | — | Runner |
| S02 I answer initialization questions | — | —; new empty project and private state | Runner using a terminal |
| S03 I initialize without a terminal | — | S02 choices.json for comparison; new empty project/state | Runner |
| S04 I open an existing declared project | S03 | S01 sample snapshot, copied per case | Runner |
| S05 My first ordinary run builds and starts the environment | S03 | S02 fresh project; S04 configured sample, each separately | Runner + desktop agent |
| S06 I run the project's tests and build | — | S05 live sample capsule and checkout | Runner |
| S07 I edit and debug in the IDE | S06 for the selected sample | S05 live capsule; S06 interpreter/dependencies | Desktop agent + runner |
| S08 A coding agent edits files and runs tests | S06 | S05 live capsule; S06 dependencies | Coding agent + independent runner |
| S09 The IDE's ACP agent integration works | S08 CLI result | S05 PyCharm capsule, separate fresh ACP state | Desktop agent + coding agent + runner |
| S10 I close and resume my work | — | S07 edits/IDE settings, S08/S09 sessions, S05 persistent state | Runner + desktop agent |
| S11 I inspect the launch command without starting the project | S03 | S04 declaration copied into a separate diagnostic checkout | Runner |
| S12 My explicit host-access choices are respected | S03 | S04 declarations copied to separate permission-test checkouts | Runner |
| S13 I have a working predecessor installation | — | S01 Python snapshot; verified 0.2.12 executable acquired separately | Runner + desktop agent |
| S14 I upgrade that working installation to RC0 | S03 | S13 exact checkout, configuration, IDE state and saved files | Runner + desktop agent |
| S15 I try a component version and can return to the old one | S06 | S05 capsule's stopped checkout; saved original component selection | Runner |
| S16 I develop the full FastAPI application | S12 host-Docker/network case | S05/S06 FastAPI checkout/environment; new test database | Runner + desktop agent |
| S17 Other workstreams' records survive my workflow commands | — | —; new local bare remote and two disposable checkouts | Runner |
| S18 Two checkouts keep their private state separate | S03 | S01 sample snapshot copied twice; separate generated checkout records | Runner + desktop agent |
| S19 I recover after a failed configuration or launch | S03 | S04 copied configuration; new failure-test checkout | Runner |
| S20 I can assess the candidate from the evidence | All selected stories terminal: passed, failed or blocked | All story result records and evidence | Test agent, then owner |

S05 must run **before** preview or any other materialization on its checkout.
S11 gets separate mutable state. A shared Docker cache may still be warm:
record that fact, never claim a completely cold machine, and never prune the
owner's cache to manufacture one. A fully cold-cache variant needs a disposable
Docker daemon; its absence does not excuse hiding first-run preparation.

## Story contracts and steps

### S00 — Obtain RC0

**Feature/promise:** distribution identity; the bytes tested are the published
candidate, and launching it requires no host Python installation.
**Preconditions:** supported host, public download access (or existing download).
**Steps:** runner downloads/copies RC0, checks the recorded SHA-256, checks
version/source JSON against `v0.2.14-rc0` / `d078b87`, records host/Docker versions.
Test agent runs the existing no-Python/no-network executable test where needed.
**Postconditions/output:** verified executable and identity record; failed
checksum stops execution before invoking the file. Python used by the test
harness must not be mistaken for a product runtime requirement.

### S01 — Obtain examples

**Feature/promise:** representative, repeatable application inputs (test setup).
**Preconditions:** Git/network available; fetching samples can proceed independently of S00.
**Steps:** runner fetches the exact TypeScript, trading-research and FastAPI
revisions listed in `00-prepare.sh`, verifies HEAD, saves their authored
manifest/lock bytes. No sample code executes during preparation.
**Postconditions/output:** immutable baseline snapshots and revision inventory.
Each mutating story receives its own copy unless reuse is explicitly required.

### S02 — Answer initialization questions

**Feature/promise:** initialization elicits missing answers, honors them, and
finishes with a usable resolution; choosing no agent does not install one.
**Preconditions:** empty directory, no checkout record; no personal credentials.
**Steps:** runner opens a pseudoterminal and invokes RC0 `project init` with
frontend-ide/node needs. It answers the creator with `smoke@example.invalid`,
answers default-agent `no`, each host recommendation `none`, and the exact
known base prompt `default`. It refuses an unknown/repeated prompt rather
than guessing. In a separate fixture it declines the base and checks refusal.
**Postconditions/output:** accepted case has exactly frontend-ide/node,
no authored host recommendations, the intended base grant and explicit Docker/
sudo/browser denials, and a fresh resolution. Declined case has no base grant
or successful resolution. Save transcript and parsed configuration assertions.
**Human work:** none. These are test data, not the owner's identity or judgment.

### S03 — Initialize without prompts

**Feature/promise:** supported command-line answers permit unattended use;
unanswered mandatory choices fail clearly without silently granting access.
**Preconditions:** S02 passed; separate empty fixture.
**Steps:** runner invokes init with explicit creator, needs and base choice,
stdin closed; compares resulting semantic choices with S02. A separate missing-
base invocation must fail with the base authorization remedy; following that
remedy must succeed. Run list/resolve; parse the saved records, not just exit 0.
**Postconditions/output:** correctly resolved project; no agent or extra host
access; no hanging input request. Paths/identity may differ from S02, choices may not.

### S04 — Use an existing project

**Feature/promise:** authored needs/recommendations survive checkout setup;
base and component acquisition choices are explicit; the diagnostic offers a
usable remedy if an old lock cannot run.
**Preconditions:** pristine S01 copy and no local checkout record.
**Steps:** runner attempts configuration with the published lock; records exact
failure/success. Test agent classifies a refusal against the documented
compatibility contract. Runner follows a concrete supported remedy, including
explicit regeneration where needed, and records old/new lock hashes. Known
fixture host denials are supplied automatically. Agent-download grants come
from the run's chosen policy; a missing decision is reported once as BLOCKED.
**Postconditions/output:** resolved sample or a specific failure; authored
manifest unchanged. A successful regeneration does not erase an earlier failure
or count as evidence that the original lock was compatible.

### S05 — First ordinary launch

**Feature/promise:** `project run` acquires declared tools, composes the image,
supplies its own runtime, and opens the chosen IDE with the right project.
**Preconditions:** configured checkout, no prior materialization for this case;
required downloads authorized, Docker reachable, desktop agent available.
**Steps:** runner records existing matching images, starts ordinary `project
run` without preview or disabling the update path, waits for the named
container and desktop readiness with a deadline. It captures Docker inspect,
image ENTRYPOINT/CMD, mounted project/state paths and runtime identity. Desktop
agent opens the actual desktop and verifies the selected IDE/project.
**Postconditions/output:** running capsule, matching launcher/runtime identity,
expected IDE, correct writable project mount, no undeclared host-X11/socket or
privilege exposure. A live process alone is insufficient. Preserve failed build
output, including any recurrence of multiline Dockerfile rendering.

### S06 — Useful application work

**Feature/promise:** selected languages and tools work inside the environment.
**Preconditions:** S05 capsule running with pinned public project.
**Steps:** runner executes the existing `04-inside.sh` workload through that
container as its ordinary user, from the actual project mount. TypeScript:
`npm ci`, unit tests, production build. Python: venv, install, sample unittest
suite. FastAPI: Python tests, frontend build and psql availability. Assert Node,
npm and npx work by name, including a child process. Record output and exit
for each command; assert expected build files exist.
**Postconditions/output:** application tests pass and build outputs exist inside
and on the host project mount. Desktop agent separately runs the same command
from the IDE terminal to test that terminal's environment; Docker exec success
alone does not establish the IDE terminal PATH.

### S07 — Edit, debug and render documentation

**Feature/promise:** the IDE supports ordinary development, not merely startup.
**Preconditions:** passing S06 selected Python/TypeScript workload.
**Steps:** desktop agent opens `tests/test_merge.py` in the pinned trading
sample, appends `# RC0 saved through PyCharm`, saves, closes/reopens it; runner
checks exact host bytes. Select `.venv/bin/python`, set a breakpoint on the
`self.assertIs` line in `test_unanimous_positions_are_converged`, debug that
single unittest, inspect `len(verdicts) == 3`, and continue to a passing result. Runner creates `.rc0-smoke/preview.md` with heading `# RC0 preview` and
`.rc0-smoke/preview.svg` with a blue rectangle. Desktop agent opens the Markdown
rendered preview and the SVG image viewer and verifies the heading/rectangle;
capture the rendered views, not just source tabs.
**Postconditions/output:** saved marker, stopped debugger with expected local
value, passing test, rendered preview screenshot. Record the file hash and resolved line number before execution; refuse a source
mismatch rather than putting the breakpoint on a different statement.
**Human work:** none planned; requires desktop-control tooling.

### S08 — Coding agent through its terminal interface

**Feature/promise:** declared agent installs completely, can read/write the
project and execute development commands with its declared persistent state.
**Preconditions:** S06, configured provider account or supported test account.
**Steps:** runner adds a fixture `smoke_arithmetic.py` with `double(n)` raising
NotImplementedError and independent tests for negative/zero/positive integers.
Coding agent receives: "Implement double without changing tests; run the tests."
Runner checks test hashes unchanged, only the allowed implementation changed,
and executes the tests itself. Agent then records a unique session marker.
**Postconditions/output:** independently passing tests, reviewed diff, actual
agent/model identity and persistent-session handle. No inference from --version.
**Human work:** provider login/MFA only if it cannot use an existing authorized
session; the task and verification are automatic.

### S09 — Coding agent through PyCharm ACP

**Feature/promise:** the IDE can start and converse with the agent through ACP;
fresh agent home is correctly wired. This is distinct from CLI execution.
**Preconditions:** S08 establishes provider availability, PyCharm desktop,
a fresh ACP state binding; no copying a working home to conceal initialization.
**Steps:** desktop agent selects the agent in PyCharm, submits a second fixed
fixture task, observes a response and edit/tool execution. Runner independently
checks its tests and file diff as in S08. Save the ACP conversation reference.
**Postconditions/output:** working exchange/edit/test through ACP and identified
state directory. A terminal transcript cannot satisfy this story.

### S10 — Stop and resume

**Feature/promise:** normal exit ends the capsule; project, IDE and declared
agent state persist across a new launch; closing the browser tab does not end it.
**Preconditions:** S07 marker/settings exist for the IDE variant. CLI/ACP continuation
variants additionally require S08/S09 respectively; unavailable provider access
does not block the file/IDE persistence check.
**Steps:** desktop agent closes/reopens the tab and checks the same running
session; exits via IDE menu. Runner waits for launcher success and absence of
that exact container, distinguishing Docker failure from absence. Start again
with identical launcher, checkout and XDG roots, without reinitializing. Desktop
agent checks saved interpreter/settings and resumes the recorded agent session;
runner compares markers/hashes and reruns the workload.
**Postconditions/output:** old container gone, new session usable, persisted
state unchanged as specified; stable inputs reuse the expected formation.
Do not rerun installers or regenerate the lock to make a resume failure pass.

### S11 — Inspect without launch

**Feature/promise:** `--print-command` prepares and reports a usable launch plan
without starting the project's container; stdout contains the command and
preparation diagnostics go to stderr.
**Preconditions:** separate diagnostic checkout; Docker events observable.
**Steps:** runner starts an event capture for its unique container name before
preview, records stdout/stderr and exit, parses shell arguments without executing
them, checks mounts, image and authorization-derived flags against configuration.
End event capture and inspect daemon state. Assert no create/start event for that
project container, even if one was created and removed before the final check.
**Postconditions/output:** correct command, no project start; build containers
are allowed. Transient paths are described honestly; saved command is not reused.

### S12 — Host choices and their scope

**Feature/promise:** recommendations alone do not grant host access; explicit
denial is respected; run-once overrides do not rewrite persistent choices.
**Preconditions:** separate checkouts; Docker available; fixed test choices.
**Steps:** runner records a denied host-browser/host-X11/host-Docker configuration,
launches and inspects actual mounts/settings; checks absence of host X socket,
Xauthority and Docker socket. In the service case grant host Docker/network
explicitly and check the resulting launch. For a run-once supported override,
compare configuration bytes before/after. Regenerate a separate denied case
and assert denial survives an authored recommendation of true.
**Postconditions/output:** exact declared permissions, unchanged persistent
choices after overrides, preserved denial after regeneration. Inspect values,
never print credential contents. No human chooses values during the test.

### S13 — Establish an actual predecessor

**Feature/promise:** valid setup for testing an existing user's upgrade.
**Preconditions:** separately checksum-verified published 0.2.12; S01 sample.
**Steps:** runner initializes and launches with 0.2.12, records explicit grants,
denials and display intent. Desktop agent creates a source marker and an IDE
setting. Exit normally; runner saves checksums and a read-only evidence copy of
configuration and persistent state. Keep the original working directories.
**Postconditions/output:** a proven working 0.2.12 checkout, not a synthetic old
TOML file. If this fails, S14 is BLOCKED, not an RC0 upgrade failure.

### S14 — Upgrade the existing checkout

**Feature/promise:** RC0 can admit/recover the supported predecessor state
without losing user choices, project work or persisted IDE state.
**Preconditions:** exact S13 directories; predecessor stopped.
**Steps:** runner replaces only the invoked executable with RC0 and runs. If a
remedy is required, capture it and use the supported public command; do not
rewrite generated TOML or invent a fresh checkout. Compare semantic grants,
denials, base selection and display intent after any schema change. Desktop
agent checks saved work/settings; runner reruns the project workload and resume.
**Postconditions/output:** working RC0 successor with preserved decisions and
state, or a precise failing recovery step; no blanket permission grants.

### S15 — Change and restore a component version

**Feature/promise:** developer-owned component selection can be previewed,
applied and rolled back without rewriting the project's lock.
**Preconditions:** stopped working checkout, exact alternate component version
and acquisition decision chosen before the story; vendor availability.
**Steps:** runner records original lock/selection/runtime version, uses public
versions preview/select, launches and verifies the actual selected version,
rolls back, launches and verifies the original version. Compare project lock
bytes and saved work. Use the existing component-upgrade script as a starting
point; its fixture IDE alone does not prove the real IDE journey.
**Postconditions/output:** chosen and restored runtime versions, unchanged
project lock and work. No arbitrary "latest" component used mid-test.

### S16 — Full web application

**Feature/promise:** permitted Docker/network use enables a real backend,
frontend and persistent database; tools can work together.
**Preconditions:** S06 FastAPI and S12 explicit service grants; free selected ports.
**Steps:** runner creates a uniquely named PostgreSQL container and records its
image ID; waits on readiness with a deadline. Starts API/frontend as the capsule
user, probes health, creates/updates/reads a uniquely named TODO and checks the
same SQL row. Desktop agent verifies that row in the UI and completes another
TODO. Runner stops/restarts the services/database and checks retained rows.
**Postconditions/output:** correct API/SQL/UI state and persistence; runner stops
only resources recorded as created by this story. No human loops, port editing
or manual service bookkeeping. Fixed fixture credentials have no external use.

### S17 — Keep other workstreams' files intact

**Feature/promise:** send, publish, claim, release and take change only the
intended coordination records, even when invoked from a nested directory.
**Preconditions:** new local bare remote and two disposable clones; no public
GitHub credentials, Docker or GUI required.
**Steps:** runner seeds unrelated mail/state/claim files, records every path's
Git blob ID, then invokes the downloaded CLI from nested and relative paths.
For each operation assert the exact allowed path changes and unchanged blob
IDs everywhere else. Verify claim visibility, publishing preserves the live
claim, release removes only that claim, and taking mail copies exact bytes to
intake/staging before removing only the addressed mailbox item. Check repeated
send/take behavior and append-only remote history; never race a sleep against TTL.
**Postconditions/output:** per-operation comparisons, exact delivered bytes,
no unrelated changes. All activity stays on a filesystem-only test remote.

### S18 — Independent checkouts

**Feature/promise:** checkout-owned configuration and managed state do not leak
between two checkouts of the same project.
**Preconditions:** two S01 copies and fresh checkout registrations.
**Steps:** runner registers distinct checkout names through the public command,
sets opposite supported host-browser choices and distinct source/state markers.
Launch A then B. Desktop agent changes an IDE preference in A and checks B;
runner verifies configuration/state paths and markers. Resume A.
**Postconditions/output:** B did not inherit A's private choice/state; A retains
its own. Any intentionally shared binding must be explicit in the fixture.

### S19 — Useful failure and recovery

**Feature/promise:** invalid/stale configuration fails before launch with a
usable remedy; a failed attempt does not destroy previously saved work.
**Preconditions:** separate working fixture and saved file/configuration hashes.
**Steps:** runner changes an authored need through a supported edit to make the
resolution stale, verifies the ordinary run refuses, follows the reported
resolve/init remedy and reruns. Separately provoke a named-container collision
using a test-owned container and verify the diagnostic and absence of unwanted
replacement. Remove only the collision fixture and retry.
**Postconditions/output:** expected nonzero failures, no silent --force, saved
work retained, offered recovery succeeds. Environment outages are recorded as
BLOCKED unless they demonstrate a product contract failure.

### S20 — Release evidence

**Feature/promise:** test records support an honest release decision (test harness).
**Preconditions:** selected stories have a result or explicit block/defer reason.
**Steps:** runner produces a summary of each story's inputs, actor, attempt,
assertions, logs and result. Test agent maps failures to the maintained bug list,
separates fixture failures from RC0 failures and proposes dispositions. Owner
accepts an exact candidate or requests further work.
**Postconditions/output:** reviewable evidence, unresolved gaps visible, no
failed/blocked story converted to PASS because another story succeeded.

## Automation delivery and human work

This file specifies the complete scoped campaign; the implementation table
must stay honest. Existing shell helpers alone do not implement these contracts.

| Work | Automation decision |
|---|---|
| Creator/default-agent/recommendation/base prompt answers | Automate with a pseudoterminal and exact expected questions (S02). |
| Repeating initialization, configuration and preservation checks | Automate through CLI plus parsed output files (S03/S04/S12). |
| Build/test/service commands, polling, timestamps and results | Runner responsibility; no manual copy/paste or result calculation. |
| IDE typing, menus, breakpoint, preview and gameplay | Desktop-agent responsibility. Tool availability is the current block, not a reason to assign all of it to the owner. |
| Provider password/MFA, personal entitlement acceptance | Owner only if demanded by provider; record BLOCKED until supplied, without exposing secrets. Reuse an authorized session where appropriate. |
| Subjective comfort/readability and final release acceptance | Owner judgment. Objective assertions must already have evidence. |

Every attempt gets a new evidence directory. Expected failure tests pass only
when their rejection and preservation assertions hold. Timeouts are failures
with diagnostics, not successes. Unknown prompts fail; no blind stream of yes/no
answers. A retry retains the first failure and references it. Validation of
scripts is recorded separately from executing these stories against real IDEs.

## Implementation and execution record, 2026-09-23

| Story / part | Implementation | Observed result |
|---|---|---|
| S00/S01 preparation | `00-prepare.sh`; fixed RC0 hash and pinned public Git revisions | Earlier preparation passed; no-Python executable evidence in release overview. |
| S02 terminal questions, base acceptance and refusal | `verify-cli.py --stories init` | PASS against downloaded RC0; saved TOML and fresh resolution checked. |
| S03 missing-answer refusal/remedy and noninteractive equivalence | Same command; reads S02 choices.json | PASS; explicit denials and base grant match prompted configuration. |
| S04 fixed configuration answers | `01-configure.sh`, stdin closed | Fresh, TypeScript, trading and FastAPI configuration completed unattended; whole S04 compatibility story is not yet passed. |
| S17 unrelated files survive workflow operations | `verify-cli.py --stories coordination` | PASS; nine operations, complete tree comparisons, exact staged mail blob, append-only history. |
| Other machine steps | Assigned to runner above; old launch/workload helpers are partial building blocks | NOT IMPLEMENTED as complete story assertions. Do not assign their unfinished automation to the owner. |
| Desktop steps | Assigned to desktop agent above | BLOCKED here: no exposed screen/keyboard/mouse control tool. |

Command: `python3 verify-cli.py RUN_DIRECTORY`; both groups run by default.
Evidence: [saved CLI validation](cli-validation.json); full local attempt
`/tmp/rc0-stories-cli-only-20260923/evidence/cli-pd1vmp8r/`.
Each invocation creates a fresh attempt and stores results.json plus command,
exit, terminal-answer and per-operation Git-tree evidence. Independent S17
still runs if S02 fails; S03 is blocked if its S02 comparison input is absent.

The first harness attempt incorrectly rejected explicit false/none denials as
"extra authorizations". Inspection showed correct denied values, consistent
with the contract's distinction between omission and denial. The assertion
was corrected to require those exact denials, and S03 now supplies them
explicitly for semantic comparison. This was a harness defect, not an RC0
bug; its failed attempt remains alongside the successful one. The first shell
helper update also supplied `network` to a fresh manifest with no such node;
that fixture error was corrected by only supplying it for the public samples
that declare it. No product code or expected host-access promise was changed.
