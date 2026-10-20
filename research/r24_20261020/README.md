# R24 research package — 20 October 2026

**Actual status: 24 study contracts; 4 implemented development pilots; 0 GPU experiments executed in this session; 0 completed empirical papers.**

This package acts on the owner's request to find and work through 24 research ideas. It does not represent the entire request as finished. The source is on an isolated review branch; historical research records and their negative/bounded results are unchanged. Worldcastr is excluded and has not been modified.

## What exists

- `STUDIES.md`: 24 individual questions with mechanisms, data/control plans, primary endpoints, falsifiers, conceptual flaws and prior-art boundaries.
- `core.py`: real PyTorch implementations for studies 01, 05, 09 and 13; not pseudocode or empty interfaces.
- `run_development.py`: generated datasets, validation selection, baseline/control execution, predictions, checkpoints, timing, CUDA memory, data/source/artifact hashes and failure receipts for those four pilots. CUDA is required; no CPU training fallback exists.
- `provenance.py`: bounded injective seed allocation across projects, replicates, splits and stochastic streams.
- `analyze.py`: retained-artifact hash verification, designated comparator contrasts, seed-level descriptive summaries and explicitly exploratory bootstrap intervals. It does not assign empirical support or hide failed seeds.
- `test_core.py`, `test_protocol.py`, `test_theory.py`: 38 authored mathematical/engineering tests. Authored is not passed; see the actual GitHub Actions receipt for execution status.
- `paper/protocol.tex`: a substantive four-study methods/protocol manuscript with mathematical derivations, explicit controls, failure analysis, scope limitations and references. It has no invented empirical section and is not a final results paper.
- `paper/arxiv.sty`: the owner's retrieved layout, transcribed from the Library source. Trailing whitespace was normalized; no byte-identical-file claim is made. Its original internal package name `arxivrefined` is preserved.
- `SOURCE_AUDIT.md`: corrections to abbreviated/mistyped literature titles and limits of the initial literature review.

## Study state

| ID | Study | Implementation state | Evidence state |
|---|---|---|---|
| 01 | Intervention-Checked Reservoirs | Development mechanism + runner | Not executed |
| 02 | Mechanism-Localized Regime Detection | Concept contract only | None |
| 03 | Regime-Conditional Coverage Audit | Concept contract only | None |
| 04 | Cost-Bounded Trading Abstention | Concept contract only | None |
| 05 | Power-Matched Adaptive Noise Reservoirs | Development mechanism + runner | Not executed |
| 06 | Conservation-Bounded Residual Corrections | Concept contract only | None |
| 07 | Noise-Benefit Response Diagnostics | Concept contract only | None |
| 08 | Finite-Memory Subgrid Closure | Concept contract only | None |
| 09 | Blockwise Antithetic Forward Optimization | Development mechanism + runner | Not executed; theoretical limitation derived |
| 10 | Local Predictive Credit Transport | Concept contract only | None |
| 11 | Error-Broadcast Rank Allocation | Concept contract only | None |
| 12 | Meta-Learned Local Update Rules | Concept contract only | None |
| 13 | Selective Memory Necessity and Substitution | Development mechanism + runner | Not executed |
| 14 | Retrieval-Value Memory Eviction | Concept contract only | None |
| 15 | Counterfactual Replay Without New Data | Concept contract only | None |
| 16 | Selective Slow-State Reset | Concept contract only | None |
| 17 | Residual-Certified Krylov Reuse | Concept contract only | None |
| 18 | Constraint-Aware Operator Coverage | Concept contract only | None |
| 19 | Misspecification-Aware Theory Discrimination | Concept contract only | None |
| 20 | Minimal Causal State Dimension | Concept contract only | None |
| 21 | Cadence-Equivariant Light-Curve Representations | Concept contract only | None |
| 22 | Selection-Aware Astronomical Anomaly Scores | Concept contract only | None |
| 23 | Language-Conditioned Access Versus Capability | Concept contract only | None |
| 24 | Error-Certified Weight Reconstruction | Concept contract only | None |

A concept contract is not a complete model specification, a novelty certificate or a passed IDEA READY gate. Studies can merge after overlap review; 24 questions do not automatically justify 24 papers. The first four pilots are implemented development versions, not full implementations of every planned external benchmark and confirmatory control.

## Running the implemented work

Use Python 3.11 or newer, a CUDA-capable PyTorch installation and NumPy. The engineering workflow pins PyTorch 2.10.0 CPU for tiny tests only. On Kaggle, retain its CUDA-enabled PyTorch installation rather than installing the CPU wheel. Exact runtime versions are written into every run manifest. CUDA execution and compatibility have not yet been verified for this package.

From this directory:

```bash
python -m unittest discover -v
python run_development.py --projects 01,05,09,13 --seeds 0,1,2 --steps 200 --output /kaggle/working/r24-dev-001
python analyze.py /kaggle/working/r24-dev-001 --output /kaggle/working/r24-analysis-001
```

The test command runs bounded engineering fixtures, not scientific training. The development command fails and writes a BLOCKED manifest when CUDA is unavailable. A used output directory is never silently overwritten. The analysis output should be outside the run directory. Development seeds 0,1,2 are not confirmatory repetitions; a larger study requires its own reviewed precision and compute budget. The runner does not accept the other twenty study IDs and will not pretend they are implemented.

Each successful pilot run retains `data.pt`, checkpoint and prediction tensors, `metrics.json`, plus the overall manifest and SHA256 inventory. A failure is retained as `failure.json` and in the global failure ledger. Torch checkpoint files should only be opened when their source is trusted. The analysis utility uses JSON, not pickle, for its summaries.

For the protocol source, from `paper/`:

```bash
pdflatex -interaction=nonstopmode -halt-on-error protocol.tex
pdflatex -interaction=nonstopmode -halt-on-error protocol.tex
```

These are reproduction commands, not claims that compilation occurred. No PDF has been compiled or visually inspected during this session. The protocol is not an arXiv-ready release and must not be submitted as a completed empirical paper.

## Findings and corrections during preparation

**Seed collision corrected before any experiment.** The original memory pilot used `400000 + replicate*10000 + step` for training and `500000 + replicate` for evaluation. Replicate 10, step 10 collides. The revised `split_seed` function assigns disjoint mixed-radix coordinates and rejects out-of-range inputs. The initial unexecuted draft remains in Git history.

**Uniform blocking does not provide the claimed variance shortcut.** For a quadratic loss and equal-sized blocks sampled uniformly, the inverse-probability antithetic estimator has total variance `(d-1)||gradient||^2`, identical to full-vector Rademacher perturbation. A derivation and finite-enumeration tests are included. Nonuniform adaptive allocation could change this but would require measuring its costs and registering a different mechanism; it is not silently substituted here.

**Power matching is conditional expectation, not realized energy matching.** The adaptive-noise gate has spatial RMS one. Expected injected power is equal at a fixed amplitude, but the realized trajectories and state energies can differ. Both are recorded rather than calling them identical physical experiments.

**Invariance is not a causal discovery guarantee.** The reservoir readout solves a strictly convex objective. That optimization fact says nothing by itself about causal identification in observational markets or profitable trading.

**The memory model is an assay, not an oracle-beating architecture.** Exact lookup should be perfect on the generated task. The question is selective intervention response; real LLM and FIM claims require their actual models and external evaluations.

## Important open flaws and required evidence

| Flaw / risk | Severity | Repair or required evidence |
|---|---|---|
| No authenticated Kaggle execution available in this session | Blocking | Establish a real GPU execution context and retain job identity/logs; do not fabricate receipts. |
| Local container/Python execution service returned ServerError | Blocking for local verification/PDF | Obtain actual hosted engineering-test receipt; do not call authored tests passed. |
| Novelty screen is only initial | High | Reproduce nearest methods and explicitly reject/merge overlapping questions. |
| Study 01 lacks strong recurrent/structural baselines and real financial data | High | Add fair tuned baselines, hidden-confounder tests and licensed point-in-time data before broad claims. |
| Study 05 lacks timestep refinement and strong ESN/autoregressive baselines | High | Verify integration and equal-cost controls before any physical-computation claim. |
| Study 09 has no universal variance advantage and no isolated per-arm memory profile | High | Narrow the question to a measured cost frontier; account for all passes and tuning. |
| Study 13 is synthetic and learned lookup is not itself novel | High | Use it as a diagnostic; evaluate actual memory architectures before generalizing. |
| Candidate-selection counts do not guarantee matched compute | High | Measure and equalize total tuning and execution cost, not just trial counts. |
| Twenty studies have no model/evaluation implementation | Blocking | Complete specifications and code only after nearest-method review. |
| No confirmatory protocol or independent verifier | Blocking | Freeze the full claim/data/baseline/analysis package, then use protected outcomes. |
| Authorship, data licenses and release status unresolved | Blocking for release | Explicit ownership and license checks; no assumed affiliations or submissions. |

## Session access and write boundaries

GitHub reads and branch writes succeeded. The browser connector rejected access because the originating browser context was unavailable. No Kaggle integration was discovered, no Kaggle credentials were available to this runtime, and the initial local environment reported CUDA unavailable. Subsequent container and Python calls returned server errors. These are observed access failures, not a statement that Kaggle can never be used.

No scientific GPU run was started, no CPU research run was substituted, no paid compute was purchased, and no scheduled/background work was created. The branch is for review, not a merged release or a claimed change to the user's local device checkout. The default branch and historical project repositories remain unchanged by this package.

## What would constitute completion

A study is complete only after its question has a defensible terminal conclusion and the evidence, implementation, uncertainty, failure analysis, manuscript, reproduction package, independent verification and release permissions are complete. Valid negative, mixed and inconclusive outcomes must remain visible. No step is allowed to turn an unexecuted method or a passing engineering test into a positive research result.
