# User-Requested Session Records

This directory preserves consequential human/agent working sessions when the
user explicitly asks for repository persistence. Session recording is never an
automatic consequence of a long chat, a checkpoint, or session closure.

## Role

A session record preserves how important requirements, decisions, rejected
alternatives, implementation choices, validation evidence, and open questions
developed during one interaction. It supplements rather than replaces the
repository's canonical artifacts:

- decisions belong in `docs/decisions/`;
- requirements belong in requirement records;
- current state and next work belong in `CURRENT-STATUS.md`;
- bugs and completed work retain their normal implementation-note records; and
- current user behavior belongs in user documentation.

If a session record conflicts with one of those artifacts, the canonical
artifact wins.

## Trigger And Capture Modes

Create a record only after an explicit user request. The request may name one
of these modes:

- `detailed` — the default when the user requests persistence without choosing
  a mode. It is an agent-authored chronological reconstruction with important
  examples, rationale, outcomes, evidence, and unresolved questions.
- `summary` — a shorter decision/evidence/next-step account.
- `verbatim` — accepted only when the user or IDE supplies an export and asks
  that it be stored. An agent must not claim that its reconstruction is an
  exact transcript.

Detailed does not mean unfiltered raw output. Records exclude hidden model
reasoning, credentials, secret values, unrelated personal data, and bulky tool
output that does not improve project memory. Note material redactions or
omissions when they affect interpretation.

## Naming And Metadata

Use:

```text
YYYY-MM-DD-short-session-topic.md
```

Begin each record with metadata identifying at least:

```yaml
date: YYYY-MM-DD
capture-mode: detailed | summary | verbatim
requested-by: user
scope: subproject or repository scope
related:
  - relative/path.md
```

The body should normally record:

1. why the session mattered;
2. the important discussion in chronological order;
3. decisions and user confirmations;
4. implementation and documentation changes;
5. validation and external-state evidence;
6. rejected or deferred alternatives;
7. unresolved questions and the next test or task; and
8. links to every canonical artifact that carries the resulting truth.

## Safety And Maintenance

- Sanitize secrets and credential-bearing output before writing.
- Prefer stable facts and representative command examples over raw logs.
- Do not turn session records into an active backlog.
- Correct factual mistakes and redact sensitive material when discovered;
  explain material corrections in the file.
- Add every new session-record markdown file to the repository `index.md`.
