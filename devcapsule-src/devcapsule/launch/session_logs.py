"""The host side of session logs: where a checkout keeps them, what a session records.

The launcher creates one directory per session under the checkout's state
namespace, the same ``$XDG_STATE_HOME/devcapsule/projects/by-path/<id>``
that holds the IDE's own log slot, binds it into the capsule at
:data:`SESSION_LOG_DESTINATION`, and writes its own log and the session
manifest there. The capsule side is ``devcapsule.container_runtime``; the
file naming and levels are ``devcapsule.logs``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any, Mapping

from devcapsule import logs
from devcapsule.build_info import BuildInfoError, current_build_info
from devcapsule.project import project_namespace

SESSION_LOG_DESTINATION = "/var/log/devcapsule"
"""The session's log directory inside the capsule; ``$DEVCAPSULE_LOG_DIR`` names it too."""
LAUNCHER_LOG_COMPONENT = "launcher"
LOGS_DIRECTORY_NAME = "logs"


def session_logs_root(project_path: str | Path, environ: Mapping[str, str] | None = None) -> Path:
    """``<state namespace>/logs`` for the checkout at ``project_path``, not created."""

    env = os.environ if environ is None else environ
    home = Path(env.get("HOME", "~")).expanduser()
    state_home = Path(env.get("XDG_STATE_HOME") or home / ".local" / "state").expanduser()
    return state_home / "devcapsule" / "projects" / "by-path" / project_namespace(project_path) / LOGS_DIRECTORY_NAME


def session_manifest(
    *,
    session_id: str,
    project: Path,
    project_mount: str,
    image: str,
    container_name: str,
    component: str,
    budget_bytes: int = logs.DEFAULT_BUDGET_BYTES,
    started_at: float | None = None,
) -> dict[str, Any]:
    """What ties a session's logs to their inputs: identities and versions."""

    try:
        build = current_build_info()
        launcher = {"version": build.version, "source": build.source_revision, "mnemonic": build.build_mnemonic}
    except BuildInfoError as error:
        launcher = {"version": "unknown", "source": "", "mnemonic": "unknown", "error": str(error)}
    return {
        "format": 1,
        "session": session_id,
        "started-at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if started_at is None else started_at)),
        "launcher": launcher,
        "image": image,
        "container": container_name,
        "project": {"path": str(project), "mount": project_mount},
        "component": component,
        "logs": {
            "directory": SESSION_LOG_DESTINATION,
            "pattern": f"{logs.LOG_FILE_PREFIX}<component>{logs.LOG_FILE_SUFFIX}",
            "budget-bytes": budget_bytes,
            "segment-bytes": logs.segment_bytes_for(budget_bytes),
            "rotations": logs.ROTATIONS,
        },
    }


def write_session_manifest(directory: Path, manifest: Mapping[str, Any]) -> Path:
    path = directory / logs.SESSION_MANIFEST
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def mark_session_ended(directory: Path, exit_code: int | None, *, ended_at: float | None = None) -> Path:
    """Record the session's end in its manifest: when, and the launcher's exit code (130 after an interrupt).

    The end record is what lets a later launch prune the session; see
    ``devcapsule.logs.session_ended``. A manifest that is missing or
    unreadable is replaced by one that carries the end alone.
    """

    path = directory / logs.SESSION_MANIFEST
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            manifest = {"format": 1}
    except (OSError, ValueError):
        manifest = {"format": 1}
    manifest["ended-at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if ended_at is None else ended_at))
    manifest["exit-code"] = exit_code
    return write_session_manifest(directory, manifest)
