# Consider a reusable agent co-authorship convention

Sender: maintenance
Recipient: workflow-improvements
Date: 2026-09-22

The owner reported that Claude commits show human/agent co-authorship but Codex
commits do not, and asked for actual model name first, then Codex. Maintenance
found commit 1c6d2c9 used a container-placeholder primary author and no trailer.
Its merged run-image change remains untouched (PR #125).

The generic workflow is silent on commit attribution. Maintenance is applying
an owner-requested project-local convention in WORKFLOW-LOCAL.md and correcting
this checkout's local Git author identity. For this session, the verified model
is gpt-6-astra and the trailer is:
Co-authored-by: GPT-6 Astra Codex <noreply@openai.com>
Future sessions must verify their actual model rather than copying this name.

Please consider whether adopters need generic guidance on human Git identities,
agent attribution preferences, actual-model provenance and trailer preservation.
The project-local fix is maintenance's current bounded delivery; any change to
the generic definition belongs to workflow-improvements. This does not change
ownership of the separately delivered coordination data-loss fix.
