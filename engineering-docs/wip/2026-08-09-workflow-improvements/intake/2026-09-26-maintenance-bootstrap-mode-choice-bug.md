# Bug filed to you: bootstrap cannot choose the workflow mode

Sent: 2026-09-26
From: `maintenance`, from the owner's first-session dogfood of 0.2.14.

Record: `engineering-docs/bugs/devcapsule/2026-09-26-bootstrap-cannot-choose-the-workflow-mode.md`
on `ws-maintenance/post-0.2.14` at `5c10f0d`, owner `workflow-improvements`,
because your 2026-09-24 onboarding work order already owns how the mode and
definition choices are expressed. Plain `devcapsule bootstrap` declares
single-stream without asking, reports it as chosen, and on a directory with no
`.devcapsule/devcapsule.toml` writes no declaration at all. The specification's
installation contract says exactly this, so the fix is a product-contract
change for the owner to shape, then code and spec together. Evidence and the
verification target are in the record. It reaches `main` with maintenance's
next integration; the bug is routed by its owner field, not by this mail.
