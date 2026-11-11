"""Real archived failures plus authored boundaries; no provider calls."""
import copy
import json
import os
import unittest
from unittest.mock import patch
import httpx
from quarterguard.store import ROOT
from quarterguard.explanation_guards import check_prose
from quarterguard.explanation_context import decision_context
from quarterguard import public_providers as pp


class V8ProseRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={r['case_id']:r for r in json.loads(
            (ROOT/'artifacts/llm-prose-v8-20261111/report.json').read_text())['records']}

    def check(self,case,text):
        row=self.rows[case]
        return check_prose(row['generated']|{'explanation_ko':text},row['tool_result'])

    def test_real_reverse_direction_is_rejected_without_changing_response(self):
        row=self.rows['h25-net-yoy'];before=copy.deepcopy(row)
        checks=check_prose(row['generated'],row['tool_result'])
        self.assertFalse(checks.get('prose_comparison_direction_consistent',True))
        self.assertEqual(row,before)

    def test_current_and_base_are_resolved_for_yoy_qoq_and_english(self):
        examples=[
            ('h25-net-yoy','2024년 3분기 대비 2025년 3분기 증감률은 -20.5146%입니다.',True),
            ('h25-net-yoy','2025년 대비 2024년 증감률은 -20.5146%입니다.',False),
            ('normal-qoq','2024년 2분기 대비 2024년 3분기 증가율은 6.7916%입니다.',True),
            ('normal-qoq','3분기 대비 2분기 증가율은 6.7916%입니다.',False),
            ('normal-qoq','2024년 대비 2024년 증가율은 6.7916%입니다.',False),
            ('normal-yoy','From 2023 Q3 to 2024 Q3, growth is 17.3491%.',True),
            ('normal-yoy','From 2024 Q3 to 2023 Q3, growth is 17.3491%.',False),
            ('normal-yoy','Q3 2024 compared with Q3 2023: 17.3491%.',True),
            ('normal-yoy','Q3 2023 compared with Q3 2024: 17.3491%.',False),
            ('normal-yoy','2024년 상반기 대비 2023년 상반기 증가율은 17.3491%입니다.',False),
        ]
        for case,text,expected in examples:
            with self.subTest(text=text):
                self.assertEqual(self.check(case,text).get('prose_comparison_direction_consistent',True),expected)

    def test_correct_direction_cannot_hide_later_reversed_claim(self):
        text='2024년 3분기 대비 2025년 3분기 증감률은 -20.5146%입니다. 2025년 대비 2024년도 -20.5146%입니다.'
        self.assertFalse(self.check('h25-net-yoy',text).get('prose_comparison_direction_consistent',True))

    def test_partial_year_match_does_not_accept_an_unsupported_period_suffix(self):
        for text in ['2024년 대비 2025년 상반기 증감률은 -20.5146%입니다.',
                     '2024년 대비 2025년 9개월 증감률은 -20.5146%입니다.',
                     'From 2024 Q3 to 2025 Q9, change is -20.5146%.']:
            with self.subTest(text=text):
                self.assertFalse(self.check('h25-net-yoy',text)['prose_comparison_direction_consistent'])

    def test_real_evidence_negation_is_allowed_without_mutation(self):
        row=self.rows['s22-net-period'];before=copy.deepcopy(row)
        self.assertTrue(check_prose(row['generated'],row['tool_result'])['prose_evidence_presence_consistent'])
        self.assertEqual(row,before)

    def test_negation_does_not_hide_contradiction_or_uncertainty(self):
        good='근거가 없는 것이 아니라, 기간이 다릅니다.'
        self.assertTrue(self.check('s22-net-period',good)['prose_evidence_presence_consistent'])
        for text in [good+' 하지만 근거가 없습니다.',
                     '근거가 없는 것이 아니라는 뜻은 아닙니다.',
                     '근거가 없는 것이 아닐 수도 있습니다.',
                     '근거가 없는 것이 아니라는 주장은 확인하지 못했습니다.']:
            with self.subTest(text=text):
                self.assertFalse(self.check('s22-net-period',text)['prose_evidence_presence_consistent'])

    def test_internal_issue_and_diagnostic_labels_are_not_prose(self):
        for code in ['COMPANY_MISMATCH','PERIOD_MISMATCH','SCOPE_MISMATCH',
                     'equal_months','yoy_year','yoy_start_month_day','UNKNOWN_UNIT']:
            with self.subTest(code=code):
                self.assertFalse(self.check('cross-company-period',code+'입니다.')['prose_review_language_localized'])
        self.assertTrue(self.check('normal-qoq','KRW는 통화이고 백만 원은 표시 단위입니다.')['prose_review_language_localized'])
        context=decision_context({'issues':['COMPANY_MISMATCH','UNSUPPORTED_NEW_CONDITION']})
        self.assertEqual([x['code'] for x in context['decision_basis']],['COMPANY_MISMATCH','UNSUPPORTED_NEW_CONDITION'])
        for row in context['decision_basis']:
            self.assertNotIn(row['code'],row['statement'])

    def test_provider_rejects_reversed_sentence_even_when_structure_matches(self):
        row=self.rows['h25-net-yoy']
        response=httpx.Response(200,json={'status':'completed','model':pp.MODEL,
            'usage':{'input_tokens':100,'output_tokens':100},
            'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(row['generated'])}]}]})
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}),patch.object(pp.httpx,'post',return_value=response):
            with self.assertRaises(pp.ExplanationRejected) as error:
                pp.generate_public({},row['tool_result'])
        self.assertTrue(error.exception.checks['value_exact'])
        self.assertTrue(error.exception.checks['citations_exact'])
        self.assertFalse(error.exception.checks['prose_comparison_direction_consistent'])
