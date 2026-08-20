from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from devcapsule import __version__
from devcapsule.host_open import HOST_OPEN_SOCKET_ENV, HostOpenBroker


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
def test_built_pex_exposes_recursive_preflight_help(built_pex: Path) -> None:
    completed = subprocess.run(
        [str(built_pex), "project", "recursive-e2e", "preflight", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "read-only" not in completed.stderr.lower()
    assert "--show-host-paths" in completed.stdout

    run_help = subprocess.run(
        [str(built_pex), "project", "recursive-e2e", "run", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert run_help.returncode == 0, run_help.stderr
    assert "--keep-on-failure" in run_help.stdout


@pytest.mark.integration
def test_built_pex_exposes_recursive_host_public_interface(built_pex: Path) -> None:
    completed = subprocess.run(
        [
            str(built_pex),
            "-c",
            "from devcapsule.recursive_host import HostDaemonLaunchContext; "
            "print(HostDaemonLaunchContext.__name__)",
        ],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PEX_INTERPRETER": "1"},
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "HostDaemonLaunchContext"


@pytest.mark.integration
def test_xdg_open_dispatches_through_built_pex_to_exact_host_argument(
    built_pex: Path,
    tmp_path: Path,
) -> None:
    xdg_open = shutil.which("xdg-open")
    if xdg_open is None:
        pytest.skip("xdg-open is unavailable on this packaging-test host")
    socket_path = tmp_path / "host-open.sock"
    captured = tmp_path / "captured-url"
    url = "https://example.test/path?a=one&b=%24%28touch%20nope%29#fragment"
    opener = (
        sys.executable,
        "-c",
        "from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2])",
        str(captured),
    )

    with HostOpenBroker(socket_path, opener=opener):
        completed = subprocess.run(
            [xdg_open, url],
            check=False,
            text=True,
            capture_output=True,
            env={
                **os.environ,
                "BROWSER": f"{built_pex} host-open",
                HOST_OPEN_SOCKET_ENV: str(socket_path),
                "DISPLAY": "",
                "XDG_CURRENT_DESKTOP": "",
                "DE": "",
            },
        )

    assert completed.returncode == 0, completed.stderr
    assert captured.read_text(encoding="utf-8") == url


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
    assert value["schema_version"] == 2
    assert value["version"] == __version__
    assert value["build_mnemonic"] == os.environ.get(
        "DEVCAPSULE_EXPECTED_BUILD_MNEMONIC", "local-v026"
    )
    if built_pex.name == "devcapsule-local.pex":
        assert value["source_revision"] == "unknown"
        assert value["source_url"] == "unknown"
    else:
        assert built_pex.name == "devcapsule.pex"
        assert re.fullmatch(r"[0-9a-f]{40,64}", value["source_revision"])
        assert value["source_url"].endswith(f"/commit/{value['source_revision']}")
    assert set(value) == {
        "schema_version",
        "version",
        "build_mnemonic",
        "source_repository",
        "source_revision",
        "source_url",
    }


@pytest.mark.integration
def test_clean_unpublished_revision_can_be_built_for_local_testing(tmp_path: Path) -> None:
    source_project = Path(__file__).resolve().parents[2]
    repository = tmp_path / "repository"
    project = repository / "devcapsule-src"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    shutil.copytree(
        source_project / "devcapsule",
        project / "devcapsule",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for name in ("pyproject.toml", "README.md", "requirements.txt"):
        shutil.copy2(source_project / name, project / name)
    for name in ("build-pex.sh", "bump-version.py"):
        shutil.copy2(source_project / "scripts" / name, scripts / name)

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
    build_environment = {
        name: value
        for name, value in os.environ.items()
        if name not in {"DEVCAPSULE_SOURCE_REPOSITORY", "DEVCAPSULE_SOURCE_REVISION"}
    }
    build_environment["PYTHON"] = sys.executable
    completed = subprocess.run(
        [str(scripts / "build-pex.sh"), "--allow-unpublished-revision"],
        check=False,
        text=True,
        capture_output=True,
        env=build_environment,
    )

    assert completed.returncode == 0, completed.stderr
    assert output.read_bytes().startswith(b"\x7fELF")
    assert zipfile.is_zipfile(output)

    inspected = subprocess.run(
        [str(output)],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "SCIE": "inspect"},
    )
    assert inspected.returncode == 0, inspected.stderr
    lift = json.loads(inspected.stdout)["scie"]["lift"]
    embedded = {item.get("key"): item for item in lift["files"]}
    assert embedded["python-distribution"]["name"].startswith(
        "cpython-3.12.14+20260814-"
    )
    assert embedded["python-distribution"]["name"].endswith(
        "-install_only_stripped.tar.gz"
    )
    assert embedded["pex"]["executable"] is True

    version = subprocess.run(
        [str(output), "version", "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    value = json.loads(version.stdout)
    assert value["build_mnemonic"] == "local-v026"
    assert value["source_revision"] == revision
    assert value["source_repository"] == "https://github.com/example/devcapsule-unpublished-test"
    assert value["source_url"].endswith(f"/commit/{revision}")
