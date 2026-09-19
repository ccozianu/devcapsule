"""Workstream mail on the coordination branch.

Intake items travel a single shared branch, ``coordination`` by default, that
lives on the remote and is never merged into the integration branch. Its
history is append-only: a sender adds one file under ``mail/<recipient>/``,
a recipient deletes only its own files after copying them into its intake
directory, and nobody ever resets or force-pushes the branch. A push that
loses a race is retried from a fresh fetch; racing commits touch different
files, so the retry never conflicts.

Everything here works through git plumbing on the remote-tracking ref. The
current branch and the working tree are never switched or dirtied, except
that ``take`` writes the received items into the recipient's intake
directory and stages them, which is the whole point of taking.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


COORDINATION_BRANCH = "coordination"
MAIL_ROOT = "mail"
DEFAULT_ATTEMPTS = 5
WORKSTREAM_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ITEM_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
FILE_MODE = "100644"
TREE_MODE = "040000"
README_PATH = "README.md"
README_TEXT = """# Coordination Branch

This branch carries workstream mail: intake items in flight between
workstreams. It is never merged into the integration branch, and its history
is append-only. A sender adds one file under `mail/<recipient>/`; the
recipient deletes only its own files after copying them into its intake
directory; nobody resets or force-pushes this branch.

Read and write it with `devcapsule workflow mail check|send|take`, or with
plain git: `git fetch origin coordination` and
`git show origin/coordination:mail/<name>/`. See *The Coordination Branch* in
`WORKFLOW.md`.
"""


class WorkflowMailError(Exception):
    """A mail operation could not be completed as asked."""


@dataclass(frozen=True)
class MailItem:
    recipient: str
    name: str
    blob: str

    @property
    def path(self) -> str:
        return f"{MAIL_ROOT}/{self.recipient}/{self.name}"


class _Git:
    """The few git invocations this module needs, run in one repository."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def run(self, *args: str, stdin: str | None = None) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.root,
            input=stdin,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise WorkflowMailError(
                f"git {' '.join(args)} failed: {completed.stderr.strip() or completed.stdout.strip()}"
            )
        return completed.stdout

    def attempt(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)


def send(
    root: Path,
    recipient: str,
    item: Path,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    attempts: int = DEFAULT_ATTEMPTS,
) -> str:
    """Deliver ``item`` to ``recipient``; return the commit that carries it.

    Delivering an item that is already on the branch with identical content
    is a no-op that returns the current tip. Delivering a different file
    under a name already in flight is refused: senders never rewrite mail.
    """
    _require_name(recipient, "recipient")
    if not item.is_file():
        raise WorkflowMailError(f"{item} is not a file")
    if ITEM_NAME.match(item.name) is None:
        raise WorkflowMailError(
            f"{item.name!r} is not an item name of the form YYYY-MM-DD-<sender>-<slug>.md"
        )
    git = _Git(root)
    blob = git.run("hash-object", "-w", str(item)).strip()
    destination = f"{MAIL_ROOT}/{recipient}/{item.name}"
    for _ in range(attempts):
        tip = _fetch_tip(git, remote, branch)
        entries = _tree_entries(git, tip) if tip else {README_PATH: _readme_blob(git)}
        existing = entries.get(destination)
        if existing == blob:
            return tip or ""
        if existing is not None:
            raise WorkflowMailError(
                f"{destination} is already in flight with different content; "
                "senders never rewrite mail, so choose another item name"
            )
        entries[destination] = blob
        commit = _commit(git, entries, tip, f"mail: {recipient} <- {item.name}")
        if _push(git, remote, branch, commit, tip):
            return commit
    raise WorkflowMailError(
        f"could not push to {remote}/{branch} after {attempts} attempts; the branch keeps moving"
    )


def check(
    root: Path, name: str, *, remote: str = "origin", branch: str = COORDINATION_BRANCH
) -> list[MailItem]:
    """The items waiting for workstream ``name``, after a fresh fetch."""
    _require_name(name, "workstream name")
    git = _Git(root)
    tip = _fetch_tip(git, remote, branch)
    if tip is None:
        return []
    return _items_for(_tree_entries(git, tip), name)


def take(
    root: Path,
    name: str,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    attempts: int = DEFAULT_ATTEMPTS,
) -> list[Path]:
    """Copy the items waiting for ``name`` into its intake directory, stage
    them, then remove them from the branch. Returns the files written.

    The local copies are written and staged before the branch is touched, so
    a push that fails after every retry leaves the mail in place and the
    copies on disk; taking again is idempotent.
    """
    _require_name(name, "workstream name")
    git = _Git(root)
    tip = _fetch_tip(git, remote, branch)
    if tip is None:
        return []
    items = _items_for(_tree_entries(git, tip), name)
    if not items:
        return []
    intake = _intake_directory(root, name)
    written: list[Path] = []
    for item in items:
        content = git.run("cat-file", "-p", item.blob)
        destination = intake / item.name
        if destination.exists() and destination.read_text(encoding="utf-8") != content:
            raise WorkflowMailError(
                f"{destination} exists with different content; resolve that before taking"
            )
        destination.write_text(content, encoding="utf-8")
        git.run("add", "--", str(destination))
        written.append(destination)
    taken = {item.path for item in items}
    for _ in range(attempts):
        entries = _tree_entries(git, tip)
        for path in taken:
            entries.pop(path, None)
        commit = _commit(git, entries, tip, f"mail: {name} took {len(taken)} item(s)")
        if _push(git, remote, branch, commit, tip):
            return written
        tip = _fetch_tip(git, remote, branch)
        if tip is None:
            raise WorkflowMailError(f"{remote}/{branch} disappeared while taking mail")
    raise WorkflowMailError(
        f"copied {len(written)} item(s) into {intake} but could not remove them from "
        f"{remote}/{branch} after {attempts} attempts; take again"
    )


def current_workstream_name(root: Path) -> str | None:
    """The workstream a checkout is on, read from a ``ws-<name>/...`` branch."""
    completed = _Git(root).attempt("symbolic-ref", "--short", "HEAD")
    if completed.returncode != 0:
        return None
    current = completed.stdout.strip()
    if not current.startswith("ws-") or "/" not in current:
        return None
    return current[len("ws-") :].split("/", 1)[0]


def _require_name(value: str, what: str) -> None:
    if WORKSTREAM_NAME.match(value) is None:
        raise WorkflowMailError(f"{value!r} is not a valid {what}: lowercase letters, digits, hyphens")


def _fetch_tip(git: _Git, remote: str, branch: str) -> str | None:
    """Fetch the branch and return its tip, or ``None`` when it does not exist
    on the remote yet."""
    completed = git.attempt(
        "fetch", "--quiet", remote, f"+refs/heads/{branch}:refs/remotes/{remote}/{branch}"
    )
    if completed.returncode != 0:
        # Ask for the exact ref: a bare pattern such as "coordination" would
        # also match "ws-<name>/coordination", and a fetch failure would then
        # be misread as an existing branch.
        listed = git.attempt("ls-remote", "--exit-code", remote, f"refs/heads/{branch}")
        if listed.returncode == 2:
            return None
        raise WorkflowMailError(f"fetching {remote}/{branch} failed: {completed.stderr.strip()}")
    return git.run("rev-parse", f"refs/remotes/{remote}/{branch}").strip()


def _tree_entries(git: _Git, commit: str) -> dict[str, str]:
    """Every blob in the commit's tree, as path -> blob sha."""
    entries: dict[str, str] = {}
    for line in git.run("ls-tree", "-r", "-z", commit).split("\0"):
        if not line:
            continue
        meta, _, path = line.partition("\t")
        _mode, kind, sha = meta.split(" ")
        if kind == "blob":
            entries[path] = sha
    return entries


def _items_for(entries: dict[str, str], name: str) -> list[MailItem]:
    prefix = f"{MAIL_ROOT}/{name}/"
    return sorted(
        (MailItem(name, path[len(prefix) :], blob) for path, blob in entries.items()
         if path.startswith(prefix) and "/" not in path[len(prefix) :]),
        key=lambda item: item.name,
    )


def _readme_blob(git: _Git) -> str:
    return git.run("hash-object", "-w", "--stdin", stdin=README_TEXT).strip()


def _commit(git: _Git, entries: dict[str, str], parent: str | None, message: str) -> str:
    tree = _mktree(git, entries)
    args = ["commit-tree", tree, "-m", message]
    if parent is not None:
        args += ["-p", parent]
    return git.run(*args).strip()


def _mktree(git: _Git, entries: dict[str, str]) -> str:
    """Write nested trees for flat path -> blob entries; return the root tree."""
    files: list[str] = []
    subtrees: dict[str, dict[str, str]] = {}
    for path, blob in entries.items():
        head, _, tail = path.partition("/")
        if tail:
            subtrees.setdefault(head, {})[tail] = blob
        else:
            files.append(f"{FILE_MODE} blob {blob}\t{head}")
    for directory, children in subtrees.items():
        files.append(f"{TREE_MODE} tree {_mktree(git, children)}\t{directory}")
    return git.run("mktree", stdin="\n".join(files) + "\n").strip()


def _push(git: _Git, remote: str, branch: str, commit: str, expected: str | None) -> bool:
    """Push ``commit`` as the branch tip if the remote still holds ``expected``
    (or nothing, when the branch is being created). ``False`` means the branch
    moved and the caller should refetch and retry; other failures raise."""
    lease = f"--force-with-lease=refs/heads/{branch}:{expected or ''}"
    completed = git.attempt("push", "--quiet", lease, remote, f"{commit}:refs/heads/{branch}")
    if completed.returncode == 0:
        return True
    stderr = completed.stderr
    if "stale info" in stderr or "rejected" in stderr:
        return False
    raise WorkflowMailError(f"pushing to {remote}/{branch} failed: {stderr.strip()}")


def _intake_directory(root: Path, name: str) -> Path:
    candidates = sorted((root / "engineering-docs" / "wip").glob(f"????-??-??-{name}"))
    if len(candidates) != 1:
        raise WorkflowMailError(
            f"expected exactly one open-work directory for {name!r} under engineering-docs/wip, "
            f"found {len(candidates)}"
        )
    intake = candidates[0] / "intake"
    intake.mkdir(exist_ok=True)
    return intake
