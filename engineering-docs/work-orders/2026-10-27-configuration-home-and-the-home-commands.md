# Work Order: One Configuration Home, Named By The Caller, And The Commands That Act On It

Drafted 2026-10-27 in the project-management session, from the owner's
design of the same day, reached in chat after the bug record of 2026-10-25
on the commands that need no project yet live under `project config`. It
scopes the workstation-commands ruling of the 0.3.0 scope recheck
(decision of 2026-10-27, item 2) to one maintenance slice on
`release-0.3.0`, for the next candidate. The pair: Codex, gpt-6-astra,
implements; Claude Code, Claude Fable 5.1, is the review partner, as for
the other slices of the cycle. The decisions this order takes are listed
at the end for the owner to reverse.

Evidence read, all at `origin/release-0.3.0` `0514d50`:
`devcapsule/platforms.py` `XdgHomes`; `configuration/storage.py`,
`configuration/trust.py`, `configuration/workstation.py`;
`commands/project.py`, the `ConfigDefaultCommand`, `ConfigTrustListCommand`,
`ConfigTrustAcceptCommand`, `ConfigTrustWithdrawCommand` and
`ConfigTrustGroup` classes; `commands/_run_flow.py`, the acceptance at the
terminal; `runtime_configuration.py`, the in-capsule guard;
`persistence.py` `StateRoots`; `notifications.py`, the store derivation;
`resolution_matrix.py`, `_ComponentPin` and `component_closure`;
`components/interface.py` `AcquisitionContract` and `locked_artifacts`;
the bug record `engineering-docs/bugs/devcapsule/2026-10-25-workstation-commands-live-under-project-config.md`;
D-0011; the owner's requirement mail of 2026-10-22 on configuration files
declaring their format and minimum reader; the docs pages listed under
*The texts*.

## The owner's design, in their words and ours

Nothing the launcher depends on is global. Gilad Bracha's objection to
`import java.io` is that `java.io` is a global the program never asked
for; the Newspeak answer is that the program takes it as an argument.
Today a DevCapsule user is forced to think of "the workstation's global
state with regard to DevCapsule": the trust record and the defaults live
in a place the user cannot name, and the only way to run two separate
uses of DevCapsule is to move every XDG application along with them.

The correction: everything the launcher reads or writes for itself relates
to one configuration home, which the caller names. By default it is
`$XDG_CONFIG_HOME/devcapsule`, else `$HOME/.config/devcapsule`, exactly as
now; set `DEVCAPSULE_CONFIG_HOME` and it is that directory instead. A user
may keep separate homes for separate uses from one executable. The owner
chose the FHS style over the Oracle style: the executable, one file, lives
anywhere, and the home is named by the environment, not derived from the
executable's path. That not every home can be read by every executable is
a known problem the owner tabled; the home's declared version is the hook
for it.

The commands that act on the home, and need no project, move out of
`project config` into a `home` group. The word "workstation" goes away
with them: what was "this workstation" is "this DevCapsule home", which is
precise where the old word was not, since the record was never the
machine's and the prompt already said "this OS user account".

## Outcome

1. `devcapsule home trust accept CHANNEL`, `home trust withdraw CHANNEL`,
   `home trust list`, `home default memory|cpus VALUE|none` and
   `home show` run from any directory, with no project in sight, and act
   on the home the launcher was given.
2. `DEVCAPSULE_CONFIG_HOME=/some/dir devcapsule …` reads and writes
   nothing of the launcher's own outside `/some/dir`: configuration,
   state, cache and the checkouts' persistent data all under it. Unset,
   the four XDG defaults apply as today.
3. The home's settings are one file, `settings.toml`, that declares its
   format and the minimum DevCapsule that reads it; a launcher older than
   that minimum refuses the home by name before any other diagnosis and
   before any write.
4. The "once per workstation" blocks of the AI Learning setup script read
   as they are meant: four `devcapsule home …` lines, then the project.
5. No text the user sees, no file the launcher writes, and no code name
   says "workstation".

## What is so today

- `XdgHomes.from_environment` is the one derivation of the launcher's
  four directories: config, data, state, cache, each the XDG variable's
  value or its default under `HOME`, plus a `devcapsule` segment. No
  DevCapsule-named variable exists. Every caller goes through it:
  `storage.config_root`, `StateRoots.from_environment`,
  `materialization`'s cache root, `history`, `version_sets`, and
  `notifications`, which takes `state.parent.resolve() / "devcapsule"`
  for its no-follow reasons.
- The config root holds `workstation.toml` (the `defaults` table, schema
  integer `devcapsule-workstation-schema-version = 1`), `trust.toml` (the
  `channels` tables, `devcapsule-trust-schema-version = 1`) and the
  checkout records under `projects/`. `load_workstation` already merges
  the two files into one in-memory document with the trust under a
  `trust` table, and every reader takes that merged document.
- The four commands sit under `project config` and the `project` group
  discovers a project before dispatching, so from a directory without one
  they exit 2; the bug record has the evidence on rc7. `default` and
  `trust withdraw` read nothing from the project. `trust accept` derives
  the channel from the project's lock through `channels_for`: the base
  channel from the lock's base reference, and each vendor component's
  channel from its `AcquisitionContract` plus the HTTPS origins of its
  pinned artifacts on this platform, read from the component's lock
  table. `trust list` is the project's view and needs the lock.
- The acceptance at the terminal in `project run` writes the same record
  through `write_trust`; `--trust CHANNEL` on `run` does too.
- Inside a capsule the launcher's records are mounted read-only;
  `require_launcher` refuses a mutating command with "This command needs
  launcher-owned configuration or state. Inside this capsule that
  configuration is read-only. Run outside the capsule: …" and prints the
  command to run.
- The scope is named five ways: "this workstation" in the group help and
  D-0011's title, "once per computer" in `_run_flow.py`, "this OS user
  account on this computer" in the acceptance prompt and the
  software-approvals page, "this account's" in the withdraw help, "per
  user" in D-0011's decision 1 and "per workstation, under the launcher's
  config root" in its decision 3.
- The file format rule the owner stated on 2026-10-22, each file states
  its format and the minimum DevCapsule that reads it, is implemented
  nowhere yet; every file has only its schema integer.

## The design

### The home

One variable, `DEVCAPSULE_CONFIG_HOME`. `XdgHomes.from_environment`
stays the one derivation and gains the rule: when the variable is set and
nonempty, config is that directory, and data, state and cache are
`data/`, `state/` and `cache/` under it; when unset, the four XDG
defaults as today, unchanged byte for byte so no existing user sees a
difference. The variable's value is expanded for `~` and resolved; a
relative path is relative to the current directory at startup, as every
other path argument is. Nothing else in the launcher reads the variable:
the places that need a directory keep asking `XdgHomes`, and
`notifications`' own derivation follows the same rule.

The home is created on first write, mode `0700` for the directory,
`0600` for `settings.toml`, as `atomic_write` already does for files. A
read of a home that does not exist is an empty home, not an error, as
`load_trust` and `load_workstation` behave today.

A `--config-home PATH` option is not added. The environment is the
injection point the owner named; a flag would be a second one.

### `settings.toml`

One file replaces `workstation.toml` and `trust.toml`:

```toml
devcapsule-settings-schema-version = 1
minimum-devcapsule = "0.3.0"

[defaults]
cpus = 4
memory = "8GiB"

[trust.channels.devcapsule-base]
vendor = "DevCapsule"
origins = ["docker.io/mycodespaceai/devcapsule-base", "https://devcapsule.mycodespace.ai"]
integrity = "the SHA-256 digest the launcher pins"
accepted = "2026-10-27T20:14:03Z"
```

The channel tables keep the fields `render_trust` writes today, including
`terms-url` when the channel has one. The `defaults` table keeps the
normalized values `WorkstationDefaults.document` writes today. The reader
is the merged document the code already uses, so the in-memory shape does
not change; what changes is that one file is read and written, and the
two schema integers become one.

The two header fields are the first instance of the 2026-10-22
requirement:

- `devcapsule-settings-schema-version` is the format, an integer, `1`.
  A reader that knows only `1` refuses any other value as every file
  does today.
- `minimum-devcapsule` is the lowest launcher version that can read this
  file, a release version string. A launcher whose version is lower
  refuses the home with one message naming the home's path, the version
  the file requires, the launcher's own version, and where to get the
  release, before any other diagnosis and before any write. A writer
  raises the field only when it writes vocabulary an older reader cannot
  honour, and never rewrites a file it did not change. On creation it is
  this launcher's release version with any candidate suffix removed,
  `0.3.0` for every 0.3.0 candidate.

The candidates rc1 to rc8 wrote `workstation.toml` and `trust.toml`. The
0.3.0 launcher reads neither and does not migrate them: a home set up on
a candidate loses its accepted channels and defaults, and the user
accepts and sets them again. No released client is affected; 0.2.15 had
neither record. The two old files are left in place, not deleted, since
the launcher does not delete what it did not write.

### The `home` group

A new top-level group, `devcapsule home`, with the help "This DevCapsule
home: what it trusts, its defaults, where it is." Its commands:

| Command | Does |
|---|---|
| `home show` | Prints the home's path and how it was chosen (the variable, `XDG_CONFIG_HOME`, or the default), the two header fields, the defaults, and the accepted channels with their acceptance dates. Exit 0 on an empty home. |
| `home trust list` | The channels this home has accepted, any project: id, vendor, product, origins, accepted date. Empty list, exit 0, when none. |
| `home trust accept CHANNEL` | Records the acceptance of one channel the launcher knows, after printing its definition and the terms sentence the terminal prompt prints today, and asking `[y/N]` unless `--yes`. |
| `home trust withdraw CHANNEL` | Removes the channel's acceptance; exit 0 and says so when it was not accepted. |
| `home default memory\|cpus VALUE\|none` | Sets or removes the home's default, with the values `normalize_launcher_value` accepts today. |

The four commands move; they are not copied. `project config default`,
`project config trust accept` and `project config trust withdraw` are
deleted from the `config` group, their classes removed, by the project's
rule that a replaced spelling is deleted, not aliased. `project config
trust list` stays, as the project's view: this project's channels and
whether this home trusts each; its help says "this home" and its "Scope:"
line names the home's path.

`home` commands run from any directory and do no project discovery. The
`project` group's `--path` does not apply to them.

### The channel source for a project-less accept

`home trust accept` cannot read a lock. It takes the channel definition
from the launcher itself:

- the base channel, `devcapsule-base`, is the constant `channels_for`
  already builds from `BASE_REPOSITORY` and `BASE_ORIGIN`; it needs no
  pin;
- a vendor component's channel is built the way `channels_for` builds it
  from a lock, with the component's lock table taken from the embedded
  matrix's pin of that component for this platform, the `_ComponentPin`
  `lock_table` the matrix uses to render a lock. The contract, the
  product, the terms URL and the origins come out the same as they would
  from a lock the same matrix wrote.

The channels the command knows are therefore the base plus every
component in the embedded matrix that has an `AcquisitionContract` and
pinned artifacts for this platform. `home trust accept` with an unknown
id exits 2 and lists the ids it knows. A channel whose origins differ
between the matrix's pin and a project's lock is a different channel by
D-0011's rule already, and the project's `trust list` says so; nothing
new is needed for it.

The refactoring is one function that yields the channel for a component
id and a lock table, which both the lock path and the matrix path call.

### `project run` and the terminal

The acceptance at the terminal, and `run --trust CHANNEL`, keep working
and write `settings.toml`. The prompt's text changes from "Accept for
this user account on this computer? [y/N]" to "Accept for this DevCapsule
home? [y/N]", and the terms sentence from "every version and every
project for this OS user account on this computer. Anyone sharing this
account uses this acceptance." to "every version and every project
launched from this DevCapsule home, `<path>`. Anyone who uses this home
uses this acceptance."

The hint `require_launcher` prints inside a capsule names the new
spelling for the moved commands.

### Inside a capsule

The mounted read-only configuration is the home the capsule sees.
`home show` and `home trust list` answer from it. The three mutating
`home` commands refuse with the existing message and the launcher
command to run outside. `DEVCAPSULE_CONFIG_HOME` set inside a capsule is
honoured like any other directory: an agent that wants its own home for
a nested use gets one.

### The texts

Every occurrence of "workstation", "this computer", "this OS user
account" and "once per computer" that names this scope becomes the home,
in: `docs/reference/cli.md` (the `home` group's table, the `run` row, the
`project list` row, the config table rows that move out), `docs/configuration/software-approvals.md`,
`docs/configuration/resource-limits.md`, `docs/configuration/index.md`,
`docs/configuration/project-versus-personal.md`,
`docs/configuration/capabilities.md`, `docs/getting-started/first-session.md`,
`docs/reference/configuration-nodes.md`, and the new section the
configuration docs need: where the home is, `DEVCAPSULE_CONFIG_HOME`,
what is under it, `settings.toml` and its two header fields. The
docs-contract page count follows.

D-0011 is amended, not superseded: the title's "Once Per Workstation"
becomes "Once Per Configuration Home", the file is renamed to match,
decision 1's "per user" and decision 3's "per workstation, under the
launcher's config root" both become "per DevCapsule home, in its
`settings.toml`", and a dated amendment note at the end records this
order as the reason. D-0010's one reference follows.

In code, the names that carry the concept are renamed with it:
`WorkstationTrust` to `HomeTrust`, `WorkstationDefaults` to
`HomeDefaults`, `configuration/workstation.py` to `configuration/home.py`,
`load_workstation`/`write_workstation` to `load_settings`/`write_settings`,
`write_trust` folded into `write_settings`, the `workstation` field of the
run-flow state and the `Documents` tuple to `home`, and
`WORKSTATION_CAPABILITY_DEFAULTS` to `HOME_CAPABILITY_DEFAULTS`. The
compat resource files under `tests/resources/compat/` are records of what
older clients wrote and keep their text. This rename is one commit of its
own, mechanical, so the review can read it apart from the behaviour.

## Tests

Unit tests under `devcapsule-src/tests/`, in the files that already
cover each piece:

1. `XdgHomes`: unset variable gives the four XDG paths as today, with and
   without each XDG variable; set gives config at the path and the three
   subdirectories; empty string counts as unset; `~` expands.
2. `settings.toml`: an empty home reads as empty; a file with both
   tables round-trips; schema `2` refuses; `minimum-devcapsule` above the
   launcher's version refuses with the message naming path, required and
   own version, before any write, proven by a write command that leaves
   the file byte-identical; a write of unchanged content does not touch
   the file; the minimum field is `0.3.0` on a file a candidate creates.
3. The `home` group: each command from a directory with no project and
   no `--path`; `show` on an empty home and a full one; `trust accept`
   for the base, for `claude-code` from the matrix pin, for an unknown
   id; `--yes` and the `N` answer; `withdraw` of an accepted and of an
   unaccepted channel; `default` set, replace, `none`, bad value; every
   mutating one inside a synthetic capsule context refuses and names the
   outside command with the new spelling.
4. The channel equality: the channel `home trust accept claude-code`
   records equals the channel `channels_for` derives from a lock the
   embedded matrix writes for the same platform, field by field.
5. `project config trust list` reports accepted and unaccepted channels
   from `settings.toml`; `project run` at the terminal writes the
   acceptance into `settings.toml`; `run --trust` too.
6. The deleted spellings: `project config default`, `project config
   trust accept` and `project config trust withdraw` are unknown to the
   parser, exit 2.
7. The word test: no file under `devcapsule-src/devcapsule/`,
   `devcapsule-src/tests/` or `docs/` contains "workstation", except the
   records under `tests/resources/compat/`; a test asserts it on the tree.

The integration test `tests/integration/test_pex_runtime.py` keeps its
coverage with the new spellings. The full gate, `nox -s build` and the
console session, from the project venv with the scratch under
`/opt/devcapsule-gate/`, before the final push.

## Acceptance evidence

Quoted in the pull request body:

1. From an empty directory with a throwaway `DEVCAPSULE_CONFIG_HOME`:
   `home show`, the four setup-script lines in their new spelling,
   `home show` again, and `cat "$DEVCAPSULE_CONFIG_HOME/settings.toml"`.
2. The same four lines with the variable unset, showing the default path
   under `~/.config/devcapsule`, then `home trust withdraw` and `home
   default memory none` restoring the state, and the file afterwards.
3. `find "$DEVCAPSULE_CONFIG_HOME"` after a `project run --print-command`
   of a checkout, showing `data/`, `state/` and `cache/` under the home and
   nothing new under `~/.local` or `~/.cache`.
4. A `settings.toml` edited to `minimum-devcapsule = "9.0.0"`: the
   refusal message from `home show` and from `home default cpus 2`, and
   the file unchanged.
5. Inside the maintenance capsule, with the runtime context: `home show`,
   `home trust list`, and the refusal of `home trust accept
   devcapsule-base`.

## Decisions taken here, for the owner to reverse if wrong

1. The variable is `DEVCAPSULE_CONFIG_HOME`; when set, data, state and
   cache are subdirectories of it, so one directory is one installation.
   The owner named the variable; the subdirectories are this order's
   reading of "one config tree".
2. No `--config-home` flag; the environment is the only injection point.
3. `settings.toml` holds defaults and trust; `workstation.toml` and
   `trust.toml` are not read, not migrated, not deleted.
4. The two header fields, `devcapsule-settings-schema-version` and
   `minimum-devcapsule`, and the refusal rule for a too-old launcher; the
   first instance of the 2026-10-22 requirement, which the other files
   get later under their own order.
5. The `home` group's five commands and the deletion of the three
   `project config` spellings; `project config trust list` stays.
6. `home trust accept` asks `[y/N]` and prints the definition first,
   with `--yes` to skip; the setup script uses `--yes`.
7. The channel source for a project-less accept is the embedded matrix's
   pin for this platform.
8. The prompt and terms texts as given under *`project run` and the
   terminal*.
9. D-0011 amended in place with a renamed file; the code names renamed
   with the concept, in one mechanical commit.
10. The candidates' homes are not migrated.

## Stopping points

The implementor stops and reports, without working around it, if: the
matrix's pin for a component on the gate's platform yields origins that
differ from what a lock written by the same matrix yields, which would
make decision 7 wrong; the no-follow derivation in `notifications` cannot
take the subdirectory rule without changing its security property; or
the rename of D-0011's file breaks a link the docs contract checks.
