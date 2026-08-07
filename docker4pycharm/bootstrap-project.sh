#!/usr/bin/env bash
set -euo pipefail

TARGET="${PROJECT_PATH:-$PWD}"

usage() {
  cat <<'USAGE'
Usage:
  docker4ide-bootstrap-project [--project DIR]

Creates a small, idempotent process/documentation seed in a mounted project:
  AGENTS.md
  REQUIREMENTS.md
  README.md current-state handoff section
  docs/
  engineering-docs/requirements/
  engineering-docs/specifications/
  engineering-docs/decisions/
  engineering-docs/design-notes/
  engineering-docs/implementation-notes/
  engineering-docs/workstreams/
  engineering-docs/bugs/
  engineering-docs/completed-tasks/
  engineering-docs/session-records/
  basic Python .gitignore entries

Existing files are preserved. Missing .gitignore entries and a missing README
handoff section are appended.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project) TARGET="${2:?missing value for --project}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ ! -d "$TARGET" ]; then
  echo "Project directory does not exist: $TARGET" >&2
  exit 1
fi

TARGET="$(cd "$TARGET" && pwd)"
cd "$TARGET"

mkdir -p \
  docs \
  engineering-docs/requirements \
  engineering-docs/specifications \
  engineering-docs/decisions \
  engineering-docs/design-notes \
  engineering-docs/implementation-notes \
  engineering-docs/workstreams \
  engineering-docs/bugs \
  engineering-docs/completed-tasks \
  engineering-docs/session-records

append_missing_gitignore_entry() {
  local entry="$1"

  touch .gitignore
  if ! grep -Fxq "$entry" .gitignore; then
    printf '%s\n' "$entry" >> .gitignore
  fi
}

if [ ! -f .gitignore ]; then
  cat > .gitignore <<'EOF_GITIGNORE'
# Python / Docker4IDE defaults
__pycache__/
*.py[cod]
*$py.class
.Python
.venv/
venv/
env/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.idea/
EOF_GITIGNORE
else
  if ! grep -Fq "Python / Docker4IDE defaults" .gitignore; then
    printf '\n# Python / Docker4IDE defaults\n' >> .gitignore
  fi
  append_missing_gitignore_entry "__pycache__/"
  append_missing_gitignore_entry "*.py[cod]"
  append_missing_gitignore_entry "*\$py.class"
  append_missing_gitignore_entry ".Python"
  append_missing_gitignore_entry ".venv/"
  append_missing_gitignore_entry "venv/"
  append_missing_gitignore_entry "env/"
  append_missing_gitignore_entry ".pytest_cache/"
  append_missing_gitignore_entry ".mypy_cache/"
  append_missing_gitignore_entry ".ruff_cache/"
  append_missing_gitignore_entry ".coverage"
  append_missing_gitignore_entry "htmlcov/"
  append_missing_gitignore_entry ".idea/"
fi

if [ ! -f AGENTS.md ]; then
  cat > AGENTS.md <<'EOF_AGENTS'
# Agent Instructions

Before starting work in this repository, read the project brief at:

```text
README.md
```

Pay special attention to the final current-state and next-step section. Then
read any target-specific or handoff documents referenced there.

After reading the required documents, acknowledge that you understand the
project purpose, requirements register, current state, and planned next step
before proceeding.

Treat `REQUIREMENTS.md` as the requirement overview and index. Read detailed
records under `engineering-docs/requirements/` only as needed for the task.

If the brief defines a planned next step, state that next step to the user
before proceeding.

If the brief does not define a planned next step, ask the user to choose the
next step to work on.

When completing a stage, retiring a task, changing project state materially, or
ending a session, update the final section of `README.md` so the next
agent/model pair can resume from the current state.
EOF_AGENTS
fi

if [ ! -f REQUIREMENTS.md ]; then
  cat > REQUIREMENTS.md <<'EOF_REQUIREMENTS'
# Requirements Register

This file is the project-level overview and index for accepted requirements.
Canonical detailed records belong under `engineering-docs/requirements/`.
This overview does not replace the active task list in `README.md`; it gives
tasks, bugs, and engineering notes stable requirement IDs to reference.

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: code or docs exist, but validation is incomplete.
- `repo-validated`: static checks, smoke tests, or automated checks passed.
- `manually validated`: the user or agent validated behavior in the running
  product.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Priority Bands

- `MVP`: required for the first useful version.
- `current stabilization`: required before closing the current stabilization
  pass.
- `later`: useful, but not required for the current target.

## Requirement Template

```markdown
### R-AREA-000: Short Name

Statement: ...

Priority: MVP | current stabilization | later
Status: proposed | accepted | implemented | repo-validated | manually validated | deferred | rejected

Implementation:
- ...

Validation:
- ...

Related:
- ...
```

Every active task, bug, or completed-task record should include a
`Requirements:` line when it materially implements, validates, changes, defers,
or reinterprets a requirement.

## Current Requirements

### R-BOOT-001: Define Initial Requirements

Statement: Replace this bootstrap placeholder with the project's real accepted
requirements.

Priority: current stabilization
Status: proposed

Implementation:
- `REQUIREMENTS.md`

Validation:
- Future agents can map active tasks and bugs to stable requirement IDs.

Related:
- `README.md`
EOF_REQUIREMENTS
fi

if [ ! -f engineering-docs/bugs/_template.md ]; then
  cat > engineering-docs/bugs/_template.md <<'EOF_BUG_TEMPLATE'
# Bug: Short Title

Date opened:

Status: open | reproduced | fixed | cannot reproduce | retired

Requirements:

- R-...

## Symptom

What the user or agent observed.

## Environment

- Image:
- Launcher command:
- Project path/mount:
- Host assumptions:
- Relevant package/app versions:

## Reproduction

Manual steps:

1. ...

Expected:

Actual:

Reproducibility: always | intermittent | once | unknown

## Evidence

Logs, stack traces, screenshots, commands, timestamps.
Do not include secrets.

## Hypothesis

Current best explanation, with uncertainty.

## Verification Target

Cheapest check that should catch this later:

- Automated test:
- Script/check:
- Manual validation:

## Fix Notes

Files changed, decision made, tradeoffs.

## Close Criteria

Done means:
Verification:
Reopen if:
EOF_BUG_TEMPLATE
fi

if [ ! -f README.md ]; then
  project_name="$(basename "$TARGET")"
  cat > README.md <<EOF_README
# $project_name

## Current State And Next Step

This section is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, retiring a task, or
ending a session.

Current stage: Initial project orientation.

Current status: Process documentation was bootstrapped. Replace this with the
real project purpose, requirements, current state, and constraints.

When resuming the project, read these files in order:

1. \`README.md\`
2. \`REQUIREMENTS.md\`
3. \`engineering-docs/bugs/\` for active bug records, if relevant
4. \`engineering-docs/implementation-notes/\`

Planned next items:

1. Inspect the project and define the first narrow task.
   Requirements: R-BOOT-001
   Done means: the project purpose, validation command, and next useful task
   are recorded here.
   Verification: run the cheapest available check or document why none exists.
   Reopen if: future sessions cannot tell what to do next from this handoff.
EOF_README
elif ! grep -Eq '^## Current State( And Next Step)?$|^## Current State And Next Step$' README.md; then
  cat >> README.md <<'EOF_README_APPEND'

## Current State And Next Step

This section is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, retiring a task, or
ending a session.

Current stage: Initial project orientation.

Current status: Process documentation was bootstrapped. Replace this with the
real current state and constraints.

When resuming the project, read these files in order:

1. `README.md`
2. `REQUIREMENTS.md`
3. `engineering-docs/bugs/` for active bug records, if relevant
4. `engineering-docs/implementation-notes/`

Planned next items:

1. Inspect the project and define the first narrow task.
   Requirements: R-BOOT-001
   Done means: the project purpose, validation command, and next useful task
   are recorded here.
   Verification: run the cheapest available check or document why none exists.
   Reopen if: future sessions cannot tell what to do next from this handoff.
EOF_README_APPEND
fi

cat <<EOF_DONE
Bootstrapped Docker4IDE project process in:
  $TARGET

Created or updated:
  AGENTS.md
  README.md
  REQUIREMENTS.md
  .gitignore
  docs/
  engineering-docs/requirements/
  engineering-docs/specifications/
  engineering-docs/decisions/
  engineering-docs/design-notes/
  engineering-docs/implementation-notes/
  engineering-docs/workstreams/
  engineering-docs/bugs/
  engineering-docs/bugs/_template.md
  engineering-docs/completed-tasks/
  engineering-docs/session-records/
EOF_DONE
