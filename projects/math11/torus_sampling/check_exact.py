#!/usr/bin/env python3
"""Independent reconstruction from the complete 7 October Math11 manuscripts.

This does not import or replay the inaccessible original proof-package sources.
All proof decisions use integers or fractions; no sampling or float tolerances.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path


class VerificationError(ValueError):
    """An exact arithmetic or certificate requirement failed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


@dataclass(frozen=True)
class Interval:
    lo: Q
    hi: Q

    def __post_init__(self):
        object.__setattr__(self, "lo", Q(self.lo))
        object.__setattr__(self, "hi", Q(self.hi))
        require(self.lo <= self.hi, "Reversed interval")

    @staticmethod
    def point(x):
        return Interval(Q(x), Q(x))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Interval) else Interval.point(x)

    def __add__(self, other):
        other = self.coerce(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other)
        corners = [x * y for x in (self.lo, self.hi)
                   for y in (other.lo, other.hi)]
        return Interval(min(corners), max(corners))

    __rmul__ = __mul__

    def reciprocal(self):
        require(not self.lo <= 0 <= self.hi, "Reciprocal crosses zero")
        return Interval(1 / self.hi, 1 / self.lo)

    def __truediv__(self, other):
        return self * self.coerce(other).reciprocal()

    def square(self):
        hi = max(self.lo * self.lo, self.hi * self.hi)
        lo = 0 if self.lo <= 0 <= self.hi else min(
            self.lo * self.lo, self.hi * self.hi)
        return Interval(lo, hi)

    def absolute(self):
        if self.lo >= 0:
            return self
        if self.hi <= 0:
            return -self
        return Interval(0, max(-self.lo, self.hi))

    def outward(self, places):
        scale = 10 ** places
        return Interval(Q((self.lo * scale).__floor__(), scale),
                        Q((self.hi * scale).__ceil__(), scale))


def fraction_text(x):
    x = Q(x)
    return str(x.numerator) + "/" + str(x.denominator)


def interval_record(x):
    return {"lo": fraction_text(x.lo), "hi": fraction_text(x.hi)}


def decimal_bound(x, places, upper=False):
    scale = 10 ** places
    n = (Q(x) * scale).__ceil__() if upper else (Q(x) * scale).__floor__()
    sign = "-" if n < 0 else ""
    whole, fraction = divmod(abs(n), scale)
    return f"{sign}{whole}.{fraction:0{places}d}"


def polynomial(x):
    return x * x * x - 3 * x - 1


ROOTS = (
    Interval(Q(1879385, 10**6), Q(1879386, 10**6)),
    Interval(Q(-1532089, 10**6), Q(-1532088, 10**6)),
    Interval(Q(-347297, 10**6), Q(-347296, 10**6)),
)
WEIGHT_CAPS = (
    (Q(71, 1000), Q(248, 1000), Q(133, 1000)),
    (Q(162, 1000), Q(380, 1000), Q(248, 1000)),
    (Q(1093, 1000), Q(132, 1000), Q(380, 1000)),
)


def check_root_and_weight_bounds():
    rows = []
    for root, caps in zip(ROOTS, WEIGHT_CAPS):
        require(polynomial(root.lo) * polynomial(root.hi) < 0,
                "Root bracket has no strict sign change")
        derivative = 3 * root.square() - 3
        require(not derivative.lo <= 0 <= derivative.hi,
                "Derivative sign not certified")
        weights = ((root * derivative).reciprocal().absolute(),
                   (root / derivative).absolute(),
                   derivative.reciprocal().absolute())
        for weight, cap in zip(weights, caps):
            require(weight.hi < cap, "Interpolation weight bound failed")
        rows.append({"root": interval_record(root),
                     "weight_enclosures": [interval_record(x) for x in weights],
                     "strict_weight_caps": [fraction_text(x) for x in caps]})
    require(ROOTS[1].hi < ROOTS[2].lo < ROOTS[2].hi < ROOTS[0].lo,
            "Root intervals are not disjoint")
    return rows


def coefficient_caps(embedding_caps):
    return [sum(embedding_caps[i] * WEIGHT_CAPS[i][j] for i in range(3))
            for j in range(3)]


def quadratic_range(triple, interval):
    """Exact extrema of p+q*x+s*x^2 on a rational closed interval."""
    p, q, s = triple
    values = [p + q * x + s * x * x for x in (interval.lo, interval.hi)]
    if s:
        vertex = Q(-q, 2 * s)
        if interval.lo <= vertex <= interval.hi:
            values.append(p + q * vertex + s * vertex * vertex)
    return Interval(min(values), max(values))


def multiply(left, right):
    coefficients = [0] * 5
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            coefficients[i + j] += x * y
    for degree in (4, 3):
        c = coefficients[degree]
        coefficients[degree - 2] += 3 * c
        coefficients[degree - 3] += c
    return tuple(coefficients[:3])


def power(base, exponent):
    require(type(exponent) is int and exponent >= 0, "Invalid power")
    answer = (1, 0, 0)
    while exponent:
        if exponent & 1:
            answer = multiply(answer, base)
        base = multiply(base, base)
        exponent //= 2
    return answer


def norm_multiplication(triple):
    columns = [multiply(triple, base) for base in
               ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
    matrix = list(zip(*columns))
    value = 0
    for permutation in itertools.permutations(range(3)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(3) for j in range(i + 1, 3))
        product = 1
        for i in range(3):
            product *= matrix[i][permutation[i]]
        value += (-1 if inversions % 2 else 1) * product
    return value


def determinant_bareiss(matrix):
    a = [list(row) for row in matrix]
    n, sign, previous = len(a), 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * a[k][k] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "Bareiss division is not exact")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = a[k][k]
    return sign * a[-1][-1]


def norm_resultant(triple):
    p, q, s = triple
    return determinant_bareiss([
        [1, 0, -3, -1, 0], [0, 1, 0, -3, -1],
        [s, q, p, 0, 0], [0, s, q, p, 0], [0, 0, s, q, p]])


UNIT_TABLE = (
    ((0, 0, 1), 1, 2, 0), ((0, 1, 0), 1, 1, 0),
    ((0, 1, 1), 1, 1, 1), ((0, 2, -1), 1, 1, -2),
    ((0, 3, 2), 1, -1, 3), ((1, -1, -1), -1, -1, 2),
    ((1, 0, 0), 1, 0, 0), ((1, 1, -1), -1, 1, -1),
    ((1, 1, 0), 1, 0, 1), ((1, 2, -2), -1, 3, -1),
    ((1, 2, -1), 1, 2, -1), ((1, 2, 1), 1, 0, 2),
    ((1, 3, -2), -1, 2, -2), ((1, 3, 0), 1, 3, 0),
    ((1, 3, 1), 1, 2, 1), ((2, -1, 0), 1, 0, -2),
    ((2, 0, -1), -1, -1, 1), ((2, 1, -1), 1, 0, -1),
    ((3, 0, -1), -1, -1, 0), ((3, 2, 0), 1, -2, 3),
    ((4, 1, -1), 1, -2, 2),
)


def check_unit_box():
    theta, theta_inverse = (0, 1, 0), (-3, 0, 1)
    eta, eta_inverse, delta = (1, 1, 0), (2, 1, -1), (-1, 1, 0)
    require(multiply(theta, theta_inverse) == (1, 0, 0), "theta inverse")
    require(multiply(eta, eta_inverse) == (1, 0, 0), "eta inverse")
    require(power(delta, 3) == tuple(3 * x for x in
            multiply(theta, power(eta_inverse, 2))), "delta identity")
    representations = set()
    rows = []
    for triple, sign, m, n in UNIT_TABLE:
        actual = multiply(power(theta if m >= 0 else theta_inverse, abs(m)),
                          power(eta if n >= 0 else eta_inverse, abs(n)))
        actual = tuple(sign * x for x in actual)
        require(actual == triple, "Printed unit identity does not hold")
        representations.add(actual)
        representations.add(tuple(-x for x in actual))
        rows.append({"triple": list(triple), "sign": sign, "m": m, "n": n})
    units, count = set(), 0
    for triple in itertools.product(range(-4, 5), range(-3, 4), range(-2, 3)):
        if triple == (0, 0, 0):
            continue
        count += 1
        first, second = norm_multiplication(triple), norm_resultant(triple)
        require(first == second, "Independent norm calculations disagree")
        if abs(first) == 1:
            units.add(triple)
    require(count == 314 and len(units) == 42, "Unit enumeration count changed")
    require(units == representations, "Unit table is not complete")
    caps = coefficient_caps([Q(5412, 1000), Q(4412, 1000), Q(2880, 1000)])
    require(all(x < n for x, n in zip(caps, (5, 4, 3))), "Unit box bounds")
    require((ROOTS[0] * (ROOTS[0] + 1)).hi < Q(5412, 1000), "Primary cap")
    require(((ROOTS[0] + 1).square() / ROOTS[0]).hi < Q(4412, 1000), "Second cap")
    require((ROOTS[0] + 1).hi < Q(2880, 1000), "Third cap")
    residues = {str(p): [polynomial(x) % p for x in range(p)] for p in (2, 5, 7)}
    require(all(0 not in values for values in residues.values()), "Inertness residue test")
    return {"nonzero_triples": count, "signed_units": len(units),
            "coefficient_strict_caps": [fraction_text(x) for x in caps],
            "unit_sign_pair_table": rows, "irreducibility_residues": residues,
            "norm_paths": ["3x3 multiplication determinant, permutation expansion",
                           "5x5 Sylvester resultant, fraction-free Bareiss"]}


def check_open_cell():
    caps = coefficient_caps([Q(23), Q(2, 5), Q(2, 5)])
    require(caps == [Q(427, 200), Q(3693, 625), Q(16551, 5000)], "Open-cell coefficient caps")
    require(all(x < n for x, n in zip(caps, (3, 6, 4))), "Open-cell completeness")
    rows, counts, survivors = [], [0, 0], []
    for triple in itertools.product(range(-2, 3), range(-5, 6), range(-3, 4)):
        if triple == (0, 0, 0):
            continue
        enclosures = [quadratic_range(triple, root) for root in ROOTS]
        disposition, margin = "survivor", None
        for i in (1, 2):
            lower = enclosures[i].absolute().lo
            if lower > Q(2, 5):
                disposition = "excluded_embedding_" + str(i)
                margin = lower - Q(2, 5)
                counts[i - 1] += 1
                break
        if disposition == "survivor":
            survivors.append(triple)
        rows.append({"triple": list(triple), "embeddings": [interval_record(x) for x in enclosures],
                     "disposition": disposition,
                     "strict_margin": None if margin is None else fraction_text(margin)})
    require(len(rows) == 384 and counts == [368, 14], "Open-cell exclusions differ")
    require(set(survivors) == {(1, 5, 3), (-1, -5, -3)}, "Unexpected survivor")
    beta = (1, 5, 3)
    bounds = [quadratic_range(beta, root).absolute() for root in ROOTS]
    require(bounds[0].hi < 21 and all(x.hi < Q(39, 100) for x in bounds[1:]), "Beta caps")
    require(norm_multiplication(beta) == norm_resultant(beta) == -3, "Beta norm")
    require(multiply((-1, 1, 0), power((1, 1, 0), 3)) == beta, "Beta identity")
    return {"rows": rows, "nonzero_triples": len(rows),
            "excluded_embedding_1": counts[0], "excluded_embedding_2": counts[1],
            "survivors": [list(x) for x in survivors], "beta_norm": -3,
            "coefficient_strict_caps": [fraction_text(x) for x in caps]}


def refined_theta(places=60):
    scale = 10 ** places
    lo, hi = scale, 2 * scale
    while hi - lo > 1:
        mid = (lo + hi) // 2
        sign = mid**3 - 3 * mid * scale**2 - scale**3
        if sign < 0:
            lo = mid
        else:
            hi = mid
    result = Interval(Q(lo, scale), Q(hi, scale))
    require(polynomial(result.lo) < 0 < polynomial(result.hi), "Refined root signs")
    return result


def log_rational(x, terms=80):
    x = Q(x)
    require(x > 0 and type(terms) is int and terms >= 1, "Invalid logarithm input")
    if x < 1:
        return -log_rational(1 / x, terms)
    t = (x - 1) / (x + 1)
    total, term = Q(0), t
    for j in range(terms):
        total += 2 * term / (2 * j + 1)
        term *= t * t
    remainder = 2 * term / ((2 * terms + 1) * (1 - t * t))
    return Interval(total, total + remainder)


def log_interval(interval):
    return Interval(log_rational(interval.lo).lo,
                    log_rational(interval.hi).hi).outward(50)


def constants():
    theta = refined_theta()
    a, b, d = log_interval((theta + 1) / theta), log_interval(theta), -log_interval(theta - 1)
    require(0 < d.lo < d.hi < a.lo < a.hi < b.lo, "Strict logarithm ordering")
    R = (a.square() + a * b + b.square()).outward(50)
    rho = (d.square() / R).outward(50)
    omega = ((b - a) / (2 * R), (2 * a + b) / (2 * R))
    require(rho.lo >= Q("0.0194522215627608629412139799") and
            rho.hi <= Q("0.0194522215627608629412139800"), "Published density enclosure")
    # The four eta-shifted rectangle corners, evaluated outward.
    C = a + b
    corners = []
    for p in (C - d, C):
        for twice_q in (a - d, a + d):
            s = (C * twice_q - (a - b) * p) / (2 * R)
            t = ((2 * a + b) * p - b * twice_q) / (2 * R)
            require(0 < s.lo <= s.hi < 1 and 0 < t.lo <= t.hi < 1,
                    "Winning rectangle corner leaves fundamental square")
            corners.append({"s": interval_record(s.outward(40)),
                            "t": interval_record(t.outward(40))})
    return {"theta": theta, "a": a, "b": b, "d": d, "R": R,
            "rho": rho, "omega": omega, "corners": corners}


def exclude_integer_interval(lo, hi, denominator):
    require(type(lo) is int and type(hi) is int and type(denominator) is int,
            "Integer lattice enclosure requires integers")
    require(denominator > 0 and lo <= hi, "Invalid integer interval")
    lower_integer = lo // denominator
    require(hi < (lower_integer + 1) * denominator and lo > lower_integer * denominator,
            "Character interval meets an integer; exclusion is inconclusive")
    return min(lo - lower_integer * denominator, (lower_integer + 1) * denominator - hi)


def fixed_step_check(c, limit):
    require(type(limit) is int and 0 <= limit <= 1000, "Limit must be an integer in [0,1000]")
    denominator = 10**40
    omega = [x.outward(40) for x in c["omega"]]
    lo0, hi0, lo1, hi1 = [int(x * denominator) for z in omega for x in (z.lo, z.hi)]
    count, smallest, witness = 0, None, None
    for k1 in range(limit + 1):
        # One representative of each {k,-k}: k1>0 or k1=0,k2>0.
        for k2 in range(1 if k1 == 0 else -limit, limit + 1):
            lower = k1 * lo0 + k2 * (lo1 if k2 >= 0 else hi1)
            upper = k1 * hi0 + k2 * (hi1 if k2 >= 0 else lo1)
            gap = exclude_integer_interval(lower, upper, denominator)
            count += 1
            if smallest is None or gap < smallest:
                smallest, witness = gap, {"k": [k1, k2], "interval": {
                    "lo": fraction_text(Q(lower, denominator)),
                    "hi": fraction_text(Q(upper, denominator))}}
    require(count == 2 * limit * (limit + 1), "Character enumeration incomplete")
    error = c["d"] * (c["a"] + Q(3, 2) * c["b"]) / c["R"] / (limit + 1)
    frequency = Interval(c["rho"].lo - error.hi, c["rho"].hi + error.hi)
    if limit == 1000:
        require(witness["k"] == [551, -497], "Closest character changed")
        require(Q(smallest, denominator) >= Q("0.000000412931334275859315641717"),
                "Published separation not certified")
        require(error.hi <= Q("0.00020759135546651049"), "Published uniform error not certified")
        require(frequency.lo >= Q("0.01924463020729435245") and
                frequency.hi <= Q("0.01965981291822737343"), "Published frequency bounds")
    return {"limit": limit, "sign_representatives": count, "covered_nonzero_vectors": 2 * count,
            "omega_enclosures": [interval_record(x) for x in omega],
            "least_gap_lower_bound": None if smallest is None else fraction_text(Q(smallest, denominator)),
            "closest_representative": witness, "uniform_error_upper": fraction_text(error.hi),
            "uniform_error_outward_decimal": decimal_bound(error.hi, 20, True),
            "limiting_frequency_outward_decimal": [decimal_bound(frequency.lo, 20),
                                                   decimal_bound(frequency.hi, 20, True)],
            "full_torus_nonresonance_proved": False,
            "finite_sample_discrepancy_bound": False}


def build_certificate(limit=1000):
    roots = check_root_and_weight_bounds()
    open_cell, unit_box, c = check_open_cell(), check_unit_box(), constants()
    return {"schema": "math11.independent_torus_arithmetic.v1",
            "provenance": "Independent reconstruction from full manuscript equations; not original-source replay",
            "root_and_weight_bounds": roots, "open_cell": open_cell, "unit_box": unit_box,
            "constants": {key: interval_record(c[key]) for key in ("theta", "a", "b", "d", "R", "rho")},
            "rectangle_corners": c["corners"], "fixed_step": fixed_step_check(c, limit),
            "analytic_proof_machine_checked": False, "external_referee_review": False}


def strict_equal(actual, expected, path="root"):
    require(type(actual) is type(expected), "Certificate type mismatch at " + path)
    if isinstance(expected, dict):
        require(actual.keys() == expected.keys(), "Certificate fields differ at " + path)
        for key in expected:
            strict_equal(actual[key], expected[key], path + "." + key)
    elif isinstance(expected, list):
        require(len(actual) == len(expected), "Certificate length differs at " + path)
        for i, (left, right) in enumerate(zip(actual, expected)):
            strict_equal(left, right, path + "[" + str(i) + "]")
    else:
        require(actual == expected, "Certificate value differs at " + path)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1000)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path, help="Create a new certificate; never overwrite")
    group.add_argument("--check", type=Path, help="Recompute and compare every field of a retained certificate")
    args = parser.parse_args(argv)
    require(0 <= args.limit <= 1000, "Limit must be in [0,1000]")
    if args.output:
        require(not args.output.exists() and not args.output.is_symlink(), "Output already exists")
    result = build_certificate(args.limit)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    if args.check:
        with args.check.open(encoding="utf-8") as stream:
            candidate = json.load(stream, object_pairs_hook=unique_keys,
                                  parse_constant=lambda x: (_ for _ in ()).throw(VerificationError("Nonfinite JSON: " + x)))
        strict_equal(candidate, result)
    print(json.dumps({"status": "PASS", "open_cell_triples": result["open_cell"]["nonzero_triples"],
                      "open_cell_exclusions": [result["open_cell"]["excluded_embedding_1"],
                                               result["open_cell"]["excluded_embedding_2"]],
                      "unit_box_triples": result["unit_box"]["nonzero_triples"],
                      "signed_units": result["unit_box"]["signed_units"],
                      "fixed_step": result["fixed_step"], "original_source_replayed": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
