# RC0 smoke observations

Run directory:
Date / tester:
Host OS / WSL2 version if applicable:
Docker context (local host or nested capsule):
Candidate identity: see `version.json`; fixture revisions: see `projects.txt`.

Use **NOT RUN**, **PASS**, **FAIL**, or **BLOCKED**. Add the actual evidence;
a zero launcher exit is not a substitute for observing the IDE. Distinguish
network/provider/license blockage from a product failure, retaining the error.

| Case | Configure / recovery | Preview | IDE opens / edit / run | Normal exit | Resume | Evidence / issue |
|---|---|---|---|---|---|---|
| Fresh VSCodium | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | |
| TypeScript public sample | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | |
| Trading research / PyCharm | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | |
| FastAPI / PyCharm | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | |

| Additional observation | Result | Evidence / issue |
|---|---|---|
| TypeScript game works in browser | NOT RUN | |
| PyCharm Markdown preview (JCEF) | NOT RUN | |
| Agent login and actual edit/test | NOT RUN | Record IDE, agent, model, terminal or ACP; no credentials. |
| Agent session resumes | NOT RUN | |
| PostgreSQL + API + frontend useful work | NOT RUN | |
| PostgreSQL data survives service restart | NOT RUN | |
| Configuration denial survives regeneration | NOT RUN | |

## Failures and recovery

For each: case, exact command, expected result, actual result, exit status,
relevant log path, user-visible remedy, whether that remedy worked, and any
configuration diff. Preserve the original failure even after a successful retry.
Do not include login codes, credentials, full desktop URLs or their tokens.

## Scope still untested

This campaign alone does not prove a running predecessor upgrade, WSL2 unless
actually used, all IDE/agent combinations, managed Docker-in-Docker, GPU bases,
or coordination-branch data preservation. Record additional evidence separately.
