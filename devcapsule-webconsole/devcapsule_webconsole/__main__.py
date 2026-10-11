"""``python -m devcapsule_webconsole``: start the console on its loopback port."""

from __future__ import annotations

import os
import sys
from typing import Sequence

import uvicorn

from .app import create_app
from .settings import SettingsError, settings_from_arguments


def main(argv: Sequence[str] | None = None) -> int:
    try:
        settings = settings_from_arguments(sys.argv[1:] if argv is None else argv, os.environ)
    except SettingsError as error:
        print(f"devcapsule-webconsole: {error}", file=sys.stderr)
        return 2
    print(
        f"devcapsule-webconsole: serving {settings.project} on http://{settings.listen}:{settings.port}/ "
        "(the run token is required on every request)",
        file=sys.stderr, flush=True,
    )
    uvicorn.run(create_app(settings), host=settings.listen, port=settings.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
