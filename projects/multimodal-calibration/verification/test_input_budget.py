"""Synthetic metadata fixtures only: no real image, processor, model or outcome."""

import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "proposed" / "check_input_budget.py"
spec = importlib.util.spec_from_file_location("check_input_budget", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def fixture():
    expected = [{"record_id": "synthetic-square", "option_labels": ["A", "B", "C", "D"]},
                {"record_id": "synthetic-wide", "option_labels": ["A", "B", "C"]}]
    rows = []
    for item, dimensions, grid in zip(expected, ([112, 112], [112, 168]), ([1, 8, 8], [1, 8, 12])):
        for condition in audit.CONDITIONS:
            record = item["record_id"]
            tokens = grid[1] * grid[2] // 4
            row = {"record_id": record, "condition": condition,
                   "model_revision": audit.REVISION, "transformers_version": "4.57.1", "use_fast": False,
                   "image_count": 1, "padding_enabled": False, "truncation_enabled": False,
                   "truncated_token_count": 0,
                   "processor_identity_sha256": digest("synthetic-identity"),
                   "processor_config_sha256": digest("synthetic-config"),
                   "canonical_dimensions": dimensions.copy(), "transformed_dimensions": dimensions.copy(),
                   "processed_dimensions": dimensions.copy(), "image_grid_thw": [grid.copy()],
                   "visual_token_count": tokens, "context_token_count": 40 + tokens,
                   "context_token_ids_sha256": digest(record + "-context"),
                   "attention_mask_token_count": 40 + tokens, "attention_mask_sha256": digest(record + "-mask"),
                   "text_prompt_sha256": digest(record + "-prompt"),
                   "pixel_values_shape": [grid[1] * grid[2], 1176], "pixel_values_dtype": "float32",
                   "tensor_byteorder": "little", "tensor_contiguous_c_order": True,
                   # S0/S1 intentionally share bytes: a constant image may survive blur unchanged.
                   "pixel_values_sha256": digest(record + ("-constant" if condition in ("S0", "S1") else condition))}
            row["option_label_processor_sequences"] = [
                {**{key: copy.deepcopy(row[key]) for key in audit.OPTION_SHARED_FIELDS},
                 "continuation": label, "continuation_token_count": index + 1,
                 "continuation_token_ids_sha256": digest("synthetic-label-" + label),
                 "exact_prefix_extension_verified": True, "entire_continuation_scored": True}
                for index, label in enumerate(item["option_labels"])]
            rows.append(row)
    return rows, expected


def update_shared(row, key, value):
    row[key] = value
    for option in row["option_label_processor_sequences"]:
        if key in audit.OPTION_SHARED_FIELDS:
            option[key] = copy.deepcopy(value)


class InputBudgetContractTests(unittest.TestCase):
    def test_valid_panel_allows_different_examples_and_continuations(self):
        rows, expected = fixture()
        result = audit.validate_input_budgets(rows, expected)
        self.assertEqual(result["rows"], 12)
        self.assertFalse(result["runtime_or_scientific_validation"])
        self.assertFalse(result["execution_authorized"])

    def test_same_token_count_different_grid_is_rejected(self):
        rows, expected = fixture()
        row = rows[-1]
        update_shared(row, "image_grid_thw", [[1, 12, 8]])
        row["processed_dimensions"] = [168, 112]
        with self.assertRaises(audit.InputBudgetError):
            audit.validate_input_budgets(rows, expected)

    def test_context_drift_with_identical_length_is_rejected(self):
        rows, expected = fixture()
        update_shared(rows[1], "context_token_ids_sha256", digest("different context"))
        with self.assertRaisesRegex(audit.InputBudgetError, "cross-shift"):
            audit.validate_input_budgets(rows, expected)

    def test_missing_shift_duplicate_shift_and_missing_record_are_rejected(self):
        rows, expected = fixture()
        for bad in (rows[:-1], [*rows[:-1], copy.deepcopy(rows[-2])], rows[:6]):
            with self.subTest(rows=len(bad)), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(bad, expected)

    def test_missing_option_and_incomplete_continuation_are_rejected(self):
        for variant in ("missing", "partial"):
            rows, expected = fixture()
            options = rows[0]["option_label_processor_sequences"]
            if variant == "missing":
                options.pop()
            else:
                options[0]["entire_continuation_scored"] = False
            with self.subTest(variant=variant), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(rows, expected)

    def test_different_pixels_within_option_comparison_are_rejected(self):
        rows, expected = fixture()
        rows[0]["option_label_processor_sequences"][1]["pixel_values_sha256"] = digest("wrong pixels")
        with self.assertRaisesRegex(audit.InputBudgetError, "option context/image"):
            audit.validate_input_budgets(rows, expected)

    def test_dtype_drift_is_rejected_even_with_equal_byte_hashes(self):
        rows, expected = fixture()
        update_shared(rows[1], "pixel_values_dtype", "float16")
        with self.assertRaisesRegex(audit.InputBudgetError, "dtype/serialization drift"):
            audit.validate_input_budgets(rows, expected)

    def test_same_label_continuation_drift_across_shifts_is_rejected(self):
        rows, expected = fixture()
        rows[1]["option_label_processor_sequences"][0]["continuation_token_count"] += 1
        with self.assertRaisesRegex(audit.InputBudgetError, "cross-shift option-continuation"):
            audit.validate_input_budgets(rows, expected)

    def test_truncation_or_missing_image_is_rejected(self):
        for key, value in (("truncation_enabled", True), ("truncated_token_count", 1), ("image_count", 0)):
            rows, expected = fixture()
            rows[5][key] = value
            with self.subTest(key=key), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(rows, expected)

    def test_config_drift_and_inconsistent_patch_accounting_are_rejected(self):
        for key, value in (("processor_config_sha256", digest("wrong config")),
                           ("visual_token_count", 999), ("pixel_values_shape", [64, 588])):
            rows, expected = fixture()
            update_shared(rows[2], key, value)
            with self.subTest(key=key), self.assertRaises(audit.InputBudgetError):
                audit.validate_input_budgets(rows, expected)

    def test_record_order_does_not_change_paired_identity(self):
        rows, expected = fixture()
        self.assertEqual(audit.validate_input_budgets(rows, expected),
                         audit.validate_input_budgets(list(reversed(rows)), expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
