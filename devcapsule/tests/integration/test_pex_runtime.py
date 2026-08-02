from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest


@pytest.mark.integration
def test_built_pex_dispatches_runtime_help(built_pex: Path) -> None:
    completed = subprocess.run(
        [str(built_pex), "runtime", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "usage: devcapsule runtime RUNTIME_PLAN.json" in completed.stdout


@pytest.mark.integration
def test_built_pex_exposes_self_contained_source_identity(built_pex: Path) -> None:
    completed = subprocess.run(
        [str(built_pex), "version", "--json"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    value = json.loads(completed.stdout)
    assert value["schema_version"] == 1
    assert value["version"] == "0.1.0"
    assert set(value) == {
        "schema_version",
        "version",
        "source_repository",
        "source_revision",
        "source_url",
    }
