#!/usr/bin/env python3
"""Replay the byte-preserved October 2 certificate with assertions enabled.

This runner verifies the original archive and every extracted member before
executing the retained verifier. It never edits the retained scientific files.
The result is a computational replay, not an independent proof or novelty review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ARCHIVE_NAME = "Math11_Certified_Release_2026-10-02.zip"
ARCHIVE_SHA256 = "8f9d8b053271fc85c53c6294e2f3601d3bc4a34bdc795816cc5dfb3f928f5eeb"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CANDIDATES = {
    (a, b, c)
    for a in range(-2, 3)
    for b in range(-6, 7)
    for c in range(-3, 4)
    if (a, b, c) != (0, 0, 0)
}


class VerificationError(ValueError):
    """A required integrity or reproducibility check failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_candidate_table(data: bytes) -> int:
    """Check complete coefficient coverage; displayed decimals are descriptive."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    expected_header = [
        "a", "b", "c", "sigma0", "sigma1", "sigma2", "entry_height", "objective", "status"
    ]
    if reader.fieldnames != expected_header:
        raise VerificationError("candidate table has an unexpected header")
    seen: set[tuple[int, int, int]] = set()
    try:
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise VerificationError("candidate table has a malformed row")
            triple = tuple(int(row[key]) for key in ("a", "b", "c"))
            if triple in seen:
                raise VerificationError("candidate table has duplicate coefficients")
            seen.add(triple)
            if not all(math.isfinite(float(row[key])) for key in expected_header[3:8]):
                raise VerificationError("candidate table contains nonfinite display values")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise VerificationError(f"invalid candidate table: {exc}") from exc
    if seen != EXPECTED_CANDIDATES:
        raise VerificationError("candidate table does not cover exactly 454 nonzero triples")
    return len(seen)


def validate_release(root: Path) -> dict[str, str]:
    archive = root / "source" / ARCHIVE_NAME
    if archive.is_symlink() or not archive.is_file():
        raise VerificationError("the original archive must be a regular file")
    archive_bytes = archive.read_bytes()
    if sha256(archive_bytes) != ARCHIVE_SHA256:
        raise VerificationError("original archive SHA-256 mismatch")
    release = root / "release"
    if release.is_symlink() or not release.is_dir():
        raise VerificationError("the release directory is missing or is a symlink")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as bundle:
        members = bundle.infolist()
        names = [item.filename for item in members]
        if len(set(names)) != len(names):
            raise VerificationError("duplicate archive member")
        if any(Path(name).name != name or name in {".", ".."} for name in names):
            raise VerificationError("unexpected archive member path")
        actual = {path.relative_to(release).as_posix() for path in release.rglob("*")}
        if actual != set(names):
            raise VerificationError("extracted release members differ from the original archive")
        hashes: dict[str, str] = {}
        for name in names:
            path = release / name
            if path.is_symlink() or not path.is_file():
                raise VerificationError(f"release member is not a regular file: {name}")
            data = path.read_bytes()
            if data != bundle.read(name):
                raise VerificationError(f"retained release member differs: {name}")
            hashes[name] = sha256(data)
    for line in (release / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected_hash, name = line.split(maxsplit=1)
        if hashes.get(name) != expected_hash:
            raise VerificationError(f"original SHA256SUMS mismatch: {name}")
    validate_candidate_table((release / "candidate_table.csv").read_bytes())
    return hashes


def reproduce(root: Path = PROJECT_ROOT) -> dict[str, object]:
    if sys.flags.optimize:
        raise VerificationError("Python optimization disables assertions; run without -O or -OO")
    hashes = validate_release(root)
    started = time.perf_counter()
    # -I ignores PYTHONOPTIMIZE and caller imports. -B keeps the archive expansion
    # byte-preserved. The original verifier relies on Python assert statements.
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str((root / "release" / "verify.py").resolve())],
        cwd=root / "release",
        capture_output=True,
        check=False,
        timeout=300,
    )
    if completed.returncode != 0 or completed.stderr:
        raise VerificationError(
            f"original verifier failed ({completed.returncode}): "
            f"{completed.stderr.decode('utf-8', errors='replace')}"
        )
    if completed.stdout != (root / "release" / "verifier_output.txt").read_bytes():
        raise VerificationError("verifier output differs from the retained successful output")
    # A second check detects accidental source changes during the run.
    if validate_release(root) != hashes:
        raise VerificationError("release changed during replay")
    return {
        "schema": "percy.math11.certificate_replay.v1",
        "status": "REPRODUCED",
        "scope": "October 2, 2026 exact computational certificate",
        "archive_sha256": ARCHIVE_SHA256,
        "member_sha256": hashes,
        "candidate_triples": len(EXPECTED_CANDIDATES),
        "log_lattice_cells": 16 * 16,
        "stdout_sha256": sha256(completed.stdout),
        "stdout_matches_original": True,
        "assertions_enabled": True,
        "python": sys.version.split()[0],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "independent_proof_review_completed": False,
        "literature_novelty_established": False,
        "excluded_claims": [
            "the numerical logarithmic exceptional density is a theorem",
            "ordinary integer-sampling density does not converge",
            "all switching intervals have been explicitly enumerated",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = reproduce(args.root.resolve())
    except (VerificationError, OSError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Evidence receipts are immutable unless a new path is selected.
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
