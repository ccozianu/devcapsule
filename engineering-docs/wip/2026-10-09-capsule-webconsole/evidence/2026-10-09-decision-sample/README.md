# Decision page sample, 2026-10-09

The first use of deliverable 5 in miniature: two items of the
project-management intake pass, as a markdown table, turned into a decision
document with `python -m devcapsule_webconsole.decisions from-table`, served
by the console from a decisions directory, answered in a browser driven by
Playwright, and written back as the answer document.

- `table.md`: the table an agent wrote.
- `2026-10-09-sample-pass.json`: the decision document built from it.
- `2026-10-09-sample-pass.answer.json`: what the console wrote when the page
  was submitted: one option for the single-choice item with a note, two for
  the multiple-choice item, and an overall note.
- Screenshots `decisions-page.png` and `decisions-answered.png` under
  `../2026-10-09-console-pages/`.

- `hand-off.txt`: slice 8's hand-off text for the same decision, printed by
  `python -m devcapsule_webconsole.decisions hand-off` with a sample origin
  and token: the numbered items an agent pastes into a chat, ending with
  the link into the console.

This directory is evidence of the mechanism. The sample decision was not
the project-management pass itself and nothing here is a record of a
decision taken.
