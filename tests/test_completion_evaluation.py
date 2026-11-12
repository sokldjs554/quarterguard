import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import httpx
from quarterguard import completion_evaluation as e


class CompletionEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def client(self, transport):
        return e.PaidClient(self.root/'out', self.root/'ledger', approved=True, transport=transport)

    def test_new_approval_and_workflow_identity_required(self):
        with self.assertRaisesRegex(ValueError, 'APPROVAL'):
            e.PaidClient(self.root/'out', self.root/'ledger')
        with patch.dict('os.environ', {}, clear=True), self.assertRaisesRegex(ValueError, 'AUTHORIZED_WORKFLOW'):
            e.PaidClient(self.root/'out', self.root/'ledger', approved=True)

    def test_caps_include_eight_decisions_per_task_and_no_more_than_52_calls(self):
        client = self.client(lambda p: httpx.Response(200, json={}))
        payload = {'model': e.MODEL, 'max_output_tokens':700}
        for _ in range(52):client.post('https://api.openai.com/v1/responses', json=payload)
        with self.assertRaisesRegex(ValueError, 'CALL_LIMIT'):
            client.post('https://api.openai.com/v1/responses', json=payload)
        self.assertEqual(e.CONTRACT['max_calls'], 20+4*8)
        maximum = (Decimal(16000)*Decimal('.4')+Decimal(700)*Decimal('1.6'))*52/1000000
        self.assertEqual(maximum, Decimal(e.CONTRACT['estimated_max_usd']))

    def test_provider_failure_stops_remaining_requests_without_retry(self):
        seen=[]
        def fail(payload):
            seen.append(payload)
            return httpx.Response(404, text='private provider message')
        client=self.client(fail)
        payload={'model':e.MODEL,'max_output_tokens':700}
        client.post('https://api.openai.com/v1/responses', json=payload)
        with self.assertRaisesRegex(ValueError,'BATCH_STOPPED'):
            client.post('https://api.openai.com/v1/responses', json=payload)
        self.assertEqual(len(seen),1)
        self.assertNotIn('private provider', (self.root/'out/response-01.json').read_text())
        with self.assertRaises(FileExistsError):
            e.PaidClient(self.root/'second', self.root/'ledger', approved=True, transport=fail)

    def test_frozen_replay_inputs_fit_budget_and_remain_product_model(self):
        self.assertEqual(len(e.replay_cases()),16)
        for case in e.replay_cases():
            payload=e.replay_payload(case)
            self.assertEqual(payload['model'],e.MODEL)
            self.assertLessEqual(len(json.dumps(payload,ensure_ascii=False).encode())+1024,16000)
            self.assertEqual(json.loads(payload['input'])['tool_result'],case['tool_result'])

    def test_bad_model_and_oversize_never_reserve_a_call(self):
        client=self.client(lambda p: self.fail('must not call'))
        for payload in ({'model':'other','max_output_tokens':700},
                        {'model':e.MODEL,'max_output_tokens':700,'input':'x'*16000}):
            with self.assertRaises(ValueError):client.post('https://api.openai.com/v1/responses', json=payload)
        self.assertEqual(client.attempts,0)

    def test_human_packet_keeps_rejected_raw_prose_without_making_up_verdicts(self):
        answer={'explanation_ko':'잘못된 원응답'}
        (self.root/'response-01.json').write_text(json.dumps({'output':[{'type':'message','content':[
            {'type':'output_text','text':json.dumps(answer)}]}]}))
        report={'explanations':[{'case_id':'bad','source_execution':'replay',
            'tool_result':{},'generation':'rejected','response_file':'response-01.json'}]}
        row=e.human_packet(report,self.root)[0]
        self.assertEqual(row['raw_generated'],answer)
        self.assertIsNone(row['human_verdict']);self.assertIsNone(row['reviewer'])
