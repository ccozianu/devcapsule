"""Unit tests of ``scripts/validate_unittests_follow_conventions.py``, the gate's check of the unit-test conventions.

Each test builds the suite it checks under ``tmp_path``; the rules under
test are the three *Unit Tests* in WORKFLOW-LOCAL.md states.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "validate_unittests_follow_conventions.py"


def _load(path: Path) -> Any:
    """The script as a module; registered in ``sys.modules`` so its dataclasses resolve their annotations."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


conventions = _load(_SCRIPT)


def _module(path: str, source: str) -> Any:
    return conventions.parse_module(Path(path), source)


DOCUMENTED = 'def test_one():\n    """It holds."""\n    assert True\n'
UNDOCUMENTED = "def test_one():\n    assert True\n"


def test_module_markers_are_read_from_pytestmark_in_both_forms() -> None:
    """Precondition: a module assigns ``pytestmark`` a single marker or a list.
    Action: parse it. Postcondition: every marker name is reported."""
    single = _module("tests/a.py", "import pytest\npytestmark = pytest.mark.legacy\n")
    listed = _module("tests/b.py", "import pytest\npytestmark = [pytest.mark.e2e, pytest.mark.flaky(reason='x')]\n")
    assert single.markers == {"legacy"} and single.legacy
    assert listed.markers == {"e2e", "flaky"} and not listed.legacy


def test_a_test_function_is_recorded_with_its_decorators_and_without_trailing_whitespace() -> None:
    """Precondition: a test function with a decorator and trailing spaces.
    Action: parse it. Postcondition: its source starts at the decorator and
    carries no trailing whitespace, so a whitespace-only edit is not a change."""
    source = "import pytest\n\n@pytest.mark.parametrize('x', [1])\ndef test_one(x):   \n    assert x\n"
    module = _module("tests/a.py", source)
    assert module.functions == {"test_one": "@pytest.mark.parametrize('x', [1])\ndef test_one(x):\n    assert x"}


def test_methods_of_test_classes_are_qualified_by_their_class() -> None:
    """Precondition: a ``Test`` class holding a test method. Action: parse.
    Postcondition: the method is listed under ``Class.method``."""
    module = _module("tests/a.py", "class TestThing:\n    def test_one(self):\n        assert True\n")
    assert list(module.functions) == ["TestThing.test_one"]
    assert module.undocumented == (("TestThing.test_one", 2),)


def test_the_mirror_maps_a_test_file_to_its_public_or_private_module(tmp_path: Path) -> None:
    """Precondition: ``devcapsule/a/b.py`` and ``devcapsule/a/_c.py`` exist.
    Action: resolve the mirror for their test paths and for a stranger.
    Postcondition: both modules resolve, the stranger does not."""
    (tmp_path / "devcapsule" / "a").mkdir(parents=True)
    (tmp_path / "devcapsule" / "a" / "b.py").write_text("")
    (tmp_path / "devcapsule" / "a" / "_c.py").write_text("")
    assert conventions.mirrored_module(Path("tests/unit/devcapsule/a/test_b.py"), tmp_path) == Path("devcapsule/a/b.py")
    assert conventions.mirrored_module(Path("tests/unit/devcapsule/a/test_c.py"), tmp_path) == Path("devcapsule/a/_c.py")
    assert conventions.mirrored_module(Path("tests/unit/devcapsule/a/test_d.py"), tmp_path) is None
    assert conventions.mirrored_module(Path("tests/test_b.py"), tmp_path) is None


def test_a_documented_test_in_the_mirror_of_an_existing_module_passes(tmp_path: Path) -> None:
    """Precondition: a non-legacy, documented test file mirroring a real module.
    Action: check. Postcondition: no breach."""
    (tmp_path / "devcapsule").mkdir()
    (tmp_path / "devcapsule" / "thing.py").write_text("")
    module = _module("tests/unit/devcapsule/test_thing.py", DOCUMENTED)
    assert conventions.check([module], {}, tmp_path) == []


def test_a_non_legacy_file_outside_the_mirror_needs_a_heavier_suite_marker(tmp_path: Path) -> None:
    """Precondition: two documented files outside the mirror, one marked e2e.
    Action: check. Postcondition: only the unmarked one is a breach, naming the mirror."""
    marked = _module("tests/test_flow.py", "import pytest\npytestmark = pytest.mark.e2e\n" + DOCUMENTED)
    unmarked = _module("tests/test_flow2.py", DOCUMENTED)
    breaches = conventions.check([marked, unmarked], {}, tmp_path)
    assert len(breaches) == 1 and breaches[0].startswith("tests/test_flow2.py: a unit test file lives under tests/unit")


def test_a_mirror_file_naming_no_module_is_a_breach(tmp_path: Path) -> None:
    """Precondition: a documented file in the mirror whose name matches no module.
    Action: check. Postcondition: one breach naming the file."""
    module = _module("tests/unit/devcapsule/test_nothing.py", DOCUMENTED)
    breaches = conventions.check([module], {}, tmp_path)
    assert breaches == ["tests/unit/devcapsule/test_nothing.py: no module under devcapsule-src is mirrored by this file name"]


def test_an_undocumented_test_in_a_non_legacy_file_is_a_breach_at_its_line(tmp_path: Path) -> None:
    """Precondition: a mirror file with one undocumented test on line 3.
    Action: check. Postcondition: the breach names the function and the line."""
    (tmp_path / "devcapsule").mkdir()
    (tmp_path / "devcapsule" / "thing.py").write_text("")
    module = _module("tests/unit/devcapsule/test_thing.py", "import pytest\n\n" + UNDOCUMENTED)
    assert conventions.check([module], {}, tmp_path) == [
        "tests/unit/devcapsule/test_thing.py:3: test_one has no docstring stating its contract"
    ]


def test_a_legacy_file_is_exempt_from_placement_and_docstrings(tmp_path: Path) -> None:
    """Precondition: an undocumented legacy file outside the mirror, unchanged from base.
    Action: check against that base. Postcondition: no breach."""
    source = "import pytest\npytestmark = pytest.mark.legacy\n" + UNDOCUMENTED
    module = _module("tests/test_old.py", source)
    base = _module("tests/test_old.py", UNDOCUMENTED)
    assert conventions.check([module], {module.path: base}, tmp_path) == []


def test_a_legacy_file_may_lose_tests_but_not_gain_or_change_them(tmp_path: Path) -> None:
    """Precondition: base holds tests a, b, c; the legacy file drops a, keeps b, changes c and adds d.
    Action: check. Postcondition: c and d are breaches, a and b are not."""
    base = _module("tests/test_old.py", "def test_a():\n    pass\ndef test_b():\n    pass\ndef test_c():\n    pass\n")
    module = _module("tests/test_old.py", "import pytest\npytestmark = pytest.mark.legacy\n"
                     "def test_b():\n    pass\ndef test_c():\n    assert 1\ndef test_d():\n    pass\n")
    breaches = conventions.check([module], {module.path: base}, tmp_path)
    assert breaches == [
        "tests/test_old.py: test_c changed in a legacy file; fix it to the convention and move it to the mirror",
        "tests/test_old.py: test_d was added to a legacy file; put it in the mirror",
    ]


def test_a_marker_other_than_legacy_cannot_be_added_to_a_legacy_file(tmp_path: Path) -> None:
    """Precondition: base has no module marker; the legacy file adds legacy and skip.
    Action: check. Postcondition: skip is a breach, legacy is not."""
    base = _module("tests/test_old.py", UNDOCUMENTED)
    module = _module("tests/test_old.py", "import pytest\npytestmark = [pytest.mark.legacy, pytest.mark.skip]\n" + UNDOCUMENTED)
    assert conventions.check([module], {module.path: base}, tmp_path) == [
        "tests/test_old.py: marker 'skip' was added to a legacy file"
    ]


def test_a_legacy_file_the_base_lacks_is_refused(tmp_path: Path) -> None:
    """Precondition: a legacy file with no base version. Action: check.
    Postcondition: one breach saying new tests follow the convention."""
    module = _module("tests/test_new.py", "import pytest\npytestmark = pytest.mark.legacy\n" + UNDOCUMENTED)
    breaches = conventions.check([module], {module.path: None}, tmp_path)
    assert len(breaches) == 1 and breaches[0].endswith("new tests follow the convention")


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *arguments],
                   cwd=root, check=True, capture_output=True)


def test_main_compares_legacy_files_with_the_merge_base_and_exits_one_on_a_breach(tmp_path: Path) -> None:
    """Precondition: a repository whose base commit holds a legacy test, then a
    commit on a branch that changes that test's body. Action: run ``main`` with
    the base ref. Postcondition: exit 1, the breach on stderr, the summary on stdout."""
    root = tmp_path / "devcapsule-src"
    tests = root / "tests"
    tests.mkdir(parents=True)
    (tests / "test_old.py").write_text("import pytest\npytestmark = pytest.mark.legacy\n" + UNDOCUMENTED)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "base")
    _git(root, "checkout", "-q", "-b", "slice")
    (tests / "test_old.py").write_text("import pytest\npytestmark = pytest.mark.legacy\ndef test_one():\n    assert 1\n")
    _git(root, "commit", "-q", "-am", "change")
    status = conventions.main(["--base", "main", "--project-root", str(root)])
    assert status == 1


def test_main_passes_a_suite_that_only_shrinks_its_legacy_files(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Precondition: a repository whose branch removes one legacy test and adds a
    documented mirror test of an existing module. Action: run ``main``.
    Postcondition: exit 0 and the summary counts one legacy file with one test."""
    root = tmp_path / "devcapsule-src"
    (root / "devcapsule").mkdir(parents=True)
    (root / "devcapsule" / "thing.py").write_text("")
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_old.py").write_text("import pytest\npytestmark = pytest.mark.legacy\n" + UNDOCUMENTED + "def test_two():\n    pass\n")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "base")
    _git(root, "checkout", "-q", "-b", "slice")
    (tests / "test_old.py").write_text("import pytest\npytestmark = pytest.mark.legacy\n" + UNDOCUMENTED)
    (tests / "unit" / "devcapsule").mkdir(parents=True)
    (tests / "unit" / "devcapsule" / "test_thing.py").write_text(DOCUMENTED)
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "shrink")
    status = conventions.main(["--base", "main", "--project-root", str(root)])
    assert status == 0
    assert "1 legacy files holding 1 legacy tests; 1 files follow the convention; 0 breaches" in capsys.readouterr().out


def test_main_fails_when_the_base_cannot_be_resolved(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Precondition: a repository with no ref named ``nowhere``. Action: run ``main``
    with that base. Postcondition: exit 1 and a message naming the base."""
    root = tmp_path / "devcapsule-src"
    (root / "tests").mkdir(parents=True)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "commit", "-q", "--allow-empty", "-m", "base")
    assert conventions.main(["--base", "nowhere", "--project-root", str(root)]) == 1
    assert "cannot resolve base 'nowhere'" in capsys.readouterr().err
