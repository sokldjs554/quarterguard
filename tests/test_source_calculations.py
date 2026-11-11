"""AI-authored calculation tests. Synthetic boundary inputs are not PDF parses."""
import importlib.util
import unittest
from quarterguard.source_evidence import DOCUMENT_ID,load_source

class SourceCalculationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('quarterguard.source_calculations'),'Source calculations not implemented')
        from quarterguard import source_calculations as module
        self.m=module
        self.cells={(c['metric'],c['year']):c for c in load_source()[1]}
    def calc(self,metric='cash',year=2024,base_metric=None,base_year=2023,mode='balance_yoy'):
        return self.m.calculate_source_pair(self.cells[metric,year]['id'],self.cells[base_metric or metric,base_year]['id'],mode)
    def test_cash_balance_change_and_evidence(self):
        r=self.calc()
        self.assertEqual(r['status'],'verified');self.assertEqual(r['difference']['value'],'3617788')
        self.assertEqual(r['growth_pct'],'47.6820');self.assertIsNone(r['share_pct'])
        self.assertEqual(r['normalized_inputs'],['11205117000000','7587329000000'])
        self.assertEqual(r['evidence'][0]['as_of'],'2024-12-31')
        self.assertIsNone(r['evidence'][0]['start']);self.assertTrue(all(c['passed'] for c in r['checks']))
    def test_inventory_and_annual_revenue_are_different_measurement_types(self):
        r=self.calc('inventory');self.assertEqual(r['difference']['value'],'-166722')
        r=self.calc('revenue',mode='annual_yoy');self.assertEqual(r['difference']['value'],'33427241')
        self.assertEqual(r['status'],'verified');self.assertEqual(r['evidence'][0]['period_kind'],'duration')
    def test_negative_base_withholds_percent_but_keeps_valid_difference(self):
        r=self.calc('operating_profit',mode='annual_yoy')
        self.assertEqual(r['issues'],['NEGATIVE_BASE']);self.assertIsNone(r['growth_pct'])
        self.assertEqual(r['status'],'needs_review');self.assertEqual(r['difference']['value'],'31197632')
        self.assertEqual(r['difference_status'],'calculated');self.assertEqual(r['transition'],'loss_to_profit')
    def test_product_share_uses_same_table_total(self):
        r=self.calc('dram',base_metric='product_total',base_year=2024,mode='product_share')
        self.assertEqual(r['share_pct'],'67.5777');self.assertIsNone(r['growth_pct'])
        self.assertIsNone(r['difference']);self.assertEqual(r['status'],'verified')
    def test_wrong_mode_account_year_type_and_denominator_block_all_arithmetic(self):
        requests=[('cash',2023,None,2024,'balance_yoy'),('cash',2024,None,2024,'balance_yoy'),
          ('cash',2024,None,2023,'annual_yoy'),('revenue',2024,None,2023,'balance_yoy'),
          ('cash',2024,'inventory',2023,'balance_yoy'),
          ('dram',2024,'product_total',2023,'product_share'),('dram',2024,'revenue',2024,'product_share'),
          ('product_total',2024,'dram',2024,'product_share')]
        for args in requests:
            with self.subTest(args=args):
                r=self.calc(*args);self.assertEqual(r['status'],'needs_review')
                for key in ('difference','growth_pct','share_pct'):self.assertIsNone(r[key])
    def test_inventory_months_requires_definition(self):
        r=self.calc('inventory',base_metric='revenue',mode='inventory_months')
        self.assertIn('RATIO_DEFINITION_REQUIRED',r['issues']);self.assertIsNone(r['difference'])
        self.assertIsNone(r['growth_pct']);self.assertIsNone(r['share_pct'])
    def test_unknown_id_and_mode_fail(self):
        with self.assertRaisesRegex(ValueError,'UNKNOWN_SOURCE_CELL'):self.m.calculate_source_pair('unknown',self.cells['cash',2023]['id'],'balance_yoy')
        with self.assertRaisesRegex(ValueError,'INVALID_CALCULATION_MODE'):self.calc(mode='invented')
    def test_synthetic_context_and_date_mutations_fail_closed(self):
        a,b=self.cells['revenue',2024],self.cells['revenue',2023]
        for mutation in [{'company':'other'},{'scope':'OFS'},{'currency':'USD'},{'scale':7},
            {'start':'2024-07-01'},{'end':'2024-12-30'},{'start':None},{'value':'NaN'},
            {'document_sha256':'0'*64},{'column':'2023'}]:
            with self.subTest(mutation=mutation):
                r=self.m._calculate_pair(a|mutation,b,'annual_yoy')
                self.assertEqual(r['status'],'needs_review');self.assertIsNone(r['difference']);self.assertIsNone(r['growth_pct'])
    def test_synthetic_zero_base_and_equivalent_scales(self):
        a,b=self.cells['cash',2024],self.cells['cash',2023]
        r=self.m._calculate_pair(a,b|{'value':'0'},'balance_yoy')
        self.assertIn('ZERO_BASE',r['issues']);self.assertEqual(r['difference']['value'],'11205117');self.assertIsNone(r['growth_pct'])
        r=self.m._calculate_pair(a|{'value':'11205117000000','scale':1},b,'balance_yoy')
        self.assertEqual(r['growth_pct'],'47.6820');self.assertEqual(r['difference']['value'],'3617788')
        self.assertEqual((r['difference']['currency'],r['difference']['scale']),('KRW',1000000))
    def test_synthetic_share_invalid_part_and_zero_total(self):
        a,b=self.cells['dram',2024],self.cells['product_total',2024]
        for aa,bb in [(a|{'value':'-1'},b),(a,b|{'value':'0'}),(a|{'value':'999999999'},b),
                       (a,b|{'table_id':'other'}),(a,b|{'row_role':'labelled'})]:
            r=self.m._calculate_pair(aa,bb,'product_share');self.assertIsNone(r['share_pct']);self.assertEqual(r['status'],'needs_review')
