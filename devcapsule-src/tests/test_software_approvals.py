"""Software approvals: new versions of vendor software approved before are one question at launch.

The owner's direction of 2026-10-22. The fixtures are the upgrade-recovery
module's: a resolved checkout of the fixture project, driven through the
real command line.
"""

from __future__ import annotations

import time
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

from devcapsule import version_sets
from devcapsule.commands import _software_approvals as offer
from devcapsule.configuration.approvals import pending_software_approvals, render_software_approvals
from devcapsule.configuration.storage import load_toml, manifest_for
from tests.test_upgrade_recovery import checkout, install_external_fakes, invoke, review  # noqa: F401

CLAUDE_TERMS = "https://www.anthropic.com/legal/commercial-terms"
ANTIGRAVITY_TERMS = "https://antigravity.google/terms/"
GUIDE = "https://devcapsule.mycodespace.ai/docs/current/configuration/software-approvals/"


def lock_path(project: Path) -> Path:
    return project / ".devcapsule" / "devcapsule.linux-amd64.lock"


def pin(project: Path, component: str, authorization: str, terms: str, version: str) -> None:
    """Pin a vendor component in the lock at ``version``, replacing an earlier pin."""
    path = lock_path(project)
    lock = tomllib.loads(path.read_text())
    lock["components"][component] = {
        "version": version, "acquisition-authorization": authorization, "terms-url": terms,
        "delivery-policy": "local-materialization",
        "artifacts": {"linux-amd64": {"url": f"https://example.test/{component}-{version}", "sha256": "e" * 64}},
    }
    from devcapsule.configuration.file_formats import render_toml
    path.write_text(render_toml(lock))


def approved_then_bumped(project: Path, record: Path) -> None:
    """A checkout that approved Claude Code 1.0.0 and whose lock now pins 1.1.0."""
    pin(project, "claude-code", "claude-code-download", CLAUDE_TERMS, "1.0.0")
    assert invoke(project, "config", "authorize", "base-image", "default") == 0
    assert invoke(project, "config", "authorize", "claude-code-download", "true") == 0
    assert invoke(project, "config", "resolve") == 0
    pin(project, "claude-code", "claude-code-download", CLAUDE_TERMS, "1.1.0")
    assert review(project, record).ready is False


def pending(project: Path, record: Path):
    _root, manifest = manifest_for(project)
    return pending_software_approvals(manifest, load_toml(lock_path(project)), load_toml(record))


def test_a_bumped_approved_download_is_a_software_approval(checkout) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    approvals = pending(project, record)
    assert approvals is not None and [a.name for a in approvals] == ["claude-code-download"]
    approval = approvals[0]
    assert (approval.component, approval.vendor, approval.version, approval.previous_version) == (
        "claude-code", "Anthropic", "1.1.0", None,
    )
    assert approval.change == "1.1.0"
    lines = render_software_approvals(approvals)
    assert lines[1] == f"- Claude Code 1.1.0, downloaded from Anthropic under {CLAUDE_TERMS} (claude-code-download)"


def test_nothing_pending_is_an_empty_list(checkout) -> None:
    project, record, _ = checkout
    pin(project, "claude-code", "claude-code-download", CLAUDE_TERMS, "1.0.0")
    assert invoke(project, "config", "authorize", "base-image", "default") == 0
    assert invoke(project, "config", "authorize", "claude-code-download", "true") == 0
    assert pending(project, record) == ()


@pytest.mark.parametrize("other", ["missing-consent", "denied-then-bumped", "stale-host-access"])
def test_any_other_pending_decision_disqualifies_the_list(checkout, other: str) -> None:
    """A missing consent, a denial, or a host-access decision in the list is decided one by one."""
    project, record, _ = checkout
    approved_then_bumped(project, record)
    if other == "missing-consent":
        pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.0.0")
    elif other == "denied-then-bumped":
        pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.0.0")
        assert invoke(project, "config", "authorize", "antigravity-download", "false") == 0
        pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.1.0")
    else:
        text = record.read_text()
        record.write_text(text.replace('"recommendation-digest"', '"recommendation-digest-x"', 1) if '"recommendation-digest"' in text else text)
        manifest_path = project / ".devcapsule/devcapsule.toml"
        manifest_path.write_text(manifest_path.read_text() + '\n[host.browser.host-open.recommended]\nvalue = true\njustification = "Open links on the host."\n')
        assert invoke(project, "config", "authorize", "host-browser", "true") == 0
        manifest_path.write_text(manifest_path.read_text().replace('"Open links on the host."', '"Open links on the host, changed."'))
    assert pending(project, record) is None


def test_the_previous_version_comes_from_the_newest_known_good_record(checkout) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    from devcapsule.configuration.file_formats import render_toml
    known_good = version_sets.state_directory(project) / "known-good"
    known_good.mkdir(parents=True, exist_ok=True)
    older = {"components": {"claude-code": {"version": "0.9.0"}}}
    newer = {"components": {"claude-code": {"version": "1.0.0"}}}
    (known_good / "older.toml").write_text(render_toml({"lock": render_toml(older), "last-success": time.time() - 100}))
    (known_good / "newer.toml").write_text(render_toml({"lock": render_toml(newer), "last-success": time.time()}))
    (known_good / "broken.toml").write_text("not = [toml")
    assert offer.previous_versions(project) == {"claude-code": "1.0.0"}
    _root, manifest = manifest_for(project)
    approvals = offer.pending_for(project, manifest)
    assert approvals is not None and approvals[0].change == "1.0.0 to 1.1.0"


def test_run_asks_once_and_launches_on_y(checkout, monkeypatch, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    events: list = []
    launch = install_external_fakes(monkeypatch, events)
    monkeypatch.setattr(offer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(offer, "confirmation_key", lambda: "y")
    assert invoke(project, "run", "--no-update-check") == 0
    out = capsys.readouterr().out
    assert "Claude Code 1.1.0, downloaded from Anthropic" in out
    assert "Approve all of them? Press y" in out
    assert "Approved 1 software update for this checkout." in out
    assert launch.call_count == 1
    answer = load_toml(record)["authorization"]["claude-code-download"]
    assert answer["value"] is True
    assert review(project, record).ready is True  # the digest is current and the resolution regenerated


def test_run_stops_on_any_other_key_and_names_the_command_and_the_guide(checkout, monkeypatch, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    before = record.read_bytes()
    events: list = []
    launch = install_external_fakes(monkeypatch, events)
    monkeypatch.setattr(offer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(offer, "confirmation_key", lambda: "n")
    assert invoke(project, "run", "--no-update-check") == 1
    out = capsys.readouterr().out
    assert "Not approved; nothing written." in out
    assert f"devcapsule project --path {project}" not in out  # the path has spaces: it is quoted
    assert "config approve --all" in out and GUIDE in out
    assert "Launch cancelled; no session was started." in out
    assert record.read_bytes() == before and launch.call_count == 0


def test_run_without_a_terminal_stops_with_the_same_instruction(checkout, monkeypatch, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    before = record.read_bytes()
    launch = install_external_fakes(monkeypatch, [])
    monkeypatch.setattr(offer.sys.stdin, "isatty", lambda: False)
    assert invoke(project, "run", "--no-update-check") == 1
    out = capsys.readouterr().out
    assert "No terminal to ask; the launch stops here." in out
    assert "config approve --all" in out and GUIDE in out
    assert record.read_bytes() == before and launch.call_count == 0


def test_run_with_other_pending_decisions_refuses_as_before(checkout, monkeypatch, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.0.0")  # never answered
    launch = install_external_fakes(monkeypatch, [])
    monkeypatch.setattr(offer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(offer, "confirmation_key", lambda: "y")
    assert invoke(project, "run", "--no-update-check") == 2
    captured = capsys.readouterr()
    assert "Approve all of them?" not in captured.out
    # The refusal is the one a changed lock always had: resolve first, which then lists the decisions.
    assert "Local resolution is stale (platform-lock)" in captured.err
    assert invoke(project, "config", "resolve") == 2
    err = capsys.readouterr().err
    assert "decisions required" in err and "antigravity-download: missing-required" in err
    assert launch.call_count == 0


def test_print_command_never_asks_or_writes(checkout, monkeypatch, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    before = record.read_bytes()
    monkeypatch.setattr(offer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(offer, "confirmation_key", lambda: pytest.fail("asked"))
    assert invoke(project, "run", "--print-command", "--no-update-check") == 2
    assert "Local resolution is stale (platform-lock)" in capsys.readouterr().err
    assert record.read_bytes() == before


def test_config_approve_lists_then_records_all_or_by_name(checkout, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.0.0")
    assert invoke(project, "config", "authorize", "antigravity-download", "true") == 0
    pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.1.0")
    # Listing only: nothing written, the command and the guide named.
    before = record.read_bytes()
    assert invoke(project, "config", "approve") == 1
    out = capsys.readouterr().out
    assert "- Antigravity CLI 2.1.0" in out and "- Claude Code 1.1.0" in out
    assert "config approve --all" in out and GUIDE in out
    assert record.read_bytes() == before
    # By name: only that one, the other stays pending.
    assert invoke(project, "config", "approve", "claude-code-download") == 0
    out = capsys.readouterr().out
    assert "Approved 1 software update" in out and "Still pending: antigravity-download" in out
    approvals = pending(project, record)
    assert approvals is not None and [a.name for a in approvals] == ["antigravity-download"]
    # The rest with --all; the resolution is regenerated and the review is ready.
    assert invoke(project, "config", "approve", "--all") == 0
    assert "Approved 1 software update" in capsys.readouterr().out
    assert pending(project, record) == () and review(project, record).ready is True
    assert invoke(project, "config", "approve") == 0
    assert "No software approvals are pending" in capsys.readouterr().out


def test_config_approve_refuses_unknown_names_and_mixed_lists(checkout, capsys) -> None:
    project, record, _ = checkout
    approved_then_bumped(project, record)
    assert invoke(project, "config", "approve", "antigravity-download") == 2
    assert "No software approval is pending for antigravity-download; pending: claude-code-download" in capsys.readouterr().err
    assert invoke(project, "config", "approve", "--all", "claude-code-download") == 2
    assert "--all cannot be combined with NAME" in capsys.readouterr().err
    pin(project, "antigravity-cli", "antigravity-download", ANTIGRAVITY_TERMS, "2.0.0")  # never answered
    assert invoke(project, "config", "approve", "--all") == 2
    assert "not all software approvals" in capsys.readouterr().err


def test_the_approve_command_is_quoted_for_a_path_with_spaces(tmp_path: Path) -> None:
    root = tmp_path / "a checkout"
    assert offer.approve_command(root) == f"devcapsule project --path '{root}' config approve --all"
    assert offer.approve_command(root, ("claude-code-download",)).endswith("config approve claude-code-download")
