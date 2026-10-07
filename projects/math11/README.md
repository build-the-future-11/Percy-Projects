# Math 11: exact cubic-field certificate

This is the complete, byte-preserved October 2, 2026 release, with an independently
executable integrity and replay runner added on October 7. It includes the paper,
LaTeX source, all 454 candidate triples, exact rational verifier, figures, claim
ledger, original successful output, and original archive.

## Reproduce

Python 3.11 or later is sufficient; there are no third-party dependencies.
From the repository root:

```bash
python -B projects/math11/tools/reproduce.py
python -B -m unittest discover -s projects/math11/tests -v
```

For a new machine-readable receipt, add `--output /path/to/new-replay.json`.
Existing receipts are never overwritten. The runner hashes the original ZIP,
compares every extracted byte with its original member, checks the complete
coefficient table, executes the retained verifier with assertions enabled, and
requires its output to match the original successful output exactly.

The original `release/verify.py` uses Python assertions. **Use the runner above:**
it rejects `-O` and `-OO`, which would disable those checks. It also rejects missing,
extra, changed, and symlinked release files before execution. The hash anchor is a
provenance record of this release, not a digital signature or an adversarial trust
system.

## Result and claim boundary

The retained manuscript states a reduction of all optimizers in
`Q(theta), theta^3 - 3 theta - 1 = 0` to absolute norms 1 or 3. It also states the
exceptional interval for `beta = 1 + 5 theta + 3 theta^2`, with the transition to
`gamma = 2 + 6 theta + 3 theta^2` at the upper endpoint. The replay checks the exact
algebraic and rational computations supporting that argument, including all
454 coefficient triples and 256 log-lattice cells.

The retained [claim ledger](release/CLAIM_STATUS.md) is authoritative for the
release's scope. A successful replay is not an independent review of the paper's
mathematical deductions, assumptions, or novelty. The numerical exceptional
density near 0.01945, ordinary-density nonconvergence, and complete global switching
list remain unproved in this release.

## Conference route

ISSAC is a conditional route if independent review establishes enough algorithmic
or symbolic-computation novelty. Reproduction alone does not establish venue fit
or acceptance. A number-theory journal is an alternative if the contribution is
primarily theoretical. No manuscript has been submitted by this GitHub work.

## Provenance

- Original archive: [October 2 release](source/Math11_Certified_Release_2026-10-02.zip)
- Original archive SHA-256: `8f9d8b053271fc85c53c6294e2f3601d3bc4a34bdc795816cc5dfb3f928f5eeb`
- Retained paper: [PDF](release/Math11_Cubic_Field_Certified_Results.pdf)
- Executed replay receipt: [October 7](results/replay_2026-10-07.json)
- Scientific state and remaining review: [state.json](state.json)

All files under `release/` and the original archive are unchanged. New tooling is
kept outside that retained release so its scientific provenance remains explicit.
