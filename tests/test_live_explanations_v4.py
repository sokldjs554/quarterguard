"""Offline safety checks; provider responses here are synthetic, never live results."""
import asyncio
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from quarterguard import evaluate_live_explanations_v4 as m


class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = asyncio.run(m.prepare_freeze())

    def test_same_cases_and_model_new_context_and_bounded_payload(self):
        old=json.loads((m.baseline.DATA/'freeze.json').read_text())
        m.validate_freeze(self.frozen)
        self.assertEqual(m.CONTRACT['model'],old['contract']['model'])
        self.assertEqual(len(self.frozen['cases']),8)
        for new,previous in zip(self.frozen['cases'],old['cases']):
            self.assertEqual(new['tool_result'],previous['tool_result'])
            self.assertEqual(new['untrusted_draft'],previous['untrusted_draft'])
            payload=m.make_payload(new)
            self.assertLessEqual(m.input_admission_bound(payload),6500)
            self.assertIn('explanation_context',json.loads(payload['input']))
            self.assertNotEqual(new['payload_sha256'],previous['payload_sha256'])
        with self.assertRaisesRegex(ValueError,'INPUT_ADMISSION_LIMIT'):
            m.make_payload({'task':'한글'*6500,'tool_result':{'evidence':[],'issues':[]}})

    def test_tampered_task_is_rejected_even_when_content_digest_is_recomputed(self):
        frozen=copy.deepcopy(self.frozen)
        frozen['cases'][0]['task']='changed after seeing response'
        frozen['content_sha256']=m.digest({k:v for k,v in frozen.items() if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError,'BASELINE_MISMATCH'):
            m.validate_freeze(frozen)

    def test_approval_and_attempt_journal_are_required(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'EXPLICIT_APPROVAL_REQUIRED'):
                m.execute(self.frozen,Path(d))
            (Path(d)/'attempts.jsonl').write_text('preserve failed attempt\n')
            with self.assertRaisesRegex(ValueError,'RUN_ALREADY_ATTEMPTED'):
                m.execute(self.frozen,Path(d),execute_approved=True)
            self.assertEqual((Path(d)/'attempts.jsonl').read_text(),'preserve failed attempt\n')

    def test_failure_stops_after_one_attempt_and_redacts_exception(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'test-secret'}),\
                patch.object(m.httpx,'post',side_effect=httpx.ReadTimeout('test-secret')) as post:
            report=m.execute(self.frozen,Path(d),execute_approved=True)
            self.assertEqual(report['calls_attempted'],1)
            self.assertEqual(report['status'],'failed')
            self.assertEqual(post.call_count,1)
            self.assertEqual(report['unmeasured_failed_attempts'],1)
            self.assertNotIn('test-secret',''.join(p.read_text() for p in Path(d).iterdir()))

    def test_usage_over_budget_stops_and_keeps_actual_usage(self):
        response=httpx.Response(200,json={'id':'synthetic','model':m.MODEL,'status':'completed',
            'usage':{'input_tokens':6501,'output_tokens':10,'total_tokens':6511},'output':[]})
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'test-secret'}),\
                patch.object(m.httpx,'post',return_value=response) as post:
            report=m.execute(self.frozen,Path(d),execute_approved=True)
            self.assertEqual(report['calls_attempted'],1)
            self.assertEqual(report['records'][0]['failure_code'],'PROVIDER_USAGE_LIMIT_EXCEEDED')
            self.assertEqual(report['measured_input_tokens'],6501)
            self.assertEqual(post.call_count,1)

    def test_presentation_checks_are_literal_not_semantic_certification(self):
        case=self.frozen['cases'][0]
        text='삼성전자 2024년 3분기 백만 원. 999% 증가했습니다.'
        result=m.audit(m.structured_answer(case['tool_result'],text),case)
        self.assertTrue(result['presentation_checks']['display_unit_named'])
        self.assertFalse(result['presentation_checks']['document_and_page_named'])
        self.assertIn('PERCENT_MISMATCH',result['issues'])
        self.assertFalse(result['semantic_certified'])
        empty=next(c for c in self.frozen['cases'] if c['id']=='no-evidence')
        self.assertTrue(m.presentation_checks({'explanation_ko':'해당 검색 범위에서 확인할 수 없습니다.'},empty)['scope_limited_if_no_evidence'])

    def test_eight_synthetic_responses_preserve_blank_human_verdicts(self):
        responses=[]
        for case in self.frozen['cases']:
            answer=m.structured_answer(case['tool_result'],'합성 테스트 문장입니다.')
            responses.append(httpx.Response(200,json={'id':'synthetic-'+case['id'],
                'status':'completed','model':m.MODEL,
                'usage':{'input_tokens':500,'output_tokens':100,'total_tokens':600},
                'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]}))
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'OPENAI_API_KEY':'test-secret'}),\
                patch.object(m.httpx,'post',side_effect=responses) as post:
            report=m.execute(self.frozen,Path(d),execute_approved=True)
            self.assertEqual(report['calls_attempted'],8)
            self.assertEqual(report['generated_count'],8)
            self.assertEqual(post.call_count,8)
            self.assertEqual(report['usage_estimated_cost_usd'],'0.006600')
            human=json.loads((Path(d)/'human-review.json').read_text())
            self.assertEqual(len(human),8)
            self.assertTrue(all(r['verdict'] is None and r['reviewer'] is None for r in human))
            self.assertTrue(all(r['semantic_certified'] is False for r in human))
