"""Generic PID 1 entrypoint for a materialized DevCapsule image."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Sequence

from . import contract as rtcontract

from .components import jetbrains
from .contract import RuntimePlan, RuntimePlanError
from .filesystem import plan_filesystem, prepare_filesystem
from .graphics import environment as graphics_environment
from .identity import foreground_command


def run(plan: rtcontract.RuntimePlan) -> None:
    filesystem = plan_filesystem(plan)
    prepare_filesystem(filesystem, plan.identity)
    os.environ.update(filesystem.environment)
    os.environ.update(plan.component_environment())
    os.environ.update(graphics_environment(os.environ))
    if plan.component.adapter != "jetbrains":
        raise RuntimePlanError(f"unsupported component adapter: {plan.component.adapter}")
    launch = jetbrains.plan(plan)
    Path(launch.properties_path).write_text(launch.properties, encoding="utf-8")
    os.environ[launch.properties_environment_variable] = launch.properties_path
    command = foreground_command(launch.command, plan.identity)
    os.execvpe(command[0], command, os.environ)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--help"]:
        print("usage: devcapsule runtime RUNTIME_PLAN.json")
        return 0
    if len(arguments) != 1:
        print("usage: devcapsule runtime RUNTIME_PLAN.json", file=sys.stderr)
        return 2
    try:
        run(RuntimePlan.from_file(arguments[0]))
    except RuntimePlanError as error:
        print(f"devcapsule runtime plan error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
