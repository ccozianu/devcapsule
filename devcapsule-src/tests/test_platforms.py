"""Tests for the host/platform friction module (D-0006)."""

from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule.platforms import Platform, UnsupportedPlatformError, XdgHomes


def test_platform_values_are_the_wire_format() -> None:
    assert Platform.LINUX_AMD64.value == "linux-amd64"
    # StrEnum: the member formats as its value wherever locks and filenames
    # interpolate it.
    assert f"devcapsule.{Platform.LINUX_AMD64}.lock" == "devcapsule.linux-amd64.lock"


def test_parse_accepts_every_member_and_only_members() -> None:
    for member in Platform:
        assert Platform.parse(member.value) is member
    with pytest.raises(UnsupportedPlatformError) as failure:
        Platform.parse("windows-arm64")
    message = str(failure.value)
    assert "'windows-arm64'" in message
    assert "linux-amd64" in message


def test_current_returns_a_member_on_a_supported_host() -> None:
    # The test suite only runs on supported platforms, so detection must
    # succeed and agree with parse().
    current = Platform.current()
    assert current in Platform
    assert Platform.parse(current.value) is current


def test_xdg_homes_honor_explicit_overrides() -> None:
    homes = XdgHomes.from_environment(
        {
            "HOME": "/home/dev",
            "XDG_CONFIG_HOME": "/elsewhere/config",
            "XDG_DATA_HOME": "/elsewhere/data",
            "XDG_STATE_HOME": "/elsewhere/state",
            "XDG_CACHE_HOME": "/elsewhere/cache",
        }
    )

    assert homes.config == Path("/elsewhere/config/devcapsule")
    assert homes.data == Path("/elsewhere/data/devcapsule")
    assert homes.state == Path("/elsewhere/state/devcapsule")
    assert homes.cache == Path("/elsewhere/cache/devcapsule")


def test_xdg_homes_fall_back_to_the_specified_defaults() -> None:
    homes = XdgHomes.from_environment({"HOME": "/home/dev"})

    assert homes.config == Path("/home/dev/.config/devcapsule")
    assert homes.data == Path("/home/dev/.local/share/devcapsule")
    assert homes.state == Path("/home/dev/.local/state/devcapsule")
    assert homes.cache == Path("/home/dev/.cache/devcapsule")


def test_xdg_empty_override_means_unset() -> None:
    # The XDG spec treats an empty variable as unset; the derivation must
    # fall back rather than produce a relative path.
    homes = XdgHomes.from_environment({"HOME": "/home/dev", "XDG_CACHE_HOME": ""})

    assert homes.cache == Path("/home/dev/.cache/devcapsule")
