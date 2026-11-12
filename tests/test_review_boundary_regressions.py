"""Known human-reviewed failures + AI-authored boundary tests; no API calls."""
import copy
import json
import os
import unittest
from unittest.mock import patch

import httpx
from jsonschema import Draft202012Validator
from quarterguard import public_providers as pp
from quarterguard.explanation_guards import check_prose, check_grounding
from quarterguard.store import ROOT
from quarterguard.store import load_facts
from quarterguard.core import reconcile


class ReviewBoundaryRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['case_id']: r for r in json.loads(
            (ROOT/'artifacts/model-completion-live-20261112/raw/completion-live/human-review.json').read_text())}

    def test_search_empty_cannot_claim_absence_from_entire_corpus(self):
        for case in ('no-evidence', 'replay-no-evidence'):
            row = self.rows[case]
            self.assertFalse(check_prose(row['raw_generated'], row['tool_result']).get(
                'prose_search_scope_bounded', True))

    def test_empty_search_schema_and_runtime_both_reject_added_claims(self):
        row = self.rows['replay-no-evidence']
        payload = pp.build_payload(row['tool_result'], '검색')
        schema = Draft202012Validator(payload['text']['format']['schema'])
        safe = copy.deepcopy(row['raw_generated'])
        safe['explanation_ko'] = '해당 검색 범위에서 근거를 확인할 수 없습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인하세요.'
        self.assertTrue(schema.is_valid(safe))
        self.assertTrue(all(check_prose(safe, row['tool_result']).values()))
        self.assertTrue(all(check_grounding(safe, row['tool_result']).values()))
        bad = safe | {'explanation_ko': safe['explanation_ko'] + ' 수집된 모든 자료에 없습니다.'}
        self.assertFalse(schema.is_valid(bad))
        self.assertFalse(check_prose(bad, row['tool_result']).get('prose_search_scope_bounded', True))

    def test_provider_withholds_previously_passed_r10_without_rewriting(self):
        row = self.rows['replay-no-evidence']
        original = copy.deepcopy(row)
        response = httpx.Response(200, json={
            'status': 'completed', 'model': pp.MODEL,
            'usage': {'input_tokens': 100, 'output_tokens': 100},
            'output': [{'type': 'message', 'content': [
                {'type': 'output_text', 'text': json.dumps(row['raw_generated'])}]}]})
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-only'}), \
                patch.object(pp.httpx, 'post', return_value=response):
            with self.assertRaises(pp.ExplanationRejected) as caught:
                pp.generate_public({}, row['tool_result'])
        self.assertFalse(caught.exception.checks['prose_search_scope_bounded'])
        self.assertEqual(row, original)

    def test_model_input_omits_independent_predicates_but_review_context_preserves_them(self):
        result = self.rows['ytd-trap']['tool_result']
        original = copy.deepcopy(result)
        data = json.loads(pp.build_payload(result, '기간 비교')['input'])
        basis = data['explanation_context']['decision_basis'][0]
        self.assertNotIn('failed_conditions', basis)
        self.assertNotIn('시작 월', basis['statement'])
        self.assertIn('기간 불일치', basis['statement'])
        self.assertEqual(pp.build_context(result)['decision_basis'][0]['failed_conditions'],
                         ['equal_months', 'yoy_start_month_day'])
        self.assertEqual(result, original)

    def test_model_reported_only_period_explanation_is_accepted_without_diagnostic_copy(self):
        result = self.rows['ytd-trap']['tool_result']
        ctx = json.loads(pp.build_payload(result, '기간 비교')['input'])['explanation_context']
        text = '\n'.join([*(r['required_claim'] for r in ctx['evidence']),
            '도구가 기간 불일치를 보고하여 선택한 방식의 성장률 계산을 보류했습니다. 세부 조건의 실행 순서는 이 결과만으로 확인할 수 없습니다.'])
        self.assertTrue(all(check_grounding({'explanation_ko': text}, result).values()))

    def test_disclosed_diagnostic_attribution_failures_are_rejected(self):
        for case in ('ytd-trap', 'replay-period-mismatch', 'replay-s22-net-period', 'replay-h25-op-period'):
            row = self.rows[case]
            self.assertFalse(check_prose(row['raw_generated'], row['tool_result'])[
                'prose_diagnostic_origin_consistent'], case)

    def test_independent_observation_is_not_a_decision_or_trace(self):
        result = self.rows['ytd-trap']['tool_result']
        safe = ('도구는 기간 불일치를 보고했습니다. '
                '입력을 별도 재계산하면 두 기간의 시작 월·일이 다릅니다. '
                '이 관찰은 도구의 조건 실행 이력이 아닙니다.')
        self.assertTrue(check_prose({'explanation_ko': safe}, result)['prose_diagnostic_origin_consistent'])
        unsafe = safe + ' 독립 재계산이 비교 계산을 보류했습니다.'
        self.assertFalse(check_prose({'explanation_ko': unsafe}, result)['prose_diagnostic_origin_consistent'])

    def test_cross_company_growth_hold_does_not_prohibit_every_comparison(self):
        row = self.rows['replay-cross-company-period']
        self.assertFalse(check_prose(row['raw_generated'], row['tool_result']).get(
            'prose_company_comparison_bounded', True))
        for text in ('이 도구의 같은 회사 성장률 계산은 보류합니다.',
                     '다른 회사의 모든 비교가 불가능하다는 뜻은 아닙니다.',
                     '다른 회사의 모든 비교가 불가능한 것은 아닙니다.'):
            self.assertTrue(check_prose({'explanation_ko': text}, row['tool_result']).get(
                'prose_company_comparison_bounded', False), text)
            self.assertFalse(check_prose({'explanation_ko': text + ' 하지만 직접 비교가 불가능합니다.'},
                                        row['tool_result'])['prose_company_comparison_bounded'])

    def test_growth_hold_note_is_scoped_to_the_selected_operation(self):
        result = self.rows['replay-cross-company-period']['tool_result']
        # No patched fact registry: this check concerns reported issues only.
        context = json.loads(pp.build_payload(result, '전년 비교')['input'])['explanation_context']
        basis = next(x for x in context['decision_basis'] if x['code'] == 'COMPANY_MISMATCH')
        self.assertIn('같은 회사의 성장률', basis['statement'])
        self.assertIn('모든 비교를 금지', basis['statement'])

    def test_reconciliation_hold_is_not_misnamed_as_growth(self):
        facts = {f.id: f for f in load_facts()}
        result = reconcile(facts['s24q3-CFS-revenue-2024-ytd-KRW'],
                           facts['s24q2-CFS-revenue-2024-q-KRW'],
                           facts['s24q3-CFS-revenue-2024-q-KRW'])
        self.assertEqual(result['issues'], ['PERIOD_MISMATCH'])
        self.assertIsNone(result['derived_value'])
        context = json.loads(pp.build_payload(result, '누적 차감 대조')['input'])['explanation_context']
        statement = context['decision_basis'][0]['statement']
        self.assertNotIn('성장률', statement)
        self.assertIn('계산을 보류', statement)
