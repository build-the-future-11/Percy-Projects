# Proposed amendment: comparable processor inputs across visual shifts

**Date:** 7 November 2026  
**Status:** PROPOSED_NOT_ADOPTED / NOT_AUTHORIZED / NOT_RUN  
**Applies to:** MULTIMODAL-CALIBRATION-SCIENCEQA-20260904, source `65e5549b6bf4bb92eeacb17228be2278077dd832`  
**Purpose:** Resolve the cross-shift input-budget gap without changing the question, model, six conditions or numerical effect thresholds.

## 1. Numerical thresholds are already present

The source manifest's `statistics` object already contains the following values. This table records them; it does not claim they were newly selected on 7 November.

| Original rule | Existing value |
| --- | --- |
| Calibration warning: relative worsening | At least 10% in at least two of Brier, NLL and ECE |
| Calibration warning: AURC | At least 10% relative worsening |
| Calibration warning: accuracy | At most 5 percentage points of absolute drop |
| Temperature scaling: mean shifted Brier and NLL | At least 5% relative improvement in each |
| Temperature scaling: any individual shifted Brier or NLL | At most 2% relative worsening in either |
| Shift aggregation | Arithmetic mean across S1–S5 for each metric |
| ECE and uncertainty | 15 equal-width bins; 5,000 paired record-bootstrap replicates; seed 20260904; two-sided 95% intervals |
| Selective-risk target | 0.20 |

These values do not by themselves establish a universal definition of a calibrated model. A failed support rule must be reported as lack of support under the specified rule; it is not proof that calibration is absent. The original protocol requires uncertainty reporting but does not say to use a confidence bound instead of a point estimate to trigger these rules. This proposal does not silently add such a condition. Relative-change handling at zero baselines, exact comparison inclusivity and the role of intervals must be explicitly reconciled before outcome access; do not choose an epsilon or a significance interpretation from the eventual results.

## 2. What the current controls establish

`transforms.mjs` canonicalizes orientation/color and preserves image dimensions through S0–S5. S5 creates an RGB 127 placeholder with the original canonical dimensions. S4 uses `floor(width/2) × floor(height/2)` pixels, with a minimum of one pixel per side; its nominal 25% area is therefore approximate for odd or tiny dimensions. Retain and report the actual occluded fraction without altering the frozen transform here.

`processor-input-preflight.py` checks shared context, image tensor bytes and grid across A–D on one 32×32 neutral image. It does not send the same example through S0–S5, does not establish cross-shift budget equality, and does not cover every possible option count accepted by `prompt-template.mjs`.

## 3. Proposed preprocessing order and configuration receipt

Make the order explicit: canonicalize the input's orientation/color once, apply the frozen shift at that canonical image size, then use the same pinned processor for every shift. Do not insert a second resize to make a difficult condition fit. This clarifies the executable transform order and must be adopted as a dated amendment if the original wording was intended differently.

Keep the inherited checkpoint and processor revision. Record and content-hash the effective processor configuration, chat template, tokenizer files and dependency versions used by the actual process, including every call-time override. The frozen model's [preprocessor configuration](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/raw/243fd99abe513d2a02a98274ea34c07e8f961b0f/preprocessor_config.json) specifies `min_pixels=3136`, `max_pixels=12845056`, `patch_size=14`, `temporal_patch_size=2`, and `merge_size=2`. Resolve and record the defaults rather than replacing them with a smaller budget. The original workflow pins Transformers 4.57.1 and `use_fast=False`; another processor/runtime is a separate versioned change.

The effective receipt must also cover resize/resampling, RGB conversion, normalization, rescaling, padding, truncation, special tokens, and any chat-template or vision-ID settings. In the pinned implementation, retain the resolved `size.shortest_edge` and `size.longest_edge` values used by the resize path as well as the constructor arguments. A matching model name is insufficient. Do not use the latest library implicitly.

## 4. Per-example equality contract

Budget equality is required **within each example across S0–S5**, not across different examples with different native aspect ratios. Each example keeps one still image in every condition. S5 remains a placeholder image; a text-only arm would change token count and remains outside this proposal.

For each example and every condition, retain the pre/post-transform dimensions, image count, effective processor identity/config hashes, unpadded context-token count and hash, attention-mask count and hash, `image_grid_thw`, visual-token count, processed `pixel_values` shape/dtype and tensor hash, actual option labels, and each option's continuation-boundary receipt. Define tensor hashes using contiguous C-order bytes and record dtype and byte order separately. Record the resize output geometry too; do not infer every observed property from original dimensions.

Require all of the following:

1. Canonical and transformed dimensions match for the example in every condition. Processor settings and call-time overrides are identical.
2. Context token IDs, text/prompt identity, attention mask, image-grid dimensions, visual-token count and processed tensor **shape** match S0. Truncation and condition-specific padding are prohibited.
3. For the pinned image processor, one still image has a single `(t,h,w)` grid, with `t=1`. The language sequence's image-placeholder count must equal `t*h*w / merge_size²`, as produced by the pinned [processor implementation](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen2_5_vl/processing_qwen2_5_vl.py). Check the observed count; the formula alone is not a receipt. The [image implementation](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py) derives grid geometry from its actual resized dimensions.
4. Within a condition, every valid answer option shares the exact context prefix, processed image tensor bytes/dtype/shape and grid. Cover the example's complete canonical option list, which need not be A–D. Continuation token identities and lengths may differ between labels; score the entire exact label continuation, never sampled text or a retokenized different prefix.
5. Across shifts, image tensor **values/hashes may change**, because image content is the intervention. Requiring their equality across shifts would remove the experimental manipulation; requiring inequality would also be wrong because a constant image can remain unchanged. Tensor shape, dtype, byte serialization and grid must remain equal.
6. B1 reuses the same frozen B0 option-likelihood vector and input provenance for that example/condition. It applies only the already-fitted scalar temperature. No second model inference, different image, prompt, option set or token budget is introduced for B1. With positive common temperature and identical tie handling, B0/B1 argmax predictions must agree; accuracy disagreement is an implementation alarm, not a calibration benefit.
7. Record any additional forward inputs, including supplied position or modality IDs, and enforce the same construction policy. Bind the actual tensors used at model invocation to the preflight receipt so a valid receipt cannot be bypassed by different inputs. Equal input budgets alone do not establish equal measured compute or runtime reproducibility.

The proposed `check_input_budget.py` checks the structural subset expressible in recorded metadata. It accepts an external expected-record/option manifest so that silently missing examples or conditions cannot become a passing cohort. It does not load a processor, authenticate a receipt, verify actual tensor contents, recompute logits, check B1's mathematical implementation, or attest that protected outcomes were unopened.

## 5. Failure and adoption policy

The proposed tolerance for the equality contract is **zero mismatches**. Missing conditions/options, duplicates, budget/config drift, truncation, incompatible grids or image omission fail the audit. Retain the failure and example identity; do not silently drop it, replace it, lower that condition's image resolution, shorten its prompt or switch precision. An OOM or processor error does not justify a condition-specific retry.

A processor-only synthetic/development-safe preflight must demonstrate the accepted contract in the actual pinned runtime before any protected evaluation is opened. If it fails, the study remains blocked; any scientific change must be versioned before outcomes. A successful structural metadata audit is necessary support for that preflight, not permission to execute the model or proof of calibration/robustness.

This proposal remains separate from the original freeze. Required next decisions are adoption of the dated clarification, completion of effective runtime/config receipts, runner integration, frozen-model scorer validation and development-only temperature provenance. No model weights, ScienceQA records or result-bearing runs were used to prepare it.
