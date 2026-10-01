#!/usr/bin/env python3
"""Execute S02, S03 and S17 against published RC0; no Docker/GUI/provider needed.

Usage: python3 verify-cli.py RUN_DIRECTORY [--stories init|coordination|all]
RUN_DIRECTORY is produced by 00-prepare.sh. Python 3.11+ is a harness dependency.
Only public CLI processes are used: no imports from DevCapsule's implementation.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import pty
import re
import select
import signal
import subprocess
import tempfile
import time
import tomllib

SHA = "2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513"
BASE = "docker.io/mycodespaceai/devcapsule-base@sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c"
CREATOR = "mailto:smoke@example.invalid"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


class Run:
    def __init__(self, root: Path):
        self.pex = root / "bin/devcapsule.pex"
        require(hashlib.sha256(self.pex.read_bytes()).hexdigest() == SHA, "Wrong candidate bytes")
        self.attempt = Path(tempfile.mkdtemp(prefix="cli-", dir=root / "evidence"))
        self.sequence = 0
        self.results: list[dict] = []
        self.env = dict(os.environ)
        self.env.pop("DEVCAPSULE_RUNTIME_PEX", None)
        self.env.update(LC_ALL="C", GIT_TERMINAL_PROMPT="0")

    def environment(self, directory: Path) -> dict[str, str]:
        env = dict(self.env)
        for kind in ("CONFIG", "DATA", "STATE", "CACHE"):
            env[f"XDG_{kind}_HOME"] = str(directory / "xdg" / kind.lower())
        return env

    def command(self, *argv: str, cwd: Path | None = None, env: dict | None = None,
                expected: int | None = 0) -> subprocess.CompletedProcess:
        self.sequence += 1
        prefix = self.attempt / f"{self.sequence:03d}"
        (prefix.with_suffix(".command.json")).write_text(json.dumps(
            {"argv": list(argv), "cwd": str(cwd) if cwd else None}, indent=2) + "\n")
        try:
            result = subprocess.run(argv, cwd=cwd, env=env or self.env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, timeout=90)
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b""
            prefix.with_suffix(".log").write_text(
                output.decode(errors="replace") if isinstance(output, bytes) else output)
            prefix.with_suffix(".exit").write_text("TIMEOUT\n")
            raise TimeoutError(f"Command exceeded 90 seconds: see {prefix}.log") from error
        prefix.with_suffix(".log").write_text(result.stdout)
        prefix.with_suffix(".exit").write_text(str(result.returncode) + "\n")
        if expected is not None:
            require(result.returncode == expected,
                    f"Exit {result.returncode}, expected {expected}: see {prefix}.log")
        return result

    def dc(self, project: Path, env: dict, *args: str, expected: int | None = 0):
        return self.command(str(self.pex), "project", "--path", str(project), *args,
                            env=env, expected=expected)

    def story(self, name: str, action) -> None:
        started = time.monotonic()
        result = {"story": name, "actor": "runner", "status": "FAIL"}
        try:
            result["outputs"] = action()
            result["status"] = "PASS"
        except Exception as error:
            result["error"] = str(error)
            raise
        finally:
            result["seconds"] = round(time.monotonic() - started, 3)
            self.results.append(result)
            (self.attempt / "results.json").write_text(json.dumps({
                "candidate_sha256": SHA, "stories": self.results}, indent=2) + "\n")
            print(f"{name}: {result['status']} ({self.attempt})", flush=True)


def terminal_init(run: Run, directory: Path, *, decline: bool = False) -> Path:
    project = directory / "project"
    project.mkdir(parents=True)
    env = run.environment(directory)
    questions = [
        (r"Project creator \(URL or email address\): $", "smoke@example.invalid"),
        (r"Select the default agent component \(antigravity-agent\)\? \(yes/no\) \[yes\]: $", "no"),
        (r"Recommend docker-daemon = host-socket for every checkout\? \(host-socket/none\) \[none\]: $", "none"),
        (r"Recommend network = host for every checkout\? \(host/none\) \[none\]: $", "none"),
        (r"Recommend development-sudo = true for every checkout\? \(true/none\) \[none\]: $", "none"),
        (r"Recommend host-browser = true for every checkout\? \(true/none\) \[none\]: $", "none"),
        (r"Authorize this checkout to execute [^\r\n]+\? \(Enter accepts; 'no' declines; or name a locally built/pulled image\) \[default\]: $", "no" if decline else "default"),
    ]
    argv = [str(run.pex), "project", "--path", str(project), "init",
            "--need", "frontend-ide", "--need", "node"]
    (directory / "command.json").write_text(json.dumps(argv) + "\n")
    master, slave = pty.openpty()
    process = subprocess.Popen(argv, stdin=slave, stdout=slave, stderr=slave, env=env,
                               start_new_session=True)
    os.close(slave)
    pending = ""
    answered = []
    deadline = time.monotonic() + 45
    transcript = directory / "terminal.log"
    try:
        with transcript.open("wb") as output:
            while True:
                if time.monotonic() > deadline:
                    raise TimeoutError(f"Unknown/missing prompt or hung init; see {transcript}")
                readable, _, _ = select.select([master], [], [], 0.2)
                if not readable:
                    if process.poll() is not None:
                        break
                    continue
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise
                if not chunk:
                    break
                output.write(chunk)
                output.flush()
                pending += chunk.decode(errors="replace").replace("\r", "")
                if questions and re.search(questions[0][0], pending):
                    pattern, answer = questions.pop(0)
                    if pattern.startswith("Authorize"):
                        # Do not authorize a different artifact because its question looks familiar.
                        require(BASE in pending, "Base prompt does not name the pinned expected digest")
                    os.write(master, (answer + "\n").encode())
                    answered.append({"question": pattern, "answer": answer})
                    pending = ""
            code = process.wait(timeout=5)
            require(not questions, f"Missing expected prompts: {questions}; see {transcript}")
            require(code == (2 if decline else 0), f"Unexpected init exit {code}; see {transcript}")
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        os.close(master)
        (directory / "answers.json").write_text(json.dumps(answered, indent=2) + "\n")
    return project


def configuration(run: Run, directory: Path, project: Path) -> dict:
    manifest = read_toml(project / ".devcapsule/devcapsule.toml")
    lock = read_toml(project / ".devcapsule/devcapsule.linux-amd64.lock")
    records = list((directory / "xdg/config").rglob("devcapsule.checkout.toml"))
    require(len(records) == 1, f"Expected one checkout record, found {records}")
    record = read_toml(records[0])
    require(manifest["project"]["creator"] == CREATOR, "Creator answer not saved")
    require(set(manifest["capabilities"]["need"]) == {"frontend-ide", "node"}, "Agent was added or needs lost")
    require(not manifest.get("host"), "Declined recommendations were authored")
    require(lock["base"]["reference"] == BASE, "Unexpected base selected")
    authorizations = record["authorization"]
    require(set(authorizations) == {"base-image", "docker-daemon", "development-sudo", "host-browser"},
            "Unexpected authorization names")
    require(authorizations["docker-daemon"]["value"] == "none", "Docker denial lost")
    require(authorizations["development-sudo"]["value"] is False, "Sudo denial lost")
    require(authorizations["host-browser"]["value"] is False, "Browser denial lost")
    require(record["authorization"]["base-image"]["reference"] == BASE, "Wrong base grant")
    require(record["checkout"]["path"] == str(project), "Wrong checkout registered")
    env = run.environment(directory)
    result = run.dc(project, env, "config", "list")
    require("fresh" in result.stdout, "Init did not finish with a fresh resolution")
    resolution = records[0].with_name("devcapsule.resolved.toml")
    require(resolution.is_file(), "Resolution is absent")
    run.dc(project, env, "config", "resolve")
    return {"need": sorted(manifest["capabilities"]["need"]), "host": manifest.get("host", {}),
            "base": lock["base"]["reference"], "authorization": record["authorization"]}


def prompts(run: Run) -> dict:
    accepted = run.attempt / "S02-accepted"
    project = terminal_init(run, accepted)
    choices = configuration(run, accepted, project)
    (accepted / "choices.json").write_text(json.dumps(choices, indent=2) + "\n")
    declined = run.attempt / "S02-declined"
    terminal_init(run, declined, decline=True)
    require("declined" in (declined / "terminal.log").read_text(), "Missing decline diagnostic")
    for record in declined.rglob("devcapsule.checkout.toml"):
        require("base-image" not in read_toml(record).get("authorization", {}), "Decline recorded a grant")
    require(not list(declined.rglob("devcapsule.resolved.toml")), "Declined init produced a resolution")
    return {"accepted_project": str(project), "state": str(accepted / "xdg"),
            "declined_fixture": str(declined), "choices": choices}


def batch(run: Run) -> dict:
    directory = run.attempt / "S03"
    project = directory / "project"
    project.mkdir(parents=True)
    env = run.environment(directory)
    args = ("init", "--need", "frontend-ide", "--need", "node", "--creator", CREATOR,
            "--authorize", "docker-daemon", "none", "--authorize", "development-sudo", "false",
            "--authorize", "host-browser", "false")
    missing = run.dc(project, env, *args, expected=None)
    require(missing.returncode == 2 and "--authorize base-image" in missing.stdout,
            "Missing base choice did not fail with its remedy")
    require(not list(directory.rglob("devcapsule.resolved.toml")), "Missing choice silently resolved")
    run.dc(project, env, *args, "--authorize", "base-image", "default")
    choices = configuration(run, directory, project)
    prompted = json.loads((run.attempt / "S02-accepted/choices.json").read_text())
    require(choices == prompted, "Prompted and noninteractive choices differ")
    return {"project": str(project), "choices_equal_S02": True}


def coordination(run: Run) -> dict:
    directory = run.attempt / "S17"
    directory.mkdir()
    env = run.environment(directory)
    # Test identity/hooks/signing are local to these disposable repositories.
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    def git(where: Path, *args: str) -> str:
        return run.command("git", "-C", str(where), *args, env=env).stdout.strip()
    origin = directory / "origin.git"
    run.command("git", "init", "--quiet", "--bare", "--initial-branch=main", str(origin), env=env)
    clones = {}
    for name in ("alpha", "beta"):
        where = directory / name
        run.command("git", "clone", "--quiet", str(origin), str(where), env=env)
        git(where, "config", "user.name", "Smoke test")
        git(where, "config", "user.email", "smoke@example.invalid")
        if name == "alpha":
            (where / "README.md").write_text("Disposable coordination validation\n")
            git(where, "add", ".")
            git(where, "commit", "--quiet", "-m", "seed")
            git(where, "push", "--quiet", "origin", "HEAD:main")
        git(where, "checkout", "--quiet", "-b", f"ws-{name}/smoke")
        work = where / "engineering-docs/wip" / f"2026-09-23-{name}"
        (work / "intake").mkdir(parents=True)
        (work / "CURRENT-STATUS.md").write_text(f"# {name}\n\nState: active\n\n## Planned Next Step\n\nTest coordination.\n")
        (work / "intake-dispositions.md").write_text("# Decisions\n\nNo items yet.\n")
        (where / "nested/deeper").mkdir(parents=True)
        clones[name] = where
    alpha = clones["alpha"]
    # Seed recognizable unrelated blobs, including a valid claim from an actual CLI call below.
    git(alpha, "checkout", "--orphan", "coordination")
    git(alpha, "rm", "-rf", "--ignore-unmatch", ".")
    seeds = {"mail/other/2026-09-23-other-unrelated.md": b"unrelated mail\x00bytes\n",
             "state/other/CURRENT-STATUS.md": b"other workstream status\n",
             "state/other/intake-dispositions.md": b"other decisions\n"}
    for name, data in seeds.items():
        path = alpha / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    git(alpha, "add", "mail", "state")
    git(alpha, "commit", "--quiet", "-m", "seed unrelated coordination files")
    git(alpha, "push", "--quiet", "origin", "coordination")
    git(alpha, "checkout", "--quiet", "ws-alpha/smoke")
    def snapshot() -> dict[str, str]:
        output = git(origin, "ls-tree", "-r", "coordination")
        return {line.split("\t", 1)[1]: line.split("\t", 1)[0] for line in output.splitlines()}
    comparisons = []
    def operation(actor: str, args: list[str], changes: set[str], *, relative: bool = True):
        before = snapshot()
        tip = git(origin, "rev-parse", "coordination")
        where = clones[actor]
        result = run.command(str(run.pex), "workflow", *args, "--project", "../.." if relative else str(where),
                             cwd=where / "nested/deeper", env=env)
        after = snapshot()
        changed = {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
        require(changed == changes, f"{args}: changed {changed}, expected {changes}")
        git(origin, "merge-base", "--is-ancestor", tip, "coordination")
        comparisons.append({"args": args, "changed": sorted(changed), "before": before, "after": after})
        (directory / "comparisons.json").write_text(json.dumps(comparisons, indent=2) + "\n")
        return result
    operation("alpha", ["claim", "unrelated claim", "--workstream", "other"], {"state/other/claim"})
    claim = "state/alpha/claim"
    operation("alpha", ["claim", "test byte preservation"], {claim})
    status_paths = {"state/alpha/CURRENT-STATUS.md", "state/alpha/intake-dispositions.md"}
    operation("alpha", ["publish"], status_paths)
    visible = operation("beta", ["status"], set())
    require("test byte preservation" in visible.stdout, "Live claim not visible from other checkout")
    item = directory / "2026-09-23-alpha-hello.md"
    payload = "# Test mail\n\nPreserve these exact bytes: café.\n"
    item.write_text(payload)
    mail = "mail/beta/" + item.name
    operation("alpha", ["mail", "send", "beta", str(item)], {mail}, relative=False)
    operation("alpha", ["mail", "send", "beta", str(item)], set())
    operation("alpha", ["claim", "--release"], {claim})
    operation("beta", ["mail", "take"], {mail})
    taken = clones["beta"] / "engineering-docs/wip/2026-09-23-beta/intake" / item.name
    require(taken.read_bytes() == item.read_bytes(), "Taken mail bytes changed")
    staged = git(clones["beta"], "rev-parse", ":" + str(taken.relative_to(clones["beta"])))
    require(staged == git(clones["beta"], "hash-object", str(item)), "Staged mail bytes changed")
    operation("beta", ["mail", "take"], set())
    require(git(alpha, "branch", "--show-current") == "ws-alpha/smoke", "Sender branch changed")
    return {"remote": str(origin), "operations": len(comparisons), "comparisons": str(directory / "comparisons.json")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--stories", choices=("init", "coordination", "all"), default="all")
    args = parser.parse_args()
    run = Run(args.root.resolve())
    failures = 0
    if args.stories in ("init", "all"):
        try:
            run.story("S02", lambda: prompts(run))
        except Exception as error:
            print(error)
            run.results.append({"story": "S03", "status": "BLOCKED", "reason": "S02 failed"})
            failures += 1
        else:
            try:
                run.story("S03", lambda: batch(run))
            except Exception as error:
                print(error)
                failures += 1
    if args.stories in ("coordination", "all"):
        try:
            run.story("S17", lambda: coordination(run))
        except Exception as error:
            print(error)
            failures += 1
    (run.attempt / "results.json").write_text(json.dumps({
        "candidate_sha256": SHA, "stories": run.results}, indent=2) + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
