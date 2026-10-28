# Persistent checkout environment for 0.3.0

## Outcome and authority

The owner requested this slice during AI Learning bootstrap, then directed
maintenance to implement it with Claude Code / Claude Fable 5.1 as the PR
review partner. A developer sets application credentials once on the launcher
host and returns with only `devcapsule project run` in the checkout directory.
This is part of the 0.3.0 candidate cycle, delivered into `release-0.3.0`.
It supports explicit host boundaries under R-PRODUCT-002. Maintenance
coordination follows R-PRODUCT-006.

## Binding decisions

Store a separate environment file for each registered checkout under the
existing XDG configuration namespace. Keep values outside Git, generated
resolutions, configuration snapshots and normal diagnostic output. Use
owner-only directory/file permissions (0700/0600), atomic replacement, and
literal Docker env-file syntax. Plaintext storage is acceptable. Processes
and agents inside the capsule are trusted with the injected environment.
Do not build encryption, a vault, or protection against those processes.

## Deliverables and completion

1. `project config set-env KEY [VALUE]` saves or replaces one variable.
   Omitting VALUE prompts without echo. A supplied value supports scripts
   and ordinary settings; the documentation recommends the prompt for secrets.
2. `project config unset-env KEY` removes a variable, idempotently.
   `project config list-env` lists names and the managed path, never values;
   JSON output carries the same information.
3. `project run` supplies the checkout's managed file to the Docker client
   automatically. No config resolve is needed after an environment change.
   It takes effect in newly created containers, not existing ones. The file
   is not mounted into the capsule. It remains client-local with a remote
   Docker daemon. Other checkouts have independent files.
4. Documentation explains setup, changing/removing values, location,
   precedence and lifecycle. No special AI Learning configuration is needed.

## Implementation decisions

Use the existing registered checkout record as the identity. Require checkout
registration before setting values. Accept ASCII environment identifiers and
literal single-line UTF-8 values, including empty values, spaces, quotes,
`#`, `$` and `=`. Reject CR, LF and NUL without printing the value. Do not
expand variables or interpret shell quoting. Serialize concurrent updates.
The implementor chooses file layout and module boundaries within the existing
configuration architecture.

Docker's explicit environment options (including launcher-owned variables)
win over the managed env-file. A later raw `--env-file` can override values
from the managed file. Existing component secret bindings retain their host
variable requirement. Raw passthrough inline values remain the caller's
responsibility; generalized command-line redaction is outside this slice.
Environment values do not roll back with configuration/version selections.
Deleting/recreating containers retains them. A new checkout registration gets
its own environment; automatic migration or sharing is outside this slice.

## Acceptance evidence

Test actual CLI parsing and persistence, replacement/removal, hidden input
and refusal without a terminal, names-only output, checkout isolation,
permissions, malformed data and failed atomic replacement. Verify launch
wiring with the real command handler and a mocked launcher; prove secret
values are absent from reports, resolutions and successful-run history.
Run the full repository gate. Use fake credentials only in tests. A focused
Docker probe may verify env-file literal semantics and precedence without
building images or starting an IDE. Report any live launch not performed.

Open an implementation PR, then run the prescribed reviewer loop. Give
Claude Fable 5.1 its own checkout and written implementation-review brief.
Assess its diff, merge accepted improvements, repeat the gate, and leave
the final PR for the human to merge. Stop for unavailable credentials or
reviewer access, or a product choice that expands this scope.

## Evidence read before writing

Remote `main` workstream list and release tip `fb1970e` were inspected.
The existing configuration storage identifies records by project creator,
slug and checkout. The `project run` handler passes raw Docker arguments
through the launcher; it also prints those raw arguments. Component secret
bindings only name exported host variables. The known-good history captures
checkout and resolution TOML files explicitly. These contracts permit a
separate managed env-file without changing the project schema or lock.
