"""``python -m devcapsule_webconsole``: start the console on its loopback port."""

from __future__ import annotations

import logging
import os
import sys
from typing import Sequence

import uvicorn

from .app import create_app
from .settings import LOG_LEVEL_ENV, SettingsError, log_level_from_environment, settings_from_arguments


def main(argv: Sequence[str] | None = None) -> int:
    try:
        settings = settings_from_arguments(sys.argv[1:] if argv is None else argv, os.environ)
    except SettingsError as error:
        print(f"devcapsule-webconsole: {error}", file=sys.stderr)
        return 2
    try:
        level = log_level_from_environment(os.environ)
    except SettingsError as error:
        level = logging.WARNING
        print(f"devcapsule-webconsole: {error}; logging at WARNING", file=sys.stderr, flush=True)
    configure_logging(level)
    print(
        f"devcapsule-webconsole: serving {settings.project} on http://{settings.listen}:{settings.port}/ "
        "(the run token is required on every request)",
        file=sys.stderr, flush=True,
    )
    uvicorn.run(
        create_app(settings), host=settings.listen, port=settings.port,
        log_level=logging.getLevelName(level).lower(), log_config=None,
    )
    return 0


def configure_logging(level: int) -> None:
    """Route the console's own records and uvicorn's to stderr at ``level``.

    The capsule's supervisor copies that stream into this component's
    session log, ``devcapsule-console.log``; the baseline is WARNING, the
    override ``$DEVCAPSULE_LOG_LEVEL`` lowers it (``devcapsule.logs``).
    ``log_config=None`` above keeps uvicorn from installing its own handlers
    beside this one, which would print every record twice.
    """

    logging.basicConfig(
        level=level, stream=sys.stderr, force=True,
        format="devcapsule-webconsole %(levelname)s %(name)s: %(message)s",
    )


if __name__ == "__main__":
    raise SystemExit(main())
