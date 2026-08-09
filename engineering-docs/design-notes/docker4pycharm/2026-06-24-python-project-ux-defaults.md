# Decision: Python Project UX Defaults

Date: 2026-06-24

Status: implemented in repository files, pending image rebuild and manual validation

## Context

The current v0 image was used against a separate ordinary Python project. The
agent in that project reported that the environment was workable, but a few
small defaults would reduce friction:

- Commits could fall back to a guessed container Git identity when the launcher
  was not passed explicit Git author flags.
- `python` was missing even though `python3` was present.
- The `file` diagnostic utility was missing.
- New Python projects benefited from a basic `.gitignore` and process handoff
  seed.
- Psycopg dependency policy should be explicit without bundling full database
  services into the IDE image.

## Decision

Keep the image lightweight, but add small Python-project defaults:

- Install `python-is-python3`, so `python` resolves to `python3`.
- Install `file`.
- Keep `lsof` and `iproute2` in the baseline for port/process inspection.
- Install `libpq5` and `libpq-dev` so projects that choose non-binary Psycopg
  builds can compile against system `libpq`.
- Do not install or start PostgreSQL, Redis, Conda, Poetry, pre-commit stacks,
  multiple linters, or heavy orchestration by default.
- Add `docker4ide-bootstrap-project`, an idempotent helper that creates missing
  `AGENTS.md`, `REQUIREMENTS.md`, a README handoff section,
  `docs/`, the categorized `engineering-docs/` structure, and basic Python
  `.gitignore` entries in a mounted project.
- Make the launcher automatically read only host global Git `user.name` and
  `user.email` strings when available. Do not mount host `~/.gitconfig`.
  Provide `--no-git-identity-from-host` as the opt-out.

## Verification

Static checks to run before closing this change:

```bash
bash -n docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/bootstrap-project.sh
shellcheck docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/bootstrap-project.sh
git diff --check
./docker4pycharm/run-pycharm-container.sh --help
```

Image/runtime checks after rebuilding:

```bash
command -v python
python --version
command -v file
file --version
dpkg -l libpq5 libpq-dev python-is-python3
docker4ide-bootstrap-project --help
```

Manual validation after rebuilding:

- Launch an ordinary Python project without Git identity flags and confirm the
  container Git config has the host global author values when those values are
  configured on the host.
- Launch with `--no-git-identity-from-host` and confirm the host author values
  are not imported.
- Run `docker4ide-bootstrap-project` in a scratch project and confirm it
  creates only the expected docs/directories, requirements register, bug
  template, and `.gitignore` entries.

## Reopen If

Reopen if commits fall back to the generated container identity during normal
launches with host global Git identity configured, if the helper overwrites
project documentation unexpectedly, if `python` no longer resolves to
`python3`, or if a future package addition starts bundled services by default.
