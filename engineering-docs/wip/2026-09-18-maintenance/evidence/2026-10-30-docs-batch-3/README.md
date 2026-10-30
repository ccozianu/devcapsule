# User Documentation 0.3.0 CLI Alignment — Batch 3 Verification Ledger

Workstream: `maintenance`
Work order: [`2026-10-30-user-docs-0-3-0-cli-alignment.md`](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/work-orders/2026-10-30-user-docs-0-3-0-cli-alignment.md)
Slice branch: `ws-maintenance/0.3.0-docs-batch-3-onboarding-project-containment` (target `release-0.3.0`)
Implementor pair: `Antigravity (Gemini 4 Argon (High))`
Review partner: `Codex (gpt-6-astra)`

## Scope (10 `docs/*.md` files across `docs/README.md`, `getting-started/`, `your-project/`, and `containment/`; 2 `status: planned` stubs retired)

| # | File | Stub retired? | Key 0.3.0 CLI & prose changes | Verification status |
|---|---|---|---|---|
| 1 | `docs/README.md` | No | Preserved `role: overview`, retired the obsolete `"Pages marked coming soon..."` paragraph, updated section summaries to cover web console, component freshness, cleanup, and `reference/cli.md`, and tightened adopter prose. | Verified against `docs/` section tree and `website/CONTRACT.md` |
| 2 | `docs/getting-started/install.md` | No | Preserved `#check-your-computer`, clarified `.pex` system-Python (`3.10+`) usage without host virtualenvs, and explained adding `$HOME/.local/bin` to `PATH` alongside `~/.local/bin/devcapsule` examples. | Verified against `{{download_url}}`/`{{tag}}`/`{{release_url}}` placeholders and `website.sh check` |
| 3 | `docs/getting-started/first-session.md` | No | Preserved `role: getting-started`, `/docs/guides/first-session/` alias, and `#1-make-a-first-workspace`; aligned interactive `project init` prompt wording (`antigravity-agent` `[yes]` default, `[none]` host recommendations, `[default]` base consent), documented both desktop and recipe-11+ web console loopback URLs, and fixed misleading `"running processes restart"` claim. | Verified against interactive `pty` probe of `project init --require node --ide frontend-ide` and `_launcher.py` |
| 4 | `docs/getting-started/stop-and-come-back.md` | No | Clarified IDE exit vs. single/double `Ctrl+C` shutdown, desktop + web console tab behavior, and corrected misleading `"Processes you had running, servers or watchers, restart"` wording to state that container processes stop on exit and must be started again. | Verified against `_launcher.py` and `sessions/what-persists.md` |
| 5 | `docs/your-project/existing-repository.md` | No | Preserved `role: your-project` and `/docs/guides/your-project/` alias; added `eclipse-ide` and `dotnet-ide` (`rider`) rows to the stack/IDE table, clarified `project checkout register NAME` and `config show`/`config check` non-mutating behavior, and replaced `~/.local/bin/` prefixes with `devcapsule`. | Verified against `commands/project.py` and `resolution_matrix.py` |
| 6 | `docs/your-project/new-project.md` | No | Expanded stack/IDE options (`python-ide`, `java-ide`, `eclipse-ide`, `dotnet-ide`, component-name IDE aliases), documented `antigravity-agent` default prompt vs. `init --with` / `config add`, and replaced `~/.local/bin/` prefixes. | Verified against `commands/project.py` and `operations.py` |
| 7 | `docs/your-project/declare-needs.md` | **Yes** (`status: planned` removed) | Authored complete `0.3.0` page covering `.devcapsule/devcapsule.toml` (schema `2`) and `.devcapsule/devcapsule.<platform>.lock`, all 17 catalog capabilities by category, `require` (`NAME>=VERSION`) vs. `offer` vs. `drop`, `require/offer env`, `[configuration.values]`, recommendations vs. permissions, `init --regenerate`, and `config check --manifest --lock`. | Verified against `resolution_matrix.py`, `owner_commands.py`, `values.py`, and `commands/project.py` |
| 8 | `docs/your-project/services-and-ports.md` | **Yes** (`status: planned` removed) | Authored complete `0.3.0` page covering reaching capsule web servers (in-capsule browser/Playwright, `--publish=127.0.0.1:PORT:PORT` via `run --` or `docker-args set` with `0.0.0.0` bind, and `authorize network host`) and running databases/services (host services + `host.docker.internal:host-gateway` + `postgresql-client`/`env set`, `docker-daemon host-socket` sibling-container caveats, and persistent in-capsule SQLite/DuckDB paths). | Verified against `_launcher.py` (`LAUNCHER_OWNED_DOCKER_OPTIONS`), `docker_arguments.py`, and `authorization.py` |
| 9 | `docs/containment/the-boundary.md` | No | Preserved `role: containment`; added recipe-11+ web console loopback port and read-only `settings.toml` mount to default boundary, listed `vscode-download`, `claude-code-download`, and `antigravity-download` explicitly, noted `--cap-drop ALL` / `no-new-privileges`, and tightened prose. | Verified against `_launcher.py` and `authorization.py` |
| 10 | `docs/containment/granting-and-withdrawing.md` | No | Replaced `~/.local/bin/` prefixes, distinguished `config deny` (the 5 host-access nodes only) from `config authorize <vendor>-download false`, documented `default` and `none` keywords across every authorization node, and added vendor download rows to the reference table. | Verified against `commands/project.py` (`ConfigDenyCommand`) and `authorization.py` |

## Validation Gate

- `git diff --name-only origin/release-0.3.0 -- docs/`: 10 files (`<= 10` batch limit satisfied; `docs/versions.yaml` untouched).
- `git grep -n '^status: planned' -- docs/README.md docs/getting-started/ docs/your-project/ docs/containment/`: 0 matches (`declare-needs.md` and `services-and-ports.md` stubs retired).
- `(cd devcapsule-src && .venv/bin/python -m nox -s docs-contract)`: passed (`192` pages including `18` aliases).
- `./scripts/website.sh build && ./scripts/website.sh check`: passed (`23` website tests, `196` HTML pages, `14,446` local links/assets/anchors).
- `(cd devcapsule-src && .venv/bin/pytest -q -k "release_docs")`: `92 passed`.
