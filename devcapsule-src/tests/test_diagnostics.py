from __future__ import annotations

import gzip
import io
import json
import os
from pathlib import Path
import stat
import tarfile
import textwrap
import tomllib
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

from devcapsule import cli, logs
from devcapsule.configuration.docker_arguments import arguments_path, update_environment
from devcapsule.configuration.file_formats import canonical_digest
from devcapsule.configuration.storage import find_checkout_record
from devcapsule.diagnostics import (
    DiagnosticsError,
    diagnose_project,
    inspect_container,
    select_session_directory,
    summarize_diagnosis,
)
from devcapsule.launch.session_logs import session_logs_root


def _init_project(project: Path) -> dict[str, Any]:
    target = project / ".devcapsule"
    target.mkdir(parents=True, exist_ok=True)
    manifest_text = "\n".join(
        [
            "devcapsule-schema-version = 1",
            "",
            "[capabilities]",
            'need = ["python", "python-ide"]',
            "",
            "[project]",
            f'name = "{project.name}"',
            f'slug = "{project.name.lower()}"',
            'creator = "mailto:dev@example.test"',
            'mount = "/workspace/project"',
            "",
        ]
    )
    (target / "devcapsule.toml").write_text(manifest_text, encoding="utf-8")
    manifest = tomllib.loads(manifest_text)
    lock_text = "\n".join(
        [
            "devcapsule-lock-format-version = 1",
            'resolution-matrix-version = "dogfood-v1"',
            f'manifest-digest = "{canonical_digest(manifest)}"',
            'platform = "linux-amd64"',
            "",
            "[image]",
            'reference = "local/pycharm:dogfood"',
            "",
            "[components]",
            'interactive-surface = "pycharm"',
            "",
        ]
    )
    (target / "devcapsule.linux-amd64.lock").write_text(lock_text, encoding="utf-8")
    return manifest


def _write_fake_docker(bin_dir: Path, script_body: str) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    docker_bin = bin_dir / "docker"
    docker_bin.write_text("#!/bin/sh\n" + script_body, encoding="utf-8")
    docker_bin.chmod(0o755)
    return docker_bin


def test_select_session_directory_handles_validation_active_and_crashed_sessions(
    tmp_path: Path,
) -> None:
    logs_root = tmp_path / "logs"
    logs_root.mkdir()

    for bad in ("../escape", "nested/id", ".dotstart", ""):
        with pytest.raises(DiagnosticsError):
            select_session_directory(logs_root, session_id=bad)

    with pytest.raises(DiagnosticsError, match="No session logs found"):
        select_session_directory(logs_root)

    s1 = logs_root / "20261027-100000-aaaa"
    s1.mkdir()
    (s1 / "session.json").write_text(
        json.dumps({"session": s1.name, "container": "dead-capsule", "started-at": "2026-10-27T10:00:00Z"}),
        encoding="utf-8",
    )
    s2 = logs_root / "20261027-110000-bbbb"
    s2.mkdir()
    (s2 / "session.json").write_text(
        json.dumps(
            {
                "session": s2.name,
                "container": "ended-capsule",
                "started-at": "2026-10-27T11:00:00Z",
                "ended-at": "2026-10-27T11:10:00Z",
                "exit-code": 0,
            }
        ),
        encoding="utf-8",
    )

    # s1 has no ended-at, yet its container is gone while s2 ended more recently -> pick s2.
    chosen, mode = select_session_directory(
        logs_root,
        is_container_running=lambda _name: False,
    )
    assert chosen == s2
    assert mode == "latest-ended"

    # If s1's container is actually still running concurrently, prefer s1 as active!
    chosen_live, mode_live = select_session_directory(
        logs_root,
        is_container_running=lambda name: name == "dead-capsule",
    )
    assert chosen_live == s1
    assert mode_live == "active"

    with pytest.raises(DiagnosticsError, match="Available sessions"):
        select_session_directory(logs_root, session_id="20261027-120000-missing")


def test_inspect_container_strips_env_values_and_handles_removed_or_hung_docker(
    tmp_path: Path,
) -> None:
    payload = [
        {
            "Id": "abc123def456",
            "Image": "sha256:1111",
            "State": {
                "Status": "running",
                "Running": True,
                "Paused": False,
                "Restarting": False,
                "OOMKilled": True,
                "Dead": False,
                "Pid": 4321,
                "ExitCode": 0,
                "Error": "",
                "StartedAt": "2026-10-27T12:00:00Z",
                "FinishedAt": "0001-01-01T00:00:00Z",
            },
            "HostConfig": {
                "Memory": 4294967296,
                "MemorySwap": 4294967296,
                "NanoCpus": 2000000000,
                "PidsLimit": 4096,
                "ShmSize": 67108864,
                "ReadonlyRootfs": True,
                "NetworkMode": "bridge",
            },
            "Config": {
                "Env": [
                    "OPENAI_API_KEY=sk-never-leak-this-secret-value",
                    "CUSTOM_INLINE=top-secret-inline",
                    "DISPLAY=:99",
                ]
            },
            "NetworkSettings": {
                "Ports": {
                    "6080/tcp": [{"HostIp": "127.0.0.1", "HostPort": "46080"}],
                    "6081/tcp": [{"HostIp": "127.0.0.1", "HostPort": "46081"}],
                }
            },
        }
    ]
    inspect_json = tmp_path / "inspect.json"
    inspect_json.write_text(json.dumps(payload), encoding="utf-8")

    bin_dir = tmp_path / "bin"
    _write_fake_docker(
        bin_dir,
        textwrap.dedent(
            f"""\
            if [ "$4" = "live-c" ]; then
              cat "{inspect_json}"
              exit 0
            fi
            if [ "$4" = "gone-c" ]; then
              echo "Error: No such container: gone-c" >&2
              exit 1
            fi
            sleep 2
            """
        ),
    )
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}

    live = inspect_container("live-c", env=env, timeout=1.0)
    assert live["available"] is True
    assert live["oom_killed"] is True
    assert live["published_ports"]["6080/tcp"] == [{"host_ip": "127.0.0.1", "host_port": 46080}]
    assert live["environment_variable_names"] == ["CUSTOM_INLINE", "DISPLAY", "OPENAI_API_KEY"]
    serialized = json.dumps(live)
    assert "sk-never-leak-this-secret-value" not in serialized
    assert "top-secret-inline" not in serialized

    gone = inspect_container("gone-c", env=env, timeout=1.0)
    assert gone["available"] is False
    assert gone["container_removed"] is True

    hung = inspect_container("hung-c", env=env, timeout=0.15)
    assert hung["available"] is False
    assert hung["timed_out"] is True


def test_summarize_diagnosis_never_treats_http_200_or_socket_accept_as_healthy() -> None:
    degraded = summarize_diagnosis(
        session_manifest_doc={"session": "s1"},
        docker_inspect={"available": True, "running": True, "oom_killed": False},
        runtime_probe={
            "available": True,
            "cgroup": {"memory": {"events": {"oom_kill": 0}}},
            "processes": {
                "stopped": [{"pid": 20, "name": "Xvnc", "role": "xvnc"}],
                "zombies": [{"pid": 99, "name": "defunct", "role": "other"}],
            },
            "probes": {
                "rfb_unix": {"healthy": False, "accepted": True, "status": "greeting-timeout"},
                "display_http": {"healthy": True, "status": "ok"},
                "display_websocket_rfb": {"healthy": False, "status": "rfb-greeting-timeout"},
                "console_http": {"healthy": True, "status": "ok"},
            },
        },
        host_probes={
            "available": True,
            "probes": {
                "display_host_http": {"healthy": False, "port": 46080, "status": "connect-error"},
                "console_host_http": {"healthy": True, "status": "ok"},
            },
        },
    )
    assert degraded["state"] == "degraded"
    joined = "\n".join(degraded["issues"])
    assert "stopped (state T)" in joined
    assert "zombie" in joined
    assert "accepted connection without RFB greeting" in joined
    assert "websockify HTTP (/vnc.html) answered 200 while WebSocket-to-RFB bridge failed" in joined
    assert "host loopback port 46080 failed" in joined

    infra_exit = summarize_diagnosis(
        session_manifest_doc={"session": "s2", "ended-at": "2026-10-27T12:00:00Z", "exit-code": 70},
        docker_inspect={"available": False, "container_removed": True},
        runtime_probe={"available": False, "unavailable_reason": "container removed"},
        host_probes={"available": False, "unavailable_reason": "container removed"},
    )
    assert infra_exit["state"] == "post-mortem-issues"
    assert any("70" in item for item in infra_exit["issues"])

    ctrl_c_exit = summarize_diagnosis(
        session_manifest_doc={"session": "s3", "ended-at": "2026-10-27T12:00:00Z", "exit-code": 130},
        docker_inspect={"available": False, "container_removed": True},
        runtime_probe={"available": False, "unavailable_reason": "container removed"},
        host_probes={"available": False, "unavailable_reason": "container removed"},
    )
    assert ctrl_c_exit["state"] == "post-mortem"
    assert ctrl_c_exit["issues"] == []


def test_project_diagnose_export_redacts_logs_gz_excludes_ide_logs_by_default_and_refuses_symlinks(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "sample-proj"
    manifest = _init_project(project)
    assert cli.main(["project", "--path", str(project), "checkout", "register", "default"]) == 0
    capsys.readouterr()
    record_path = find_checkout_record(manifest, project)
    assert record_path is not None
    update_environment(arguments_path(record_path), "CUSTOM_SAVED_SECRET", "saved_docker_secret_val_999")

    # Configure fake docker returning "No such container" so post-mortem path runs deterministically.
    bin_dir = tmp_path / "bin"
    _write_fake_docker(bin_dir, 'echo "Error: No such container: $4" >&2\nexit 1\n')

    jetbrains_logs = tmp_path / "ide-slots" / "jetbrains-log"
    jetbrains_logs.mkdir(parents=True)
    (jetbrains_logs / "idea.log").write_text(
        "2026-10-27 INFO open url http://127.0.0.1:6080/vnc.html?token=ide_url_token_1122334455667788\n",
        encoding="utf-8",
    )
    (jetbrains_logs / "symlink-idea.log").symlink_to("/etc/hosts")

    eclipse_meta = tmp_path / "ide-slots" / "eclipse" / ".metadata"
    (eclipse_meta / ".plugins").mkdir(parents=True)
    (eclipse_meta / ".log").write_text("!ENTRY eclipse log CUSTOM_SAVED_SECRET=saved_docker_secret_val_999\n", encoding="utf-8")
    (eclipse_meta / ".bak_0.log").write_text("!ENTRY rotated eclipse log\n", encoding="utf-8")
    (eclipse_meta / ".plugins" / "workspace-source-cache.txt").write_text(
        "UNRELATED_WORKSPACE_PLUGIN_STATE_MUST_NEVER_BE_EXPORTED\n",
        encoding="utf-8",
    )

    logs_dir = session_logs_root(project) / "20261027-123000-cafe"
    logs_dir.mkdir(parents=True)
    session_doc = {
        "schema-version": 1,
        "session": logs_dir.name,
        "started-at": "2026-10-27T12:30:00Z",
        "ended-at": "2026-10-27T12:35:00Z",
        "exit-code": 0,
        "container": "devcapsule-sample-proj",
        "network-mode": "bridge",
        "display": {"transport": "contained", "host-port": 46080, "container-port": 6080},
        "console": {"enabled": True, "host-port": 46081, "container-port": 6081},
        "ide-logs": [
            {
                "slot": "pycharm/log",
                "family": "jetbrains",
                "host-path": str(jetbrains_logs),
                "container-path": "/home/devcapsule/.cache/JetBrains/PyCharm/log",
            },
            {
                "slot": "eclipse/workspace",
                "family": "eclipse",
                "host-path": str(eclipse_meta),
                "container-path": "/home/devcapsule/eclipse-workspace/.metadata",
            },
        ],
    }
    (logs_dir / "session.json").write_text(json.dumps(session_doc, indent=2), encoding="utf-8")
    (logs_dir / "devcapsule-novnc.log").write_text(
        "2026-10-27T12:30:01Z GET /vnc.html?token=deadbeefcafe1234567890abcdef1234\n"
        "2026-10-27T12:30:02Z redirect token%3Dencoded_secret_token_99887766\n"
        "2026-10-27T12:30:03Z Cookie: devcapsule-console-token=console_cookie_secret_554433\n"
        "2026-10-27T12:30:04Z Authorization: Bearer bearer_secret_value_776655\n",
        encoding="utf-8",
    )
    with gzip.open(logs_dir / "devcapsule-launcher.log.1.gz", "wb") as gz_handle:
        gz_handle.write(
            (
                "2026-10-27T12:30:00Z docker run --env CUSTOM_SAVED_SECRET=saved_docker_secret_val_999\n"
                "2026-10-27T12:30:01Z OPENAI_API_KEY=sk-proj-secret-value-123456789\n"
            ).encode("utf-8")
        )
    (logs_dir / "devcapsule-corrupt.log.2.gz").write_bytes(b"\x1f\x8b\x08corrupt-not-valid-gzip")
    (logs_dir / "evil-symlink.log").symlink_to("/etc/hosts")

    # --include-ide-logs without --export must fail clearly.
    rc_bad = cli.main(["project", "--path", str(project), "diagnose", "--include-ide-logs"])
    assert rc_bad == 2
    assert "--include-ide-logs requires --export" in capsys.readouterr().err

    # Exporting through a symlink destination must be refused.
    symlink_export = tmp_path / "symlink-bundle.tar.gz"
    symlink_export.symlink_to(tmp_path / "target.tar.gz")
    with patch.dict(os.environ, {"PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}):
        rc_sym = cli.main(
            ["project", "--path", str(project), "diagnose", "--export", str(symlink_export)]
        )
    assert rc_sym == 2
    assert "symlink" in capsys.readouterr().err.lower()

    default_bundle = tmp_path / "default-export.tar.gz"
    with patch.dict(os.environ, {"PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}):
        rc_ok = cli.main(
            ["project", "--path", str(project), "diagnose", "--json", "--export", str(default_bundle)]
        )
    assert rc_ok == 0
    out_json = json.loads(capsys.readouterr().out)
    assert out_json["schema-version"] == 1
    assert out_json["browser_evidence"]["collected"] is False
    assert out_json["browser_evidence"]["mode"] == "manual-devtools"
    assert out_json["ide_native_logs"]["included_in_export"] is False
    assert len(out_json["ide_native_logs"]["entries"]) == 2

    saved_snap = Path(out_json["saved_snapshot_path"])
    assert stat.S_IMODE(saved_snap.stat().st_mode) == 0o600
    assert stat.S_IMODE(default_bundle.stat().st_mode) == 0o600

    forbidden_secrets = (
        "deadbeefcafe1234567890abcdef1234",
        "encoded_secret_token_99887766",
        "console_cookie_secret_554433",
        "bearer_secret_value_776655",
        "saved_docker_secret_val_999",
        "sk-proj-secret-value-123456789",
        "ide_url_token_1122334455667788",
    )

    with tarfile.open(default_bundle, "r:gz") as tar:
        names = tar.getnames()
        assert not any("/ide-logs/" in name for name in names)
        assert not any("evil-symlink" in name for name in names)
        for member in tar.getmembers():
            extracted = tar.extractfile(member)
            assert extracted is not None
            raw = extracted.read()
            text = (
                gzip.decompress(raw).decode("utf-8")
                if member.name.endswith(".gz")
                else raw.decode("utf-8")
            )
            for secret in forbidden_secrets:
                assert secret not in text, f"secret {secret!r} leaked in {member.name}"
            if member.name.endswith("/snapshot.json"):
                archived_snap = json.loads(text)
                skipped_reasons = {item["reason"] for item in archived_snap["export"]["skipped_files"]}
                assert "symlink refused" in skipped_reasons
                assert any("read failed" in reason for reason in skipped_reasons)

    # Now opt in with --include-ide-logs: JetBrains + Eclipse .log/.bak_0.log included (redacted),
    # Eclipse .plugins/ workspace files and symlinks STILL excluded!
    opt_in_bundle = tmp_path / "with-ide-logs.tar.gz"
    with patch.dict(os.environ, {"PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}):
        rc_ide = cli.main(
            [
                "project",
                "--path",
                str(project),
                "diagnose",
                "--export",
                str(opt_in_bundle),
                "--include-ide-logs",
            ]
        )
    assert rc_ide == 0
    human_out = capsys.readouterr().out
    assert "Verdict: post-mortem" in human_out
    assert "Export bundle:" in human_out

    with tarfile.open(opt_in_bundle, "r:gz") as tar:
        ide_members = [name for name in tar.getnames() if "/ide-logs/" in name]
        assert any(name.endswith("/idea.log") for name in ide_members)
        assert any(name.endswith("/.log") for name in ide_members)
        assert any(name.endswith("/.bak_0.log") for name in ide_members)
        assert not any("workspace-source-cache" in name for name in ide_members)
        assert not any("symlink-idea" in name for name in ide_members)
        for member in tar.getmembers():
            extracted = tar.extractfile(member)
            assert extracted is not None
            raw = extracted.read()
            text = (
                gzip.decompress(raw).decode("utf-8")
                if member.name.endswith(".gz")
                else raw.decode("utf-8")
            )
            for secret in forbidden_secrets:
                assert secret not in text, f"secret {secret!r} leaked in {member.name}"


def test_diagnose_project_in_capsule_mode_runs_in_process_and_guards_other_sessions(
    tmp_path: Path,
) -> None:
    capsule_logs = tmp_path / "var-log-devcapsule"
    capsule_logs.mkdir()
    (capsule_logs / "session.json").write_text(
        json.dumps({"session": "20261027-124000-live", "started-at": "2026-10-27T12:40:00Z"}),
        encoding="utf-8",
    )
    fake_context = SimpleNamespace(
        document={
            "project": {"creator": "mailto:dev@example.test", "slug": "capsule-proj"},
            "launcher-root": "/host/path/capsule-proj",
            "runtime-root": "/workspace/capsule-proj",
        },
        checkout_name="default",
        launcher_command=lambda args: f"devcapsule project --path /host/path/capsule-proj {' '.join(args)}",
    )
    fake_probe = {
        "schema_version": 1,
        "cgroup": {"available": False},
        "processes": {"available": True, "total_processes": 3, "components": {}, "novnc_workers": [], "zombies": [], "stopped": []},
        "sockets": {},
        "probes": {
            "rfb_unix": {"healthy": True, "status": "ok"},
            "display_http": {"healthy": True, "status": "ok"},
            "display_websocket_rfb": {"healthy": True, "status": "ok"},
            "console_http": {"healthy": True, "status": "ok"},
        },
    }

    with (
        patch("devcapsule.diagnostics.runtime_configuration.for_project", return_value=fake_context),
        patch("devcapsule.diagnostics.collect_runtime_probe", return_value=dict(fake_probe)),
    ):
        with pytest.raises(DiagnosticsError, match="inspect other sessions from the host"):
            diagnose_project(
                tmp_path,
                session_id="20261027-090000-older",
                environ={logs.DIRECTORY_ENV: str(capsule_logs)},
            )

        snap = diagnose_project(
            tmp_path,
            environ={logs.DIRECTORY_ENV: str(capsule_logs)},
        )
    assert snap["context"] == "in-capsule"
    assert snap["session"]["id"] == "20261027-124000-live"
    assert snap["summary"]["state"] == "healthy"
