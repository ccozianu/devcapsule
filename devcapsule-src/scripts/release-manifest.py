"""Create or verify the immutable inputs and outputs of a tag release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from zipfile import ZipFile
import tomllib
from pathlib import Path

from devcapsule.build_info import read_pex_build_info
from devcapsule.resolution_matrix import MATRICES
from devcapsule.platforms import Platform


def manifest(pex: Path, tag: str, revision: str) -> dict[str, object]:
    info = read_pex_build_info(pex)
    if (info.build_mnemonic, info.version, info.source_revision) != (tag, tag.removeprefix("v").replace("-rc", "rc"), revision):
        raise ValueError("Release PEX identity disagrees with the selected tag and revision")
    # Resolve representative supported needs, recording each distinct base.
    bases = sorted({
        str(tomllib.loads(MATRICES[Platform.LINUX_AMD64].resolve([need]).render_lock())["base"]["reference"])
        for need in ("python-ide", "frontend-ide")
    })
    return {
        "schema-version": 2,
        "tag": tag,
        "source-revision": revision,
        "version": info.version,
        "base-references": bases,
        "artifacts": {pex.name: hashlib.sha256(pex.read_bytes()).hexdigest()},
    }


def frozen_inputs(pex: Path) -> dict:
    project = Path(__file__).resolve().parents[1]
    with ZipFile(pex) as archive:
        distributions = json.loads(archive.read("PEX-INFO"))["distributions"]
    inspected = json.loads(subprocess.check_output(
        [str(pex.resolve())], env={**os.environ, "SCIE": "inspect"}, text=True))
    python = next(item for item in inspected["scie"]["lift"]["files"]
                  if item.get("key") == "python-distribution")
    return {
        "files": {name: hashlib.sha256((project / name).read_bytes()).hexdigest()
                  for name in ("requirements.txt", "dev-requirements.txt", "pyproject.toml", "scripts/build-pex.sh")},
        "distributions": {name: digest for name, digest in distributions.items()
                          if not name.startswith("devcapsule-")},
        "python": {key: python[key] for key in ("name", "hash")},
    }


def check_candidate(final: dict, candidate: dict, record: dict) -> None:
    if (candidate["tag"] != record["candidate-tag"]
            or candidate["source-revision"] != final["source-revision"]
            or candidate["artifacts"]["devcapsule.pex"] != record["candidate-sha256"]):
        raise ValueError("Candidate manifest disagrees with acceptance")
    for key in ("frozen-inputs", "base-references"):
        if candidate[key] != final[key]:
            raise ValueError(f"Final {key} differ from the accepted candidate")


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("tag")
    parser.add_argument("revision")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--candidate", type=Path)
    arguments = parser.parse_args()
    expected = manifest(Path("dist/devcapsule.pex"), arguments.tag, arguments.revision)
    expected["frozen-inputs"] = frozen_inputs(Path("dist/devcapsule.pex"))
    gate = json.loads(arguments.gate.read_text())
    if gate["tag"] != arguments.tag or gate["source-revision"] != arguments.revision:
        raise ValueError("Gate does not match artifact")
    expected["release-branch"] = gate["release-branch"]
    expected["prerelease"] = gate["prerelease"]
    if "integration" in gate:
        # A candidate carries how its source relates to main at build time,
        # including any explicit exception, so the published artifact is
        # self-describing.
        expected["integration"] = gate["integration"]
    path = Path("dist/release-manifest.json")
    if "promotion" in gate:
        expected["promotion"] = gate["promotion"]
        if not arguments.candidate:
            raise ValueError("Final release requires the downloaded candidate manifest")
        check_candidate(expected, json.loads(arguments.candidate.read_text()), gate["promotion"]["record"])
    if arguments.verify and "promotion" in expected:
        # Later main commits must not invalidate an otherwise identical retry.
        stored = json.loads(path.read_text())
        previous = stored.get("promotion", {})
        if previous.get("record") != gate["promotion"]["record"]:
            raise ValueError("Published promotion evidence has changed")
        expected["promotion"] = previous
    if arguments.verify and "integration" in expected:
        # Main integrating the candidate's commits after publication changes
        # the gate's live answer, not the published fact; keep what was built.
        expected["integration"] = json.loads(path.read_text()).get("integration", expected["integration"])
    if arguments.verify:
        if json.loads(path.read_text()) != expected:
            raise ValueError("Published release manifest does not match its artifacts and tagged source")
    else:
        path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
