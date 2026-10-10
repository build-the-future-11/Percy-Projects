# Research engineering audit — 10 October 2026

Thirteen public repositories received executable code repairs with regression verification. All 13 candidates are published as draft pull requests; none is merged. This dated record supplements the canonical lifecycle document and preserves earlier registry work.

## Verification scope

These results concern implementation and bounded development behavior. They do not assign a new scientific outcome, certify a paper, or reclassify a closed study. Tests include both existing and newly added cases; local, focused, full-suite and platform counts overlap.

The linked pull requests contain exact commands, source identities, evidence and limitations. Some branches received concurrent follow-ups: the original session revision is recorded separately from the latest observed head, and later tests are bound to the later source. A full CI workflow may check GitHub's merge preview; explicit exact-head checks are identified in the JSON receipts.

## Published corrections

| Project and PR | Executable correction | Verified engineering result |
| --- | --- | --- |
| [World Series #1](https://github.com/build-the-future-11/world-series/pull/1) | Atomic immutable artifacts, sealed terminal receipts, finite budgets and interruption-safe reporting. | 52 focused local tests; full hosted implementation checks, package build and CLI doctor pass. [Checks](https://github.com/build-the-future-11/world-series/actions/runs/38019364063) |
| [NeuroCAD #95](https://github.com/THE-BU1LD/NeuroCAD/pull/95) | Correct zero-base autodiff powers and reject invalid gradient indices or returned Jet dimensions. | 1,208 tests pass, 9 skip in the Python 3.12 job; all 10 CI jobs and Gmsh pass. [Checks](https://github.com/THE-BU1LD/NeuroCAD/actions/runs/38019363749) |
| [FIM #28](https://github.com/THE-BU1LD/Fabric-Induced-Memory/pull/28) | Repair the actual Trainer/model API and make parameter EMA evaluation reversible. | 192 tests pass, 7 skip and 10 subtests pass; protected trajectory job stays skipped. [Checks](https://github.com/THE-BU1LD/Fabric-Induced-Memory/actions/runs/38018589291) |
| [LAM-JEPA #201](https://github.com/vertex-studyAI/LAM-JEPA/pull/201) | Load canonical checkpoint config once and preserve RNG, model modes and quantizer state during inference. | Current observed branch: 48 inference contracts pass; all 6 workflows pass. [Checks](https://github.com/vertex-studyAI/LAM-JEPA/actions/runs/38021103566) |
| [RIPII #21](https://github.com/THE-BU1LD/RIPII/pull/21) | Validate semantic masks, converted values and complete rollout inputs before model calls. | 250 tests pass on each supported Python matrix version; 80.91% coverage clears the unchanged 75% gate. [Checks](https://github.com/THE-BU1LD/RIPII/actions/runs/38020075938) |
| [RIS #4](https://github.com/build-the-future-11/RIS/pull/4) | Use float64 finite differences and correct symmetric Hessian stencils for integer and low-precision inputs. | 14 hosted tests, compile and real demo pass. [Checks](https://github.com/build-the-future-11/RIS/actions/runs/38020451323) |
| [FI-JEPA #10](https://github.com/Finance-Meta-Research/FI-JEPA/pull/10) | Use complete shared-calendar asset splits, training-only normalization and stable asset IDs. | Current observed branch: 42 tests pass; source-bound 21- and 41-test predecessors remain identified. [Checks](https://github.com/Finance-Meta-Research/FI-JEPA/actions/runs/38021041883) |
| [Eigen-JEPA #31](https://github.com/Finance-Meta-Research/Eigen-JEPA/pull/31) | Prospective v2 fold admission checks complete context/target footprints while preserving frozen v1. | Current observed branch: 125 tests and submission gate pass; one-seed paper rigor remains insufficient. [Checks](https://github.com/Finance-Meta-Research/Eigen-JEPA/actions/runs/38020909272) |
| [GaussianMemory #4](https://github.com/THE-BU1LD/GaussianMemory/pull/4) | Advance separate train/evaluation streams, use an unobserved temporal target and repair train/eval CLI execution. | 30 hosted tests pass, including real bounded train/eval CLI exercises. [Checks](https://github.com/THE-BU1LD/GaussianMemory/actions/runs/38019845294) |
| [IRIS #9](https://github.com/build-the-future-11/IRIS/pull/9) | Stable filter/metric arithmetic and complete atomic replayable development records with protected-ID admission. | 106 hosted tests; all five 32-observation development records replay; protected ID rejection passes. [Checks](https://github.com/build-the-future-11/IRIS/actions/runs/38018872922) |
| [IRIS-Space #40](https://github.com/build-the-future-11/IRIS-Space/pull/40) | Train-only passband vocabulary, unknown bands, finite v2 tensors and exact consumed-source hashes. | Current branch: 52 exact-head tests; full merge-preview CI has 729 tests and 129 subtests, all gates pass. [Checks](https://github.com/build-the-future-11/IRIS-Space/actions/runs/38020896062) |
| [EPU #9](https://github.com/THE-BU1LD/EPU/pull/9) | Validate vector/state contracts and prevent normalization, clipping and fixed-point overflow. | 20 methods pass; unchanged goldens and actual Verilog simulation match all 8 retained steps. [Checks](https://github.com/THE-BU1LD/EPU/actions/runs/38019219144) |
| [EigenFinance offline proposal #3](https://github.com/Finance-Meta-Research/EigenFinance/pull/3) | Retain actual per-fold covariance predictions, paired errors and input/context/evaluation/source identities. | 21 hosted tests pass, including real CLI and direct future-shock invariance. Reserved proposal only. [Checks](https://github.com/Finance-Meta-Research/EigenFinance/actions/runs/38020918771) |

## Immutable revision bindings

| Repository | Session-published revision | Observed branch revision |
| --- | --- | --- |
| build-the-future-11/world-series | [dbf580acc75a](https://github.com/build-the-future-11/world-series/commit/dbf580acc75a5d5650de74d55fbaab6b023f3374) | [dbf580acc75a](https://github.com/build-the-future-11/world-series/commit/dbf580acc75a5d5650de74d55fbaab6b023f3374) |
| THE-BU1LD/NeuroCAD | [6b3c27f0b077](https://github.com/THE-BU1LD/NeuroCAD/commit/6b3c27f0b07732b7b61dc83035ec2282d7ac2ff5) | [6b3c27f0b077](https://github.com/THE-BU1LD/NeuroCAD/commit/6b3c27f0b07732b7b61dc83035ec2282d7ac2ff5) |
| THE-BU1LD/Fabric-Induced-Memory | [0ae2bf91fb1b](https://github.com/THE-BU1LD/Fabric-Induced-Memory/commit/0ae2bf91fb1b88217637a5319f9c74628ffa4436) | [0ae2bf91fb1b](https://github.com/THE-BU1LD/Fabric-Induced-Memory/commit/0ae2bf91fb1b88217637a5319f9c74628ffa4436) |
| vertex-studyAI/LAM-JEPA | [2323d33e2be7](https://github.com/vertex-studyAI/LAM-JEPA/commit/2323d33e2be76c3121e0c7ca68c8bf69619b8624) | [0cf0b7a18572](https://github.com/vertex-studyAI/LAM-JEPA/commit/0cf0b7a18572fcf9e07c573092b53fe2e2d5dcc9) |
| THE-BU1LD/RIPII | [db45f504546a](https://github.com/THE-BU1LD/RIPII/commit/db45f504546a21c589ba85028b67bd6db037991c) | [db45f504546a](https://github.com/THE-BU1LD/RIPII/commit/db45f504546a21c589ba85028b67bd6db037991c) |
| build-the-future-11/RIS | [f043f643011d](https://github.com/build-the-future-11/RIS/commit/f043f643011d06597d092ecb74d1b6e9ee290937) | [f043f643011d](https://github.com/build-the-future-11/RIS/commit/f043f643011d06597d092ecb74d1b6e9ee290937) |
| Finance-Meta-Research/FI-JEPA | [4fdfd92513e4](https://github.com/Finance-Meta-Research/FI-JEPA/commit/4fdfd92513e4bf5a0d9baba81efa37dc190a1fb4) | [1416cecbd79f](https://github.com/Finance-Meta-Research/FI-JEPA/commit/1416cecbd79fc35b4c5df09b1a3da3682c36fc2e) |
| Finance-Meta-Research/Eigen-JEPA | [e791016d0eda](https://github.com/Finance-Meta-Research/Eigen-JEPA/commit/e791016d0eda9fb579116231e6661caa5799f187) | [d55b0d62615e](https://github.com/Finance-Meta-Research/Eigen-JEPA/commit/d55b0d62615ee99adf8fd50d64098a1cf6f51097) |
| THE-BU1LD/GaussianMemory | [ff6d0fced236](https://github.com/THE-BU1LD/GaussianMemory/commit/ff6d0fced236f2a6b4080a6137b805194c043884) | [ff6d0fced236](https://github.com/THE-BU1LD/GaussianMemory/commit/ff6d0fced236f2a6b4080a6137b805194c043884) |
| build-the-future-11/IRIS | [5943f7b7c135](https://github.com/build-the-future-11/IRIS/commit/5943f7b7c135bd83e22d5cc1df5ba0a07c955e9a) | [5943f7b7c135](https://github.com/build-the-future-11/IRIS/commit/5943f7b7c135bd83e22d5cc1df5ba0a07c955e9a) |
| build-the-future-11/IRIS-Space | [15a52801c424](https://github.com/build-the-future-11/IRIS-Space/commit/15a52801c424784f63b7ac165ea7b2eaed20b434) | [62a3470bbdb2](https://github.com/build-the-future-11/IRIS-Space/commit/62a3470bbdb2411f88c14f720ed69a6c3766d299) |
| THE-BU1LD/EPU | [38ea737c64c5](https://github.com/THE-BU1LD/EPU/commit/38ea737c64c59e6986cb8c65b7e3a3d549e998cf) | [38ea737c64c5](https://github.com/THE-BU1LD/EPU/commit/38ea737c64c59e6986cb8c65b7e3a3d549e998cf) |
| Finance-Meta-Research/EigenFinance | [04c151ee810d](https://github.com/Finance-Meta-Research/EigenFinance/commit/04c151ee810d9cb1cc42de045d90b35246dd3f1c) | [04c151ee810d](https://github.com/Finance-Meta-Research/EigenFinance/commit/04c151ee810d9cb1cc42de045d90b35246dd3f1c) |

## Remaining scientific limits

- Eigen-JEPA's paper-facing rigor requirement still has insufficient independent seeds; passing code and submission-integrity checks does not meet that requirement.
- IRIS development record replay does not establish the unresolved canonical provenance needed to open protected experiment IDs.
- IRIS-Space preprocessing and evidence-cohort checks do not establish a discovery, forecast-superiority or population-shift result.
- RIPII's hosted MPS job reports an infrastructure limitation; real MPS/CUDA device testing is not certified.
- EPU's reference arithmetic and Verilog simulation are verified. Physical FPGA implementation and hardware performance are not established.
- The EigenFinance changes improve its existing proposed offline implementation. Its reserved study/activation status remains unchanged.
- Existing submitted or negative/mixed study conclusions remain intact; new engineering work does not restart them.

## Machine-readable evidence

See [the structured public record](2026-10-10_public_research_engineering.json) for per-repository heads, PR bases, run/job IDs, exact testing scope, source-preservation evidence and limitations. The record covers public repositories only and does not reproduce private-project details.
