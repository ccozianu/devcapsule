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


@pytest.fixture(autouse=True)
def private_artifact_cache(request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give every test an empty artifact cache of its own.

    ``cache_root`` follows ``XDG_CACHE_HOME``, which a capsule exports as the
    developer's real cache. A test that resolves or runs a checkout retains
    that cache's artifacts into its own state, gigabytes per test where the
    cache holds an IDE, and nothing on a laptop without the cache: the same
    test wrote 2.4 GB here and 68 KB with an empty cache (2026-10-10). The
    Docker-backed suites keep the real cache, because their base builds
    would otherwise download every artifact again; a test that wants a
    particular cache sets ``XDG_CACHE_HOME`` itself, after this fixture.
    """

    if any(request.node.get_closest_marker(marker) for marker in DOCKER_MARKERS):
        return
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "private-cache"))


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
