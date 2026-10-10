# Math 11 certified cubic-field release

This package is the October 2, 2026 cleanup of the Math 11 cubic-field project.

## Main result

For

`K = Q(theta), theta^3 - 3 theta - 1 = 0`

and

`M(H) = min_{0 != alpha in O_K, |sigma0(alpha)| <= H} max(|sigma1(alpha)|, |sigma2(alpha)|)`, 

the release proves a global two-layer reduction and a globally complete exceptional interval for

`beta = 1 + 5 theta + 3 theta^2 = (theta-1)(theta+1)^3`.

The earlier 454-triple computation is no longer merely a bounded search: an inverse-Vandermonde argument proves that every true optimizer in the beta/gamma transition window must lie inside that exact box.

## Files

- `Math11_Cubic_Field_Certified_Results.pdf` - polished 9-page paper.
- `paper.tex` - LaTeX source.
- `verify.py` - standalone exact/rational verifier.
- `verifier_output.txt` - output from a clean successful verifier run.
- `candidate_table.csv` - all 454 finite-certificate triples with numerical embedding summaries.
- `certificate_manifest.json` - machine-readable statement of field, claims, endpoints, and status.
- `CLAIM_STATUS.md` - explicit proved/unproved ledger.
- `log_lattice.png` and `bounded_frontier.png` - paper figures.

## Reproduce

From this directory:

```bash
python3 verify.py
```

Expected result: every line begins with `PASS`, including the global norm-coset reduction and the exact beta/gamma transition.

To compile the manuscript in a standard TeX installation:

```bash
latexmk -pdf paper.tex
```

## Research boundary

This release deliberately does **not** promote the previously reported `0.01945222156` density into a theorem. The exact density and ordinary-density oscillation remain the next mathematical layer to prove.
