#!/usr/bin/env python3
"""Opt-in, bounded real Codex upgrade/rollback through an isolated ordinary CLI.

Run with this checkout's Python and freshly built PEX. ROOT must be a new path
on a host-backed mount when using an external Docker daemon. No owner checkout,
credentials or existing container is changed. Exact new images/artifacts remain
for inspection; no Docker-wide cleanup is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tomllib

from devcapsule.configuration.documents import render_document
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pex", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate", required=True, help="An exact real Codex version to try.")
    args = parser.parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    project = root / "project"
    config = project / ".devcapsule"
    config.mkdir(parents=True)
    env = dict(os.environ)
    for variable, directory in (("XDG_CONFIG_HOME", "config"), ("XDG_STATE_HOME", "state"),
                                ("XDG_DATA_HOME", "data"), ("XDG_CACHE_HOME", "cache")):
        env[variable] = str(root / directory)
    env["BROWSER"] = "true"
    manifest = {"devcapsule-schema-version": 1,
        "project": {"name": "Component upgrade acceptance fixture", "creator": "mailto:fixture@example.invalid",
                    "slug": "component-upgrade-smoke", "mount": "/workspace/project"},
        "capabilities": {"need": ["python", "python-ide", "codex-agent"]}}
    (config / "devcapsule.toml").write_text(render_document(manifest))
    lock = tomllib.loads(MATRICES[Platform.current()].resolve(manifest["capabilities"]["need"], allow_unverified=True).render_lock())
    baseline = lock["components"]["codex"]["version"]
    payload = b'#!/bin/sh\nset -eu\ncodex --version | tee /workspace/project/observed-version.txt\n'
    archive = root / "fixture-ide.tgz"
    with tarfile.open(archive, "w:gz") as stream:
        member = tarfile.TarInfo("fixture/bin/pycharm.sh")
        member.mode, member.size = 0o755, len(payload)
        stream.addfile(member, io.BytesIO(payload))
    lock["components"]["pycharm"].update(version="upgrade-fixture-1", url=archive.as_uri(), sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    lock_path = config / "devcapsule.linux-amd64.lock"
    lock_path.write_text(render_document(lock))
    original = lock_path.read_bytes()
    log = root / "commands.log"
    def run(*command: str) -> str:
        result = subprocess.run([str(args.pex.resolve()), "project", "--path", str(project), *command],
                                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        # Display session tokens are transient secrets; keep them out of evidence.
        output = re.sub(r"token=[^\s&]+", "token=REDACTED", result.stdout)
        with log.open("a") as stream:
            stream.write("project " + " ".join(command) + "\n" + output + "\n")
        if result.returncode:
            raise RuntimeError(f"{' '.join(command)} exited {result.returncode}; see {log}")
        return output
    run("config", "authorize", "base-image", "default")
    run("config", "authorize", "host-x11", "false")
    run("config", "resolve")
    run("versions", "show")
    run("run")
    first = (project / "observed-version.txt").read_text().strip()
    assert first == "codex-cli " + baseline, first
    run("versions", "check")
    output = run("versions", "preview", "codex", args.candidate)
    preview = re.search(r"^Preview ([0-9a-f]{64})$", output, re.MULTILINE)
    assert preview is not None, output
    run("versions", "select", preview[1], "--unvalidated")
    run("run")
    second = (project / "observed-version.txt").read_text().strip()
    assert second == "codex-cli " + args.candidate, second
    run("versions", "history")
    run("versions", "propose", str(root / "upstream.patch"))
    run("versions", "rollback")
    run("run")
    third = (project / "observed-version.txt").read_text().strip()
    assert third == first, (first, third)
    run("versions", "follow-project", "--apply")
    assert lock_path.read_bytes() == original
    evidence = {"baseline": first, "candidate": second, "rollback": third,
                "project-lock-unchanged": True, "pex-sha256": hashlib.sha256(args.pex.read_bytes()).hexdigest(),
                "scope": "Real Codex --version through ordinary launch; fixture IDE, no accounts or interactive IDE acceptance."}
    (root / "result.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
