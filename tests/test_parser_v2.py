"""Small synthetic layouts; official PDF regression is recorded separately."""
import unittest

from quarterguard.ingest import parse_statement


def statement(year=2025, quarter=3, notes='27', values=None):
    month, word = ('June', 'six') if quarter == 2 else ('September', 'nine')
    values = values or '8,000 7,000 6,000 5,000 4,000 3,000 2,000 1,000'
    return f'''INTERIM CONSOLIDATED STATEMENTS OF PROFIT OR LOSS
In millions of Korean won and in thousands of US dollars
For the three-month periods ended {month} 30, For the {word}-month periods ended {month} 30,
Notes {year} {year-1} {year} {year-1} {year} {year-1} {year} {year-1}
KRW KRW USD USD KRW KRW USD USD
Revenue {notes} {values}
Cost of sales'''


def document(**changes):
    return dict(id='opaque-id', url='https://example.org/report.pdf', sha256='a'*64,
                quarter=3, report_end='2025-09-30') | changes


class ParserV2Tests(unittest.TestCase):
    def parse(self, text=None, doc=None):
        return parse_statement(text or statement(), doc or document(), 34, metrics=['revenue'])

    def test_generic_year_comes_from_verified_header(self):
        facts = self.parse()
        self.assertEqual(len(facts), 8)
        self.assertEqual((facts[0].start, facts[0].end, facts[0].value),
                         ('2025-07-01', '2025-09-30', '8000'))
        self.assertEqual((facts[5].start, facts[5].end, facts[5].currency),
                         ('2024-01-01', '2024-09-30', 'KRW'))

    def test_post_disclosure_comma_units_header_preserves_units(self):
        # Added after the first blind evaluation disclosed this punctuation.
        text = statement(year=2023).replace('won and in', 'won, in')
        doc = document(report_end='2023-09-30')
        try:
            facts = self.parse(text, doc)
        except ValueError as error:
            self.fail(f'Unambiguous comma units header rejected: {error}')
        self.assertEqual((facts[0].scale, facts[2].scale), (1000000, 1000))
        self.assertEqual(facts[0].end, '2023-09-30')
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
            self.parse(text.replace('millions of Korean won', 'thousands of Korean won'), doc)

    def test_missing_manifest_date_uses_header_never_document_id(self):
        doc = document(id='s99q1'); doc.pop('report_end')
        self.assertEqual(self.parse(doc=doc)[0].end, '2025-09-30')

    def test_company_is_carried_from_explicit_manifest(self):
        self.assertEqual(self.parse(doc=document(company='example_company'))[0].company,
                         'example_company')

    def test_2026_and_half_year_are_not_hardcoded(self):
        facts = self.parse(statement(year=2026, quarter=2),
                           document(quarter=2, report_end='2026-06-30'))
        self.assertEqual(facts[0].start, '2026-04-01')
        self.assertEqual(facts[4].start, '2026-01-01')

    def test_only_incomplete_comma_group_can_wrap(self):
        text = statement(values='8,000 7,000 6,000 5,000 110,300,26\n5 3,000 2,000 1,000')
        self.assertEqual(self.parse(text)[4].value, '110300265')

    def test_complete_numeric_cells_on_separate_lines_stay_separate(self):
        self.assertEqual(self.parse(statement(values='8,000\n7,000 6,000 5,000 4,000 3,000 2,000 1,000'))[1].value, '7000')

    def test_note_cell_variants(self):
        for note in ['', '7', '18, 19', '18,19', '(18, 19)']:
            with self.subTest(note=note):
                self.assertEqual(self.parse(statement(notes=note))[0].value, '8000')

    def test_parentheses_negatives_and_wrapped_labels(self):
        facts = self.parse(statement(values='(8,000) 7,000 6,000 5,000 4,000 3,000 2,000 1,000'))
        self.assertEqual(facts[0].value, '-8000')
        text = statement().replace('Cost of sales', 'Selling and\nadministrative\nexpenses 18, 19 8,000 7,000 6,000 5,000 4,000 3,000 2,000 1,000')
        facts = parse_statement(text, document(), 34, metrics=['operating_expenses'])
        self.assertEqual(facts[0].row, 'Selling and administrative expenses')

    def test_canonical_metric_cannot_match_modified_row_label(self):
        values = '8,000 7,000 6,000 5,000 4,000 3,000 2,000 1,000'
        for prefix in ['Adjusted ', 'Other ', 'Subtotal ', 'Adjusted\n', 'Adjusted 2 ']:
            for flatten in [False, True]:
                text = statement() + '\n' + prefix + 'Gross profit ' + values
                if flatten:
                    text = ' '.join(text.split())
                with self.subTest(prefix=prefix, flatten=flatten), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                    parse_statement(text, document(), 34, metrics=['gross_profit'])

    def test_canonical_row_after_complete_row_works_when_flattened(self):
        text = statement().replace('Cost of sales', 'Gross profit 8,000 7,000 6,000 5,000 4,000 3,000 2,000 1,000')
        facts = parse_statement(' '.join(text.split()), document(), 34, metrics=['gross_profit'])
        self.assertEqual((facts[0].row, facts[0].value), ('Gross profit', '8000'))

    def test_rejects_conflicting_dates_and_quarter(self):
        for changes in [dict(report_end='2024-09-30'), dict(report_end='2025-09-29'),
                        dict(quarter=2), dict(quarter=1), dict(report_end='invalid')]:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(doc=document(**changes))

    def test_rejects_ambiguous_or_contradictory_headers(self):
        text = statement()
        corruptions = [
            text.replace('2025 2024', '2024 2025', 1),
            text.replace('2025 2024', '2025 2023'),
            text.replace('KRW KRW USD USD', 'USD USD KRW KRW', 1),
            text.replace('millions of Korean won', 'thousands of Korean won'),
            text.replace('For the three-month', 'For the nine-month'),
            text.replace('INTERIM CONSOLIDATED', 'INTERIM SEPARATE INTERIM CONSOLIDATED'),
            text + '\n' + text,
        ]
        for corrupted in corruptions:
            with self.subTest(text=corrupted), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(corrupted)

    def test_rejects_manifest_scope_and_page_conflict(self):
        for changes in [dict(scope='OFS'), dict(statement_pages={'CFS': 35})]:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(doc=document(**changes))

    def test_rejects_duplicate_missing_extra_or_malformed_cells(self):
        text = statement()
        for corrupted in [text + '\nRevenue 27 8,000 7,000 6,000 5,000 4,000 3,000 2,000 1,000',
                          text.replace('1,000', ''), text.replace('1,000', '1,000 9,000'),
                          text.replace('8,000', '8,00'), text.replace('8,000', '(8,000'),
                          text.replace('8,000', '8,00\n12'), text.replace('8,000', '8,00 0'),
                          text.replace('1,000', '1,000x')]:
            with self.subTest(text=corrupted), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_LAYOUT'):
                self.parse(corrupted)


if __name__ == '__main__':
    unittest.main()
