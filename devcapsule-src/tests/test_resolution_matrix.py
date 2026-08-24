"""Focused tests for the embedded resolution matrix."""

from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from devcapsule.configuration_nodes import build_node_registry
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    canonical_digest,
    lock_for,
)
from devcapsule.resolution_matrix import (
    MATRIX_VERSION,
    generate_platform_lock,
    normalize_capability_need,
    supported_capabilities,
)


def parse(content: str) -> dict:
    return tomllib.loads(content)


def test_minimal_need_generates_a_complete_pycharm_lock() -> None:
    generated = generate_platform_lock(["python", "python-ide"], "linux-amd64")
    lock = parse(generated.content)

    assert lock["devcapsule-lock-format-version"] == 1
    assert lock["resolution-matrix-version"] == MATRIX_VERSION
    assert lock["platform"] == "linux-amd64"
    assert lock["base"]["reference"].startswith(
        "docker.io/mycodespaceai/devcapsule-base@sha256:"
    )
    assert lock["base"]["build-mnemonic"] == "v026"
    assert lock["components"]["interactive-surface"] == "pycharm"
    assert lock["components"]["pycharm"]["version"] == "2026.2.0.1"
    assert lock["materialization"]["recipe"] == "jetbrains-local-materialization"
    assert set(lock["components"]) == {"interactive-surface", "pycharm"}
    # The scoped digest covers exactly the derivation input; the retired
    # whole-manifest digest is never written.
    assert lock["capabilities-digest"] == canonical_digest(
        {"need": ["python", "python-ide"]}
    )
    assert "manifest-digest" not in lock


def test_agent_and_database_capabilities_select_their_pinned_components() -> None:
    generated = generate_platform_lock(
        ["python", "python-ide", "codex-agent", "claude-code-agent", "postgresql-client"],
        "linux-amd64",
    )
    lock = parse(generated.content)

    codex = lock["components"]["codex"]
    assert codex["version"] == "0.145.0"
    assert codex["artifacts"]["linux-amd64"]["sha256"] == (
        "11239480f8e3efd1430f23bbe91c1a397856b8bbe6185ccbaee2382d25e03df2"
    )

    claude = lock["components"]["claude-code"]
    assert claude["acquisition-authorization"] == "claude-code-download"
    assert claude["terms-url"] == "https://www.anthropic.com/legal/commercial-terms"
    assert claude["artifacts"]["linux-amd64"]["sha256"] == (
        "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
    )

    postgres = lock["components"]["postgresql-client"]
    assert postgres == {"version": "16", "delivery-policy": "base-image", "license": "PostgreSQL"}


def test_unknown_capability_lists_the_supported_vocabulary() -> None:
    with pytest.raises(ProjectConfigurationError) as failure:
        generate_platform_lock(["python-ide", "quantum-debugger"], "linux-amd64")
    assert "'quantum-debugger'" in str(failure.value)
    for name in supported_capabilities():
        assert name in str(failure.value)


def test_missing_interactive_capability_is_explained() -> None:
    with pytest.raises(ProjectConfigurationError, match="python-ide"):
        generate_platform_lock(["python"], "linux-amd64")


def test_unsupported_platform_is_explained() -> None:
    with pytest.raises(ProjectConfigurationError, match="linux-amd64"):
        generate_platform_lock(["python-ide"], "windows-arm64")


def test_need_is_normalized_to_a_sorted_unique_set() -> None:
    assert normalize_capability_need(["python-ide", "python", "python-ide"]) == (
        "python",
        "python-ide",
    )
    duplicated = generate_platform_lock(["python-ide", "python", "python"], "linux-amd64")
    unique = generate_platform_lock(["python", "python-ide"], "linux-amd64")
    assert duplicated.content == unique.content


def test_malformed_need_values_are_rejected() -> None:
    with pytest.raises(ProjectConfigurationError, match="array"):
        normalize_capability_need("python-ide")
    with pytest.raises(ProjectConfigurationError, match="non-empty strings"):
        normalize_capability_need(["python-ide", 7])


def test_generation_is_deterministic() -> None:
    first = generate_platform_lock(["python-ide", "codex-agent"], "linux-amd64")
    second = generate_platform_lock(["python-ide", "codex-agent"], "linux-amd64")
    assert first.content == second.content


def test_generated_lock_passes_the_real_loaders(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / ".devcapsule").mkdir(parents=True)
    need = ["python", "python-ide", "claude-code-agent", "codex-agent"]
    manifest = {
        "devcapsule-schema-version": 1,
        "capabilities": {"need": need},
        "project": {
            "name": "Example",
            "slug": "example",
            "creator": "https://github.com/example",
            "mount": "/workspace/example",
        },
    }
    generated = generate_platform_lock(need, "linux-amd64")
    (project / ".devcapsule" / "devcapsule.linux-amd64.lock").write_text(
        generated.content, encoding="utf-8"
    )

    lock_path, lock = lock_for(project, manifest)
    assert lock_path.name == "devcapsule.linux-amd64.lock"

    registry = build_node_registry(manifest, lock)
    assert registry.node("base-image").required is True
    assert registry.node("claude-code-download").family == "authorize"
    assert registry.node("codex/openai-api-key").providers == ("host-environment",)
    assert registry.node("pycharm/system").family == "bind"
