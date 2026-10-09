# Console smoke evidence, 2026-10-09

Deliverable 1 of the capsule web console work order, proven on a locally
built base recipe 10 with the public PEX of revision
`7659c6d8e3efd9084951cd5930d361241a5cd49e` (build mnemonic
`v0.2.16.dev0-local-linux-x86_64`).

- Base image: `devcapsule-base-e2e:webconsole-161638`, id `sha256:3123197fc295ae37fe50c8faf1a15ecee0778935c4395c4370eb0c1b57a3b1da`, built over host networking with
  `images build --type base --recipe ubuntu-24.04`; labels
  `devcapsule.base.recipe-version=10`, `devcapsule.base.webconsole=/opt/devcapsule-webconsole`.
- `tests/e2e/test_built_base.py`: passed; the venv imports the console and
  its dependencies with the network off, and `-m devcapsule_webconsole --help` runs.
- `tests/e2e/test_console_answers.py`: passed. Facts in the two JSON files:
  with the contained display, from `project run` of a fresh codium project,
  and headless, the same image through the runtime's job mode with no
  display section. In both: home 200, configuration page 200, configuration
  document 200 with schema version 1, tokenless request 403, `..` and
  absolute paths 403, a file inside the mount 200.
- `launcher-log-excerpt.txt`: the launcher's announcement of both links and
  both ready lines, tokens redacted; the console child's own start line.
- `headless-docker-run-args.json`: the headless invocation, bind sources
  translated for the host daemon, token redacted.
- `ide-smoke-codium-facts.json`: the IDE smoke on the built base, codium, passed; its new "console answers" fact is 200 and the tokenless probe was 403.
