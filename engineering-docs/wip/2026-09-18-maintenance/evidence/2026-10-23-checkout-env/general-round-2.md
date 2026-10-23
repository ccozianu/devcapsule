# Round 2 of review #255 — overlapping ambiguous split tokens

The session-log fix, attached-short refusal and general conservative approach
are accepted. One related counterexample remains:

    args = ["--label", "--env", "--env", "TOKEN=before"]

Docker's first --env token is the label operand; the next --env is a real
option. In the current helper, the ambiguous split candidate consumes the
following real --env token as its own value. Two observable failures result:

1. redact_environment(args) leaves TOKEN=before unmasked, and
   inline_environment_names(args) misses TOKEN. Narration, preview and the
   session log can therefore disclose it.
2. update_environment(..., 'TOKEN', 'after') succeeds and prepends TOKEN=after,
   but leaves the real TOKEN=before later in the list, so Docker still sees
   the old value. unset-env similarly returns success without removing it.
   The name-filtered ambiguity refusal is not sufficient: an ambiguous span
   can hide the identity of a following real option.

Please make the bounded scanner conservative for overlapping ambiguous split
candidates: do not skip a possible next option merely because the preceding
ambiguous candidate might consume it. For diagnostics, include every possible
inline env value in masking. For convenience mutation, refuse ANY unresolved
ambiguity before writing, as list-env already does; remove the apparent-name
filter and adjust the previous test allowing OTHER edits in an ambiguous list.
This simplification needs no Docker schema and stays within round 1's contract.

Add regressions for the exact list above and a split short -e variant: no
sentinel in diagnostics, TOKEN identified for masking, set/unset/list refused
without changing file bytes, and ordinary adjacent environment options still
working. Keep actual saved/launch tokens unchanged. Update docs to say any
ambiguity prevents convenience edits. No other feature work is requested.

Use the same branch, checkout, author trailer, focused tests and full gate as
before. No status/evidence/work-order edits, merges, rebases, containers or real
credentials. Commit, push, update #255 and reply with the validation. Print the
comment URL last. This is the second round; the three-round limit still applies.
