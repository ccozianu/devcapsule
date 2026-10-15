"""The base contract: identity by promises, compatibility by the API rule,
provenance kept apart, and the matrix pins obeying the additive rule."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from devcapsule.images.contract import (
    BaseContract,
    BaseImage,
    CONTAINED_DISPLAY,
    HOST_X11_ONLY_DISPLAY,
    LAUNCHER_SUPPLIED_RUNTIME,
    LEGACY_RECIPE_SOURCE_PATH,
    RECIPE_SOURCE_LABEL,
    RECIPE_SOURCE_PATH,
    REPOSITORY,
    SERVICES_LABEL,
)
from devcapsule.images.base import BASE_RECIPE_VERSION, BASE_SERVICES, current_contract
from devcapsule.configuration.authorization import authorization_declarations
from devcapsule.resolution_matrix import MATRICES, compatibility_report, known_base_image

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_LOCK = REPO_ROOT / ".devcapsule" / "devcapsule.linux-amd64.lock"
REPO_MANIFEST = REPO_ROOT / ".devcapsule" / "devcapsule.toml"

OLD = BaseContract("ubuntu-24.04", 6, frozenset({"python", "node"}), HOST_X11_ONLY_DISPLAY, LAUNCHER_SUPPLIED_RUNTIME)
NEW = BaseContract("ubuntu-24.04", 9, frozenset({"python", "node", "java"}), CONTAINED_DISPLAY, LAUNCHER_SUPPLIED_RUNTIME)
OTHER = BaseContract("ubuntu-26.04", 1, frozenset({"python", "node", "java"}), CONTAINED_DISPLAY, LAUNCHER_SUPPLIED_RUNTIME)


def test_identity_is_family_at_recipe_and_never_a_release() -> None:
    assert NEW.identity == "ubuntu-24.04@9"
    assert "v0.2" not in NEW.describe()


def test_compatibility_is_the_api_rule() -> None:
    assert NEW.accepts(OLD), "a newer recipe of the family runs what the older one validated"
    assert NEW.accepts(NEW)
    assert not OLD.accepts(NEW), "an older recipe cannot promise what a newer one added"
    assert not OTHER.accepts(NEW), "a new family inherits nothing"


def test_additive_rule_within_a_family() -> None:
    assert NEW.extends(OLD)
    shrunk = BaseContract("ubuntu-24.04", 10, frozenset({"python"}), CONTAINED_DISPLAY, LAUNCHER_SUPPLIED_RUNTIME)
    assert not shrunk.extends(NEW), "removing a service is not a recipe bump; it is a new family"


def test_matrix_pins_obey_the_additive_rule() -> None:
    for matrix in MATRICES.values():
        by_family: dict[str, list[BaseContract]] = {}
        for image in matrix.base_images():
            by_family.setdefault(image.contract.family, []).append(image.contract)
        for family, contracts in by_family.items():
            ordered = sorted(contracts, key=lambda contract: contract.recipe)
            for older, newer in zip(ordered, ordered[1:]):
                assert newer.extends(older), f"{family}: recipe {newer.recipe} drops services of recipe {older.recipe}"


def test_recipe_declares_the_current_contract() -> None:
    contract = current_contract()
    assert contract.identity == f"ubuntu-24.04@{BASE_RECIPE_VERSION}"
    assert contract.services == BASE_SERVICES
    pinned = known_base_image("docker.io/mycodespaceai/devcapsule-base@sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c")
    assert pinned is not None and pinned.contract.identity == "ubuntu-24.04@9"
    assert contract.accepts(pinned.contract), "today's recipe still honours what the pinned base promised"


def test_image_is_reconstructed_from_its_labels() -> None:
    labels = {
        "devcapsule.base.recipe": "ubuntu-24.04",
        "devcapsule.base.recipe-version": "9",
        "devcapsule.base.display": "contained",
        "devcapsule.base.runtime": "launcher-supplied",
        SERVICES_LABEL: "docker-cli,java,maven,node,postgresql-client,python",
        "org.opencontainers.image.version": "v0.2.14-rc2",
        "devcapsule.source.revision": "8d005b38af9777b7e3314bf3e2910314effef4d2",
        RECIPE_SOURCE_LABEL: RECIPE_SOURCE_PATH,
    }
    image = BaseImage.from_labels("sha256:64c8db54", labels)
    assert image.contract.identity == "ubuntu-24.04@9"
    assert "postgresql-client" in image.contract.services
    assert image.built.builder == "v0.2.14-rc2"
    assert image.built.recipe_url == f"{REPOSITORY}/blob/8d005b38af9777b7e3314bf3e2910314effef4d2/{RECIPE_SOURCE_PATH}"
    older = BaseImage.from_labels("sha256:old", {k: v for k, v in labels.items() if k not in (SERVICES_LABEL, RECIPE_SOURCE_LABEL)}, services=frozenset({"python"}))
    assert older.contract.services == frozenset({"python"}), "pre-services images take the caller's knowledge"
    assert older.built.recipe_path == LEGACY_RECIPE_SOURCE_PATH, "an image built before the move points at the old recipe file"
    with pytest.raises(ValueError):
        BaseImage.from_labels("sha256:none", {})


def test_consent_names_the_contract_and_the_recipe_source() -> None:
    manifest = tomllib.loads(REPO_MANIFEST.read_text(encoding="utf-8"))
    lock = tomllib.loads(REPO_LOCK.read_text(encoding="utf-8"))
    declaration = authorization_declarations(manifest, lock)["base-image"]
    assert declaration.description.startswith("Execute base ubuntu-24.04@9 at docker.io/")
    assert "built by v0.2.12-rc5" in declaration.description
    assert f"{REPOSITORY}/blob/v0.2.12-rc5/{LEGACY_RECIPE_SOURCE_PATH}" in declaration.description
    assert declaration.display_value is not None and declaration.display_value.startswith("ubuntu-24.04@9 — ")


def test_compatibility_report_names_the_rule_and_the_evidence() -> None:
    lock = tomllib.loads(REPO_LOCK.read_text(encoding="utf-8"))
    report = compatibility_report(lock)
    assert report[0].startswith("Compatibility: components validated on family ubuntu-24.04 run on ubuntu-24.04@9")
    assert any(line.startswith("  validated:") or line.startswith("  not validated:") for line in report[1:])
