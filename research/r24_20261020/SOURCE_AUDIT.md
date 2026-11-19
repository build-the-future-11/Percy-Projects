# Source audit — 20 October 2026

This is an initial prior-art screen, not a systematic review or novelty certificate. Abstract-level reading does not establish that a method has been independently reproduced. Sources describe prior work; none establishes efficacy of an R24 implementation.

## Canonical titles checked against the arXiv records

These entries correct or expand the display titles in the first `STUDIES.md` draft. The arXiv identifiers and intended sources are unchanged; this audit is authoritative for bibliographic wording.

| Study-register source | Canonical title | Source |
|---|---|---|
| S02 | Using Machine Learning to Assess Short Term Causal Dependence and Infer Network Links | https://arxiv.org/abs/1912.02721 |
| S14 | Predictive Coding: Towards a Future of Deep Learning beyond Backpropagation? | https://arxiv.org/abs/2202.09467 |
| S18 | Causal Intervention-Based Memory Selection for Long-Horizon LLM Agents | https://arxiv.org/abs/2605.17641 |
| S23 | Conformal Prediction for Neural Operators: Distribution-Free Uncertainty Quantification in Physics Simulation | https://arxiv.org/abs/2606.09923 |
| S25 | Robust Experimental Design via Generalised Bayesian Inference | https://arxiv.org/abs/2511.07671 |
| S26 | Separating Tongue from Thought: Activation Patching Reveals Language-Agnostic Concept Representations in Transformers | https://arxiv.org/abs/2411.08745 |

The original S18 display title incorrectly said 'Long-Term Conversational Agents'; the correct wording is 'Long-Horizon LLM Agents'. S23 omitted the final phrase 'in Physics Simulation'. S26 omitted its leading phrase 'Separating Tongue from Thought'. No scientific conclusion rests on those shortened titles.

## Particularly important novelty boundaries

1. Reservoir-based short-term causal-dependence and network-link inference predates this package. A reservoir representation does not by itself identify financial causes. The R24-01 implementation currently tests intervention robustness on a known simulated SCM, not discovery on market data.
2. Predictive coding, forward-mode gradients and finite-difference forward-only optimization are different established research directions. R24-09 is a finite-difference estimator; it must not be described as the invention of training without backpropagation.
3. Existing causal-memory-selection work directly overlaps a generic claim that 'useful memory should be selected by intervention'. R24-13 is presently an intervention assay; R24-14 requires a genuinely distinct fixed-cost online eviction question to justify separate research.
4. Operator conformal prediction already exists. R24-18 must distinguish whole-field from pointwise coverage and account for approximate constraints excluding the true solution.
5. Activation patching has already been used to separate language and concept representations. R24-23 needs a new, tightly controlled failure regime rather than repeating the same general conclusion.

## Outstanding review obligations

The sources in `STUDIES.md` were screened for direct conceptual overlap, not exhaustively traced through every citation, implementation and subsequent correction. Statements about a source's novelty, state-of-the-art status or reliability require deeper review. Numerical performance from those papers is not imported into any R24 result table. Recent preprints are treated as prior-art candidates, not independent verification of their authors' claims. Every final manuscript must use a verified version-specific bibliography and a line-by-line claim/source audit.
