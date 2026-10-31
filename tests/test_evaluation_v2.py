"""Evaluation integrity tests: do not turn parser/search observations into gold."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from quarterguard.core import Fact
from quarterguard.evaluation_v2 import DATA, calculation_observation, exact_fact, load_frozen, query_observation


class EvaluationV2IntegrityTests(unittest.TestCase):
    def test_frozen_manifest_and_balanced_identifiers(self):
        freeze, data = load_frozen()
        self.assertFalse(freeze['human_reviewed'])
        self.assertFalse(freeze['pipeline_run_before_freeze'])
        self.assertEqual(len(data['facts']), 80)
        self.assertEqual(len(data['retrieval_gold']), 24)
        ids = {f['id'] for f in data['facts']}
        self.assertEqual(ids, {c['fact_id'] for c in data['source_cells']})
        for q in data['retrieval_gold']:
            self.assertTrue(set(q['gold_fact_ids']) <= ids)
        self.assertEqual({s['company'] for s in data['sources']}, {'samsung', 'hyundai'})

    def test_a_single_changed_gold_byte_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            for path in DATA.glob('*.json'):
                (temp / path.name).write_bytes(path.read_bytes())
            with (temp / 'facts.json').open('a') as handle:
                handle.write(' ')
            with self.assertRaisesRegex(ValueError, 'FROZEN_INPUT_CHANGED'):
                load_frozen(temp)

    def test_exact_cell_requires_value_and_every_citation_context_field(self):
        row = json.loads((DATA / 'facts.json').read_text())[0]
        fact = Fact(**row)
        self.assertTrue(exact_fact(fact, row))
        changes = {'value': '1', 'page': 999, 'company': 'hyundai', 'scope': 'OFS',
                   'row': 'Profit for the period', 'column': '2022 Q KRW',
                   'document_sha256': '0' * 64, 'source_url': 'https://example.com',
                   'start': '2023-01-01', 'end': '2023-09-30', 'scale': 1, 'currency': 'USD'}
        for key, value in changes.items():
            with self.subTest(field=key):
                self.assertFalse(exact_fact(replace(fact, **{key: value}), row))

    def test_failed_ingestion_never_gets_credit_for_negative_query(self):
        case = {'query': 'ambiguous', 'gold_fact_ids': [], 'expected_answerable': False,
                'expected_clarification': True}
        self.assertFalse(query_observation(None, case)['passed'])

    def test_missing_raw_inputs_block_calculation_without_fixture_substitution(self):
        core = Mock()
        observation = calculation_observation(core, {'inputs': ['missing']}, {})
        self.assertFalse(observation['passed'])
        self.assertEqual(observation['status'], 'blocked_missing_parsed_fact')
        core.compare.assert_not_called()
        core.reconcile.assert_not_called()

    def test_top_rank_does_not_mean_trusted_complete_query(self):
        index = Mock()
        index.search_with_diagnostics.return_value = {'hits': [{'fact_ids': ['x']}],
            'status': 'needs_clarification', 'trusted_query': False, 'issues': ['MISSING_SCOPE']}
        case = {'query': 'incomplete', 'gold_fact_ids': ['x'], 'expected_answerable': True,
                'expected_clarification': False}
        result = query_observation(index, case)
        self.assertTrue(result['retrieval_passed'])
        self.assertFalse(result['passed'])


if __name__ == '__main__':
    unittest.main()
