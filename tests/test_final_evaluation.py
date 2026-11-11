import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from quarterguard import final_evaluation as e
from quarterguard.live_verification import MODEL

class EvaluationBudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def client(self, output='out',transport=None):
        return e.PaidClient(self.root/output,self.root/'ledger',transport=transport or (lambda p:httpx.Response(200,json={})),approved=True)
    def test_approval_required_and_restart_at_different_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'APPROVAL'):
            e.PaidClient(self.root/'no',self.root/'ledger',approved=False)
        self.client()
        with self.assertRaises(FileExistsError):self.client('other')
    def test_bad_model_and_oversize_never_sent(self):
        seen=[]
        client=self.client(transport=lambda payload:seen.append(payload))
        for payload in [{'model':'wrong'}, {'model':MODEL,'max_output_tokens':700,'input':'x'*17000}]:
            with self.assertRaises(ValueError):client.post('https://api.openai.com/v1/responses',json=payload)
        self.assertEqual(seen,[]);self.assertEqual(client.attempts,0)
    def test_failure_reserved_before_call_and_no_retry(self):
        def fail(payload):raise httpx.ReadTimeout('private')
        client=self.client(transport=fail)
        with self.assertRaises(httpx.ReadTimeout):
            client.post('https://api.openai.com/v1/responses',json={'model':MODEL,'max_output_tokens':700})
        self.assertEqual(client.attempts,1)
        self.assertTrue((self.root/'out'/'request-01.json').exists())
    def test_total_attempt_cap(self):
        client=self.client(transport=lambda p:httpx.Response(200,json={'status':'completed'}))
        for _ in range(e.MAX_CALLS):client.post('https://api.openai.com/v1/responses',json={'model':MODEL,'max_output_tokens':700})
        with self.assertRaisesRegex(ValueError,'CALL_LIMIT'):
            client.post('https://api.openai.com/v1/responses',json={'model':MODEL,'max_output_tokens':700})
    def test_planner_rejects_text_or_wrong_model_or_multiple_tools(self):
        for body in [{'model':MODEL,'status':'completed','output':[]}, {'model':'wrong','status':'completed','output':[]}]:
            with self.assertRaises(ValueError):e.parse_action(body)
    def test_production_validator_is_executed_not_reimplemented(self):
        result={'status':'needs_review','issues':['SEARCH_EMPTY'],'evidence':[]}
        client=self.client(transport=lambda p:httpx.Response(200,json={'status':'incomplete'}))
        with patch.dict('os.environ',{'OPENAI_API_KEY':'test-only'}), self.assertRaisesRegex(RuntimeError,'FAILED_OR_REJECTED'):
            e.explain(client,result,'no evidence')
        self.assertEqual(client.attempts,1)

    def test_preflight_blocks_wrong_math_before_spend(self):
        from quarterguard.orchestrator import cases
        from quarterguard.core import compare
        from quarterguard.store import load_facts
        case=next(c for c in cases() if c['id']=='qoq-revenue')
        facts={f.id:f for f in load_facts()}
        result=compare(*(facts[f['id']] for f in case['expected_evidence']),case['mode'])
        self.assertTrue(e.matches_public_preflight(case,result))
        self.assertFalse(e.matches_public_preflight(case,result|{'growth_pct':'999'}))
        self.assertFalse(e.matches_public_preflight(case,result|{'evidence':[]}))
        self.assertFalse(e.matches_public_preflight(case,result|{'status':'needs_review'}))

    def test_real_transport_is_restricted_to_guarded_workflow(self):
        with patch.dict('os.environ',{},clear=True), self.assertRaisesRegex(ValueError,'AUTHORIZED_WORKFLOW'):
            e.PaidClient(self.root/'local-live',self.root/'ledger',approved=True)
