"""Offline contract checks; synthetic HTTP responses are never real model evidence."""
import asyncio
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from quarterguard import public_providers as pp


class CurrentGuardBatchTests(unittest.TestCase):
    def setUp(self):
        # Removing the new harness must fail explicitly before any possible call.
        self.assertIsNotNone(importlib.util.find_spec('quarterguard.evaluate_live_explanations_v5'))
        from quarterguard import evaluate_live_explanations_v5 as m
        self.m=m
        self.frozen=asyncio.run(m.prepare_freeze())

    def response(self, case, *, bad_id=False, usage=500):
        answer=self.m.structured_answer(case['tool_result'],'합성 테스트 문장입니다.')
        if bad_id:answer['evidence_ids'][-1]=answer['evidence_ids'][-1][:-3]+'KKR'
        return httpx.Response(200,json={'id':'synthetic-'+case['id'],'model':self.m.MODEL,'status':'completed',
            'usage':{'input_tokens':usage,'output_tokens':100,'total_tokens':usage+100},
            'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]})

    def test_current_product_instructions_context_and_schema_reach_every_payload(self):
        self.m.validate_freeze(self.frozen)
        for c in self.frozen['cases']:
            payload=self.m.make_payload(c);production=pp.build_payload(c['tool_result'],c['task'])
            self.assertEqual(payload['instructions'],production['instructions'])
            self.assertEqual(payload['text'],production['text'])
            self.assertEqual(json.loads(payload['input'])['explanation_context'],json.loads(production['input'])['explanation_context'])
            self.assertLessEqual(self.m.input_admission_bound(payload),7500)
        with self.assertRaises(ValueError):
            self.m.make_payload(self.frozen['cases'][0]|{'task':'A'*20000})

    def test_same_disclosed_cases_preserve_previous_mcp_inputs_and_drafts(self):
        old=json.loads(self.m.PREVIOUS_FREEZE.read_text())
        for current,previous in zip(self.frozen['cases'],old['cases']):
            for field in ('id','task','dimension','source_case_id','tool_result','untrusted_draft'):
                self.assertEqual(current[field],previous[field])
            self.assertNotEqual(current['payload_sha256'],previous['payload_sha256'])
        self.assertFalse(self.frozen['human_reviewed'])
        self.assertFalse(self.frozen['generation_started'])

    def test_tampered_input_rejected_even_with_recomputed_freeze_digest(self):
        frozen=copy.deepcopy(self.frozen);frozen['cases'][0]['task']='replacement'
        frozen['content_sha256']=self.m.digest({k:v for k,v in frozen.items() if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError,'BASELINE_MISMATCH'):self.m.validate_freeze(frozen)

    def test_changed_source_blocks_before_reading_key_or_contacting_provider(self):
        with tempfile.TemporaryDirectory() as d,patch.object(self.m,'source_hashes',return_value={}),patch.object(self.m.httpx,'post') as post:
            with self.assertRaisesRegex(ValueError,'FREEZE_CODE_OR_CONTRACT_MISMATCH'):
                self.m.execute(self.frozen,d,execute_approved=True)
            post.assert_not_called()
            self.assertFalse((Path(d)/'attempts.jsonl').exists())

    def test_approval_and_journal_prevent_calls_and_preserve_old_attempt(self):
        with tempfile.TemporaryDirectory() as d,patch.object(self.m.httpx,'post') as post:
            with self.assertRaisesRegex(ValueError,'EXPLICIT_APPROVAL_REQUIRED'):self.m.execute(self.frozen,d)
            p=Path(d)/'attempts.jsonl';p.write_text('previous failure\n')
            with self.assertRaisesRegex(ValueError,'RUN_ALREADY_ATTEMPTED'):self.m.execute(self.frozen,d,execute_approved=True)
            self.assertEqual(p.read_text(),'previous failure\n');post.assert_not_called()

    def test_timeout_stops_once_without_retry_or_exposing_key(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'fake-secret'}),patch.object(self.m.httpx,'post',side_effect=httpx.ReadTimeout('fake-secret')) as post:
            report=self.m.execute(self.frozen,d,execute_approved=True)
            self.assertEqual(report['calls_attempted'],1);self.assertEqual(post.call_count,1)
            self.assertEqual(report['records'][0]['failure_code'],'OPENAI_CONNECTION_FAILED')
            self.assertNotIn('fake-secret',''.join(p.read_text() for p in Path(d).iterdir()))

    def test_provider_schema_rejection_stops_once_and_preserves_http_failure(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'fake-secret'}),patch.object(self.m.httpx,'post',return_value=httpx.Response(400,text='fake-secret')) as post:
            report=self.m.execute(self.frozen,d,execute_approved=True)
            self.assertEqual(report['calls_attempted'],1);self.assertEqual(post.call_count,1)
            self.assertEqual(report['records'][0]['failure_code'],'OPENAI_HTTP_400')
            self.assertEqual(report['generated_count'],0)
            self.assertNotIn('fake-secret',''.join(p.read_text() for p in Path(d).iterdir()))

    def test_usage_over_cap_stops_and_preserves_measured_cost(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'fake-secret'}),patch.object(self.m.httpx,'post',return_value=self.response(self.frozen['cases'][0],usage=7501)) as post:
            report=self.m.execute(self.frozen,d,execute_approved=True)
            self.assertEqual(report['calls_attempted'],1);self.assertEqual(post.call_count,1)
            self.assertEqual(report['records'][0]['failure_code'],'PROVIDER_USAGE_LIMIT_EXCEEDED')
            self.assertEqual(report['measured_input_tokens'],7501)

    def test_wrong_id_is_preserved_for_audit_but_would_not_pass_product_gate(self):
        responses=[self.response(c,bad_id=c['id']=='normal-yoy') for c in self.frozen['cases']]
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'fake-secret'}),patch.object(self.m.httpx,'post',side_effect=responses) as post:
            report=self.m.execute(self.frozen,d,execute_approved=True)
            self.assertEqual(report['calls_attempted'],8);self.assertEqual(post.call_count,8)
            self.assertEqual(report['generated_count'],8);self.assertEqual(report['production_gate_passed_count'],7)
            row=next(r for r in report['records'] if r['case_id']=='normal-yoy')
            self.assertFalse(row['production_gate_passed']);self.assertFalse(row['production_checks']['citations_exact'])
            self.assertTrue(row['generated']['evidence_ids'][-1].endswith('KKR'))
            blank=json.loads((Path(d)/'human-review.json').read_text())
            self.assertEqual(len(blank),8)
            self.assertTrue(all(r['verdict'] is None and r['reviewer'] is None for r in blank))
            self.assertFalse(report['semantic_certified'])

    def test_comparison_reaudits_both_batches_without_copying_human_labels(self):
        old=json.loads(self.m.BASELINE.read_text())
        new=copy.deepcopy(old);new['freeze_sha256']=self.frozen['content_sha256']
        new['records'][1]['generated']['evidence_ids']=[f['id'] for f in self.frozen['cases'][1]['tool_result']['evidence']]
        report=self.m.compare_reports(old,new,self.frozen)
        self.assertEqual(report['baseline']['structured_exact'],7)
        self.assertEqual(report['followup']['structured_exact'],8)
        self.assertFalse(report['new_human_review'])
        self.assertIsNone(report['semantic_accuracy'])
        self.assertTrue(all(p['followup_human_verdict'] is None for p in report['pairs']))
