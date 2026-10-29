import unittest,asyncio
from dataclasses import replace
from unittest.mock import AsyncMock,patch
from quarterguard.store import load_facts
from quarterguard.core import compare,reconcile
from quarterguard.search import SearchIndex
from quarterguard.ingest import parse_statement
from quarterguard.evaluate import evaluate_cases
class ReviewRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.f={f.id:f for f in load_facts()};cls.index=SearchIndex(list(cls.f.values()))
 def test_usd_convenience_translation_block(self):
  a=self.f['s24q3-CFS-revenue-2024-q-USD'];b=self.f['s24q2-CFS-revenue-2024-q-USD']
  self.assertIn('CONVENIENCE_TRANSLATION',compare(a,b)['issues'])
 def test_unknown_or_conflicting_search(self):
  for q in ['samsung Apple 2024 Q3 CFS revenue quarter KRW','samsung 2024 Q3 CFS revenue quarter CHF','삼성전자 2024년 1분기 연결 매출액 3개월 KRW','SK hynix 2024 Q3 CFS revenue quarter KRW','samsung 2024 Q3 CFS revenue quarter ytd KRW','samsung 2024 Q1 CFS revenue quarter KRW','samsung 2024 Q4 CFS revenue quarter KRW','samsung 2024 Q3 CFS revenue quarter EUR','samsung 2024 Q3 CFS OFS revenue quarter KRW','samsung 2023 2024 Q3 CFS revenue quarter KRW']:
   with self.subTest(query=q):self.assertEqual(self.index.search(q),[])
 def test_korean_year_suffix(self):
  hits=self.index.search('삼성전자 2023년 3분기 연결 매출액 3개월 KRW')
  self.assertEqual(hits[0]['fact_ids'],['s24q3-CFS-revenue-2023-q-KRW'])
 def test_forged_citation(self):
  a=self.f['s24q3-CFS-revenue-2024-q-KRW'];b=self.f['s24q2-CFS-revenue-2024-q-KRW']
  for attrs in [dict(source_url='https://made-up.example/report'),dict(page=99999),dict(row='Wrong'),dict(column='Wrong'),dict(document_sha256='z'*64)]:
   with self.subTest(attrs=attrs):self.assertIn('SOURCE_MISMATCH',compare(replace(a,**attrs),b)['issues'])
 def test_bad_header_order_and_date(self):
  prefix='INTERIM CONSOLIDATED STATEMENTS OF PROFIT OR LOSS In millions of Korean won and in thousands of US dollars '
  suffix=' Notes 2024 2023 2024 2023 2024 2023 2024 2023 KRW KRW USD USD KRW KRW USD USD Revenue 26 225,082,634 191,155,556 166,430,921 141,344,513 79,098,731 67,404,652 58,487,296 49,840,444 Cost of sales'
  for hdr in ['For the nine-month periods ended September 30, For the three-month periods ended September 30,','For the three-month periods ended October 31, For the nine-month periods ended October 31,']:
   with self.subTest(header=hdr):
    with self.assertRaisesRegex(ValueError,'UNSUPPORTED_LAYOUT'):parse_statement(prefix+hdr+suffix,{'id':'s24q3','quarter':3,'url':'https://example.org','sha256':'a'*64,'report_end':'2024-09-30'},34,metrics=['revenue'])
 def test_all_mcp_failures_remain_reportable(self):
  failed={'case_id':'x','execution_mode':'live_mcp','result':{'status':'needs_review','issues':['TOOL_ERROR'],'evidence':[]},'trace':[],'latency_ms':1}
  with patch('quarterguard.evaluate.run_case',new=AsyncMock(return_value=failed)),patch('pathlib.Path.write_text'):
   report=asyncio.run(evaluate_cases())
  self.assertEqual(report['workflow_success_rate'],0);self.assertEqual(report['case_accuracy'],0);self.assertIsNone(report['tool_success_rate'])
