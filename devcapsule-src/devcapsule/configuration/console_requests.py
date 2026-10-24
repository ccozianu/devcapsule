"""The console's deferred requests: widenings asked on the console, kept until the user confirms them on the host.

The contract and the classification are :mod:`console_channel`. A deferred
request lives in the checkout's ``requests.json`` under the launcher's
config root, in a tree beside the Docker-arguments files so the mounted
records directory never exposes it. Each is a pending, soft decision of the
checkout's listing: ``run`` asks it at the terminal, ``config show`` lists
it with the confirming command, ``config console`` applies or discards it.
"""

from __future__ import annotations

from pathlib import Path
import shlex
from typing import Sequence

from .console_channel import DeferredRequest, parse_deferred, read_document, render_deferred
from .file_formats import ProjectConfigurationError
from .listing import Decision, ListingRow
from .storage import atomic_write, config_root

__all__ = ["console_requests_path", "deferred_requests", "deferred_rows", "write_deferred"]


def console_requests_path(checkout_record: Path) -> Path:
    """Where the console's deferred requests for ``checkout_record`` live, outside the mounted records tree."""
    relative = checkout_record.relative_to(config_root() / "projects")
    name = relative.name.removesuffix(".checkout.toml")
    return config_root() / "console-requests" / relative.parent / name / "requests.json"


def deferred_requests(checkout_record: Path) -> list[DeferredRequest]:
    path = console_requests_path(checkout_record)
    if not path.is_file():
        return []
    return parse_deferred(read_document(path), str(path))


def write_deferred(checkout_record: Path, requests: Sequence[DeferredRequest]) -> Path:
    """Write the requests, or remove the file when none remain."""
    path = console_requests_path(checkout_record)
    if requests:
        atomic_write(path, render_deferred(requests))
    else:
        path.unlink(missing_ok=True)
    return path


def deferred_rows(checkout_record: Path | None, project: Path | None) -> list[ListingRow]:
    """The deferred requests as listing rows: pending, soft, each with its confirming command."""
    if checkout_record is None:
        return []
    try:
        requests = deferred_requests(checkout_record)
    except (ProjectConfigurationError, ValueError) as exc:
        return [ListingRow("console", "*", "invalid", str(exc), "repair or remove the console-requests file", "")]
    rows: list[ListingRow] = []
    context = ["--path", str(project)] if project is not None else []
    for item in requests:
        command = shlex.join(["devcapsule", "project", *context, "config", "console", "apply", item.id])
        rows.append(ListingRow(
            "console", item.id, "-", f"console request at {item.requested}",
            f"confirm or discard: {item.statement}", command,
            Decision("console", item.id, item.statement, command, reason=item.requested),
        ))
    return rows
