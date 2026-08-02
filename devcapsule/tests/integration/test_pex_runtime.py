from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

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
    assert built_pex.name == "devcapsule-local.pex"
    assert value["schema_version"] == 1
    assert value["version"] == "0.1.0"
    assert value["source_revision"] == "unknown"
    assert value["source_url"] == "unknown"
    assert set(value) == {
        "schema_version",
        "version",
        "source_repository",
        "source_revision",
        "source_url",
    }


@pytest.mark.integration
def test_clean_unpublished_revision_can_be_built_for_local_testing(tmp_path: Path) -> None:
    source_project = Path(__file__).resolve().parents[2]
    repository = tmp_path / "repository"
    project = repository / "devcapsule"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    shutil.copytree(
        source_project / "devcapsule",
        project / "devcapsule",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for name in ("pyproject.toml", "README.md", "requirements.txt"):
        shutil.copy2(source_project / name, project / name)
    shutil.copy2(source_project / "scripts" / "build-pex.sh", scripts / "build-pex.sh")

    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "DevCapsule Tests"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.email", "tests@devcapsule.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-q", "-m", "Test unpublished build"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "remote",
            "add",
            "origin",
            "https://github.com/example/devcapsule-unpublished-test.git",
        ],
        check=True,
    )
    revision = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    output = project / "dist" / "devcapsule.pex"
    completed = subprocess.run(
        [str(scripts / "build-pex.sh"), "--allow-unpublished-revision"],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHON": sys.executable},
    )

    assert completed.returncode == 0, completed.stderr
    version = subprocess.run(
        [str(output), "version", "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    value = json.loads(version.stdout)
    assert value["source_revision"] == revision
    assert value["source_repository"] == "https://github.com/example/devcapsule-unpublished-test"
    assert value["source_url"].endswith(f"/commit/{revision}")
