"""Generic PID 1 entrypoint for a materialized DevCapsule image.

The entrypoint prepares the capsule from the runtime plan and then stays: it
spawns the one distinguished foreground child — the interactive surface from
the plan, or the headless job given after ``--`` — and supervises it as PID 1
until the session ends. The session's exit code is the child's, honestly.
"""

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
from .supervisor import SupervisedChild, Supervisor, SupervisorError

USAGE = "usage: devcapsule runtime RUNTIME_PLAN.json [-- COMMAND [ARGUMENT...]]"


def run(plan: rtcontract.RuntimePlan, job: tuple[str, ...] | None = None) -> int:
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
    if job is None:
        child = SupervisedChild(
            name=plan.component.id,
            command=foreground_command(launch.command, plan.identity),
            foreground=True,
        )
    else:
        # Headless mode: the same distinguished slot with no GUI. The job runs
        # in the project it was launched against, not the image's workdir.
        child = SupervisedChild(
            name="job",
            command=foreground_command(job, plan.identity),
            foreground=True,
            working_directory=plan.project_path,
        )
    return Supervisor((child,)).run()


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--help"]:
        print(USAGE)
        return 0
    job: tuple[str, ...] | None = None
    if len(arguments) >= 2 and arguments[1] == "--":
        job = tuple(arguments[2:])
        arguments = arguments[:1]
    if len(arguments) != 1 or job == ():
        print(USAGE, file=sys.stderr)
        return 2
    try:
        return run(RuntimePlan.from_file(arguments[0]), job)
    except RuntimePlanError as error:
        print(f"devcapsule runtime plan error: {error}", file=sys.stderr)
        return 2
    except SupervisorError as error:
        print(f"devcapsule supervisor error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
