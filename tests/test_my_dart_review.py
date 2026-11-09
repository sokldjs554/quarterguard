import unittest

from quarterguard.live_verification import check_dart_rows
from quarterguard.store import load_facts


class MyDartReviewTests(unittest.TestCase):
    def setUp(self):
        facts = {fact.id: fact for fact in load_facts()}
        self.fact = facts['s24q3-CFS-revenue-2024-q-KRW']
        # Independent DART fixture: do not derive amount from fact.amount.
        self.row = {
            'company_code': '00126380',
            'year': '2024',
            'report_code': '11014',
            'scope': 'CFS',
            'currency': 'KRW',
            'account_id': 'ifrs-full_Revenue',
            'period_kind': 'quarter',
            'source_field': 'thstrm_amount',
            'amount': '79098731000000',
            'source_url': 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20241114000001',
        }

    def check_one(self, rows):
        checks = check_dart_rows(rows, [self.fact], '11014')
        self.assertEqual(len(checks), 1)
        return checks[0]

    def test_won_conversion_matches_one_candidate(self):
        result = self.check_one([self.row])

        self.assertEqual(result['expected_krw'], '79098731000000')
        self.assertEqual(result['dart_krw'], '79098731000000')
        self.assertEqual(result['candidate_count'], 1)
        self.assertTrue(result['passed'])

    def test_rejects_amount_without_scale(self):
        row = self.row | {'amount': '79098731'}
        result = self.check_one([row])

        self.assertEqual(result['candidate_count'], 1)
        self.assertEqual(result['expected_krw'], '79098731000000')
        self.assertEqual(result['dart_krw'], '79098731')
        self.assertFalse(result['passed'])

    def test_rejects_two_identical_candidate_rows(self):
        duplicate = self.row.copy()  # A different dict, not the same object twice.
        self.assertIsNot(duplicate, self.row)
        result = self.check_one([self.row, duplicate])

        self.assertEqual(result['candidate_count'], 2)
        self.assertFalse(result['passed'])
        self.assertIsNone(result['dart_krw'])
        self.assertIsNone(result['dart_source'])


if __name__ == '__main__':
    unittest.main()
