"""VS Code discovery, local materialization, foreground contract, state slots, and home trust."""

from __future__ import annotations

from copy import deepcopy
import io
from pathlib import Path
import tarfile
import tomllib
from types import SimpleNamespace
from typing import cast

import pytest

from devcapsule import cli
from devcapsule.commands._run_flow import RunFlags, prepare_launch
from devcapsule.compat import CliError, DecisionPending
from devcapsule.components import discovery
from devcapsule.components.vscode import (
    DEFINITION,
    VSCODE_AUTHORIZATION,
    VSCODE_INSTALLATION_PATH,
    VSCODE_TERMS_URL,
    logical_state_slots,
)
from devcapsule.configuration.authorization import review_authorizations
from devcapsule.configuration.home_channels import known_channels
from devcapsule.configuration.storage import (
    checkout_record_paths,
    load_settings,
    load_toml,
    manifest_for,
    settings_path,
)
from devcapsule.configuration.trust import BASE_CHANNEL, HomeTrust, channels_for
from devcapsule.container_runtime import entrypoint
from devcapsule.container_runtime.components.vscode import plan
from devcapsule.container_runtime.contract import Identity, RuntimePlan
from devcapsule.images.build import ContributionComponent, DirectoryComponent, ExecComponent
from devcapsule.launch.pycharm._launcher import (
    PycharmRunConfig,
    declared_shared_memory_size,
    launches_unsandboxed_renderers,
)
from devcapsule.materialization import (
    ArtifactSpec,
    canonical_json,
    component_runtime_template,
    normalize_archive_directory,
    parse_locked_environment,
    surface_materialization_spec,
    surface_profile,
)
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES


MATRIX = MATRICES[Platform.LINUX_AMD64]


def _runtime_plan() -> RuntimePlan:
    return RuntimePlan.for_component(
        DEFINITION.runtime_template(),
        project_path="/workspace/project",
        home="/home/devcapsule",
        identity=Identity(1000, 1000),
    )


def test_vscode_component_and_foreground_runtime_contract() -> None:
    assert DEFINITION.id == "vscode"
    assert DEFINITION.capability == "vscode-ide"
    contract = DEFINITION.acquisition()
    assert contract is not None
    assert (contract.authorization, contract.terms_url, contract.display_name, contract.vendor) == (
        VSCODE_AUTHORIZATION,
        VSCODE_TERMS_URL,
        "Visual Studio Code",
        "Microsoft",
    )
    assert logical_state_slots() == ("vscode/user-data", "vscode/extensions", "vscode/cache")
    template = DEFINITION.runtime_template()
    assert template.persistence.home == "required"
    assert template.persistence.xdg == "home-relative"
    assert template.component.environment == {"DONT_PROMPT_WSL_INSTALL": "1"}
    runtime = _runtime_plan()
    run_config = cast(PycharmRunConfig, SimpleNamespace(runtime_plan=runtime))
    assert launches_unsandboxed_renderers(run_config) is True
    assert declared_shared_memory_size(run_config) == "640m"
    assert runtime.slots_by_name() == {
        "vscode/user-data": "/ide-user-data",
        "vscode/extensions": "/ide-extensions",
        "vscode/cache": "/home/devcapsule/.cache",
    }
    planned = plan(runtime)
    assert planned.command == (
        "/opt/vscode/code",
        "--user-data-dir=/ide-user-data",
        "--extensions-dir=/ide-extensions",
        "--no-sandbox",
        "/workspace/project",
    )


def test_entrypoint_supervises_vscode_foreground_binary_with_wsl_prompt_suppressed(monkeypatch: pytest.MonkeyPatch) -> None:
    children = []
    env: dict[str, str] = {}
    monkeypatch.setattr(entrypoint, "prepare_filesystem", lambda *args: None)
    monkeypatch.setattr(entrypoint.os, "environ", env)
    monkeypatch.setattr(entrypoint.os, "geteuid", lambda: 0)

    class Supervisor:
        def __init__(self, selected, **_logging):
            children.extend(selected)

        def run(self) -> int:
            return 0

    monkeypatch.setattr(entrypoint, "Supervisor", Supervisor)
    assert entrypoint.run(_runtime_plan()) == 0
    (child,) = children
    assert child.name == "vscode" and child.foreground
    assert child.command == ("gosu", "1000:1000", *plan(_runtime_plan()).command)
    assert env["DONT_PROMPT_WSL_INSTALL"] == "1"


def test_vscode_archive_unpacks_to_opt_vscode_without_setuid_sandbox(tmp_path: Path) -> None:
    document = tomllib.loads(MATRIX.resolve(["vscode-ide", "node"]).render_lock())
    environment = parse_locked_environment(document)
    assert environment.component_id == "vscode"
    assert environment.recipe_id == "vscode-local-materialization"
    assert environment.recipe_version == "2"

    profile = surface_profile("vscode")
    assert profile.installation_path == VSCODE_INSTALLATION_PATH
    assert profile.archive_probes == ("code", "bin/code", "chrome-sandbox")
    assert profile.post_install == ()

    archive = tmp_path / "code-stable-x64.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for rel, mode, payload in (
            ("VSCode-linux-x64/code", 0o755, b"electron"),
            ("VSCode-linux-x64/bin/code", 0o755, b"#!/usr/bin/env sh\n"),
            ("VSCode-linux-x64/chrome-sandbox", 0o4755, b"sandbox"),
        ):
            info = tarfile.TarInfo(rel)
            info.size = len(payload)
            info.mode = mode
            bundle.addfile(info, io.BytesIO(payload))

    unpacked = normalize_archive_directory(archive, tmp_path / "unpacked")
    for probe in profile.archive_probes:
        assert (unpacked / probe).is_file()
    # Setuid bits from upstream tarballs are stripped during extraction.
    assert (unpacked / "chrome-sandbox").stat().st_mode & 0o7777 == 0o755

    template_path = tmp_path / "component-runtime-template.json"
    template_path.write_text(canonical_json(component_runtime_template("vscode")) + "\n", encoding="utf-8")
    spec = surface_materialization_spec(
        base_reference=environment.base_reference,
        base_identity="ubuntu-24.04@11",
        image="devcapsule-local-vscode:test",
        surface_root=unpacked,
        component_template=template_path,
        artifact=ArtifactSpec(environment.artifact.version, environment.artifact.url, environment.artifact.sha256),
        ancillary_files=(),
        npm_projects=(),
        native_package_directory=None,
        platform="linux-amd64",
        recipe_id=environment.recipe_id,
        recipe_version=environment.recipe_version,
        component_id="vscode",
    )
    contribution = spec.components[0]
    assert isinstance(contribution, ContributionComponent)
    assert contribution.name == "vscode"
    assert contribution.exports == ("/opt/vscode",)
    assert contribution.components == (DirectoryComponent(unpacked, "/opt/vscode"),)
    assert not any(
        isinstance(item, ExecComponent) and "4755" in " ".join(item.args)
        for item in spec.components
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("delivery-policy", "base-image"),
        ("acquisition-authorization", "other-download"),
        ("terms-url", "https://example.invalid/terms"),
    ],
)
def test_vscode_lock_rejects_tampered_acquisition_metadata(field: str, value: str) -> None:
    document = tomllib.loads(MATRIX.resolve(["vscode-ide"]).render_lock())
    document["components"]["vscode"][field] = value
    with pytest.raises(CliError):
        parse_locked_environment(document)


def test_vscode_discovery_queries_microsoft_stable_tarball_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_json(url: str) -> dict[str, object]:
        seen.append(url)
        return {
            "url": "https://vscode.download.prss.microsoft.com/dbazure/download/stable/abc/code-stable-x64-1.tar.gz",
            "productVersion": "1.144.0",
            "sha256hash": "a" * 64,
        }

    monkeypatch.setattr(discovery, "read_json", fake_json)
    channel = DEFINITION.discovery_channel()
    assert channel is not None
    report = channel.check("1.143.1", "linux-amd64")
    assert seen == ["https://update.code.visualstudio.com/api/update/linux-x64/stable/latest"]
    assert [candidate.version for candidate in report.candidates] == ["1.144.0"]
    assert channel.check("1.144.0", "linux-arm64").candidates == ()
    assert seen[-1] == "https://update.code.visualstudio.com/api/update/linux-arm64/stable/latest"

    for broken in (
        {"url": "http://vscode.download.prss.microsoft.com/code.tar.gz", "productVersion": "1.144.0", "sha256hash": "a" * 64},
        {"url": "https://vscode.download.prss.microsoft.com/code.deb", "productVersion": "1.144.0", "sha256hash": "a" * 64},
        {"url": "https://vscode.download.prss.microsoft.com/code.tar.gz", "productVersion": "1.144.0", "sha256hash": "short"},
        {"url": "https://vscode.download.prss.microsoft.com/code.tar.gz", "productVersion": "insiders", "sha256hash": "a" * 64},
    ):
        monkeypatch.setattr(discovery, "read_json", lambda _url, payload=broken: payload)
        with pytest.raises(CliError, match="unavailable"):
            channel.check("1.143.1", "linux-amd64")


def test_home_trust_accepts_vscode_channel_and_respects_checkout_denial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    config_home = tmp_path / "config-home"
    monkeypatch.setenv("DEVCAPSULE_CONFIG_HOME", str(config_home))
    project = tmp_path / "project"
    project.mkdir()
    assert cli.main(["project", "--path", str(project), "init", "--require", "python", "--creator", "mailto:owner@example.test"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "ide", "vscode"]) == 0
    out = capsys.readouterr().out
    assert "Your IDE for this checkout: vscode-ide (vscode)." in out

    matrix_lock = tomllib.loads(MATRIX.resolve(["vscode-ide", "python"]).render_lock())
    channel = channels_for(matrix_lock)["vscode"]
    assert known_channels()["vscode"] == channel
    assert (channel.vendor, channel.product, channel.origins, channel.terms_url, channel.authorization) == (
        "Microsoft",
        "Visual Studio Code",
        ("https://vscode.download.prss.microsoft.com",),
        VSCODE_TERMS_URL,
        VSCODE_AUTHORIZATION,
    )

    with pytest.raises(DecisionPending, match="--trust vscode"):
        prepare_launch(project, RunFlags(), interactive=False)

    assert cli.main(["home", "trust", "accept", BASE_CHANNEL, "--yes"]) == 0
    assert cli.main(["home", "trust", "accept", "vscode", "--yes"]) == 0
    assert HomeTrust.read(load_settings()).covers(channel)

    prepared = prepare_launch(project, RunFlags(), interactive=False)
    assert prepared.selected.lock["components"]["interactive-surface"] == "vscode"
    assert prepared.selected.resolution["authorization"][VSCODE_AUTHORIZATION] is True

    # Explicit checkout denial overrides home trust.
    assert cli.main(["project", "--path", str(project), "config", "authorize", VSCODE_AUTHORIZATION, "false"]) == 0
    _root, manifest = manifest_for(project)
    record = load_toml(checkout_record_paths(manifest, project)[0])
    reviews = {
        item.name: item
        for item in review_authorizations(manifest, prepared.selected.lock, record, HomeTrust.read(load_settings()))
    }
    assert reviews[VSCODE_AUTHORIZATION].trusted_channel is None
    assert reviews[VSCODE_AUTHORIZATION].recorded == "false"
    with pytest.raises(DecisionPending):
        prepare_launch(project, RunFlags(), interactive=False)


@pytest.mark.parametrize("broken", ["http", "credentials", "digest", "terms", "authorization", "missing-url"])
def test_tampered_vscode_lock_establishes_no_trust_channel(broken: str) -> None:
    lock = deepcopy(tomllib.loads(MATRIX.resolve(["vscode-ide"]).render_lock()))
    metadata = lock["components"]["vscode"]
    if broken == "http":
        metadata["url"] = "http://vscode.download.prss.microsoft.com/code.tar.gz"
    elif broken == "credentials":
        metadata["url"] = "https://user@vscode.download.prss.microsoft.com/code.tar.gz"
    elif broken == "digest":
        metadata["sha256"] = "not-a-sha256"
    elif broken == "terms":
        metadata["terms-url"] = "https://example.invalid/license"
    elif broken == "authorization":
        metadata["acquisition-authorization"] = "other-download"
    else:
        del metadata["url"]
    assert "vscode" not in channels_for(lock)


def test_both_vscode_ide_and_frontend_ide_provider_selection_paths_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEVCAPSULE_CONFIG_HOME", str(tmp_path / "home"))
    assert MATRIX.canonical_name("codium") == "frontend-ide"
    assert MATRIX.canonical_name("vscode") == "vscode-ide"
    assert cli.main(["home", "trust", "accept", BASE_CHANNEL, "--yes"]) == 0
    assert cli.main(["home", "trust", "accept", "vscode", "--yes"]) == 0

    project = tmp_path / "web"
    project.mkdir()
    assert cli.main(["project", "--path", str(project), "init", "--require", "node", "--creator", "mailto:owner@example.test"]) == 0

    # Path 1: frontend-ide defaults to codium, can switch to vscode via `config use` or `run --use`, and switch back.
    assert cli.main(["project", "--path", str(project), "config", "ide", "frontend-ide"]) == 0
    assert prepare_launch(project, RunFlags(), interactive=False).selected.lock["components"]["interactive-surface"] == "codium"

    one_shot = prepare_launch(project, RunFlags(providers=(("frontend-ide", "vscode"),)), interactive=False)
    assert one_shot.selected.lock["components"]["interactive-surface"] == "vscode"

    assert cli.main(["project", "--path", str(project), "config", "use", "frontend-ide", "vscode"]) == 0
    chosen = prepare_launch(project, RunFlags(), interactive=False)
    assert chosen.selected.lock["components"]["interactive-surface"] == "vscode"
    assert set(chosen.selected.lock["components"]) == {"interactive-surface", "vscode"}

    # Path 2: switching from frontend-ide (with vscode provider) to standalone vscode-ide works cleanly.
    assert cli.main(["project", "--path", str(project), "config", "ide", "vscode-ide"]) == 0
    standalone = prepare_launch(project, RunFlags(), interactive=False)
    assert standalone.selected.lock["components"]["interactive-surface"] == "vscode"
    assert set(standalone.selected.lock["components"]) == {"interactive-surface", "vscode"}
    capsys.readouterr()
    assert cli.main(["project", "--path", str(project), "config", "check"]) == 0
    assert "Nothing is pending" in capsys.readouterr().out

    # Project-level recommendation for frontend-ide = vscode also works cleanly.
    assert cli.main(["project", "--path", str(project), "config", "recommend", "ide", "frontend-ide"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "recommend", "frontend-ide", "vscode"]) == 0
    assert cli.main(["project", "--path", str(project), "config", "ide", "frontend-ide"]) == 0
    capsys.readouterr()
    assert cli.main(["project", "--path", str(project), "config", "ide", "frontend-ide"]) == 0
    assert "frontend-ide (vscode)" in capsys.readouterr().out
    assert settings_path().is_file()
