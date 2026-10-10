# Lifecycle ledger engineering record — 2026-10-10

## Scope and disposition

This change implements a working artifact/state CLI for the existing research
pipeline. It is an engineering delivery, not a completed empirical study and not
evidence that any portfolio hypothesis is supported. No model training, protected
evaluation, paid scientific execution, or real scientific release was performed.
The only gate-10 states generated during validation were explicitly artificial
temporary software fixtures; none is included in the repository.

Base: `c6945e8028b6d99886bb4748763d2670b39365d3`, containing only
`PERCY_PROJECTS_README.md`. The existing README is unchanged. Existing metadata
registry and theory-work pull requests were inspected for overlap and remain
untouched. The admitted study shape is a fixed comparative empirical matrix,
not a universal proof-only or observational protocol engine.

The implementation contract in `DESIGN.md` was written before coding. Two
independent agent review passes inspected the source adversarially; the first
identified the defects below, which were fixed and regression tested. The second
review reported no remaining blocking issue. These were software reviews, not
independent verification of scientific findings.

## Mechanism implemented

- One canonical generated `STATE.md`, containing readable state plus a replayable
  SHA-256-linked event history; stale, corrupted, or manually edited state fails
  verification. Rejected valid-state updates remain in the history.
- Immutable, content-addressed artifact snapshots, verified byte identities,
  checked provenance parents, and preserved failed/invalid run receipts.
- Ordered qualification and freeze gates, exact configuration/code/data/split/
  environment/seed matching, and a claim → raw → analysis → display graph.
- Accounting of all retained runtime and development runs across revisions,
  including failures. Over-budget receipts remain available; qualification and
  conclusion rules expose and constrain the overrun.
- Supported, mixed, negative, and inconclusive completion paths; explicit invalid
  closure; distinct new-hypothesis and same-hypothesis validity-correction studies.
- Exclusive process locks, atomic replacement, file and directory synchronization,
  explicit post-replacement durability-error semantics, and predecessor protection.
- A complete CLI, schema guide, bounded stdlib CI, and an executable artificial
  example that performs no research execution.

## Development failures and review corrections retained

| Finding | Cause / correction | Evidence |
| --- | --- | --- |
| Declared budgets were initially only validated and displayed | Add cumulative accounting, immutable overrun records, prefreeze qualification/freeze blocks, explicit amendments, and frozen overrun closure limits | Boundary, failure, revision, large-number, and frozen-cap tests |
| Direct artifact metadata could reference absent bytes and make newly written state unreadable | Verify the content object before ledger admission; retain rejection without committing the invalid reference | Missing-object and wrong-size admission tests |
| Literal ledger framing in scientific text could break state parsing | Select the final generated delimiter and require exact rerender | Contract-with-delimiter round-trip test |
| Very large JSON integers could escape domain validation through `OverflowError` | Explicit finite-number checks and strict floating literal parsing | Huge-integer and `1e999` tests |
| Freeze could select input objects different from the qualified ones | Bind protocol, architecture, and code to gates 3, 2, and 4 | Three unqualified-replacement cases |
| Multi-run claims could omit the raw evidence of one named run | Require each run to contribute a selected source; supported statements require actual raw output from each successful run | Missing-run-evidence and log-only claim tests |
| Directory durability was initially not synchronized | Fsync object/store ancestors and state directory; report installed-state errors without promising rollback | Before/after replacement fault injection and retry tests |
| An invalid study initially had no same-hypothesis correction path | Add `correct-invalid` with documented defect/repair, changed protocol identity, and new project ID | Valid correction, valid-predecessor rejection, unchanged-protocol rejection |
| A nested successor could add files within a supposedly preserved predecessor | Require nonoverlapping project directories | Nested-target rejection and byte-preservation tests |
| A replaced object could be a FIFO and block an ordinary open | Open nonblocking, then require a regular-file descriptor | Bounded subprocess verification test |

These findings concern development of the new CLI. They are not scientific
negative results, discarded study outcomes, or evidence about other projects.

## Executed validation

Runtime: Linux, Python 3.12.14. The tests use real temporary directories, operating
system locks, subprocess CLI calls, retained object bytes, and fault injection.
No third-party scientific package is imported by the tool or tests.

| Verification | Result |
| --- | --- |
| Final development regression suite | **52 passed**, 10.495 seconds |
| Fresh virtual environment created with `venv --without-pip`; same final suite | **52 passed**, 11.114 seconds |
| Ruff `E4,E7,E9,F,I` on source and test files | Passed |
| Python compilation of source and tests | Passed |
| All four valid dispositions reaching checkpoint 10 | Passed as artificial fixtures |
| Artificial negative demonstration plus CLI verification, expected head, and overwrite refusal | Passed |
| Concurrent process contention, stale writers, artifact mutation, failed writes, failure retention | Passed |

Reproduction commands from repository root:

```sh
python -m unittest discover -s tests -p test_research_pipeline.py -v
python -m venv --without-pip /tmp/percy-ledger-clean-environment
/tmp/percy-ledger-clean-environment/bin/python -B -m unittest discover -s tests -p test_research_pipeline.py -v
python -m research_pipeline.demo --output /tmp/new-artificial-ledger-example
python -m research_pipeline verify /tmp/new-artificial-ledger-example/study
```

Use new temporary paths; the example refuses existing targets. The fresh
environment verifies the runtime dependency claim on Python 3.12, not every
filesystem or interpreter. Hosted CI is configured for Python 3.11 and 3.12;
this record makes no claim that hosted jobs had finished before publication.

## Exact tested source identities

SHA-256 values exclude this report to avoid a self-referential digest. The Git
commit/tree of the publication identifies the complete delivered file set.

| File | SHA-256 |
| --- | --- |
| `research_pipeline/__init__.py` | `1ee07845ad094ad0fbc13e6a0e05dee0ad2a1d824d731ecfb63ac2eec0b04727` |
| `research_pipeline/ledger.py` | `e4a517cd267f32c1bafd0041d8ee56a52ee0b81005e280e8ad981d37acbe3e40` |
| `research_pipeline/__main__.py` | `62e688f58a7a5a0c4d6920604cd74a898b378510366dfdaa88fef9e93fd96368` |
| `research_pipeline/demo.py` | `4392edff288c080df747b28d8c8ff342a61595c3f6a74567aaca0e5d246cd8d1` |
| `research_pipeline/DESIGN.md` | `51e9334a66227ce5138a644c98c0ec12c5b0fb1d76121fb652757e416e5405d0` |
| `research_pipeline/README.md` | `b2bb38047272395fd13a62189ef10fe18f9e74ebe384254ac50f457f3ecf604d` |
| `tests/test_research_pipeline.py` | `67b86fb68588149acfadfb22ff487f0d8c6c2be9c85ec7cea05a504bb01458a0` |
| `.github/workflows/research-pipeline.yml` | `052458c7a1f9efc925e3ab29114e9b095c0d92e47c6811721fbe828d2aa609a7` |

## Remaining scientific and operational limits

Review attestations and conclusion labels remain human judgments. Matching bytes
do not prove the declared code was executed, the method is novel, data is free of
leakage, or the statistical result is valid. The CLI cannot prevent or recover an
unreported external run, authenticate an authorization, or restore test secrecy.
It does not admit adaptive or incomplete matrices. Whole-history rewrite detection
needs a trusted external head; local locks and POSIX synchronization depend on
filesystem and hardware behavior. Every load verifies all registered evidence,
which favors integrity over throughput for large artifact collections.
