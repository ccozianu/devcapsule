"""Test driver: run a Supervisor over a JSON child-set spec.

The supervisor blocks signals on the thread that runs it, so tests exercise
it in a dedicated process rather than inside pytest. The driver's exit code
is the session's; that is the observable under test.
"""

from __future__ import annotations

import json
import sys

from devcapsule.container_runtime.supervisor import SupervisedChild, Supervisor


def main() -> int:
    spec = json.loads(sys.argv[1])
    children = tuple(
        SupervisedChild(
            name=child["name"],
            command=tuple(child["command"]),
            foreground=child.get("foreground", False),
        )
        for child in spec["children"]
    )
    return Supervisor(children, grace_seconds=spec.get("grace_seconds", 5.0)).run()


if __name__ == "__main__":
    sys.exit(main())
