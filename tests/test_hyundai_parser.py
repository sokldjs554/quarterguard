"""Hyundai four-column income statement contracts; no holdout gold imported."""
import json
from pathlib import Path
import unittest

from quarterguard.ingest import parse_statement


ROOT = Path(__file__).resolve().parents[1]


def statement(year=2023, quarter=3):
    month, word = ('June', 'Six') if quarter == 2 else ('September', 'Nine')
    return f'''HYUNDAI MOTOR COMPANY AND ITS SUBSIDIARIES
INTERIM CONSOLIDATED STATEMENTS OF INCOME
FOR THE THREE-MONTH AND {word.upper()}-MONTH PERIODS ENDED {month.upper()} 30, {year} AND {year-1} (Unaudited)
{year} {year-1} NOTES
Three-month period ended {month} 30
{word}-month period ended {month} 30
Three-month period ended {month} 30
{word}-month period ended {month} 30
(In millions of Korean Won, except per share amounts)
Sales 27,40 ￦ 8,000 ￦ 23,000 ￦ 7,000 ￦ 19,000
Cost of sales 32 6,000 17,000 5,000 14,000
Gross profit 2,000 6,000 2,000 5,000
Selling and administrative expenses 28,32 900 2,700 800 2,400
Operating profit 1,100 3,300 1,200 2,600
Income tax expense 34 300 900 400 800
Profit for the period ￦ 800 ￦ 2,400 ￦ 800 ￦ 1,800
Profit attributable to:
Owners of the Company 700 2,000 700 1,500
'''


def document(**changes):
    return dict(id='opaque-id', company='hyundai', quarter=3,
                report_end='2023-09-30', scope='CFS', statement_pages={'CFS': 8},
                pages=68, sha256='a'*64,
                url='https://www.hyundai.com/report.pdf') | changes


class HyundaiParserTests(unittest.TestCase):
    def parse(self, text=None, doc=None, metrics=None):
        return parse_statement(text or statement(), doc or document(), 8,
                               metrics=metrics or ['revenue'])

    def test_maps_year_grouped_columns_and_source_context(self):
        try:
            facts = self.parse()
        except ValueError as exc:
            self.fail(f'Unambiguous Hyundai income statement rejected: {exc}')
        self.assertEqual([(f.value, f.start, f.end, f.column) for f in facts], [
            ('8000', '2023-07-01', '2023-09-30', '2023 Q KRW'),
            ('23000', '2023-01-01', '2023-09-30', '2023 YTD KRW'),
            ('7000', '2022-07-01', '2022-09-30', '2022 Q KRW'),
            ('19000', '2022-01-01', '2022-09-30', '2022 YTD KRW')])
        first = facts[0]
        self.assertEqual((first.company, first.metric, first.row, first.scope,
                          first.currency, first.scale, first.page),
                         ('hyundai', 'revenue', 'Revenue', 'CFS', 'KRW', 1000000, 8))
        self.assertEqual((first.document_id, first.document_sha256, first.source_url),
                         ('opaque-id', 'a'*64, 'https://www.hyundai.com/report.pdf'))
        self.assertEqual((first.translation_basis, first.translation_rate),
                         ('reported_currency', None))

    def test_six_metrics_preserve_values_and_canonical_rows(self):
        try:
            facts = parse_statement(statement(), document(), 8)
        except ValueError as exc:
            self.fail(str(exc))
        self.assertEqual(len(facts), 24)
        self.assertEqual([(f.metric, f.value) for f in facts[::4]], [
            ('revenue', '8000'), ('cost_of_sales', '6000'), ('gross_profit', '2000'),
            ('operating_expenses', '900'), ('operating_profit', '1100'), ('net_profit', '800')])

    def test_half_year_and_generic_year_come_from_explicit_header(self):
        facts = self.parse(statement(year=2026, quarter=2),
                           document(id='h00q3', quarter=2, report_end='2026-06-30'))
        self.assertEqual((facts[0].start, facts[1].start, facts[2].end),
                         ('2026-04-01', '2026-01-01', '2025-06-30'))

    def test_whitespace_wrapping_and_negative_amounts(self):
        text = statement().replace('8,000', '(8,000)', 1).replace('Sales', 'Sales\n')
        self.assertEqual(self.parse(text)[0].value, '-8000')
        self.assertEqual(self.parse(' '.join(text.split()))[0].value, '-8000')

    def test_rejects_manifest_conflicts(self):
        for change in [dict(quarter=2), dict(quarter=1), dict(report_end='2022-09-30'),
                       dict(scope='OFS'), dict(statement_pages={'CFS': 9}),
                       dict(statement_pages={'OFS': 8}), dict(pages=7),
                       dict(company='samsung'), dict(company=None)]:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(doc=document(**change))

    def test_rejects_missing_changed_and_duplicate_header_context(self):
        text = statement()
        changes = [
            text.replace('HYUNDAI MOTOR COMPANY', 'OTHER COMPANY'),
            text.replace('CONSOLIDATED', 'SEPARATE'),
            text.replace('millions', 'thousands'),
            text.replace('Korean Won', 'US dollars'),
            text.replace('2023 2022 NOTES', '2022 2023 NOTES'),
            text.replace('2023 2022 NOTES', '2023 2021 NOTES'),
            text.replace('2023 AND 2022', '2024 AND 2023'),
            text.replace('Three-month period ended September 30', 'Nine-month period ended September 30', 1),
            text.replace('September 30', 'June 30', 1),
            text.replace('NOTES', ''),
            text.replace('(Unaudited)', 'KRW USD'),
            text + '\n' + text,
        ]
        for changed in changes:
            with self.subTest(text=changed), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(changed)

    def test_rejects_missing_extra_malformed_or_mixed_currency_cells(self):
        text = statement()
        for replacement in ['', '￦ 19,000 ￦ 20,000', '￦ 19,00', '￦ (19,000',
                            '￦ 19,000x', '$ 19,000', '￦ -', '￦ 19,00 0']:
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(text.replace('￦ 19,000', replacement))

    def test_rejects_duplicate_or_qualified_rows(self):
        text = statement()
        for changed in [text + '\nSales 27,40 8,000 23,000 7,000 19,000',
                        text.replace('Sales', 'Adjusted Sales'),
                        text.replace('Gross profit', 'Adjusted Gross profit'),
                        text.replace('Gross profit', 'Other 2 Gross profit'),
                        text.replace('Profit for the period', 'Other Profit for the period')]:
            for flat in [changed, ' '.join(changed.split())]:
                with self.subTest(text=flat), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                    self.parse(flat, metrics=['revenue', 'gross_profit', 'net_profit'])

    def test_rejects_ambiguous_note_or_missing_value(self):
        text = statement().replace('27,40 ￦ 8,000 ￦ 23,000 ￦ 7,000 ￦ 19,000',
                                   '27 8,000 23,000 7,000')
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
            self.parse(text)

    def test_note_references_and_bare_amount_rows(self):
        for notes in ['', '27', '27, 40', '(27,40)']:
            text = statement().replace('27,40', notes, 1).replace('￦ ', '')
            self.assertEqual(self.parse(text)[0].value, '8000')

    def test_rejects_unknown_metric(self):
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
            self.parse(metrics=['adjusted_profit'])

    def test_disclosed_dash_in_preceding_row_is_structural_not_a_target_value(self):
        preceding = 'Loss from discontinued operations 8 ￦ - ￦ (319,110) ￦ (38,297) ￦ (262,372)\n'
        text = statement().replace('Profit for the period', preceding + 'Profit for the period')
        try:
            facts = self.parse(text, metrics=['net_profit'])
        except ValueError as exc:
            self.fail(f'Dash in unrelated preceding row must not hide net-profit facts: {exc}')
        self.assertEqual([f.value for f in facts], ['800', '2400', '800', '1800'])
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
            self.parse(text.replace('Profit for the period ￦ 800', 'Profit for the period ￦ -'),
                       metrics=['net_profit'])

    @unittest.skipUnless((ROOT / 'work/v2-blind-raw/h23q3.pdf').exists(), 'official PDF cache unavailable')
    def test_known_official_pdf_matches_all_sixteen_frozen_cells(self):
        from dataclasses import asdict
        from pypdf import PdfReader
        sources = json.loads((ROOT / 'data/v2-blind/sources.json').read_text())
        doc = next(s for s in sources if s['id'] == 'h23q3')
        text = PdfReader(ROOT / 'work/v2-blind-raw/h23q3.pdf').pages[7].extract_text()
        try:
            actual = {f.id: asdict(f) for f in parse_statement(text, doc, 8)}
        except ValueError as exc:
            self.fail(f'Known official PDF still rejected: {exc}')
        gold = [f for f in json.loads((ROOT / 'data/v2-blind/facts.json').read_text())
                if f['document_id'] == doc['id']]
        self.assertEqual(len(actual), 24)
        self.assertEqual(len(gold), 16)
        for expected in gold:
            self.assertEqual(actual[expected['id']], expected)


if __name__ == '__main__':
    unittest.main()
