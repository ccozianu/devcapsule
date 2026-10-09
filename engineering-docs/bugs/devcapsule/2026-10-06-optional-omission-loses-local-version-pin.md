---
status: closed
severity: minor
target: none
owner: component-catalog
opened: 2026-10-06
closed: 2026-10-08
requirements: [R-CONFIG-001, R-UPGRADE-001]
---

# Clearing an optional omission fails to restore a local version-set provider

## Symptom and contract

With an explicit local version set, omitting `browser-automation` removes its
Playwright provider from the persistent selected lock. Clearing `--without`
subsequently leaves Playwright absent. The shared lock still supplies it.
The [configuration guide](../../../docs/configuration/capabilities.md) promises
that clearing omissions restores project enhancements and that retained local
pins survive capability changes. This is a defect in composing those behaviors.

No shared configuration is lost, and required capabilities remain present.
Severity is minor: the developer can explicitly return to project recommendations,
but that changes their version-selection policy and cannot recover the discarded
local pin. That recovery path is supported by source inspection, not an executed
host rollout in this review. No release target is assigned here.

## Environment and evidence

Reproduced 2026-10-06 in branch `ws-component-catalog/intellij-idea`, source commit
`99ff26ac564368427f77773ac0a4c2beaa257eea`, Linux AMD64, using
`devcapsule-src/.venv/bin/python` and the source command adapter. Temporary
project/checkout state is beneath `/opt/devcapsule-gate`; `XDG_CONFIG_HOME` is
isolated. No image, container, vendor download, host launcher replacement or
working-repository configuration mutation is involved.

Run this fixture from the repository root. The direct checkout write represents
an already-selected local version set, following the existing pin-retention unit
test's setup. It is test fixture construction, not an adopter repair procedure.

```python
import os
import tempfile
from pathlib import Path

from devcapsule.configuration import capability_commands as commands
from devcapsule.configuration.documents import (
    canonical_digest, render_document, selected_version_lock,
)
from devcapsule.configuration.storage import (
    checkout_record_paths, load_toml, lock_for,
)

with tempfile.TemporaryDirectory(dir="/opt/devcapsule-gate") as temporary:
    root = Path(temporary) / "project"
    root.mkdir()
    os.environ["XDG_CONFIG_HOME"] = str(Path(temporary) / "config")
    commands.initialize(
        root, name=None, slug=None, creator="mailto:review@example.test",
        mount=None, required=["python"], optional=["browser-automation"],
        majors=[], local=["python-ide"],
    )
    manifest = load_toml(commands.paths(root)[0])
    record = checkout_record_paths(manifest, root)[0]
    checkout = load_toml(record)
    selected = lock_for(root, manifest)[1]
    selected["components"]["playwright"]["version"] = "retained-pin"
    checkout["version-set"] = {
        "format": 1,
        "lock": render_document(selected),
        "recommendation-digest": canonical_digest(
            load_toml(commands.paths(root)[1])
        ),
    }
    record.write_text(render_document(checkout))
    commands.configure(root, without=["browser-automation"])
    print("omitted lock:", sorted(selected_version_lock(
        load_toml(record))["components"]))
    commands.configure(root, without=[])
    print("cleared omissions:", load_toml(record)["capabilities"]["without"])
    print("restored effective lock:", sorted(lock_for(root, manifest)[1]["components"]))
    print("shared provider remains:", "playwright" in
          load_toml(commands.paths(root)[1])["components"])
```

Observed stdout:

```text
omitted lock: ['interactive-surface', 'pycharm']
cleared omissions: []
restored effective lock: ['interactive-surface', 'pycharm']
shared provider remains: True
```

The final read also warns that optional `browser-automation` has missing
supported provider `playwright`. Expected: clearing the omission restores that
provider with the exact retained pin, leaving shared files and host decisions
unchanged. The sentinel version marks metadata preservation; this experiment
does not claim that the sentinel names a downloadable vendor release.

## Cause, verification target and disposition

At the reviewed commit,
[`capability_commands.py:175–186`](https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_commands.py#L175-L186)
uses the current local version lock as source, projects it through the omission
policy, then writes that reduced effective lock into the persistent version set.
The next command has no retained optional pin to restore. This explains the
observed result; no source fix is included in the documentation review.

Add a regression combining the explicit-version-set sentinel fixture with
omit/restore. Assert preservation of persistent pin metadata, restoration of the
effective provider, unchanged shared bytes and unchanged host decisions. Preserve
persistent software intent separately from the effective optional subset, then
rerun the focused policy/version-set suites and required gate before closure.
Do not close this record merely because the existing tests pass.

The [correctness argument](../../implementation-notes/devcapsule/2026-10-06-configuration-correctness.md)
explains which invariants still hold and why the existing tests missed this
interaction. Owner is `component-catalog` because that open workstream owns this
configuration implementation; the follow-up precedes its integration handoff.

## Fix (2026-10-08)

Fixed on review branch `ws-component-catalog/intellij-idea-correctness`, commit
`236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98`, proposed as a pull request into
the workstream branch. The implementation now distinguishes the checkout's
persistent selection (`compose_lock`) from its execution projection
(`usable_lock`); only the projection applies omissions, and both command
writers of a version-set record, the local capability edit and `versions
preview`/`select`, write the selection (`versions rollback` is a recorded limit).
The Codex review of PR #171 found that `select` still consumed the candidate as
the execution lock; commit `e9be77a` makes consent, pinning and preview freshness
act on the projection, with four more regression tests. The regression combining the sentinel
version-set pin with omit and restore is
`tests/test_capability_policy.py::test_omitting_then_restoring_an_optional_keeps_the_version_set_pin`;
the same interaction through `versions preview`/`select` is
`tests/test_version_sets.py::test_version_selection_keeps_an_omitted_optional_pin_for_later_restoration`.
Both failed on the reviewed commit and pass with the fix. The argument is the
[2026-10-08 follow-up note](../../implementation-notes/devcapsule/2026-10-08-configuration-composition-correctness.md).

Close when the owner has merged the review branch and the workstream PR; reopen
if a writer of `version-set.lock` is added that persists an execution
projection, or if `rollback` is changed to compose from known-good records
without preserving omitted optional pins (currently a recorded limit, not a
regression of this fix).

## Closure, 2026-10-08

Closed on the stated condition: the owner merged the review branch through
[PR #171](https://github.com/ccozianu/devcapsule/pull/171) into
`ws-component-catalog/intellij-idea` at `4575eae` and the workstream branch
through [PR #170](https://github.com/ccozianu/devcapsule/pull/170) into `main`
at `6ae1a01`. The reopening conditions above stand unchanged.
