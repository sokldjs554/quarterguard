"""Synthetic control comparisons, not additional provider responses."""
import copy
import importlib.util
import json
import unittest
from unittest.mock import patch
import httpx
from quarterguard.store import ROOT
from quarterguard import public_providers

spec=importlib.util.spec_from_file_location('followup_compare',ROOT/'scripts/compare_explanation_followup.py')
comparison=importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class PairedComparisonTests(unittest.TestCase):
    def setUp(self):
        self.baseline=json.loads((ROOT/'artifacts/llm-live-20261109/report.json').read_text())
        self.frozen=json.loads((ROOT/'data/llm-followup-20261110/freeze.json').read_text())
        self.control=copy.deepcopy(self.baseline)
        self.control['freeze_sha256']=self.frozen['content_sha256']

    def test_identical_outputs_have_identical_audits_and_no_new_human_labels(self):
        report=comparison.compare_reports(self.baseline,self.control,self.frozen)
        self.assertEqual(report['baseline'],report['followup'])
        self.assertEqual(report['followup']['structured_exact'],8)
        self.assertTrue(all(p['followup_human_verdict'] is None for p in report['pairs']))

    def test_changed_model_or_source_is_not_a_paired_comparison(self):
        self.control['contract']['model']='different-model'
        with self.assertRaisesRegex(ValueError,'MODEL_MISMATCH'):
            comparison.compare_reports(self.baseline,self.control,self.frozen)
        self.control['contract']['model']=self.baseline['contract']['model']
        self.control['records'][0]['tool_result']['growth_pct']='999'
        with self.assertRaisesRegex(ValueError,'INPUT_MISMATCH'):
            comparison.compare_reports(self.baseline,self.control,self.frozen)

    def test_missing_response_stays_missing_in_counts_and_review(self):
        self.control['records']=self.control['records'][:1]
        report=comparison.compare_reports(self.baseline,self.control,self.frozen)
        self.assertEqual(report['followup']['completed'],1)
        self.assertEqual(len(report['pairs']),8)
        self.assertIsNone(report['pairs'][1]['followup_generated'])

    def test_observed_followup_citation_typo_is_rejected_by_public_guard(self):
        report=json.loads((ROOT/'artifacts/llm-followup-20261110/report.json').read_text())
        row=next(r for r in report['records'] if r['case_id']=='normal-yoy')
        self.assertEqual(row['generated']['evidence_ids'][1],'s24q3-CFS-revenue-2023-q-KKR')
        # Replay the actual generated JSON with synthetic public-provider metadata.
        # This is not a fresh GPT-4.1-mini response or network request.
        response=httpx.Response(200,json={'status':'completed','model':public_providers.MODEL,
            'usage':{'input_tokens':100,'output_tokens':100},
            'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(row['generated'])}]}]})
        with patch.dict('os.environ',{'OPENAI_API_KEY':'test-only'}),\
                patch.object(public_providers.httpx,'post',return_value=response):
            with self.assertRaisesRegex(RuntimeError,'OPENAI_RESPONSE_FAILED_OR_REJECTED'):
                public_providers.generate_public({},row['tool_result'])
