"""Regression tests for exact boundary decisions and certificate admission."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_exact as v


class ExactArithmeticTests(unittest.TestCase):
    def test_quadratic_interior_vertex(self):
        self.assertEqual(v.quadratic_range((1, 0, -1), v.Interval(-2, 2)), v.Interval(-3, 1))

    def test_quadratic_linear_and_constant(self):
        self.assertEqual(v.quadratic_range((3, -2, 0), v.Interval(-1, 2)), v.Interval(-1, 5))
        self.assertEqual(v.quadratic_range((3, 0, 0), v.Interval(-1, 2)), v.Interval(3, 3))

    def test_interval_negative_product(self):
        self.assertEqual(v.Interval(-3, -2) * v.Interval(-5, 7), v.Interval(-21, 15))

    def test_interval_reciprocal_and_zero_rejection(self):
        self.assertEqual(v.Interval(-4, -2).reciprocal(), v.Interval(v.Q(-1, 2), v.Q(-1, 4)))
        for bounds in [(0, 1), (-1, 0), (-1, 1)]:
            with self.subTest(bounds=bounds), self.assertRaises(v.VerificationError):
                v.Interval(*bounds).reciprocal()

    def test_square_and_outward_rounding(self):
        self.assertEqual(v.Interval(-3, 2).square(), v.Interval(0, 9))
        self.assertEqual(v.Interval(v.Q(-121, 100), v.Q(119, 100)).outward(1), v.Interval(v.Q(-13, 10), v.Q(12, 10)))

    def test_bareiss_requires_row_swap(self):
        self.assertEqual(v.determinant_bareiss([[0, 2], [3, 4]]), -6)
        self.assertEqual(v.determinant_bareiss([[1, 2], [2, 4]]), 0)

    def test_independent_norms_on_larger_box(self):
        for p in range(-5, 6):
            for q in range(-4, 5):
                for s in range(-3, 4):
                    triple = (p, q, s)
                    self.assertEqual(v.norm_multiplication(triple), v.norm_resultant(triple), triple)

    def test_roots_and_interpolation(self):
        self.assertEqual(len(v.check_root_and_weight_bounds()), 3)

    def test_closed_open_cell_is_exhaustive(self):
        result = v.check_open_cell()
        self.assertEqual((result['nonzero_triples'], result['excluded_embedding_1'], result['excluded_embedding_2']), (384, 368, 14))
        self.assertEqual({tuple(x) for x in result['survivors']}, {(1, 5, 3), (-1, -5, -3)})
        for row in result['rows']:
            if row['strict_margin'] is not None:
                self.assertGreater(v.Q(row['strict_margin']), 0)

    def test_unit_group_table_and_norm_identity(self):
        result = v.check_unit_box()
        self.assertEqual((result['nonzero_triples'], result['signed_units']), (314, 42))
        self.assertEqual(v.norm_multiplication((-1, 1, 0)), 3)

    def test_integer_exclusion_on_both_sides(self):
        self.assertEqual(v.exclude_integer_interval(12, 18, 10), 2)
        self.assertEqual(v.exclude_integer_interval(-18, -12, 10), 2)

    def test_integer_touch_and_crossing_are_inconclusive(self):
        for pair in [(10, 18), (12, 20), (-20, -12), (-18, -10), (-1, 1)]:
            with self.subTest(pair=pair), self.assertRaises(v.VerificationError):
                v.exclude_integer_interval(*pair, 10)

    def test_invalid_integer_enclosures_rejected(self):
        for args in [(True, 1, 10), (1, 0, 10), (1, 2, 0)]:
            with self.subTest(args=args), self.assertRaises(v.VerificationError):
                v.exclude_integer_interval(*args)

    def test_log_identity_and_series_remainder(self):
        self.assertEqual(v.log_rational(1), v.Interval(0, 0))
        short = v.log_rational(2, terms=4)
        long = v.log_rational(2, terms=12)
        self.assertLessEqual(short.lo, long.lo)
        self.assertGreaterEqual(short.hi, long.hi)
        self.assertEqual(v.log_rational(v.Q(1, 2), terms=12), -long)
        for x in (0, -1):
            with self.assertRaises(v.VerificationError):
                v.log_rational(x)

    def test_refined_root_and_decimal_signs(self):
        root = v.refined_theta(places=12)
        self.assertLess(v.polynomial(root.lo), 0)
        self.assertGreater(v.polynomial(root.hi), 0)
        self.assertEqual(v.decimal_bound(v.Q(-123, 100), 1), '-1.3')
        self.assertEqual(v.decimal_bound(v.Q(-123, 100), 1, True), '-1.2')


class CertificateAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads(Path(__file__).with_name('independent_certificate.json').read_text())

    def test_certificate_unchanged_accepted(self):
        v.strict_equal(copy.deepcopy(self.certificate), self.certificate)

    def test_mutated_count_missing_row_and_false_claim_rejected(self):
        mutations = [lambda x: x['open_cell'].__setitem__('nonzero_triples', 383),
                     lambda x: x['open_cell']['rows'].pop(),
                     lambda x: x['fixed_step'].__setitem__('full_torus_nonresonance_proved', True)]
        for mutate in mutations:
            changed = copy.deepcopy(self.certificate)
            mutate(changed)
            with self.assertRaises(v.VerificationError):
                v.strict_equal(changed, self.certificate)

    def test_boolean_does_not_replace_integer(self):
        with self.assertRaises(v.VerificationError):
            v.strict_equal({'x': True}, {'x': 1})

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(v.VerificationError):
            json.loads('{"x": 1, "x": 2}', object_pairs_hook=v.unique_keys)

    def test_existing_output_and_symlink_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'original.json'
            original.write_text('retain these bytes')
            link = Path(directory) / 'link.json'
            link.symlink_to(original)
            for target in (original, link):
                with self.assertRaises(v.VerificationError):
                    v.main(['--limit', '0', '--output', str(target)])
            self.assertEqual(original.read_text(), 'retain these bytes')

    def test_nonfinite_json_rejected_before_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'bad.json'
            bad.write_text('{"x": NaN}')
            with patch.object(v, 'build_certificate', return_value={'x': None}):
                with self.assertRaisesRegex(v.VerificationError, 'Nonfinite JSON'):
                    v.main(['--limit', '0', '--check', str(bad)])

    def test_incomplete_character_enumeration_or_resonance_rejected(self):
        c = {'omega': [v.Interval.point(v.Q(1, 2)), v.Interval.point(v.Q(1, 3))]}
        with self.assertRaises(v.VerificationError):
            v.fixed_step_check(c, 2)

    def test_limit_validation(self):
        for limit in (-1, 1001, True):
            with self.assertRaises(v.VerificationError):
                v.fixed_step_check({}, limit)

    def test_output_is_complete_json(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'new.json'
            small = {'open_cell': {'nonzero_triples': 384, 'excluded_embedding_1': 368, 'excluded_embedding_2': 14},
                     'unit_box': {'nonzero_triples': 314, 'signed_units': 42}, 'fixed_step': {}}
            with patch.object(v, 'build_certificate', return_value=small), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(v.main(['--limit', '0', '--output', str(target)]), 0)
            self.assertEqual(json.loads(target.read_text()), small)


if __name__ == '__main__':
    unittest.main()
