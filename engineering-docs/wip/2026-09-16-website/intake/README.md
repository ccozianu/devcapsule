# Intake: `website`

Work taken from this workstream's mailbox and not yet decided. Follow
[The Coordination Branch in WORKFLOW.md](../../../../WORKFLOW.md#the-coordination-branch):
send items with `devcapsule workflow mail send website <file>`; take them at
session start and before pausing with
`devcapsule workflow mail take --workstream website` (the explicit name is
needed while this workstream retains its legacy branch prefix). Commit taken
items promptly on the working branch, then record each decision and delete its
item together in one commit. Inter-workstream mail does not travel the outbox.
Resolved items are recorded in [the disposition log](../intake-dispositions.md).
