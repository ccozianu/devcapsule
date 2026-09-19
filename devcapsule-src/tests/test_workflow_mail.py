from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from devcapsule import cli, workflow_mail
from devcapsule.workflow_mail import WorkflowMailError, check, send, take


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
