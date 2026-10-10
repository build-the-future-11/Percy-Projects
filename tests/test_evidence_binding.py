"""Artificial evidence identities and actual v1 ledger compatibility fixtures."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_research_pipeline as fixtures

from research_pipeline import GateError, Project
from research_pipeline.ledger import MARKER


class EvidenceBindingTests(unittest.TestCase):
    # Reuse fixture builders, without inheriting/re-running the original suite.
    setUp = fixtures.LedgerTests.setUp
    file = fixtures.LedgerTests.file
    prepare = fixtures.LedgerTests.prepare
    run_manifest = fixtures.LedgerTests.run_manifest
    claim = fixtures.LedgerTests.claim
    lock = fixtures.LedgerTests.lock
    verification_receipt = fixtures.LedgerTests.verification_receipt
    release_manifest = fixtures.LedgerTests.release_manifest

    def add(self, artifact_id, kind, value, parents=()):
        if artifact_id == getattr(self, "changed_artifact", None):
            value = "ARTIFICIAL different retained bytes; receipt labels stay the same."
        return fixtures.LedgerTests.add(self, artifact_id, kind, value, parents)

    def sealed(self, label, changed_artifact=None):
        self.project = Project(self.base / label)
        self.counter = 0
        self.changed_artifact = changed_artifact
        self.lock()
        return self.project.read()["state"]["evidence_lock"]

    def restore_legacy(self, stage):
        fixture_path = Path(__file__).with_name("fixtures") / "legacy_ledger_v1.json"
        fixture = json.loads(fixture_path.read_text())
        self.assertTrue(fixture["artificial_fixture"])
        self.assertEqual(fixture["source_commit"], "a664fea4a5db0789bde91898328514ceb8d45a31")
        self.project = Project(self.base / ("legacy-" + stage))
        objects = self.project.root / ".research" / "objects"
        objects.mkdir(parents=True)
        for sha, text in fixture["objects"].items():
            (objects / sha).write_text(text)
        original = fixture["states"][stage]
        self.project.path.write_text(original)
        return original

    def test_different_evidence_bytes_cannot_share_a_seal(self):
        original = self.sealed("original")["sha256"]
        self.assertEqual(original, self.sealed("identical")["sha256"])
        for artifact_id in ("spec", "code", "config", "data", "split", "env", "dry",
                            "raw-proposed", "log-baseline", "analysis", "table"):
            with self.subTest(artifact=artifact_id):
                self.assertNotEqual(original, self.sealed(artifact_id, artifact_id)["sha256"])

    def test_manifest_is_byte_bound_and_stable_after_later_artifacts(self):
        sealed = self.sealed("new")
        self.assertEqual(sealed["schema_version"], 2)
        state = self.project.read()["state"]
        self.assertEqual(sealed["manifest"]["artifacts"], state["artifacts"])
        self.assertEqual(sealed["manifest"]["contract"], state["contract"])
        self.add("paper", "paper", "ARTIFICIAL paper, recorded after evidence lock.")
        self.assertEqual(self.project.read()["state"]["evidence_lock"], sealed)
        self.assertNotIn("paper", sealed["manifest"]["artifacts"])

    def test_review_cannot_attest_a_different_paper_or_environment(self):
        self.sealed("new")
        self.add("paper", "paper", "ARTIFICIAL paper bytes.")
        for field in ("paper_sha256", "environment_sha256"):
            with self.subTest(field=field):
                receipt = self.verification_receipt()
                receipt[field] = "0" * 64
                self.add("review-" + field, "verification", receipt)
                with self.assertRaisesRegex(GateError, "identity"):
                    self.project.apply("verify_review", {"verification_artifact": "review-" + field})
                self.assertEqual(self.project.read()["state"]["checkpoint"], 8)

    def test_authentic_legacy_states_remain_readable_byte_for_byte(self):
        for stage, checkpoint in (("locked", 8), ("verified", 9), ("complete", 10)):
            with self.subTest(stage=stage):
                original = self.restore_legacy(stage)
                result = self.project.read()
                self.assertEqual(result["state"]["checkpoint"], checkpoint)
                expected = json.loads(original.rpartition(MARKER)[2][:-5])["events"][-1]["sha256"]
                self.assertEqual(result["head"], expected)
                self.assertEqual(self.project.path.read_text(), original)

    def test_review_environment_must_be_the_frozen_release_environment(self):
        self.prepare(freeze=False)
        self.add("other-env", "environment", "ARTIFICIAL different environment.")
        self.project.apply("freeze", {"protocol_artifact": "protocol"})
        for arm in ("proposed", "baseline"):
            self.project.apply("run", self.run_manifest(arm))
        self.project.apply("claim", self.claim())
        self.project.apply("lock_evidence", {"disposition": "NEGATIVE", "scope": "Artificial fixture pair only",
                                              "reason": "Artificial result, without scientific execution."})
        self.add("paper", "paper", "ARTIFICIAL paper.")
        receipt = self.verification_receipt()
        receipt["environment_artifact"] = "other-env"
        receipt["environment_sha256"] = self.project.read()["state"]["artifacts"]["other-env"]["sha256"]
        self.add("wrong-environment-review", "verification", receipt)
        with self.assertRaisesRegex(GateError, "frozen release environment"):
            self.project.apply("verify_review", {"verification_artifact": "wrong-environment-review"})
        self.assertEqual(self.project.read()["state"]["checkpoint"], 8)

    def test_legacy_review_and_release_require_an_explicit_reseal(self):
        self.restore_legacy("locked")
        self.add("paper", "paper", "ARTIFICIAL paper.")
        self.add("new-review", "verification", self.verification_receipt())
        with self.assertRaisesRegex(GateError, "reseal"):
            self.project.apply("verify_review", {"verification_artifact": "new-review"})
        self.restore_legacy("verified")
        self.add("instructions", "other", "ARTIFICIAL reproduction instructions.")
        self.add("new-release", "release", self.release_manifest())
        with self.assertRaisesRegex(GateError, "reseal"):
            self.project.apply("complete", {"release_artifact": "new-release"})

    def test_reseal_preserves_prior_events_freeze_and_results_and_requires_review(self):
        self.restore_legacy("verified")
        old_history = self.project.history()["events"]
        old_state = self.project.read()["state"]
        self.project.apply("reseal_evidence", {"reason": "Bind retained artifact bytes; no scientific outcome changed."})
        current = self.project.read()["state"]
        self.assertEqual(self.project.history()["events"][:-1], old_history)
        self.assertEqual(current["freeze"], old_state["freeze"])
        self.assertEqual(current["runs"], old_state["runs"])
        self.assertEqual(current["scientific_result"], "NEGATIVE")
        self.assertEqual(current["checkpoint"], 8)
        self.assertIsNone(current["verification"])
        self.assertEqual(current["evidence_lock"]["manifest"]["previous_seal"], old_state["evidence_lock"])
        self.assertNotEqual(current["evidence_lock"]["sha256"], old_state["evidence_lock"]["sha256"])
        self.assertIn("independent", current["artifacts"])
        self.add("resealed-review", "verification", self.verification_receipt())
        self.project.apply("verify_review", {"verification_artifact": "resealed-review"})
        self.add("instructions", "other", "ARTIFICIAL reproduction instructions.")
        self.add("resealed-release", "release", self.release_manifest())
        self.project.apply("complete", {"release_artifact": "resealed-release"})
        self.assertEqual(self.project.read()["state"]["status"], "COMPLETE")

    def test_completed_legacy_studies_cannot_be_rewritten_by_reseal(self):
        original = self.restore_legacy("complete")
        with self.assertRaises(GateError):
            self.project.apply("reseal_evidence", {"reason": "ARTIFICIAL attempted mutation."})
        self.assertEqual(self.project.path.read_text(), original)

    def test_cli_explicit_reseal_and_verification_disclose_seal_version(self):
        self.restore_legacy("locked")
        repo = Path(__file__).resolve().parents[1]
        def cli(*args):
            return subprocess.run([sys.executable, "-m", "research_pipeline", *args],
                                  cwd=repo, capture_output=True, text=True, timeout=10)
        before = cli("verify", str(self.project.root))
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(json.loads(before.stdout)["evidence_seal_version"], 1)
        receipt = self.file({"reason": "ARTIFICIAL explicit artifact-byte reseal."}, ".json")
        reseal = cli("reseal-evidence", str(self.project.root), "--json", str(receipt))
        self.assertEqual(reseal.returncode, 0, reseal.stderr)
        verified = cli("verify", str(self.project.root))
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["evidence_seal_version"], 2)


if __name__ == "__main__":
    unittest.main()
