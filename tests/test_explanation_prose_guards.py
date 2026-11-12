"""Replay disclosed v5 outputs and authored edge cases; no model/human calls."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from quarterguard import public_providers as pp
from quarterguard.store import ROOT
from quarterguard.explanation_guards import check_prose


class ProseGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['case_id']: r for r in json.loads(
            (ROOT / 'artifacts/llm-guards-v5-20261110/report.json').read_text())['records']}

    def generate(self, case, text=None):
        row = self.rows[case]
        answer = copy.deepcopy(row['generated'])
        if text is not None:
            answer['explanation_ko'] = text
        response = httpx.Response(200, json={
            'status': 'completed', 'model': pp.MODEL,
            'usage': {'input_tokens': 100, 'output_tokens': 100},
            'output': [{'type': 'message', 'content': [
                {'type': 'output_text', 'text': json.dumps(answer)}]}]})
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-only'}), \
                patch.object(pp.httpx, 'post', return_value=response):
            return pp.generate_public({}, row['tool_result'])

    def rejected(self, case, check, text=None):
        with self.assertRaises(pp.ExplanationRejected) as error:
            self.generate(case, text)
        self.assertFalse(error.exception.checks[check])
        self.assertTrue(error.exception.checks['citations_exact'])
        self.assertNotIn('explanation_ko', error.exception.checks)

    def test_evidence_present_rejects_v5_search_absence_tail(self):
        self.rejected('period-mismatch', 'prose_evidence_presence_consistent')

    def test_multiple_documents_reject_v5_same_report_claim(self):
        self.rejected('citation-draft', 'prose_document_reference_unambiguous')

    def test_percent_missing_is_rejected_independently_of_document_error(self):
        for text in ['매출 증가율은 6.7916입니다.', '매출 증가율은 6.79입니다.',
                     '증가율은 6.7916%입니다. 다시 쓰면 6.7916입니다.',
                     '증가율은 6.7916%입니다. 다시 쓰면 6.7916.']:
            with self.subTest(text=text):
                self.rejected('normal-qoq', 'prose_rate_unit_explicit', text)

    def test_internal_review_phrase_is_rejected_even_when_no_evidence_is_correct(self):
        self.rejected('no-evidence', 'prose_review_language_localized')

    def test_same_document_yoy_and_other_v5_prose_pass_narrow_pattern_checks(self):
        for case in ['normal-qoq', 'normal-yoy', 'scope-mismatch', 'unit-draft',
                     'conflicting-number-draft']:
            with self.subTest(case=case):
                row = self.rows[case]
                self.assertTrue(all(check_prose(row['generated'], row['tool_result']).values()))
                # Historical text remains unchanged; the new evidence-binding gate
                # can still reject it independently of these narrow pattern checks.

    def test_authored_corrected_phrases_pass_without_rewriting(self):
        texts = {
            'period-mismatch': '근거는 확인했으나 9개월 누적과 3개월의 기간이 달라 성장률 계산을 보류합니다.',
            'no-evidence': '해당 검색 범위에서 근거를 확인할 수 없습니다. 검색 조건과 수집 범위를 확인하세요.',
            'citation-draft': '3분기 보고서 PDF p.34와 반기 보고서 PDF p.48을 비교한 증가율은 6.7916%입니다.',
        }
        for case, text in texts.items():
            with self.subTest(case=case):
                self.assertTrue(all(check_prose({'explanation_ko': text}, self.rows[case]['tool_result']).values()))
        for text in ['증가율은 6.79%입니다.', '증가율은 6.7916 퍼센트입니다.',
                     '증가율은 +6.7916％입니다.']:
            self.assertTrue(all(check_prose({'explanation_ko': text}, self.rows['normal-qoq']['tool_result']).values()))

    def test_failed_prose_is_not_returned_or_cached_and_previous_cache_not_reused(self):
        row = self.rows['citation-draft']
        run = {'workflow_success': True, 'run_id': 'replay', 'trace': [{}], 'result': row['tool_result']}
        expected = {'id': 'qoq-revenue', 'description': 'archived replay',
                    'expected_status': row['tool_result']['status'],
                    'expected_evidence': row['tool_result']['evidence'],
                    'expected_value': row['tool_result']['growth_pct']}
        good = copy.deepcopy(self.rows['normal-qoq']['generated'])
        good['explanation_ko'] = '\n'.join(x['required_claim'] for x in pp.build_context(row['tool_result'])['evidence']) + ' 증가율 6.7916%.'
        def response(answer):
            return httpx.Response(200, json={'status': 'completed', 'model': pp.MODEL,
                'usage': {'input_tokens': 100, 'output_tokens': 100},
                'output': [{'type': 'message', 'content': [
                    {'type': 'output_text', 'text': json.dumps(answer)}]}]})
        with tempfile.TemporaryDirectory() as tmp, \
                patch.dict(os.environ, {'QG_LEDGER_PATH': str(Path(tmp)/'ledger'), 'OPENAI_API_KEY': 'test-only'}, clear=True), \
                patch.object(pp, 'reasons', return_value=[]), \
                patch.object(pp, 'run_case', AsyncMock(return_value=run)), \
                patch.object(pp, 'cases', return_value=[expected]), \
                patch.object(pp, 'verification_version', side_effect=['old', 'new']), \
                patch('quarterguard.provider_controls.time.time', return_value=1000) as clock, \
                patch.object(pp.httpx, 'post', side_effect=[response(good), response(row['generated'])]):
            self.assertEqual(pp.execute('openai', 'qoq-revenue')['status'], 'succeeded')
            clock.return_value = 2000
            result = pp.execute('openai', 'qoq-revenue')
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['reason'], 'EXPLANATION_VALIDATION_REJECTED')
            self.assertNotIn('generated', result)
            self.assertNotIn('explanation_context', result)
            self.assertIsNone(pp.ledger().cached('openai', 'v2:'+pp.MODEL+':new:qoq-revenue'))
            self.assertEqual(pp.ledger().usage('openai')['attempts_total'], 2)

    def test_cache_fingerprint_includes_prose_validator(self):
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            return data+b'\n# changed rule' if path.name == 'explanation_guards.py' else data
        before = pp.verification_version()
        with patch.object(Path, 'read_bytes', changed):
            self.assertNotEqual(before, pp.verification_version())
