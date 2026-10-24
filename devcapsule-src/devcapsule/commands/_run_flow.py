"""What ``project run`` does before it launches: derive, report, ask.

Principle 2 of the CLI UX redesign work order of 2026-10-24: what follows
from the project and the workstation is derived and shown; what encodes the
developer's intent is asked, once, in the settled order (the command line,
an earlier answer, the record, a derivable default, and only then a prompt);
every question has a flag. Section 3.4: without a terminal nothing is
asked; a missing answer ends the command with exit status 3, naming each
decision with its flag or command, and nothing is written. Answer 12: every
``run`` flag applies to this launch only; ``--save`` records the flags given
as the checkout's answers before launching.

The decisions come from the listing (:mod:`devcapsule.configuration.listing`),
so what ``run`` asks is exactly what ``config check`` reports. The IDE, a
required environment variable, a consent, a recorded host answer whose
recommendation changed, a required value and a required secret block the
launch until answered; so does a vendor's or DevCapsule's channel the
workstation has not accepted yet (D-0011, once per computer); a host access
the project recommends and the developer never answered is asked, and "not
now" launches with the secure default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import getpass
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence, TextIO

from devcapsule.compat import DecisionPending
from devcapsule.configuration.authorization import authorization_declarations, normalize_authorization_value
from devcapsule.configuration.capabilities import LocalCapabilities
from devcapsule.configuration.capability_commands import configure as configure_capabilities
from devcapsule.configuration.derivation import CheckoutState, Selection, derive_plan, load_state, register_checkout
from devcapsule.configuration.docker_arguments import arguments_path, update_environment, validate_name, validate_value
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.configuration.listing import Decision, Listing
from devcapsule.configuration.operations import CheckoutRecord, apply_configuration_answers, ProvidedAnswer
from devcapsule.configuration.storage import ResolvedProject, manifest_for
from devcapsule.configuration.values import LAUNCHER_VALUE_NAMES, memory_size_bytes, normalize_launcher_value

__all__ = ["Prepared", "RunFlags", "prepare_launch"]

BLOCKING_KINDS = {"ide", "env", "renew", "trust", "consent", "value", "secret"}


@dataclass(frozen=True)
class RunFlags:
    """The run flags that answer or override a choice; each applies to this launch only unless ``save``."""

    ide: str | None = None
    agents: tuple[str, ...] = ()
    memory: str | None = None
    cpus: str | None = None
    environment: tuple[str, ...] = ()  # NAME=VALUE saved for this run, or NAME taken from the host
    authorize: tuple[tuple[str, str], ...] = ()  # (node, value)
    trust: tuple[str, ...] = ()  # channel ids accepted for this workstation, recorded at once
    save: bool = False
    allow_unverified: bool = False


@dataclass
class Prepared:
    """What the launch runs with: the derived plan and this run's overrides."""

    selected: ResolvedProject
    host_overrides: dict[str, Any] = field(default_factory=dict)
    memory_override: int | None = None
    cpus_override: int | None = None
    environment_tokens: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def prepare_launch(
    start: Path,
    flags: RunFlags,
    *,
    interactive: bool | None = None,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
    print_only: bool = False,
) -> Prepared:
    """Derive the checkout's plan, asking what is pending, and write its resolution.

    With ``print_only`` nothing is asked and nothing is written but the
    resolution of an already complete checkout. Without a terminal, a
    blocking decision raises :class:`DecisionPending` before any write.
    """
    interactive = sys.stdin.isatty() if interactive is None else interactive
    output = output_stream if output_stream is not None else sys.stdout
    root, manifest = manifest_for(start)
    state = load_state(root, manifest)
    prepared_notes: list[str] = []

    if flags.trust and not print_only:
        # A trust statement is the workstation's, not this launch's: recorded
        # now, as ``--save`` records its flags, whatever the launch then asks.
        for channel_id in flags.trust:
            accept_channel(root, manifest, channel_id)
            prepared_notes.append(f"Accepted the channel {channel_id} for this workstation.")
        state = load_state(root, manifest)
    selection = Selection(LocalCapabilities.read(state.checkout), state.surfaces, state.agents)
    selection_changed = False
    if flags.ide is not None:
        selection.ide = _capability(flags.ide, state.surfaces, "IDE")
        selection_changed = True
    for agent in flags.agents:
        selection.agents.add(_capability(agent, state.agents, "agent"))
        selection_changed = True
    host_overrides: dict[str, Any] = {}
    memory_override: int | None = None
    cpus_override: int | None = None
    if flags.memory is not None:
        memory_override = memory_size_bytes(str(normalize_launcher_value("memory", flags.memory)))
    if flags.cpus is not None:
        cpus_override = int(normalize_launcher_value("cpus", flags.cpus))
    environment_tokens: list[str] = []
    answered_environment: set[str] = set()
    for item in flags.environment:
        name, separator, value = item.partition("=")
        validate_name(name)
        if separator:
            validate_value(value)
        environment_tokens.extend(["--env", item])
        answered_environment.add(name)

    if flags.save and not print_only:
        # Recorded exactly as the config family records them, before anything else.
        register_checkout(state)
        if selection_changed:
            configure_capabilities(root, local=list(selection.local().selected), allow_unverified=flags.allow_unverified)
        record = CheckoutRecord(manifest, root)
        if flags.memory is not None:
            record.values["memory"] = normalize_launcher_value("memory", flags.memory)
        if flags.cpus is not None:
            record.values["cpus"] = normalize_launcher_value("cpus", flags.cpus)
        for node, value in flags.authorize:
            declaration = authorization_declarations(manifest, state.composed_lock()).get(node)
            if declaration is None:
                raise ProjectConfigurationError(f"Authorization {node!r} is not declared by this project.")
            record.authorize(declaration, normalize_authorization_value(declaration, value))
        record.write()
        for item in flags.environment:
            name, separator, value = item.partition("=")
            update_environment(arguments_path(record.input_path), name, value if separator else None, from_host=not separator)
        environment_tokens = []
        memory_override = cpus_override = None
        state = load_state(root, manifest)
        selection_changed = False
        prepared_notes.append("Recorded the flags given for this checkout.")
    else:
        for node, value in flags.authorize:
            declaration = authorization_declarations(manifest, state.composed_lock()).get(node)
            if declaration is None or declaration.required:
                raise ProjectConfigurationError(f"Authorization {node!r} cannot be answered for one run; the host accesses can.")
            host_overrides[node] = normalize_authorization_value(declaration, value)
            print(f"Run-once authorization: {node} = {value}", file=sys.stderr)

    checkout = state.with_selection(selection, allow_unverified=flags.allow_unverified) if selection_changed else state.checkout
    listing = state.listing(checkout)
    decisions = [
        decision for decision in listing.decisions
        if not (decision.kind == "access" and decision.name in host_overrides)
        and not (decision.kind == "env" and decision.name in answered_environment)
    ]
    blocking = [decision for decision in decisions if decision.kind in BLOCKING_KINDS]
    soft = [decision for decision in decisions if decision.kind not in BLOCKING_KINDS]
    if blocking and (print_only or not interactive):
        raise DecisionPending(_render_pending(blocking, root, prepared_notes))
    if decisions and not print_only and interactive:
        register_checkout(state)
        state, checkout, host_overrides = _settle(state, checkout, decisions, host_overrides, selection,
                                                 selection_changed, flags, input_stream, output)
        listing = state.listing(checkout)
        still = [d for d in listing.decisions if d.kind in BLOCKING_KINDS]
        if still:
            raise DecisionPending(_render_pending(still, root, prepared_notes, answered=True))
    elif soft:
        for decision in soft:
            prepared_notes.append(
                f"The project asks for {decision.description} ({decision.reason}); not granted this run. "
                f"Allow or deny: {decision.command}"
            )
    register_checkout(state)
    selected = derive_plan(state, checkout)
    return Prepared(selected, host_overrides, memory_override, cpus_override, environment_tokens, prepared_notes)


def accept_channel(root: Path, manifest: dict[str, Any], channel_id: str) -> Path:
    """Record the user's acceptance of one channel for this workstation; return the record's path."""
    from devcapsule.configuration.storage import load_trust, recommendation_lock_for, write_trust
    from devcapsule.configuration.trust import WorkstationTrust, channels_for
    _path, lock = recommendation_lock_for(root, manifest)
    channels = channels_for(lock)
    channel = channels.get(channel_id)
    if channel is None:
        raise ProjectConfigurationError(
            f"No channel {channel_id!r} on this project; its channels: " + (", ".join(sorted(channels)) or "none") + "."
        )
    trust = WorkstationTrust.read(load_trust()).with_channel(channel)
    return write_trust(trust.document())


def _capability(value: str, names: Mapping[str, str], kind: str) -> str:
    candidate = value.strip()
    by_component = {component: name for name, component in names.items()}
    candidate = by_component.get(candidate, candidate)
    if candidate not in names:
        raise ProjectConfigurationError(f"Unknown {kind} {value!r}; choose one of {', '.join(sorted(names))}.")
    return candidate


def _render_pending(decisions: list[Decision], root: Path, recorded: Sequence[str] = (), *, answered: bool = False) -> str:
    """The status-3 text: each decision with its flag and command, then what was and was not written."""
    lines = ["the launch of this checkout needs answers:"]
    for decision in decisions:
        flag = {"ide": "--ide IDE", "env": f"--env {decision.name}=VALUE", "consent": f"--authorize {decision.name} {decision.value}",
                "access": f"--authorize {decision.name} {decision.value}", "trust": f"--trust {decision.name}",
                "renew": "", "value": "", "secret": ""}[decision.kind]
        lines.append(f"  {decision.kind} {decision.name}: {decision.description}" + (f"  ({decision.reason})" if decision.reason else ""))
        lines.append("      " + (f"{flag}  |  " if flag else "") + decision.command)
    lines.extend(recorded)
    if answered:
        lines.append("The answers given were recorded; nothing else was written.")
    elif recorded:
        lines.append("Nothing else was written. Answer on the command line or in a terminal.")
    else:
        lines.append("Nothing was written. Answer on the command line or in a terminal.")
    return "\n".join(lines)


def _settle(
    state: CheckoutState, checkout: dict[str, Any], decisions: list[Decision], host_overrides: dict[str, Any],
    selection: Selection, selection_changed: bool, flags: RunFlags, input_stream: TextIO | None, output: TextIO,
) -> tuple[CheckoutState, dict[str, Any], dict[str, Any]]:
    """Ask each decision at the terminal and record the answer where the config family would."""
    reader = (input_stream.readline if input_stream is not None else lambda: sys.stdin.readline())
    root, manifest = state.root, state.manifest
    assert state.input_path is not None
    for decision in decisions:
        if decision.kind == "ide":
            output.write("The project leaves the IDE to you. Choose one:\n")
            for index, (name, version) in enumerate(decision.choices, start=1):
                output.write(f"  {index}. {name:<13} {version}\n")
            choice = _ask(output, reader, f"IDE [1-{len(decision.choices)}]: ")
            names = [name for name, _ in decision.choices]
            picked = names[int(choice) - 1] if choice.isdecimal() and 1 <= int(choice) <= len(names) else _capability(choice, state.surfaces, "IDE")
            selection.ide = picked
            configure_capabilities(root, local=list(selection.local().selected), allow_unverified=flags.allow_unverified)
            output.write(f"Recorded for this checkout. Change: devcapsule project --path {root} config ide IDE\n")
            selection_changed = False
        elif decision.kind == "env":
            output.write(f"The project needs {decision.name}" + (f": {decision.reason}" if decision.reason else "") + "\n")
            value = _hidden(output, reader, f"{decision.name} [hidden, kept on this computer]: ")
            update_environment(arguments_path(state.input_path), decision.name, value)
            output.write(f"Recorded for this checkout. Change: devcapsule project --path {root} config env set {decision.name}\n")
        elif decision.kind == "access":
            output.write(f"The project asks for {decision.description}: {decision.reason}\n")
            answer = _ask(output, reader, "[a]llow for this checkout, allow [o]nce, [d]eny for this checkout, Enter = not now: ").lower()
            record = CheckoutRecord(manifest, root)
            declaration = authorization_declarations(manifest, state.composed_lock(checkout))[decision.name]
            if answer in {"a", "allow"}:
                record.authorize(declaration, normalize_authorization_value(declaration, decision.value))
                record.write()
            elif answer in {"d", "deny"}:
                record.authorize(declaration, normalize_authorization_value(declaration, "none"))
                record.write()
            elif answer in {"o", "once"}:
                host_overrides[decision.name] = normalize_authorization_value(declaration, decision.value)
            else:
                output.write(f"Not now; the secure default applies. Allow or deny later: {decision.command}\n")
        elif decision.kind == "renew":
            output.write(f"Your answer for {decision.name} predates the project's current recommendation: {decision.reason}\n")
            answer = _ask(output, reader, f"[a]llow {decision.name} {decision.value} for this checkout, or [d]eny: ").lower()
            record = CheckoutRecord(manifest, root)
            declaration = authorization_declarations(manifest, state.composed_lock(checkout))[decision.name]
            if answer in {"a", "allow"}:
                record.authorize(declaration, normalize_authorization_value(declaration, decision.value))
                record.write()
            elif answer in {"d", "deny"}:
                record.authorize(declaration, normalize_authorization_value(declaration, "none"))
                record.write()
            else:
                output.write(f"Not answered; renew it later: {decision.command}\n")
        elif decision.kind == "trust":
            output.write(f"{decision.description}\n")
            if decision.reason:
                output.write(f"  {decision.reason}\n")
            answer = _ask(output, reader, "Accept, once for this computer? [y/N]: ").lower()
            if answer in {"y", "yes"}:
                accept_channel(root, manifest, decision.name)
                output.write(f"Recorded for this workstation. Withdraw: devcapsule project --path {root} config trust withdraw {decision.name}\n")
            else:
                output.write(f"Not accepted. Accept later: {decision.command}\n")
        elif decision.kind == "consent":
            output.write(f"{decision.description}\n")
            answer = _ask(output, reader, "Accept? [y/N]: ").lower()
            if answer in {"y", "yes"}:
                record = CheckoutRecord(manifest, root)
                declaration = authorization_declarations(manifest, state.composed_lock(checkout))[decision.name]
                record.authorize(declaration, declaration.recommended_value)
                record.write()
            else:
                output.write(f"Not accepted. Accept later: {decision.command}\n")
        elif decision.kind == "value":
            value = _ask(output, reader, f"{decision.name} ({decision.description}): ")
            record = CheckoutRecord(manifest, root)
            apply_configuration_answers((ProvidedAnswer("set", decision.name, value),), manifest, state.composed_lock(checkout), record)
            record.write()
        elif decision.kind == "secret":
            output.write(f"{decision.description}\n")
            answer = _ask(output, reader, f"Bind {decision.name} to the host's variable {decision.variable}? [y/N]: ").lower()
            if answer in {"y", "yes"}:
                record = CheckoutRecord(manifest, root)
                apply_configuration_answers((ProvidedAnswer("bind", decision.name, f"host-environment:{decision.variable}"),),
                                            manifest, state.composed_lock(checkout), record)
                record.write()
        state = load_state(root, manifest)
        state.saved_environment = state.saved_environment  # re-read by load_state
        checkout = state.with_selection(selection, allow_unverified=flags.allow_unverified) if selection_changed else state.checkout
    return state, checkout, host_overrides


def _ask(output: TextIO, reader: Callable[[], str], prompt: str) -> str:
    output.write(prompt)
    output.flush()
    line = reader()
    if line == "":
        raise DecisionPending("the terminal closed before the answer; nothing more was written")
    return line.rstrip("\n").strip()


def _hidden(output: TextIO, reader: Callable[[], str], prompt: str) -> str:
    if sys.stdin.isatty() and reader is not None and reader.__name__ == "<lambda>":
        try:
            return getpass.getpass(prompt)
        except (EOFError, getpass.GetPassWarning):
            raise DecisionPending("the terminal closed before the answer; nothing more was written") from None
    return _ask(output, reader, prompt)
