import copy
import json
import unittest
from quarterguard.store import ROOT
from quarterguard.explanation_guards import check_grounding


class ReconciliationCompletionTests(unittest.TestCase):
    def setUp(self):
        records=json.loads((ROOT/'artifacts/closeout-live-20261112/raw/closeout-live/human-review.json').read_text())
        self.row=records[3]

    def test_actual_n04_listing_values_without_conclusion_is_withheld(self):
        checks=check_grounding(self.row['raw_generated'],self.row['tool_result'])
        self.assertFalse(all(checks.values()))
        self.assertFalse(checks.get('prose_reconciliation_conclusion_present',True))

    def test_explicit_positive_conclusion_is_supported_without_changing_tool_result(self):
        result=copy.deepcopy(self.row['tool_result'])
        answer=self.row['raw_generated']|{'explanation_ko':self.row['raw_generated']['explanation_ko']+' 누적 차감 결과가 직접 공시 값과 일치합니다.'}
        self.assertTrue(all(check_grounding(answer,result).values()))
        self.assertEqual(result,self.row['tool_result'])

    def test_negated_or_hypothetical_conclusion_is_not_a_completed_answer(self):
        for phrase in ['누적 차감 결과가 직접 공시 값과 일치하지 않습니다.',
                       '누적 차감 결과가 직접 공시 값과 일치할 수 있습니다.',
                       '누적 차감 결과가 직접 공시 값과 일치합니다라는 주장은 틀렸습니다.']:
            answer=self.row['raw_generated']|{'explanation_ko':self.row['raw_generated']['explanation_ko']+' '+phrase}
            with self.subTest(phrase=phrase):self.assertFalse(all(check_grounding(answer,self.row['tool_result']).values()))
