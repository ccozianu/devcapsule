# The configuration channel

The console's one way to change the next launch. Answer 7 of the CLI UX
redesign work order (`engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`,
2026-10-24): the launcher is the only writer of the user's records, so the
console and the launcher communicate through a directory the launcher
mounts into the capsule for the run, writable, at
`/run/devcapsule-configuration` (`--configuration`,
`$DEVCAPSULE_CONSOLE_CONFIGURATION`). Answer 16: the launcher writes the
listing it computed at launch into the same directory, so inspection inside
the capsule shows the truth with its time.

Every file is JSON and complete when visible: the writer creates it under
a temporary name in the directory and renames it into place. A reader
never sees a partial file.

## Files

| File | Writer | Content |
| --- | --- | --- |
| `listing.json` | launcher, once, at launch | `{"format": 1, "at": "<ISO 8601 UTC>", "listing": <the config show --json document>}` |
| `NNNNNN-VERB.request.json` | console | `{"format": 1, "requested": "<time>", "arguments": [<config tokens>]}` |
| `NNNNNN-VERB.result.json` | launcher, beside the request | `{"format": 1, "status": "recorded" \| "refused" \| "deferred", "text": "<what happened>", "at": "<time>"}` |

`NNNNNN` is the console's sequence number, six digits from `000001`; `VERB`
is the request's first token, lower case. The launcher handles requests in
name order and never reuses a name. A request is the argument tokens of
one `devcapsule project config` command, without `--path`: the launcher
names the project.

## What the launcher does with a request

- **Recorded at once**, with the command's own validation and output, when
  the verb keeps the checkout's own choices or narrows what the next launch
  reaches: `ide`, `agent`, `tool`, `set`, `deny`, `forget`, `env set`,
  `env unset`, `unbind`, `trust withdraw`, `docker-args clear`.
- **Deferred** when the verb widens what the next launch reaches:
  `authorize`, `trust accept`, `bind`, `docker-args set`. Anything running
  inside the capsule can write to the mounted directory, not only the
  console, so a widening is never taken from it unconfirmed. The launcher
  keeps it as the console's request beside the checkout record; the user
  confirms or discards it on the host, at the next `devcapsule project run`
  or with `devcapsule project config console apply|discard ID`.
- **Refused**, with the reason, for anything else: a read-only verb, a
  workstation default, an owner's command, an unknown verb, a malformed
  document.

The console checks the verb before writing, so a typo is refused on the
page; the launcher validates the whole command again. The result's `text`
is what the command printed, or the reason.

## Routes

- `GET /api/configuration`: the runtime CLI's `config list --json`, which
  inside a capsule with the channel is the launcher's listing at launch
  with `at`, `console-requests` and `launcher-command`; each pending row
  gains `request`, the config tokens its host command implies; `channel`
  says whether the channel is mounted.
- `GET /api/configuration/requests`: every request of this run with its
  result, in order.
- `POST /api/configuration/requests`, same origin only, body
  `{"command": "<config tokens>"}`: writes one request; `201` with the
  request, `422` with the reason, `403` from another origin, `413` when
  too large, `500` when the directory cannot be written.

Inside the capsule, `devcapsule project config show` prints the same
listing labelled "At launch, <time>" and, below it, the requests asked on
the console since, each with the launcher's result.
