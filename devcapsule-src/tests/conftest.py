from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def host_launch_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make launcher tests behave as if they run on the host.

    The launcher translates bind sources when it detects that it is running
    inside a container against an external Docker daemon. That is correct in
    production but would otherwise make the suite depend on where it runs:
    identical tests would take different paths on a laptop and inside a
    DevCapsule dogfood container. Tests that exercise translation opt in by
    overriding this in the test body.
    """

    monkeypatch.setattr(
        "devcapsule.launch.pycharm._launcher.requires_translation",
        lambda _env: False,
    )


DOCKER_MARKERS = ("e2e", "base_build_e2e", "recursive_e2e", "contributor_e2e", "ide_smoke")


def inherited_cache_home() -> Path:
    """The cache home the process was started with: ``XDG_CACHE_HOME``, else ``~/.cache``."""
    return Path(os.environ.get("XDG_CACHE_HOME") or Path(os.environ.get("HOME", "~")).expanduser() / ".cache")


@pytest.fixture(autouse=True)
def private_user_directories(request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give non-Docker tests private user-directory paths under their tmp_path.

    Override HOME and each XDG directory: changing HOME alone leaves exported
    XDG paths active. This keeps artifact retention and restoration, config,
    state, and launcher runtime files away from the developer's directories.
    Docker-marked tests keep their inherited directories so builds reuse the
    real artifact cache. A test or function-scoped fixture can set its own
    paths after this autouse fixture runs. Leave directory creation to the
    tested code so refusal tests can still assert that nothing was written.
    """

    if any(request.node.get_closest_marker(marker) for marker in DOCKER_MARKERS):
        return
    # The build tools' caches are content-addressed and shared by the
    # developer's own builds: pex's under PEX_ROOT, and the scie launcher's
    # unpacked Python under SCIE_BASE. Moving them under the scratch made every
    # clean revision build download the launcher and its Python again and
    # unpack it per case, 250 MB a time. Pin both before the homes move.
    cache = inherited_cache_home()
    monkeypatch.setenv("PEX_ROOT", os.environ.get("PEX_ROOT") or str(cache / "pex"))
    monkeypatch.setenv("SCIE_BASE", os.environ.get("SCIE_BASE") or str(cache / "nce"))
    for variable, leaf in (
        ("HOME", "home"),
        ("XDG_CACHE_HOME", "cache"),
        ("XDG_CONFIG_HOME", "config"),
        ("XDG_DATA_HOME", "data"),
        ("XDG_STATE_HOME", "state"),
        ("XDG_RUNTIME_DIR", "runtime"),
    ):
        monkeypatch.setenv(variable, str(tmp_path / "user" / leaf))


@pytest.fixture
def built_pex() -> Path:
    selected = os.environ.get("DEVCAPSULE_PEX_UNDER_TEST")
    path = (
        Path(selected).expanduser().resolve()
        if selected
        else Path(__file__).resolve().parents[1] / "dist" / "devcapsule-local.pex"
    )
    assert path.is_file(), (
        f"Built PEX does not exist: {path}; run the corresponding Nox session"
    )
    return path
