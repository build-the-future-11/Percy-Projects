# Multimodal calibration under distribution shift

**Project:** MULTIMODAL-CALIBRATION-SCIENCEQA-20260904  
**Status:** NEEDS_REVIEW  
**Phase:** source reconciliation and proposed processor-budget amendment  
**Scientific result:** NOT_YET_TESTED / NOT_RUN  
**Execution:** NOT_AUTHORIZED  
**Last updated:** 7 November 2026

## Identity and source custody

This is the existing ScienceQA/Qwen2.5-VL calibration study, not a successor hypothesis or a new experiment. Its source remains the preserved [VertexED research commit 65e5549](https://github.com/vertex-studyAI/vertexED.ai/tree/65e5549b6bf4bb92eeacb17228be2278077dd832/research/multimodal-calibration). [PR #709](https://github.com/vertex-studyAI/vertexED.ai/pull/709) was closed **unmerged** on 9 September 2026 because generic research belonged outside the VertexED application repository. The [closure comment](https://github.com/vertex-studyAI/vertexED.ai/pull/709#issuecomment-5610086443) preserved the freeze and prohibited treating closure as execution authorization.

`Percy-Projects` is the designated scientific-state repository under its [lifecycle instructions](../../PERCY_PROJECTS_README.md). This review branch proposes the canonical state folder `projects/multimodal-calibration/`. Adoption remains pending. It does not reopen the old PR, migrate an executable package, or change any original frozen file.

Seven selected public source files are retained byte-for-byte in `source_snapshot/`; `SOURCE_PROVENANCE.json` records their original paths, Git blob identities and SHA-256 digests. Relative paths inside those preserved files still refer to the original repository. They must not be executed as a relocated package. The remaining implementation, tests, dependencies and history stay at the exact source commit.

## Research question and scope

For the fixed image-present ScienceQA records and fixed Qwen2.5-VL-3B-Instruct revision, does calibration/selective-risk deterioration under S1–S5 occur with limited accuracy loss, and does a scalar temperature fitted only on clean development records help under shift?

The inherited scope is 2,097 development records and 2,017 evaluation records, S0 clean plus three blur levels, central occlusion and a same-dimension neutral placeholder; raw option likelihoods versus one development-only temperature. No new condition, dataset, endpoint, numerical effect threshold or real-model run is introduced here.

## What is already fixed

The original authorization manifest already specifies numerical decision thresholds. The separate proposed amendment restates those exact values and does not backdate a new selection. The original model family, processor and tokenizer are pinned to `Qwen/Qwen2.5-VL-3B-Instruct@243fd99abe513d2a02a98274ea34c07e8f961b0f`. Original execution flags remain false and runtime/temperature receipts remain unresolved.

## Current evidence and supported claims

- Seven source snapshots match their original Git blob SHA values exactly.
- Source inspection shows that the old processor preflight compares A–D within one 32×32 synthetic image. It does not compare S0–S5 for an example.
- The original transforms preserve decoded image dimensions; S5 retains an image rather than removing the image token. This source property is not a live processor or model result.
- The proposed metadata checker is engineering support for a future recorded preflight. Its fixture tests establish only that specified metadata drift is rejected.

No actual ScienceQA record, model weight, development likelihood, fitted temperature, protected outcome, calibration metric or robustness result was produced in this reconciliation.

## Completed work

1. Resolved the closed/unmerged source history and the correct research-state destination.
2. Preserved the selected original source bytes and their provenance.
3. Reconciled the already-frozen numerical thresholds.
4. Wrote the proposed cross-shift processor-budget contract and a focused metadata checker.

## Missing work and blockers

The amendment is **PROPOSED_NOT_ADOPTED**. Its adoption must be recorded before any protected results are opened. No acceptance or independent scientific approval is implied by a branch, PR, source audit or fixture check.

The effective processor/runtime configuration must be captured, and the proposed contract must be wired into the actual runner and verified on synthetic or permitted development inputs. The exact host/accelerator/runtime, frozen-model scorer validation, full development S0 likelihood set and verified temperature-fit receipt are still missing. Quantitative zero-denominator and confidence-interval decision semantics remain to be made explicit by the study owner if they are not resolved in other authoritative evidence. Do not introduce a numerical epsilon, discard a zero-baseline metric, or claim statistical significance by default.

## Budget and protected boundary

This work permits source reading, documentation, and local deterministic metadata checks only. Real-model development and evaluation execution, paid compute, output-bearing reruns and outreach remain unapproved. Evaluation data and outcomes remain unopened. No scientific conclusion is available.

## Next executable action and definition of done

Review the exact dated amendment and source mapping; then, only under an accepted pre-outcome contract and permitted runtime work, bind the cross-shift checks to recorded processor outputs. A passed metadata check is not sufficient to authorize the study. Scientific completion still requires the frozen execution, retained evidence, claim audit and independent verification described by the original protocol.

See [TASKS.md](TASKS.md), [DECISIONS.md](DECISIONS.md), [the proposed amendment](proposed/INPUT_BUDGET_AMENDMENT_20261107.md), and [verification evidence](verification/REPORT.md).
