---
status: confirmed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-10-25
requirements: [R-PRODUCT-001]
---

# Workstation-scoped commands live under `project config` and need a project

## Symptom

Filed at the owner's direction on 2026-10-25, reading the setup script for
the AI Learning bootstrap project on rc7. The script's first block is
titled "once per workstation" and reads:

```text
devcapsule project config trust accept devcapsule-base
devcapsule project config trust accept claude-code
devcapsule project config default memory 8GiB
devcapsule project config default cpus 4
```

Each of these is workstation-scoped by its own definition: `trust accept`
records a channel "once per workstation, for every project here" (D-0011);
`default` sets "this workstation's default for memory or cpus, used by
every project here". Yet the user types `project config`, and the command
needs a project directory: the `project` group discovers a project before
dispatching. From a directory without one, on rc7, `config trust accept`
and `config default` fail with status 2. Observed inside a capsule, where
the fallback is the runtime context and the message says the
configuration is read-only there and names a `--path` to run outside;
on a plain workstation the same discovery has no project to find. Only
the read-only `trust list` ran, because it lists the channels of the
project it found.

The owner's word: "It's a little puzzling that once per workstation we do
`project config`."

## Cause

The CLI UX redesign of rc4 made `project config` the one surface for
every choice a developer makes, and the workstation records that arrived
with it, the trust record of D-0011 and the defaults for memory and CPUs,
were placed there as subcommands for the sake of one surface. Their scope
is wider than the surface that hosts them, and the project discovery of
the `project` group applies to them although they need no project.

## Expected

A workstation-scoped command has a workstation home that needs no
project and runs from any directory, for example `devcapsule trust
accept|withdraw|list` and `devcapsule default memory|cpus`, or one
`devcapsule workstation` group holding both. `project config trust list`
may remain as the project's view, which channels this project's software
comes through and whether this workstation trusts each, since that view
does need the project. The spellings are the owner's to decide; by the
project's rule a replaced spelling is deleted outright, not kept as an
alias. The documentation's "once per workstation" blocks then read as
they are meant: no project in sight.

## Evidence

- rc7, `~/.cache/devcapsule-releases/v0.3.0-rc7/devcapsule.pex`, from an
  empty directory under a throwaway configuration home, inside the
  maintenance capsule: `project config trust accept devcapsule-base` and
  `project config default memory 8GiB` exit 2 with "This command needs
  launcher-owned configuration or state. Inside this capsule that
  configuration is read-only. Run outside the capsule: devcapsule project
  --path … config trust accept devcapsule-base"; `project config trust
  list` exits 0.
- The same four commands succeed from the root of a project checkout, as
  the setup script's dry run showed the same day.
