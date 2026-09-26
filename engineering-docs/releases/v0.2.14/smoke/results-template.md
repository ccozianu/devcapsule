# RC0 story results

Candidate SHA-256:
Platform / Docker version:
Test agent / desktop-control facility:
Evidence root / attempt:

The [story specification](stories.md) defines every precondition and expected
result. The runner's `cli-*/results.json` records implemented CLI assertions.
The test agent fills this summary from evidence, not from script availability.
Use PASS, FAIL, BLOCKED or NOT RUN. Each result names its actual variant/input.
Do not make the owner copy exit codes or reconstruct which files were reused.

| Story | Result | Input evidence / reused output | Assertions and evidence |
|---|---|---|---|
| S00 Exact candidate | NOT RUN | | |
| S01 Pinned samples | NOT RUN | | |
| S02 Prompted initialization | NOT RUN | | |
| S03 Noninteractive initialization | NOT RUN | | |
| S04 Existing project configuration | NOT RUN | | |
| S05 First ordinary launch | NOT RUN | | |
| S06 Application tests/build | NOT RUN | | |
| S07 IDE edit/debug/preview | NOT RUN | | |
| S08 Coding agent CLI task | NOT RUN | | |
| S09 PyCharm ACP task | NOT RUN | | |
| S10 Stop/resume: files and IDE | NOT RUN | | |
| S10 Stop/resume: CLI agent | NOT RUN | | |
| S10 Stop/resume: ACP agent | NOT RUN | | |
| S11 Print command without launch | NOT RUN | | |
| S12 Host access and persistence | NOT RUN | | |
| S13 Working predecessor | NOT RUN | | |
| S14 Upgrade that predecessor | NOT RUN | | |
| S15 Component select/rollback | NOT RUN | | |
| S16 API/database/frontend | NOT RUN | | |
| S17 Preserve other workstreams' files | NOT RUN | | |
| S18 Separate checkout state | NOT RUN | | |
| S19 Failure and offered recovery | NOT RUN | | |
| S20 Candidate assessment | NOT RUN | | |

## Failures, blocks and retries

For each: story/variant, prerequisite outcome, exact command/action, expected
postcondition, actual result, evidence path, whether this is a fixture/tooling
failure or candidate failure, remedy attempted, and next attempt identifier.
Preserve the first failure. Missing credentials or desktop tooling are BLOCKED,
not PASS and not automatically a product failure. Do not include passwords,
provider tokens, login codes or desktop URLs.

## Owner decisions

Record any accepted deferral and its reason, plus acceptance of an exact
candidate. The absence of a human observation is not inferred approval.
