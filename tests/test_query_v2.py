"""Query safety tests use real retrieval and independently specified fact IDs."""
from dataclasses import replace
import unittest

from quarterguard.search import SearchIndex, chunks
from quarterguard.store import load_facts


class QueryV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = load_facts()
        cls.index = SearchIndex(cls.facts)

    def diagnostic(self, query, index=None):
        index = index or self.index
        self.assertTrue(callable(getattr(index, 'search_with_diagnostics', None)),
                        'Search must distinguish candidates from complete query conditions')
        return index.search_with_diagnostics(query)

    def test_natural_bilingual_queries_keep_every_explicit_constraint(self):
        queries = [
            'Please show Samsung Electronics consolidated revenue for Q3 2024 for three months in millions of Korean won.',
            '삼성전자의 2024년 3분기 연결 매출액을 3개월 기준 백만원 단위로 알려주세요.',
        ]
        for query in queries:
            with self.subTest(query=query):
                hits = self.index.search(query)
                self.assertTrue(hits, 'Natural phrasing must retain the fully specified fact')
                self.assertEqual(hits[0]['fact_ids'], ['s24q3-CFS-revenue-2024-q-KRW'])
                result = self.diagnostic(query)
                self.assertTrue(result['trusted_query'])
                self.assertEqual(result['status'], 'ready')
                self.assertEqual(result['answer_status'], 'not_verified')
                self.assertEqual(result['filters'], dict(company='samsung', metric='revenue',
                    year='2024', quarter=3, kind='quarter', scope='CFS', currency='KRW', scale=1000000))

    def test_missing_unit_is_candidates_only_even_if_unique(self):
        result = self.diagnostic('samsung 2024 Q3 CFS revenue quarter KRW')
        self.assertTrue(result['hits'])
        self.assertFalse(result['trusted_query'])
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertIn('MISSING_SCALE', result['issues'])
        self.assertNotIn('scale', result['filters'])

    def test_natural_omissions_do_not_inherit_currency_kind_or_unit(self):
        result = self.diagnostic('What was Samsung consolidated revenue in the third quarter of 2024?')
        self.assertTrue(result['hits'])
        self.assertEqual(set(result['missing_fields']), {'kind', 'currency', 'scale'})
        self.assertFalse(result['trusted_query'])

    def test_nine_months_explicitly_means_year_to_date_ending_q3(self):
        result = self.diagnostic('Show Samsung separate net income for the first nine months of 2024 in millions of won.')
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['hits'][0]['fact_ids'], ['s24q3-OFS-net_profit-2024-ytd-KRW'])

    def test_unknown_and_negated_terms_never_return_candidates(self):
        base = 'samsung 2024 Q3 CFS revenue quarter KRW scale 1000000'
        for query in [base+' Apple', base+' CHF', base+' crore', base+' not consolidated',
                      base+' excluding revenue', base+' 연결 제외', base+' 별도가 아닌',
                      base.replace('revenue', 'adjusted revenue'), base+' 1999', base+' Q5',
                      base+' €', base+' $', base+' %']:
            with self.subTest(query=query):
                result = self.diagnostic(query)
                self.assertEqual(result['hits'], [])
                self.assertFalse(result['trusted_query'])
                self.assertEqual(result['status'], 'needs_clarification')

    def test_conflicting_conditions_are_never_silently_dropped(self):
        base = 'samsung 2024 Q3 CFS revenue quarter KRW scale 1000000'
        for addition in ['2023', 'Q2', 'OFS', 'USD', 'ytd', 'operating_profit', 'thousands']:
            with self.subTest(addition=addition):
                result = self.diagnostic(base+' '+addition)
                self.assertEqual(result['hits'], [])
                self.assertTrue(any(i.startswith('CONFLICT_') for i in result['issues']))

    def test_explicit_unit_mismatch_is_no_results_not_conversion(self):
        result = self.diagnostic('삼성전자 2024년 3분기 연결 매출 3개월 KRW 억원 단위')
        self.assertEqual(result['filters']['scale'], 100000000)
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['status'], 'no_results')

    def test_registered_issuer_and_configured_alias_do_not_assume_samsung(self):
        fact = replace(self.facts[0], id='other-revenue', company='example_issuer',
                       metric='revenue', start='2026-07-01', end='2026-09-30', scale=1000000,
                       scope='CFS', currency='KRW')
        index = SearchIndex([fact], company_aliases={'example_issuer': ['Example Industries', '예제산업']})
        for name in ['example_issuer', 'Example Industries', '예제산업']:
            result = self.diagnostic(f'{name} 2026 Q3 CFS revenue quarter KRW million', index)
            self.assertEqual(result['hits'][0]['fact_ids'], ['other-revenue'])
            self.assertTrue(result['trusted_query'])
        self.assertEqual(index.search('Samsung 2026 Q3 CFS revenue quarter KRW million'), [])

    def test_fixed_chunk_header_is_derived_from_facts(self):
        fact = replace(self.facts[0], company='example_issuer', start='2026-07-01', end='2026-09-30')
        text = ' '.join(c['text'] for c in chunks([fact], 'fixed'))
        self.assertIn('example_issuer', text)
        self.assertIn('2026', text)
        self.assertNotIn('samsung', text)
        self.assertNotIn('2024', text)

    def test_diagnostic_guardrails_apply_to_every_ranking_configuration(self):
        for config in ['fixed_word', 'cell_word', 'cell_char', 'hybrid_meta']:
            index = SearchIndex(self.facts, config)
            result = self.diagnostic('samsung 2024 Q3 CFS revenue quarter EUR million', index)
            self.assertEqual(result['hits'], [])

    def test_spaced_korean_units_keep_currency_and_scale(self):
        for unit, currency, scale, fact_id in [
            ('백만 원', 'KRW', 1000000, 's24q3-CFS-revenue-2024-q-KRW'),
            ('천 달러', 'USD', 1000, 's24q3-CFS-revenue-2024-q-USD'),
        ]:
            result = self.diagnostic(f'삼성전자 2024년 3분기 연결 매출 3개월 {unit} 단위로 보여줘')
            self.assertEqual(result['status'], 'ready')
            self.assertEqual(result['filters']['currency'], currency)
            self.assertEqual(result['filters']['scale'], scale)
            self.assertEqual(result['hits'][0]['fact_ids'], [fact_id])

    def test_alias_shared_by_registered_issuers_requires_clarification(self):
        a = replace(self.facts[0], company='issuer_a', id='a')
        b = replace(self.facts[0], company='issuer_b', id='b')
        index = SearchIndex([a, b], company_aliases={'issuer_a': ['Shared'], 'issuer_b': ['Shared']})
        result = self.diagnostic('Shared 2024 Q3 CFS revenue quarter KRW million', index)
        self.assertEqual(result['hits'], [])
        self.assertIn('CONFLICT_COMPANY', result['issues'])

    def test_duplicate_matching_facts_are_not_a_unique_ready_result_even_at_k_one(self):
        fact = next(f for f in self.facts if f.id == 's24q3-CFS-revenue-2024-q-KRW')
        index = SearchIndex([fact, replace(fact, id='other-source', value='1')])
        result = index.search_with_diagnostics('Samsung 2024 Q3 CFS revenue quarter KRW million', k=1)
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertIn('AMBIGUOUS_FACT', result['issues'])
        self.assertEqual(result['candidate_fact_count'], 2)

    def test_first_half_korean_period_is_ytd_ending_q2(self):
        result = self.diagnostic('삼성전자 2024년 상반기 연결 매출 백만원')
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['filters']['quarter'], 2)
        self.assertEqual(result['filters']['kind'], 'ytd')
        self.assertEqual(result['hits'][0]['fact_ids'], ['s24q2-CFS-revenue-2024-ytd-KRW'])

    def test_hyundai_aliases_only_resolve_when_issuer_is_registered(self):
        # Post-disclosure development fixture; does not use blind facts or gold.
        base = next(f for f in self.facts if f.id == 's24q3-CFS-revenue-2024-q-KRW')
        index = SearchIndex([replace(base, company='hyundai', id='hyundai-synthetic')])
        for alias in ['Hyundai Motor', 'Hyundai Motor Company', '현대자동차']:
            query = f'{alias} 2024 Q3 CFS revenue quarter KRW million'
            with self.subTest(alias=alias):
                result = self.diagnostic(query, index)
                self.assertEqual(result['status'], 'ready')
                self.assertEqual(result['filters']['company'], 'hyundai')
                self.assertEqual(result['hits'][0]['fact_ids'], ['hyundai-synthetic'])
                self.assertEqual(self.index.search(query), [])


if __name__ == '__main__':
    unittest.main()
