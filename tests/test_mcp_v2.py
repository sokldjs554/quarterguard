"""Actual stdio MCP checks are separate from explicitly injected failures."""
import asyncio
from contextlib import asynccontextmanager
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard import orchestrator
from quarterguard.store import ROOT, load_facts
from quarterguard.core import compare, reconcile

WIRE_CHECKS = [
    ('malformed_id', 'get_fact', {'fact_id': 'absent'}, True, None),
    ('invalid_mode', 'verify_comparison', {
        'current_id': 's24q3-CFS-revenue-2024-q-KRW',
        'base_id': 's24q2-CFS-revenue-2024-q-KRW', 'mode': 'invalid'}, True, None),
    ('period_mismatch', 'verify_comparison', {
        'current_id': 's24q3-CFS-revenue-2024-ytd-KRW',
        'base_id': 's24q3-CFS-revenue-2023-q-KRW', 'mode': 'yoy'}, False, 'PERIOD_MISMATCH'),
    ('scope_mismatch', 'verify_comparison', {
        'current_id': 's24q3-CFS-revenue-2024-q-KRW',
        'base_id': 's24q2-OFS-revenue-2024-q-KRW', 'mode': 'qoq'}, False, 'SCOPE_MISMATCH'),
    ('usd_translation_block', 'verify_comparison', {
        'current_id': 's24q3-CFS-revenue-2024-q-USD',
        'base_id': 's24q2-CFS-revenue-2024-q-USD', 'mode': 'qoq'}, False, 'CONVENIENCE_TRANSLATION'),
]


async def injected_failure(kind):
    """No real wire or provider: inject failure on get_fact after one search."""
    @asynccontextmanager
    async def fake_stdio(*args, **kwargs):
        yield None, None

    class Session:
        def __init__(self, *args):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def initialize(self):
            return SimpleNamespace(protocolVersion='injected-test-protocol')
        async def call_tool(self, name, args):
            if name == 'search_documents':
                return SimpleNamespace(isError=False, structuredContent={
                    'hits': [{'fact_ids': ['s24q3-CFS-revenue-2024-q-KRW']}]})
            if kind == 'transport':
                raise ConnectionError('private-provider-token-must-not-appear')
            if kind == 'timeout':
                await asyncio.Event().wait()
            if kind == 'tool_error':
                return SimpleNamespace(isError=True)
            if kind == 'invalid_response':
                return SimpleNamespace(isError=False, structuredContent=None,
                                       content=[SimpleNamespace(type='text', text='not json')])
            raise AssertionError(kind)

    with patch.object(orchestrator, 'stdio_client', fake_stdio), \
            patch.object(orchestrator, 'ClientSession', Session), \
            patch.object(orchestrator, '_WORKFLOW_TIMEOUT_SECONDS', 0.03, create=True):
        return await orchestrator.run_case('qoq-revenue')


async def injected_shape(tool, payload, case_id='qoq-revenue'):
    """Valid JSON with wrong tool schema, using an explicitly mocked session."""
    case = next(c for c in orchestrator.cases() if c['id'] == case_id)
    facts = {f.id: f for f in load_facts()}
    @asynccontextmanager
    async def fake_stdio(*args, **kwargs):
        yield None, None
    class Session:
        def __init__(self, *args): self.queries = 0
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return False
        async def initialize(self): return SimpleNamespace(protocolVersion='injected-test-protocol')
        async def call_tool(self, name, args):
            if name == tool:
                value = payload
            elif name == 'search_documents':
                value = {'hits': [{'fact_ids': [case['expected_evidence'][self.queries]['id']]}]}
                self.queries += 1
            elif name == 'get_fact':
                value = facts[args['fact_id']].public()
            elif name == 'verify_comparison':
                value = compare(facts[args['current_id']], facts[args['base_id']], args['mode'])
            else:
                value = reconcile(facts[args['ytd_id']], facts[args['previous_id']], facts[args['direct_id']])
            return SimpleNamespace(isError=False, structuredContent=value)
    with patch.object(orchestrator, 'stdio_client', fake_stdio), patch.object(orchestrator, 'ClientSession', Session):
        return await orchestrator.run_case(case_id)


class MCPFailureInjectionV2Tests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_json_wrong_schema_is_failed_before_success(self):
        for tool, payload, case in [
            ('search_documents', {'hits': 'not-a-list'}, 'qoq-revenue'),
            ('search_documents', {'hits': [{}]}, 'qoq-revenue'),
            ('get_fact', {}, 'qoq-revenue'),
            ('verify_comparison', {'status': 'verified'}, 'qoq-revenue'),
            ('verify_comparison', {'status': 'verified', 'issues': [], 'evidence': [], 'growth_pct': '1'}, 'qoq-revenue'),
            ('reconcile_quarter', {'status': 'verified'}, 'reconcile-revenue'),
        ]:
            with self.subTest(tool=tool, payload=payload):
                try:
                    result = await injected_shape(tool, payload, case)
                except Exception as error:
                    self.fail(f'Malformed tool response escaped run_case: {type(error).__name__}')
                self.assertEqual(result['result'], {'status': 'needs_review', 'issues': ['TOOL_ERROR'], 'evidence': []})
                self.assertFalse(result['workflow_success'])
                self.assertEqual(result['trace'][-1]['tool'], tool)
                self.assertEqual(result['trace'][-1].get('failure_type'), 'INVALID_TOOL_RESPONSE')
                self.assertFalse(result['trace'][-1]['success'])

    async def test_semantically_typed_payloads_require_canonical_evidence_and_finite_values(self):
        facts = {f.id: f for f in load_facts()}
        current = facts['s24q3-CFS-revenue-2024-q-KRW']
        base = facts['s24q2-CFS-revenue-2024-q-KRW']
        valid = compare(current, base, 'qoq')
        variants = [('get_fact', current.public() | {'page': 999}),
                    ('verify_comparison', valid | {'growth_pct': 'NaN'}),
                    ('verify_comparison', valid | {'issues': 'not-a-list'}),
                    ('verify_comparison', valid | {'evidence': [current.public(), current.public()]})]
        for tool, payload in variants:
            with self.subTest(tool=tool, payload=payload):
                result = await injected_shape(tool, payload)
                self.assertEqual(result['trace'][-1].get('failure_type'), 'INVALID_TOOL_RESPONSE')
                self.assertEqual(result['result']['status'], 'needs_review')
                self.assertEqual(result['result']['evidence'], [])

    async def test_transport_failure_retains_attempt_and_sanitizes_exception(self):
        result = await injected_failure('transport')
        self.assertEqual(len(result['trace']), 2)
        step = result['trace'][-1]
        self.assertEqual(step['tool'], 'get_fact')
        self.assertEqual(step['arguments']['fact_id'], 's24q3-CFS-revenue-2024-q-KRW')
        self.assertEqual(step['failure_type'], 'TOOL_TRANSPORT_ERROR')
        self.assertFalse(step['success'])
        self.assertGreaterEqual(step['latency_ms'], 0)
        self.assertNotIn('private-provider-token', json.dumps(result))
        self.assertEqual(result['result'], {'status': 'needs_review', 'issues': ['TOOL_ERROR'], 'evidence': []})
        self.assertFalse(result['workflow_success'])

    async def test_timeout_retains_failed_tool_and_clears_result(self):
        self.assertTrue(hasattr(orchestrator, '_WORKFLOW_TIMEOUT_SECONDS'))
        result = await injected_failure('timeout')
        self.assertEqual(len(result['trace']), 2)
        self.assertEqual(result['trace'][-1]['failure_type'], 'TOOL_TIMEOUT')
        self.assertFalse(result['trace'][-1]['success'])
        self.assertEqual(result['result'], {'status': 'needs_review', 'issues': ['TOOL_TIMEOUT'], 'evidence': []})
        self.assertFalse(result['workflow_success'])

    async def test_error_response_and_invalid_json_are_traced(self):
        for kind, code in [('tool_error', 'TOOL_ERROR'), ('invalid_response', 'INVALID_TOOL_RESPONSE')]:
            with self.subTest(kind=kind):
                result = await injected_failure(kind)
                self.assertEqual(len(result['trace']), 2)
                self.assertEqual(result['trace'][-1]['failure_type'], code)
                self.assertFalse(result['trace'][-1]['success'])
                self.assertEqual(result['result']['status'], 'needs_review')
                self.assertEqual(result['result']['evidence'], [])


class MCPRealWireV2Tests(unittest.IsolatedAsyncioTestCase):
    async def test_eight_curated_cases_keep_order_and_gold(self):
        for case in orchestrator.cases():
            with self.subTest(case=case['id']):
                run = await orchestrator.run_case(case['id'])
                self.assertTrue(run['workflow_success'])
                self.assertEqual(run['result']['status'], case['expected_status'])
                self.assertEqual(run['result']['evidence'], case['expected_evidence'])
                if 'expected_issue' in case:
                    self.assertIn(case['expected_issue'], run['result']['issues'])
                if 'expected_value' in case:
                    self.assertEqual(run['result'].get('growth_pct', run['result'].get('derived_value')), case['expected_value'])
                expected = ['search_documents'] if case['id'] == 'no-evidence' else [
                    name for _ in case['queries'] for name in ('search_documents', 'get_fact')
                ] + ['verify_comparison' if case['operation'] == 'compare' else 'reconcile_quarter']
                self.assertEqual([step['tool'] for step in run['trace']], expected)
                self.assertTrue(all(step['success'] for step in run['trace']))

    async def test_real_wire_invalid_input_and_context_blocks(self):
        async with stdio_client(StdioServerParameters(command=sys.executable,
                args=['-m', 'quarterguard.mcp_server'], cwd=str(ROOT))) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                for name, tool, arguments, error, issue in WIRE_CHECKS:
                    with self.subTest(case=name):
                        response = await session.call_tool(tool, arguments)
                        self.assertEqual(response.isError, error)
                        if issue:
                            value = response.structuredContent
                            if value is None:
                                value = json.loads(next(c.text for c in response.content if c.type == 'text'))
                            self.assertEqual(value['status'], 'needs_review')
                            self.assertIn(issue, value['issues'])


if __name__ == '__main__':
    unittest.main()
