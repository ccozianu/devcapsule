"""Workflow operations that need git plumbing rather than a branch switch."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from devcapsule.commands.framework import Command, Group
from devcapsule.compat import CliError
from devcapsule import workflow_coordination as workflow_mail


def _add_mail_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        dest="project_path",
        type=Path,
        default=Path("."),
        help="Repository checkout to operate in. Defaults to the current directory.",
    )
    parser.add_argument("--remote", default="origin", help="Git remote holding the branch.")
    parser.add_argument(
        "--branch",
        default=workflow_mail.COORDINATION_BRANCH,
        help="Coordination branch name.",
    )


def _add_name_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workstream",
        dest="name",
        help="Workstream name. Defaults to the one the current ws-<name>/ branch belongs to.",
    )


def _resolve_name(arguments: argparse.Namespace) -> str:
    if arguments.name:
        return str(arguments.name)
    inferred = workflow_mail.current_workstream_name(arguments.project_path)
    if inferred is None:
        raise CliError(
            "no workstream given and the current branch is not ws-<name>/...; pass --workstream"
        )
    return inferred


class MailSendCommand(Command):
    name = "send"
    help = "Deliver one intake item to a workstream."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_mail_options(parser)
        parser.add_argument("recipient", help="Workstream name of the recipient.")
        parser.add_argument("item", type=Path, help="Item file, named YYYY-MM-DD-<sender>-<slug>.md.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            commit = workflow_mail.send(
                arguments.project_path,
                arguments.recipient,
                arguments.item,
                remote=arguments.remote,
                branch=arguments.branch,
            )
        except workflow_mail.WorkflowMailError as exc:
            raise CliError(str(exc)) from exc
        print(f"delivered {arguments.item.name} to {arguments.recipient} at {commit[:12]}")
        return 0


class MailCheckCommand(Command):
    name = "check"
    help = "List the items waiting for a workstream."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_mail_options(parser)
        _add_name_option(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = _resolve_name(arguments)
        try:
            items = workflow_mail.check(
                arguments.project_path, name, remote=arguments.remote, branch=arguments.branch
            )
        except workflow_mail.WorkflowMailError as exc:
            raise CliError(str(exc)) from exc
        if not items:
            print(f"no mail for {name}")
            return 0
        print(f"{len(items)} item(s) for {name}:")
        for item in items:
            print(f"  {item.name}")
        return 0


class MailTakeCommand(Command):
    name = "take"
    help = "Copy a workstream's waiting items into its intake and remove them from the branch."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_mail_options(parser)
        _add_name_option(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = _resolve_name(arguments)
        try:
            written = workflow_mail.take(
                arguments.project_path, name, remote=arguments.remote, branch=arguments.branch
            )
        except workflow_mail.WorkflowMailError as exc:
            raise CliError(str(exc)) from exc
        if not written:
            print(f"no mail for {name}")
            return 0
        print(f"took {len(written)} item(s) into intake, staged:")
        for path in written:
            print(f"  {path}")
        return 0


class MailCommand(Group):
    name = "mail"
    help = "Workstream mail on the coordination branch."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            MailSendCommand.name: MailSendCommand,
            MailCheckCommand.name: MailCheckCommand,
            MailTakeCommand.name: MailTakeCommand,
        }


class PublishCommand(Command):
    name = "publish"
    help = "Push a workstream's status file and decision log to the coordination branch."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_mail_options(parser)
        _add_name_option(parser)
        parser.add_argument(
            "--retire",
            action="store_true",
            help="Remove the workstream's published state instead; used when it concludes.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = _resolve_name(arguments)
        try:
            commit = workflow_mail.publish(
                arguments.project_path,
                name,
                remote=arguments.remote,
                branch=arguments.branch,
                retire=arguments.retire,
            )
        except workflow_mail.WorkflowMailError as exc:
            raise CliError(str(exc)) from exc
        if commit is None:
            print(f"{name}: already current on {arguments.branch}")
        elif arguments.retire:
            print(f"{name}: retired from {arguments.branch} at {commit[:12]}")
        else:
            print(f"{name}: published to {arguments.branch} at {commit[:12]}")
        return 0


class ListCommand(Command):
    name = "list"
    help = "Show every open workstream's live state from the coordination branch."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_mail_options(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            rows = workflow_mail.list_state(
                arguments.project_path, remote=arguments.remote, branch=arguments.branch
            )
        except workflow_mail.WorkflowMailError as exc:
            raise CliError(str(exc)) from exc
        print(workflow_mail.render_list(rows), end="")
        return 0


class WorkflowCommand(Group):
    name = "workflow"
    help = "Multiple-stream workflow operations."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            MailCommand.name: MailCommand,
            PublishCommand.name: PublishCommand,
            ListCommand.name: ListCommand,
        }


COMMAND = WorkflowCommand
