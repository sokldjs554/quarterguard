"""User seven cases are development inputs; adversarial variations are AI authored."""
import json
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from quarterguard.api import app

DOC='apple-2024-10k'
class AppleReviewTests(unittest.TestCase):
    def setUp(self):self.client=TestClient(app)
    def review(self,q):
        r=self.client.post('/api/source-review',json={'document_id':DOC,'query':q})
        self.assertEqual(r.status_code,200,r.text)
        return r.json()
    def test_catalog_and_original_seven(self):
        self.assertIn(DOC,[x['id'] for x in self.client.get('/api/source-documents').json()])
        cases=json.loads(Path('data/apple-submitted-20261112/submission.json').read_text())['cases']
        for i,c in enumerate(cases):
            with self.subTest(c['id']):
                r=self.review(c['question'])
                self.assertEqual(r['status'],'verified' if i<5 else 'needs_review')
                self.assertGreater(len(r['evidence']),0)
                self.assertEqual(r['execution'],'deterministic_source_review')
                self.assertEqual(r['currency'],'USD')
                self.assertEqual(r['scale'],1000000)
        q=[c['question'] for c in cases]
        r=self.review(q[0]);self.assertEqual(r['values']['services_margin_pct'],'73.8804');self.assertEqual(r['values']['products_margin_pct'],'37.1806')
        r=self.review(q[1]);self.assertEqual(r['values'],{'china_difference':'-5607','total_difference':'7750'});self.assertIn('52',str(r['warnings']))
        self.assertEqual(self.review(q[2])['values']['operating_cash_less_capex'],'108807')
        r=self.review(q[3]);self.assertEqual(r['values']['spending_increase'],'17399');self.assertEqual(r['values']['signed_cash_flow_change'],'-17399')
        self.assertEqual(self.review(q[4])['values']['tax_expense_change'],'13008')
    def test_search_candidates_and_canonical_source(self):
        r=self.client.get('/api/source-search',params={'document_id':DOC,'q':'2024 제품 서비스 매출총이익률'}).json()
        self.assertEqual(r.get('answer_status'),'not_calculated')
        self.assertIsNone(r['calculated_answer']);self.assertEqual(len(r['hits']),4)
        for h in r['hits']:
            c=h['cell'];self.assertEqual(self.client.get('/api/source-cells/'+c['id']).json(),c)
            self.assertEqual(c['source_format'],'SEC_HTML');self.assertIsNone(c['page'])
            self.assertEqual(c['printed_page'],29)
    def test_unsupported_conditions_never_use_previous_answer(self):
        self.review('2024 제품 서비스 매출총이익률')
        for q in ['2025 제품 서비스 매출총이익률','2024 제품 서비스 매출총이익률 KRW','2024 제품 서비스 매출총이익률 별도','2024 제품 서비스 매출총이익률 분기','2024 제품 서비스 매출총이익률 조정','2024 제품 서비스 매출총이익률 제외','2024 제품 서비스 매출총이익률 10% 환율 가정','2024 제품 서비스 매출총이익률 삼성전자','2024 제품 서비스 매출총이익률 1월부터 12월','2024 제품 서비스 매출총이익률 아님']:
            with self.subTest(q=q):
                r=self.review(q);self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{});self.assertTrue(r['issues'])
    def test_english_and_missing_year(self):
        r=self.review('2024 products services gross margin');self.assertEqual(r['values']['services_margin_pct'],'73.8804')
        r=self.review('products services gross margin');self.assertEqual(r['values'],{});self.assertIn('YEAR_REQUIRED',r['issues'])
    def test_supported_document_default_is_explicit(self):
        r=self.review('중국권 매출이 줄었는데도 전체 매출은 늘었나?')
        self.assertEqual(r['context']['years_origin'],'selected_document_comparative_columns')
        self.assertEqual(r['context']['current_year'],2024);self.assertEqual(r['context']['base_year'],2023)
    def test_bad_request_contract(self):
        self.assertEqual(self.client.post('/api/source-review',json={'document_id':DOC,'query':'x','amount':'10'}).status_code,422)
        self.assertEqual(self.client.post('/api/source-review',json={'document_id':DOC,'query':'x'*501}).status_code,422)
        self.assertEqual(self.client.post('/api/source-review',json={'document_id':'fake','query':'2024 매출'}).status_code,404)

    def test_reversed_years_are_not_answered_in_opposite_direction(self):
        for q in ['2023년 자사주 매입에 쓴 현금은 2024년보다 얼마나 늘었나?', '2023 buyback spending increase versus 2024']:
            r=self.review(q);self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{})
    def test_reversed_subtraction_does_not_reverse_user_operands(self):
        for q in ['2024 capex minus operating cash flow','2024 subtract operating cash flow from capex']:
            r=self.review(q);self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{})
    def test_other_operation_qualifiers_and_multiple_intents_block(self):
        for q in ['2024 제품 서비스 매출총이익률 공통비 차감','2024 products services gross margin less tax','2024 products services gross margin and operating cash flow minus capex']:
            r=self.review(q);self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{})
    def test_snapshot_failure_then_recovery(self):
        from unittest.mock import patch
        with patch('quarterguard.apple_source.load_source',side_effect=ValueError('SOURCE_EVIDENCE_INTEGRITY')):
            r=self.client.post('/api/source-review',json={'document_id':DOC,'query':'2024 products services gross margin'})
            self.assertEqual(r.status_code,503);self.assertNotIn('values',r.json())
        self.assertEqual(self.review('2024 products services gross margin')['status'],'verified')
    def test_zero_sales_and_corrupt_period_withhold_calculation(self):
        import copy
        from unittest.mock import patch
        from quarterguard.apple_source import load_source
        manifest,e=load_source()
        for field,value in [('value','0'),('currency','KRW'),('start','2024-01-01')]:
            changed=copy.deepcopy(e)
            next(c for c in changed['cells'] if c['metric']=='products_sales' and c['year']==2024)[field]=value
            with patch('quarterguard.apple_source.load_source',return_value=(manifest,changed)):
                r=self.review('2024 products services gross margin');self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{})
    def test_supported_english_operations_keep_order_and_reject_extra_subtraction(self):
        r=self.review('2024 operating cash flow minus capex');self.assertEqual(r['values']['operating_cash_less_capex'],'108807')
        r=self.review('2024 buyback spending increase');self.assertEqual(r['values']['spending_increase'],'17399')
        for q in ['2024 operating cash flow minus capex minus capex','2024 제품 서비스 매출총이익률 증가']:
            r=self.review(q);self.assertEqual(r['status'],'needs_review');self.assertEqual(r['values'],{})
