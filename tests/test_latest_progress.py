import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.store import ROOT


class LatestProgressTests(unittest.TestCase):
    def test_latest_is_separate_from_unchanged_historical_snapshot(self):
        c=TestClient(app)
        historical=c.get('/api/evaluation/current/progress').json()
        self.assertEqual(historical,json.loads((ROOT/'artifacts/progress-v2-final.json').read_text()))
        self.assertEqual(historical['created_at'],'2026-10-31T12:47:32.201099+00:00')
        response=c.get('/api/evaluation/latest')
        self.assertEqual(response.status_code,200)
        r=response.json()
        self.assertEqual(r['summary']['as_of_kst'],'2026-11-10')
        self.assertIn('runtime_commit',r)
        self.assertEqual(r['summary']['human_review']['followup'],{'참':7,'모호':1})
        self.assertEqual(r['summary']['llm']['calls_per_batch'],[8,8])
        self.assertEqual(r['summary']['production']['companies'],['samsung'])
        self.assertFalse(r['summary']['hyundai']['production_registered'])

    def test_missing_or_tampered_sources_fail_closed_without_history_fallback(self):
        from quarterguard.latest_progress import load_latest_progress
        original=Path.read_bytes
        def tampered(path):
            data=original(path)
            return data+b' ' if path==ROOT/'artifacts/human-llm-followup-20261110/review.json' else data
        with patch.object(Path,'read_bytes',tampered):
            with self.assertRaisesRegex(ValueError,'SUMMARY_SOURCE_MISMATCH'):load_latest_progress()
            r=TestClient(app).get('/api/evaluation/latest')
            self.assertEqual(r.status_code,503)
            self.assertEqual(r.json()['detail'],'LATEST_EVIDENCE_UNAVAILABLE')

    def test_counts_and_reference_hashes_match_published_evidence(self):
        from quarterguard.latest_progress import load_latest_progress
        r=load_latest_progress()
        for name,sha in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)
        hy=json.loads((ROOT/'artifacts/hyundai-final-20261109/summary.json').read_text())
        self.assertEqual(r['hyundai']['raw_cells'],hy['final_first_raw_cell_summary'])
        old=json.loads((ROOT/'artifacts/human-review-followup-20261110/review.json').read_text())
        new=json.loads((ROOT/'artifacts/human-llm-followup-20261110/review.json').read_text())
        for key in ['참','모호']:
            self.assertEqual(r['human_review']['baseline'][key],old['verdict_counts'][key])
            self.assertEqual(r['human_review']['followup'][key],new['reported_counts'][key])
        self.assertEqual(r['personal_review']['added_tests'],5)
        self.assertEqual(r['verification']['python_tests'],191)
        self.assertIn('Ran 191 tests',(ROOT/r['verification']['log']).read_text())
