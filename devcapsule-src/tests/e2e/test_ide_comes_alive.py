"""Smoke: each IDE surface the product offers comes alive in a fresh project.

Opt-in (``nox -s ide-smoke``): a run initializes a project per surface with
the executable under test, launches it, and proves the IDE is up from the
outside. A first run on a machine acquires the IDE and builds its environment,
which takes minutes; later runs reuse both. Needs Docker and the base image
the executable recommends; runs inside a capsule as well as on a host.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.e2e.ide_session import SURFACES, IdeSurface, capture_desktop, desktop_page_answers, ide_session, wait_for_ide_window

EVIDENCE_ROOT = Path(__file__).resolve().parents[2] / "dist" / "e2e-evidence" / "ide-smoke"


@pytest.mark.e2e
@pytest.mark.ide_smoke
@pytest.mark.parametrize("surface", SURFACES, ids=[surface.name for surface in SURFACES])
def test_ide_comes_alive(surface: IdeSurface, built_pex: Path, tmp_path: Path) -> None:
    evidence = EVIDENCE_ROOT / surface.name
    with ide_session(built_pex, surface, tmp_path, evidence) as session:
        # 1. The launcher published a desktop and the page behind it answers.
        assert desktop_page_answers(session.desktop_url) == 200, session.desktop_url
        # 2. The IDE owns a top-level window on the capsule's own display.
        window = wait_for_ide_window(session)
        # 3. Optional pixel evidence: the desktop renders more than a bare desktop.
        pixels = capture_desktop(session.desktop_url, evidence / "desktop.png")
        if pixels is not None:
            distinct = pixels["distinctColours"]
            assert isinstance(distinct, int) and distinct >= 64, pixels
        facts = {
            "surface": surface.name,
            "needs": list(surface.needs),
            "container": session.container,
            "desktop_url_port": session.desktop_url.split(":")[2].split("/")[0],
            "ide_window": window,
            "pixels": pixels if pixels is not None else "not captured: Playwright and its browser are optional",
        }
        (evidence / "facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
