# Work Order: The Manifest's Two Schemas As Classes; `init --regenerate` Migrates

Drafted 2026-10-26 on the owner's direction of the same day: `project init
--regenerate` migrates the manifest to schema 2, and the codebase keeps
schema 1 and schema 2 explicitly represented, as classes. The owner made
this a gate of the final 0.3.0 tag. Workstream: `maintenance`. The design
below is worked out here as asked; the decisions it takes are listed at the
end for the owner to reverse.

Evidence read: `devcapsule-src/devcapsule/configuration/` at `e415e5b`
(`file_formats.py`, `manifest.py`, `manifest_document.py`,
`capabilities.py`, `operations.py`, `owner_commands.py`,
`capability_commands.py`, `model.py`, `fingerprints.py`),
`workflow_bootstrap.py`; the CLI UX order's decisions 11, 19 and 20 and the
capabilities order's retirement of the SDK major; R-CONFIG-001; the schema-1
manifests in evidence: this repository's own, the three sample projects',
the compat fixtures `v0.2.11`, `v026.2` and `v026-formation`, and the AI
Learning bootstrap's manifest as rc3 wrote it; the rc7 run of 2026-10-25.

## Outcome

Reading `manifest_schemas.py` tells a reader what a schema-1 manifest is,
what a schema-2 manifest is, and how one becomes the other, without
reading any other module. No reader elsewhere knows a schema-1 word. The
owner who runs `project init --regenerate` on a schema-1 project gets a
schema-2 manifest beside the regenerated lock, with the leading comment
block kept, and the report says so. A developer who runs anything else
on that project sees the file untouched.

## What is so today

- Schema 1 and schema 2 are one number in one tuple
  (`MANIFEST_SCHEMA_VERSIONS = (1, 2)`); the shape check is the same for
  both. Nothing in the code says what a schema-1 file may contain.
- Schema 1 has two capability forms: `need` (this repository, the samples,
  the compat fixtures) and `required`/`optional` beside an empty
  `[capabilities.sdk-major]` table, as rc3 wrote it (the AI Learning
  bootstrap before the owner's rewrite). `need` may hold an IDE capability
  (`python-ide`); the lock then carries the IDE. The root key
  `workflow-type` stands beside `[workflow]` in two of the files.
- `CapabilityPolicy.read` reads both forms and remembers which through the
  flag `layered`; `current_capability_fields` filters the retired SDK major;
  `WorkflowDeclaration` reads `workflow-type` as a fallback. Three messages
  still speak of `capabilities.need` or "the project need"
  (`operations.py` 1215 and 1277, `authorization.py` 565).
- Writers stamp schema 2 on every owner edit (`owner_commands.py`,
  `capability_commands.py`), each by deep-copying the dict and setting the
  version. `init --regenerate` keeps an existing manifest byte for byte
  (`_prepare_manifest`, "Honored existing"): verified on rc7, only the
  lock's matrix version and base table changed, the manifest stayed at 1.
  The compat tests prove a schema-1 project launches without a rewrite
  (`test_schema_one_ide_in_need_launches_without_rewriting_manifest`).
- Decision 19 of the CLI UX order rules that an untouched schema-1 file is
  never rewritten by an unrelated command. Regeneration is the owner's own
  act on the project's shared files, not an unrelated command; the owner's
  direction of 2026-10-26 settles that it migrates. Non-owner commands stay
  as decision 19 says.

## The design

One new module, `devcapsule/configuration/manifest_schemas.py`, pure, with
four public names. Nothing else in the package defines what a manifest is.

- **`ManifestV1`**, a frozen dataclass. Fields: `project`; the capability
  lists as written, either `need` or `required` plus `optional`, in one
  field whose type says which form the file used; `resolution` (provider
  choices, carried as data); `host`; `configuration_values`; `workflow`;
  `workflow_type` (the root key, or `None`); `extensions`, the tables
  neither schema names, kept opaque (R-CONFIG-001). `ManifestV1.read(document,
  source)` requires `devcapsule-schema-version = 1`, refuses both capability
  forms at once, and refuses `[environment]`, `[recommendations]` and
  `[capabilities.reasons]` by name: those are schema-2 words, and a file
  that uses them says 2. The retired `sdk-major` table is tolerated and
  dropped, with today's note.
- **`ManifestV2`**, a frozen dataclass composed of the values that already
  exist: `project`, `CapabilityPolicy` (required with minimums, optional),
  the reasons, `resolution`, `EnvironmentPolicy`, `Recommendations`,
  `host`, `configuration_values`, `workflow`, `extensions`.
  `ManifestV2.read(document, source)` requires version 2 and refuses
  `capabilities.need` and the root `workflow-type` by name. `sdk-major` is
  tolerated and dropped as on V1, since rc4 wrote schema 2 with it.
  `ManifestV2.document()` returns the mapping in schema 2, the input of the
  one writer, `render_manifest`.
- **`read_manifest(document, source) -> ManifestV1 | ManifestV2`**
  dispatches on the version and refuses any other with today's message.
- **`upgrade(v1, *, is_ide) -> ManifestV2`**, in memory, by these laws.
  `is_ide` is the one catalog question the module needs; the callers pass
  the matrix's predicate.
  1. `need` becomes `required`; `required`, `optional` and the minimums are
     kept.
  2. Every IDE capability leaves the lists. A required one becomes
     `recommendations.ide`. Two required IDEs are refused, naming both and
     `config drop NAME`; an optional IDE is dropped, since every developer
     chooses their own.
  3. The SDK-major table is dropped.
  4. `workflow-type` folds into `[workflow].mode`: taken when `mode` is
     absent, dropped when equal, refused when they disagree.
  5. `host`, `configuration.values`, `resolution`, `[workflow]` and the
     extension tables are carried verbatim. Absent tables stay absent; the
     writer omits what says nothing.
  6. Reading the rendered result gives an equal `ManifestV2`.

Every consumer reads through these classes. `validate_manifest` becomes
`read_manifest`; `Configuration`, the operations, the owner commands and
the fingerprints take a `ManifestV2`, obtained by `upgrade` when the file
is V1, and never write it. Where a consumer still wants a mapping it takes
`document()`. In consequence `CapabilityPolicy.read` reads schema 2 only
and the flag `layered` is deleted; the three messages that say
`capabilities.need` say `required`; `WorkflowDeclaration` keeps its
fallback, since it reads the file on its own for the bootstrap and that
file may be schema 1.

The owner commands stop deep-copying and stamping: each builds its
candidate from `upgrade(...)` or the `ManifestV2` it read, so there is one
migration path and the first owner edit of a schema-1 file is the same
migration `init --regenerate` performs.

## `project init --regenerate`

With an existing schema-1 manifest, the manifest action is **Migrated**:
the text written is `render_manifest(upgrade(v1).document(),
preamble=manifest_preamble(text))`; the report line names the schema and
says that comments outside the leading block were not kept, which is the
writer's existing contract. With a schema-2 manifest, the action stays
**Honored existing**, byte for byte, apart from the recommendation blocks
init already appends. Without `--regenerate`, an existing manifest of
either schema is honored as today: a collaborator's init must not rewrite
the shared file.

The lock regenerated beside a migrated manifest is project-only, as rc4's
init writes it: the IDE that left the requirement is no longer pinned in
it. Every checkout re-resolves on its next `run`, because the manifest's
fingerprint changes with the version, and the resolution is the launch's
own derived artifact since rc4. A developer whose checkout never chose an
IDE gets the recommended one by default, disclosed, not asked (decision
24), so the same IDE starts. Both are proven by tests, not assumed.

## Files that stay schema 1

The compat fixtures are the oracle of what older launchers wrote and stay
as they are. This repository's own manifest, the website's and the three
sample projects' are migrated by the owner with the shipped candidate, by
`init --regenerate` in each, as the release overview already rules for the
repository's own lock.

## Documentation

Two sentences, nothing else under `docs/`: the `init` paragraph of
`docs/reference/cli.md` says `--regenerate` rewrites the lock and migrates
a schema-1 manifest to schema 2, keeping the leading comment block; the
*Existing files and older launchers* section of
`docs/configuration/capabilities.md` says the next owner write or
`init --regenerate` writes schema 2 and removes the SDK-major table. The
changelog, the release overview and the status are the release driver's.

## Tests

- The laws of `upgrade`, one test each, parametrized over the schema-1
  shapes in evidence: `need` with an IDE, `need` without, `required` with
  the empty SDK-major table, `workflow-type` beside `[workflow]`, an
  extension table.
- `ManifestV1.read` refuses `[environment]`, `[recommendations]`,
  `[capabilities.reasons]` and both capability forms; `ManifestV2.read`
  refuses `need` and `workflow-type`; `read_manifest` refuses version 3 and
  the string `"2"`.
- `init --regenerate` on a copy of the `v0.2.11` fixture with a leading
  comment block added: the manifest at
  schema 2, `need` gone, `python-ide` as the IDE recommendation, the
  leading comment block kept, the lock project-only, the report line; a
  second `--regenerate` leaves the manifest's bytes unchanged.
- The existing compat tests stay green unchanged, the no-rewrite test among
  them; the owner-command test that writes schema 2 passes through
  `upgrade`.
- Full gate: `nox -s build` from `devcapsule-src`, both sessions; the
  docs contract check.

## Acceptance evidence

- The gate counts, and `grep -rn 'capabilities.need\|layered' devcapsule`
  returning only `manifest_schemas.py` and `WorkflowDeclaration`'s
  fallback.
- With the executable the gate builds, on a scratch copy of the trading
  sample and on the AI Learning manifest as rc3 wrote it: `init
  --regenerate`, then `config show` and `config check`, the migrated
  manifest quoted in the PR body.
- `git diff --check` clean; one PR to `release-0.3.0`; no word of
  substrate, edge, gen1 or gen2.

## Decisions taken here, for the owner to reverse if wrong

- One module owns both schemas and the migration; the existing value
  classes are composed, not duplicated.
- Each class is strict about the other schema's words; tolerance is for
  unknown tables, not for the other version's vocabulary.
- A required IDE becomes the IDE recommendation; an optional one is
  dropped.
- `workflow-type` folds into `[workflow].mode`; the root key is not a
  schema-2 word.
- `init` without `--regenerate` keeps honoring a schema-1 file.
- Comments outside the leading block are lost on migration, as on every
  write of the one writer; the report says so instead of a second writer
  learning to keep them.
- `layered` is deleted, not kept as a false constant.
- No schema 3: migration is the only thing the number changes.

## Stopping points

Before the implementation brief, on the owner's merge of this order; the
implementer and reviewer pair as for the capabilities order. Before the
final tag, as the overview says: this order's slice ships in a candidate
and the owner's regeneration of the repository's own manifest follows it.
