"""The repository's own manifest must stay readable by the latest released client.

Released clients validate ``runtime-effect`` by exact membership in the
vocabulary they shipped with, and refuse the whole manifest otherwise. A
declaration added here therefore strands every contributor who installed the
release the guides point at, and the refusal cannot explain itself (bug
2026-09-24, released launchers reject the repository manifest). Move the
pinned vocabulary only when a final release ships with the new entry.
"""

from pathlib import Path
import tomllib

import pytest


LATEST_RELEASED_CLIENT = "v0.2.12"
RELEASED_RUNTIME_EFFECTS = {"docker.memory-limit"}

REPOSITORY_MANIFEST = Path(__file__).resolve().parents[2] / ".devcapsule" / "devcapsule.toml"


@pytest.mark.skipif(not REPOSITORY_MANIFEST.is_file(), reason="not a repository checkout")
def test_repository_manifest_declares_only_released_runtime_effects():
    manifest = tomllib.loads(REPOSITORY_MANIFEST.read_text(encoding="utf-8"))
    values = manifest.get("configuration", {}).get("values", {})
    assert values, "the repository manifest declares configuration values"
    for name, declaration in values.items():
        effect = declaration.get("runtime-effect")
        assert effect is None or effect in RELEASED_RUNTIME_EFFECTS, (
            f"{name} declares runtime-effect {effect!r}, which {LATEST_RELEASED_CLIENT} "
            "rejects; rely on a reserved name or wait for the release that knows it"
        )
