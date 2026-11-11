"""AI-authored API integration tests, no provider calls."""
import unittest
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.source_evidence import load_source

class CalculationAPITests(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app)
        self.cells={(c['metric'],c['year']):c for c in load_source()[1]}
        self.request={'current_id':self.cells['cash',2024]['id'],'base_id':self.cells['cash',2023]['id'],'mode':'balance_yoy'}
    def test_options_and_registered_calculation(self):
        r=self.client.get('/api/source-calculations/options');self.assertEqual(r.status_code,200)
        self.assertEqual(len(r.json()['cells']),18);self.assertIn('balance_yoy',r.json()['modes'])
        self.assertTrue(r.json()['document']['calculation_supported'])
        self.assertEqual(r.json()['document'],self.client.get('/api/source-documents').json()[0])
        r=self.client.post('/api/source-calculations',json=self.request);self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['growth_pct'],'47.6820');self.assertEqual(r.json()['source_integrity'],'registered_snapshot')
    def test_rejects_values_unknown_ids_and_invalid_mode(self):
        for request in [self.request|{'value':'1'},self.request|{'mode':'custom'},self.request|{'current_id':None},{}]:
            self.assertEqual(self.client.post('/api/source-calculations',json=request).status_code,422)
        self.assertEqual(self.client.post('/api/source-calculations',json=self.request|{'current_id':'not-found'}).status_code,404)
    def test_data_failure_is_503_then_recovers(self):
        from unittest.mock import patch
        with patch('quarterguard.source_evidence.load_source',side_effect=ValueError('SOURCE_EVIDENCE_INTEGRITY')):
            self.assertEqual(self.client.post('/api/source-calculations',json=self.request).status_code,503)
        self.assertEqual(self.client.post('/api/source-calculations',json=self.request).status_code,200)
    def test_old_search_still_candidate_only(self):
        r=self.client.get('/api/source-search',params={'document_id':self.cells['cash',2024]['document_id'],'q':'2024 현금'})
        self.assertIsNone(r.json()['calculated_answer']);self.assertEqual(r.json()['answer_status'],'not_calculated')
