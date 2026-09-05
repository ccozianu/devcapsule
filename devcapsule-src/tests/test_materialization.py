from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile

import pytest

from devcapsule.compat import CliError
from devcapsule.components import LockedArtifactDeclaration
from devcapsule.image_build import ExecStep
from devcapsule.materialization import (
    ENTRYPOINT_CONTRACT,
    RUNTIME_PLAN_PATH,
    descriptor_differences,
    ArtifactSpec,
    ImageDetails,
    acquire_artifact,
    canonical_image_name,
    canonical_json,
    component_runtime_template,
    ensure_materialized_surface,
    formation_descriptor,
    formation_identity,
    npm_install_step,
    parse_locked_environment,
    surface_materialization_spec,
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


def member_archive(path: Path, member: str) -> bytes:
    content = b"tool-binary-fixture"
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo(member)
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


def codium_fixture_archive(path: Path) -> bytes:
    # Real VSCodium archives are flat: the installation sits at the archive
    # root instead of inside one wrapping directory.
    with tarfile.open(path, "w:gz") as archive:
        for member, content in (
            ("./codium", b"electron-binary-fixture"),
            ("./bin/codium", b"#!/bin/sh\n"),
            ("./chrome-sandbox", b"sandbox-helper-fixture"),
            ("./product.json", b"{}\n"),
        ):
            info = tarfile.TarInfo(member)
            info.mode = 0o755
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return path.read_bytes()


def codium_artifact(path: Path, digest: str = "b" * 64) -> ArtifactSpec:
    return ArtifactSpec("1.126.04524", path.as_uri(), digest, None)


def test_codium_formation_descriptor_has_no_variant_and_its_own_recipe(tmp_path: Path) -> None:
    descriptor = formation_descriptor(
        platform="linux-amd64",
        base_identity="sha256:base",
        artifact=codium_artifact(tmp_path / "unused.tar.gz"),
        recipe_id="vscode-local-materialization",
        component_id="codium",
    )

    assert descriptor["components"][0]["id"] == "codium"
    assert "variant" not in descriptor["components"][0]
    assert descriptor["recipe"]["id"] == "vscode-local-materialization"
    assert descriptor["recipe"]["parameters"] == {"installation-path": "/opt/codium"}


def test_codium_materialization_builds_an_image_with_no_setuid_binary(tmp_path: Path) -> None:
    # Recipe version 2 (product-owner ruling 2026-09-02): renderers run
    # --no-sandbox, so no step marks chrome-sandbox setuid-root; see the
    # renderer-sandboxing design note.
    source = tmp_path / "codium.tar.gz"
    payload = codium_fixture_archive(source)
    spec = codium_artifact(source, hashlib.sha256(payload).hexdigest())
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        assert any(copy.destination == "/opt/codium" for copy in plan.directories)
        assert plan.exec_steps == ()
        labels = dict(plan.labels)
        assert labels["devcapsule.component.id"] == "codium"
        assert labels["devcapsule.component.vscode.version"] == "1.126.04524"
        assert labels["devcapsule.materialization.recipe-version"] == "2"
        assert "devcapsule.component.variant" not in labels
        built[plan.image] = image_details(plan.image, labels)

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
        recipe_id="vscode-local-materialization",
        recipe_version="2",
        component_id="codium",
    )

    assert created is True
    assert image.startswith("devcapsule-local-codium:")


def test_codium_materialization_rejects_an_archive_without_the_sandbox_helper(tmp_path: Path) -> None:
    source = tmp_path / "codium.tar.gz"
    payload = fixture_archive(source)  # a JetBrains-shaped archive
    spec = codium_artifact(source, hashlib.sha256(payload).hexdigest())

    with pytest.raises(CliError, match="does not contain codium"):
        ensure_materialized_surface(
            base_reference="base:debug",
            base_identity="sha256:base",
            platform="linux-amd64",
            artifact=spec,
            cache_root=tmp_path / "cache",
            inspect_image=lambda reference: None,
            build=lambda _spec: None,
            recipe_id="vscode-local-materialization",
            component_id="codium",
        )


def test_codium_lock_parses_without_variant(tmp_path: Path) -> None:
    locked = parse_locked_environment(
        {
            "platform": "linux-amd64",
            "base": {"reference": "docker.io/example/base@sha256:abc"},
            "components": {
                "interactive-surface": "codium",
                "codium": {
                    "version": "1.126.04524",
                    "delivery-policy": "local-materialization",
                    "url": "https://example.invalid/codium.tar.gz",
                    "sha256": "b" * 64,
                },
            },
            "materialization": {
                "recipe": "vscode-local-materialization",
                "recipe-version": "2",
            },
        }
    )

    assert locked.component_id == "codium"
    assert locked.artifact.variant is None
    assert locked.recipe_id == "vscode-local-materialization"


def test_codium_lock_rejects_the_jetbrains_recipe() -> None:
    with pytest.raises(CliError, match="vscode-local-materialization"):
        parse_locked_environment(
            {
                "platform": "linux-amd64",
                "base": {"reference": "docker.io/example/base@sha256:abc"},
                "components": {
                    "interactive-surface": "codium",
                    "codium": {
                        "version": "1.126.04524",
                        "delivery-policy": "local-materialization",
                        "url": "https://example.invalid/codium.tar.gz",
                        "sha256": "b" * 64,
                    },
                },
                "materialization": {
                    "recipe": "jetbrains-local-materialization",
                    "recipe-version": "1",
                },
            }
        )


def test_codium_lock_from_the_setuid_recipe_era_is_rejected() -> None:
    # A version-1 codium lock predates the --no-sandbox posture; building it
    # with the version-2 recipe would produce an image its recorded recipe no
    # longer describes, so it must fail loudly toward re-init.
    with pytest.raises(CliError, match="'vscode-local-materialization'@2"):
        parse_locked_environment(
            {
                "platform": "linux-amd64",
                "base": {"reference": "docker.io/example/base@sha256:abc"},
                "components": {
                    "interactive-surface": "codium",
                    "codium": {
                        "version": "1.126.04524",
                        "delivery-policy": "local-materialization",
                        "url": "https://example.invalid/codium.tar.gz",
                        "sha256": "b" * 64,
                    },
                },
                "materialization": {
                    "recipe": "vscode-local-materialization",
                    "recipe-version": "1",
                },
            }
        )


def test_materialization_reuses_only_verified_canonical_image(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "missing.tar.gz")
    canonical, labels = expected_labels("sha256:base", spec)
    builds: list[object] = []
    image, created = ensure_materialized_surface(
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
        ensure_materialized_surface(
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

    image, created = ensure_materialized_surface(
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


def test_materialization_extracts_a_locked_archive_member(tmp_path: Path) -> None:
    pycharm_source = tmp_path / "pycharm.tar.gz"
    pycharm_payload = fixture_archive(pycharm_source)
    pycharm_spec = artifact(pycharm_source, hashlib.sha256(pycharm_payload).hexdigest())
    member = "antigravity"
    tool_source = tmp_path / "antigravity.tar.gz"
    tool_payload = member_archive(tool_source, member)
    tool = LockedArtifactDeclaration(
        component_id="antigravity-cli",
        version="1.1.24",
        url=tool_source.as_uri(),
        sha256=hashlib.sha256(tool_payload).hexdigest(),
        archive_member=member,
        destination="/opt/antigravity-cli/bin/antigravity",
    )
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        copied = next(
            copy for copy in plan.files if copy.destination == "/opt/antigravity-cli/bin/antigravity"
        )
        assert copied.source.read_bytes() == b"tool-binary-fixture"
        assert copied.permissions == 0o755
        assert plan.exec_steps == ()
        labels = dict(plan.labels)
        built[plan.image] = image_details(plan.image, labels)

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=pycharm_spec,
        ancillary_artifacts=(tool,),
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
    )

    assert created is True
    descriptor = json.loads(built[image].labels["devcapsule.materialization.descriptor"])
    assert descriptor["components"][1]["id"] == "antigravity-cli"
    assert descriptor["components"][1]["artifact"]["sha256"] == tool.sha256
    assert descriptor["components"][1]["installation"] == {
        "archive-member": member,
        "destination": "/opt/antigravity-cli/bin/antigravity",
        "format": "tar-gz-member",
    }


def codex_npm_declarations(tmp_path: Path) -> tuple[LockedArtifactDeclaration, ...]:
    """Two verified npm tarballs, the shape the codex component declares."""

    meta_source = tmp_path / "codex-0.153.0.tgz"
    meta_source.write_bytes(b"meta-package-tarball")
    platform_source = tmp_path / "codex-0.153.0-linux-x64.tgz"
    platform_source.write_bytes(b"platform-package-tarball")
    return (
        LockedArtifactDeclaration(
            component_id="codex",
            version="0.153.0",
            url=meta_source.as_uri(),
            sha256=hashlib.sha256(meta_source.read_bytes()).hexdigest(),
            destination="/opt/codex/0.153.0",
            artifact_format="npm-package",
            npm_package="@openai/codex",
            permissions=0o644,
            environment=(("PATH", "/opt/codex/0.153.0/node_modules/.bin:${PATH}"),),
        ),
        LockedArtifactDeclaration(
            component_id="codex",
            version="0.153.0",
            url=platform_source.as_uri(),
            sha256=hashlib.sha256(platform_source.read_bytes()).hexdigest(),
            destination="/opt/codex/0.153.0",
            artifact_format="npm-package",
            npm_package="@openai/codex-linux-x64",
            permissions=0o644,
        ),
    )


def test_materialization_installs_npm_packages_with_npm_offline(tmp_path: Path) -> None:
    pycharm_source = tmp_path / "pycharm.tar.gz"
    pycharm_payload = fixture_archive(pycharm_source)
    pycharm_spec = artifact(pycharm_source, hashlib.sha256(pycharm_payload).hexdigest())
    meta, platform = codex_npm_declarations(tmp_path)
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        copies = {copy.destination: copy for copy in plan.files}
        # The verified tarballs travel whole, named as npm published them,
        # beside a manifest that declares each as a file: dependency.
        assert copies["/opt/codex/0.153.0/codex-0.153.0.tgz"].source.read_bytes() == (
            b"meta-package-tarball"
        )
        assert copies["/opt/codex/0.153.0/codex-0.153.0-linux-x64.tgz"].source.read_bytes() == (
            b"platform-package-tarball"
        )
        assert copies["/opt/codex/0.153.0/codex-0.153.0.tgz"].permissions == 0o644
        manifest = json.loads(copies["/opt/codex/0.153.0/package.json"].source.read_text())
        assert manifest == {
            "name": "devcapsule-codex",
            "version": "0.0.0",
            "private": True,
            "dependencies": {
                "@openai/codex": "file:./codex-0.153.0.tgz",
                "@openai/codex-linux-x64": "file:./codex-0.153.0-linux-x64.tgz",
            },
        }
        # One offline install per project, after every copy, with the cache
        # scrubbed in the same step; the launcher directory joins PATH.
        assert plan.exec_steps == (ExecStep(npm_install_step("/opt/codex/0.153.0")),)
        assert npm_install_step("/opt/codex/0.153.0") == (
            "sh",
            "-c",
            "npm_config_cache=/tmp/devcapsule-npm-cache npm --prefix '/opt/codex/0.153.0' "
            "install --offline --ignore-scripts --no-audit --no-fund --no-update-notifier "
            "--loglevel=error --logs-max=0 && rm -rf /tmp/devcapsule-npm-cache",
        )
        assert ("PATH", "/opt/codex/0.153.0/node_modules/.bin:${PATH}") in plan.env
        built[plan.image] = image_details(plan.image, dict(plan.labels))

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=pycharm_spec,
        ancillary_artifacts=(meta, platform),
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
    )

    assert created is True
    descriptor = json.loads(built[image].labels["devcapsule.materialization.descriptor"])
    assert [item["id"] for item in descriptor["components"]] == ["pycharm", "codex", "codex"]
    assert descriptor["components"][1]["installation"] == {
        "destination": "/opt/codex/0.153.0",
        "format": "npm-package",
        "npm-package": "@openai/codex",
    }
    assert descriptor["components"][2]["installation"] == {
        "destination": "/opt/codex/0.153.0",
        "format": "npm-package",
        "npm-package": "@openai/codex-linux-x64",
    }


def test_npm_package_artifacts_are_validated_when_the_lock_is_read() -> None:
    def lock(**codex: object) -> dict:
        return {
            "platform": "linux-amd64",
            "base": {"reference": "base@sha256:manifest"},
            "components": {
                "interactive-surface": "pycharm",
                "pycharm": {
                    "version": "2026.2.0.1",
                    "variant": "professional",
                    "delivery-policy": "local-materialization",
                    "url": "https://example.test/pycharm.tar.gz",
                    "sha256": "a" * 64,
                },
                "codex": {
                    "version": "0.153.0",
                    "delivery-policy": "local-materialization",
                    "npm-package": "@openai/codex",
                    "url": "https://example.test/codex-0.153.0.tgz",
                    "sha256": "b" * 64,
                    "artifacts": {
                        "linux-amd64": {
                            "npm-package": "@openai/codex-linux-x64",
                            "url": "https://example.test/codex-0.153.0-linux-x64.tgz",
                            "sha256": "c" * 64,
                        }
                    },
                    **codex,
                },
            },
            "materialization": {"recipe": "jetbrains-local-materialization", "recipe-version": "1"},
        }

    locked = parse_locked_environment(lock())
    assert [item.npm_package for item in locked.ancillary_artifacts] == [
        "@openai/codex",
        "@openai/codex-linux-x64",
    ]

    with pytest.raises(CliError, match="must end in a tarball file name"):
        parse_locked_environment(lock(url="https://example.test/codex/"))


def test_npm_projects_refuse_a_directory_shared_by_two_components(tmp_path: Path) -> None:
    from devcapsule.materialization import _npm_projects

    meta, platform = codex_npm_declarations(tmp_path)
    other = LockedArtifactDeclaration(
        component_id="other-agent",
        version="1",
        url="https://example.test/other-1.tgz",
        sha256="d" * 64,
        destination="/opt/codex/0.153.0",
        artifact_format="npm-package",
        npm_package="@example/other",
    )
    with pytest.raises(CliError, match="claimed by several components: codex, other-agent"):
        _npm_projects(((tmp_path, meta), (tmp_path, platform), (tmp_path, other)), tmp_path)

    duplicate = LockedArtifactDeclaration(
        component_id="codex",
        version="0.153.0",
        url="https://example.test/codex-again.tgz",
        sha256="d" * 64,
        destination="/opt/codex/0.153.0",
        artifact_format="npm-package",
        npm_package="@openai/codex",
    )
    with pytest.raises(CliError, match="declares npm package '@openai/codex' twice"):
        _npm_projects(((tmp_path, meta), (tmp_path, duplicate)), tmp_path)


def test_materialization_installs_locked_raw_executable_and_image_environment(
    tmp_path: Path,
) -> None:
    pycharm_source = tmp_path / "pycharm.tar.gz"
    pycharm_payload = fixture_archive(pycharm_source)
    pycharm_spec = artifact(pycharm_source, hashlib.sha256(pycharm_payload).hexdigest())
    claude_source = tmp_path / "claude"
    claude_source.write_bytes(b"claude-code-binary-fixture")
    claude = LockedArtifactDeclaration(
        component_id="claude-code",
        version="2.1.227",
        url=claude_source.as_uri(),
        sha256=hashlib.sha256(claude_source.read_bytes()).hexdigest(),
        destination="/opt/claude/bin/claude",
        artifact_format="file",
        environment=(
            ("PATH", "/opt/claude/bin:${PATH}"),
            ("DISABLE_UPDATES", "1"),
        ),
    )
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        copied = next(
            item for item in plan.files if item.destination == "/opt/claude/bin/claude"
        )
        assert copied.source.read_bytes() == b"claude-code-binary-fixture"
        assert copied.permissions == 0o755
        assert ("PATH", "/opt/claude/bin:${PATH}") in plan.env
        assert ("DISABLE_UPDATES", "1") in plan.env
        built[plan.image] = image_details(plan.image, dict(plan.labels))

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=pycharm_spec,
        ancillary_artifacts=(claude,),
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
    )

    assert created is True
    descriptor = json.loads(built[image].labels["devcapsule.materialization.descriptor"])
    assert descriptor["components"][1]["installation"] == {
        "destination": "/opt/claude/bin/claude",
        "format": "file",
    }


def test_materialized_image_has_complete_formation_labels(tmp_path: Path) -> None:
    pycharm = tmp_path / "pycharm"
    pycharm.mkdir()
    template = tmp_path / "component-template.json"
    template.write_text(canonical_json(component_runtime_template()), encoding="utf-8")
    spec = artifact(tmp_path / "pycharm.tar.gz")
    descriptor = formation_descriptor(platform="linux-amd64", base_identity="sha256:base", artifact=spec)
    image = canonical_image_name(descriptor)

    plan = surface_materialization_spec(
        base_reference="base:debug",
        base_identity="sha256:base",
        image=image,
        surface_root=pycharm,
        component_template=template,
        artifact=spec,
        platform="linux-amd64",
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


def test_ancillary_environment_chains_path_prefixes_and_rejects_conflicts() -> None:
    """Several components may each prepend a bin directory to PATH; any other
    disagreement over one variable is a contract conflict."""

    from devcapsule.materialization import _ancillary_environment

    def declaration(component_id: str, environment: tuple[tuple[str, str], ...]):
        return LockedArtifactDeclaration(
            component_id=component_id,
            version="1",
            url="https://example.invalid/artifact",
            sha256="a" * 64,
            destination=f"/opt/{component_id}/bin/{component_id}",
            environment=environment,
        )

    merged = dict(
        _ancillary_environment(
            (
                declaration("claude-code", (("PATH", "/opt/claude/bin:${PATH}"),)),
                declaration("antigravity-cli", (("PATH", "/opt/antigravity-cli/bin:${PATH}"),)),
            )
        )
    )
    assert merged["PATH"] == "/opt/claude/bin:/opt/antigravity-cli/bin:${PATH}"

    with pytest.raises(CliError, match="conflicting values for environment DISABLE_UPDATES"):
        _ancillary_environment(
            (
                declaration("claude-code", (("DISABLE_UPDATES", "1"),)),
                declaration("other", (("DISABLE_UPDATES", "0"),)),
            )
        )


# ---------------------------------------------------------------------------
# Boot-contract enforcement (the 2026-09-02 formation-identity record,
# entrypoint half ruled 2026-09-05)


def test_materialization_recipe_enforces_the_boot_contract(tmp_path: Path) -> None:
    source = tmp_path / "pycharm.tar.gz"
    payload = fixture_archive(source)
    spec = artifact(source, hashlib.sha256(payload).hexdigest())
    built: dict[str, ImageDetails] = {}

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        assert plan.entrypoint == ENTRYPOINT_CONTRACT
        assert plan.command == (RUNTIME_PLAN_PATH,)
        built[plan.image] = ImageDetails(
            plan.image,
            "sha256:image",
            dict(plan.labels),
            "linux",
            "amd64",
            entrypoint=plan.entrypoint,
            command=plan.command,
        )

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
    )
    assert created is True
    # The post-build recheck accepted an image whose actual boot
    # configuration equals the descriptor claim.
    assert built[image].entrypoint == ENTRYPOINT_CONTRACT


def test_existing_image_with_stale_boot_config_is_repaired_in_place(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "missing.tar.gz")
    canonical, labels = expected_labels("sha256:base", spec)
    stale = ImageDetails(
        canonical,
        "sha256:stale",
        labels,
        "linux",
        "amd64",
        entrypoint=("/usr/bin/tini", "--") + ENTRYPOINT_CONTRACT,
        command=(RUNTIME_PLAN_PATH,),
    )
    state = {"current": stale}
    repairs: list[object] = []
    messages: list[str] = []

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        repairs.append(build_spec)
        # Configuration-only: FROM the canonical tag (held still by the
        # materialization lock), no content steps, just the boot contract.
        assert plan.base_image == canonical
        assert plan.directories == () and plan.files == () and plan.labels == ()
        assert plan.entrypoint == ENTRYPOINT_CONTRACT
        assert plan.command == (RUNTIME_PLAN_PATH,)
        state["current"] = ImageDetails(
            canonical,
            "sha256:repaired",
            labels,
            "linux",
            "amd64",
            entrypoint=plan.entrypoint,
            command=plan.command,
        )

    image, created = ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: state["current"] if reference == canonical else None,
        build=build,
        report=messages.append,
    )
    assert image == canonical
    assert created is False
    assert len(repairs) == 1
    assert any("Enforcing the recorded boot contract" in message for message in messages)


def test_verify_rejects_boot_config_contradicting_descriptor(tmp_path: Path) -> None:
    spec = artifact(tmp_path / "missing.tar.gz")
    canonical, labels = expected_labels("sha256:base", spec)
    descriptor = formation_descriptor(
        platform="linux-amd64", base_identity="sha256:base", artifact=spec
    )
    lying = ImageDetails(
        canonical,
        "sha256:image",
        labels,
        "linux",
        "amd64",
        entrypoint=("/usr/bin/tini", "--") + ENTRYPOINT_CONTRACT,
        command=(RUNTIME_PLAN_PATH,),
    )
    with pytest.raises(CliError, match="boots differently"):
        verify_materialized_image(lying, descriptor=descriptor, canonical_name=canonical)


def test_materialization_explains_first_and_nearest_formations(tmp_path: Path) -> None:
    source = tmp_path / "pycharm.tar.gz"
    payload = fixture_archive(source)
    spec = artifact(source, hashlib.sha256(payload).hexdigest())
    _prior_canonical, prior_labels = expected_labels("sha256:otherbase", spec)
    prior = ImageDetails(
        "devcapsule-local-pycharm:oldtag",
        "sha256:prior",
        prior_labels,
        "linux",
        "amd64",
        size_bytes=7_000_000_000,
    )
    built: dict[str, ImageDetails] = {}
    messages: list[str] = []

    def build(build_spec) -> None:
        plan = build_spec.build_plan()
        built[plan.image] = ImageDetails(
            plan.image,
            "sha256:image",
            dict(plan.labels),
            "linux",
            "amd64",
            entrypoint=plan.entrypoint,
            command=plan.command,
        )

    ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache",
        inspect_image=lambda reference: built.get(reference),
        build=build,
        report=messages.append,
        list_formations=lambda: (prior,),
    )
    assert any(
        "differs from devcapsule-local-pycharm:oldtag in base.identity" in message
        for message in messages
    )
    assert any(
        "Prior pycharm formation images remain (7.0 GB total)" in message
        for message in messages
    )

    messages.clear()
    built.clear()
    ensure_materialized_surface(
        base_reference="base:debug",
        base_identity="sha256:base",
        platform="linux-amd64",
        artifact=spec,
        cache_root=tmp_path / "cache2",
        inspect_image=lambda reference: built.get(reference),
        build=build,
        report=messages.append,
        list_formations=lambda: (),
    )
    assert any("first pycharm formation on this host" in message for message in messages)


def test_descriptor_differences_reports_leaf_paths() -> None:
    expected = {"base": {"identity": "a"}, "runtime": {"entrypoint": ["x"], "command": ["c"]}}
    actual = {"base": {"identity": "b"}, "runtime": {"entrypoint": ["y"], "command": ["c"]}}
    assert descriptor_differences(expected, actual) == (
        "base.identity",
        "runtime.entrypoint",
    )
