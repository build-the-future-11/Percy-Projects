"""Counterexamples for the replay runner, with no third-party dependencies."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "reproduce.py"
SPEC = importlib.util.spec_from_file_location("math11_reproduce", RUNNER)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CertificateIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "math11"
        shutil.copytree(ROOT / "release", self.root / "release")
        shutil.copytree(ROOT / "source", self.root / "source")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_complete_original_release_and_candidate_box(self) -> None:
        hashes = module.validate_release(self.root)
        self.assertEqual(len(hashes), 11)
        self.assertEqual(len(module.EXPECTED_CANDIDATES), 454)

    def test_modified_original_archive_is_rejected(self) -> None:
        archive = self.root / "source" / module.ARCHIVE_NAME
        archive.write_bytes(archive.read_bytes() + b"extra")
        with self.assertRaisesRegex(module.VerificationError, "archive SHA-256"):
            module.validate_release(self.root)

    def test_modified_verifier_is_rejected_before_execution(self) -> None:
        verifier = self.root / "release" / "verify.py"
        verifier.write_bytes(verifier.read_bytes() + b"\nprint('PASS: forged')\n")
        with self.assertRaisesRegex(module.VerificationError, "release member differs"):
            module.validate_release(self.root)

    def test_missing_member_is_rejected(self) -> None:
        (self.root / "release" / "paper.tex").unlink()
        with self.assertRaisesRegex(module.VerificationError, "members differ"):
            module.validate_release(self.root)

    def test_unmanifested_member_is_rejected(self) -> None:
        (self.root / "release" / "unverified_result.txt").write_text("PASS")
        with self.assertRaisesRegex(module.VerificationError, "members differ"):
            module.validate_release(self.root)

    def test_symlink_member_is_rejected(self) -> None:
        member = self.root / "release" / "paper.tex"
        member.unlink()
        member.symlink_to(ROOT / "release" / "paper.tex")
        with self.assertRaisesRegex(module.VerificationError, "not a regular file"):
            module.validate_release(self.root)

    def test_duplicate_or_missing_candidate_is_rejected(self) -> None:
        rows = (ROOT / "release" / "candidate_table.csv").read_bytes().splitlines()
        with self.assertRaisesRegex(module.VerificationError, "duplicate"):
            module.validate_candidate_table(b"\n".join(rows[:-1] + [rows[1]]))
        with self.assertRaisesRegex(module.VerificationError, "exactly 454"):
            module.validate_candidate_table(b"\n".join(rows[:-1]))

    def test_fractional_candidate_coefficient_is_rejected(self) -> None:
        data = (ROOT / "release" / "candidate_table.csv").read_bytes()
        with self.assertRaises(module.VerificationError):
            module.validate_candidate_table(data.replace(b"-2,-6,-3,", b"-2.5,-6,-3,", 1))

    def test_optimized_python_refuses_to_claim_success(self) -> None:
        for flag in ("-O", "-OO"):
            with self.subTest(flag=flag):
                completed = subprocess.run(
                    [sys.executable, flag, "-B", str(RUNNER), "--root", str(self.root)],
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("disables assertions", completed.stderr)
                self.assertNotIn('"status": "REPRODUCED"', completed.stdout)


if __name__ == "__main__":
    unittest.main()
