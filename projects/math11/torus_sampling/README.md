# Math11: independent exact checks for torus sampling

This is a new, manuscript-derived verification unit for the October 7 ordinary-height,
exact-area and fixed-step notes. It independently reproduces their finite arithmetic
using Python integers and fractions. It does **not** replay their original source code:
complete authenticated manuscript text was read, but the original PDF and archive byte
transfers returned HTTP 403. No checksum or source identity is invented for those files.
The byte-preserved [October 2 release](../release/CLAIM_STATUS.md) remains separate.

## Reproduce

Python 3.11 or newer; no third-party dependencies. From the repository root:

```bash
python -B projects/math11/torus_sampling/check_exact.py --check projects/math11/torus_sampling/independent_certificate.json
python -B -O projects/math11/torus_sampling/check_exact.py --check projects/math11/torus_sampling/independent_certificate.json
python -B -m unittest discover -s projects/math11/torus_sampling -p 'test_*.py' -v
```

Every certificate field is recomputed, including all 384 exclusion rows and all
2,002,000 character representatives. Checks use explicit exceptions, so optimized
Python does not disable them. To write a new certificate, use `--output NEW_PATH`;
existing files and symlinks are refused. `--limit N` allows a smaller diagnostic
character box, but only the default `N=1000` reproduces the retained full certificate.

## Executed results

| Calculation | Independently reconstructed result |
| --- | --- |
| Open-cell coefficient box | 384 nonzero triples; 368 excluded by the first small embedding and 14 by the second; survivors `±(1,5,3)` have norm `−3` and `+3` |
| Unit-group coefficient box | 314 nonzero triples; 42 signed units; all 21 displayed sign-pair identities checked |
| Norm cross-check | Multiplication-matrix determinant and a separately constructed Sylvester resultant agree on the unit box; tests extend agreement to 693 triples |
| Area | `rho = d² / (a² + ab + b²)` lies in `[0.0194522215627608629412139799, 0.0194522215627608629412139800]` |
| Finite step-one character exclusion | 2,002,000 sign representatives cover 4,004,000 nonzero vectors with supremum norm at most 1000 |
| Closest certified character | `(551, −497)`, near integer `−368`; separation exceeds `0.000000412931334275859315641717` |
| Limiting frequency for every phase | `[0.01924463020729435245, 0.01965981291822737343]`, using the manuscript's finite criterion |
| Regression tests | 24 passed, including exact boundary contact, negative intervals, altered certificates, incomplete rows, duplicate keys, nonfinite JSON and overwrite refusal |

Here `theta` is the largest root of `x³−3x−1`, `a=log((theta+1)/theta)`,
`b=log(theta)`, and `d=−log(theta−1)`. The rational logarithm enclosures use 80
terms of the atanh series with a rigorous positive remainder, after isolating the
root to a rational interval of width `10⁻⁶⁰`. No floating-point tolerance decides a result.

## Mathematical scope

The [proof review](PROOF_REVIEW.md) traces the analytical dependencies and the
strict winning rectangle. The newer manuscripts provide arguments for ordinary
integer-height density nonconvergence and for logarithmic/harmonic density equal
to `rho`; this unit checks their arithmetic and records a mathematical assessment.
It is not a proof-assistant formalization, institutional review or referee report.

**MATH-02 remains open:** a finite exclusion does not prove that step one is
nonresonant on the full torus. The displayed frequency interval bounds a limiting
frequency, not the error after a finite number of samples. Novelty and archival
venue fit remain unresolved. See [claims and next work](CLAIMS.md),
[provenance](provenance.json), and the [executed validation record](validation.json).
