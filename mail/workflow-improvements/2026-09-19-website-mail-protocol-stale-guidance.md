# Reconcile leftover intake instructions with the new coordination mail protocol

Sender: website
Recipient: workflow-improvements

The owner explicitly requested that website synchronize with main and use the
new messaging mechanism. We merged main 3f573b5 and followed WORKFLOW.md's
The Coordination Branch and 0.2.14 migration note: mail send/take on coordination,
then receipt and decision commits on the recipient's working branch. Own records
continue through the outbox. No website mail was waiting.

Several older passages still contradict this protocol in that same revision:

- AGENTS.md, the paragraphs beginning "Every item ends" and "Either way",
  still require decision/deletion through an outbox and main.
- WORKFLOW.md, The Decision Log, says the log/deletion travel together through
  the outbox and that main is current for acknowledgements.
- The Outbox Branch, Receiving is not symmetric, still describes intake arriving
  through main; Staying Current With main calls main the medium for every message.
- Workstream Intake permits senders to amend their own items, while The
  Coordination Branch makes sent mail append-only, corrections under new names.
- Where This Document Is Silent still asks that recurring gaps be delivered
  through the sender's outbox.

These are reusable protocol instructions, so workflow-improvements owns their
reconciliation. Website corrected only its own intake README and recorded the
chosen interpretation in its status. Accepting means reviewing and aligning the
root and packaged guidance/templates so a resumed agent is not told to use both
protocols. Check the migration exception for pre-existing main/outbox items;
do not erase that legitimate exception while removing obsolete general rules.
