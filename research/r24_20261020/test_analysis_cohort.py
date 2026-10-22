"""Constructed manifest admission; no model or scientific data execution."""

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import analyze


class AnalysisCohortTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / 'run'
        self.root.mkdir()
        self.output = self.parent / 'analysis'
        self.manifest = {'phase': 'DEVELOPMENT', 'status': 'DEVELOPMENT_FINISHED',
                         'projects': ['01'], 'seeds': [0], 'failure_count': 0}
        self.record = {'phase': 'DEVELOPMENT', 'project': '01', 'seed': 0,
                       'scores': {'invariant_reservoir': {'nmse': .8},
                                  'ridge_reservoir': {'nmse': 1.},
                                  'linear_lag_baseline': {'nmse': .6}}}
        self.write_receipt(0, self.record)

    def write_receipt(self, path_seed, record):
        path = self.root / f'p01_seed{path_seed}' / 'metrics.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(record))

    def invoke(self):
        (self.root / 'manifest.json').write_text(json.dumps(self.manifest))
        inventory = {path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in self.root.rglob('*.json') if path.name != 'SHA256.json'}
        (self.root / 'SHA256.json').write_text(json.dumps(inventory))
        with patch('sys.argv', ['analyze.py', str(self.root), '--output', str(self.output)]):
            with redirect_stdout(io.StringIO()):
                analyze.main()

    def assert_rejected(self):
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertFalse(self.output.exists())

    def test_duplicate_seed_cannot_turn_one_receipt_into_ten_replicates(self):
        self.manifest['seeds'] = [0] * 10
        self.assert_rejected()

    def test_boolean_seed_is_rejected(self):
        self.manifest['seeds'] = [False]
        self.assert_rejected()

    def test_float_seed_is_rejected(self):
        self.manifest['seeds'] = [0.0]
        self.assert_rejected()

    def test_empty_seed_list_is_rejected(self):
        self.manifest['seeds'] = []
        self.assert_rejected()

    def test_negative_seed_is_rejected(self):
        self.manifest['seeds'] = [-1]
        self.assert_rejected()

    def test_seed_outside_runner_domain_is_rejected(self):
        self.manifest['seeds'] = [1_000_000]
        self.assert_rejected()

    def test_nonarray_seed_container_is_rejected(self):
        self.manifest['seeds'] = 0
        self.assert_rejected()

    def test_unhashable_seed_identity_is_rejected(self):
        self.manifest['seeds'] = [[]]
        self.assert_rejected()

    def test_duplicate_project_is_rejected(self):
        self.manifest['projects'] = ['01', '01']
        self.assert_rejected()

    def test_unsupported_project_is_rejected(self):
        self.manifest['projects'] = ['99']
        self.assert_rejected()

    def test_nonarray_project_container_is_rejected(self):
        self.manifest['projects'] = '01'
        self.assert_rejected()

    def test_empty_project_list_is_rejected(self):
        self.manifest['projects'] = []
        self.assert_rejected()

    def test_unhashable_project_identity_is_rejected(self):
        self.manifest['projects'] = [[]]
        self.assert_rejected()

    def test_boolean_receipt_seed_is_rejected(self):
        self.record['seed'] = False
        self.write_receipt(0, self.record)
        self.assert_rejected()

    def test_float_receipt_seed_is_rejected(self):
        self.record['seed'] = 0.0
        self.write_receipt(0, self.record)
        self.assert_rejected()

    def test_unique_nonconsecutive_seeds_keep_replicate_counts(self):
        self.manifest['seeds'] = [0, 5]
        other = dict(self.record, seed=5)
        self.write_receipt(5, other)
        self.invoke()
        summary = json.loads((self.output / 'development_summary.json').read_text())
        self.assertEqual(summary['scientific_disposition'], 'UNCONFIRMED')
        for result in summary['projects']['01']['statistics'].values():
            self.assertEqual(result['replicates'], 2)
            self.assertIsNone(result['exploratory_bootstrap_95_percent_interval'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
