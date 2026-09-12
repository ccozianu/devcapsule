"""Test driver: run a Supervisor over a JSON child-set spec.

The supervisor blocks signals on the thread that runs it, so tests exercise
it in a dedicated process rather than inside pytest. The driver's exit code
is the session's; that is the observable under test.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Callable

from devcapsule.container_runtime.supervisor import SupervisedChild, Supervisor, SupervisorError


def path_exists_probe(path: str) -> Callable[[], bool]:
    # A readiness probe in the spec is "this path exists", which is exactly
    # the shape the display children use (sockets, files).
    return lambda: Path(path).exists()


def main() -> int:
    spec = json.loads(sys.argv[1])
    children = tuple(
        SupervisedChild(
            name=child["name"],
            command=tuple(child["command"]),
            foreground=child.get("foreground", False),
            ready=path_exists_probe(child["ready_path"]) if "ready_path" in child else None,
            ready_timeout_seconds=child.get("ready_timeout_seconds", 20.0),
        )
        for child in spec["children"]
    )
    try:
        return Supervisor(children, grace_seconds=spec.get("grace_seconds", 5.0)).run()
    except SupervisorError as error:
        # The entrypoint reports a start failure the same way: message, exit 2.
        print(f"devcapsule supervisor error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
