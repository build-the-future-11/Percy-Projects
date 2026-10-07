# Claim status - Math 11 cubic-field release (2026-10-02)

## Proved / certified in this release

1. **Ring of integers:** `O_K = Z[theta]` for `theta^3 - 3 theta - 1 = 0`.
2. **Global norm-coset reduction:** every optimizer of
   `M(H) = min_{0 != alpha in O_K, |sigma0(alpha)| <= H} max(|sigma1(alpha)|, |sigma2(alpha)|)`
   has absolute norm `1` or `3`; hence it is a unit or `(theta-1)` times a unit.
3. **Exact exceptional interval:** for `beta = 1 + 5 theta + 3 theta^2`, if `L` is the largest root of
   `x^3 - 21x^2 + 3` and `U` the largest root of `x^3 - 24x^2 + 3x + 1`, then
   `argmin M(H) = {+/- beta}` for every `L <= H < U`.
4. **Endpoint transition:** at `H = U`, the unique minimizers up to sign are
   `gamma = 2 + 6 theta + 3 theta^2 = (theta+1)^3`.
5. **Finite-search completeness:** every possible optimizer in the transition window is forced into
   `|a|<=2, |b|<=6, |c|<=3`, leaving exactly 454 nonzero triples.

## Not proved in this release

- The numerical logarithmic exceptional density near `0.01945222156`.
- Nonconvergence of ordinary integer-sampling density.
- A complete explicit list of all switching intervals over all heights.
- Novelty relative to the full literature on cubic relative minima / reduction. The release includes only a preliminary related-work comparison.

## Verification boundary

`verify.py` makes pass/fail decisions using exact integers and rational interval arithmetic. Logarithms are enclosed by a rational atanh-series remainder bound. The script does not use floating-point arithmetic to decide the certified theorems.
