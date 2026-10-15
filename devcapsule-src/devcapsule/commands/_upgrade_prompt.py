"""Launch-time critical upgrade decisions through the shared elicitation engine."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Callable

from devcapsule import version_sets
from devcapsule.compat import CliError
from devcapsule.configuration.authorization import AuthorizationReview
from devcapsule.elicitation import Elicitor


def _choice(*values: str) -> Callable[[str], str]:
    def validate(value: str) -> str:
        value = value.lower()
        if "yes" in values:
            value = {"y": "yes", "n": "no"}.get(value, value)
        if value not in values:
            raise CliError("Choose " + ", ".join(values) + ".")
        return value
    return validate


def offer_upgrades(root: Path, *, refresh: bool = True) -> bool:
    """Return whether launch may proceed. EOF/stop cancels without consent.

    Optional discovery failures don't gate launch. Once preparation is chosen,
    failures are shown and the developer decides whether to launch the old set.
    The caller must reload admitted configuration after this returns.
    """
    interactive = sys.stdin.isatty()
    try:
        notices = version_sets.launch_notices(root, refresh=refresh and interactive)
    except (CliError, OSError) as exc:
        print(f"Component update check unavailable: {exc}. Continuing with the selected version set.")
        return True
    for notice in notices:
        current = version_sets.Workspace.load(root).lock["components"].get(notice["component"], {})
        if current.get("version") != notice["current"]:
            continue  # Another advisory may already have prompted this upgrade.
        if not version_sets.notice_decision(root, notice):
            continue
        label = "Security" if notice["kind"] == "security" else "End-of-support / vendor deprecation"
        checked = datetime.fromtimestamp(notice["checked-at"], timezone.utc).isoformat()
        print(f"{label} notice for {notice['component']} {notice['current']}: {notice['detail']}\n"
              f"Source: {notice['source']}\nLast checked: {checked}; cached metadata may be stale.")
        if not interactive:
            print("No interactive decision is possible. Keeping the selected version; run 'devcapsule project versions check' "
                  "and 'versions preview COMPONENT VERSION' to review an upgrade.")
            continue
        candidates = notice["candidates"]
        # Each notice has its own answer namespace; acquisition/confirmation
        # answers cannot accidentally authorize another component's upgrade.
        elicitor = Elicitor(interactive=True)
        choices = ("upgrade", "later", "keep", "stop") if candidates else ("later", "keep", "stop")
        if candidates:
            print(f"Available candidate: {notice['component']} {candidates[0]}. Availability does not establish a security fix or DevCapsule validation.")
        else:
            print("No available replacement was reported. Consult the source for remediation.")
        answer = elicitor.seek(
            "critical-upgrade", description=("Choose " + ("upgrade (review first), " if candidates else "")
                + "later (seven days), keep (silence this notice), or stop launch"),
            remedy="devcapsule project versions check", empty_answer="later", validate=_choice(*choices),
        )
        if answer is None or answer.value == "stop":
            return False
        if answer.value in {"later", "keep"}:
            version_sets.notice_decision(root, notice, action="defer" if answer.value == "later" else "dismiss")
            continue
        try:
            identity = version_sets.preview(root, notice["component"], candidates[0])
            # Preview discloses the actual validation gaps. This affirmative
            # answer is also explicit consent to try those unvalidated inputs.
            confirm = elicitor.seek(
                "select-upgrade", description="Prepare and launch this exact version set, accepting any validation gaps shown? (yes/no)",
                remedy=f"devcapsule project versions select {identity} --unvalidated",
                empty_answer="no", validate=_choice("yes", "no"),
            )
            if confirm is None:
                return False
            if confirm.value == "no":
                version_sets.notice_decision(root, notice, action="defer")
                continue

            def authorize(item: AuthorizationReview) -> bool:
                consent = elicitor.seek(
                    item.name, description=f"{item.description}\n{item.problem}\nAuthorize this candidate acquisition? (yes/no)",
                    remedy=f"--authorize {item.name} true", empty_answer="no", validate=_choice("yes", "no"),
                )
                return consent is not None and consent.value == "yes"

            version_sets.select(root, identity, unvalidated=True, authorize=authorize)
            print("Upgrade selected. This launch will use it; use 'devcapsule project versions rollback' to return to a known-good set.")
        except (CliError, OSError) as exc:
            print(f"Upgrade could not finish: {exc}")
            answer = elicitor.seek(
                "continue-after-upgrade-failure", description="Continue launching the selected version set? (yes/no)",
                remedy="devcapsule project run", empty_answer="no", validate=_choice("yes", "no"),
            )
            if answer is None or answer.value == "no":
                return False
            version_sets.notice_decision(root, notice, action="defer")
    return True
