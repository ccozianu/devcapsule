"""Processes and resources: the cgroup reader, the rates, and the process sampler."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import psutil
import pytest

from conftest import with_token
from devcapsule_webconsole import monitor
from devcapsule_webconsole.monitor import CgroupReading, processes, read_cgroup, resources


def write_cgroup(root: Path, *, usage: int = 1_000_000, cpu_max: str = "max 100000", memory_max: str = "max",
                 current: int = 512 * 1024 * 1024, pids: int = 42) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "cpu.stat").write_text(f"usage_usec {usage}\nuser_usec {usage // 2}\nsystem_usec {usage // 2}\nnr_periods 0\n")
    (root / "cpu.max").write_text(cpu_max + "\n")
    (root / "memory.current").write_text(f"{current}\n")
    (root / "memory.max").write_text(memory_max + "\n")
    (root / "memory.stat").write_text(f"anon {current // 2}\nfile {current // 4}\nkernel 123\n")
    (root / "pids.current").write_text(f"{pids}\n")
    (root / "pids.max").write_text("4096\n")


def test_read_cgroup_parses_limits_and_treats_max_as_unlimited(tmp_path: Path) -> None:
    write_cgroup(tmp_path / "cg", usage=7_686_797_447, cpu_max="max 100000", memory_max="max", current=8_021_737_472)
    reading = read_cgroup(tmp_path / "cg")
    assert reading == CgroupReading(
        available=True, usage_usec=7_686_797_447, quota_usec=None, period_usec=100000,
        memory_current=8_021_737_472, memory_max=None, anon=4_010_868_736, file=2_005_434_368,
        pids_current=42, pids_max=4096,
    )
    write_cgroup(tmp_path / "limited", cpu_max="50000 100000", memory_max="2147483648")
    limited = read_cgroup(tmp_path / "limited")
    assert (limited.quota_usec, limited.period_usec, limited.memory_max) == (50000, 100000, 2147483648)


def test_read_cgroup_without_a_v2_root_is_unavailable(tmp_path: Path) -> None:
    assert read_cgroup(tmp_path / "absent") == CgroupReading(available=False)
    (tmp_path / "v1").mkdir()
    (tmp_path / "v1" / "memory.current").write_text("1\n")
    assert read_cgroup(tmp_path / "v1") == CgroupReading(available=False)


def test_read_cgroup_tolerates_a_partly_readable_root(tmp_path: Path) -> None:
    root = tmp_path / "cg"
    root.mkdir()
    (root / "cpu.stat").write_text("usage_usec 10\nbogus\nnr_periods x\n")
    (root / "cpu.max").write_text("garbage\n")
    reading = read_cgroup(root)
    assert reading.available and reading.usage_usec == 10
    assert (reading.quota_usec, reading.period_usec, reading.memory_current, reading.memory_max, reading.anon) == (None, None, None, None, None)


def test_resources_measures_cpu_over_the_interval_against_the_available_cpus(tmp_path: Path) -> None:
    root = tmp_path / "cg"
    write_cgroup(root, usage=1_000_000, cpu_max="200000 100000", memory_max="1073741824", current=268435456)
    ticks = iter([10.0, 10.2])

    def advance(seconds: float) -> None:
        assert seconds == 0.25
        write_cgroup(root, usage=1_000_000 + 100_000, cpu_max="200000 100000", memory_max="1073741824", current=268435456)

    document = resources(root, sleep=advance, clock=lambda: next(ticks), cpu_count=lambda: 16)
    assert document["available"] is True
    assert document["interval-seconds"] == 0.2
    # 100 000 µs of CPU in 200 000 µs of wall time on a 2-CPU quota: a quarter.
    assert document["cpu"] == {"usage-seconds": 1.1, "percent": 25.0, "limit-cpus": 2.0, "available-cpus": 2.0}
    assert document["memory"] == {"current-bytes": 268435456, "limit-bytes": 1073741824,
                                  "anon-bytes": 134217728, "file-bytes": 67108864, "percent": 25.0}
    assert document["pids"] == {"current": 42, "max": 4096}
    assert document["sampled-at"].endswith("+00:00")


def test_resources_without_a_quota_divide_by_the_host_cpus_and_report_no_limits(tmp_path: Path) -> None:
    root = tmp_path / "cg"
    write_cgroup(root, usage=0)
    ticks = iter([0.0, 0.5])
    document = resources(root, sleep=lambda _: write_cgroup(root, usage=2_000_000), clock=lambda: next(ticks), cpu_count=lambda: 4)
    assert document["cpu"] == {"usage-seconds": 2.0, "percent": 100.0, "limit-cpus": None, "available-cpus": 4.0}
    assert document["memory"]["limit-bytes"] is None and document["memory"]["percent"] is None


def test_resources_are_unavailable_outside_a_cgroup_root(tmp_path: Path) -> None:
    document = resources(tmp_path / "none", sleep=lambda _: None, clock=lambda: 1.0, cpu_count=lambda: None)
    assert document["available"] is False
    assert document["cpu"] == {"usage-seconds": None, "percent": None, "limit-cpus": None, "available-cpus": 1.0}
    assert document["memory"] == {"current-bytes": None, "limit-bytes": None, "anon-bytes": None, "file-bytes": None, "percent": None}
    assert document["pids"] == {"current": None, "max": None}


class FakeProcess:
    def __init__(self, pid: int, cpu: float, rss: int, *, cmdline: list[str] | None = None, fail: str = "") -> None:
        self.info = {"pid": pid, "ppid": 1, "name": f"proc{pid}", "username": "devcapsule",
                     "cmdline": cmdline if cmdline is not None else [f"/bin/proc{pid}", "--flag"],
                     "status": "sleeping", "memory_info": SimpleNamespace(rss=rss), "create_time": 1_700_000_000.0}
        self.cpu = cpu
        self.fail = fail
        self.calls = 0

    def cpu_times(self) -> SimpleNamespace:
        self.calls += 1
        if self.fail == "first" or (self.fail == "second" and self.calls == 2):
            raise psutil.NoSuchProcess(self.info["pid"])
        return SimpleNamespace(user=0.0 if self.calls == 1 else self.cpu * 0.25 / 100, system=0.0)

    def is_running(self) -> bool:
        return True


def test_processes_prime_wait_and_sort_by_cpu_then_memory() -> None:
    fakes = [FakeProcess(10, 1.5, 100), FakeProcess(11, 40.0, 50), FakeProcess(12, 1.5, 900),
             FakeProcess(13, 99.0, 1, fail="first"), FakeProcess(14, 99.0, 1, fail="second"),
             FakeProcess(16, 0.0, 10, cmdline=[]), FakeProcess(15, 0.0, 10, cmdline=["x" * 300])]
    slept: list[float] = []

    def iterate(fields: tuple[str, ...]) -> list[FakeProcess]:
        assert fields == monitor.PROCESS_FIELDS
        return fakes

    listing = processes(sleep=slept.append, iterate=iterate, clock=lambda: 0.25 if slept else 0.0)
    assert slept == [0.25]
    assert [row["pid"] for row in listing["processes"]] == [11, 12, 10, 15, 16]
    assert listing["count"] == 5
    first = listing["processes"][0]
    assert first == {"pid": 11, "ppid": 1, "user": "devcapsule", "name": "proc11", "command": "/bin/proc11 --flag",
                     "status": "sleeping", "cpu-percent": 40.0, "rss-bytes": 50, "started": "2023-11-14T22:13:20+00:00"}
    long_command = next(row for row in listing["processes"] if row["pid"] == 15)["command"]
    assert len(long_command) == monitor.COMMAND_LINE_LIMIT + 1 and long_command.endswith("…")
    assert next(row for row in listing["processes"] if row["pid"] == 16)["command"] == "proc16"
    assert all(fake.calls == 2 for fake in fakes if fake.fail != "first")


def test_processes_run_against_the_real_process_table() -> None:
    listing = processes(interval=0.05)
    assert listing["count"] >= 1
    assert any(row["pid"] == psutil.Process().pid for row in listing["processes"])


@pytest.mark.parametrize("route", ["/api/processes", "/api/resources"])
def test_monitor_routes_serve_the_readings_behind_the_token(client, monkeypatch, route):
    documents = {
        "/api/processes": {"count": 1, "processes": [{"pid": 123}], "sampled-at": "t", "interval-seconds": 0.25},
        "/api/resources": {"available": False, "cpu": {}, "memory": {}, "pids": {}, "sampled-at": "t", "interval-seconds": 0},
    }
    calls = []

    def read(path):
        calls.append(path)
        return documents[path]

    monkeypatch.setattr(monitor, "processes", lambda: read("/api/processes"))
    monkeypatch.setattr(monitor, "resources", lambda: read("/api/resources"))
    assert client.get(route).status_code == 403
    assert calls == []
    response = with_token(client).get(route)
    assert response.status_code == 200
    assert response.json() == documents[route]
    assert calls == [route]
    for method in ("post", "put", "patch", "delete"):
        assert getattr(client, method)(route).status_code == 405
    assert calls == [route]


def test_processes_page_is_served_and_names_its_script(client):
    assert client.get("/processes").status_code == 403
    response = with_token(client).get("/processes")
    assert response.status_code == 200
    assert 'data-page="processes"' in response.text and "<h1>Processes and resources</h1>" in response.text
    assert '<script src="/static/console.js" defer></script>' in response.text
    assert with_token(client).get("/").text.count('href="/processes"') == 2  # navigation and card


def test_host_hierarchy_root_is_not_a_capsule(tmp_path: Path) -> None:
    # The unified host root exposes cpu.stat without non-root controller files.
    (tmp_path / "cpu.stat").write_text("usage_usec 123\n")
    assert read_cgroup(tmp_path) == CgroupReading(available=False)


@pytest.mark.parametrize("file", ["memory.current", "pids.current"])
def test_cgroup_with_cpu_controller_disabled_keeps_other_readings(tmp_path, file):
    (tmp_path / "cpu.stat").write_text("usage_usec 123\n")
    (tmp_path / file).write_text("42\n")
    reading = read_cgroup(tmp_path)
    assert reading == CgroupReading(available=True, usage_usec=123,
                                   memory_current=42 if file == "memory.current" else None,
                                   pids_current=42 if file == "pids.current" else None)


@pytest.mark.parametrize("elapsed, usage, expected", [(0, 1_100_000, None), (0.25, 500_000, None), (0.25, 1_125_000, 100.0)])
def test_resources_reject_invalid_rates_and_handle_fractional_quota(tmp_path, elapsed, usage, expected):
    write_cgroup(tmp_path, cpu_max="50000 100000")
    ticks = iter([0.0, elapsed])
    result = resources(tmp_path, sleep=lambda _: write_cgroup(tmp_path, usage=usage, cpu_max="50000 100000"),
                       clock=lambda: next(ticks))
    assert result["cpu"]["percent"] == expected
    assert result["cpu"]["limit-cpus"] == 0.5


def test_unreadable_cgroup_files_and_unlimited_pids(tmp_path, monkeypatch):
    write_cgroup(tmp_path)
    (tmp_path / "pids.max").write_text("max\n")
    read_text = Path.read_text

    def denied(path, *args, **kwargs):
        if path.name in {"cpu.stat", "cpu.max", "memory.current", "memory.stat"}:
            raise PermissionError(path)
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied)
    result = read_cgroup(tmp_path)
    assert result == CgroupReading(available=True, pids_current=42)


@pytest.mark.parametrize("refused_call", [1, 2])
def test_processes_keep_access_denied_cpu_and_missing_fields(refused_call):
    class Denied(FakeProcess):
        def cpu_times(self):
            result = super().cpu_times()
            if self.calls == refused_call:
                raise psutil.AccessDenied(self.info["pid"])
            return result

    denied = Denied(12, 40.0, 90)
    denied.info.update(username=None, memory_info=None, create_time=None, cmdline=None, name=None)
    ticks = iter([0.0, 0.0, 0.25, 0.25])
    result = processes(sleep=lambda _: None, iterate=lambda _: [denied, FakeProcess(13, 0.0, 1)],
                       clock=lambda: next(ticks))
    assert [row["pid"] for row in result["processes"]] == [13, 12]
    assert result["processes"][1] == {
        "pid": 12, "ppid": 1, "user": None, "name": None, "command": "", "status": "sleeping",
        "cpu-percent": None, "rss-bytes": None, "started": None,
    }
    assert denied.calls == 2


def test_processes_omit_a_reused_pid():
    class Reused(FakeProcess):
        def is_running(self):
            return False

    result = processes(sleep=lambda _: None, iterate=lambda _: [Reused(12, 40.0, 90)])
    assert result["processes"] == [] and result["count"] == 0


def test_overlapping_process_samples_keep_their_own_times_and_info():
    # process_iter returns the same cached object to both requests.
    class Shared(FakeProcess):
        def cpu_times(self):
            return SimpleNamespace(user=now[0] ** 3, system=now[0], children_user=999.0)

    now = [0.0]
    shared = Shared(12, 0.0, 90)
    inner = []

    def overlap(_):
        now[0] = 1.0
        shared.info = {**shared.info, "name": "later"}

        def advance_inner(_):
            now[0] = 2.0

        inner.append(processes(sleep=advance_inner, iterate=lambda _: [shared], clock=lambda: now[0]))
        now[0] = 3.0

    result = processes(sleep=overlap, iterate=lambda _: [shared], clock=lambda: now[0])
    assert result["processes"][0]["cpu-percent"] == 1000.0  # (27 + 3) / 3
    assert result["processes"][0]["name"] == "proc12"
    assert inner[0]["processes"][0]["cpu-percent"] == 800.0  # ((8 + 2) - (1 + 1)) / 1
    assert inner[0]["processes"][0]["name"] == "later"


@pytest.mark.parametrize("elapsed, cpu", [(0.0, 10.0), (0.25, -10.0)])
def test_processes_leave_invalid_cpu_rates_unknown(elapsed, cpu):
    ticks = iter([0.0, elapsed])
    result = processes(sleep=lambda _: None, iterate=lambda _: [FakeProcess(12, cpu, 90)], clock=lambda: next(ticks))
    assert result["processes"][0]["cpu-percent"] is None


def test_cgroup_stat_permission_failure_is_unavailable(tmp_path, monkeypatch):
    def denied(_):
        raise PermissionError("cgroup directory")

    monkeypatch.setattr(Path, "is_file", denied)
    assert read_cgroup(tmp_path) == CgroupReading(available=False)


@pytest.mark.parametrize("missing_sample", [1, 2])
def test_resources_require_two_cpu_readings(tmp_path, missing_sample):
    write_cgroup(tmp_path)
    if missing_sample == 1:
        (tmp_path / "cpu.stat").write_text("")

    def advance(_):
        (tmp_path / "cpu.stat").write_text("" if missing_sample == 2 else "usage_usec 2000000\n")

    ticks = iter([0.0, 0.25])
    result = resources(tmp_path, sleep=advance, clock=lambda: next(ticks))
    assert result["cpu"]["percent"] is None
    assert result["cpu"]["usage-seconds"] == (2.0 if missing_sample == 1 else None)


def test_resources_keep_zero_memory_and_pid_limits(tmp_path):
    write_cgroup(tmp_path, usage=0, memory_max="0", current=0, pids=0)
    (tmp_path / "pids.max").write_text("0\n")
    ticks = iter([0.0, 0.25])

    def advance(_):
        (tmp_path / "cpu.stat").write_text("usage_usec 125000\n")

    result = resources(tmp_path, sleep=advance, clock=lambda: next(ticks), cpu_count=lambda: None)
    assert result["cpu"] == {"usage-seconds": 0.125, "percent": 50.0, "limit-cpus": None, "available-cpus": 1.0}
    assert result["memory"] == {"current-bytes": 0, "limit-bytes": 0, "anon-bytes": 0, "file-bytes": 0, "percent": None}
    assert result["pids"] == {"current": 0, "max": 0}
