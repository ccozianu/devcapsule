from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from devcapsule.compat import CliError
from devcapsule.environment_realization import ensure_local_image, realize_environment
from devcapsule.materialization import ImageDetails
from devcapsule.project_configuration import ResolvedProject, canonical_digest


BASE_REFERENCE = f"docker.io/example/devcapsule-base@sha256:{'b' * 64}"
CANONICAL_IMAGE = "devcapsule-local-pycharm:0123456789abcdef0123"


def resolved_project(tmp_path: Path, *, authorized: bool = True) -> ResolvedProject:
    lock = {
        "platform": "linux-amd64",
        "base": {"reference": BASE_REFERENCE, "identity": "sha256:base"},
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
        "materialization": {
            "recipe": "jetbrains-local-materialization",
            "recipe-version": "1",
        },
    }
    checkout = {}
    if authorized:
        checkout = {
            "authorization": {
                "base-image": {
                    "reference": BASE_REFERENCE,
                    "lock-digest": canonical_digest(lock),
                }
            }
        }
    return ResolvedProject(
        root=tmp_path / "project",
        manifest={"project": {"creator": "example", "slug": "project"}},
        lock_path=tmp_path / "project" / ".devcapsule" / "devcapsule.linux-amd64.lock",
        lock=lock,
        checkout_path=tmp_path / "checkout.toml",
        checkout=checkout,
        resolution_path=tmp_path / "resolved.toml",
        resolution={"runtime": {"component": "pycharm"}},
    )


def base_image(reference: str = BASE_REFERENCE, identity: str = "sha256:base") -> ImageDetails:
    return ImageDetails(
        reference=reference,
        identity=identity,
        labels={
            "devcapsule.image.managed": "true",
            "devcapsule.metadata.version": "1",
            "devcapsule.image.kind": "base",
        },
        operating_system="linux",
        architecture="amd64",
    )


def completed_image() -> ImageDetails:
    return ImageDetails(
        reference=CANONICAL_IMAGE,
        identity="sha256:environment",
        labels={"devcapsule.materialization.identity": "f" * 64},
        operating_system="linux",
        architecture="amd64",
    )


@pytest.mark.parametrize("created", [False, True])
def test_realize_environment_reuses_or_builds_canonical_image(
    tmp_path: Path, created: bool
) -> None:
    selected = resolved_project(tmp_path)
    base = base_image()
    completed = completed_image()
    obtain = Mock(return_value=base)
    inspect = Mock()
    require = Mock(return_value=completed)
    build = Mock()
    materialize = Mock(return_value=(CANONICAL_IMAGE, created))

    realized = realize_environment(
        selected,
        root=tmp_path / "cache",
        obtain_image=obtain,
        inspect_image=inspect,
        require_image=require,
        build=build,
        materialize=materialize,
    )

    assert realized.image == completed
    assert realized.base == base
    assert realized.created is created
    assert realized.explicit_base_override is False
    obtain.assert_called_once_with(BASE_REFERENCE)
    require.assert_called_once_with(CANONICAL_IMAGE)
    assert materialize.call_args.kwargs["base_reference"] == BASE_REFERENCE
    assert materialize.call_args.kwargs["base_identity"] == "sha256:base"
    assert materialize.call_args.kwargs["platform"] == "linux-amd64"
    assert materialize.call_args.kwargs["cache_root"] == (tmp_path / "cache").resolve()
    assert materialize.call_args.kwargs["inspect_image"] is inspect
    assert materialize.call_args.kwargs["build"] is build


def test_realize_environment_requires_exact_locked_base_authorization(tmp_path: Path) -> None:
    selected = resolved_project(tmp_path, authorized=False)
    obtain = Mock()
    materialize = Mock()

    with pytest.raises(CliError, match="config authorize base-image"):
        realize_environment(
            selected,
            obtain_image=obtain,
            materialize=materialize,
        )

    obtain.assert_not_called()
    materialize.assert_not_called()


@pytest.mark.parametrize("already_local", [True, False])
def test_ensure_local_image_pulls_only_when_missing(already_local: bool) -> None:
    details = base_image()
    with (
        patch(
            "devcapsule.environment_realization.docker.image.exists",
            return_value=already_local,
        ),
        patch("devcapsule.environment_realization.docker.image.pull") as pull,
        patch(
            "devcapsule.environment_realization.required_local_image",
            return_value=details,
        ) as require,
    ):
        assert ensure_local_image(BASE_REFERENCE) == details

    if already_local:
        pull.assert_not_called()
    else:
        pull.assert_called_once_with(BASE_REFERENCE)
    require.assert_called_once_with(BASE_REFERENCE)


def test_realize_environment_allows_explicit_managed_base_override(tmp_path: Path) -> None:
    selected = resolved_project(tmp_path, authorized=False)
    local_reference = "local/devcapsule-base:test"
    base = base_image(local_reference, "sha256:local-base")
    completed = completed_image()

    realized = realize_environment(
        selected,
        base_override=local_reference,
        root=tmp_path / "cache",
        obtain_image=Mock(return_value=base),
        inspect_image=Mock(),
        require_image=Mock(return_value=completed),
        build=Mock(),
        materialize=Mock(return_value=(CANONICAL_IMAGE, False)),
    )

    assert realized.base_reference == local_reference
    assert realized.base.identity == "sha256:local-base"
    assert realized.explicit_base_override is True


def test_realize_environment_propagates_canonical_conflict_without_launch(
    tmp_path: Path,
) -> None:
    selected = resolved_project(tmp_path)
    require = Mock()
    conflict = CliError("canonical image has conflicting metadata")

    with pytest.raises(CliError, match="conflicting metadata"):
        realize_environment(
            selected,
            root=tmp_path / "cache",
            obtain_image=Mock(return_value=base_image()),
            inspect_image=Mock(),
            require_image=require,
            build=Mock(),
            materialize=Mock(side_effect=conflict),
        )

    require.assert_not_called()
