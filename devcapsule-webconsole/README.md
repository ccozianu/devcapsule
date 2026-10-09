# DevCapsule web console

The capsule web console shows a running capsule as web pages: what the
`devcapsule` commands report about the capsule and its project. It is a
separate process from the runtime, started and supervised by it, and it
imports none of the runtime's internals. Its API is the runtime CLI's
`--json` output, read by running the command. See requirement
`R-CONSOLE-001` and the work order
`engineering-docs/work-orders/2026-10-09-capsule-webconsole.md`.

## Boundaries

- Every request carries the run token or is refused. The token arrives once
  in the URL the launcher prints, and the console answers with a cookie so
  the pages' links and requests carry it from then on.
- File reads resolve inside the project mount only. A path that escapes
  it, by `..`, by an absolute path or by a symbolic link, is refused.
- The console changes nothing: every route is `GET`. The processes page
  reads psutil and the cgroup; it never signals a process.
- Records render in the browser with `markdown-it` and DOT with `viz.js`,
  both vendored under `devcapsule_webconsole/static/vendor/` with their
  provenance in `VENDORED.md`; no build step, no Node in the capsule. Raw
  HTML in a record is not rendered. Raw files carry a sandbox policy and
  `nosniff`; an opened SVG cannot use the console origin. DOT output is an
  image, so its links are inactive. Record headings have fragment targets;
  relative URL paths are decoded before resolution inside the project.

## Running it on a host

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install -e . --no-deps
printf '%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(24))')" > /tmp/console-token
.venv/bin/python -m devcapsule_webconsole --project /path/to/checkout \
    --cli ~/.local/bin/devcapsule --token-file /tmp/console-token --port 8080
```

Then open `http://127.0.0.1:8080/?token=$(cat /tmp/console-token)`.

## Checks

From `devcapsule-src`: `.venv/bin/python -m nox -s webconsole` runs this
package's type check and tests in their own environment, built from
`requirements-dev.txt`. The build gate runs it too.

`requirements.txt` and `requirements-dev.txt` are hash-pinned with
`pip-compile --generate-hashes` from the `.in` files beside them; the base
image recipe installs the runtime set from them.
