# Decisions

## 7 November 2026: preserve the existing freeze and propose the missing comparison

**Decision:** Retain selected source files exactly as they were at `vertex-studyAI/vertexED.ai@65e5549b6bf4bb92eeacb17228be2278077dd832`; place a separate dated proposal in the research-state repository. Do not edit or reopen the closed VertexED PR.

**Why:** The old PR's public closure directs generic research into its appropriate repository. The authorization manifest already contains numerical thresholds. The observed remaining processor-control gap is cross-shift input-budget equality, whereas the old preflight verifies answer-label equality within one synthetic image.

**Consequence:** Historical numerical values remain unchanged. The proposed amendment and its metadata checker require adoption and actual runner validation. Nothing here changes `execution_authorized=false`, `results_status=NOT_RUN`, the study's hypothesis, or the protected-evaluation boundary.

**Alternatives considered:** Reopening PR #709 would conflict with its explicit repository-isolation closure. Replacing the original manifest would blur historical freeze versus new decisions. Claiming the existing 32×32 fixture validated all shifts would overstate its scope.

**Evidence:** `SOURCE_PROVENANCE.json`; original protocol, manifest, model receipt, transform code, prompt renderer, processor preflight and its pinned workflow. Both source and destination repositories were verified public before preparing the migration. No private correspondence or private research artifact is included.

**What could change this decision:** A newer authoritative source or an explicit accepted migration/amendment decision. Any such change must preserve the current evidence and history.

## 19 November 2026: reject ambiguous receipt metadata without adopting the amendment

**Decision:** Require exact integer types for pixel tensor shapes and exact recursive JSON types for per-option/cross-shift budget equality. Parse both receipt files strictly, rejecting duplicate members and all non-finite numbers. Preserve the original proposal, source snapshots and November 7 evidence.

**Why:** Python treats integers, equal-valued floats and booleans as equal; ordinary JSON parsing also silently accepts duplicate members and non-standard/non-finite numbers. Constructed fixtures demonstrated that malformed metadata could pass the prior checker. Rejection is an engineering correction to the declared structural contract and does not change any scientific threshold or outcome rule.

**Evidence:** The new `verification_20261119/` directory retains the pre-repair failures, four regression methods, a 15-test passing result and exact source hashes. All seven original source snapshots were checked against the original repository commit again.

**Consequence:** The proposal can be retained through source-only integration after ordinary review. Integration does not supply an owner adoption decision, runtime validation, execution authority or a scientific result. The project remains **PROPOSED_NOT_ADOPTED / NOT_AUTHORIZED / NOT_RUN**, and the previously recorded open gates remain in force.
