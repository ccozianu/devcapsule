# Intake: `maintenance`

Work other workstreams have delivered to `maintenance` and that `maintenance`
has not yet dispositioned.

Senders add one file per item, named `YYYY-MM-DD-<sender-mnemonic>-<slug>.md`,
and deliver it through their own `<mnemonic>/outbox` branch rather than waiting
for their own integration. Senders never remove or reclassify items, and never
edit anything else in this workstream's directory.

Bug records are not intake items. A bug is handed to this workstream by setting
its `owner` field to `maintenance`; see *Bug Intake* in `WORKFLOW.md`. Intake
is for everything else: questions, handovers with context, and work that is
not a bug.

`WORKFLOW.md` is the authority for the rest. See *Workstream Intake*.
