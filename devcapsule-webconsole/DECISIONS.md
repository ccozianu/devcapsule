# Decision pages: the contract between an agent and the console

Deliverable 5 of the capsule web console work order. An agent inside the
capsule hands the human a decision with several options as a page in the
console. The human reads the records cited beside each option, chooses, and
the choice is written where the agent reads it back. The agent then records
the decision in the normal files and discards the page. The page is never a
record itself.

## Where the files live

Decisions live in one directory of the capsule's writable state:

```text
$XDG_STATE_HOME/devcapsule/decisions/      (inside a capsule: /home/devcapsule/.local/state/devcapsule/decisions)
```

The console reads that directory; `--decisions DIR` or
`$DEVCAPSULE_CONSOLE_DECISIONS` names another one. The directory is not a
record: nothing under it is committed, and the agent deletes a decision and
its answer once it has recorded the outcome.

An agent asks by writing `<id>.json`. The console answers by writing
`<id>.answer.json` beside it. `<id>` is lowercase letters, digits and
hyphens, at most 100 characters, and is the file's stem.

## The decision document, `<id>.json`

```json
{
  "format": 1,
  "id": "2026-10-09-intake-pass",
  "title": "Intake disposition pass",
  "asked-by": "project-management",
  "asked-at": "2026-10-09T18:00:00+00:00",
  "context": "Thirty-nine items wait in intake. Decide each one.\n\nMarkdown, rendered.",
  "items": [
    {
      "key": "2026-09-06-component-catalog-development-blog",
      "title": "Component catalog: a development blog",
      "summary": "Markdown, rendered beside the options.",
      "records": ["engineering-docs/wip/2026-08-09-project-management/intake/2026-09-06-component-catalog-development-blog.md"],
      "options": [
        {"key": "accept", "label": "Accept", "summary": "Take it as a task."},
        {"key": "decline", "label": "Decline", "summary": "Close it with a reason."},
        {"key": "defer", "label": "Defer", "summary": "Leave it in intake."}
      ],
      "multiple": false
    }
  ]
}
```

- `format` is 1. A reader refuses another value.
- `items` has at least one item. One decision with one item is the simple
  case; an intake pass has many. Each item has a unique `key` with the same
  grammar as `<id>`, a `title`, at least two `options` with unique keys, and
  optionally a `summary` in markdown, `records` (paths inside the project
  mount, shown as links to the records page) and `multiple` (several
  options may be chosen; default false).
- `context` is markdown, shown above the items. `asked-by` names the
  workstream or agent; `asked-at` is an ISO 8601 timestamp.

A different agent can produce this document from a markdown table with
`python -m devcapsule_webconsole.decisions from-table TABLE.md --id ID
--title TITLE --asked-by NAME > ID.json`. The table has a header row; the
columns `key` and `title` are required, `summary`, `records` (paths
separated by spaces) and `options` (`key:Label` pairs separated by commas)
are optional, and an item without `options` gets accept, decline and defer.

## The answer document, `<id>.answer.json`

```json
{
  "format": 1,
  "id": "2026-10-09-intake-pass",
  "answered-at": "2026-10-09T18:12:40+00:00",
  "answers": {
    "2026-09-06-component-catalog-development-blog": {"chosen": ["accept"], "note": "Good for the website."}
  },
  "note": "Everything else next week."
}
```

- The console writes it atomically when the human submits the page, and
  overwrites it when the human submits again; the latest answer stands
  until the agent reads it.
- `answers` holds one entry per item the human answered, by item key, with
  the chosen option keys and an optional note. An item the human left
  unanswered is absent. `note` is the human's overall note.
- The console validates each chosen key against the item's options and
  refuses a single-choice item with several choices.

## What the agent does with the answer

Read `<id>.answer.json`, record each outcome in the normal files, the
status file, the decision log or the intake dispositions, then delete both
files. The console shows the decision as answered until then. The console
never deletes a decision or an answer.

## What the console does and does not do

- `GET /decisions` lists the decisions in the directory, answered or not.
- `GET /decisions/<id>` renders one: the context, every item with its
  summary, its records as links and its options, and the answer when there
  is one.
- `POST /api/decisions/<id>/answer` is the console's one write: it writes
  the answer document. It accepts a same-origin request only and refuses a
  body that names an unknown item or option.
- Nothing else writes. The decision pages are the only place the console
  changes anything, as the work order allows.
