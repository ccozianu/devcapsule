# C10 evidence: the interrupted fresh-workspace launch, 2026-10-22

`interrupted-launch-terminal.log` is the launcher's terminal output of
`tests/e2e/test_interrupted_launch.py`, run inside this capsule against the
executable the gate built from `ws-maintenance/0.3.0-first-session-summary`
and the local recipe-11 base, on the lightest surface, VSCodium. The test
initialized a fresh project, launched it in its own process group, waited
for the desktop, and sent SIGINT to the group as a terminal does. The
launcher printed the interrupt line, the result line and the path of every
log file of the session, exited 130, and the container was gone; the IDE's
own output is in its file and not in this transcript. Run tokens are
redacted. `interrupted-launch-facts.json` is the test's record of the exit
code. The run took 18 seconds because the VSCodium formation was cached.

After the review PR #246 was merged into the slice at `1c905ec`, the test
ran again against the executable the gate built from that merge: passed
in 13 seconds, exit code 130, the same lines. `brief-pr244-1.md` and
`round1-pr244-1.md` are the briefs the review partner, the Antigravity and
Gemini 4 Argon (High) pair, received; Antigravity's print mode took the
brief on standard input behind a one-line `-p` instruction, with the model
flag before `-p`.
