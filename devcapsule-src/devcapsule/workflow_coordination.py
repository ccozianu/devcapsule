"""The coordination branch: workstream mail and live workstream state.

One shared branch, ``coordination`` by default, lives on the remote and is
never merged into the integration branch. It carries two things:

- ``mail/<recipient>/<item>.md``: intake items in flight. A sender adds one
  file; the recipient deletes only its own files after copying them into its
  intake directory.
- ``state/<name>/``: the live copy of each open workstream's status file and
  decision log, pushed by the workstream itself from its working branch. The
  copies on ``main`` are the record as of the last integration; these are
  the truth while the workstream is open.

The branch's history is append-only in the sense that matters: nobody resets
or force-pushes it, and every change is an ordinary commit on top. A push
that loses a race is retried from a fresh fetch; racing commits touch
different files, so the retry never conflicts.

Everything here works through git plumbing on the remote-tracking ref. The
current branch and the working tree are never switched or dirtied, except
that ``take`` writes the received items into the recipient's intake
directory and stages them, which is the whole point of taking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import subprocess


COORDINATION_BRANCH = "coordination"
MAIL_ROOT = "mail"
STATE_ROOT = "state"
STATE_FILES = ("CURRENT-STATUS.md", "intake-dispositions.md")
DEFINITION_FILES = ("WORKFLOW.md", "WORKFLOW-LOCAL.md")
CLAIM_FILE = "claim"
DEFAULT_CLAIM_HOURS = 12
DEFINITION_READ_KEY = "Definition read"
ALL_RECIPIENTS = "all"
DEFAULT_ATTEMPTS = 5
WORKSTREAM_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ITEM_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
FILE_MODE = "100644"
TREE_MODE = "040000"
README_PATH = "README.md"
README_TEXT = """# Coordination Branch

This branch carries the workflow's live coordination state and is never
merged into the integration branch. Nobody resets or force-pushes it.

- `mail/<recipient>/`: intake items in flight. A sender adds one file; the
  recipient deletes only its own files after copying them into its intake
  directory.
- `state/<name>/`: the live copy of each open workstream's status file and
  decision log, pushed by that workstream from its working branch, and its
  claim: who is working on it, on what, until when. While a workstream is
  open this is the truth; the copies on the integration branch
  are the record as of its last integration.

Read and write it with `devcapsule workflow brief`, `status`, `claim`,
`publish`, and `mail check|send|take`, or with plain git: `git fetch origin coordination` and `git show origin/coordination:<path>`.
See *The Coordination Branch* in `WORKFLOW.md`.
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
    if not item.is_file():
        raise WorkflowMailError(f"{item} is not a file")
    if ITEM_NAME.match(item.name) is None:
        raise WorkflowMailError(
            f"{item.name!r} is not an item name of the form YYYY-MM-DD-<sender>-<slug>.md"
        )
    git = _Git(root)
    blob = git.run("hash-object", "-w", str(item)).strip()
    for _ in range(attempts):
        tip = _fetch_tip(git, remote, branch)
        entries = _tree_entries(git, tip) if tip else {README_PATH: _readme_blob(git)}
        recipients = _recipients(recipient, entries)
        changed = False
        for name in recipients:
            destination = f"{MAIL_ROOT}/{name}/{item.name}"
            existing = entries.get(destination)
            if existing == blob:
                continue
            if existing is not None:
                raise WorkflowMailError(
                    f"{destination} is already in flight with different content; "
                    "senders never rewrite mail, so choose another item name"
                )
            entries[destination] = blob
            changed = True
        if not changed:
            return tip or ""
        label = recipient if len(recipients) == 1 else f"{len(recipients)} workstreams"
        commit = _commit(git, entries, tip, f"mail: {label} <- {item.name}")
        if _push(git, remote, branch, commit, tip):
            return commit
    raise WorkflowMailError(
        f"could not push to {remote}/{branch} after {attempts} attempts; the branch keeps moving"
    )


def _recipients(recipient: str, entries: dict[str, str]) -> list[str]:
    """One workstream name, a comma-separated list, or ``all``: every
    workstream with published state, which is the live list."""
    if recipient == ALL_RECIPIENTS:
        owners = [owner for owner in (_state_owner(path) for path in entries) if owner]
        if not owners:
            raise WorkflowMailError("no workstream has published state; nothing to send to")
        return sorted(set(owners))
    names = [part.strip() for part in recipient.split(",") if part.strip()]
    for name in names:
        _require_name(name, "recipient")
    if not names:
        raise WorkflowMailError("no recipient given")
    return names


def _state_owner(path: str) -> str | None:
    head, _, rest = path.partition("/")
    if head != STATE_ROOT or not rest.endswith("/" + STATE_FILES[0]):
        return None
    name = rest[: -len("/" + STATE_FILES[0])]
    return None if "/" in name else name


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


@dataclass(frozen=True)
class Claim:
    """A soft claim: who is working on a workstream, where, on what, and until
    when. It informs and never refuses; an expired claim is shown as such."""

    who: str
    branch: str
    slice: str
    since: datetime
    expires: datetime

    def expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) >= self.expires

    def render(self) -> str:
        lines = [f"who: {self.who}", f"branch: {self.branch}", f"slice: {self.slice}",
                 f"since: {self.since.isoformat(timespec='seconds')}",
                 f"expires: {self.expires.isoformat(timespec='seconds')}"]
        return "\n".join(lines) + "\n"

    @classmethod
    def parse(cls, text: str) -> "Claim | None":
        fields: dict[str, str] = {}
        for line in text.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip()] = value.strip()
        try:
            return cls(
                fields["who"], fields["branch"], fields["slice"],
                datetime.fromisoformat(fields["since"]), datetime.fromisoformat(fields["expires"]),
            )
        except (KeyError, ValueError):
            return None


@dataclass(frozen=True)
class WorkstreamState:
    """One workstream's live row, read from its published status file, with
    the facts the session-start synchronization judgment needs, its claim,
    and when it last published."""

    name: str
    state: str
    branch: str
    next_step: str
    behind_main: int | None = None
    """Commits on the integration branch that the workstream's branch lacks;
    ``None`` when the branch is not on the remote."""
    definition_changed: bool | None = None
    """Whether the integration branch has moved the definition or the local
    workflow file past what the status file says was last read: the files
    differ from the stamp and changed on the integration branch since the
    workstream's branch diverged from it. A workstream that is itself editing
    the definition is not flagged. ``None`` when there is no stamp."""
    claim: Claim | None = None
    published: datetime | None = None
    """When the status file was last published, from the branch's history."""


def claim(
    root: Path,
    name: str,
    slice_: str | None,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    hours: float = DEFAULT_CLAIM_HOURS,
    release: bool = False,
    now: datetime | None = None,
    attempts: int = DEFAULT_ATTEMPTS,
) -> str | None:
    """Write, replace, or with ``release`` remove ``state/<name>/claim``.

    A claim names the git user, the checkout's current branch, the slice, and
    an expiry ``hours`` from now. Returns the commit made, or ``None`` when
    the branch already held exactly this claim (or, releasing, none).
    """
    _require_name(name, "workstream name")
    git = _Git(root)
    path = f"{STATE_ROOT}/{name}/{CLAIM_FILE}"
    wanted: str | None = None
    if not release:
        if not slice_:
            raise WorkflowMailError("a claim needs a slice: what you are working on")
        who = git.attempt("config", "user.name").stdout.strip() or "unknown"
        current = git.attempt("symbolic-ref", "--short", "HEAD").stdout.strip() or "(detached)"
        start = now or datetime.now(timezone.utc)
        wanted = git.run(
            "hash-object", "-w", "--stdin",
            stdin=Claim(who, current, slice_, start, start + timedelta(hours=hours)).render(),
        ).strip()
    for _ in range(attempts):
        tip = _fetch_tip(git, remote, branch)
        entries = _tree_entries(git, tip) if tip else {README_PATH: _readme_blob(git)}
        if entries.get(path) == wanted:
            return None
        if wanted is None:
            entries.pop(path, None)
        else:
            entries[path] = wanted
        verb = "released" if release else "claimed"
        commit = _commit(git, entries, tip, f"claim: {name} {verb}")
        if _push(git, remote, branch, commit, tip):
            return commit
    raise WorkflowMailError(
        f"could not push to {remote}/{branch} after {attempts} attempts; the branch keeps moving"
    )


def publish(
    root: Path,
    name: str,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    retire: bool = False,
    attempts: int = DEFAULT_ATTEMPTS,
) -> str | None:
    """Push the working tree's copies of ``name``'s records to
    ``state/<name>/``, or remove that directory when ``retire`` is set.

    Returns the commit made, or ``None`` when the branch already held exactly
    these contents. The copies are taken from the working tree, so what is
    published is what the pair is looking at, committed or not.
    """
    _require_name(name, "workstream name")
    git = _Git(root)
    wanted: dict[str, str] = {}
    if not retire:
        directory = _workstream_directory(root, name)
        status = directory / STATE_FILES[0]
        if not status.is_file():
            raise WorkflowMailError(f"{status} does not exist; nothing to publish")
        _stamp_definition_read(git, status)
        for file_name in STATE_FILES:
            source = directory / file_name
            if source.is_file():
                wanted[f"{STATE_ROOT}/{name}/{file_name}"] = git.run(
                    "hash-object", "-w", str(source)
                ).strip()
    prefix = f"{STATE_ROOT}/{name}/"
    for _ in range(attempts):
        tip = _fetch_tip(git, remote, branch)
        entries = _tree_entries(git, tip) if tip else {README_PATH: _readme_blob(git)}
        current = {path: blob for path, blob in entries.items() if path.startswith(prefix)}
        if current == wanted:
            return None
        for path in current:
            del entries[path]
        entries.update(wanted)
        verb = "retired" if retire else "published"
        commit = _commit(git, entries, tip, f"state: {name} {verb}")
        if _push(git, remote, branch, commit, tip):
            return commit
    raise WorkflowMailError(
        f"could not push to {remote}/{branch} after {attempts} attempts; the branch keeps moving"
    )


def _definition_blobs(git: _Git, revision: str) -> dict[str, str]:
    """Blob ids of the definition files at ``revision``; absent files are
    left out, so a project without a local file still stamps cleanly."""
    blobs: dict[str, str] = {}
    for file_name in DEFINITION_FILES:
        completed = git.attempt("rev-parse", "--verify", "--quiet", f"{revision}:{file_name}")
        if completed.returncode == 0:
            blobs[file_name] = completed.stdout.strip()[:12]
    return blobs


def _stamp_definition_read(git: _Git, status: Path) -> None:
    """Write ``Definition read: WORKFLOW.md@<blob>, ...`` into the status
    file, from the checkout's HEAD, which is what the pair has read.
    Inserted after the ``State:`` line on first use, replaced afterwards."""
    blobs = _definition_blobs(git, "HEAD")
    if not blobs:
        return
    stamp = f"{DEFINITION_READ_KEY}: " + ", ".join(f"{k}@{v}" for k, v in blobs.items())
    lines = status.read_text(encoding="utf-8").split("\n")
    for index, line in enumerate(lines):
        if line.startswith(DEFINITION_READ_KEY + ":"):
            if line == stamp:
                return
            lines[index] = stamp
            break
    else:
        # After the State paragraph, which may wrap over several lines: the
        # first blank line following the "State:" line, or the title if there
        # is no State line.
        anchor = next((i for i, line in enumerate(lines) if line.startswith("State:")), None)
        if anchor is None:
            lines[1:1] = ["", stamp]
        else:
            end = next((i for i in range(anchor, len(lines)) if not lines[i].strip()), len(lines))
            lines[end:end] = ["", stamp]
    status.write_text("\n".join(lines), encoding="utf-8")


def _parse_stamp(text: str) -> dict[str, str] | None:
    for line in text.splitlines():
        if line.startswith(DEFINITION_READ_KEY + ":"):
            stamped: dict[str, str] = {}
            for part in line.partition(":")[2].split(","):
                file_name, _, blob = part.strip().partition("@")
                if file_name and blob:
                    stamped[file_name] = blob
            return stamped
    return None


def list_state(
    root: Path,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    integration_branch: str = "main",
) -> list[WorkstreamState]:
    """Every workstream with a published status file, read live from the
    remote, in name order, with how far its branch is behind the integration
    branch and whether the definition changed since it last read it."""
    git = _Git(root)
    tip = _fetch_tip(git, remote, branch)
    if tip is None:
        return []
    git.attempt("fetch", "--quiet", remote)
    main_ref = f"refs/remotes/{remote}/{integration_branch}"
    current_definition = _definition_blobs(git, main_ref)
    rows: list[WorkstreamState] = []
    for path, blob in sorted(_tree_entries(git, tip).items()):
        name = _state_owner(path)
        if name is None:
            continue
        text = git.run("cat-file", "-p", blob)
        parsed = _parse_status(name, text)
        stamped = _parse_stamp(text)
        branch_ref = _branch_ref(git, remote, parsed.branch)
        changed: bool | None
        if stamped is None:
            changed = None
        else:
            differs = any(current_definition.get(k) != v for k, v in stamped.items()) or any(
                k not in stamped for k in current_definition
            )
            changed = differs and _main_moved_definition(git, branch_ref, main_ref)
        claim_blob = _tree_entries(git, tip).get(f"{STATE_ROOT}/{name}/{CLAIM_FILE}")
        found = Claim.parse(git.run("cat-file", "-p", claim_blob)) if claim_blob else None
        rows.append(
            WorkstreamState(
                parsed.name,
                parsed.state,
                parsed.branch,
                parsed.next_step,
                _behind(git, branch_ref, main_ref),
                changed,
                found,
                _published_at(git, tip, path),
            )
        )
    return rows


def _published_at(git: _Git, tip: str, path: str) -> datetime | None:
    completed = git.attempt("log", "-1", "--format=%cI", tip, "--", path)
    stamp = completed.stdout.strip()
    if completed.returncode != 0 or not stamp:
        return None
    return datetime.fromisoformat(stamp)


def _ago(then: datetime, now: datetime | None = None) -> str:
    delta = (now or datetime.now(timezone.utc)) - then
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 48:
        return f"{hours} h ago"
    return f"{hours // 24} days ago"


def _branch_ref(git: _Git, remote: str, association: str) -> str | None:
    """The remote-tracking ref of the first ``ws-`` branch the association
    names, when the remote has it."""
    match = re.search(r"`(ws-[^`\s]+)`", association)
    if match is None:
        return None
    ref = f"refs/remotes/{remote}/{match.group(1)}"
    return ref if git.attempt("rev-parse", "--verify", "--quiet", ref).returncode == 0 else None


def _main_moved_definition(git: _Git, branch_ref: str | None, main_ref: str) -> bool:
    """Whether the integration branch changed a definition file since the
    workstream's branch diverged from it. Without a branch to compare, any
    difference counts."""
    if branch_ref is None:
        return True
    base = git.attempt("merge-base", branch_ref, main_ref)
    if base.returncode != 0:
        return True
    diff = git.attempt("diff", "--quiet", base.stdout.strip(), main_ref, "--", *DEFINITION_FILES)
    return diff.returncode != 0


def _behind(git: _Git, branch_ref: str | None, main_ref: str) -> int | None:
    """Commits on the integration branch that the workstream's branch lacks,
    or ``None`` when the branch is not on the remote."""
    if branch_ref is None:
        return None
    completed = git.attempt("rev-list", "--count", f"{branch_ref}..{main_ref}")
    if completed.returncode != 0:
        return None
    return int(completed.stdout.strip() or 0)


def _parse_status(name: str, text: str) -> WorkstreamState:
    """What a status file says about itself: the ``State:`` line, the branch
    association (a ``Branch association:`` line, or the first paragraph under
    a *Branch Association* heading), and the first paragraph under *Planned
    Next Step* or *Next Resumable Task*. Wrapped lines are joined."""
    state = branch = next_step = ""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        key, _, value = line.partition(":")
        if key.strip() == "State" and not state:
            state = value.strip()
        elif key.strip() == "Branch association" and not branch:
            branch = value.strip()
        elif line.startswith("## "):
            heading = line[3:].strip()
            if heading == "Branch Association" and not branch:
                branch = _first_paragraph(lines, index + 1)
            elif heading in ("Planned Next Step", "Next Resumable Task") and not next_step:
                next_step = _first_paragraph(lines, index + 1)
    return WorkstreamState(name, state, branch, next_step)


def _first_paragraph(lines: list[str], start: int) -> str:
    collected: list[str] = []
    for line in lines[start:]:
        if line.strip():
            collected.append(line.strip())
        elif collected:
            break
    return " ".join(collected)


def render_list(rows: list[WorkstreamState]) -> str:
    if not rows:
        return "no published workstream state\n"
    width = max(len(row.name) for row in rows)
    out = []
    for row in rows:
        out.append(f"{row.name:<{width}}  {row.state}")
        facts = []
        if row.behind_main is not None:
            facts.append(f"behind main: {row.behind_main}")
        if row.definition_changed is None:
            facts.append("definition: never stamped")
        elif row.definition_changed:
            facts.append("definition: CHANGED since last read")
        else:
            facts.append("definition: current")
        if row.published is not None:
            facts.append(f"published {_ago(row.published)}")
        out.append(f"{'':<{width}}  branch: {row.branch}")
        out.append(f"{'':<{width}}  {'; '.join(facts)}")
        if row.claim is not None:
            state = "EXPIRED" if row.claim.expired() else f"since {_ago(row.claim.since)}"
            out.append(
                f"{'':<{width}}  claimed by {row.claim.who} on {row.claim.branch}: "
                f"{row.claim.slice} ({state})"
            )
        if row.next_step:
            out.append(f"{'':<{width}}  next: {row.next_step}")
    return "\n".join(out) + "\n"


def brief(
    root: Path,
    name: str,
    *,
    remote: str = "origin",
    branch: str = COORDINATION_BRANCH,
    integration_branch: str = "main",
) -> str:
    """Everything a session needs before acting, for one workstream: its
    row, who else is working on what, its mail, the definition changes it
    has not read, and the synchronization facts with a suggested verdict.
    The judgment stays the agent's; this prints the facts and nothing more."""
    _require_name(name, "workstream name")
    rows = list_state(root, remote=remote, branch=branch, integration_branch=integration_branch)
    mine = next((row for row in rows if row.name == name), None)
    out: list[str] = [f"# {name}"]
    if mine is None:
        out.append("not published: run `devcapsule workflow publish` so others can see this workstream")
    else:
        out.append(f"state: {mine.state}")
        out.append(f"branch: {mine.branch}")
        if mine.next_step:
            out.append(f"next: {mine.next_step}")
    others = [row for row in rows if row.name != name and row.claim and not row.claim.expired()]
    out.append("")
    out.append("## Who is working on what")
    if others:
        for row in others:
            assert row.claim is not None
            out.append(f"- {row.name}: {row.claim.who} on {row.claim.branch}, {row.claim.slice}")
    else:
        out.append("- nobody has a live claim")
    waiting = check(root, name, remote=remote, branch=branch)
    out.append("")
    out.append(f"## Mail: {len(waiting)} waiting" + ("" if waiting else ", nothing to take"))
    for item in waiting:
        out.append(f"- {item.name}")
    git = _Git(root)
    unread = _unread_changes(git, mine, f"refs/remotes/{remote}/{integration_branch}") if mine else []
    out.append("")
    out.append("## Definition changes not yet read" if unread else "## Definition: nothing new since last read")
    for line in unread:
        out.append(f"- {line}")
    out.append("")
    out.append("## Synchronization facts")
    if mine is None or mine.behind_main is None:
        out.append("- branch not on the remote, or not published; distance unknown")
    else:
        out.append(f"- behind {integration_branch}: {mine.behind_main}")
    if mine is not None and mine.definition_changed:
        verdict = "must synchronize: the definition or local workflow file changed"
    elif mine is not None and mine.behind_main:
        verdict = "should synchronize if the task touches files main changed; otherwise may defer, recording why"
    else:
        verdict = "nothing to synchronize"
    out.append(f"- suggested: {verdict}")
    return "\n".join(out) + "\n"


def _unread_changes(git: _Git, row: WorkstreamState, main_ref: str) -> list[str]:
    """Titles of *Changes* bullets in the integration branch's definition that
    the stamped copy lacks: what this workstream has not read."""
    completed = git.attempt("rev-parse", "--verify", "--quiet", f"{main_ref}:{DEFINITION_FILES[0]}")
    if completed.returncode != 0:
        return []
    current = git.run("cat-file", "-p", completed.stdout.strip())
    stamp = _parse_stamp_from_state(git, row.name)
    if stamp is None or DEFINITION_FILES[0] not in stamp:
        return _change_titles(current)
    old = git.attempt("cat-file", "-p", stamp[DEFINITION_FILES[0]])
    seen = set(_change_titles(old.stdout)) if old.returncode == 0 else set()
    return [title for title in _change_titles(current) if title not in seen]


def _parse_stamp_from_state(git: _Git, name: str) -> dict[str, str] | None:
    tip = git.attempt("rev-parse", f"refs/remotes/origin/{COORDINATION_BRANCH}").stdout.strip()
    if not tip:
        return None
    blob = _tree_entries(git, tip).get(f"{STATE_ROOT}/{name}/{STATE_FILES[0]}")
    return _parse_stamp(git.run("cat-file", "-p", blob)) if blob else None


def _change_titles(text: str) -> list[str]:
    """The bold titles of the bullets under the *Changes* section."""
    titles: list[str] = []
    in_changes = False
    for line in text.splitlines():
        if line.startswith("### "):
            in_changes = line.strip() == "### Changes"
            continue
        if in_changes and line.startswith("## "):
            break
        if in_changes and line.startswith("- **"):
            end = line.find("**", 4)
            if end > 4:
                titles.append(line[4:end])
    return titles


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


def _workstream_directory(root: Path, name: str) -> Path:
    candidates = sorted((root / "engineering-docs" / "wip").glob(f"????-??-??-{name}"))
    if len(candidates) != 1:
        raise WorkflowMailError(
            f"expected exactly one open-work directory for {name!r} under engineering-docs/wip, "
            f"found {len(candidates)}"
        )
    return candidates[0]


def _intake_directory(root: Path, name: str) -> Path:
    intake = _workstream_directory(root, name) / "intake"
    intake.mkdir(exist_ok=True)
    return intake
