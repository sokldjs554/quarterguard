import unittest

from quarterguard.core import compare
from quarterguard.store import load_facts


class PeriodReviewTests(unittest.TestCase):
    def setUp(self):
        facts = {fact.id: fact for fact in load_facts()}
        self.current = facts['s24q3-CFS-revenue-2024-q-KRW']
        self.base = facts['s24q3-CFS-revenue-2023-q-KRW']

        self.assertEqual(self.current.months, 3)
        self.assertEqual(self.base.months, 3)

    def test_nonadjacent_three_month_periods_block_qoq(self):
        result = compare(self.current, self.base, 'qoq')

        self.assertEqual(result['issues'], ['PERIOD_MISMATCH'])
        self.assertEqual(result['status'], 'needs_review')
        self.assertIsNone(result['growth_pct'])

    def test_same_quarter_previous_year_allows_yoy(self):
        result = compare(self.current, self.base, 'yoy')

        self.assertEqual(result['issues'], [])
        self.assertEqual(result['status'], 'verified')
        self.assertIsNotNone(result['growth_pct'])
        self.assertEqual(result['growth_pct'], '17.3491')


if __name__ == '__main__':
    unittest.main()
