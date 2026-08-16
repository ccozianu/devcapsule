# Intake: `workflow-improvements`

Work other workstreams have delivered to `workflow-improvements` and that `workflow-improvements` has not yet
accepted, deferred, or rejected.

Senders add one file per item, named `YYYY-MM-DD-<sender-mnemonic>-<slug>.md`,
and deliver it through their own `<mnemonic>/outbox` branch rather than waiting
for their own integration. Senders never remove or reclassify items, and never
edit anything else in this workstream's directory.

`WORKFLOW.md` is the authority for the rest. This file deliberately does not
restate the protocol, so that changing the protocol never requires editing
inside a workstream's directory.

`workflow-improvements` dispositions each item, records the outcome and its reasoning in its own
handoff, then removes the file. This is a queue, not an archive; Git retains
the history. A file still present here has not been dispositioned.

See *Workstream Intake* in `WORKFLOW.md`.
