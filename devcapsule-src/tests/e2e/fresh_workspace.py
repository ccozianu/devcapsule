"""A fresh workspace for an end-to-end test: a clean clone with its own configuration roots.

The rule, from the owner's ruling of 2026-10-05 recorded in
``engineering-docs/development/e2e-tests.md``: every end-to-end test runs on
a fresh workspace. It refuses a source checkout with uncommitted changes,
clones the current revision from the local tree into its own run directory,
and keeps every configuration root the launcher would otherwise share
(``XDG_CONFIG_HOME`` and friends) beneath that run directory. The test then
runs against the clone and never reads or writes the capsule's own checkout
records, which is what lets those records go stale or be read-only without
the test caring.

Inside a capsule the run directory lives under the persistent home's E2E
workspace, a host-backed bind mount the host daemon can translate and bind
for a successor; ``/tmp`` is a container-local tmpfs the daemon cannot see.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tomllib
from typing import Any, Mapping

from devcapsule.recursive_successor import MILESTONE_MANIFEST, OWNER_MARKER, WORKSPACE_ROOT
from devcapsule.runtime_configuration import CONFIGURATION_PATH, CONTEXT_PATH


class DirtySourceError(AssertionError):
    """The source checkout has uncommitted changes; a fresh workspace needs an exact commit."""


def require_clean_source(source: Path) -> str:
    """The full revision of ``source``'s HEAD, refusing a dirty worktree.

    Submodule worktrees are ignored: the clone never recurses into them and
    takes the committed pointer, so a submodule moved by hand cannot reach
    the clone, while a moved pointer is the ordinary state of a developer's
    checkout of this repository.
    """
    status = _git(source, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=all")
    if status:
        raise DirtySourceError(
            "the source checkout has uncommitted changes; commit or remove them before the "
            f"end-to-end test, which clones an exact commit:\n{status}"
        )
    return _git(source, "rev-parse", "--verify", "HEAD^{commit}")


@dataclass(frozen=True)
class FreshWorkspace:
    """One run directory this test owns: the clone, its configuration roots, its evidence."""

    run_id: str
    run_root: Path
    checkout: Path
    revision: str

    @classmethod
    def create(cls, source: Path, *, workspace_root: Path = WORKSPACE_ROOT) -> FreshWorkspace:
        """Clone ``source``'s HEAD into a new owned run directory under ``workspace_root``."""
        revision = require_clean_source(source)
        run_id = secrets.token_hex(16)
        run_root = workspace_root / run_id
        run_root.mkdir(parents=True, mode=0o700)
        run_root.chmod(0o700)
        (run_root / OWNER_MARKER).write_text(
            json.dumps({"schema_version": 1, "run_id": run_id}), encoding="utf-8"
        )
        for name in ("config", "data", "state", "cache", "git-home", "empty-hooks"):
            (run_root / "xdg" / name).mkdir(parents=True, mode=0o700)
        workspace = cls(run_id, run_root, run_root / "checkout", revision)
        workspace.record_state("stage-4-cloning", source_revision=revision)
        workspace._clone(source)
        workspace.record_state("stage-4-cloned", source_revision=revision, checkout=str(workspace.checkout))
        return workspace

    def _clone(self, source: Path) -> None:
        # Git gets an allowlist, not the ambient environment: a local clone
        # must not import credential helpers, prompts, templates or hooks.
        git_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.run_root / "xdg" / "git-home"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        }
        hooks = self.run_root / "xdg" / "empty-hooks"
        subprocess.run(
            ["git", "-c", "protocol.file.allow=always", "-c", "credential.helper=",
             "-c", f"init.templateDir={hooks}", "clone", "--quiet", "--local", "--no-hardlinks",
             "--no-checkout", "--no-recurse-submodules", "--", str(source), str(self.checkout)],
            env=git_env, check=True, capture_output=True, text=True,
        )
        for arguments in (("config", "core.hooksPath", str(hooks)),
                          ("-c", "advice.detachedHead=false", "checkout", "--quiet", "--detach", self.revision),
                          ("remote", "remove", "origin")):
            subprocess.run(["git", "-C", str(self.checkout), *arguments], env=git_env, check=True,
                           capture_output=True, text=True)
        assert _git(self.checkout, "rev-parse", "HEAD") == self.revision
        assert not _git(self.checkout, "status", "--porcelain=v1", "--untracked-files=all")

    def environment(self) -> dict[str, str]:
        """The ambient environment with every configuration root under the run directory."""
        xdg = self.run_root / "xdg"
        return {
            **os.environ,
            "XDG_CONFIG_HOME": str(xdg / "config"), "XDG_DATA_HOME": str(xdg / "data"),
            "XDG_STATE_HOME": str(xdg / "state"), "XDG_CACHE_HOME": str(xdg / "cache"),
        }

    def cli(self, *arguments: str) -> list[str]:
        """The launcher under test, selecting the clone."""
        return [sys.executable, "-m", "devcapsule", "project", "--path", str(self.checkout), *arguments]

    def run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        """Run one launcher command against the clone under the isolated roots."""
        completed = subprocess.run(self.cli(*arguments), env=self.environment(), text=True,
                                   capture_output=True, stdin=subprocess.DEVNULL, check=False)
        assert completed.returncode == 0, (
            f"{' '.join(arguments)} failed with exit {completed.returncode}:\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
        return completed

    def configure_like_this_capsule(self) -> dict[str, Any]:
        """Answer the clone's authorizations and values as this capsule's own checkout did.

        The answers come from the launcher's record mounted read-only at
        launch; they are written to the clone's own record under the isolated
        roots through the ordinary commands, never by editing a file. The
        base image is taken as the lock recommends it.
        """
        context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
        with (CONFIGURATION_PATH / context["checkout-file"]).open("rb") as stream:
            record = tomllib.load(stream)
        answers: dict[str, Any] = {}
        for name, answer in record.get("authorization", {}).items():
            value = "default" if name == "base-image" else answer["value"]
            answers[name] = value
            self.run("config", "authorize", name, _spell(value))
        for name, value in record.get("configuration", {}).get("values", {}).items():
            answers[name] = value
            self.run("config", "set", name, _spell(value))
        self.run("config", "resolve")
        self.record_state("stage-5-resolved", source_revision=self.revision, answers=answers)
        return answers

    def record_state(self, state: str, **facts: Any) -> None:
        """Write the run manifest the successor launch reads and updates."""
        (self.run_root / MILESTONE_MANIFEST).write_text(
            json.dumps({"schema_version": 1, "run_id": self.run_id, "state": state, **facts},
                       sort_keys=True), encoding="utf-8")

    def manifest(self) -> dict[str, Any]:
        try:
            value = json.loads((self.run_root / MILESTONE_MANIFEST).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}

    def cleanup(self) -> bool:
        """Remove the run directory and free its space; best effort, reported not fatal."""
        shutil.rmtree(self.run_root, ignore_errors=True)
        return not self.run_root.exists()


def _spell(value: Any) -> str:
    return str(value).lower() if isinstance(value, bool) else str(value)


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(["git", "--no-optional-locks", "-C", str(root), *arguments], check=True,
                          capture_output=True, text=True).stdout.strip()
