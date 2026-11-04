"""The linux-arm64 matrix pins the linux-amd64 versions with arm64 artifacts only."""

from __future__ import annotations

import json
import re
from typing import Any

from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES

AMD64 = MATRICES[Platform.LINUX_AMD64]
ARM64 = MATRICES[Platform.LINUX_ARM64]
AMD64_MARKERS = re.compile(r"x86[_-]64|[_-]x64|amd64|linux64/|cft/[^/]+/linux64|ffmpeg-linux\.zip")


def _urls(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [url for key, item in value.items() for url in ([item] if key == "url" else _urls(item))]
    if isinstance(value, (list, tuple)):
        return [url for item in value for url in _urls(item)]
    return []


def test_arm64_pins_the_same_component_versions_as_amd64() -> None:
    assert {component: [pin.version for pin in pins] for component, pins in ARM64._components.items()} == {
        component: [pin.version for pin in pins] for component, pins in AMD64._components.items()
    }


def test_no_arm64_pin_names_an_amd64_artifact() -> None:
    for component, pins in ARM64._components.items():
        for pin in pins:
            for url in _urls(pin.lock_table):
                assert not AMD64_MARKERS.search(url), (component, pin.version, url)


def test_every_arm64_artifact_is_hash_pinned_and_differs_from_amd64() -> None:
    for component, pins in ARM64._components.items():
        for arm64, amd64 in zip(pins, AMD64._components[component]):
            if arm64.lock_table.get("delivery-policy") == "base-image":
                assert arm64 is amd64
                continue
            assert re.fullmatch(r"[0-9a-f]{64}", str(arm64.lock_table.get("sha256", "0" * 64)))
            if "url" in arm64.lock_table and not str(arm64.lock_table["url"]).endswith("codex-" + arm64.version + ".tgz"):
                assert arm64.lock_table["sha256"] != amd64.lock_table["sha256"], (component, arm64.version)


def test_platform_fields_and_artifact_keys_name_arm64() -> None:
    for component, pins in ARM64._components.items():
        for pin in pins:
            table = pin.lock_table
            if "platform" in table:
                assert table["platform"] == "linux-arm64", component
            if component in {"codex", "claude-code", "antigravity-cli"}:
                assert list(table["artifacts"]) == ["linux-arm64"], component
    assert "linux-amd64" not in json.dumps([pin.lock_table for pins in ARM64._components.values() for pin in pins])


def test_eclipse_native_closure_is_arm64_or_architecture_independent() -> None:
    (eclipse,) = ARM64._components["eclipse"]
    packages = eclipse.lock_table["native-packages"]
    # The same packages, plus what arm64's own dependencies add.
    assert set(packages) - set(AMD64._components["eclipse"][0].lock_table["native-packages"]) == {"libunwind8"}
    for name, entry in packages.items():
        # Architecture-independent packages keep the amd64 closure's bytes.
        if entry["url"].endswith("_all.deb"):
            continue
        assert entry["url"].startswith("https://ports.ubuntu.com/ubuntu-ports/pool/"), name
        assert entry["url"].endswith("_arm64.deb"), name


def test_arm64_base_is_its_own_unpublished_recipe_11_pin() -> None:
    (base,) = ARM64.base_images()
    assert base.contract.recipe == 11
    assert base.reference.startswith("docker.io/mycodespaceai/devcapsule-base@sha256:")
    assert base.reference not in {image.reference for image in AMD64.base_images()}


def _personal_pins(platform: str, component: str, matrix: Any) -> dict[str, Any]:
    pin = matrix.component_pins()[component]
    return {"platform": platform, "components": {component: dict(pin), "interactive-surface": component}}


def test_personal_pins_take_the_artifacts_of_the_platform_they_run_on() -> None:
    # A checkout chose codium while the project ran as linux-amd64; the
    # project then gained an arm64 lock. Its pins must deliver arm64 bytes.
    from devcapsule.configuration.capability_selection import pins_for_platform

    amd64 = _personal_pins("linux-amd64", "codium", AMD64)
    on_arm64 = pins_for_platform(amd64, ARM64)
    assert on_arm64["platform"] == "linux-arm64"
    assert on_arm64["components"]["codium"] == dict(ARM64.component_pins()["codium"])
    assert on_arm64["components"]["interactive-surface"] == "codium"
    assert amd64["components"]["codium"] == dict(AMD64.component_pins()["codium"])  # input unchanged
    # Pins already written wrongly, arm64 platform with amd64 bytes, are healed too.
    mislabelled = dict(amd64, platform="linux-arm64")
    assert pins_for_platform(mislabelled, ARM64)["components"]["codium"] == dict(ARM64.component_pins()["codium"])
    assert pins_for_platform(on_arm64, AMD64)["components"]["codium"] == dict(AMD64.component_pins()["codium"])


def test_a_personal_version_the_other_platform_lacks_asks_for_a_new_choice() -> None:
    import pytest

    from devcapsule.configuration.capability_selection import pins_for_platform
    from devcapsule.configuration.storage import ProjectConfigurationError

    channel = {"platform": "linux-amd64", "components": {"codex": {"version": "9.9.9", "url": "https://example.test/x64.tgz"}}}
    with pytest.raises(ProjectConfigurationError, match="codex 9.9.9 is pinned for linux-amd64.*linux-arm64 has no pin"):
        pins_for_platform(channel, ARM64)
    assert pins_for_platform(channel, AMD64)["components"]["codex"]["version"] == "9.9.9"
