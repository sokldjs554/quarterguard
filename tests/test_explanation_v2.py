import copy,json,unittest
from quarterguard.store import ROOT
from quarterguard.explanation_audit import audit_explanation

class ExplanationAuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=json.loads((ROOT/'artifacts/live-openai.json').read_text())['openai']['records']
 def run_text(self,text,index=0):
  row=self.rows[index];a=copy.deepcopy(row['generated']);a['explanation_ko']=text
  return audit_explanation(a,row['mcp_run']['result'],context_years=['2025'] if index==2 else [])
 def test_recorded_numeric_statement_is_not_semantic_certification(self):
  r=self.run_text(self.rows[0]['generated']['explanation_ko'])
  self.assertEqual(r['automatic_verdict'],'no_detected_rule_violation');self.assertFalse(r['semantic_verified']);self.assertTrue(r['human_review_required'])
 def test_wrong_percentage_is_flagged(self):
  self.assertIn('PERCENT_MISMATCH',self.run_text('2024년 3분기 연결 매출은 9.9999% 증가했습니다.')['issues'])
 def test_wrong_scope_and_period_and_unit_are_flagged(self):
  for text,issue in [('별도 매출 증가율은 6.7916%입니다.','SCOPE_CLAIM_CONFLICT'),('2026년 연결 매출 증가율입니다.','YEAR_CLAIM_CONFLICT'),('12개월 누적 매출입니다.','MONTHS_CLAIM_CONFLICT'),('금액 단위는 천 원입니다.','UNIT_CLAIM_CONFLICT')]:
   with self.subTest(text=text):self.assertIn(issue,self.run_text(text)['issues'])
 def test_correct_scaled_amount_and_wrong_amount(self):
  self.assertNotIn('AMOUNT_MISMATCH',self.run_text('2024년 3분기 연결 매출은 79,098,731 백만 원입니다.')['issues'])
  self.assertIn('AMOUNT_MISMATCH',self.run_text('2024년 3분기 연결 매출은 79,098,732 백만 원입니다.')['issues'])
 def test_recorded_ambiguous_individual_term_is_review(self):
  row=self.rows[3];r=audit_explanation(row['generated'],row['mcp_run']['result'])
  self.assertIn('AMBIGUOUS_SCOPE_TERM',r['issues']);self.assertTrue(r['human_review_required'])
 def test_amount_from_wrong_period_is_not_validated_by_membership(self):
  self.assertIn('AMOUNT_CONTEXT_MISMATCH',self.run_text('2024년 3분기 연결 매출은 74,068,302 백만 원입니다.')['issues'])
 def test_period_binding_respects_supported_spelling_variants(self):
  for quarter in ['3 분기','Q3']:
   with self.subTest(quarter=quarter):
    self.assertIn('AMOUNT_CONTEXT_MISMATCH',self.run_text(f'2024년 {quarter} 연결 매출은 74,068,302 백만 원입니다.')['issues'])
 def test_months_binding_respects_whitespace(self):
  self.assertIn('AMOUNT_CONTEXT_MISMATCH',self.run_text('3 개월 연결 매출은 225082634 백만 원입니다.',1)['issues'])
 def test_english_scope_binds_amount_in_mixed_scope_result(self):
  result=json.loads((ROOT/'artifacts/prepared.json').read_text())['scope-trap']['result']
  other=next(f for f in result['evidence'] if f['scope']=='OFS')
  answer={'status':result['status'],'value':None,'issues':result['issues'],'evidence_ids':[f['id'] for f in result['evidence']],'explanation_ko':f"consolidated 매출은 {other['value']} 백만 원입니다."}
  self.assertIn('AMOUNT_CONTEXT_MISMATCH',audit_explanation(answer,result)['issues'])
 def test_currency_without_number_is_checked(self):
  self.assertIn('CURRENCY_CLAIM_CONFLICT',self.run_text('금액은 USD 단위입니다.')['issues'])
 def test_insufficient_evidence_cannot_support_amount(self):
  self.assertIn('UNSUPPORTED_NUMERIC_CLAIM',self.run_text('2025년 매출은 100 백만 원입니다.',2)['issues'])
 def test_citation_tamper_and_page_are_checked(self):
  row=copy.deepcopy(self.rows[0]);row['generated']['evidence_ids']=['invented']
  r=audit_explanation(row['generated'],row['mcp_run']['result']);self.assertFalse(r['structured_checks']['citations_exact'])
  row=copy.deepcopy(self.rows[0]);row['mcp_run']['result']['evidence'][0]['page']=999
  r=audit_explanation(row['generated'],row['mcp_run']['result']);self.assertFalse(r['canonical_evidence_valid'])
 def test_unlisted_inline_citation_is_rejected(self):
  self.assertIn('INLINE_CITATION_MISMATCH',self.run_text('출처 https://example.org/fake.pdf#page=4 입니다.')['issues'])
 def test_negation_and_unbound_numbers_require_human(self):
  self.assertIn('NEGATION_REQUIRES_REVIEW',self.run_text('별도가 아닌 연결 매출입니다.')['issues'])
  self.assertIn('UNBOUND_NUMBER_REQUIRES_REVIEW',self.run_text('매출은 79098731입니다.')['issues'])
 def test_rejected_result_not_announced_as_verified(self):
  self.assertIn('REJECTION_OVERRIDDEN_IN_PROSE',self.run_text('검증 통과, 문제가 없습니다.',1)['issues'])
