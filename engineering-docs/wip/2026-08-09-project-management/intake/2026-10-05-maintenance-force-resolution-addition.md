# Owner addition to the conservative-writers correction: forced resolution and forced run

Sender: maintenance. Recipient: project-management. Date: 2026-10-05.

Maintenance acknowledged component-catalog's item
`2026-10-05-component-catalog-conservative-writers-tolerant-readers.md` on
2026-10-05: the command and validation gap is a 0.3.0 requirement, folded
into the in-capsule project-command work. The principle and its
sequencing stay with you, as the item asked.

The owner added two product decisions while accepting, for the 0.3 scope
you hold:

- `project config resolve --force` shows the configuration that would be
  produced if errors were skipped: a component the local launcher does not
  know is skipped; a missing IDE surface falls back to the IDE of last
  resort, bash, since vim and the SDK are inside. It highlights what is
  skipped and shows the totality that would be in place. It writes no
  local lock.
- `project run --force-config` launches with that error-skipping
  configuration and warns the user about every skip. It is distinct from
  today's `run --force`, which only accepts a stale resolution once.

Recorded in maintenance's status file under *Requirement: configuration
validated and changed by commands only*. Schema names and command
spellings are not chosen yet; they are the design step's, with the owner.
