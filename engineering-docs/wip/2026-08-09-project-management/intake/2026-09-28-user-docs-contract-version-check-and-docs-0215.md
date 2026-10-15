# Two small facts for the content–website contract, from writing the 0.2.15 docs

From: user-docs. To: project-management. Date: 2026-09-28.

1. The contract's typed-version check, section 4.4, pattern
   `v?0\.\d+\.\d+(\.dev\d+)?`, matches the loopback address `127.0.0.1`,
   which the first-session guide must print. Amend it to require that the
   match is not preceded by a digit or a dot, `(?<![\d.])`, and skip link
   targets that are tokens. The producer's own check in this delivery does
   both and passes on all 43 pages.
2. UD-006 items 1 to 7 are on `ws-user-docs/first-session` at `41f4319`,
   awaiting the owner's pull request to `main`. The tree describes 0.2.15
   exactly, so carrying `docs/` onto `docs-0.2.15` is a copy of that
   directory at that commit, your section-4 step 1. Release notes for both
   versions are under `engineering-docs/releases/<tag>/notes.md`.

Accepting means amending the contract document's section 4.4 and scheduling
the `docs-0.2.15` copy after the merge.
