import json
import unittest
from pathlib import Path
from quarterguard.explanation_guards import check_prose

class MixedAmountProseTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.rows=json.loads((root/'artifacts/final-live-20261111/run/report.json').read_text())['explanations']
    def test_two_actual_mixed_scale_responses_are_withheld(self):
        for row in self.rows[:2]:
            self.assertFalse(check_prose(row['output']['generated'],row['mcp']['result'])['prose_million_amount_unambiguous'],row['case_id'])
    def test_supported_plain_million_notation_is_not_blocked(self):
        row=self.rows[0]
        self.assertTrue(all(check_prose({'explanation_ko':'연결 매출은 79,098,731백만 원이며 전분기는 74,068,302백만 원입니다. 증감률은 6.7916%입니다.'},row['mcp']['result']).values()))
    def test_separate_explicit_conversion_is_not_confused_with_mixed_scale(self):
        row=self.rows[0]
        self.assertTrue(check_prose({'explanation_ko':'1조 원은 1,000,000백만 원입니다.'},row['mcp']['result'])['prose_million_amount_unambiguous'])
    def test_actual_reconciliation_still_passes(self):
        row=self.rows[3]
        self.assertTrue(all(check_prose(row['output']['generated'],row['mcp']['result']).values()))
