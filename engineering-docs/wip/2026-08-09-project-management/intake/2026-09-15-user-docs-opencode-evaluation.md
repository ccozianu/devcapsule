# Intake: Evaluate OpenCode For The Adopter Journey

Sender: `user-docs`, 2026-09-15. Recipient: `project-management`.

The owner explicitly requested that project-management take responsibility for
OpenCode testing. User-docs separately accepts testing and documenting an
OpenCode setup as later work in its handoff.

The intended v1 first sessions involve starting a small project with at least
one AI. A locally run open model should be a possible route, alongside hosted
models. OpenCode appears suitable because it supports local model endpoints
and reads `AGENTS.md`; neither fact establishes that a particular pairing is
effective in DevCapsule.

Please arrange a bounded evaluation of an OpenCode/model setup for this journey,
and assign any resulting component integration work and its sequence. Identify
the model, runtime, hardware and context requirements, whether it can perform a
small useful coding task and resume work, and any gaps in project-instruction
handling, persistence or explicit host boundaries. Gemma is a candidate for the
local path; the pairing has not been selected or tested here.

Accepting means owning the evaluation's scheduling and assignment, and recording
its outcome and implementation gaps where user-docs can use that evidence.
The existing component-catalog workstream has a frozen delivery scope; this
request does not reopen it or authorize an immediate installation here.

Sources:

- [User-docs direction and later requirement](../../2026-09-12-user-docs/CURRENT-STATUS.md)
- [Agent-neutral base and optional components](../../../decisions/product/d-0005-agent-neutral-base-and-optional-agent-components.md)
- [OpenCode provider support](https://opencode.ai/docs/providers/)
- [OpenCode project instructions](https://opencode.ai/docs/rules/)
