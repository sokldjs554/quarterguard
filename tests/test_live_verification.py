import json
import unittest
from unittest.mock import patch

import httpx

from quarterguard.live_verification import check_explanation, check_dart_rows, generate
from quarterguard.store import load_facts
from quarterguard.dart import fetch


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.result = {'status': 'verified', 'issues': [], 'growth_pct': '6.7916',
                       'evidence': [{'id': 'source-a'}, {'id': 'source-b'}]}
        self.answer = {'status': 'verified', 'issues': [], 'value': '6.7916',
                       'evidence_ids': ['source-a', 'source-b'], 'explanation_ko': '검증된 매출 증가율입니다.'}

    def test_rejects_altered_number_status_and_invented_citation(self):
        self.assertTrue(all(check_explanation(self.answer, self.result).values()))
        for key, value in [('value', '7'), ('status', 'needs_review'),
                           ('evidence_ids', ['invented']), ('issues', ['invented'])]:
            with self.subTest(key=key):
                self.assertFalse(all(check_explanation(self.answer | {key: value}, self.result).values()))

    def test_refusal_cannot_invent_a_value_or_citation(self):
        r = {'status': 'needs_review', 'issues': ['SEARCH_EMPTY'], 'evidence': []}
        a = self.answer | {'status': 'needs_review', 'issues': ['SEARCH_EMPTY'],
                           'value': None, 'evidence_ids': []}
        self.assertTrue(all(check_explanation(a, r).values()))
        self.assertFalse(check_explanation(a | {'value': '0'}, r)['value_exact'])

    def test_provider_errors_never_echo_secret_or_response_body(self):
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'private-test-value'}):
            for response in [httpx.Response(401, text='private-test-value'),
                             httpx.Response(429, text='private-test-value')]:
                with patch('quarterguard.live_verification.httpx.post', return_value=response):
                    with self.assertRaisesRegex(RuntimeError, '^OPENAI_HTTP_[0-9]+$'):
                        generate(self.result, 'test')

    def test_incomplete_output_is_not_a_success(self):
        response = httpx.Response(200, json={'status': 'incomplete', 'output': []})
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'private-test-value'}), \
                patch('quarterguard.live_verification.httpx.post', return_value=response):
            with self.assertRaisesRegex(RuntimeError, '^OPENAI_INCOMPLETE$'):
                generate(self.result, 'test')


class DartCrossCheckTests(unittest.TestCase):
    def test_raw_provider_context_mismatch_is_rejected(self):
        row = {'corp_code': '99999999', 'bsns_year': '2023', 'reprt_code': '11012',
               'sj_div': 'IS', 'account_id': 'ifrs-full_Revenue', 'account_nm': '매출액',
               'currency': 'KRW', 'thstrm_amount': '79098731000000', 'rcept_no': '20241114000001'}
        response = httpx.Response(200, json={'status': '000', 'list': [row]},
                                  request=httpx.Request('GET', 'https://opendart.fss.or.kr'))
        with patch.dict('os.environ', {'DART_API_KEY': 'private-test-value'}), \
                patch('quarterguard.dart.httpx.get', return_value=response):
            with self.assertRaisesRegex(RuntimeError, '^DART_RESPONSE_CONTEXT_MISMATCH$'):
                fetch('00126380', '2024', '11014')

    def setUp(self):
        self.facts = [f for f in load_facts() if f.document_id == 's24q3' and f.scope == 'CFS'
                      and f.start.startswith('2024') and f.currency == 'KRW'
                      and f.metric in ('revenue', 'operating_profit')]
        self.rows = [{'company_code': '00126380', 'year': '2024', 'report_code': '11014',
                      'scope': 'CFS', 'currency': 'KRW',
                      'account_id': 'ifrs-full_Revenue' if f.metric == 'revenue' else 'dart_OperatingIncomeLoss',
                      'period_kind': 'quarter' if f.months == 3 else 'ytd',
                      'source_field': 'thstrm_amount' if f.months == 3 else 'thstrm_add_amount',
                      'amount': str(f.amount),
                      'source_url': 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20241114000001'}
                     for f in self.facts]

    def test_won_conversion_and_period_fields(self):
        self.assertEqual(len(self.facts), 4)
        self.assertTrue(all(c['passed'] for c in check_dart_rows(self.rows, self.facts, '11014')))
        self.rows[0]['amount'] = '1'
        self.assertFalse(check_dart_rows(self.rows, self.facts, '11014')[0]['passed'])

    def test_rejects_missing_duplicate_and_wrong_context(self):
        for rows in [[], self.rows + [self.rows[0]],
                     [r | {'currency': 'USD'} for r in self.rows],
                     [r | {'source_field': 'thstrm_add_amount'} for r in self.rows],
                     [r | {'report_code': '11012'} for r in self.rows]]:
            with self.subTest(rows=len(rows)):
                self.assertFalse(all(c['passed'] for c in check_dart_rows(rows, self.facts, '11014')))
