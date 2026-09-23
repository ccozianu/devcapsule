#!/usr/bin/env python3
"""Run RC0 CLI checks or record a real project session. Python 3.11+, stdlib only."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import uuid

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[3]
DEFAULT_PEX = REPOSITORY / "devcapsule-src/dist/rc0-published/devcapsule.pex"
RUNS = REPOSITORY / "devcapsule-src/dist/rc0-runs"
RC0_SHA = "2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513"
ENV_NAMES = ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME",
             "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def capture(argv: list[str], env: dict | None = None) -> str:
    result = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def save(directory: Path, record: dict) -> None:
    # A reader sees the old or new complete record, never half a JSON document.
    temporary = directory / "run.json.tmp"
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(directory / "run.json")


@contextmanager
def locked(directory: Path):
    with (directory / "run.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("This run already has an active runner; no concurrent mutation allowed") from error
        yield


def read(directory: Path) -> dict:
    record = json.loads((directory / "run.json").read_text())
    if record.get("schema") != 1 or record.get("candidate_sha256") != RC0_SHA:
        raise ValueError("Not a session record from this RC0 runner")
    return record


def verify_pex(path: Path) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != RC0_SHA:
        raise ValueError("Executable is not the published RC0; it was not started")


def project_facts(project: Path) -> dict:
    declaration = project / ".devcapsule/devcapsule.toml"
    if not declaration.is_file():
        raise ValueError("--project must name the project root containing .devcapsule/devcapsule.toml")
    facts = {"path": str(project), "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((project / ".devcapsule").glob("*")) if p.is_file()}}
    try:
        facts["revision"] = capture(["git", "-C", str(project), "rev-parse", "HEAD"])
        facts["changes"] = capture(["git", "-C", str(project), "status", "--porcelain"])
        diff = capture(["git", "-C", str(project), "diff", "HEAD", "--binary"])
        facts["tracked_diff_sha256"] = hashlib.sha256(diff.encode()).hexdigest()
    except RuntimeError:
        facts["revision"] = None  # An initialized project need not use Git.
    return facts


def container_id(name: str, env: dict) -> str:
    # A Docker error raises; it is not evidence that the container is absent.
    return capture(["docker", "container", "ls", "--all", "--no-trunc", "--filter",
                    f"name=^/{name}$", "--format", "{{.ID}}"], env)


def inspect_container(identifier: str, env: dict) -> dict:
    data = json.loads(capture(["docker", "inspect", identifier], env))[0]
    # Do not save Config.Env: it may contain credentials/session tokens.
    return {"id": data["Id"], "image_id": data["Image"], "image": data["Config"]["Image"],
            "user": data["Config"]["User"], "running": data["State"]["Running"],
            "network": data["HostConfig"]["NetworkMode"],
            "privileged": data["HostConfig"]["Privileged"],
            "readonly_root": data["HostConfig"]["ReadonlyRootfs"],
            "mounts": [{key: mount.get(key) for key in ("Type", "Source", "Destination", "RW")}
                       for mount in data["Mounts"]]}


def environment(record: dict) -> dict:
    env = dict(os.environ)
    env.pop("DEVCAPSULE_RUNTIME_PEX", None)
    for key, value in record["environment"].items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return env


def session(directory: Path, record: dict) -> int:
    pex, project = Path(record["pex"]), Path(record["project"])
    verify_pex(pex)
    if record["host_home"] != str(Path.home()):
        raise ValueError("Resume must use the original host home; default state paths would otherwise change")
    env = environment(record)
    daemon = capture(["docker", "info", "--format", "{{.ID}}"], env)
    if record.get("docker_daemon") not in (None, daemon):
        raise ValueError("Docker daemon changed; resume would use different images/containers")
    record["docker_daemon"] = daemon
    if container_id(record["container_name"], env):
        raise ValueError("The previous session's container still exists; resume refused")
    attempt = {"number": len(record["sessions"]) + 1, "started": now(), "status": "RUNNING",
               "before": project_facts(project), "container": None, "monitor_errors": []}
    record["sessions"].append(attempt)
    save(directory, record)
    stop = threading.Event()

    def monitor() -> None:
        # Collect one real container observation; leave IDE interaction to its actor.
        while not stop.is_set():
            try:
                identifier = container_id(record["container_name"], env)
                if identifier:
                    observation = inspect_container(identifier, env)
                    if observation["running"]:
                        attempt["container"] = observation
                        save(directory, record)
                        return
            except Exception as error:
                attempt["monitor_errors"].append(str(error))
                save(directory, record)
                return
            stop.wait(2)

    command = [str(pex), "project", "--path", str(project), "run", "--name", record["container_name"]]
    attempt["command"] = command
    print(f"Run record: {directory}\nStarting ordinary project run. Exit the IDE normally when finished.", flush=True)
    print("The desktop URL stays in your terminal; it is not copied into the report.", flush=True)
    watcher = threading.Thread(target=monitor, daemon=True)
    watcher.start()
    process = None
    code = 1
    try:
        # Inherit the terminal so ordinary product prompts and browser URLs work unchanged.
        # No preview first; no silent config regeneration; no update-check bypass.
        process = subprocess.Popen(command, env=env)
        try:
            code = process.wait()
        except KeyboardInterrupt:
            attempt["interrupted"] = True
            process.send_signal(signal.SIGINT)
            try:
                code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    code = process.wait()
            # Interruption is not a successful normal-exit check even if child returns zero.
            code = code or 130
        attempt["launcher_exit"] = code
    except Exception as error:
        attempt["error"] = str(error)
        code = 1
    finally:
        stop.set()
        watcher.join(timeout=45)
        if watcher.is_alive():
            attempt["monitor_errors"].append("Container observer did not stop within its deadline")
        attempt["ended"] = now()
        try:
            attempt["container_absent_after_exit"] = not bool(container_id(record["container_name"], env))
        except Exception as error:
            attempt["container_absent_after_exit"] = None
            attempt["monitor_errors"].append(str(error))
        try:
            attempt["after"] = project_facts(project)
        except Exception as error:
            attempt["snapshot_error"] = str(error)
        passed = (code == 0 and attempt["container"] is not None
                  and attempt["container_absent_after_exit"] is True
                  and not attempt["monitor_errors"] and not attempt.get("snapshot_error"))
        attempt["status"] = "PROCESS_CHECKS_PASSED" if passed else "NEEDS_REVIEW"
        save(directory, record)
    report(directory, record)
    return 0 if passed else 1


def report(directory: Path, record: dict) -> None:
    print(f"\nProject: {record['project']}\nCandidate: v0.2.14-rc0 (checksum verified)")
    for item in record["sessions"]:
        print(f"Session {item['number']}: {item['status']}; exit={item.get('launcher_exit', 'unknown')}; "
              f"container gone={item.get('container_absent_after_exit', 'unknown')}")
    print("Recorded observations:")
    for item in record["observations"]:
        print(f"  {item['story']} / session {item['session']}: {item['outcome']} by {item['actor']} — {item['text']}")
    if not record["observations"]:
        print("  None. Process checks do not certify that the IDE or application worked.")
    print(f"Evidence: {directory / 'run.json'}")
    print(f"Resume: {sys.executable} {HERE / 'runner.py'} resume {directory}")


def main() -> int:
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    launch = commands.add_parser("launch", help="Run an existing configured project and collect session facts")
    launch.add_argument("--project", type=Path, required=True)
    launch.add_argument("--pex", type=Path, default=DEFAULT_PEX)
    launch.add_argument("--output", type=Path, help="New evidence directory; defaults to dist/rc0-runs")
    launch.add_argument("--state-from", type=Path, help="Use XDG state from a prepared smoke directory")
    for action in ("resume", "report", "note"):
        command = commands.add_parser(action)
        command.add_argument("run", type=Path)
        if action == "note":
            command.add_argument("--story", required=True, choices=[f"S{i:02}" for i in range(21)])
            command.add_argument("--session", type=int, required=True)
            command.add_argument("--outcome", choices=("PASS", "FAIL", "BLOCKED"), required=True)
            command.add_argument("--actor", choices=("human", "desktop-agent", "test-agent"), required=True)
            command.add_argument("--text", required=True, help="Observed action/result, with no URLs or credentials")
    cli = commands.add_parser("cli", help="Prepare and execute the automated CLI stories")
    cli.add_argument("--run", type=Path, help="An existing 00-prepare.sh directory")
    cli.add_argument("--pex", type=Path, default=DEFAULT_PEX)
    args = parser.parse_args()
    if args.action == "cli":
        if args.run is None:
            RUNS.mkdir(parents=True, exist_ok=True)
            args.run = RUNS / ("cli-" + uuid.uuid4().hex[:12])
            subprocess.run(["bash", str(HERE / "00-prepare.sh"), "--cli-only", str(args.run),
                            str(args.pex.resolve())], check=True)
        return subprocess.call([sys.executable, str(HERE / "verify-cli.py"), str(args.run.resolve())])
    if args.action == "launch":
        project, pex = args.project.resolve(), args.pex.resolve()
        verify_pex(pex)
        project_facts(project)
        identifier = uuid.uuid4().hex[:12]
        directory = args.output.resolve() if args.output else RUNS / ("session-" + identifier)
        directory.mkdir(parents=True, exist_ok=False)
        selected_env = {key: os.environ.get(key) for key in ENV_NAMES}
        if args.state_from:
            root = args.state_from.resolve()
            if (root / ".rc0-smoke").read_text().strip() != "v0.2.14-rc0":
                raise ValueError("--state-from must name a prepared RC0 smoke directory")
            for kind in ("CONFIG", "DATA", "STATE", "CACHE"):
                selected_env[f"XDG_{kind}_HOME"] = str(root / "xdg" / kind.lower())
        record = {"schema": 1, "created": now(), "candidate_sha256": RC0_SHA,
                  "pex": str(pex), "project": str(project), "environment": selected_env,
                  "host_home": str(Path.home()),
                  "container_name": "rc0-runner-" + identifier, "sessions": [], "observations": []}
        with locked(directory):
            save(directory, record)
            return session(directory, record)
    directory = args.run.resolve()
    if args.action == "report":
        report(directory, read(directory))
        return 0
    with locked(directory):
        return existing_action(args, directory)


def existing_action(args, directory: Path) -> int:
    record = read(directory)
    if args.action == "resume":
        if any(item["status"] == "RUNNING" for item in record["sessions"]):
            raise ValueError("A session record is still RUNNING; inspect the interrupted run before resuming")
        return session(directory, record)
    if args.action == "note":
        if any(item["status"] == "RUNNING" for item in record["sessions"]):
            raise ValueError("Record observations after the runner has finished, to avoid concurrent record writes")
        if not 1 <= args.session <= len(record["sessions"]):
            raise ValueError("No such session in this run")
        record["observations"].append({"at": now(), "session": args.session, "story": args.story,
                                       "actor": args.actor, "outcome": args.outcome, "text": args.text})
        save(directory, record)
    report(directory, record)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Runner failed: {error}", file=sys.stderr)
        raise SystemExit(1)
