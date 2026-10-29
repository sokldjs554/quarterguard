"""Harness integrity tests; benchmark failures are reported, not disguised as passes."""
from fractions import Fraction
from dataclasses import asdict
import hashlib
import json
import unittest
from unittest.mock import patch

from quarterguard.core import source_manifest, valid_source
from quarterguard.heldout_evaluation import DATA, ROOT, downstream, load_frozen
from quarterguard.search import SearchIndex


class HeldoutHarnessTests(unittest.TestCase):
    def setUp(self):
        self.freeze, self.sources, self.facts, self.cases = load_frozen(post_fix=True)
        self.manifest = {s['id']: s for s in self.sources}

    def test_gold_is_frozen_and_new_documents_are_separate(self):
        self.assertEqual(len(self.sources), 2)
        self.assertEqual(len(self.facts), 64)
        self.assertEqual(len(self.cases), 40)
        self.assertFalse(set(self.manifest) & set(source_manifest()))
        self.assertFalse(self.freeze['human_reviewed'])
        self.assertEqual(len({c['id'] for c in self.cases}), len(self.cases))

    def test_expected_growth_uses_independent_rational_arithmetic(self):
        for case in self.cases:
            if case['stage'] != 'fixture_calculation' or case['operation'] != 'compare':
                continue
            a, b = [int(self.facts[id].value) for id in case['inputs']]
            rounded = round((Fraction(a, b) - 1) * 1000000)
            self.assertEqual(int(Fraction(case['expected_value']) * 10000), rounded)

    def test_manifest_adapter_keeps_real_validator_and_restores_registry(self):
        fact = next(iter(self.facts.values()))
        self.assertFalse(valid_source(fact))
        with patch('quarterguard.core.source_manifest', return_value=self.manifest), \
                patch('quarterguard.core.source_facts', return_value={id: asdict(f) for id, f in self.facts.items()}):
            self.assertTrue(valid_source(fact))
            case = next(c for c in self.cases if c['id'] == 'citation-hash')
            result = downstream(case, self.facts, None)
            self.assertFalse(result['actual_valid'])
            self.assertTrue(result['passed'])
        self.assertFalse(valid_source(fact))

    def test_real_source_disagreement_is_not_replaced_with_derived_gold(self):
        case = next(c for c in self.cases if c['id'] == 'calc-08')
        with patch('quarterguard.core.source_manifest', return_value=self.manifest), \
                patch('quarterguard.core.source_facts', return_value={id: asdict(f) for id, f in self.facts.items()}):
            result = downstream(case, self.facts, None)
        self.assertEqual(result['result']['derived_value'], '0')
        self.assertEqual(result['result']['difference'], '-5116435')
        self.assertEqual(result['result']['issues'], ['NUMERIC_CONFLICT'])
        self.assertTrue(result['passed'])

    def test_first_run_records_every_failure_and_is_identifiable(self):
        baseline_path = DATA / 'first-run.json'
        baseline = json.loads(baseline_path.read_text())
        artifact = json.loads((ROOT / 'artifacts/heldout-evaluation.json').read_text())
        self.assertEqual(artifact['first_run_sha256'], hashlib.sha256(baseline_path.read_bytes()).hexdigest())
        self.assertEqual(baseline['freeze'], self.freeze)
        self.assertEqual(baseline['failure_ids'], [r['id'] for r in baseline['results'] if not r['passed']])
        self.assertEqual(len(baseline['failure_ids']), 12)
        self.assertEqual(baseline['raw_registry']['accepted'], 0)
        self.assertEqual(sum(a['passed'] for a in baseline['source_audit']), 64)

    def test_natural_query_failure_is_visible(self):
        case = next(c for c in self.cases if c['id'] == 'retrieve-06')
        result = downstream(case, self.facts, SearchIndex(list(self.facts.values())))
        self.assertIsNone(result['rank'])
        self.assertEqual(result['retrieved'], [])
        self.assertFalse(result['passed'])


if __name__ == '__main__':
    unittest.main()
