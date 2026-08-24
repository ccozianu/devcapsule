"""Focused tests for the argparse command framework's public guarantees."""

from __future__ import annotations

import argparse
from typing import Mapping

import pytest

from devcapsule import cli
from devcapsule.commands import framework
from devcapsule.commands.framework import (
    CarrierAnswer,
    Command,
    Group,
    UsageError,
    add_carrier_options,
    carrier_answers,
)


class _Echo(Command):
    name = "echo"
    help = "Echo the parsed values for inspection."
    seen: tuple[object, object, object] | None = None

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--value")
        parser.add_argument("--path", dest="leaf_path")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        cls.seen = (arguments.value, arguments.leaf_path, context)
        return 0


class _HiddenLeaf(Command):
    name = "secret"
    hidden = True
    help = "Not listed."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        return 0


class _Tree(Group):
    name = "tree"
    help = "Example group with a group-scoped option."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {_Echo.name: _Echo, _HiddenLeaf.name: _HiddenLeaf}

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--path", dest="group_path")

    @classmethod
    def make_context(cls, arguments: argparse.Namespace, parent: object | None) -> object | None:
        return arguments.group_path


def test_group_option_before_subcommand_reaches_group_context() -> None:
    assert _Tree.invoke("tree", ["--path", "/somewhere", "echo", "--value", "x"]) == 0
    assert _Echo.seen == ("x", None, "/somewhere")


def test_tokens_after_the_subcommand_name_belong_to_the_leaf() -> None:
    # The leaf declares its own --path; the group must not capture it.
    assert _Tree.invoke("tree", ["echo", "--path", "/leaf-owned"]) == 0
    assert _Echo.seen == (None, "/leaf-owned", None)


def test_unknown_subcommand_lists_only_visible_commands() -> None:
    with pytest.raises(UsageError) as failure:
        _Tree.invoke("tree", ["bogus"])
    assert "unknown command 'bogus'" in str(failure.value)
    assert "echo" in str(failure.value)
    assert "secret" not in str(failure.value)


def test_group_without_subcommand_prints_help_and_succeeds(capsys) -> None:
    assert _Tree.invoke("tree", []) == 0
    output = capsys.readouterr().out
    assert "Commands:" in output
    assert "echo" in output
    assert "secret" not in output


def test_group_help_option_lists_subcommands(capsys) -> None:
    with pytest.raises(SystemExit) as leave:
        _Tree.invoke("tree", ["--help"])
    assert leave.value.code == 0
    output = capsys.readouterr().out
    assert "Commands:" in output
    assert "echo" in output


def test_leaf_usage_failure_raises_usage_error_with_usage_line() -> None:
    with pytest.raises(UsageError) as failure:
        _Tree.invoke("tree", ["echo", "--bogus"])
    assert "usage:" in str(failure.value)


class _Carriers(Command):
    name = "carriers"
    help = "Accept the shared carrier grammar."
    answers: tuple[CarrierAnswer, ...] = ()

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        add_carrier_options(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        cls.answers = carrier_answers(arguments)
        return 0


def test_carrier_grammar_accepts_two_and_three_token_answers() -> None:
    assert (
        _Carriers.invoke(
            "carriers",
            [
                "--set",
                "runtime.memory-limit",
                "8GiB",
                "--authorize",
                "docker-daemon",
                "host-socket",
                "Required to run peer capsules in the full test suite.",
                "--bind",
                "pycharm/system",
                "host-directory:/somewhere",
            ],
        )
        == 0
    )
    assert _Carriers.answers == (
        CarrierAnswer("set", "runtime.memory-limit", "8GiB", None),
        CarrierAnswer("bind", "pycharm/system", "host-directory:/somewhere", None),
        CarrierAnswer(
            "authorize",
            "docker-daemon",
            "host-socket",
            "Required to run peer capsules in the full test suite.",
        ),
    )


def test_carrier_grammar_stops_at_the_next_option() -> None:
    assert (
        _Carriers.invoke(
            "carriers",
            ["--authorize", "network", "host", "--set", "runtime.memory-limit", "8GiB"],
        )
        == 0
    )
    assert _Carriers.answers == (
        CarrierAnswer("set", "runtime.memory-limit", "8GiB", None),
        CarrierAnswer("authorize", "network", "host", None),
    )


def test_carrier_grammar_rejects_a_lone_name() -> None:
    with pytest.raises(UsageError, match="--set requires NAME VALUE"):
        _Carriers.invoke("carriers", ["--set", "runtime.memory-limit"])


def test_carrier_grammar_rejects_an_unquoted_justification() -> None:
    with pytest.raises(UsageError, match="Quote a justification"):
        _Carriers.invoke(
            "carriers",
            ["--authorize", "network", "host", "reach", "host", "services"],
        )


def test_top_level_unknown_command_and_option_fail_with_exit_code_two(capsys) -> None:
    assert cli.main(["definitely-not-a-command"]) == 2
    assert "unknown command" in capsys.readouterr().err
    assert cli.main(["--definitely-not-an-option"]) == 2
    assert "unknown option" in capsys.readouterr().err


def test_command_names_hide_hidden_commands_by_default() -> None:
    visible = cli.command_names()
    everything = cli.command_names(include_hidden=True)
    assert "host-open" not in visible
    assert "host-open" in everything
    assert set(visible) <= set(everything)


def test_render_command_listing_is_empty_for_no_visible_commands() -> None:
    assert framework.render_command_listing({}) == ""
    assert framework.render_command_listing({"secret": _HiddenLeaf}) == ""
