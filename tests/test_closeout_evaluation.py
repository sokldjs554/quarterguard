import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from quarterguard import closeout_evaluation as e


class CloseoutEvaluationTests(unittest.TestCase):
    def test_all_twenty_payloads_prepared_without_a_provider_call(self):
        with patch('httpx.post', side_effect=AssertionError('NO_PAID_CALL')):
            prepared = e.prepare()
        self.assertEqual(len(prepared['cases']),20)
        self.assertEqual(prepared['contract']['max_calls'],20)
        self.assertTrue(all(c['input_admission_bytes']<=16000 for c in prepared['cases']))
        self.assertEqual(prepared['contract']['estimated_max_usd'],'0.15040')
        self.assertTrue(all(c['source_execution']=='stored_tool_result' for c in prepared['cases']))

    def test_approval_and_exact_new_workflow_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'APPROVAL'):
                e.CloseoutClient(Path(tmp)/'out',Path(tmp)/'ledger')
            with patch.dict('os.environ',{},clear=True),self.assertRaisesRegex(ValueError,'AUTHORIZED_WORKFLOW'):
                e.CloseoutClient(Path(tmp)/'out',Path(tmp)/'ledger',approved=True)

    def test_attempt_cap_and_fixed_contract_prevent_repeat_spend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            client=e.CloseoutClient(root/'out',root/'ledger',approved=True,transport=lambda p:httpx.Response(200,json={}))
            payload={'model':e.MODEL,'max_output_tokens':700}
            for _ in range(20):client.post('https://api.openai.com/v1/responses',json=payload)
            with self.assertRaisesRegex(ValueError,'CALL_LIMIT'):client.post('https://api.openai.com/v1/responses',json=payload)
            with self.assertRaises(FileExistsError):e.CloseoutClient(root/'other',root/'ledger',approved=True,transport=lambda p:None)

    def test_budget_constraints_reject_before_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=e.CloseoutClient(Path(tmp)/'out',Path(tmp)/'ledger',approved=True,transport=lambda p:None)
            for payload in ({'model':'other','max_output_tokens':700},
                            {'model':e.MODEL,'max_output_tokens':701},
                            {'model':e.MODEL,'max_output_tokens':700,'input':'x'*16000}):
                with self.assertRaises(ValueError):client.post('https://api.openai.com/v1/responses',json=payload)
            self.assertEqual(client.attempts,0)

    def test_error_is_preserved_without_provider_error_body_and_stops_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            client=e.CloseoutClient(root/'out',root/'ledger',approved=True,transport=lambda p:httpx.Response(500,text='sensitive body'))
            payload={'model':e.MODEL,'max_output_tokens':700}
            client.post('https://api.openai.com/v1/responses',json=payload)
            with self.assertRaisesRegex(ValueError,'BATCH_STOPPED'):client.post('https://api.openai.com/v1/responses',json=payload)
            self.assertEqual(client.attempts,1)
            self.assertNotIn('sensitive',(root/'out/response-01.json').read_text())
