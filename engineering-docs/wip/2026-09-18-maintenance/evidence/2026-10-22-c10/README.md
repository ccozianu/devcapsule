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
