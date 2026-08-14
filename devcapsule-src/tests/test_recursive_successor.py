from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Callable

import pytest

from devcapsule.recursive_successor import (
    EXPECTED_PLAN,
    MILESTONE_MANIFEST,
    OWNER_MARKER,
    RecursiveSuccessorError,
    inspect_successor,
)
from devcapsule.recursive_successor_plan import ExpectedSuccessorPlan

from tests.test_recursive_successor_plan import (
    IMAGE_IDENTITY,
    IMAGE_LABELS,
    IMAGE_REFERENCE,
    RUNTIME_PLAN_DESTINATION,
    RUNTIME_PLAN_DIGEST,
    docker_args,
    matching_inspection,
)


RUN_ID = "b2093d85912fa34ac1324e1da26a9dcd"
CONTAINER_ID = "7e" * 32
SOURCE_REVISION = "600c085228884112e8860c3e6cdc4fb7b6674c0b"


def owned_plan() -> ExpectedSuccessorPlan:
    args = [
        *docker_args(),
        "--label",
        f"devcapsule.e2e.run-id={RUN_ID}",
        "--label",
        f"devcapsule.e2e.source-revision={SOURCE_REVISION}",
    ]
    return ExpectedSuccessorPlan.from_docker_args(
        args,
        image_reference=IMAGE_REFERENCE,
        image_identity=IMAGE_IDENTITY,
        image_labels=IMAGE_LABELS,
        runtime_plan_destination=RUNTIME_PLAN_DESTINATION,
        runtime_plan_digest=RUNTIME_PLAN_DIGEST,
    )


def probe_evidence(**overrides: str) -> dict[str, str]:
    evidence = {
        "claude": "2.1.227 (Claude Code)",
        "codex": "codex-cli 0.145.0",
        "node": "v22.23.1",
        "java": "javac 25.0.4",
        "maven": "Apache Maven 3.9.16",
        "java_home": "/opt/java/current",
        "maven_home": "/opt/maven/current",
        "runtime_plan_sha256": RUNTIME_PLAN_DIGEST,
        "runtime_plan_writable": "no",
    }
    evidence.update(overrides)
    return evidence


@pytest.fixture
def retained_run(tmp_path: Path) -> Path:
    plan = owned_plan()
    root = tmp_path / RUN_ID
    root.mkdir(parents=True)
    (root / OWNER_MARKER).write_text(
        json.dumps({"schema_version": 1, "run_id": RUN_ID}), encoding="utf-8"
    )
    (root / MILESTONE_MANIFEST).write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": RUN_ID,
                "state": "stage-6-running",
                "launch": {
                    "source_revision": SOURCE_REVISION,
                    "container_id": CONTAINER_ID,
                    "container_name": plan.name,
                    "image_id": IMAGE_IDENTITY,
                    "expected_plan_digest": plan.digest(),
                    "role": "successor",
                },
            }
        ),
        encoding="utf-8",
    )
    (root / EXPECTED_PLAN).write_text(plan.to_json(show_host_paths=True) + "\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def fake_docker(monkeypatch: pytest.MonkeyPatch) -> Callable[..., list[list[str]]]:
    """Record Docker invocations and answer them from test-owned evidence."""

    def install(
        inspection: dict[str, Any] | None = None,
        probe: dict[str, str] | None = None,
        probe_returncode: int = 0,
    ) -> list[list[str]]:
        calls: list[list[str]] = []

        def fake_run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if command[:2] == ["docker", "inspect"]:
                selected = matching_inspection(owned_plan()) if inspection is None else inspection
                return subprocess.CompletedProcess(command, 0, json.dumps([selected]), "")
            if command[:2] == ["docker", "exec"]:
                return subprocess.CompletedProcess(
                    command,
                    probe_returncode,
                    json.dumps(probe_evidence() if probe is None else probe),
                    "",
                )
            raise AssertionError(f"unexpected Docker command: {command}")

        monkeypatch.setattr(subprocess, "run", fake_run)
        return calls

    return install


def test_inspection_records_every_hardened_check(
    retained_run: Path,
    fake_docker: Any,
) -> None:
    calls = fake_docker()

    result = inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)

    assert result.state == "inspection-passed"
    assert result.container_id == CONTAINER_ID
    assert result.checks["mounts"] == "pass"
    assert result.checks["security_settings"] == "pass"
    assert result.checks["formation_identity"] == "pass"
    assert result.checks["runtime_plan"] == "pass"
    assert result.checks["codex"] == "codex-cli 0.145.0"
    assert [call[1] for call in calls] == ["inspect", "exec"]
    assert CONTAINER_ID in calls[0]


def test_inspection_evidence_never_records_daemon_side_sources(
    retained_run: Path,
    fake_docker: Any,
) -> None:
    fake_docker()

    inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)

    manifest = (retained_run / RUN_ID / MILESTONE_MANIFEST).read_text(encoding="utf-8")
    assert "/host/" not in manifest
    assert manifest.count("pass") > 1


def test_retained_plan_tampering_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker()
    plan_path = retained_run / RUN_ID / EXPECTED_PLAN
    tampered = json.loads(plan_path.read_text(encoding="utf-8"))
    tampered["privileged"] = True
    plan_path.write_text(json.dumps(tampered), encoding="utf-8")

    with pytest.raises(RecursiveSuccessorError, match="digest recorded at launch"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_absent_retained_plan_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker()
    (retained_run / RUN_ID / EXPECTED_PLAN).unlink()

    with pytest.raises(RecursiveSuccessorError, match="absent or malformed"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_manifest_without_a_plan_digest_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker()
    manifest_path = retained_run / RUN_ID / MILESTONE_MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["launch"]["expected_plan_digest"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RecursiveSuccessorError, match="incomplete successor launch evidence"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_manifest_disagreeing_with_the_retained_plan_is_rejected(
    retained_run: Path,
    fake_docker: Any,
) -> None:
    fake_docker()
    manifest_path = retained_run / RUN_ID / MILESTONE_MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["launch"]["image_id"] = "sha256:" + "ab" * 32
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RecursiveSuccessorError, match="disagree on identity"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_substituted_runtime_plan_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker(probe=probe_evidence(runtime_plan_sha256="b" * 64))

    with pytest.raises(RecursiveSuccessorError, match="runtime plan does not match the digest"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_writable_runtime_plan_mount_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker(probe=probe_evidence(runtime_plan_writable="yes"))

    with pytest.raises(RecursiveSuccessorError, match="not mounted read-only"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_unplanned_mount_fails_the_independent_inspection(
    retained_run: Path,
    fake_docker: Any,
) -> None:
    inspection = matching_inspection(owned_plan())
    inspection["Mounts"].append(
        {
            "Type": "bind",
            "Source": "/host/home/costin/.ssh",
            "Destination": "/home/devcapsule/.ssh",
            "RW": True,
        }
    )
    fake_docker(inspection=inspection)

    with pytest.raises(RecursiveSuccessorError, match="unplanned mounts") as error:
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)

    assert "/host/home/costin/.ssh" not in str(error.value)


def test_malformed_docker_inspection_is_rejected(
    retained_run: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, "not json", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RecursiveSuccessorError, match="malformed successor inspection"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_ambiguous_docker_inspection_is_rejected(
    retained_run: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, json.dumps([{}, {}]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RecursiveSuccessorError, match="ambiguous successor inspection"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)


def test_failing_readiness_probe_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker(probe_returncode=1)

    with pytest.raises(RecursiveSuccessorError, match="readiness probe failed"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run, readiness_timeout=0.0)


def test_ownership_marker_mismatch_is_rejected(retained_run: Path, fake_docker: Any) -> None:
    fake_docker()
    (retained_run / RUN_ID / OWNER_MARKER).write_text(
        json.dumps({"schema_version": 1, "run_id": "0" * 32}), encoding="utf-8"
    )

    with pytest.raises(RecursiveSuccessorError, match="ownership marker"):
        inspect_successor(RUN_ID, environ={}, workspace_root=retained_run)
