"""Run the current CLI through preparation, stopping before acquisition or Docker.

Configuration tests need a generated launch record. The retired explicit
resolution command used to provide it. Keep these tests offline by ending
run at the update-review boundary, after real launch preparation.
"""
from pathlib import Path
from unittest.mock import patch

from devcapsule import cli
from devcapsule.commands._run_flow import prepare_launch


class _Prepared(Exception):
    pass


def run_until_prepared(project: Path | None = None) -> int:
    def prepare(*args, **kwargs):
        return prepare_launch(*args, **kwargs, interactive=False, check_display=False)

    prefix = ["project"] if project is None else ["project", "--path", str(project)]
    with patch("devcapsule.commands.project.offer_software_approvals", return_value=True), \
         patch("devcapsule.commands.project.prepare_launch", side_effect=prepare), \
         patch("devcapsule.commands.project.offer_upgrades", side_effect=_Prepared):
        try:
            return cli.main([*prefix, "run", "--no-update-check"])
        except _Prepared:
            return 0
