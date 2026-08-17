from __future__ import annotations

import os
from unittest.mock import Mock, call
from unittest.mock import patch

import noxfile


RELEASE_WORKFLOW = noxfile.REPO_ROOT / ".github" / "workflows" / "release-pex.yml"


def test_release_workflow_scopes_source_repository_to_pex_build_step() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    job_environment = workflow.split("    env:\n", 1)[1].split("    defaults:\n", 1)[0]
    build_step = workflow.split(
        "      - name: Build the self-contained release PEX\n", 1
    )[1].split("      - name:", 1)[0]

    assert "DEVCAPSULE_SOURCE_REPOSITORY" not in job_environment
    assert (
        "DEVCAPSULE_SOURCE_REPOSITORY: "
        "${{ github.server_url }}/${{ github.repository }}"
    ) in build_step


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
    session.run.side_effect = ["", None]

    with patch.dict(os.environ, {}, clear=True):
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
    session.run.side_effect = ["", None]

    with patch.dict(
        os.environ,
        {noxfile.PUBLIC_PEX_REPOSITORY_ENV: "https://github.com/example/devcapsule"},
        clear=True,
    ):
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


def test_clean_machine_proof_forwards_selected_pex() -> None:
    session = Mock()
    session.env = {
        noxfile.PEX_UNDER_TEST_ENV: "/tmp/published-devcapsule.pex",
        "DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE": "ubuntu:24.04",
    }

    noxfile.run_clean_machine_pex_test(session)

    session.run.assert_called_once_with(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "e2e",
        str(noxfile.PROJECT_ROOT / "tests" / "e2e" / "test_self_contained_pex.py"),
        env={
            noxfile.PEX_UNDER_TEST_ENV: "/tmp/published-devcapsule.pex",
            "DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE": "ubuntu:24.04",
        },
    )
