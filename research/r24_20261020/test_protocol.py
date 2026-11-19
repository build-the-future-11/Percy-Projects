"""Hand-verifiable protocol fixtures, not scientific simulations."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import analyze
from provenance import split_seed


class ProtocolTests(unittest.TestCase):
    def test_seed_deterministic(self):
        self.assertEqual(split_seed(13, 10, 1, 10), split_seed(13, 10, 1, 10))

    def test_seed_disjoint_streams(self):
        seeds = [split_seed(p, r, s, i) for p in (1, 5, 9, 13)
                 for r in (0, 1, 10, 999999) for s in range(16) for i in (0, 1, 99999)]
        self.assertEqual(len(seeds), len(set(seeds)))

    def test_old_collision_repaired(self):
        self.assertEqual(400000 + 10 * 10000 + 10, 500000 + 10)
        self.assertNotEqual(split_seed(13, 10, 1, 10), split_seed(13, 10, 3))

    def test_seed_bounds(self):
        self.assertGreaterEqual(split_seed(0, 0, 0), 0)
        self.assertLess(split_seed(99, 999999, 15, 99999), 2**63)
        for bad in ((100, 0, 0, 0), (1, -1, 0, 0), (1, 1000000, 0, 0),
                    (1, 0, 16, 0), (1, 0, 0, 100000)):
            with self.assertRaises(ValueError):
                split_seed(*bad)

    def test_seed_rejects_noninteger(self):
        with self.assertRaises(ValueError):
            split_seed(1, 0.0, 0)
        with self.assertRaises(ValueError):
            split_seed(1, True, 0)

    def test_quantile_interpolation(self):
        self.assertEqual(analyze.quantile([0., 10.], .25), 2.5)
        self.assertEqual(analyze.quantile([10., 0.], 1), 10.)

    def test_describe_single(self):
        result = analyze.describe([3.])
        self.assertEqual(result['mean'], 3.)
        self.assertIsNone(result['standard_deviation'])
        self.assertIsNone(result['exploratory_bootstrap_95_percent_interval'])
        self.assertEqual(result['scientific_disposition'], 'UNCONFIRMED')

    def test_describe_invalid(self):
        for values in ([], [float('nan')], [float('inf')]):
            with self.assertRaises(ValueError):
                analyze.describe(values)

    def test_bootstrap_constant(self):
        result = analyze.describe([2.] * 10)
        self.assertEqual(result['exploratory_bootstrap_95_percent_interval'], [2., 2.])

    def test_bootstrap_deterministic(self):
        self.assertEqual(analyze.describe(list(range(10))), analyze.describe(list(range(10))))

    def test_contrast_direction(self):
        row = {'project': '01', 'scores': {'invariant_reservoir': {'nmse': .8},
               'ridge_reservoir': {'nmse': 1.}, 'linear_lag_baseline': {'nmse': .6}}}
        result = analyze.contrasts(row)
        self.assertAlmostEqual(result['error_reduction_vs_ridge_reservoir'], .2)
        self.assertAlmostEqual(result['error_reduction_vs_linear_lag_baseline'], -.2)

    def test_integrity_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = b'original evidence'
            (root / 'evidence.txt').write_bytes(payload)
            (root / 'SHA256.json').write_text(json.dumps({'evidence.txt': hashlib.sha256(payload).hexdigest()}))
            analyze.verify_hashes(root)
            (root / 'evidence.txt').write_bytes(b'altered evidence')
            with self.assertRaises(ValueError):
                analyze.verify_hashes(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
