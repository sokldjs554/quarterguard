"""Offline development regressions; no real provider calls or human labels."""
import copy
import json
import os
import unittest
from unittest.mock import patch

import httpx
from quarterguard import public_providers as pp
from quarterguard.store import ROOT


class ExplanationContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['case_id']: r for r in json.loads(
            (ROOT / 'artifacts/llm-live-20261109/report.json').read_text())['records']}

    def context(self, result):
        data = json.loads(pp.build_payload(result, '검토')['input'])
        self.assertIn('explanation_context', data)
        return data['explanation_context']

    def test_units_and_locators_come_from_source_not_generated_text(self):
        result = copy.deepcopy(self.rows['normal-qoq']['tool_result'])
        ctx = self.context(result)
        a, b = ctx['evidence']
        self.assertEqual(a['display_unit'], '백만 원')
        self.assertEqual(a['currency'], 'KRW')
        self.assertEqual(a['value'], '79098731')
        self.assertEqual(a['page'], 34)
        self.assertEqual(b['page'], 48)
        self.assertEqual(a['row'], 'Revenue')
        self.assertEqual(a['column'], '2024 Q KRW')
        self.assertEqual(a['source_href'].split('#')[-1], 'page=34')
        self.assertIn('2024 3Q', a['document_title'])
        self.assertIn('백만 원', a['statement'])
        self.assertIn('PDF p.34', a['statement'])
        self.assertEqual(result, self.rows['normal-qoq']['tool_result'])

    def test_empty_search_is_scoped_and_does_not_invent_citation(self):
        ctx = self.context(self.rows['no-evidence']['tool_result'])
        self.assertEqual(ctx['status'], 'no_evidence')
        self.assertEqual(ctx['evidence'], [])
        self.assertIn('해당 검색 범위', ctx['notice'])
        self.assertIn('실적 자체가 없다는 뜻은 아닙니다', ctx['notice'])

    def test_period_and_scope_rejections_remain_visible(self):
        for case, issue in [('period-mismatch', 'PERIOD_MISMATCH'), ('scope-mismatch', 'SCOPE_MISMATCH')]:
            result = self.rows[case]['tool_result']
            ctx = self.context(result)
            self.assertEqual(ctx['comparison_status'], 'needs_review')
            self.assertIn(issue, ctx['issues'])
            self.assertIn('계산 보류', ctx['notice'])
        ctx = self.context(self.rows['scope-mismatch']['tool_result'])
        self.assertEqual([x['scope'] for x in ctx['evidence']], ['CFS', 'OFS'])

    def test_forged_page_currency_scale_and_unknown_fact_withhold_all_citations(self):
        for key, val in [('page', 99), ('currency', 'USD'), ('scale', 1000), ('value', '1'),
                         ('id', 'invented'), ('source_url', 'javascript:alert(1)')]:
            result = copy.deepcopy(self.rows['normal-qoq']['tool_result'])
            result['evidence'][0][key] = val
            ctx = self.context(result)
            self.assertEqual(ctx['status'], 'needs_review', key)
            self.assertEqual(ctx['evidence'], [], key)

    def test_unknown_unit_is_not_guessed_even_for_equivalent_amount(self):
        result = copy.deepcopy(self.rows['normal-qoq']['tool_result'])
        result['evidence'][0].update(scale=2, value='39549365500000')
        ctx = self.context(result)
        self.assertEqual(ctx['status'], 'needs_review')
        self.assertEqual(ctx['evidence'], [])

    def test_provider_keeps_actual_prose_separate_from_deterministic_context(self):
        row = self.rows['unit-draft']
        answer = row['generated']
        response = httpx.Response(200, json={
            'status': 'completed', 'model': pp.MODEL,
            'usage': {'input_tokens': 600, 'output_tokens': 200},
            'output': [{'type': 'message', 'content': [
                {'type': 'output_text', 'text': json.dumps(answer)}]}]})
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-only'}), \
                patch.object(pp.httpx, 'post', return_value=response):
            result = pp.generate_public(pp.build_payload(row['tool_result'], '검토'), row['tool_result'])
        self.assertEqual(result['generated'], answer)
        self.assertFalse(result['prose_semantics_verified'])
        self.assertIn('explanation_context', result)
        self.assertEqual(result['explanation_context']['origin'], 'deterministic_tool_context')
        self.assertEqual(result['explanation_context']['evidence'][0]['display_unit'], '백만 원')
