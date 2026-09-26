# Blocking bug filed for 0.2.15: `project init` discards answers on a late `--authorize` error

Sent: 2026-09-26
From: `project-management`, at the owner's direction, from the owner's own
first-session attempt with the released 0.2.14 launcher.

Bug record, owner `maintenance`, severity `blocking`, target `0.2.15`:
`engineering-docs/bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md`
on `ws-project-management/coordination` at `58b296e`. It reaches `main` with
project-management's next integration; this mail is so you can start before
that. The record traces the order of operations in `initialize_project`
(prompts and manifest/lock writes precede the first node-name check of the
supplied answers; `record.write()` comes last) and names the smallest fix and
the verification target.

The owner rated it a show stopper: the first command an adopter runs must not
throw away the consent it just asked for. Sequencing within 0.2.15 is yours.

## The owner's transcript, verbatim

```text
devcapsule project init --name chessclub-website --need frontend-ide --need node   --creator https://github.com/ccozianu --need frontend-ide --need antigravity-agent --need claude-code-agent --need codex-agent --authorize base-image default --authorize network host --authorize docker host
Recommend docker-daemon = host-socket for every checkout? (host-socket/none) [none]: host-socket
Justification recorded beside the docker-daemon recommendation: My old laptop needs that
Justification recorded beside the network recommendation: My old laptop needs that
Recommend development-sudo = true for every checkout? (true/none) [none]:
Recommend host-browser = true for every checkout? (true/none) [none]: true
Justification recorded beside the host-browser recommendation: because
Download checksum-pinned Antigravity CLI 1.1.24 directly from Google during local materialization, subject to https://antigravity.google/terms/. Authorize? (yes/no) [yes]:
Download checksum-pinned Claude Code 2.1.261 directly from Anthropic during local materialization, subject to https://www.anthropic.com/legal/commercial-terms. Authorize? (yes/no) [yes]:
devcapsule: Configuration node 'docker' is not declared by this project and lock; declared nodes: antigravity-cli/gemini-api-key, antigravity-cli/home, antigravity-download, base-image, claude-code-download, claude-code/home, codex/home, codex/openai-api-key, codium/cache, codium/extensions, codium/user-data, development-sudo, docker-daemon, home, host-browser, host-x11, network.
$ devcapsule project run
devcapsule: Local resolution is missing; run 'devcapsule project config resolve'.
$ devcapsule version
DevCapsule v0.2.14 (package 0.2.14)
Source revision: abb785d7ad4069606fd3ab84009ca8efeabc22b9
$ devcapsule project config resolve
devcapsule: Configuration review: decisions required.
antigravity-download: missing-required; recorded: unanswered; recommended: true
  An explicit decision is required before this environment can run. DevCapsule 0.2.14 and later ask for every vendor download; earlier clients did not record this one.
base-image: missing-required; recorded: unanswered; recommended: v0.2.12-rc5 — docker.io/mycodespaceai/devcapsule-base@sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c
claude-code-download: missing-required; recorded: unanswered; recommended: true
Display: no host-x11 decision is recorded. A base with contained-display support uses its browser desktop by default; an older base uses host X11. ...
```
