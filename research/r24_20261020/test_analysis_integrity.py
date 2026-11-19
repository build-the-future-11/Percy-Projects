"""Constructed JSON receipt checks; no model, dataset or scientific run."""

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import analyze


class AnalysisIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / "run"
        self.root.mkdir()
        self.metric = self.root / "p01_seed0" / "metrics.json"
        self.metric.parent.mkdir()
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({
            "phase": "DEVELOPMENT", "status": "DEVELOPMENT_FINISHED",
            "projects": ["01"], "seeds": [0], "failure_count": 0,
        }))
        self.metric.write_text(json.dumps({
            "phase": "DEVELOPMENT", "project": "01", "seed": 0,
            "scores": {"invariant_reservoir": {"nmse": .8},
                       "ridge_reservoir": {"nmse": 1.},
                       "linear_lag_baseline": {"nmse": .6}},
        }))
        self.inventory = self.root / "SHA256.json"
        self.refresh_inventory()
        self.output = self.parent / "analysis"

    def refresh_inventory(self):
        entries = {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in (self.manifest, self.metric)}
        self.inventory.write_text(json.dumps(entries))

    def invoke(self):
        with patch("sys.argv", ["analyze.py", str(self.root), "--output", str(self.output)]):
            with redirect_stdout(io.StringIO()):
                analyze.main()

    def assert_rejected_before_output(self):
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertFalse(self.output.exists())

    def test_valid_complete_receipts_keep_statistics_and_source_bytes(self):
        saved = {path: path.read_bytes() for path in (self.manifest, self.metric, self.inventory)}
        self.invoke()
        result = json.loads((self.output / "development_summary.json").read_text())
        self.assertEqual(result["scientific_disposition"], "UNCONFIRMED")
        stats = result["projects"]["01"]["statistics"]
        self.assertAlmostEqual(stats["error_reduction_vs_ridge_reservoir"]["mean"], .2)
        self.assertIsNone(stats["error_reduction_vs_ridge_reservoir"]["exploratory_bootstrap_95_percent_interval"])
        for path, before in saved.items():
            self.assertEqual(path.read_bytes(), before)

    def test_manifest_must_be_in_hash_inventory(self):
        inventory = json.loads(self.inventory.read_text())
        del inventory["manifest.json"]
        self.inventory.write_text(json.dumps(inventory))
        self.assert_rejected_before_output()

    def test_consumed_metric_must_be_in_hash_inventory(self):
        inventory = json.loads(self.inventory.read_text())
        del inventory["p01_seed0/metrics.json"]
        self.inventory.write_text(json.dumps(inventory))
        self.assert_rejected_before_output()

    def test_metric_changed_after_initial_inventory_check_is_rejected(self):
        original = analyze.verify_hashes

        def change_after_verification(root):
            inventory = original(root)
            changed = json.loads(self.metric.read_text())
            changed["scores"]["invariant_reservoir"]["nmse"] = .01
            self.metric.write_text(json.dumps(changed))
            return inventory

        with patch.object(analyze, "verify_hashes", change_after_verification):
            self.assert_rejected_before_output()

    def test_duplicate_manifest_phase_is_rejected(self):
        self.manifest.write_text(self.manifest.read_text().replace(
            '"phase": "DEVELOPMENT"', '"phase": "CONFIRMATORY", "phase": "DEVELOPMENT"'))
        self.refresh_inventory()
        self.assert_rejected_before_output()

    def test_duplicate_inventory_member_is_rejected(self):
        original = self.inventory.read_text()
        self.inventory.write_text('{"manifest.json": "' + '0' * 64 + '", ' + original[1:])
        self.assert_rejected_before_output()

    def test_nonstandard_nonfinite_receipt_value_is_rejected(self):
        self.metric.write_text(self.metric.read_text()[:-1] + ', "audit": NaN}')
        self.refresh_inventory()
        self.assert_rejected_before_output()

    def test_overflowing_json_receipt_value_is_rejected(self):
        self.metric.write_text(self.metric.read_text()[:-1] + ', "audit": 1e400}')
        self.refresh_inventory()
        self.assert_rejected_before_output()

    def test_analysis_output_cannot_modify_retained_run_directory(self):
        self.output = self.root / "new-analysis"
        self.assert_rejected_before_output()


if __name__ == "__main__":
    unittest.main(verbosity=2)
