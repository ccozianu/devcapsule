"""Known-good checkout-configuration history (D-0008).

A generation is recorded only when a launch succeeds (the launcher observed
exit code zero), and only when no existing generation has identical
content — the history is a short menu of distinct proven configurations,
never a diary of edits. Generations are plain stamped directories under the
XDG state home, so restoring is an ordinary file copy with no failure modes
of its own.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote

from devcapsule.platforms import XdgHomes

__all__ = ["history_directory", "record_known_good_configuration"]

_SNAPSHOT_METADATA = "snapshot.toml"


def history_directory(
    manifest: Mapping[str, Any], env: Mapping[str, str] | None = None
) -> Path:
    """This project's known-good history root under the XDG state home.

    Deliberately outside the config tree: ``project list`` discovers
    checkouts by globbing for ``devcapsule.checkout.toml``, so historical
    copies inside ``config/…/projects`` would appear as phantom checkouts.
    The creator/slug encoding matches the config tree's directory scheme.
    """

    project = manifest["project"]
    creator = quote(str(project["creator"]), safe="")
    slug = quote(str(project["slug"]), safe="")
    return XdgHomes.from_environment(env).state / "config-history" / creator / slug


def record_known_good_configuration(
    manifest: Mapping[str, Any],
    checkout_record: Path,
    generated_resolution: Path,
    env: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> Path | None:
    """Record the configuration a successful launch just proved, once.

    Returns the created generation directory, or None when an existing
    generation already holds identical content. Content identity is
    recomputed from the copied files themselves rather than trusted from
    metadata, so hand-pruned or hand-edited history stays honest.
    """

    files = {
        checkout_record.name: checkout_record.read_bytes(),
        generated_resolution.name: generated_resolution.read_bytes(),
    }
    digest = _content_digest(files)
    root = history_directory(manifest, env)
    if any(_generation_digest(existing) == digest for existing in _generations(root)):
        return None

    root.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    destination = _unclaimed(root, stamp)
    # Stage under a dot-prefixed name (excluded from _generations) and
    # rename, so a crash mid-copy never leaves a half generation visible.
    staging = root / f".incoming-{destination.name}"
    staging.mkdir(mode=0o700)
    for name, content in files.items():
        _write_private(staging / name, content)
    _write_private(
        staging / _SNAPSHOT_METADATA,
        (
            f'recorded-at = "{stamp}"\n'
            f'content-digest = "{digest}"\n'
            f'checkout-record = "{checkout_record}"\n'
        ).encode("utf-8"),
    )
    staging.rename(destination)
    return destination


def _content_digest(files: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(files[name])
        digest.update(b"\x00")
    return digest.hexdigest()


def _generations(root: Path) -> tuple[Path, ...]:
    if not root.is_dir():
        return ()
    return tuple(
        entry
        for entry in sorted(root.iterdir())
        if entry.is_dir() and not entry.name.startswith(".")
    )


def _generation_digest(generation: Path) -> str:
    files = {
        entry.name: entry.read_bytes()
        for entry in sorted(generation.iterdir())
        if entry.is_file() and entry.name != _SNAPSHOT_METADATA
    }
    return _content_digest(files)


def _unclaimed(root: Path, stamp: str) -> Path:
    candidate = root / stamp
    counter = 2
    while candidate.exists() or (root / f".incoming-{candidate.name}").exists():
        candidate = root / f"{stamp}-{counter}"
        counter += 1
    return candidate


def _write_private(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
