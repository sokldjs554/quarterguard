import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from quarterguard import public_providers as pp
from quarterguard.provider_controls import Blocked
from quarterguard.store import load_facts
from quarterguard.core import compare,valid_source
from dataclasses import replace
class ProviderTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.env=patch.dict(os.environ,{'QG_LEDGER_PATH':str(Path(self.tmp.name)/'calls.sqlite3')},clear=True);self.env.start();self.addCleanup(self.env.stop)
 def test_no_key_and_paid_approval_are_fail_closed(self):
  with patch.object(pp,'generate_public') as generate:
   r=pp.execute('openai','qoq-revenue')
   self.assertEqual(r['external_calls_this_request'],0);generate.assert_not_called()
   self.assertIn('PAID_APPROVAL_REQUIRED',r['blocked_reasons'])
 def test_ephemeral_storage_cannot_enable_paid_calls(self):
  with patch.dict(os.environ,{'OPENAI_API_KEY':'TEST-NOT-A-KEY','QG_PAID_APPROVAL':pp.APPROVAL,'QG_LEDGER_DURABLE':'true'}):
   self.assertIn('DURABLE_LEDGER_REQUIRED',pp.reasons('openai'))
 def test_unknown_target_cannot_call(self):
  with patch.object(pp,'fetch') as fetch:
   with self.assertRaises(Blocked):pp.execute('dart','https://other.invalid')
   fetch.assert_not_called()
 def test_dart_success_cache_no_second_network_and_context(self):
  with patch.dict(os.environ,{'DART_API_KEY':'TEST-NOT-A-KEY'}),patch.object(pp,'fetch',return_value=[]) as fetch,patch.object(pp,'check_dart_rows',return_value=[{'passed':True} for _ in range(4)]):
   r=pp.execute('dart','s24q3-CFS');self.assertEqual(r['status'],'succeeded')
   self.assertEqual(r['external_calls_this_request'],1)
   c=pp.execute('dart','s24q3-CFS');self.assertEqual(c['external_calls_this_request'],0)
   self.assertEqual(c['execution'],'cached_provider_response');self.assertEqual(c['created_at'],r['created_at']);self.assertEqual(fetch.call_count,1)
 def test_cache_invalidates_when_verifier_or_evidence_changes(self):
  with patch.dict(os.environ,{'DART_API_KEY':'TEST-NOT-A-KEY'}),patch.object(pp,'fetch',return_value=[]),patch.object(pp,'check_dart_rows',return_value=[{'passed':True} for _ in range(4)]),patch.object(pp,'verification_version',return_value='old'):
   self.assertEqual(pp.execute('dart','s24q3-CFS')['status'],'succeeded')
  with patch.dict(os.environ,{'DART_API_KEY':'TEST-NOT-A-KEY'}),patch.object(pp,'verification_version',return_value='new'),patch.object(pp,'fetch') as fetch:
   with self.assertRaisesRegex(Blocked,'COOLDOWN'):pp.execute('dart','s24q3-CFS')
   fetch.assert_not_called()
 def test_error_never_leaks_secret_and_still_consumes_attempt(self):
  with patch.dict(os.environ,{'DART_API_KEY':'TEST-SECRET'}),patch.object(pp,'fetch',side_effect=RuntimeError('TEST-SECRET url?key=TEST-SECRET')):
   r=pp.execute('dart','s24q3-CFS');self.assertEqual(r['status'],'failed');self.assertNotIn('TEST-SECRET',json.dumps(r))
   self.assertEqual(pp.ledger().usage('dart')['attempts_total'],1)
 def test_payload_cap_precedes_network(self):
  with self.assertRaises(Blocked):pp.build_payload({'x':'a'*13000},'title')
 def test_source_rejects_forged_value_company_and_scale(self):
  fact=load_facts()[0];self.assertTrue(valid_source(fact))
  for field,value in [('value','999'),('company','other'),('scale',1)]:
   self.assertFalse(valid_source(replace(fact,**{field:value})))
if __name__=='__main__':unittest.main()

class GeneratedResponseTests(unittest.TestCase):
 def test_structured_mismatch_is_rejected_and_usage_is_measured(self):
  import httpx
  result={'status':'verified','growth_pct':'1.0000','issues':[],'evidence':[{'id':'fact-1'}]}
  answer={'status':'verified','value':'1.0000','issues':[],'evidence_ids':['fact-1'],'explanation_ko':'공개 수치에 근거한 설명입니다.'}
  def response():
   return httpx.Response(200,json={'status':'completed','model':pp.MODEL,'usage':{'input_tokens':100,'output_tokens':20},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]})
  with patch.dict(os.environ,{'OPENAI_API_KEY':'TEST-NOT-A-KEY'}),patch.object(pp.httpx,'post',side_effect=lambda *a,**k:response()) as post:
   value=pp.generate_public(pp.build_payload(result,'fixed'),result)
   self.assertEqual(value['estimated_cost_usd'],'0.000072')
   self.assertIsNone(value['billed_cost_usd']);self.assertFalse(value['prose_semantics_verified'])
   self.assertEqual(post.call_args.kwargs['json']['max_output_tokens'],700)
   answer['evidence_ids']=['invented']
   with self.assertRaisesRegex(RuntimeError,'OPENAI_RESPONSE_FAILED_OR_REJECTED'):pp.generate_public({},result)
 def test_incomplete_or_timeout_never_returns_unchecked_prose(self):
  import httpx
  with patch.dict(os.environ,{'OPENAI_API_KEY':'TEST-NOT-A-KEY'}):
   for value in [httpx.Response(200,json={'status':'incomplete'}),httpx.ReadTimeout('secret request')]:
    with patch.object(pp.httpx,'post',**({'side_effect':value} if isinstance(value,Exception) else {'return_value':value})):
     with self.assertRaisesRegex(RuntimeError,'^OPENAI_RESPONSE_FAILED_OR_REJECTED$'):pp.generate_public({}, {})
 def test_failed_paid_attempt_is_reserved_and_cooldown_blocks_retry(self):
  from unittest.mock import AsyncMock
  from quarterguard.orchestrator import cases
  expected=next(c for c in cases() if c['id']=='qoq-revenue')
  run={'workflow_success':True,'run_id':'mock-run','trace':[{}], 'result':{'status':expected['expected_status'],'growth_pct':expected['expected_value'],'issues':[],'evidence':expected['expected_evidence']}}
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'QG_LEDGER_PATH':str(Path(tmp)/'db')},clear=True),patch.object(pp,'reasons',return_value=[]),patch.object(pp,'run_case',AsyncMock(return_value=run)),patch.object(pp,'generate_public',side_effect=RuntimeError('provider failed')) as generate:
   value=pp.execute('openai','qoq-revenue')
   self.assertEqual(value['status'],'failed');self.assertEqual(value['external_calls_this_request'],1)
   self.assertEqual(pp.ledger().usage('openai')['attempts_total'],1)
   with self.assertRaisesRegex(Blocked,'COOLDOWN'):pp.execute('openai','qoq-revenue')
   self.assertEqual(generate.call_count,1)
 def test_mcp_gold_mismatch_reserves_no_paid_attempt(self):
  from unittest.mock import AsyncMock
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'QG_LEDGER_PATH':str(Path(tmp)/'db')},clear=True),patch.object(pp,'reasons',return_value=[]),patch.object(pp,'run_case',AsyncMock(return_value={'workflow_success':True,'result':{'status':'fake'}})),patch.object(pp,'generate_public') as generate:
   with self.assertRaisesRegex(Blocked,'MCP_GOLD_MISMATCH'):pp.execute('openai','qoq-revenue')
   self.assertEqual(pp.ledger().usage('openai')['attempts_total'],0);generate.assert_not_called()
