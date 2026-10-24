"""The launcher's side of the console's configuration channel: watch, apply, defer, and the deferred store.

The contract is :mod:`devcapsule.configuration.console_channel`. While a
capsule runs, a watcher thread sweeps the mounted directory for complete
request files and answers each with a result file. An applied request runs
the config command as the command line would, in a child process, so its
validation, its output and its exit status are the command's own and no
output crosses into the launcher's terminal. A deferred request is kept in
the checkout's console-requests file under the launcher's config root, a
sibling tree of the Docker-arguments files, until the user confirms or
discards it on the host.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import subprocess
import sys
import threading
from typing import Any, Sequence

from devcapsule.configuration.console_channel import (
    CHANNEL_FORMAT,
    LISTING_FILE,
    REQUEST_SUFFIX,
    RESULT_SUFFIX,
    DeferredRequest,
    Disposition,
    classify,
    now,
    parse_deferred,
    parse_request,
    read_document,
    render_deferred,
    request_id,
    result_document,
    statement,
    write_complete,
)
from devcapsule.configuration.console_requests import deferred_requests, write_deferred
from devcapsule.configuration.file_formats import ProjectConfigurationError

__all__ = ["ChannelView", "ChannelWatcher", "apply_deferred", "discard_deferred", "handle_request", "read_channel",
           "run_config", "sweep"]

_log = logging.getLogger("devcapsule.console-channel")
COMMAND_TIMEOUT_SECONDS = 120.0
SWEEP_INTERVAL_SECONDS = 1.0


def _config_command(root: Path, arguments: Sequence[str]) -> list[str]:
    return [sys.executable, "-m", "devcapsule", "project", "--path", str(root), "config", *arguments]


def run_config(root: Path, arguments: Sequence[str]) -> tuple[int, str]:
    """Run ``config ARGUMENTS`` for the project at ``root`` as its own process; the status and the combined output."""
    try:
        completed = subprocess.run(_config_command(root, arguments), capture_output=True, text=True,
                                   timeout=COMMAND_TIMEOUT_SECONDS, check=False, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 1, f"the command did not finish within {COMMAND_TIMEOUT_SECONDS:g} seconds"
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode, output


def handle_request(root: Path, checkout_record: Path, request_path: Path) -> dict[str, Any]:
    """Answer one request file with its result file; the result document."""
    identifier = request_id(request_path)
    try:
        document = read_document(request_path)
        arguments = parse_request(document, request_path.name)
    except ProjectConfigurationError as exc:
        result = result_document("refused", str(exc))
        write_complete(request_path.with_name(identifier + RESULT_SUFFIX), result)
        return result
    disposition, reason = classify(arguments)
    if disposition is Disposition.APPLY:
        status, output = run_config(root, arguments)
        if status == 0:
            result = result_document("recorded", output or f"Recorded for the next launch: {statement(arguments)}")
        else:
            result = result_document("refused", output or f"{statement(arguments)} exited with status {status}")
    elif disposition is Disposition.DEFER:
        asked = document.get("requested") if isinstance(document, dict) else None
        requested = asked if isinstance(asked, str) and asked else now()
        kept = [item for item in deferred_requests(checkout_record) if item.id != identifier]
        kept.append(DeferredRequest(identifier, requested, tuple(arguments)))
        write_deferred(checkout_record, kept)
        result = result_document(
            "deferred",
            f"Kept as the console's request {identifier}: {statement(arguments)}. It widens what the next launch "
            "reaches, so the launcher takes it only from you, on the host: the next 'devcapsule project run' asks, "
            f"or 'devcapsule project config console apply {identifier}'.",
            requested,
        )
    else:
        result = result_document("refused", reason)
    write_complete(request_path.with_name(identifier + RESULT_SUFFIX), result)
    return result


def sweep(directory: Path, root: Path, checkout_record: Path) -> int:
    """Answer every complete request in ``directory`` that has no result yet; how many were answered."""
    answered = 0
    try:
        names = sorted(path for path in directory.iterdir() if path.name.endswith(REQUEST_SUFFIX))
    except OSError:
        return 0
    for request_path in names:
        try:
            identifier = request_id(request_path)
        except ProjectConfigurationError:
            continue  # not the contract's name; a file the console did not write
        if request_path.with_name(identifier + RESULT_SUFFIX).exists():
            continue
        try:
            handle_request(root, checkout_record, request_path)
        except Exception as exc:  # noqa: BLE001 - one bad request never stops the watcher
            _log.warning("console request %s: %s", request_path.name, exc)
            try:
                write_complete(request_path.with_name(identifier + RESULT_SUFFIX),
                               result_document("refused", f"the launcher could not handle it: {exc}"))
            except OSError:
                pass
        answered += 1
    return answered


class ChannelWatcher:
    """A thread sweeping the channel directory while the capsule runs; ``stop`` sweeps once more."""

    def __init__(self, directory: Path, root: Path, checkout_record: Path,
                 interval: float = SWEEP_INTERVAL_SECONDS) -> None:
        self.directory = directory
        self.root = root
        self.checkout_record = checkout_record
        self.interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="devcapsule-console-channel", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=COMMAND_TIMEOUT_SECONDS + 5)
        sweep(self.directory, self.root, self.checkout_record)

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            sweep(self.directory, self.root, self.checkout_record)


def apply_deferred(root: Path, checkout_record: Path, identifier: str) -> tuple[int, str]:
    """Run the deferred request ``identifier`` as its command, and forget it; the command's status and output."""
    requests = deferred_requests(checkout_record)
    match = next((item for item in requests if item.id == identifier), None)
    if match is None:
        raise ProjectConfigurationError(f"No console request {identifier!r} awaits confirmation for this checkout.")
    status, output = run_config(root, match.arguments)
    if status == 0:
        write_deferred(checkout_record, [item for item in requests if item.id != identifier])
    return status, output


def discard_deferred(checkout_record: Path, identifier: str) -> None:
    requests = deferred_requests(checkout_record)
    if all(item.id != identifier for item in requests):
        raise ProjectConfigurationError(f"No console request {identifier!r} awaits confirmation for this checkout.")
    write_deferred(checkout_record, [item for item in requests if item.id != identifier])


@dataclass(frozen=True)
class ChannelView:
    """What the capsule reads from the mounted directory: the launch-time listing and the requests since."""

    at: str
    listing: dict[str, Any]
    requests: tuple[dict[str, Any], ...]


def read_channel(directory: Path) -> ChannelView | None:
    """The channel's view inside a capsule, or ``None`` when the launcher wrote no listing there."""
    from devcapsule.configuration.console_channel import parse_listing
    listing_path = directory / LISTING_FILE
    if not listing_path.is_file():
        return None
    at, listing = parse_listing(read_document(listing_path))
    requests: list[dict[str, Any]] = []
    for request_path in sorted(path for path in directory.iterdir() if path.name.endswith(REQUEST_SUFFIX)):
        try:
            identifier = request_id(request_path)
            arguments = parse_request(read_document(request_path), request_path.name)
        except ProjectConfigurationError as exc:
            requests.append({"id": request_path.name, "arguments": [], "statement": "", "requested": "",
                             "result": {"format": CHANNEL_FORMAT, "status": "refused", "text": str(exc), "at": ""}})
            continue
        document = read_document(request_path)
        result_path = request_path.with_name(identifier + RESULT_SUFFIX)
        result = read_document(result_path) if result_path.is_file() else None
        requests.append({"id": identifier, "arguments": arguments, "statement": statement(arguments),
                         "requested": str(document.get("requested", "")), "result": result})
    return ChannelView(at, listing, tuple(requests))
