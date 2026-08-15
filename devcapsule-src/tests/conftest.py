from __future__ import annotations

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
        "devcapsule.configurations.pycharm._launcher.requires_translation",
        lambda _env: False,
    )


@pytest.fixture
def built_pex() -> Path:
    path = Path(__file__).resolve().parents[1] / "dist" / "devcapsule-local.pex"
    assert path.is_file(), f"Built PEX does not exist: {path}; run the corresponding Nox session"
    return path
