# Verification: source reconciliation and proposed input-budget contract

Date: 7 November 2026. Scope: **source bytes and synthetic receipt metadata only**.

## Observed result

- **7/7 source snapshots:** Git blob SHA and SHA-256 match the retained provenance manifest. The original protocol, authorization manifest and model-freeze receipt were not rewritten.
- **11/11 local tests passed**, zero failures/errors/skips, on Python 3.12.14.
- An independent agent's static methods review was incorporated before publication of this proposal. This was not owner approval or an empirical processor validation.

The tests exercise the concrete failure modes the missing cross-shift check needs to catch: changed spatial grid with unchanged token count, changed context with unchanged length, missing/duplicate conditions, omitted records/options, an incompletely scored continuation, different tensor bytes across answer options, dtype drift, truncation/image omission, config/patch-accounting drift, and inconsistent tokenization of the same answer label across shifts. A valid panel intentionally permits different image sizes between records, different continuation lengths between labels, and equal pixel hashes between shifts.

## Reproduce

From the repository root:

```sh
python3 projects/multimodal-calibration/verification/test_input_budget.py
```

For an externally supplied receipt panel and its independent expected-record/option manifest:

```sh
python3 projects/multimodal-calibration/proposed/check_input_budget.py \
  --rows /path/to/processor_rows.json \
  --expected-records /path/to/expected_record_options.json
```

The command emits `STRUCTURAL_METADATA_PASS_ONLY` or a failed check. Do not describe this as an actual runtime preflight. Neither command downloads weights or datasets, calls a model, computes scientific metrics, fits temperature, or changes authorization. The retained local test output and machine-readable receipt contain the exact test count and checked source identities.

## Limits that remain

The fixture data were constructed solely to test metadata comparisons. The actual processor/runtime was not executed and is not installed in the inspected local Python environment. Consequently, no cross-shift live processor pass, tensor-content/receipt authenticity, model-forward consistency, score-extraction validity, B1 implementation correctness, compute parity, calibration or robustness result is claimed.

The original source includes code and workflows that are **not** present as an executable migrated package. Selected originals are reference snapshots; their internal relative paths still name the historical repository. The proposed checker is a separate engineering aid, not an alteration of the old protected protocol.

Owner/reviewer adoption of the dated amendment, resolution of decision-rule edge semantics, effective runtime/config binding, actual runner integration/preflight, frozen-model scorer validation, full development fit provenance and explicit execution authorization remain open. Status is **PROPOSED_NOT_ADOPTED / NOT_AUTHORIZED / NOT_RUN**.
