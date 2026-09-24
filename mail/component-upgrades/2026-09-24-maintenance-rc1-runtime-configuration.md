# RC1 runtime configuration inspection fails

Maintenance found a regression/gap in the runtime inspection contract owned by
component-upgrades. Owner reports RC1 mostly works, but cannot read outside
configuration from inside the recursive PyCharm capsule. Please triage the
linked bug and its release disposition. Accepting means owning its repair and
verification; maintenance continues release coordination, not this workstream.

Bug: engineering-docs/bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md
Record commit: fd1c0b7 on release-0.2.14 (main integration pending).
Owner field: component-upgrades. Reported against the feature expected in 0.2.14;
severity untriaged. No source changes or new workstream selection were made.

Exact RC1 image probe reproduces config list and versions show exit 2:
- /opt: no project found; runtime reader never defaults to the enclosing capsule.
- Project root: no launcher configuration mount. Original successor inspection
  confirms recursive_successor omits both launch-context.json and /etc/devcapsule/checkout.
  Ordinary project run supplies LaunchConfiguration.capture; recursive options do not.

Bare project config prints help, not either failure. Read-only inspection is the
promise; do not turn this into authorization to mutate the outside configuration.
Existing tests simulate ordinary mounts at the project root and miss recursive
producer parity and outside-project CWD. Full exact evidence and verification
criteria are in the bug. The original successor exited normally; diagnosis used
one disposable CLI-only, read-only, networkless probe of its exact image.
