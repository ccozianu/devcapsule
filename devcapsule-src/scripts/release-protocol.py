"""Release ref, acceptance and integration gates; no mutations of Git refs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

TAG = re.compile(r"v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))(?:-rc(0|[1-9][0-9]*))?")


def identity(tag: str) -> tuple[str, str, bool]:
    match = TAG.fullmatch(tag)
    if not match:
        raise ValueError("Release tag must be vMAJOR.MINOR.PATCH[-rcN]")
    version, candidate = match.groups()
    return version, version + ("rc" + candidate if candidate is not None else ""), candidate is not None


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def ancestor(revision: str, ref: str) -> bool:
    result = subprocess.run(["git", "merge-base", "--is-ancestor", revision, ref], check=False)
    if result.returncode not in (0, 1):
        raise ValueError(f"Cannot check ancestry of {revision} in {ref}")
    return result.returncode == 0


def require_text(record: dict, key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Promotion record requires {key}")
    return value


def commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Evidence revisions must be full commit SHAs")
    if git("rev-parse", value + "^{commit}") != value:
        raise ValueError("Evidence does not identify a commit")
    return value


EXCEPTION_KEYS = ("authorized-by", "rationale", "forward-port-owner", "follow-up")


def exception_path(tag: str) -> str:
    return f"engineering-docs/releases/{tag}-integration-exception.json"


def unintegrated_commits(revision: str, main_ref: str) -> list[str]:
    """Commits the candidate carries that main has neither merged nor cherry-picked.

    Patch equivalence (``--cherry-pick``) recognizes a cherry-picked fix as
    integrated; merge commits carry no patch of their own and are ignored.
    """

    output = git("rev-list", "--right-only", "--cherry-pick", "--no-merges", f"{main_ref}...{revision}")
    return output.split()


def validate_candidate_integration(tag: str, revision: str, main_ref: str) -> dict:
    """A candidate builds only from source main already has, or with a stated exception.

    Owner rule 2026-09-13: every change since the release branch was cut must
    be merged or cherry-picked to mainline before a candidate is built, unless
    an explicit, documented exception travels with the candidate's own source
    (for example a patch to an old release too far from mainline). The
    exception file lives at ``exception_path(tag)`` in the tagged tree and
    carries the same fields the final promotion record's exception requires.
    """

    missing = unintegrated_commits(revision, main_ref)
    if not missing:
        return {"method": "mainline", "unintegrated-commits": []}
    path = exception_path(tag)
    shown = subprocess.run(["git", "show", f"{revision}:{path}"], check=False, text=True, capture_output=True)
    if shown.returncode != 0:
        listed = ", ".join(item[:12] for item in missing)
        raise ValueError(
            f"Candidate {tag} carries {len(missing)} commit(s) main has neither merged nor "
            f"cherry-picked ({listed}); integrate them to main first, or commit an explicit "
            f"exception at {path} on the release branch"
        )
    record = json.loads(shown.stdout)
    if not isinstance(record, dict) or record.get("schema-version") != 1 or record.get("tag") != tag:
        raise ValueError(f"Integration exception at {path} must have schema-version 1 and name {tag}")
    for key in EXCEPTION_KEYS:
        require_text(record, key)
    return {"method": "exception", "unintegrated-commits": missing, "record": record, "path": path}


def validate_promotion(tag: str, revision: str, record: dict, main_ref: str) -> None:
    version, _, is_candidate = identity(tag)
    candidate = require_text(record, "candidate-tag")
    candidate_version, _, candidate_kind = identity(candidate)
    if is_candidate or not candidate_kind or candidate_version != version:
        raise ValueError("Promotion must name a candidate for this final version")
    if record.get("schema-version") != 1 or record.get("tag") != tag:
        raise ValueError("Promotion record schema/tag mismatch")
    if record.get("source-revision") != revision or git("rev-parse", f"refs/tags/{candidate}^{{commit}}") != revision:
        raise ValueError("Final source must equal the accepted candidate commit")
    if not re.fullmatch(r"[0-9a-f]{64}", require_text(record, "candidate-sha256")):
        raise ValueError("Candidate checksum must be SHA-256")
    require_text(record, "accepted-by")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
        raise ValueError("Acceptance requires smoke/E2E evidence")
    integration = record.get("integration", {})
    if not isinstance(integration, dict):
        raise ValueError("Integration must be an object")
    baseline = commit(require_text(integration, "baseline"))
    if not ancestor(baseline, revision):
        raise ValueError("Integration baseline must be an ancestor of the candidate")
    method = integration.get("method")
    if method == "ancestry":
        if not ancestor(revision, main_ref):
            raise ValueError("Candidate source has not been merged to main")
    elif method == "reviewed":
        require_text(integration, "reviewed-by")
        require_text(integration, "rationale")
        # This is an explicit review assertion covering the entire baseline..RC
        # delta, not an automated claim of semantic patch equivalence.
        if integration.get("covers-release-delta") is not True:
            raise ValueError("Review must cover the complete release delta")
        revisions = integration.get("main-commits")
        if not isinstance(revisions, list) or not revisions:
            raise ValueError("Review requires integrated main commits")
        for item in revisions:
            if not ancestor(commit(item), main_ref):
                raise ValueError("Reviewed integration commit is absent from main")
    elif method == "exception":
        for key in ("authorized-by", "rationale", "forward-port-owner", "follow-up"):
            require_text(integration, key)
    else:
        raise ValueError("Integration method must be ancestry, reviewed, or exception")


def gate(tag: str, output: Path) -> dict:
    version, package_version, is_candidate = identity(tag)
    revision = git("rev-parse", f"refs/tags/{tag}^{{commit}}")
    if git("rev-parse", "HEAD") != revision:
        raise ValueError("Checkout must be the selected tag")
    branch = f"release-{version}"
    git("fetch", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}",
        "refs/heads/main:refs/remotes/origin/main")
    if not ancestor(revision, f"refs/remotes/origin/{branch}"):
        raise ValueError(f"Tag must belong to {branch}")
    result: dict = {"tag": tag, "source-revision": revision, "version": package_version,
              "prerelease": is_candidate, "release-branch": branch}
    if is_candidate:
        result["integration"] = validate_candidate_integration(tag, revision, "refs/remotes/origin/main")
    else:
        main_revision = git("rev-parse", "refs/remotes/origin/main")
        path = f"engineering-docs/releases/{tag}.json"
        record = json.loads(git("show", f"{main_revision}:{path}"))
        validate_promotion(tag, revision, record, main_revision)
        result["promotion"] = {"record": record, "main-revision": main_revision, "path": path}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("tag")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = gate(args.tag, args.output)
    if env := os.environ.get("GITHUB_ENV"):
        with open(env, "a") as stream:
            stream.write(f"DEVCAPSULE_EXPECTED_RELEASE_VERSION={result['version']}\n")
            stream.write(f"RELEASE_PRERELEASE={str(result['prerelease']).lower()}\n")
            if "promotion" in result:
                stream.write(f"ACCEPTED_CANDIDATE={result['promotion']['record']['candidate-tag']}\n")


if __name__ == "__main__":
    main()
