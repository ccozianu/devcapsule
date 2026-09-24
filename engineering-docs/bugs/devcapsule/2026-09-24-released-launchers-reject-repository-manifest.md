---
status: confirmed
severity: blocking
target: 0.2.14
owner: maintenance
opened: 2026-09-24
requirements: [R-COMPAT-001, R-RUNTIME-001]
---

# Released launchers reject the repository's own manifest since RC1

The owner reports that `devcapsule project config list` and `config resolve`
fail on a fresh checkout of the DevCapsule repository with:

```text
devcapsule: .../.devcapsule/devcapsule.toml configuration.values.runtime.devcapsule-command.runtime-effect must be one of: docker.memory-limit.
```

Designated a show stopper by the owner on 2026-09-24. Every project command
that loads the manifest fails, including the diagnostic command whose purpose
is to explain the state the user is in.

## Root cause

The message is the runtime-effect validator's exact-membership check, and it
lists every effect the running executable knows. An executable that knows
only `docker.memory-limit` is one built before commit `658749f`:

| Executable | `RUNTIME_EFFECT_TYPES` | Where |
|---|---|---|
| v0.2.12, the latest final release | `docker.memory-limit` only | `project_configuration.py:38`, check at line 262 |
| v0.2.14-rc0 | `docker.memory-limit` only | `configuration/values.py:19` |
| v0.2.14-rc1 and the release branch | adds `devcapsule.command-name` | `configuration/values.py:21` |

Commit `658749f` (2026-09-24, "expose runtime CLI with configurable
development command name", the fix for the
[missing runtime command](2026-09-24-runtime-cli-not-on-path.md)) did two
things at once: it added the effect `devcapsule.command-name` to the
vocabulary, and it declared that effect in this repository's own
`.devcapsule/devcapsule.toml`, recommending `devcapsule0` for development.
PR #136 integrated it into `main` the same day. From that moment every
checkout of `main` or `release-0.2.14` is unreadable by every released
client, because the validator rejects any effect it does not know, and the
message names neither the running version nor the fact that the project
requires a newer one.

The reported failure therefore comes from a 0.2.12 or rc0 executable on the
host `PATH`, not from rc1. The reproduction below shows the exact message
from the published 0.2.12 against this checkout, and success from rc1. It is
still a release defect: the first-session guide sends contributors to the
latest final release, 0.2.12, and that client can no longer open the
project that ships it. The break is the inverse of R-COMPAT-001's direction,
a project change that strands existing clients, but the user experience is
the same one that requirement forbids: nothing the user did, and a refusal
that cannot explain itself.

A second cause made this invisible until the owner hit it: no test or smoke
runs a released client against the repository's manifest. The recursive
dogfood evidence always used the candidate under test.

## Reproduction, 2026-09-24

Published executables, checksums verified, run against this checkout of
`release-0.2.14` at `deaa802`:

| Executable | `project config list` |
|---|---|
| v0.2.12 | the reported message, exit 2 |
| v0.2.14-rc1 | passes manifest validation; reports the unrelated in-capsule inspection condition |
| source build at `deaa802` | same as rc1 |

With `runtime-effect = "devcapsule.command-name"` removed from a copy of the
manifest and isolated XDG state, v0.2.12 lists the configuration and shows
`runtime.devcapsule-command` as an ordinary `unset-optional` string value.
rc1 accepts the same copy.

## Fix

1. **Reserved name.** DevCapsule applies the `devcapsule.command-name` effect
   to a value named `runtime.devcapsule-command` whether or not the
   declaration spells `runtime-effect`; if it does, it must agree. The
   repository manifest omits the attribute, so 0.2.12 and rc0 read it as a
   plain string and ignore it, while rc2 and later apply the effect.
2. **Diagnostic.** An unknown `runtime-effect` names the running DevCapsule
   version, lists the supported effects, and says the project may require a
   newer DevCapsule. This cannot repair 0.2.12, which already shipped, but
   it ends the class for every later addition to the vocabulary.
3. **Guard.** A test pins this repository's manifest to the effect
   vocabulary of the latest released client, so a future declaration cannot
   strand released clients unnoticed. The pinned set moves when a final
   release ships with the new vocabulary.
4. Documentation of the reserved name in the source README.

## Verification needed before closure

- Published v0.2.12 `project config list` and `config resolve` succeed on
  the fixed manifest of `release-0.2.14`.
- The next candidate applies the `devcapsule0` recommendation from the
  reserved name inside a real capsule, with `devcapsule` left free.
- The unknown-effect diagnostic names the version in a source-form run and
  in the built executable.
- The owner's host executable is identified by `devcapsule version`; the
  report is closed only once that executable, whichever it is, opens the
  repository.
