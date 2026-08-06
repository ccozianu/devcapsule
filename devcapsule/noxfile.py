from __future__ import annotations

from pathlib import Path

import nox


nox.options.sessions = ["build"]
nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True

PROJECT_ROOT = Path(__file__).parent
REPO_ROOT = PROJECT_ROOT.parent
TEST_PEX_PATH = PROJECT_ROOT / "dist" / "devcapsule-local.pex"
PUBLIC_PEX_PATH = PROJECT_ROOT / "dist" / "devcapsule.pex"


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
    base_image = session.env.get("DEVCAPSULE_E2E_BASE_IMAGE")
    if base_image is not None:
        environment["DEVCAPSULE_E2E_BASE_IMAGE"] = base_image
    session.run(
        "python",
        "-m",
        "pytest",
        "--no-cov",
        "-m",
        "e2e",
        str(PROJECT_ROOT / "tests" / "e2e"),
        env=environment,
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
    session.run("python", "-m", "devcapsule", "pycharm", "run", "--help")
    session.run("python", "-m", "devcapsule", "project", "--help")
    session.run("python", "-m", "devcapsule", "project", "list", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "list", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "resolve", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "set", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "bind", "--help")
    session.run("python", "-m", "devcapsule", "project", "config", "authorize", "--help")
    session.run("python", "-m", "devcapsule", "project", "run-image", "--help")
    session.run("python", "-m", "devcapsule", "recursive-e2e", "preflight", "--help")
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

    session.run(
        str(PROJECT_ROOT / "scripts" / "build-pex.sh"),
        "--output",
        str(PUBLIC_PEX_PATH),
        "--allow-unpublished-revision",
        env={"PYTHON": "python"},
        external=True,
    )
    return True


def smoke_pex(session: nox.Session, path: Path = TEST_PEX_PATH) -> None:
    session.run("python", str(path), "--help")
    session.run("python", str(path), "version", "--json")
    session.run("python", str(path), "runtime", success_codes=[2])
    session.run("python", str(path), "pycharm", "run", "--help")
    session.run("python", str(path), "project", "--help")
    session.run("python", str(path), "project", "list", "--help")
    session.run("python", str(path), "project", "config", "list", "--help")
    session.run("python", str(path), "project", "config", "resolve", "--help")
    session.run("python", str(path), "project", "config", "set", "--help")
    session.run("python", str(path), "project", "config", "bind", "--help")
    session.run("python", str(path), "project", "config", "authorize", "--help")
    session.run("python", str(path), "project", "run-image", "--help")
    session.run("python", str(path), "recursive-e2e", "preflight", "--help")
    session.run("python", str(path), "images", "list", "--help")
    session.run("python", str(path), "images", "build", "--help")
    session.run("python", str(path), "pycharm", "build", "--help")
    session.run("python", str(path), "vscode_with_claude", "--help")
    session.run("python", str(path), "codium_with_claude", "build", "--help")
    session.run("python", str(path), "codium_with_claude", "run", "--help")


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
def e2e(session: nox.Session) -> None:
    install_locked(session)
    build_test_pex(session)
    run_e2e_tests(session)


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
