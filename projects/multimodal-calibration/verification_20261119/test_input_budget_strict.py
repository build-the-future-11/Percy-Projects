"""Constructed metadata admission regressions; no processor or scientific run."""

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "verification" / "test_input_budget.py"
spec = importlib.util.spec_from_file_location("input_budget_original_fixtures", FIXTURE_PATH)
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
audit = fixtures.audit


class StrictInputBudgetTests(unittest.TestCase):
    def invoke(self, rows_text, expected_text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = root / "rows.json"
            expected = root / "expected.json"
            rows.write_text(rows_text, encoding="utf-8")
            expected.write_text(expected_text, encoding="utf-8")
            output = io.StringIO()
            with patch("sys.argv", ["check_input_budget.py", "--rows", str(rows),
                                     "--expected-records", str(expected)]):
                with redirect_stdout(output):
                    status = audit.main()
            return status, json.loads(output.getvalue())

    def test_pixel_shape_requires_exact_integers(self):
        for shape in ([64.0, 1176], [64, 1176.0]):
            rows, expected = fixtures.fixture()
            fixtures.update_shared(rows[0], "pixel_values_shape", shape)
            with self.subTest(shape=shape), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(rows, expected)

    def test_option_budget_requires_exact_nested_types(self):
        variants = (("context_token_count", 56.0),
                    ("attention_mask_token_count", 56.0),
                    ("image_grid_thw", [[True, 8, 8]]),
                    ("image_grid_thw", [[1, 8.0, 8]]),
                    ("pixel_values_shape", [64.0, 1176]))
        for key, value in variants:
            rows, expected = fixtures.fixture()
            rows[0]["option_label_processor_sequences"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(rows, expected)

    def test_cli_rejects_duplicate_and_nonfinite_json(self):
        rows, expected = fixtures.fixture()
        rows_text, expected_text = json.dumps(rows), json.dumps(expected)
        cases = [
            (rows_text.replace('"condition": "S0"',
                               '"condition": "S5", "condition": "S0"', 1), expected_text),
            (rows_text, expected_text.replace('"record_id": "synthetic-square"',
                                               '"record_id": "other", "record_id": "synthetic-square"', 1)),
        ]
        for number in ("NaN", "Infinity", "-Infinity", "1e400"):
            cases.append((rows_text.replace('{', '{"unused_audit": ' + number + ', ', 1), expected_text))
        for index, (row_input, expected_input) in enumerate(cases):
            with self.subTest(case=index):
                status, result = self.invoke(row_input, expected_input)
                self.assertEqual(status, 2)
                self.assertEqual(result["status"], "STRUCTURAL_METADATA_FAIL")
                self.assertFalse(result["execution_authorized"])

    def test_cli_valid_panel_remains_metadata_only(self):
        rows, expected = fixtures.fixture()
        status, result = self.invoke(json.dumps(rows), json.dumps(expected))
        self.assertEqual(status, 0)
        self.assertEqual(result["status"], "STRUCTURAL_METADATA_PASS_ONLY")
        self.assertFalse(result["runtime_or_scientific_validation"])
        self.assertFalse(result["execution_authorized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
