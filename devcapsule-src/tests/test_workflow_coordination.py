from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from devcapsule import cli, workflow_coordination as workflow_mail
from devcapsule.workflow_coordination import (
    WorkflowMailError,
    check,
    list_state,
    publish,
    send,
    take,
)


def git(root: Path, *args: str, stdin: str | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, input=stdin, capture_output=True, text=True, check=True
    ).stdout


def clone(origin: Path, where: Path, name: str, branch: str) -> Path:
    """A checkout on ws-<name>/<branch> with an open-work directory for ``name``."""
    git(origin.parent, "clone", "--quiet", str(origin), str(where))
    git(where, "config", "user.name", name)
    git(where, "config", "user.email", f"{name}@example.invalid")
    git(where, "checkout", "--quiet", "-b", f"ws-{name}/{branch}")
    intake = where / "engineering-docs" / "wip" / f"2026-09-19-{name}" / "intake"
    intake.mkdir(parents=True)
    return where


@pytest.fixture
def repos(tmp_path: Path) -> tuple[Path, Path, Path]:
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--quiet", "--bare", str(origin))
    seed = tmp_path / "seed"
    git(tmp_path, "clone", "--quiet", str(origin), str(seed))
    git(seed, "config", "user.name", "seed")
    git(seed, "config", "user.email", "seed@example.invalid")
    (seed / "README.md").write_text("# project\n", encoding="utf-8")
    git(seed, "add", "README.md")
    git(seed, "commit", "--quiet", "-m", "seed")
    git(seed, "push", "--quiet", "origin", "HEAD:main")
    # A branch whose last path component equals the coordination branch's
    # name must not be mistaken for it when the real branch does not exist.
    git(seed, "push", "--quiet", "origin", "HEAD:refs/heads/ws-gamma/coordination")
    sender = clone(origin, tmp_path / "sender", "alpha", "v1")
    recipient = clone(origin, tmp_path / "recipient", "beta", "v1")
    return origin, sender, recipient


def item(root: Path, name: str, text: str = "# Intake: hello\n") -> Path:
    """An item file written beside the checkout, not inside it, so sending
    leaves the sender's working tree clean."""
    outbox = root.parent / f"{root.name}-items"
    outbox.mkdir(exist_ok=True)
    path = outbox / name
    path.write_text(text, encoding="utf-8")
    return path


def test_send_creates_the_branch_and_check_sees_the_item(repos) -> None:
    origin, sender, recipient = repos

    commit = send(sender, "beta", item(sender, "2026-09-19-alpha-hello.md"))

    assert git(origin, "rev-parse", "refs/heads/coordination").strip() == commit
    tree = git(origin, "ls-tree", "-r", "--name-only", "coordination").split()
    assert tree == ["README.md", "mail/beta/2026-09-19-alpha-hello.md"]
    waiting = check(recipient, "beta")
    assert [entry.name for entry in waiting] == ["2026-09-19-alpha-hello.md"]
    assert check(recipient, "alpha") == []
    # The sender's own checkout is untouched: same branch, clean tree.
    assert git(sender, "symbolic-ref", "--short", "HEAD").strip() == "ws-alpha/v1"
    assert git(sender, "status", "--porcelain").strip() == ""


def test_take_copies_into_intake_stages_and_removes_from_branch(repos) -> None:
    origin, sender, recipient = repos
    send(sender, "beta", item(sender, "2026-09-19-alpha-one.md", "one\n"))
    send(sender, "beta", item(sender, "2026-09-19-alpha-two.md", "two\n"))

    written = take(recipient, "beta")

    intake = recipient / "engineering-docs/wip/2026-09-19-beta/intake"
    assert sorted(path.name for path in written) == [
        "2026-09-19-alpha-one.md",
        "2026-09-19-alpha-two.md",
    ]
    assert (intake / "2026-09-19-alpha-one.md").read_text(encoding="utf-8") == "one\n"
    staged = git(recipient, "diff", "--cached", "--name-only").split()
    assert len(staged) == 2 and all("intake/" in path for path in staged)
    assert git(origin, "ls-tree", "-r", "--name-only", "coordination").split() == ["README.md"]
    assert check(recipient, "beta") == []
    assert take(recipient, "beta") == []
    # History is append-only: the take is a commit on top of the sends, not a reset.
    assert len(git(origin, "rev-list", "coordination").split()) == 3


def test_send_is_idempotent_for_identical_content_and_refuses_rewrites(repos) -> None:
    _origin, sender, _recipient = repos
    path = item(sender, "2026-09-19-alpha-same.md", "same\n")
    first = send(sender, "beta", path)

    assert send(sender, "beta", path) == first
    path.write_text("changed\n", encoding="utf-8")
    with pytest.raises(WorkflowMailError, match="never rewrite"):
        send(sender, "beta", path)


def test_send_retries_after_losing_a_push_race(repos, monkeypatch) -> None:
    _origin, sender, recipient = repos
    send(recipient, "alpha", item(recipient, "2026-09-19-beta-first.md"))
    real_push = workflow_mail._push
    raced = {"done": False}

    def racing_push(git_, remote, branch, commit, expected):
        # Somebody else lands a commit between our fetch and our push, once.
        if not raced["done"]:
            raced["done"] = True
            send(recipient, "alpha", item(recipient, "2026-09-19-beta-second.md"))
        return real_push(git_, remote, branch, commit, expected)

    monkeypatch.setattr(workflow_mail, "_push", racing_push)

    send(sender, "beta", item(sender, "2026-09-19-alpha-late.md"))

    names = [entry.name for entry in check(sender, "alpha")]
    assert names == ["2026-09-19-beta-first.md", "2026-09-19-beta-second.md"]
    assert [entry.name for entry in check(sender, "beta")] == ["2026-09-19-alpha-late.md"]


def test_names_are_validated(repos) -> None:
    _origin, sender, _recipient = repos
    with pytest.raises(WorkflowMailError, match="not a valid recipient"):
        send(sender, "Beta/../x", item(sender, "2026-09-19-alpha-x.md"))
    with pytest.raises(WorkflowMailError, match="item name"):
        send(sender, "beta", item(sender, "notes.md"))
    with pytest.raises(WorkflowMailError, match="not a valid workstream name"):
        check(sender, "../beta")


def test_cli_infers_the_workstream_from_the_branch(repos, capsys) -> None:
    _origin, sender, recipient = repos
    sent = item(sender, "2026-09-19-alpha-cli.md")

    assert cli.main(["workflow", "mail", "send", "--project", str(sender), "beta", str(sent)]) == 0
    assert "delivered 2026-09-19-alpha-cli.md to beta" in capsys.readouterr().out
    assert cli.main(["workflow", "mail", "check", "--project", str(recipient)]) == 0
    assert "1 item(s) for beta" in capsys.readouterr().out
    assert cli.main(["workflow", "mail", "take", "--project", str(recipient)]) == 0
    assert "took 1 item(s)" in capsys.readouterr().out
    assert cli.main(["workflow", "mail", "check", "--project", str(recipient)]) == 0
    assert "no mail for beta" in capsys.readouterr().out


def status_file(root: Path, name: str, state: str, next_step: str) -> Path:
    path = root / "engineering-docs" / "wip" / f"2026-09-19-{name}" / "CURRENT-STATUS.md"
    path.write_text(
        f"# Workstream Current Status: {name}\n\nName: `{name}`\n\nState: {state}\n\n"
        f"Branch association: `ws-{name}/v1`\n\n## Planned Next Step\n\n{next_step}\n",
        encoding="utf-8",
    )
    return path


def test_publish_pushes_live_state_and_list_reads_it(repos) -> None:
    origin, sender, recipient = repos
    status_file(sender, "alpha", "active", "Ship the thing.")
    (sender / "engineering-docs/wip/2026-09-19-alpha/intake-dispositions.md").write_text(
        "| Item |\n", encoding="utf-8"
    )
    status_file(recipient, "beta", "paused 2026-09-19; waiting", "Resume after alpha ships.")

    first = publish(sender, "alpha")
    assert first is not None
    assert publish(sender, "alpha") is None  # nothing changed: no commit
    publish(recipient, "beta")

    tree = git(origin, "ls-tree", "-r", "--name-only", "coordination").split()
    assert "state/alpha/CURRENT-STATUS.md" in tree
    assert "state/alpha/intake-dispositions.md" in tree
    assert "state/beta/CURRENT-STATUS.md" in tree
    rows = list_state(recipient)
    assert [(row.name, row.state, row.branch) for row in rows] == [
        ("alpha", "active", "`ws-alpha/v1`"),
        ("beta", "paused 2026-09-19; waiting", "`ws-beta/v1`"),
    ]
    assert rows[0].next_step == "Ship the thing."
    # Publishing reads the working tree: an uncommitted edit is what goes live.
    status_file(sender, "alpha", "blocked; needs beta", "Wait.")
    publish(sender, "alpha")
    assert list_state(sender)[0].state == "blocked; needs beta"
    # The sender's checkout is untouched beyond its own files.
    assert git(sender, "symbolic-ref", "--short", "HEAD").strip() == "ws-alpha/v1"


def test_retire_removes_published_state_and_mail_survives(repos) -> None:
    origin, sender, recipient = repos
    status_file(sender, "alpha", "active", "x")
    publish(sender, "alpha")
    send(recipient, "alpha", item(recipient, "2026-09-19-beta-note.md"))

    assert publish(sender, "alpha", retire=True) is not None
    assert publish(sender, "alpha", retire=True) is None

    tree = git(origin, "ls-tree", "-r", "--name-only", "coordination").split()
    assert tree == ["README.md", "mail/alpha/2026-09-19-beta-note.md"]
    assert list_state(sender) == []


def test_publish_requires_a_status_file(repos) -> None:
    _origin, sender, _recipient = repos
    with pytest.raises(WorkflowMailError, match="nothing to publish"):
        publish(sender, "alpha")


def test_cli_publish_and_list(repos, capsys) -> None:
    _origin, sender, recipient = repos
    status_file(sender, "alpha", "active", "Do it.")

    assert cli.main(["workflow", "publish", "--project", str(sender)]) == 0
    assert "alpha: published to coordination" in capsys.readouterr().out
    assert cli.main(["workflow", "list", "--project", str(recipient)]) == 0
    out = capsys.readouterr().out
    assert "alpha  active" in out and "next: Do it." in out
    assert cli.main(["workflow", "publish", "--project", str(sender), "--retire"]) == 0
    assert "retired" in capsys.readouterr().out


def test_list_reads_headed_branch_association_and_joins_wrapped_paragraphs(repos) -> None:
    _origin, sender, _recipient = repos
    path = sender / "engineering-docs/wip/2026-09-19-alpha/CURRENT-STATUS.md"
    path.write_text(
        "# Status\n\nState: active\n\n## Branch Association\n\n`ws-alpha/v2`, forked\n"
        "from `main`.\n\n## Next Resumable Task\n\nFinish the first\nslice.\n\nThen rest.\n",
        encoding="utf-8",
    )
    publish(sender, "alpha")

    row = list_state(sender)[0]
    assert row.branch == "`ws-alpha/v2`, forked from `main`."
    assert row.next_step == "Finish the first slice."
