"""Disclosed paid response replay; no new generation or human verdicts."""
import copy
import json
import unittest
from pathlib import Path
from quarterguard.explanation_guards import check_prose, check_grounding, rates_match_tool
from quarterguard.evaluate_live_explanations_v9 import registry


class CompletionResponseRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        cls.rows={r['case_id']:r for r in json.loads((root/'artifacts/model-completion-live-20261112/raw/completion-live/human-review.json').read_text())}
        cls.cases={c['id']:c for c in json.loads((root/'data/llm-prose-v9-20261111/freeze.json').read_text())['cases']}

    def test_actual_decline_magnitude_is_not_wrong_sign(self):
        for cid in ('h25-op-yoy','h25-net-yoy'):
            row=self.rows['replay-'+cid];before=copy.deepcopy(row)
            with registry(self.cases[cid]):
                self.assertTrue(check_grounding(row['raw_generated'],row['tool_result'])['prose_rates_match_tool'])
            self.assertEqual(row,before)

    def test_wrong_direction_wrong_number_and_bare_positive_rate_still_rejected(self):
        row=self.rows['replay-h25-net-yoy'];original=row['raw_generated']['explanation_ko']
        for changed in (original.replace('20.5146% 감소','20.5146% 증가'),
                        original.replace('20.5146% 감소','20.5146% 변화'),
                        original.replace('20.5146% 감소','21.5146% 감소'),
                        original.replace('20.5146% 감소','-20.5146% 감소')):
            with registry(self.cases['h25-net-yoy']):
                self.assertFalse(check_grounding(row['raw_generated']|{'explanation_ko':changed},row['tool_result'])['prose_rates_match_tool'])

    def test_actual_trace_attribution_is_rejected_even_with_correct_disclaimer(self):
        row=self.rows['ytd-trap'];text=row['raw_generated']['explanation_ko']
        self.assertIn('도구의 조건 실행 이력이 아닙니다',text)
        self.assertFalse(check_prose(row['raw_generated'],row['tool_result'])['prose_diagnostic_origin_consistent'])
        corrected=text.replace('도구 실행 이력에 따르면','입력을 별도 재계산한 진단에 따르면')
        self.assertTrue(check_prose({'explanation_ko':corrected},row['tool_result'])['prose_diagnostic_origin_consistent'])

    def test_quarter_yoy_is_not_annualized_growth(self):
        row=self.rows['replay-s22-op-yoy']
        self.assertFalse(check_prose(row['raw_generated'],row['tool_result'])['prose_growth_kind_consistent'])

    def test_signed_growth_and_explicit_magnitude_are_distinct(self):
        for text in ('증가율은 -20%입니다.', '20% 감소했습니다.', '감소율은 20%입니다.'):
            self.assertTrue(rates_match_tool(text,'-20'),text)
        for text in ('증가율은 20%입니다.', '-20% 감소했습니다.', '감소율은 20% 증가했습니다.'):
            self.assertFalse(rates_match_tool(text,'-20'),text)

    def test_negated_declines_and_explicit_positive_sign_abstain(self):
        for text in ('20% 감소하지 않았습니다.', '20% 감소한 것이 아닙니다.',
                     '감소율은 20%가 아닙니다.', '+20% 감소했습니다.'):
            self.assertFalse(rates_match_tool(text,'-20'),text)

    def test_annualized_negation_does_not_hide_a_separate_positive_claim(self):
        row=self.rows['replay-s22-op-yoy']
        for text in ('CAGR이 아닙니다.', '연평균 성장률이 아닙니다.',
                     '이는 연평균 성장률이나 CAGR이 아니라 전년 동기 대비 증감률입니다.'):
            self.assertTrue(check_prose({'explanation_ko':text},row['tool_result'])['prose_growth_kind_consistent'])
            self.assertFalse(check_prose({'explanation_ko':text+' 그러나 CAGR은 -31.3923%입니다.'},row['tool_result'])['prose_growth_kind_consistent'])
