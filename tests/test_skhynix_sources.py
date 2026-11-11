"""AI-authored development/negative tests; raw text from the official PDF baseline."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / 'artifacts/skhynix-human-20261111/first-baseline'

class SourceParserTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('quarterguard.source_evidence'),
                             'Source-evidence adapter is not implemented')
        from quarterguard import source_evidence
        self.s = source_evidence

    def text(self, page, label):
        return (TEXTS / f'pdf-{page}-{label}.txt').read_text()

    def test_three_tables_values_dates_columns_and_blank_total(self):
        cells = sum((self.s.parse_page(self.text(p,l),p) for p,l in [(191,'F-73'),(193,'F-75'),(264,'F-146')]), [])
        self.assertEqual(len(cells),18)
        by = {(c['metric'],c['year']):c for c in cells}
        cash=by['cash',2024]
        self.assertEqual((cash['value'],cash['period_kind'],cash['as_of']),('11205117','instant','2024-12-31'))
        self.assertIsNone(cash['start']); self.assertIsNone(cash['end'])
        op=by['operating_profit',2023]
        self.assertEqual((op['value'],op['start'],op['end']),('-7730313','2023-01-01','2023-12-31'))
        self.assertEqual((op['row'],op['amount_column'],op['page'],op['printed_page']),('Operating profit (loss)',2,193,'F-75'))
        self.assertEqual(by['operating_profit',2024]['value'],'23467319')
        self.assertEqual(by['product_total',2024]['row'],'')
        self.assertEqual(by['product_total',2024]['row_role'],'total')
        self.assertEqual(by['dram',2024]['table_id'],'note-24-2')
        for c in cells:
            self.assertEqual((c['company'],c['scope'],c['currency'],c['scale']),('skhynix','CFS','KRW',1000000))

    def test_rejects_ambiguous_or_incomplete_table(self):
        raw=self.text(193,'F-75')
        for broken in [raw.replace('Consolidated','Separate'),raw.replace('2024 and 2023','2023 and 2024'),
                       raw.replace('millions of Korean won','thousands of US dollars'),
                       raw.replace('23,467,3 19','23,467 319'),raw.replace('(7,730,313)','-'),
                       raw.replace('Revenue 4,24,31 W 66,192,960 W 32,765,719','Revenue 4,24,31 W 66,192,960 W 32,765,719 99'),
                       raw+'\nRevenue 4,24,31 W 66,192,960 W 32,765,719',
                       raw.replace('SK hynix','Other Corp'),raw.replace('F-75','F-74'),raw.replace('Notes  2024 2023','Notes  2024 2023 2022')]:
            with self.subTest(text=broken[:80]), self.assertRaises(ValueError):self.s.parse_page(broken,193)

    def test_product_subsection_required_and_total_arithmetic_checked(self):
        raw=self.text(264,'F-146')
        for broken in [raw.replace('(2)','(9)'), raw.replace('44,731,664','44,731,665')]:
            with self.assertRaises(ValueError):self.s.parse_page(broken,264)

class SourceSearchTests(unittest.TestCase):
    def setUp(self):
        from quarterguard import source_evidence
        self.s=source_evidence
        self.assertTrue(hasattr(self.s,'search_source'),'Document-scoped retrieval is not implemented')

    def search(self,q):return self.s.search_source(self.s.DOCUMENT_ID,q)

    def pairs(self,r):return {(x['cell']['metric'],x['cell']['year']) for x in r['hits']}

    def test_original_questions_find_required_cells_without_calculating(self):
        import json
        cases=json.loads((ROOT/'data/skhynix-human-20261111/cases.json').read_text())
        expected=[{('cash',2024),('cash',2023)},
            {('inventory',2024),('inventory',2023),('revenue',2024),('revenue',2023)},
            {('dram',2024),('product_total',2024)},
            {('operating_profit',2024),('operating_profit',2023)},
            {('inventory',2024),('revenue',2023),('cost_of_sales',2023)}]
        for c,want in zip(cases,expected):
            with self.subTest(c=c['id']):
                r=self.search(c['question']);self.assertEqual(self.pairs(r),want)
                self.assertIsNone(r['calculated_answer']);self.assertEqual(r['answer_status'],'not_calculated')
                self.assertEqual(r['context']['source'],'selected_document')
        self.assertIn('CURRENT_YEAR_CONFIRMATION',self.search(cases[0]['question'])['issues'])
        self.assertIn('NEGATIVE_BASE_POLICY',self.search(cases[3]['question'])['issues'])
        last=self.search(cases[4]['question'])
        self.assertIn('RATIO_DEFINITION_REQUIRED',last['issues'])
        self.assertEqual([h['cell']['metric'] for h in last['hits'] if h['role']=='related_definition'],['cost_of_sales'])

    def test_conflicting_context_and_unknown_constraints_fail_closed(self):
        for q in ['삼성전자 2024년 매출','SK hynix 2025 revenue',
                  '2024년 별도 매출','2024년 매출 USD million','2024년 매출 억원',
                  '2024년 3분기 매출','2024년 매출 조정','2024년 매출 제외',
                  '2024년 매출 외계조건','2024년 예상 매출','2024년 상반기 매출',
                  '2024년 EBITDA','2024년 평균 재고','2024 cash EUR',
                  '2024 DRAM revenue not NAND']:
            with self.subTest(q=q):
                r=self.search(q);self.assertTrue(r['blocked']);self.assertEqual(r['hits'],[])
        with self.assertRaises(ValueError):self.s.search_source('unknown','2024 매출')

    def test_new_ai_queries_preserve_year_metric_and_table(self):
        r=self.search('SK hynix consolidated 2023 cash in KRW million')
        self.assertEqual(self.pairs(r),{('cash',2023)})
        r=self.search('2023년 NAND 매출')
        self.assertEqual(self.pairs(r),{('nand',2023)})
        r=self.search('2024년 매출원가')
        self.assertEqual(self.pairs(r),{('cost_of_sales',2024)})
        r=self.search('매출')
        self.assertIn('YEAR_REQUIRED',r['issues']);self.assertEqual(len(r['hits']),2)
        self.assertEqual(r['status'],'needs_clarification')

    def test_explicit_dates_and_other_century_years_are_not_dropped(self):
        for q in ['2024-06-30 cash','2024/06/30 cash','1999 cash','2100 cash']:
            r=self.search(q)
            self.assertTrue(r['blocked'],q);self.assertEqual(r['hits'],[],q)

    def test_shared_and_postpositive_years_do_not_misbind(self):
        r=self.search('2024년과 2023년 재고와 매출')
        self.assertEqual(self.pairs(r),{('inventory',2024),('inventory',2023),('revenue',2024),('revenue',2023)})
        r=self.search('재고 2024년 / 매출 2023년')
        self.assertIn('YEAR_BINDING_CONFIRMATION',r['issues'])
        self.assertEqual(r['status'],'needs_clarification')
        self.assertEqual(self.pairs(r),{('inventory',2024),('inventory',2023),('revenue',2024),('revenue',2023)})

    def test_product_keyword_does_not_erase_other_revenue(self):
        r=self.search('2024년 매출과 2023년 DRAM 매출')
        self.assertEqual(self.pairs(r),{('revenue',2024),('dram',2023)})
