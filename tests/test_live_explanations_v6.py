"""Bounded evaluation contract with fake HTTP only; no paid calls."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx


class ProseBatchTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('quarterguard.evaluate_live_explanations_v6'))
        from quarterguard import evaluate_live_explanations_v6 as m
        self.m = m
        self.frozen = m.prepare_freeze()

    def response(self, case, *, usage=200, text='합성 계약 테스트 문장입니다.'):
        result = case['tool_result']
        answer = {'status': result['status'], 'value': result.get('growth_pct'),
                  'issues': result['issues'], 'evidence_ids': [f['id'] for f in result['evidence']],
                  'explanation_ko': text}
        return httpx.Response(200, json={'id': 'fixture', 'status': 'completed', 'model': self.m.MODEL,
            'usage': {'input_tokens': usage, 'output_tokens': 100},
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(answer)}]}]})

    def test_two_groups_use_frozen_product_without_registering_production_facts(self):
        from quarterguard.core import source_facts
        before = copy.deepcopy(source_facts())
        self.m.validate_freeze(self.frozen)
        self.assertEqual(len(self.frozen['cases']), 16)
        self.assertEqual([c['cohort'] for c in self.frozen['cases']], ['paired_development']*8+['new_tasks_known_documents']*8)
        for case in self.frozen['cases']:
            payload=self.m.make_payload(case)
            self.assertLessEqual(self.m.input_admission_bound(payload), 8500)
            context=json.loads(payload['input'])['explanation_context']
            self.assertEqual(len(context['evidence']),len(case['tool_result']['evidence']))
            if case['tool_result']['evidence']:
                self.assertEqual(context['status'],'available')
                self.assertTrue(all(f['display_unit']=='백만 원' for f in context['evidence']))
        self.assertEqual(source_facts(), before)
        self.assertNotIn('h25q3-CFS-net_profit-2025-q-KRW', before)

    def test_modified_inputs_fail_even_with_recomputed_digest(self):
        frozen = copy.deepcopy(self.frozen)
        frozen['cases'][-1]['task'] = 'changed task'
        frozen['content_sha256'] = self.m.digest({k:v for k,v in frozen.items() if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError, 'FROZEN_CASES_MISMATCH'):
            self.m.validate_freeze(frozen)

    def test_code_change_and_missing_approval_precede_any_http_or_journal(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(self.m.httpx, 'post') as post:
            with self.assertRaisesRegex(ValueError, 'EXPLICIT_APPROVAL_REQUIRED'):
                self.m.execute(self.frozen, Path(tmp)/'out')
            with patch.object(self.m, 'source_hashes', return_value={}):
                with self.assertRaisesRegex(ValueError, 'FREEZE_CODE_MISMATCH'):
                    self.m.execute(self.frozen, Path(tmp)/'out', approved=True)
            self.assertFalse((Path(tmp)/'out').exists())
            post.assert_not_called()

    def test_completed_sixteen_preserve_blank_human_labels_and_separate_cohorts(self):
        replies=[self.response(c) for c in self.frozen['cases']]
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'OPENAI_API_KEY':'fake-secret'}), \
                patch.object(self.m.httpx, 'post', side_effect=replies) as post:
            out=Path(tmp)/'run'
            report=self.m.execute(self.frozen,out,approved=True)
            self.assertEqual(report['calls_attempted'],16)
            self.assertEqual(post.call_count,16)
            self.assertEqual(report['cohorts']['paired_development']['generated'],8)
            self.assertEqual(report['cohorts']['new_tasks_known_documents']['generated'],8)
            human=json.loads((out/'human-review.json').read_text())
            self.assertTrue(all(x['verdict'] is None and x['reviewer'] is None for x in human))
            with self.assertRaisesRegex(ValueError,'OUTPUT_ALREADY_EXISTS'):
                self.m.execute(self.frozen,out,approved=True)
            self.assertEqual(post.call_count,16)

    def test_http_timeout_and_invalid_response_stop_without_retry_or_secret_leak(self):
        for response in [httpx.Response(400,text='fake-secret'),httpx.ReadTimeout('fake-secret'),
                         httpx.Response(200,json={'secret':'fake-secret'})]:
            with self.subTest(response=type(response).__name__), tempfile.TemporaryDirectory() as tmp, \
                    patch.dict('os.environ',{'OPENAI_API_KEY':'fake-secret'}), \
                    patch.object(self.m.httpx,'post',**({'side_effect':response} if isinstance(response,Exception) else {'return_value':response})) as post:
                report=self.m.execute(self.frozen,Path(tmp)/'run',approved=True)
                self.assertEqual(report['calls_attempted'],1)
                self.assertEqual(report['status'],'failed')
                self.assertEqual(post.call_count,1)
                self.assertNotIn('fake-secret',''.join(p.read_text() for p in (Path(tmp)/'run').iterdir()))

    def test_usage_over_limit_preserves_cost_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'OPENAI_API_KEY':'fake'}), \
                patch.object(self.m.httpx,'post',return_value=self.response(self.frozen['cases'][0],usage=8501)) as post:
            report=self.m.execute(self.frozen,Path(tmp)/'run',approved=True)
            self.assertEqual(report['records'][0]['failure_code'],'USAGE_LIMIT_EXCEEDED')
            self.assertEqual(report['measured_input_tokens'],8501)
            self.assertEqual(post.call_count,1)

    def test_disclosed_bad_prose_is_preserved_and_current_product_gate_rejects(self):
        case=self.frozen['cases'][0]
        replies=[self.response(c) for c in self.frozen['cases']]
        replies[0]=self.response(case,text='매출 증가율은 6.7916입니다.')
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'OPENAI_API_KEY':'fake'}), \
                patch.object(self.m.httpx,'post',side_effect=replies):
            report=self.m.execute(self.frozen,Path(tmp)/'run',approved=True)
            first=report['records'][0]
            self.assertFalse(first['production_gate_passed'])
            self.assertIn('6.7916입니다',first['generated']['explanation_ko'])
            self.assertEqual(len(json.loads((Path(tmp)/'run/comparison.json').read_text())['pairs']),8)

    def test_oversized_request_and_wrong_returned_model_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'INPUT_ADMISSION_LIMIT'):
            self.m.make_payload(self.frozen['cases'][0]|{'task':'x'*20000})
        response=self.response(self.frozen['cases'][0]).json();response['model']='different-model'
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'OPENAI_API_KEY':'fake'}), \
                patch.object(self.m.httpx,'post',return_value=httpx.Response(200,json=response)) as post:
            report=self.m.execute(self.frozen,Path(tmp)/'run',approved=True)
            self.assertEqual(report['records'][0]['failure_code'],'MODEL_MISMATCH')
            self.assertEqual(post.call_count,1)
