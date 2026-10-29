import unittest
from dataclasses import replace
from quarterguard.core import Fact, compare, reconcile, select_unique
from quarterguard.ingest import parse_statement

def fact(**kw):
    base=dict(id='a',company='samsung',metric='revenue',scope='CFS',currency='KRW',scale=1000000,
      start='2024-07-01',end='2024-09-30',value='79098731',source_url='https://example.org/report.pdf',
      page=34,row='Revenue',column='2024 Q3 KRW',document_id='s24q3',document_sha256='a'*64)
    return Fact(**(base|kw))

class VerificationTests(unittest.TestCase):
    def test_qoq_decimal(self):
        r=compare(fact(),fact(id='b',start='2024-04-01',end='2024-06-30',value='74068302'),'qoq')
        self.assertEqual(r['status'],'verified'); self.assertEqual(r['growth_pct'],'6.7916')
    def test_context_mismatches(self):
        for field,v,code in [('company','other','COMPANY_MISMATCH'),('scope','OFS','SCOPE_MISMATCH'),('metric','net_profit','METRIC_MISMATCH'),('currency','USD','CURRENCY_MISMATCH')]:
            with self.subTest(field=field):
                r=compare(fact(),fact(id='b',**{field:v}),'yoy')
                self.assertIn(code,r['issues']); self.assertIsNone(r['growth_pct'])
    def test_cumulative_not_quarter(self):
        r=compare(fact(start='2024-01-01'),fact(id='b',start='2023-07-01',end='2023-09-30'),'yoy')
        self.assertIn('PERIOD_MISMATCH',r['issues'])
    def test_nonadjacent_qoq(self):
        self.assertIn('PERIOD_MISMATCH',compare(fact(),fact(start='2023-07-01',end='2023-09-30'),'qoq')['issues'])
    def test_scale_conversion(self):
        r=compare(fact(),fact(id='b',start='2024-04-01',end='2024-06-30',value='74068302000',scale=1000),'qoq')
        self.assertEqual(r['growth_pct'],'6.7916')
    def test_unknown_scale(self):
        self.assertIn('UNKNOWN_UNIT',compare(fact(scale=7),fact(),'yoy')['issues'])
    def test_zero_denominator(self):
        r=compare(fact(),fact(id='b',start='2024-04-01',end='2024-06-30',value='0'),'qoq')
        self.assertIn('ZERO_BASE',r['issues']); self.assertIsNone(r['growth_pct'])
    def test_negative_base_not_growth(self):
        r=compare(fact(),fact(id='b',start='2024-04-01',end='2024-06-30',value='-2'),'qoq')
        self.assertIn('NEGATIVE_BASE',r['issues']); self.assertIsNone(r['growth_pct'])
    def test_missing_source(self):
        self.assertIn('MISSING_SOURCE',compare(fact(source_url=''),fact(),'yoy')['issues'])
    def test_reconcile_independent_report(self):
        r=reconcile(fact(id='ytd',start='2024-01-01',value='225082634'),fact(id='h1',start='2024-01-01',end='2024-06-30',value='145983903'),fact())
        self.assertEqual(r['status'],'verified'); self.assertEqual(r['derived_value'],'79098731'); self.assertEqual(r['difference'],'0')
    def test_reconcile_conflict(self):
        r=reconcile(fact(start='2024-01-01',value='225082635'),fact(start='2024-01-01',end='2024-06-30',value='145983903'),fact())
        self.assertIn('NUMERIC_CONFLICT',r['issues'])
    def test_reconcile_start_mismatch(self):
        r=reconcile(fact(start='2024-01-01'),fact(start='2024-04-01',end='2024-06-30'),fact())
        self.assertIn('PERIOD_MISMATCH',r['issues'])
    def test_ambiguous_conflicting_fact(self):
        with self.assertRaisesRegex(ValueError,'AMBIGUOUS_FACT'):
            select_unique([fact(),fact(id='b',value='1')],company='samsung',metric='revenue')
    def test_empty_search(self):
        with self.assertRaisesRegex(ValueError,'NOT_FOUND'): select_unique([],company='other')
    def test_nonfinite(self):
        with self.assertRaises(ValueError): fact(value='NaN')

class ParserTests(unittest.TestCase):
    def test_missing_header_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_LAYOUT'):
            parse_statement('Revenue 1 2 3 4 5 6 7 8',{},1)
    def test_layout_context(self):
        text='''INTERIM CONSOLIDATED STATEMENTS OF PROFIT OR LOSS
        In millions of Korean won and in thousands of US dollars
        For the three-month periods ended September 30, For the nine-month periods ended September 30,
        Notes 2024 2023 2024 2023 2024 2023 2024 2023
        KRW KRW USD USD KRW KRW USD USD
        Revenue 26 79,098,731 67,404,652 58,487,296 49,840,444 225,082,634 191,155,556 166,430,921 141,344,513
        Cost of sales'''
        fs=parse_statement(text,{'id':'s24q3','url':'https://example.org/doc.pdf','sha256':'a'*64,'quarter':3},34,metrics=['revenue'])
        self.assertEqual(len(fs),8)
        self.assertEqual(fs[0].value,'79098731'); self.assertEqual(fs[4].start,'2024-01-01')
        self.assertEqual(fs[2].currency,'USD'); self.assertEqual(fs[2].scale,1000)
        self.assertEqual(fs[0].page,34)

if __name__=='__main__': unittest.main()
