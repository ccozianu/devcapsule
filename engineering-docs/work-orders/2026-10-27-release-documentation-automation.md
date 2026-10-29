# Work Order: The Documentation Obligations Of A Release, Checked And Run By The Tag

Drafted 2026-10-27 in the project-management session, from the owner's
direction of the same day on C20. It scopes C20 for 0.3.0 to one slice:
after this order, the documentation of a release reaches the test site
without anyone remembering to do anything, and a release cannot be tagged,
or a site built, in a state that contradicts the downloads. Workstream:
`maintenance`, on `release-0.3.0`, as the other dogfooding slices of the
cycle. The pair: Codex, gpt-6-astra, implements; Claude Code, Claude Fable
5.1, is the review partner, by the owner's word of 2026-10-27. The
decisions this order takes are listed at the end for the owner to reverse.

Evidence read: `.github/workflows/release-pex.yml` and `website.yml` at
`8d41fab`; `devcapsule-src/scripts/release-protocol.py`,
`prepare-promotion.py`, `release-manifest.py` and
`tests/test_release_protocol.py`; `docs/versions.yaml` on `main` and on
`release-0.3.0`; the content–website contract, version 1, sections 4.1,
4.2, 8 and 9; R-DOCS-003 part 2, the four statuses and the lifecycle; the
runbook's *Documentation Is Part Of The Release* and its steps 3, 6 and 7;
`WORKFLOW-LOCAL.md`, the `docs-<version>` ref; the website's
`scripts/contract.mjs`, `checkDeclaredVersion` and `resolveSource`, at the
pinned revision `2bcfe6e`; the design issue of 2026-09-28; the maintenance
mail of 2026-10-18 on the content check failing on a release branch; the
GitHub releases `v0.2.12`, `v0.2.14`, `v0.2.15` and `v0.3.0-rc8`, each
final or prerelease as expected, each with the three assets.

## Outcome

When the owner pushes the final tag `v0.3.0`:

1. the backend refuses the tag, before anything is public, unless the
   versions file at the tag's commit promotes 0.3.0, the release notes
   exist at the tag, and the `docs-0.3.0` branch carries the tag's
   documentation;
2. the backend publishes the pex with `notes.md` as the release body;
3. the backend then builds the test site from `main`, which already holds
   the promoted versions file through the pre-final merge;
4. the owner reads the test site and promotes it to production in the
   website repository, the one step that stays by hand.

And at any other moment, a website build refuses to serve a version whose
download does not exist, so a build run in the window between the
pre-final merge and the tag fails harmlessly.

## What is so today

- The backend creates every release with GitHub's generated notes, the
  commit list. For a final release the operator replaces the body with
  `engineering-docs/releases/vX.Y.Z/notes.md` by hand. Nothing refuses a
  final tag when the file is missing; the runbook's step 6 says not to tag
  before it exists.
- The website workflow runs on manual dispatch only, in two modes. The
  test site is this repository's GitHub Pages, deployed by the dispatch
  with mode `production`, origin `https://test-devcapsule.mycodespace.ai`
  and base path `/`. Production is the owner's run in the website
  repository, from a candidate the test deployment packaged.
- `docs/versions.yaml` on `main` is edited by hand after the final tag:
  `current` moves, the new version is listed as `supported`, the previous
  ones are demoted. R-DOCS-003 states the lifecycle: `development` from
  the cut, `supported` at the final tag, `deprecated` when the next final
  release ships, `unsupported` one release later, at most one `supported`
  and one `deprecated` at a time. 0.2.15 shipped on 2026-09-27 and the
  site described 0.2.12 until the migration of the following week.
- The content check reads any checkout as `main` and requires the `devel`
  entry's source to declare a development version. On `release-0.3.0`
  the source declares 0.3.0, so the gate passes only with
  `source-version: "0.3.0"` on the `devel` entry, the form the check
  itself names. Maintenance added the line on 2026-10-18 as a judgment and
  mailed the gap to project-management. On `main`, which declares
  0.3.1.dev0, the line is harmless: the check accepts a development
  version first.
- `docs-<version>` is forked from the final tag by the local rule, so it
  cannot be named in the versions file before the tag exists, and the
  content check refuses a source it cannot resolve.
- The final-tag job already reads something from the release directory:
  the acceptance record `engineering-docs/releases/vX.Y.Z.json`, through
  `release-protocol.py`, which also tells the workflow whether the tag is
  a candidate. The scripts under `devcapsule-src/scripts/` are plain
  Python with `argparse`, tested by loading the file as a module. No YAML
  parser is among the development dependencies.

## The design

One script, `devcapsule-src/scripts/release-docs.py`, owns the
documentation obligations of a release. It mutates no Git ref, as
`release-protocol.py` does not. Four subcommands, each usable by the
operator and by the workflows:

- **`promote X.Y.Z`**, run on the release branch before the final tag,
  edits `docs/versions.yaml` in place: `current` becomes `X.Y.Z`; an entry
  `X.Y.Z` with `source: docs-X.Y.Z` and `status: supported` is inserted
  after the `devel` entry; the previous `supported` version becomes
  `deprecated`; every `deprecated` version becomes `unsupported`; the
  `devel` entry's `source-version` is set to `X.Y.Z`. `--hold VERSION`,
  repeatable, keeps a named version at its present status; the owner's
  exception at release time. The command refuses when `X.Y.Z` is already
  listed, when the checkout's `devcapsule-src/pyproject.toml` does not
  declare `X.Y.Z`, so that it runs on the right branch, when the file's
  `contract` is not 1, or when the result would hold two `supported`
  versions. It prints the lifecycle moves it made.
- **`check X.Y.Z`**, run by the final-tag job at the tag's commit, and by
  the operator before pushing the tag: `current` is `X.Y.Z`; the `X.Y.Z`
  entry is `supported` with source `docs-X.Y.Z`; no other version is
  `supported`; `engineering-docs/releases/vX.Y.Z/notes.md` exists, is not
  empty, and contains no `<...>` placeholder. Exit status 1 with every
  failing condition named.
- **`notes X.Y.Z`** prints the release body: `notes.md` without its front
  matter. The job passes it to `gh release create --notes-file`.
- **`published`** reads `docs/versions.yaml` and, for every entry whose
  status is not `development`, requires the GitHub release `v<version>`
  to exist, be neither draft nor prerelease, and carry `devcapsule.pex`.
  The release state comes from `gh release view` through a callable the
  tests replace. Exit status 1 naming each version without a download.
  Run by the website workflow before its build.

The file is read and written with PyYAML, added to the development
dependencies and pinned by `pip-compile` as the others are, with its type
stubs for mypy. The writer emits the whole file from the parsed content
behind the fixed header comment; the `notice` is kept as the folded block
it is; `note` and `legacy` fields are carried per entry. Comments inside
the version list are not kept, as with the manifest writer; the header is
the only comment the file has had.

### The release workflow, `release-pex.yml`

On the final-tag path only, `RELEASE_PRERELEASE == 'false'`:

1. **Verify the documentation obligations**, a step after *Verify the
   selected tag and revision* and before *Verify accepted candidate
   assets*: `release-docs.py check X.Y.Z`; then
   `git fetch origin refs/heads/docs-X.Y.Z` and
   `git diff --quiet FETCH_HEAD "$RELEASE_TAG" -- docs/`, so the branch the
   site builds from carries exactly the tag's documentation. Any failure
   ends the job here, with nothing created on GitHub. The operator fixes
   the branch, which may mean a new pre-final merge, and pushes the tag
   again; the workflow's recovery path already tolerates a re-run.
2. **Stage the verified release** passes `--notes-file` with the output of
   `release-docs.py notes X.Y.Z` in place of `--generate-notes`.
   Candidates keep the generated notes.
3. **Build the test website**, a step after *Publish the complete
   release*: `gh workflow run website.yml --ref main -f mode=production
   -f site_origin=https://test-devcapsule.mycodespace.ai -f base_path=/`.
   The workflow's permissions gain `actions: write` for this one call.
   The step summary names the dispatched run.

The candidate path is unchanged. The final-only steps therefore run for
the first time at the final tag, as the existing accepted-candidate
verification does; the checks run before publication, so a failure costs
a second push of the tag and nothing else.

### The website workflow, `website.yml`

One step after the checkout and before the build: install the pinned
PyYAML and run `python3 devcapsule-src/scripts/release-docs.py published`
with `GH_TOKEN` set to the workflow token. The job fails naming the
version without a download. The step runs in both modes; a preview of a
site that names a missing download is as wrong as a deployment of it.

### The rules that change with it

- **`WORKFLOW-LOCAL.md`, the `docs-<version>` ref**, item 2: the branch is
  forked from the release branch at promotion, before the final tag, by
  the operator's `git push origin HEAD:refs/heads/docs-X.Y.Z` right after
  the promotion commit; its `docs/` tree equals the final tag's, which the
  final-tag job verifies. Items 3 to 6 stand. The version's source in the
  manifest is this branch from the start, so the content check resolves
  it on every branch.
- **The content–website contract, section 4.2**, the sentence that makes
  the 0.2.12 case the field's only intended use: `source-version` on the
  `devel` entry names the release most recently promoted, so that a
  release branch, whose source declares the release version, passes the
  check that reads every checkout as `main`. The website's check needs no
  change; the copy in this repository is amended and the amendment goes
  to the website repository as the producer's proposal, as section 11a
  did. This closes the maintenance mail of 2026-10-18: the line is the
  documented practice, written by the helper, removed by nobody.
- **The runbook**, *Documentation Is Part Of The Release* and steps 3, 6
  and 7: obligation 2's "the operator pastes it" becomes the job's
  `--notes-file`; obligation 3's "a follow-up in the 0.2.16 planning"
  becomes the job's dispatch; step 6 names `release-docs.py check` as the
  operator's last command before the tag; step 7's "then promote the
  version in `docs/versions.yaml` on `main`" moves before the tag, as
  `release-docs.py promote` on the release branch, followed by the
  `docs-X.Y.Z` push and the pre-final merge. Production promotion stays
  the owner's run in the website repository, after the test site.
- **The 0.3.0 release overview** records the slice and the order of the
  final steps as the runbook now has them.

### The 0.3.0 sequence, concretely

1. The slice merges into `release-0.3.0` and rides the next candidate, so
   the candidate's tag runs the changed workflow on its unchanged path.
2. With the scope settled, the driver writes `notes.md` from the changelog
   and runs `release-docs.py promote 0.3.0` on the release branch; commits
   both; pushes `docs-0.3.0` at that commit. The gate's content check
   passes on the branch.
3. The pre-final merge carries both to `main`. `main` now lists 0.3.0 as
   current; a website build in this window fails on `published`.
4. The acceptance record, the final tag, the backend: the checks, the pex,
   the body, the test site.
5. The owner reads the test site and promotes it.

## Tests

- `tests/test_release_docs.py`, loading the script as
  `test_release_protocol.py` does. `promote`: the lifecycle on the file
  as `main` has it today, parametrized with and without `--hold 0.2.15`;
  the refusals, one each; a second `promote` of the same version refused;
  the output read back equals the input plus the moves, the `notice`
  folded block and the `note` fields intact. `check`: each condition
  failing alone, named in the output. `notes`: the front matter stripped,
  the placeholder refused. `published`: the release state injected; a
  draft, a prerelease, a missing asset and a missing release each named;
  the `devel` entry skipped.
- The workflow files are not executable in a test. The implementer
  validates them with `actionlint` if present on the capsule, and
  otherwise by reading; the PR body says which.
- Full gate: `nox -s build` from `devcapsule-src`, both sessions; the
  docs contract check on the branch after a trial `promote` run and
  reverted, with the output quoted in the PR body.

## Acceptance evidence

- The gate counts; `release-docs.py promote 0.3.0` on a scratch copy of
  the release branch's versions file, the diff quoted in the PR body;
  `check 0.3.0` on the same copy, before and after a `notes.md` stub.
- `published` against the real releases from the capsule, through `gh`:
  passes on `main`'s file today; fails naming 0.3.0 on the promoted copy.
- `git diff --check` clean; one PR to `release-0.3.0`; the commit
  messages name the component and the evidence.

## Decisions taken here, for the owner to reverse if wrong

- The lifecycle applies on the day: 0.2.15 becomes deprecated, 0.2.14 and
  0.2.12 unsupported, when 0.3.0 ships. `--hold` exists for the owner's
  exception; none is planned.
- The promotion happens on the release branch before the final tag and
  reaches `main` by the pre-final merge, not by a pull request the tag
  job opens. The final-tag job checks, it does not edit.
- `docs-X.Y.Z` is forked before the tag, at the promotion commit, and
  verified equal to the tag in `docs/`; the branch is never moved.
- `source-version` on the `devel` entry is written by the helper and
  names the last promoted release; the contract's wording follows.
- PyYAML joins the development dependencies rather than a parser of our
  own for a file the contract describes in YAML.
- The test site is built by the final-tag job's dispatch, not by a push
  trigger on `main`, so the site changes only after the download exists.
- `published` guards both website modes.
- The helper refuses rather than repairs: a malformed file, a wrong
  branch, two supported versions are errors for a human, not cases to
  handle.
- The website trigger on the tag and the manifest promotion were the two
  pieces of C20 proposed for 0.3.1 earlier in the session; this order
  takes both, since the owner's ordering made each a few lines.

## Stopping points

Before the implementation brief, on the owner's merge of this order into
`main`; then the dispatch to the pair in this session. Before the
candidate that carries the slice. Before the final tag, where the owner
runs `promote`, or asks the driver to, and reads the moves it prints.
