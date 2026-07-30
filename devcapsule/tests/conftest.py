from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def built_pex() -> Path:
    path = Path(__file__).resolve().parents[1] / "dist" / "devcapsule.pex"
    assert path.is_file(), f"Built PEX does not exist: {path}; run the corresponding Nox session"
    return path
