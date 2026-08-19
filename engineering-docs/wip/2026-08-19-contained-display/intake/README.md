# Intake: `contained-display`

Work other workstreams have delivered to `contained-display` and that `contained-display` has not yet
accepted, deferred, or rejected.

Senders add one file per item, named `YYYY-MM-DD-<sender-mnemonic>-<slug>.md`,
and deliver it to `main` promptly rather than waiting for their own
integration. Senders never remove or reclassify items, and never edit anything
else in this workstream's directory.

`contained-display` dispositions each item, records the outcome and its reasoning in its own
handoff, then removes the file. This is a queue, not an archive; Git retains
the history. A file still present here has not been dispositioned.

See *Workstream Intake* in `WORKFLOW.md`.
