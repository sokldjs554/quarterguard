import json
import unittest
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.store import ROOT


class CloseoutSummaryTests(unittest.TestCase):
    def test_current_summary_includes_confirmed_work_without_rewriting_history(self):
        summary = TestClient(app).get('/api/evaluation/latest').json()['summary']
        self.assertEqual(summary['as_of_kst'], '2026-11-12')
        current = summary['current_status']
        self.assertEqual(current['author_questions'], {'skhynix': 5, 'apple': 7})
        self.assertEqual(current['human_completion_counts'], {'참': 11, '거짓': 4, '모호': 5})
        self.assertTrue(current['json_followup_complete'])
        self.assertTrue(summary['llm']['v9_generation_batch']['human_reviewed'])
        old = json.loads((ROOT/'data/latest-progress-v9-20261111.json').read_text())
        self.assertFalse(old['llm']['v9_generation_batch']['human_reviewed'])
        self.assertEqual(old['llm']['v9_generation_batch']['human_authored_cases_received'], 0)

    def test_sk_current_catalog_matches_supported_calculations(self):
        from quarterguard.source_calculations import options
        document = options()['document']
        self.assertTrue(document['calculation_supported'])
        self.assertNotIn('No annual, balance-change, product-share or inventory-ratio answer calculation.', document['limitations'])
        self.assertIn('inventory_months', document['clarification_only_modes'])

    def test_new_generation_has_its_own_unreviewed_record(self):
        summary=TestClient(app).get('/api/evaluation/latest').json()['summary']
        batch=summary['current_status']['fresh_batch']
        actual=json.loads((ROOT/'artifacts/closeout-live-20261112/summary.json').read_text())
        self.assertEqual(batch['calls'],actual['actual_calls'])
        self.assertEqual(batch['passed'],actual['product_passed'])
        self.assertFalse(batch['human_reviewed'])
        prepared=json.loads((ROOT/'data/latest-progress-closeout-20261112.json').read_text())
        self.assertNotIn('fresh_batch',prepared['current_status'])
        sheet=json.loads((ROOT/'docs/validation-kit/closeout-live-20261112/review-sheet.json').read_text())
        self.assertEqual(len(sheet['rows']),20)
        self.assertTrue(all(r['explanation_verdict'] is None for r in sheet['rows']))

