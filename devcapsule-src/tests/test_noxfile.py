from __future__ import annotations

from unittest.mock import Mock, call

import noxfile


def test_public_pex_is_skipped_and_advertised_for_dirty_repository() -> None:
    session = Mock()
    session.run.return_value = " M devcapsule-src/noxfile.py\n"

    built = noxfile.build_public_pex_if_clean(session)

    assert not built
    session.run.assert_called_once_with(
        "git",
        "-C",
        str(noxfile.REPO_ROOT),
        "status",
        "--porcelain",
        external=True,
        silent=True,
    )
    notice = session.log.call_args.args[0]
    assert "Not building dist/devcapsule.pex" in notice
    assert "may be stale" in notice
    assert "dist/devcapsule-local.pex" in notice


def test_public_pex_is_built_for_clean_repository() -> None:
    session = Mock()
    session.env = {}
    session.run.side_effect = ["", None]

    built = noxfile.build_public_pex_if_clean(session)

    assert built
    assert session.run.call_args_list == [
        call(
            "git",
            "-C",
            str(noxfile.REPO_ROOT),
            "status",
            "--porcelain",
            external=True,
            silent=True,
        ),
        call(
            str(noxfile.PROJECT_ROOT / "scripts" / "build-pex.sh"),
            "--output",
            str(noxfile.PUBLIC_PEX_PATH),
            "--allow-unpublished-revision",
            env={"PYTHON": "python"},
            external=True,
        ),
    ]


def test_public_pex_forwards_explicit_repository_only_to_packaging_step() -> None:
    session = Mock()
    session.env = {
        noxfile.PUBLIC_PEX_REPOSITORY_ENV: "https://github.com/example/devcapsule"
    }
    session.run.side_effect = ["", None]

    assert noxfile.build_public_pex_if_clean(session)

    assert session.run.call_args_list[1] == call(
        str(noxfile.PROJECT_ROOT / "scripts" / "build-pex.sh"),
        "--output",
        str(noxfile.PUBLIC_PEX_PATH),
        "--allow-unpublished-revision",
        env={
            "PYTHON": "python",
            "DEVCAPSULE_SOURCE_REPOSITORY": "https://github.com/example/devcapsule",
        },
        external=True,
    )
