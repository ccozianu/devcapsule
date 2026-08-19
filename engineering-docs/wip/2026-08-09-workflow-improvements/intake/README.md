# Intake: `workflow-improvements`

Work other workstreams have delivered to `workflow-improvements` and that
`workflow-improvements` has not yet dispositioned.

Senders add one file per item, named `YYYY-MM-DD-<sender-mnemonic>-<slug>.md`,
and deliver it through their own `<mnemonic>/outbox` branch rather than waiting
for their own integration. Senders never remove or reclassify items, and never
edit anything else in this workstream's directory.

`WORKFLOW.md` is the authority for the rest. This file deliberately does not
restate the protocol, so that changing the protocol never requires editing
inside a workstream's directory.

`workflow-improvements` either acknowledges each item as its own work or
forwards it to `project-management` with a reason, then deletes it from `main`.
A file still present on `main` has not been dispositioned, and this workstream
cannot conclude while any remain.

See *Workstream Intake* in `WORKFLOW.md`.
