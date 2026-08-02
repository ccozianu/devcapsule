from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile

import pytest

from devcapsule.compat import CliError
from devcapsule.materialization import (
    ArtifactSpec,
    ImageDetails,
    acquire_artifact,
    canonical_image_name,
    canonical_json,
    component_runtime_template,
    ensure_materialized_pycharm,
    formation_descriptor,
    formation_identity,
    parse_locked_environment,
    pycharm_materialization_spec,
    validate_base_image,
    verify_materialized_image,
)


def fixture_archive(path: Path) -> bytes:
    content = b"#!/bin/sh\n"
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo("pycharm-test/bin/pycharm.sh")
        info.mode = 0o755
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    return path.read_bytes()


def artifact(path: Path, digest: str = "a" * 64) -> ArtifactSpec:
    return ArtifactSpec("2026.2.0.1", path.as_uri(), digest, "professional")


def image_details(reference: str, labels: dict[str, str], identity: str = "sha256:image") -> ImageDetails:
    return ImageDetails(reference, identity, labels, "linux", "amd64")


def expected_labels(base_identity: str, spec: ArtifactSpec) -> tuple[str, dict[str, str]]:
    descriptor = formation_descriptor(platform="linux-amd64", base_identity=base_identity, artifact=spec)
    canonical = canonical_image_name(descriptor)
    labels = {
        "devcapsule.image.managed": "true",
        "devcapsule.metadata.version": "1",
        "devcapsule.image.kind": "materialized",
        "devcapsule.image.canonical-name": canonical,
        "devcapsule.materialization.descriptor": canonical_json(descriptor),
        "devcapsule.materialization.identity": formation_identity(descriptor),
        "devcapsule.materialization.recipe-version": "1",
        "devcapsule.materialization.base-identity": base_identity,
        "devcapsule.component.id": "pycharm",
        "devcapsule.component.version": spec.version,
        "devcapsule.component.sha256": spec.sha256,
    }
    return canonical, labels


def test_acquisition_verifies_digest_and_reuses_cache(tmp_path: Path) -> None:
    source = tmp_path / "source.tar.gz"
    payload = fixture_archive(source)
    spec = artifact(source, hashlib.sha256(payload).hexdigest())

    first = acquire_artifact(spec, tmp_path / "cache")
    second = acquire_artifact(spec, tmp_path / "cache")

    assert first.downloaded is True
    assert second.downloaded is False
    assert second.path == first.path
    assert (tmp_path / "cache" / "locks" / "artifacts" / f"{spec.sha256}.lock").is_file()


def test_acquisition_rejects_digest_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source.tar.gz"
    fixture_archive(source)
    spec = artifact(source, "0" * 64)
    with pytest.raises(CliError, match="digest mismatch"):
        acquire_artifact(spec, tmp_path / "cache")


def test_formation_descriptor_is_canonical_and_excludes_checkout_data(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "unused.tar.gz")
    descriptor = formation_descriptor(
        platform="linux-amd64", base_identity="sha256:base", artifact=spec
    )

    assert descriptor["schema"] == {"name": "devcapsule-formation", "version": 1}
    assert descriptor["base"] == {"identity": "sha256:base"}
    assert descriptor["components"][0]["artifact"]["sha256"] == "a" * 64
    encoded = canonical_json(descriptor)
    assert json.loads(encoded) == descriptor
    assert "/workspace" not in encoded
    assert "/home/devcapsule" not in encoded
    assert "uid" not in encoded
    assert len(formation_identity(descriptor)) == 64


def test_materialized_component_template_owns_its_persistence_interface() -> None:
    template = component_runtime_template()
    component = template["component"]
    persistence = component["persistence"]
    slots = {slot["name"]: slot for slot in persistence["state_slots"]}

    assert persistence["home"] == "required"
    assert persistence["xdg"] == "home-relative"
    assert "state_slots" not in template
    assert slots["config"]["kind"] == "durable"
    assert slots["system"]["kind"] == "cache"
    assert slots["cache"]["home_overlay"] is True


def test_materialization_reuses_only_verified_canonical_image(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "missing.tar.gz")
    canonical, labels = expected_labels("sha256:base", spec)
    builds: list[object] = []
    image, created = ensure_materialized_pycharm(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: image_details(reference, labels) if reference == canonical else None,
        build=builds.append,
    )
    assert image == canonical
    assert created is False
    assert builds == []


def test_materialization_rejects_conflicting_canonical_tag(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "missing.tar.gz")
    canonical, labels = expected_labels("sha256:base", spec)
    labels["devcapsule.component.sha256"] = "b" * 64

    with pytest.raises(CliError, match="conflicting or malformed metadata"):
        ensure_materialized_pycharm(
            base_reference="base:debug",
            base_identity="sha256:base",
            platform="linux-amd64",
            artifact=spec,
            cache_root=tmp_path / "cache",
            inspect_image=lambda reference: image_details(reference, labels) if reference == canonical else None,
            build=lambda _spec: None,
        )


def test_materialization_builds_from_verified_archive_and_rechecks_result(tmp_path: Path) -> None:
    source = tmp_path / "pycharm.tar.gz"
    payload = fixture_archive(source)
    spec = artifact(source, hashlib.sha256(payload).hexdigest())
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        labels = dict(plan.labels)
        built[plan.image] = image_details(plan.image, labels)
        assert plan.base_image == "base:debug"
        assert any(copy.destination == "/opt/jetbrains/pycharm" for copy in plan.directories)
        assert any(copy.destination == "/etc/devcapsule/component-runtime-template.json" for copy in plan.files)
        assert not any(copy.destination == "/etc/devcapsule/runtime-plan.json" for copy in plan.files)

    image, created = ensure_materialized_pycharm(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
    )

    assert created is True
    assert image in built
    assert (tmp_path / "cache" / "locks" / "materializations").is_dir()


def test_materialized_image_has_complete_formation_labels(tmp_path: Path) -> None:
    pycharm = tmp_path / "pycharm"
    pycharm.mkdir()
    template = tmp_path / "component-template.json"
    template.write_text(canonical_json(component_runtime_template()), encoding="utf-8")
    spec = artifact(tmp_path / "pycharm.tar.gz")
    descriptor = formation_descriptor(platform="linux-amd64", base_identity="sha256:base", artifact=spec)
    image = canonical_image_name(descriptor)

    plan = pycharm_materialization_spec(
        base_reference="base:debug",
        base_identity="sha256:base",
        image=image,
        pycharm_root=pycharm,
        component_template=template,
        artifact=spec,
    ).build_plan()
    labels = dict(plan.labels)

    assert labels["devcapsule.image.kind"] == "materialized"
    assert labels["devcapsule.image.canonical-name"] == image
    assert labels["devcapsule.materialization.descriptor"] == canonical_json(descriptor)
    assert labels["devcapsule.materialization.identity"] == formation_identity(descriptor)
    assert labels["devcapsule.materialization.base-identity"] == "sha256:base"
    assert labels["devcapsule.component.version"] == "2026.2.0.1"
    verify_materialized_image(image_details(image, labels), descriptor=descriptor, canonical_name=image)


def test_parse_locked_environment_and_validate_managed_base() -> None:
    locked = parse_locked_environment(
        {
            "platform": "linux-amd64",
            "base": {"reference": "base@sha256:manifest", "identity": "sha256:base"},
            "components": {
                "interactive-surface": "pycharm",
                "pycharm": {
                    "version": "2026.2.0.1",
                    "variant": "professional",
                    "delivery-policy": "local-materialization",
                    "url": "https://example.test/pycharm.tar.gz",
                    "sha256": "a" * 64,
                },
            },
            "materialization": {"recipe": "jetbrains-local-materialization", "recipe-version": "1"},
        }
    )
    assert locked.component_id == "pycharm"
    assert locked.artifact.version == "2026.2.0.1"

    validate_base_image(
        image_details(
            locked.base_reference,
            {
                "devcapsule.image.managed": "true",
                "devcapsule.metadata.version": "1",
                "devcapsule.image.kind": "base",
            },
            identity="sha256:base",
        ),
        platform=locked.platform,
        expected_identity=locked.base_identity,
    )


def test_validate_base_rejects_wrong_identity() -> None:
    details = image_details(
        "base:debug",
        {
            "devcapsule.image.managed": "true",
            "devcapsule.metadata.version": "1",
            "devcapsule.image.kind": "base",
        },
        identity="sha256:other",
    )
    with pytest.raises(CliError, match="identity mismatch"):
        validate_base_image(details, platform="linux-amd64", expected_identity="sha256:expected")
