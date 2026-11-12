import json
import unittest
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.store import ROOT


class CloseoutSummaryTests(unittest.TestCase):
    def test_current_summary_includes_confirmed_work_without_rewriting_history(self):
        summary = TestClient(app).get('/api/evaluation/latest').json()['summary']
        self.assertEqual(summary['as_of_kst'], '2026-11-13')
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

    def test_new_generation_review_is_added_without_rewriting_unreviewed_snapshot(self):
        summary=TestClient(app).get('/api/evaluation/latest').json()['summary']
        batch=summary['current_status']['fresh_batch']
        actual=json.loads((ROOT/'artifacts/closeout-live-20261112/summary.json').read_text())
        self.assertEqual(batch['calls'],actual['actual_calls'])
        self.assertEqual(batch['passed'],actual['product_passed'])
        self.assertTrue(batch['human_reviewed'])
        self.assertEqual(batch['human_verdict_counts'],{'참':17,'모호':3,'거짓':0})
        before=json.loads((ROOT/'data/latest-progress-closeout-live-20261112.json').read_text())
        self.assertFalse(before['current_status']['fresh_batch']['human_reviewed'])
        prepared=json.loads((ROOT/'data/latest-progress-closeout-20261112.json').read_text())
        self.assertNotIn('fresh_batch',prepared['current_status'])
        sheet=json.loads((ROOT/'docs/validation-kit/closeout-live-20261112/review-sheet.json').read_text())
        self.assertEqual(len(sheet['rows']),20)
        self.assertTrue(all(r['explanation_verdict'] is None for r in sheet['rows']))

    def test_final_replay_distinguishes_execution_pass_from_human_review(self):
        s=TestClient(app).get('/api/evaluation/latest').json()['summary']['current_status']
        self.assertEqual(s['closeout']['status'],'completed')
        self.assertEqual(s['closeout']['replay_passed'],7)
        self.assertEqual(s['closeout']['human_true_withheld'],10)
        self.assertEqual(s['closeout']['human_ambiguous_withheld'],3)
        self.assertEqual(s['fresh_batch']['passed'],8)


    def test_latest_binding_replay_preserves_original_generation_and_review(self):
        s=TestClient(app).get('/api/evaluation/latest').json()['summary']['current_status']
        followup=s['prose_binding_followup']
        self.assertEqual((followup['before_passed'],followup['after_passed']),(7,17))
        self.assertEqual(followup['human_true_withheld'],0)
        self.assertEqual(followup['human_ambiguous_withheld'],3)
        self.assertEqual(followup['new_paid_calls'],0)
        self.assertEqual(followup['new_human_reviews'],0)
        self.assertEqual(s['fresh_batch']['passed'],8)
        self.assertEqual(s['closeout']['replay_passed'],7)
