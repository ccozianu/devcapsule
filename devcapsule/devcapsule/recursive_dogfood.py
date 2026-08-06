"""Read-only discovery and validation for recursive dogfood execution."""

from __future__ import annotations

from dataclasses import dataclass
import grp
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
from typing import Mapping, Sequence
import zipfile

from devcapsule.build_info import current_build_info
from devcapsule.container_runtime.contract import RuntimePlan, RuntimePlanError


RUNTIME_PLAN_PATH = Path("/etc/devcapsule/runtime-plan.json")
X11_SOCKET_DIRECTORY = Path("/tmp/.X11-unix")
WORKSPACE_RELATIVE_PATH = Path(".local/share/devcapsule/e2e-workspaces")
MINIMUM_RECOMMENDED_FREE_BYTES = 20 * 1024**3
CONTAINER_NAME_ENV = "DEVCAPSULE_CONTAINER_NAME"


class PreflightError(ValueError):
    """A recursive-dogfood input is unsafe, ambiguous, or unsupported."""


@dataclass(frozen=True)
class Mount:
    source: str
    destination: str
    kind: str
    writable: bool


@dataclass(frozen=True)
class ContainerInspection:
    identity: str
    name: str
    image: str
    source_revision: str | None
    network_mode: str
    mounts: tuple[Mount, ...]
    upper_directory: str | None


@dataclass(frozen=True)
class Finding:
    status: str
    check: str
    summary: str


@dataclass(frozen=True)
class PreflightReport:
    findings: tuple[Finding, ...]
    facts: Mapping[str, str]
    mounts: tuple[Mount, ...]

    @property
    def ready(self) -> bool:
        return all(item.status != "error" for item in self.findings)

    def to_mapping(self, *, show_host_paths: bool = False) -> dict[str, object]:
        return {
            "schema_version": 1,
            "ready": self.ready,
            "facts": dict(self.facts),
            "findings": [
                {"status": item.status, "check": item.check, "summary": item.summary}
                for item in self.findings
            ],
            "mounts": [
                {
                    "source": item.source if show_host_paths else "<redacted>",
                    "destination": _display_destination(item.destination),
                    "type": item.kind,
                    "mode": "rw" if item.writable else "ro",
                }
                for item in self.mounts
            ],
        }


class _ReportBuilder:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.facts: dict[str, str] = {}

    def add(self, status: str, check: str, summary: str) -> None:
        self.findings.append(Finding(status, check, summary))

    def finish(self, mounts: tuple[Mount, ...] = ()) -> PreflightReport:
        return PreflightReport(tuple(self.findings), dict(self.facts), mounts)


def run_recursive_preflight(
    checkout: Path,
    *,
    runtime_plan_path: Path = RUNTIME_PLAN_PATH,
    environ: Mapping[str, str] | None = None,
) -> PreflightReport:
    """Inspect the current capsule without creating or changing any resource."""

    env = dict(os.environ if environ is None else environ)
    runtime_plan_path = runtime_plan_path.expanduser().resolve()
    report = _ReportBuilder()
    _inspect_distribution(report)
    checkout_root = _inspect_checkout(report, checkout)
    runtime_plan = _inspect_runtime_plan(report, runtime_plan_path)
    _inspect_process_authorization(report)
    docker_host = _inspect_docker_socket(report, env)
    container = _inspect_current_container(report, env, docker_host)

    mounts: tuple[Mount, ...] = ()
    if container is not None:
        mounts = container.mounts
        report.facts["container"] = f"{container.name} ({container.identity[:12]})"
        report.facts["network"] = container.network_mode
        report.add("pass", "container", "Current running container was identified through the host daemon.")
        if container.network_mode == "host":
            report.add("pass", "network", "Host networking is explicitly enabled for this dogfood container.")
        else:
            report.add(
                "warning",
                "network",
                "Host networking is not enabled; later local-clone or build steps may require an explicit alternative.",
            )

    if checkout_root is not None and runtime_plan is not None and container is not None:
        _inspect_required_mounts(
            report,
            checkout_root=checkout_root,
            runtime_plan_path=runtime_plan_path,
            runtime_plan=runtime_plan,
            container=container,
            env=env,
        )
        _inspect_disk(report, Path(runtime_plan.home))

    return report.finish(mounts)


def render_preflight(report: PreflightReport, *, show_host_paths: bool = False) -> str:
    """Render a stable human-readable report with host paths redacted by default."""

    value = report.to_mapping(show_host_paths=show_host_paths)
    lines = [f"Recursive dogfood preflight: {'READY' if report.ready else 'NOT READY'}"]
    facts = value["facts"]
    assert isinstance(facts, dict)
    for name, fact in facts.items():
        lines.append(f"{name.replace('_', ' ').title()}: {fact}")
    lines.append("Checks:")
    for item in report.findings:
        lines.append(f"  [{item.status.upper()}] {item.check}: {item.summary}")
    mounts = value["mounts"]
    assert isinstance(mounts, list)
    if mounts:
        lines.append("Current container mounts:")
        for item in mounts:
            assert isinstance(item, dict)
            lines.append(
                f"  {item['destination']} <- {item['source']} ({item['type']},{item['mode']})"
            )
    return "\n".join(lines)


def preflight_json(report: PreflightReport, *, show_host_paths: bool = False) -> str:
    return json.dumps(
        report.to_mapping(show_host_paths=show_host_paths),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def safe_child(root: Path, relative: Path) -> Path:
    """Return a normalized child and reject absolute or escaping input."""

    if relative.is_absolute() or ".." in relative.parts:
        raise PreflightError("recursive workspace path must be a relative non-escaping path")
    selected_root = root.resolve(strict=False)
    selected = (selected_root / relative).resolve(strict=False)
    if selected != selected_root and selected_root not in selected.parents:
        raise PreflightError("recursive workspace path escapes its persistent-home root")
    return selected


def docker_socket_path(docker_host: str | None) -> Path:
    if not docker_host:
        raise PreflightError("DOCKER_HOST must explicitly select the authorized host Docker socket")
    prefix = "unix://"
    if not docker_host.startswith(prefix):
        raise PreflightError("recursive dogfood supports only an explicitly selected unix Docker socket")
    raw_path = docker_host.removeprefix(prefix)
    selected = Path(raw_path)
    if not selected.is_absolute() or ".." in selected.parts:
        raise PreflightError("DOCKER_HOST must contain an absolute normalized unix-socket path")
    return selected


def validate_container_name(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value) is None:
        raise PreflightError(f"{CONTAINER_NAME_ENV} is malformed")
    return value


def parse_container_inspection(value: object) -> ContainerInspection:
    if not isinstance(value, dict):
        raise PreflightError("Docker returned a malformed container inspection")
    identity = value.get("Id")
    raw_name = value.get("Name")
    if not isinstance(identity, str) or re.fullmatch(r"[0-9a-f]{64}", identity) is None:
        raise PreflightError("Docker returned a malformed container identity")
    if not isinstance(raw_name, str) or not raw_name.startswith("/"):
        raise PreflightError("Docker returned a malformed container name")
    name = validate_container_name(raw_name.removeprefix("/"))
    config = value.get("Config")
    host_config = value.get("HostConfig")
    graph_driver = value.get("GraphDriver")
    if not isinstance(config, dict) or not isinstance(host_config, dict):
        raise PreflightError("Docker inspection is missing container configuration")
    image = value.get("Image")
    if not isinstance(image, str) or not image:
        raise PreflightError("Docker inspection is missing the image identity")
    labels = config.get("Labels") or {}
    if not isinstance(labels, dict):
        raise PreflightError("Docker inspection contains malformed labels")
    revision = labels.get("devcapsule.source.revision")
    if revision is not None and not isinstance(revision, str):
        raise PreflightError("Docker inspection contains a malformed source revision label")
    network_mode = host_config.get("NetworkMode")
    if not isinstance(network_mode, str) or not network_mode:
        raise PreflightError("Docker inspection is missing its network mode")
    raw_mounts = value.get("Mounts")
    if not isinstance(raw_mounts, list):
        raise PreflightError("Docker inspection is missing its mount table")
    mounts = tuple(_parse_mount(item) for item in raw_mounts)
    _reject_duplicate_destinations(mounts)

    upper_directory: str | None = None
    if isinstance(graph_driver, dict):
        data = graph_driver.get("Data")
        if isinstance(data, dict) and isinstance(data.get("UpperDir"), str):
            upper_directory = data["UpperDir"]
    return ContainerInspection(
        identity=identity,
        name=name,
        image=image,
        source_revision=revision,
        network_mode=network_mode,
        mounts=mounts,
        upper_directory=upper_directory,
    )


def identify_current_container(
    inspections: Sequence[ContainerInspection],
    *,
    expected_name: str | None,
    self_upper_directory: str | None,
) -> ContainerInspection:
    if expected_name is not None:
        selected_name = validate_container_name(expected_name)
        matches = [item for item in inspections if item.name == selected_name]
        if len(matches) != 1:
            raise PreflightError(
                "the daemon container set does not match the declared current container name"
            )
        return matches[0]
    if self_upper_directory is None:
        raise PreflightError(
            f"{CONTAINER_NAME_ENV} is absent and this storage driver exposes no safe fallback identity"
        )
    matches = [item for item in inspections if item.upper_directory == self_upper_directory]
    if len(matches) != 1:
        raise PreflightError("the current container identity is absent or ambiguous in the host daemon")
    return matches[0]


def covering_mount(path: Path, mounts: Sequence[Mount], *, require_writable: bool) -> Mount:
    selected_path = PurePosixPath(str(path))
    candidates = [
        item
        for item in mounts
        if selected_path == PurePosixPath(item.destination)
        or PurePosixPath(item.destination) in selected_path.parents
    ]
    if not candidates:
        raise PreflightError(f"container path {path} is not backed by a Docker mount")
    greatest_length = max(len(PurePosixPath(item.destination).parts) for item in candidates)
    matches = [item for item in candidates if len(PurePosixPath(item.destination).parts) == greatest_length]
    if len(matches) != 1:
        raise PreflightError(f"container path {path} has ambiguous Docker mount mappings")
    selected = matches[0]
    if require_writable and not selected.writable:
        raise PreflightError(f"container path {path} is backed by a read-only Docker mount")
    return selected


def _inspect_distribution(report: _ReportBuilder) -> None:
    info = current_build_info()
    origin = "PEX" if _running_from_pex() else "source checkout"
    report.facts["distribution"] = f"DevCapsule {info.version} ({origin})"
    report.facts["distribution_revision"] = info.source_revision
    report.add("pass", "distribution", "Embedded build information is readable.")


def _inspect_checkout(report: _ReportBuilder, checkout: Path) -> Path | None:
    selected = checkout.expanduser().resolve()
    root_result = _command(
        ["git", "--no-optional-locks", "-C", str(selected), "rev-parse", "--show-toplevel"]
    )
    if root_result.returncode != 0:
        report.add("error", "checkout", "Selected path is not inside a readable Git checkout.")
        return None
    root = Path(root_result.stdout.strip()).resolve()
    revision = _command(["git", "--no-optional-locks", "-C", str(root), "rev-parse", "HEAD"])
    status = _command(
        [
            "git",
            "--no-optional-locks",
            "-C",
            str(root),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ]
    )
    if revision.returncode != 0 or status.returncode != 0:
        report.add("error", "checkout", "Cannot inspect the checkout revision and cleanliness.")
        return None
    report.facts["checkout"] = str(root)
    report.facts["checkout_revision"] = revision.stdout.strip()
    if status.stdout:
        report.facts["checkout_clean"] = "no"
        report.add(
            "warning",
            "checkout",
            "Checkout has local changes; later clean-clone acceptance will select an exact commit.",
        )
    else:
        report.facts["checkout_clean"] = "yes"
        report.add("pass", "checkout", "Checkout revision is exact and the worktree is clean.")
    return root


def _inspect_runtime_plan(report: _ReportBuilder, path: Path) -> RuntimePlan | None:
    try:
        plan = RuntimePlan.from_file(path)
    except RuntimePlanError:
        report.add("error", "runtime-plan", "The external container runtime plan is absent or malformed.")
        return None
    report.facts["component"] = plan.component.id
    report.add("pass", "runtime-plan", "External runtime plan is readable and structurally valid.")
    return plan


def _inspect_process_authorization(report: _ReportBuilder) -> None:
    if os.geteuid() == 0:
        report.add("error", "identity", "Recursive dogfood must run as the mapped unprivileged user.")
    else:
        report.add("pass", "identity", "Process is running as an unprivileged user.")
    group_names: set[str] = set()
    for group_id in os.getgroups():
        try:
            group_names.add(grp.getgrgid(group_id).gr_name)
        except KeyError:
            continue
    if "host-docker" in group_names:
        report.add("pass", "docker-authorization", "Host-Docker group authorization is present.")
    else:
        report.add(
            "warning",
            "docker-authorization",
            "The named host-Docker group is absent; socket access will be validated directly.",
        )
    if "ide-sudo" in group_names:
        report.add("pass", "development-sudo", "Optional development-sudo authorization is present.")
    else:
        report.add("warning", "development-sudo", "Optional development-sudo authorization is absent.")


def _inspect_docker_socket(report: _ReportBuilder, env: Mapping[str, str]) -> str | None:
    try:
        path = docker_socket_path(env.get("DOCKER_HOST"))
    except PreflightError as exc:
        report.add("error", "docker-socket", str(exc))
        return None
    try:
        mode = path.stat().st_mode
    except OSError:
        report.add("error", "docker-socket", "The selected Docker socket is missing or inaccessible.")
        return None
    if not stat.S_ISSOCK(mode):
        report.add("error", "docker-socket", "The selected DOCKER_HOST path is not a unix socket.")
        return None
    if shutil.which("docker") is None:
        report.add("error", "docker-cli", "The Docker CLI is not installed in this container.")
        return None
    version = _command(["docker", "version", "--format", "{{json .}}"], env=env)
    try:
        version_value = json.loads(version.stdout)
        client = version_value["Client"]["Version"]
        server = version_value["Server"]["Version"]
        if not isinstance(client, str) or not client or not isinstance(server, str) or not server:
            raise KeyError("Version")
    except (json.JSONDecodeError, KeyError, TypeError):
        report.add("error", "docker-daemon", "Docker client/server version negotiation failed.")
        return None
    report.facts["docker_socket"] = str(path)
    report.facts["docker_versions"] = f"client {client}; server {server}"
    report.add("pass", "docker-socket", "Explicit authorized Docker socket is present.")
    report.add("pass", "docker-daemon", "Docker client reached the authorized host daemon.")
    return env["DOCKER_HOST"]


def _inspect_current_container(
    report: _ReportBuilder,
    env: Mapping[str, str],
    docker_host: str | None,
) -> ContainerInspection | None:
    if docker_host is None:
        return None
    declared_name = env.get(CONTAINER_NAME_ENV)
    if declared_name is not None:
        try:
            validate_container_name(declared_name)
        except PreflightError as exc:
            report.add("error", "container-identity", str(exc))
            return None
        result = _command(["docker", "container", "inspect", declared_name], env=env)
    else:
        listed = _command(
            ["docker", "container", "list", "--quiet", "--filter", "status=running"], env=env
        )
        identifiers = listed.stdout.split() if listed.returncode == 0 else []
        if not identifiers:
            report.add(
                "error", "container-identity", "The host daemon returned no inspectable running containers."
            )
            return None
        result = _command(["docker", "container", "inspect", *identifiers], env=env)
    if result.returncode != 0:
        report.add("error", "container-identity", "The host daemon rejected container inspection.")
        return None
    try:
        raw = json.loads(result.stdout)
        if not isinstance(raw, list) or not raw:
            raise PreflightError("Docker returned an empty container inspection set")
        inspections = tuple(parse_container_inspection(item) for item in raw)
        return identify_current_container(
            inspections,
            expected_name=declared_name,
            self_upper_directory=_self_overlay_upper_directory(),
        )
    except (json.JSONDecodeError, PreflightError):
        report.add(
            "error",
            "container-identity",
            "Current container identity is malformed, absent, ambiguous, or mismatched at the host daemon.",
        )
        return None


def _inspect_required_mounts(
    report: _ReportBuilder,
    *,
    checkout_root: Path,
    runtime_plan_path: Path,
    runtime_plan: RuntimePlan,
    container: ContainerInspection,
    env: Mapping[str, str],
) -> None:
    requirements = (
        ("checkout-mount", checkout_root, True, "bind"),
        ("persistent-home", Path(runtime_plan.home), True, "bind"),
        ("runtime-plan-mount", runtime_plan_path, False, "bind"),
        ("x11-mount", X11_SOCKET_DIRECTORY, False, "bind"),
    )
    for check, path, writable, kind in requirements:
        try:
            selected = covering_mount(path, container.mounts, require_writable=writable)
            if selected.kind != kind:
                raise PreflightError(f"container path {path} must use a {kind} mount")
            if check in {"runtime-plan-mount", "x11-mount"} and selected.writable:
                raise PreflightError(f"security-sensitive container path {path} must be read-only")
        except PreflightError as exc:
            report.add("error", check, str(exc))
        else:
            report.add("pass", check, "Required mount mapping and access mode are valid.")

    configured_home = env.get("HOME")
    if configured_home != runtime_plan.home:
        report.add("error", "home", "HOME does not match the runtime plan's persistent-home path.")
    elif not Path(runtime_plan.home).is_dir() or not os.access(
        runtime_plan.home, os.W_OK | os.X_OK
    ):
        report.add("error", "home", "Persistent home is not writable by the runtime user.")
    else:
        report.add("pass", "home", "HOME matches the runtime plan's persistent-home path.")

    try:
        workspace = safe_child(Path(runtime_plan.home), WORKSPACE_RELATIVE_PATH)
        selected = covering_mount(workspace, container.mounts, require_writable=True)
        if selected.kind != "bind":
            raise PreflightError("recursive workspace must be backed by a host bind mount")
    except PreflightError as exc:
        report.add("error", "workspace", str(exc))
    else:
        report.facts["workspace"] = str(workspace)
        report.add("pass", "workspace", "Future E2E workspace is contained by writable persistent home.")

    display = env.get("DISPLAY")
    xauthority = env.get("XAUTHORITY")
    if not display:
        report.add("error", "display", "DISPLAY is not configured for successor IDE validation.")
    elif not X11_SOCKET_DIRECTORY.is_dir():
        report.add("error", "display", "The X11 socket directory is absent.")
    else:
        report.add("pass", "display", "Display and X11 socket forwarding are configured.")
    if not xauthority:
        report.add("error", "display-authorization", "Xauthority is not configured.")
    else:
        selected_xauthority = Path(xauthority)
        if not selected_xauthority.is_absolute() or ".." in selected_xauthority.parts:
            report.add("error", "display-authorization", "Xauthority path is not absolute and normalized.")
        elif not selected_xauthority.is_file() or not os.access(selected_xauthority, os.R_OK):
            report.add("error", "display-authorization", "Xauthority material is absent or unreadable.")
        else:
            try:
                mount = covering_mount(selected_xauthority, container.mounts, require_writable=False)
                if mount.kind != "bind" or mount.writable:
                    raise PreflightError("Xauthority material must use a read-only bind mount")
            except PreflightError as exc:
                report.add("error", "display-authorization", str(exc))
            else:
                report.add("pass", "display-authorization", "Xauthority is readable through a read-only bind.")

    if container.source_revision:
        running_revision = current_build_info().source_revision
        if running_revision == container.source_revision:
            report.add("pass", "image-revision", "Running distribution matches the container image revision.")
        else:
            report.add(
                "warning",
                "image-revision",
                "Running source distribution differs from the container image; this is allowed only for bootstrap.",
            )
    else:
        report.add("warning", "image-revision", "Container image has no source-revision label to compare.")


def _inspect_disk(report: _ReportBuilder, home: Path) -> None:
    try:
        free = shutil.disk_usage(home).free
    except OSError:
        report.add("error", "disk", "Cannot inspect free space on persistent home.")
        return
    report.facts["persistent_home_free"] = _format_bytes(free)
    if free < MINIMUM_RECOMMENDED_FREE_BYTES:
        report.add(
            "warning",
            "disk",
            "Persistent home has less than the recommended 20 GiB free for recursive image builds.",
        )
    else:
        report.add("pass", "disk", "Persistent home has at least the recommended 20 GiB free.")


def _parse_mount(value: object) -> Mount:
    if not isinstance(value, dict):
        raise PreflightError("Docker inspection contains a malformed mount")
    source = value.get("Source")
    destination = value.get("Destination")
    kind = value.get("Type")
    writable = value.get("RW")
    if not isinstance(source, str) or not source:
        raise PreflightError("Docker inspection contains a mount without a source")
    if not isinstance(destination, str) or not _normalized_absolute(destination):
        raise PreflightError("Docker inspection contains a non-normalized mount destination")
    if not isinstance(kind, str) or not kind:
        raise PreflightError("Docker inspection contains a mount without a type")
    if not isinstance(writable, bool):
        raise PreflightError("Docker inspection contains a mount without an access mode")
    return Mount(source, destination, kind, writable)


def _reject_duplicate_destinations(mounts: Sequence[Mount]) -> None:
    destinations: set[str] = set()
    for item in mounts:
        if item.destination in destinations:
            raise PreflightError(f"Docker inspection has an ambiguous mount at {item.destination}")
        destinations.add(item.destination)


def _normalized_absolute(value: str) -> bool:
    path = PurePosixPath(value)
    return path.is_absolute() and ".." not in path.parts and str(path) == value


def _self_overlay_upper_directory(path: Path = Path("/proc/self/mountinfo")) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        before, separator, after = line.partition(" - ")
        fields = before.split()
        filesystem = after.split()
        if not separator or len(fields) < 6 or len(filesystem) < 3 or fields[4] != "/":
            continue
        if filesystem[0] != "overlay":
            return None
        match = re.search(r"(?:^|,)upperdir=([^,]+)", filesystem[2])
        return _mountinfo_unescape(match.group(1)) if match else None
    return None


def _mountinfo_unescape(value: str) -> str:
    replacements = {r"\040": " ", r"\011": "\t", r"\012": "\n", r"\134": "\\"}
    for escaped, plain in replacements.items():
        value = value.replace(escaped, plain)
    return value


def _display_destination(value: str) -> str:
    if value == "/tmp/.docker.xauth":
        return "<display-authorization>"
    return value


def _format_bytes(value: int) -> str:
    return f"{value / 1024**3:.1f} GiB"


def _running_from_pex() -> bool:
    selected = Path(sys.argv[0]).expanduser()
    return selected.is_file() and zipfile.is_zipfile(selected)


def _command(
    args: Sequence[str], *, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=None if env is None else dict(env),
    )
