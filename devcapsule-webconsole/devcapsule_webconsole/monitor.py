"""Live processes and resources: psutil for the processes, the cgroup for the capsule's share.

Deliverable 3 of the capsule web console work order. Everything here is a
reading; the API that serves it is ``GET`` only, so the console can show a
process but never signal, stop or restart one.

A capsule is a cgroup. Under cgroup v2 its root exposes the CPU time it has
used, its CPU quota, its memory use and limit, and its task count; this
module reads those files directly. Outside a cgroup v2 root, or on a host
whose cgroup is not the capsule's, the resource reading says it is not
available instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import time
from typing import Any, Callable, Iterable

import psutil

CGROUP_ROOT = Path("/sys/fs/cgroup")
SAMPLE_INTERVAL_SECONDS = 0.25
"""How long a CPU rate is measured over; short enough for a page, long enough to mean something."""
COMMAND_LINE_LIMIT = 200
PROCESS_FIELDS = ("pid", "ppid", "name", "username", "cmdline", "status", "memory_info", "create_time")


@dataclass(frozen=True)
class CgroupReading:
    """One reading of the cgroup v2 files the console shows; ``None`` is absent or unlimited."""

    available: bool
    usage_usec: int | None = None
    quota_usec: int | None = None
    period_usec: int | None = None
    memory_current: int | None = None
    memory_max: int | None = None
    anon: int | None = None
    file: int | None = None
    pids_current: int | None = None
    pids_max: int | None = None


def read_cgroup(root: Path = CGROUP_ROOT) -> CgroupReading:
    """Read a cgroup v2 root, excluding the host's unrestricted hierarchy root.

    The host hierarchy root has CPU statistics but lacks these non-root
    controller files. Accept any one, since controllers can be disabled.
    """
    try:
        has_cgroup = (root / "cpu.stat").is_file() and any(
            (root / name).is_file() for name in ("cpu.max", "memory.current", "pids.current")
        )
    except OSError:
        return CgroupReading(available=False)
    if not has_cgroup:
        return CgroupReading(available=False)
    stat = _key_values(root / "cpu.stat")
    memory_stat = _key_values(root / "memory.stat")
    quota, period = _cpu_max(root / "cpu.max")
    return CgroupReading(
        available=True,
        usage_usec=stat.get("usage_usec"),
        quota_usec=quota,
        period_usec=period,
        memory_current=_integer(root / "memory.current"),
        memory_max=_integer(root / "memory.max"),
        anon=memory_stat.get("anon"),
        file=memory_stat.get("file"),
        pids_current=_integer(root / "pids.current"),
        pids_max=_integer(root / "pids.max"),
    )


def resources(
    root: Path = CGROUP_ROOT,
    *,
    interval: float = SAMPLE_INTERVAL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    cpu_count: Callable[[], int | None] = os.cpu_count,
) -> dict[str, Any]:
    """The capsule's CPU and memory use against its limits, as the resources page shows them.

    CPU use is a rate: the cgroup's CPU time over ``interval`` of wall time,
    divided by the CPUs the capsule may use, its quota when it has one and
    the host's count otherwise. Memory is the current charge against the
    limit, when there is one.
    """
    first = read_cgroup(root)
    started = clock()
    sleep(interval)
    second = read_cgroup(root)
    elapsed = clock() - started
    limit_cpus = (second.quota_usec / second.period_usec) if second.quota_usec and second.period_usec else None
    available_cpus = limit_cpus if limit_cpus is not None else float(cpu_count() or 1)
    percent: float | None = None
    if (first.usage_usec is not None and second.usage_usec is not None
            and second.usage_usec >= first.usage_usec and elapsed > 0):
        percent = round((second.usage_usec - first.usage_usec) / (elapsed * 1_000_000 * available_cpus) * 100, 1)
    memory_percent = (
        round(second.memory_current / second.memory_max * 100, 1)
        if second.memory_current is not None and second.memory_max else None
    )
    return {
        "available": second.available,
        "sampled-at": _now(),
        "interval-seconds": round(elapsed, 3),
        "cpu": {
            "usage-seconds": None if second.usage_usec is None else round(second.usage_usec / 1_000_000, 3),
            "percent": percent,
            "limit-cpus": limit_cpus,
            "available-cpus": available_cpus,
        },
        "memory": {
            "current-bytes": second.memory_current,
            "limit-bytes": second.memory_max,
            "anon-bytes": second.anon,
            "file-bytes": second.file,
            "percent": memory_percent,
        },
        "pids": {"current": second.pids_current, "max": second.pids_max},
    }


def processes(
    *,
    interval: float = SAMPLE_INTERVAL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    iterate: Callable[..., Iterable[Any]] = psutil.process_iter,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Every process the console can see, with its CPU share over ``interval`` and its memory.

    CPU is user plus system time divided by elapsed wall time: 100% means
    one busy CPU. Keep the samples local to this request: process_iter
    caches Process objects, whose cpu_percent baseline other requests could
    overwrite. Omit an exited or replaced process. Retain unreadable fields
    as None, including CPU when either CPU reading is refused.
    """
    candidates = []
    for process in iterate(PROCESS_FIELDS):
        try:
            first_cpu = _process_cpu_time(process)
        except psutil.NoSuchProcess:
            continue
        candidates.append((process, process.info, first_cpu, clock()))
    sleep(interval)
    rows = []
    for process, info, first_cpu, started in candidates:
        try:
            if not process.is_running():
                continue
            second_cpu = _process_cpu_time(process)
        except psutil.NoSuchProcess:
            continue
        elapsed = clock() - started
        cpu = (
            round((second_cpu - first_cpu) / elapsed * 100, 1)
            if first_cpu is not None and second_cpu is not None
            and second_cpu >= first_cpu and elapsed > 0 else None
        )
        memory = info.get("memory_info")
        command = " ".join(info.get("cmdline") or ()) or info.get("name") or ""
        created = info.get("create_time")
        rows.append({
            "pid": info.get("pid"),
            "ppid": info.get("ppid"),
            "user": info.get("username"),
            "name": info.get("name"),
            "command": command[:COMMAND_LINE_LIMIT] + ("…" if len(command) > COMMAND_LINE_LIMIT else ""),
            "status": info.get("status"),
            "cpu-percent": cpu,
            "rss-bytes": None if memory is None else int(memory.rss),
            "started": None if created is None else datetime.fromtimestamp(created, timezone.utc).isoformat(),
        })
    rows.sort(key=lambda row: (row["cpu-percent"] is None, -(row["cpu-percent"] or 0),
                               -(row["rss-bytes"] or 0), row["pid"] or 0))
    return {"sampled-at": _now(), "interval-seconds": interval, "count": len(rows), "processes": rows}


def _process_cpu_time(process: psutil.Process) -> float | None:
    try:
        times = process.cpu_times()
    except psutil.AccessDenied:
        return None
    return float(times.user + times.system)


def _key_values(path: Path) -> dict[str, int]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    values: dict[str, int] = {}
    for line in lines:
        key, _, value = line.partition(" ")
        if value.strip().isdigit():
            values[key] = int(value)
    return values


def _integer(path: Path) -> int | None:
    """A single-value cgroup file; ``max`` and an unreadable file are ``None``."""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return int(text) if text.isdigit() else None


def _cpu_max(path: Path) -> tuple[int | None, int | None]:
    """``cpu.max`` is ``$QUOTA $PERIOD`` with ``max`` for no quota."""
    try:
        quota, _, period = path.read_text(encoding="utf-8").strip().partition(" ")
    except OSError:
        return None, None
    return (int(quota) if quota.isdigit() else None), (int(period) if period.strip().isdigit() else None)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
