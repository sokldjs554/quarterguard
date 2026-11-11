"""Actual archived SEC HTML and deliberate structure mutations, not numeric fixtures."""
import copy,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from lxml import html
from quarterguard import apple_source as s

class AppleSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=gzip.decompress((s.DATA/'source.html.gz').read_bytes())
    def test_raw_source_reproduces_snapshot(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),s.SHA)
        self.assertEqual(s.extract_html(self.raw),s.load_source()[1])
        cells=s.load_source()[1]['cells'];self.assertEqual(len(cells),25)
        c=next(c for c in cells if c['metric']=='capex_payment' and c['year']==2024)
        self.assertEqual(c['value'],'-9447');self.assertEqual(c['printed_page'],33)
        self.assertEqual(c['start'],'2023-10-01');self.assertEqual(c['fiscal_weeks'],52)
    def mutate(self,fn):
        root=html.fromstring(self.raw);fn(root)
        with self.assertRaises(ValueError):s.extract_html(html.tostring(root))
    def test_duplicate_rows_block(self):
        def change(r):
            t=r.xpath('//table')[22];row=next(x for x in t.xpath('./tr') if x.xpath('./td') and s.norm(x.xpath('./td')[0])=='Products')
            row.addnext(copy.deepcopy(row))
        self.mutate(change)
    def test_year_header_corruption_blocks(self):
        def change(r):
            t=r.xpath('//table')[14];e=next(x for x in t.xpath('.//span') if s.norm(x)=='2024');e.text='2025'
        self.mutate(change)
    def test_company_currency_period_dimension_corruption_blocks(self):
        for tag,old,new in [('xbrli:identifier','0000320193','0000000001'),('xbrli:startdate','2023-10-01','2024-01-01'),('xbrli:measure','iso4217:USD','iso4217:KRW'),('xbrldi:explicitmember','us-gaap:ProductMember','us-gaap:ServiceMember')]:
            def change(r):
                for e in r.iter(tag):
                    if e.text==old:e.text=new
            with self.subTest(tag=tag):self.mutate(change)
    def test_raw_unknown_hash_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.html';p.write_bytes(self.raw+b' ')
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED_HTML_HASH'):s.parse_html(p)
    def test_corrupt_snapshot_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'manifest.json').write_bytes((s.DATA/'manifest.json').read_bytes());(p/'evidence.json').write_text('{}')
            with patch.object(s,'DATA',p),self.assertRaisesRegex(ValueError,'INTEGRITY'):s.load_source()
