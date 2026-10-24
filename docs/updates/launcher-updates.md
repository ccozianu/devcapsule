---
description: How the launcher tells you a newer DevCapsule exists, how to install it, and what does not change when you do.
weight: 2
updated: 2026-10-24
---
# Launcher updates

Once a day, `project run` checks whether a newer DevCapsule release exists
and tells you interactively; `--no-update-check` skips the check for one
launch, and a cached critical notice still lets you decide. Installing the
newer release is the [install block](../getting-started/install.md) again,
with the new version's download address; it replaces the executable and
nothing else.

An upgraded launcher keeps every project's lock and every checkout's
recorded choices. It grants no new host access. If a project changed its own
configuration in the meantime, the next launch asks what is pending, as
[Project versus personal](../configuration/project-versus-personal.md#when-the-project-changes)
describes. Existing per-checkout consents remain valid when they still match
the selected software. A missing consent or channel acceptance can require
an answer. An upgrade alone does not invalidate a matching consent.
