"""Offline safety and audit regressions; never calls a paid provider."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx


class LiveExplanationV3Tests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('quarterguard.evaluate_live_explanations_v3'),
                             'bounded live evaluation harness is missing')
        from quarterguard import evaluate_live_explanations_v3
        return evaluate_live_explanations_v3

    def test_admission_bound_counts_unicode_schema_and_rejects_oversize(self):
        m = self.module()
        payload = m.make_payload({'id': 'x', 'task': '한글', 'tool_result': {'evidence': []}})
        self.assertGreaterEqual(m.input_admission_bound(payload), len(json.dumps(payload, ensure_ascii=False).encode()))
        with self.assertRaisesRegex(ValueError, 'INPUT_ADMISSION_LIMIT'):
            m.make_payload({'id': 'x', 'task': '한글' * 6000, 'tool_result': {}})

    def test_execution_requires_explicit_approval_and_preserves_existing_attempts(self):
        m = self.module()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'EXPLICIT_APPROVAL_REQUIRED'):
                m.execute({}, Path(d), execute_approved=False)
            (Path(d) / 'attempts.jsonl').write_text('prior attempt\n')
            with self.assertRaisesRegex(ValueError, 'RUN_ALREADY_ATTEMPTED'):
                m.execute({}, Path(d), execute_approved=True)
            self.assertEqual((Path(d) / 'attempts.jsonl').read_text(), 'prior attempt\n')

    def test_failed_http_attempt_is_sanitized_and_never_retried(self):
        m = self.module()
        case = {'id': 'one', 'task': 'test', 'tool_result': {'status': 'needs_review', 'issues': ['SEARCH_EMPTY'], 'evidence': []}}
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'OPENAI_API_KEY': 'private-secret'}), \
                patch.object(m, 'validate_freeze'), patch.object(m.httpx, 'post', return_value=httpx.Response(429, text='private-secret')) as post:
            report = m.execute({'cases': [case, case], 'contract': m.CONTRACT}, Path(d), execute_approved=True)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(report['calls_attempted'], 1)
            self.assertEqual(report['status'], 'failed')
            self.assertIn('OPENAI_HTTP_429', json.dumps(report))
            self.assertNotIn('private-secret', ''.join(p.read_text() for p in Path(d).iterdir()))

    def test_timeout_is_one_failed_attempt_without_exception_text(self):
        m = self.module()
        case = {'id': 'one', 'task': 'test', 'tool_result': {'status': 'needs_review', 'issues': ['SEARCH_EMPTY'], 'evidence': []}}
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'OPENAI_API_KEY': 'private-secret'}), \
                patch.object(m, 'validate_freeze'), patch.object(m.httpx, 'post', side_effect=httpx.ReadTimeout('private-secret')) as post:
            report = m.execute({'cases': [case], 'contract': m.CONTRACT}, Path(d), execute_approved=True)
            self.assertEqual(post.call_count, 1)
            self.assertEqual(report['records'][0]['failure_code'], 'OPENAI_CONNECTION_FAILED')
            self.assertNotIn('private-secret', json.dumps(report))

    def test_frozen_cases_cover_all_dimensions_and_tampering_fails(self):
        m = self.module()
        frozen = json.loads((m.DATA / 'freeze.json').read_text())
        m.validate_freeze(frozen)
        self.assertEqual(len(frozen['cases']), 8)
        self.assertEqual({c['dimension'] for c in frozen['cases']}, {'qoq', 'yoy', 'period', 'scope', 'unit', 'no_evidence', 'conflicting_number', 'citation'})
        changed = copy.deepcopy(frozen)
        changed['cases'][0]['tool_result']['growth_pct'] = '999'
        with self.assertRaisesRegex(ValueError, 'FREEZE_CONTENT_MISMATCH'):
            m.validate_freeze(changed)

    def test_synthetic_challenges_are_separate_and_never_certify_semantics(self):
        m = self.module()
        frozen = json.loads((m.DATA / 'freeze.json').read_text())
        rows = m.synthetic_checks(frozen)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r['expected_rule_detected'] for r in rows))
        self.assertTrue(all(r['origin'] == 'authored_synthetic_validator_challenge' for r in rows))
        self.assertTrue(all(r['audit']['semantic_certified'] is False for r in rows))

    def test_provider_response_retains_actual_prose_usage_and_blank_human_task(self):
        m = self.module()
        frozen = json.loads((m.DATA / 'freeze.json').read_text())
        case = frozen['cases'][0]
        answer = m.structured_answer(case['tool_result'], '2024년 3분기 연결 매출은 전분기 대비 6.7916% 증가했습니다.')
        body = {'id': 'resp_test', 'status': 'completed', 'model': m.MODEL, 'usage': {'input_tokens': 500, 'output_tokens': 100},
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(answer)}]}], 'unsafe_arbitrary_metadata': 'private-secret'}
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'OPENAI_API_KEY': 'private-secret'}), \
                patch.object(m, 'validate_freeze'), patch.object(m.httpx, 'post', return_value=httpx.Response(200, json=body)):
            report = m.execute({'cases': [case], 'contract': m.CONTRACT}, Path(d), execute_approved=True)
            row = report['records'][0]
            self.assertEqual(row['generated'], answer)
            self.assertEqual(row['provider']['input_tokens'], 500)
            self.assertEqual(row['provider']['estimated_cost_usd'], '0.000825')
            self.assertIsNone(row['provider']['billed_cost_usd'])
            review = json.loads((Path(d) / 'human-review.json').read_text())[0]
            self.assertIsNone(review['verdict'])
            self.assertIsNone(review['reviewer'])
            self.assertFalse(row['audit']['semantic_certified'])
            self.assertNotIn('private-secret', ''.join(p.read_text() for p in Path(d).iterdir()))
