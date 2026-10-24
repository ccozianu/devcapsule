"""Workstation trust (D-0011): a vendor's channel accepted once per computer, for every project and version."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tomllib

import pytest

from devcapsule import cli
from devcapsule.commands._run_flow import RunFlags, prepare_launch
from devcapsule.compat import DecisionPending
from devcapsule.configuration.authorization import review_authorizations
from devcapsule.configuration.capability_commands import paths
from devcapsule.configuration.file_formats import ProjectConfigurationError, render_toml
from devcapsule.configuration.storage import checkout_record_paths, load_toml, load_trust, manifest_for, trust_path
from devcapsule.configuration.trust import BASE_CHANNEL, Channel, WorkstationTrust, channels_for, render_trust

CLAUDE_TERMS = "https://www.anthropic.com/legal/commercial-terms"


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME"):
        monkeypatch.setenv(key, str(tmp_path / key.lower()))
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["project", "--path", str(root), "init", "--require", "node", "--creator", "mailto:owner@example.test"]) == 0
    return root


def config(root: Path, *arguments: str) -> int:
    return cli.main(["project", "--path", str(root), "config", *arguments])


def lock_path(root: Path) -> Path:
    return root / ".devcapsule" / "devcapsule.linux-amd64.lock"


def pin_claude_code(root: Path, version: str) -> None:
    lock = tomllib.loads(lock_path(root).read_text())
    lock["components"]["claude-code"] = {
        "version": version, "acquisition-authorization": "claude-code-download", "terms-url": CLAUDE_TERMS,
        "delivery-policy": "local-materialization",
        "artifacts": {"linux-amd64": {"url": f"https://downloads.example.test/claude-{version}", "sha256": "e" * 64}},
    }
    lock_path(root).write_text(render_toml(lock))


def reviews(root: Path) -> dict:
    _root, manifest = manifest_for(root)
    record = load_toml(checkout_record_paths(manifest, root)[0])
    return {item.name: item for item in review_authorizations(manifest, load_toml(lock_path(root)), record,
                                                              WorkstationTrust.read(load_trust()))}


def test_channels_are_the_locks_base_and_vendor_products(project: Path) -> None:
    channels = channels_for(load_toml(lock_path(project)))
    assert list(channels) == [BASE_CHANNEL]
    base = channels[BASE_CHANNEL]
    assert base.authorization == "base-image" and base.vendor == "DevCapsule"
    assert "docker.io/mycodespaceai/devcapsule-base" in base.statement() and "every version" in base.statement()
    pin_claude_code(project, "1.0.0")
    channels = channels_for(load_toml(lock_path(project)))
    claude = channels["claude-code"]
    assert (claude.vendor, claude.origins, claude.terms_url, claude.authorization) == (
        "Anthropic", ("downloads.example.test",), CLAUDE_TERMS, "claude-code-download")
    # A base outside DevCapsule's repository is a departure: no channel, per-checkout consent as before.
    lock = tomllib.loads(lock_path(project).read_text())
    lock["base"]["reference"] = "registry.example.test/other-base@sha256:" + "a" * 64
    assert BASE_CHANNEL not in channels_for(lock)


def test_the_record_round_trips_and_covers_only_what_was_accepted() -> None:
    channel = Channel("claude-code", "Anthropic", "Claude Code", ("downloads.example.test",), "sha", CLAUDE_TERMS)
    trust = WorkstationTrust().with_channel(channel)
    reloaded = WorkstationTrust.read(tomllib.loads(render_trust(trust)))
    assert reloaded.covers(channel) and reloaded.channels["claude-code"]["accepted"]
    assert WorkstationTrust.read({"trust": trust.document()}).covers(channel)  # the merged workstation document
    moved = Channel("claude-code", "Anthropic", "Claude Code", ("downloads.example.test", "cdn.example.test"), "sha", CLAUDE_TERMS)
    assert not reloaded.covers(moved)  # a new origin asks again
    assert not reloaded.covers(Channel("claude-code", "Anthropic", "Claude Code", channel.origins, "sha", "https://other/terms"))
    assert not reloaded.without("claude-code").channels
    with pytest.raises(ProjectConfigurationError, match="No trust is recorded"):
        reloaded.without("codex")
    with pytest.raises(ProjectConfigurationError, match="unsupported schema version"):
        WorkstationTrust.read({"devcapsule-trust-schema-version": 2})
    with pytest.raises(ProjectConfigurationError, match="must name its vendor"):
        WorkstationTrust.read({"channels": {"x": {"origins": []}}})


def test_trust_list_accept_and_withdraw(project: Path, capsys) -> None:
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "check") == 3
    assert config(project, "trust", "list") == 0
    out = capsys.readouterr().out
    assert "devcapsule-base" in out and "not yet" in out and str(trust_path()) in out
    assert config(project, "trust", "accept", "devcapsule-base") == 0
    out = capsys.readouterr().out
    assert "Trust DevCapsule to supply the base images" in out and "Recorded for this workstation" in out
    assert load_toml(trust_path())["channels"]["devcapsule-base"]["vendor"] == "DevCapsule"
    assert config(project, "show") == 0
    assert "workstation trust (devcapsule-base)" in capsys.readouterr().out
    assert config(project, "check") == 0
    capsys.readouterr()
    assert config(project, "trust", "list", "--json") == 0
    listed = json.loads(capsys.readouterr().out)
    assert [(row["channel"], row["trusted"]) for row in listed["channels"]] == [("devcapsule-base", True)]
    assert config(project, "trust", "withdraw", "devcapsule-base") == 0
    assert config(project, "check") == 3
    assert config(project, "trust", "withdraw", "devcapsule-base") == 2
    assert config(project, "trust", "accept", "codex") == 2
    assert "its channels: devcapsule-base" in capsys.readouterr().err


def test_run_trust_flag_records_the_channel_before_the_questions(project: Path) -> None:
    with pytest.raises(DecisionPending, match="--trust devcapsule-base"):
        prepare_launch(project, RunFlags(ide="python-ide"), interactive=False)
    assert not trust_path().exists()
    prepared = prepare_launch(project, RunFlags(ide="python-ide", trust=("devcapsule-base",)), interactive=False)
    assert prepared.selected.resolution["authorization"]["base-image"]["reference"].startswith("docker.io/mycodespaceai/devcapsule-base@")
    assert "devcapsule-base" in load_toml(trust_path())["channels"]
    assert "Accepted the channel devcapsule-base for this workstation." in prepared.notes
    # Printing the command stages the acceptance for the plan and writes nothing.
    assert config(project, "trust", "withdraw", "devcapsule-base") == 0
    prepare_launch(project, RunFlags(ide="python-ide", trust=("devcapsule-base",)), print_only=True)
    assert not WorkstationTrust.read(load_trust()).channels
    # With another decision pending and no terminal, the flag's acceptance is staged with the other answers: nothing is written.
    with pytest.raises(DecisionPending, match="Nothing was written"):
        prepare_launch(project, RunFlags(trust=("devcapsule-base",)), interactive=False)  # the IDE is still unchosen
    assert not WorkstationTrust.read(load_trust()).channels
    # Declined at the prompt: nothing recorded, the launch is still pending.
    assert config(project, "ide", "python-ide") == 0
    prompts = io.StringIO()
    with pytest.raises(DecisionPending):
        prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO("n\n"), output_stream=prompts)
    assert "Not accepted. Accept later:" in prompts.getvalue()
    assert not WorkstationTrust.read(load_trust()).channels


def test_a_trusted_vendor_covers_every_version_and_a_denial_still_wins(project: Path, capsys) -> None:
    pin_claude_code(project, "1.0.0")
    assert reviews(project)["claude-code-download"].status == "missing-required"
    assert config(project, "trust", "accept", "claude-code") == 0
    review = reviews(project)["claude-code-download"]
    assert (review.status, review.trusted_channel, review.problem) == ("trusted", "claude-code", None)
    pin_claude_code(project, "1.1.0")  # the software-approval question of D-0012 does not arise
    assert reviews(project)["claude-code-download"].status == "trusted"
    assert config(project, "authorize", "claude-code-download", "false") == 0
    review = reviews(project)["claude-code-download"]
    assert review.trusted_channel is None and review.recorded == "false"
    capsys.readouterr()
    assert config(project, "trust", "list") == 0
    assert "Anthropic" in capsys.readouterr().out


def test_a_real_run_launches_on_the_workstations_trust_alone(project: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every reader of the base selection takes the trust: the realization, the history, the plan."""
    from tests.test_upgrade_recovery import install_external_fakes, invoke
    launch = install_external_fakes(monkeypatch, [])
    monkeypatch.setattr("sys.stdin", io.StringIO("python-ide\ny\n"))
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert invoke(project, "run", "--no-update-check") == 0
    assert launch.call_count == 1
    _root, manifest = manifest_for(project)
    assert "base-image" not in load_toml(checkout_record_paths(manifest, project)[0]).get("authorization", {})
    assert "devcapsule-base" in load_toml(trust_path())["channels"]
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert invoke(project, "run", "--no-update-check") == 0  # the second launch asks nothing
