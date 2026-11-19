# Strict metadata admission verification — 19 November 2026

This is an engineering review of Percy-Projects PR #12 at parent head `b62da190e2536d6e6bf5e4776c778755c0d96a74`. The amendment remains **PROPOSED_NOT_ADOPTED**. Execution remains **NOT_AUTHORIZED** and scientific results remain **NOT_RUN**.

## Reproduced defects and correction

The prior checker accepted float-valued pixel tensor dimensions and equal-valued float/boolean aliases in option counts, image grids and tensor shapes. It also accepted duplicate object members and non-finite JSON numbers in supplied files. Four new test methods reproduced thirteen failed assertions, including subtests, against the original checker; the positive CLI case passed. `baseline.json` and `baseline_test_output.txt` retain this adverse run.

The repair requires exact integer tensor dimensions, exact recursive type-and-value equality for shared budget metadata, and strict parsing of both rows and expected-record files. Parsing rejects duplicate members at every depth, NaN/Infinity and overflowing numeric literals. Valid finite JSON and valid metadata retain the same metadata-only result and false execution-authorization flag.

## Verification

- Python 3.12.14, standard library only; 15 test methods passed with zero failures/errors: the original eleven plus four new regressions.
- The new regressions cover row tensor shape types, nested option type aliases, ambiguous/non-finite JSON at the CLI boundary, and a valid metadata-only CLI result.
- All seven preserved snapshots match their recorded Git blobs, SHA-256 digests and byte sizes. Their Git blobs were also independently fetched from `vertex-studyAI/vertexED.ai@65e5549b6bf4bb92eeacb17228be2278077dd832` and match.
- The original proposal, source provenance, frozen snapshot bytes, and entire November 7 verification directory remain unchanged.
- `receipt.json` records exact tested source hashes; `test_output.txt` is the new run output. These are separate evidence from the original eleven-test receipt.

From this project directory, run both test directories without installing model packages:

```sh
python3 -B -m unittest discover -v -s verification
python3 -B -m unittest discover -v -s verification_20261119
```

## Review disposition and remaining work

The source proposal is ready for ordinary integration after review of this repair. Merging its source does not adopt its scientific amendment. Review confirmed that inherited thresholds are restated rather than replaced; the old source preflight only compares A–D on one synthetic 32×32 image, while the separate proposal specifies per-example S0–S5 budgets. The proposed preprocessing-order clarification and unresolved zero-baseline/confidence-interval decision semantics require an explicit pre-outcome owner decision.

Actual runner binding, pinned processor/runtime and model scorer validation, development temperature provenance, protected execution and scientific closeout remain incomplete. No processor was downloaded or run, no model weights or dataset records were opened, no scientific run was performed, and no protected result or historical threshold changed.
