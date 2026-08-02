---
id: D-0005
title: Agent-Neutral Base And Optional Agent Components
status: accepted
date-proposed: 2026-08-02
date-decided: 2026-08-02
decided-by: Costin Cozianu
requirements:
  - R-PRODUCT-001
  - R-PRODUCT-002
  - R-PYTHON-MVP-003
  - R-IMAGE-BUILD-001
supersedes:
superseded-by:
---

# D-0005: Agent-Neutral Base And Optional Agent Components

## Context

D-0001 assumed that Gemini CLI would be the default agent capability because
it could be redistributed in DevCapsule images. The first Python-owned base
therefore installed Gemini CLI alongside Node.js/npm, and the Codium launcher
mounted host Gemini state even though agent tooling has a separate release,
authentication, state, licensing, and trust lifecycle from the development
runtime.

The product owner directed that V1 bases stop carrying an ambient agent CLI.
Google now offers Antigravity CLI as a separate terminal surface, but its
optional DevCapsule component will be designed and validated in a later V1
task rather than downloaded or installed as part of this decision.

Public verification on 2026-08-02 did not substantiate the separate claim that
Gemini CLI itself is deprecated. Google's
[`@google/gemini-cli` package](https://www.npmjs.com/package/@google/gemini-cli)
reported stable version `0.53.1` without a deprecation marker, the
[official repository](https://github.com/google-gemini/gemini-cli) was active
and unarchived, and Google published
[release `v0.53.1`](https://github.com/google-gemini/gemini-cli/releases/tag/v0.53.1)
on 2026-07-31. Google's
[Antigravity download page](https://antigravity.google/download) separately
advertised Antigravity CLI `v1.1.9`. DevCapsule's change is therefore a
product-boundary decision, not a claim about Google's official Gemini CLI
support status.

## Options Considered

### Option A: Keep Gemini CLI in every base

This preserves the current dogfood behavior and makes one agent immediately
available.

Cost: every user receives a fast-changing agent they may not want, base rebuilds
become coupled to its cadence, and agent-specific credentials and state appear
ambient rather than explicitly selected.

### Option B: Replace ambient Gemini CLI immediately with ambient Antigravity CLI

This follows the preferred future Google agent surface without waiting for a
component contract.

Cost: it repeats the same coupling under a new name, downloads a new executable
before its acquisition, licensing, persistence, and validation contracts are
settled, and exceeds the authorized scope of the current task.

### Option C: Keep the base agent-neutral and materialize agents explicitly

The base retains general language/runtime prerequisites such as pinned
Node.js/npm, while agent CLIs become separately selected, pinned, inspectable
components with their own state and trust behavior.

Cost: an agent is not immediately present in a fresh base, and V1 needs a
follow-up component implementation before offering Antigravity as a curated
choice.

## Decision

Adopt Option C.

V1 default bases and transitional Python-owned IDE builds contain no ambient
AI-agent CLI and mount no agent-specific host credential/state directory by
default. General prerequisites such as Node.js/npm may remain when justified
as language tooling.

Agent CLIs are optional components. Each component must declare its exact
identity and acquisition/install behavior, explain its license and trust
effects, use persistent home or explicit namespaced state, and avoid granting
host access merely by being installed. Antigravity CLI is the first planned
V1 agent component, but its implementation and any acquisition are a later
task. Gemini CLI may be considered separately as an optional component; this
decision does not assert that Google deprecated it.

This decision replaces only D-0001's assumption that Gemini CLI is the default
ambient agent capability. D-0001's capability-first model remains adopted.
The reserved D-0003 Gemini-default decision is no longer needed in that form.

## Rationale

The base should contain stable, broadly useful development infrastructure.
Agent choice is personal and security-relevant: agents authenticate to external
services, preserve conversations and trust decisions, execute tools, and
change faster than Python/compiler/debugging prerequisites. Making them
explicit components keeps the default understandable and lets projects express
a capability without forcing every developer to execute one publisher's CLI.

Deferring Antigravity acquisition also preserves the project's checksum,
materialization, authorization, and user-disclosure standards instead of
introducing an unreviewed installer into the base.

## Consequences

- Rebuild and republish the V1 base before changing the committed lock; the
  immutable v019 digest still contains Gemini CLI.
- Remove ambient Gemini installation and direct host `~/.gemini` mounts from
  active Python-owned paths.
- The user inventory must say that no agent CLI is present by default and
  explain why agents are optional components.
- Add a later V1 task for a pinned, validated Antigravity CLI component without
  downloading or installing it during this slice.
- Existing historical images and records may continue to describe their actual
  Gemini-inclusive contents.

## Reopen If

- user research shows that an agent-neutral default prevents adoption more
  than explicit choice improves trust;
- one agent runtime becomes a stable, open, universally expected platform
  prerequisite rather than a product choice; or
- component materialization cannot provide acceptable startup time or state
  continuity.
