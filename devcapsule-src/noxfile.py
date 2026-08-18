from __future__ import annotations

import os
from pathlib import Path

import nox


nox.options.sessions = ["build"]
nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True

PROJECT_ROOT = Path(__file__).parent
REPO_ROOT = PROJECT_ROOT.parent
TEST_PEX_PATH = PROJECT_ROOT / "dist" / "devcapsule-local.pex"
PUBLIC_PEX_PATH = PROJECT_ROOT / "dist" / "devcapsule.pex"
PUBLIC_PEX_REPOSITORY_ENV = "DEVCAPSULE_PUBLIC_PEX_SOURCE_REPOSITORY"
PEX_UNDER_TEST_ENV = "DEVCAPSULE_PEX_UNDER_TEST"


def install_locked(session: nox.Session) -> None:
    session.install("-r", str(PROJECT_ROOT / "dev-requirements.txt"))
    session.install("-e", str(PROJECT_ROOT), "--no-deps")


def check_python_syntax(session: nox.Session) -> None:
    session.run("python", "-m", "compileall", "-q", str(PROJECT_ROOT / "devcapsule"))


def check_shell_syntax(session: nox.Session) -> None:
    scripts = [
        *sorted((REPO_ROOT / "docker4pycharm").glob("*.sh")),
        *sorted((PROJECT_ROOT / "scripts").glob("*.sh")),
        *sorted((PROJECT_ROOT / "devcapsule" / "assets").rglob("*.sh")),
    ]
    for script in scripts:
        session.run("bash", "-n", str(script), external=True)


def run_tests(session: nox.Session) -> None:
    session.run("python", "-m", "pytest", str(PROJECT_ROOT / "tests"))


def run_packaging_tests(session: nox.Session) -> None:
    session.run(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "integration",
        str(PROJECT_ROOT / "tests" / "integration"),
    )


def run_e2e_tests(session: nox.Session) -> None:
    environment: dict[str, str] = {}
    for name in (
        "DEVCAPSULE_E2E_BASE_IMAGE",
        "DEVCAPSULE_EARLY_EXIT_E2E_IMAGE",
        "DEVCAPSULE_CONTRIBUTOR_E2E_IMAGE",
        "DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE",
    ):
        value = session.env.get(name)
        if value is not None:
            environment[name] = value
    session.run(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "e2e and not recursive_e2e",
        str(PROJECT_ROOT / "tests" / "e2e"),
        env=environment,
    )


def run_recursive_e2e_tests(session: nox.Session) -> None:
    session.run(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "recursive_e2e or contributor_e2e",
        str(PROJECT_ROOT / "tests" / "e2e"),
    )


def run_typecheck(session: nox.Session) -> None:
    session.run(
        "python",
        "-m",
        "mypy",
        str(PROJECT_ROOT / "devcapsule"),
        str(PROJECT_ROOT / "tests"),
        str(PROJECT_ROOT / "noxfile.py"),
    )


def run_smoke(session: nox.Session) -> None:
    session.run("python", "-m", "devcapsule", "--help")
    session.run("python", "-m", "devcapsule", "version", "--json")
    session.run("python", "-m", "devcapsule", "runtime", success_codes=[2])
    session.run("python", "-m", "devcapsule", "host-open", "--help")
    session.run("python", "-m", "devcapsule", "pycharm", "run", "--help")
    session.run("python", "-m", "devcapsule", "project", "--help")
    session.run("python", "-m", "devcapsule", "project", "list", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "list", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "resolve", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "set", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "bind", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "authorize", "--help")
    session.run("python", "-m", "devcapsule", "project", "run", "--help")
    session.run("python", "-m", "devcapsule", "project", "run-image", "--help")
    session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "preflight", "--help")
    session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "run", "--help")
    session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "launch-successor", "--help")
    session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "inspect-successor", "--help")
    session.run("python", "-m", "devcapsule", "images", "list", "--help")
    session.run("python", "-m", "devcapsule", "images", "build", "--help")
    session.run("python", "-m", "devcapsule", "pycharm", "build", "--help")
    session.run("python", "-m", "devcapsule", "vscode_with_claude", "--help")
    session.run("python", "-m", "devcapsule", "codium_with_claude", "build", "--help")
    session.run("python", "-m", "devcapsule", "codium_with_claude", "run", "--help")
    session.run(str(REPO_ROOT / "docker4pycharm" / "run-pycharm-container.sh"), "--help", external=True)


def build_test_pex(session: nox.Session) -> None:
    session.run(
        str(PROJECT_ROOT / "scripts" / "build-pex.sh"),
        "--output",
        str(TEST_PEX_PATH),
        "--allow-local-source",
        env={"PYTHON": "python"},
        external=True,
    )


def build_public_pex_if_clean(session: nox.Session) -> bool:
    status = session.run(
        "git",
        "-C",
        str(REPO_ROOT),
        "status",
        "--porcelain",
        external=True,
        silent=True,
    )
    if str(status).strip():
        session.log(
            "Not building dist/devcapsule.pex: the repository has uncommitted "
            "changes. Any existing file at that path is unchanged and may be "
            "stale. The local validation artifact is dist/devcapsule-local.pex."
        )
        return False

    build_environment = {"PYTHON": "python"}
    explicit_repository = os.environ.get(PUBLIC_PEX_REPOSITORY_ENV)
    if explicit_repository:
        build_environment["DEVCAPSULE_SOURCE_REPOSITORY"] = explicit_repository
    session.run(
        str(PROJECT_ROOT / "scripts" / "build-pex.sh"),
        "--output",
        str(PUBLIC_PEX_PATH),
        "--allow-unpublished-revision",
        env=build_environment,
        external=True,
    )
    return True


def smoke_pex(session: nox.Session, path: Path = TEST_PEX_PATH) -> None:
    session.run(str(path), "--help", external=True)
    session.run(str(path), "version", "--json", external=True)
    session.run(str(path), "runtime", success_codes=[2], external=True)
    session.run(str(path), "host-open", "--help", external=True)
    session.run(str(path), "pycharm", "run", "--help", external=True)
    session.run(str(path), "project", "--help", external=True)
    session.run(str(path), "project", "list", "--help", external=True)
    session.run(str(path), "project", "config", "list", "--help", external=True)
    session.run(str(path), "project", "config", "resolve", "--help", external=True)
    session.run(str(path), "project", "config", "set", "--help", external=True)
    session.run(str(path), "project", "config", "bind", "--help", external=True)
    session.run(str(path), "project", "config", "authorize", "--help", external=True)
    session.run(str(path), "project", "run", "--help", external=True)
    session.run(str(path), "project", "run-image", "--help", external=True)
    session.run(
        str(path), "project", "recursive-e2e", "preflight", "--help", external=True
    )
    session.run(str(path), "project", "recursive-e2e", "run", "--help", external=True)
    session.run(
        str(path), "project", "recursive-e2e", "launch-successor", "--help", external=True
    )
    session.run(
        str(path), "project", "recursive-e2e", "inspect-successor", "--help", external=True
    )
    session.run(str(path), "images", "list", "--help", external=True)
    session.run(str(path), "images", "build", "--help", external=True)
    session.run(str(path), "pycharm", "build", "--help", external=True)
    session.run(str(path), "vscode_with_claude", "--help", external=True)
    session.run(str(path), "codium_with_claude", "build", "--help", external=True)
    session.run(str(path), "codium_with_claude", "run", "--help", external=True)


def run_clean_machine_pex_test(session: nox.Session) -> None:
    environment: dict[str, str] = {}
    for name in ("DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE", PEX_UNDER_TEST_ENV):
        value = session.env.get(name) or os.environ.get(name)
        if value is not None:
            environment[name] = value
    session.run(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "e2e",
        str(PROJECT_ROOT / "tests" / "e2e" / "test_self_contained_pex.py"),
        env=environment,
    )


@nox.session(python="3.12")
def syntax(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    check_shell_syntax(session)


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    run_tests(session)


@nox.session(python="3.12")
def smoke(session: nox.Session) -> None:
    install_locked(session)
    run_smoke(session)


@nox.session(python="3.12")
def typecheck(session: nox.Session) -> None:
    install_locked(session)
    run_typecheck(session)


@nox.session(python="3.12")
def pex(session: nox.Session) -> None:
    install_locked(session)
    check_shell_syntax(session)
    build_test_pex(session)
    smoke_pex(session)


@nox.session(python="3.12")
def integration(session: nox.Session) -> None:
    install_locked(session)
    build_test_pex(session)
    run_packaging_tests(session)


@nox.session(python="3.12")
def pex_clean_machine(session: nox.Session) -> None:
    """Prove the eager PEX scie on a networkless image with no host Python."""

    install_locked(session)
    selected_pex = session.env.get(PEX_UNDER_TEST_ENV) or os.environ.get(
        PEX_UNDER_TEST_ENV
    )
    if not selected_pex:
        build_test_pex(session)
    run_clean_machine_pex_test(session)


@nox.session(python="3.12")
def e2e(session: nox.Session) -> None:
    install_locked(session)
    build_test_pex(session)
    run_e2e_tests(session)


@nox.session(python="3.12")
def recursive_dogfood_e2e(session: nox.Session) -> None:
    """Run explicit host-sensitive recursive dogfood checks."""

    install_locked(session)
    session.run(
        "python",
        "-m",
        "devcapsule",
        "project",
        "--path",
        str(REPO_ROOT),
        "recursive-e2e",
        "run",
        "--json",
    )
    run_recursive_e2e_tests(session)


@nox.session(python="3.12")
def build(session: nox.Session) -> None:
    install_locked(session)
    check_python_syntax(session)
    check_shell_syntax(session)
    run_typecheck(session)
    run_tests(session)
    run_smoke(session)
    build_test_pex(session)
    smoke_pex(session)
    run_packaging_tests(session)
    if build_public_pex_if_clean(session):
        smoke_pex(session, PUBLIC_PEX_PATH)
