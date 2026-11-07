"""Audit the proposed per-example S0-S5 receipt structure, without model execution.

This is PROPOSED_NOT_ADOPTED engineering code. A pass means supplied metadata is
internally consistent; it does not authenticate receipts, run a processor,
inspect tensor bytes, or authorize/validate a scientific experiment.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CONDITIONS = tuple(f"S{i}" for i in range(6))
REVISION = "243fd99abe513d2a02a98274ea34c07e8f961b0f"
HASH = re.compile(r"[0-9a-f]{64}\Z")
IDENTITY_FIELDS = ("processor_identity_sha256", "processor_config_sha256")
BUDGET_FIELDS = (
    "canonical_dimensions", "transformed_dimensions", "processed_dimensions",
    "context_token_ids_sha256", "context_token_count", "attention_mask_sha256",
    "attention_mask_token_count", "image_grid_thw", "visual_token_count",
    "pixel_values_shape", "pixel_values_dtype", "tensor_byteorder",
    "text_prompt_sha256",
)
OPTION_SHARED_FIELDS = (
    "context_token_ids_sha256", "context_token_count", "attention_mask_sha256",
    "attention_mask_token_count", "image_grid_thw", "pixel_values_shape",
    "pixel_values_dtype", "tensor_byteorder", "pixel_values_sha256",
)


class InputBudgetError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputBudgetError(message)


def positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def integer_vector(value: object, length: int) -> bool:
    return isinstance(value, list) and len(value) == length and all(
        positive_integer(item) for item in value
    )


def is_hash(value: object) -> bool:
    return isinstance(value, str) and HASH.fullmatch(value) is not None


def validate_input_budgets(rows: list[dict], expected: list[dict]) -> dict:
    """Check six rows per expected record; expected options come from its freeze.

    Rows contain observed processor metadata before any model call. Hashes of
    the context/mask/tensor must be computed by the recorded runtime; this
    function checks their format and equality only. It does not attest them.
    """
    require(isinstance(rows, list) and isinstance(expected, list) and bool(expected),
            "rows and a nonempty external expected-record manifest are required")
    expected_options = {}
    for item in expected:
        require(isinstance(item, dict), "expected record must be an object")
        record = item.get("record_id")
        options = item.get("option_labels")
        require(isinstance(record, str) and bool(record), "expected record ID must be nonempty")
        require(record not in expected_options, "duplicate expected record")
        require(isinstance(options, list) and 2 <= len(options) <= 26,
                "expected option count must match the canonical renderer's 2-26 range")
        require(options == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(options)]),
                "expected labels must be in canonical order")
        expected_options[record] = options
    require(len(rows) == 6 * len(expected_options), "missing or extra record/condition rows")

    grouped = {record: {} for record in expected_options}
    identity = None
    tensor_format = None
    for row in rows:
        require(isinstance(row, dict), "receipt row must be an object")
        record, condition = row.get("record_id"), row.get("condition")
        require(isinstance(record, str) and record in grouped, "unexpected record")
        require(condition in CONDITIONS, "unknown condition")
        require(condition not in grouped[record], "duplicate record/condition")
        require(row.get("model_revision") == REVISION, "model revision drift")
        require(row.get("transformers_version") == "4.57.1", "processor library drift")
        require(row.get("use_fast") is False, "processor implementation drift")
        require(type(row.get("image_count")) is int and row["image_count"] == 1,
                "exactly one image must be retained in every condition")
        require(row.get("padding_enabled") is False and row.get("truncation_enabled") is False,
                "padding/truncation is forbidden by the proposed contract")
        require(type(row.get("truncated_token_count")) is int and row["truncated_token_count"] == 0,
                "truncated token count must be zero")
        for key in (*IDENTITY_FIELDS, "context_token_ids_sha256", "attention_mask_sha256",
                    "text_prompt_sha256", "pixel_values_sha256"):
            require(is_hash(row.get(key)), f"missing or invalid {key}")
        current_identity = tuple(row[key] for key in IDENTITY_FIELDS)
        if identity is None:
            identity = current_identity
        require(current_identity == identity, "effective processor identity/config drift")

        for key in ("canonical_dimensions", "transformed_dimensions", "processed_dimensions"):
            require(integer_vector(row.get(key), 2), f"invalid {key}")
        require(row["canonical_dimensions"] == row["transformed_dimensions"],
                "the transform changed image dimensions")
        grid = row.get("image_grid_thw")
        require(isinstance(grid, list) and len(grid) == 1 and integer_vector(grid[0], 3),
                "one complete image grid is required")
        t, h, w = grid[0]
        require(t == 1 and h % 2 == 0 and w % 2 == 0, "invalid still-image/merge grid")
        patches = t * h * w
        require(row["processed_dimensions"] == [h * 14, w * 14],
                "processed geometry disagrees with grid and patch size")
        require(row.get("pixel_values_shape") == [patches, 3 * 2 * 14 * 14],
                "pixel tensor shape disagrees with the pinned patch layout")
        require(type(row.get("visual_token_count")) is int and row["visual_token_count"] == patches // 4,
                "observed image-token count disagrees with grid/merge size")
        require(positive_integer(row.get("context_token_count")) and
                row["context_token_count"] > row["visual_token_count"], "invalid context token count")
        require(type(row.get("attention_mask_token_count")) is int and
                row["attention_mask_token_count"] == row["context_token_count"],
                "unpadded attention mask and context lengths disagree")
        require(row.get("pixel_values_dtype") in ("float16", "bfloat16", "float32", "float64"),
                "missing or unsupported tensor dtype")
        require(row.get("tensor_byteorder") in ("little", "big") and
                row.get("tensor_contiguous_c_order") is True, "tensor byte serialization is unspecified")
        current_format = (row["pixel_values_dtype"], row["tensor_byteorder"])
        if tensor_format is None:
            tensor_format = current_format
        require(current_format == tensor_format, "processor tensor dtype/serialization drift")

        options = row.get("option_label_processor_sequences")
        require(isinstance(options, list) and all(isinstance(option, dict) for option in options),
                "option receipt list is required")
        require([option.get("continuation") for option in options] == expected_options[record],
                "missing, extra or reordered answer options")
        for option in options:
            require(all(option.get(key) == row[key] for key in OPTION_SHARED_FIELDS),
                    "option context/image tensor differs from its condition prefix")
            require(option.get("exact_prefix_extension_verified") is True and
                    option.get("entire_continuation_scored") is True,
                    "exact prefix and complete continuation receipt required")
            require(positive_integer(option.get("continuation_token_count")), "empty continuation")
            require(is_hash(option.get("continuation_token_ids_sha256")), "invalid continuation hash")
        grouped[record][condition] = row

    for record, conditions in grouped.items():
        require(set(conditions) == set(CONDITIONS), f"incomplete condition panel for {record}")
        baseline = conditions["S0"]
        for condition in CONDITIONS[1:]:
            for key in BUDGET_FIELDS:
                require(conditions[condition][key] == baseline[key],
                        f"cross-shift {key} drift for {record}/{condition}")
            signature = lambda option: (option["continuation"], option["continuation_token_count"],
                                        option["continuation_token_ids_sha256"])
            require(list(map(signature, conditions[condition]["option_label_processor_sequences"])) ==
                    list(map(signature, baseline["option_label_processor_sequences"])),
                    f"cross-shift option-continuation drift for {record}/{condition}")
    return {"status": "STRUCTURAL_METADATA_PASS_ONLY", "records": len(expected_options),
            "conditions_per_record": 6, "rows": len(rows),
            "runtime_or_scientific_validation": False, "execution_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--expected-records", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_input_budgets(json.loads(args.rows.read_text()),
                                        json.loads(args.expected_records.read_text()))
    except (InputBudgetError, OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "STRUCTURAL_METADATA_FAIL", "error": str(error),
                          "execution_authorized": False}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
