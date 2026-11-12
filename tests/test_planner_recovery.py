"""Scripted decisions exercise real tools; these are not model success counts."""
import json
import unittest
from tests import test_bounded_planner as base_tests
from tests.test_bounded_planner import sequence, action, A, B


class PlannerRecoveryTests(unittest.IsolatedAsyncioTestCase):
    run_plan = base_tests.PlannerTests.run_plan
    async def test_missing_reads_are_observed_then_model_can_retry_comparison(self):
        actions = sequence()[:2] + [sequence()[-1]] + sequence()[2:]
        out = await self.run_plan(actions)
        self.assertIsNone(out['failure'])
        self.assertEqual(out['result']['growth_pct'], '6.7916')
        self.assertEqual(out['model_decisions'], 6)
        self.assertEqual(out['tool_calls'], 5)
        rejected = out['trace'][2]
        self.assertFalse(rejected['executed'])
        self.assertEqual(rejected['output']['error'], 'UNREAD_FACT')
        self.assertEqual(rejected['output']['missing_fact_ids'], [A, B])
        self.assertTrue(out['trace'][-1]['executed'])

    async def test_repeated_missing_reads_stop_at_recovery_budget(self):
        out = await self.run_plan(sequence()[:2] + [sequence()[-1]] * 3)
        self.assertEqual(out['failure'], 'RECOVERY_LIMIT')
        self.assertIsNone(out['result'])
        self.assertEqual(out['tool_calls'], 2)

    async def test_reversed_unread_comparison_is_not_recoverable(self):
        out = await self.run_plan(sequence()[:2] + [action(
            'verify_comparison', current_id=B, base_id=A, mode='qoq')])
        self.assertEqual(out['failure'], 'COMPARISON_NOT_ALLOWED')
        self.assertIsNone(out['result'])

    async def test_missing_reads_feedback_reaches_next_model_request(self):
        from quarterguard import bounded_planner as p
        from quarterguard.mcp_server import search_documents, get_fact, verify_comparison
        from tests.test_bounded_planner import QUERIES
        steps = iter(sequence()[:2] + [sequence()[-1]] + sequence()[2:])
        observed = []
        async def choose(payload):
            observed.append(json.loads(payload['input']))
            return next(steps)
        async def call(name, args):
            return {'search_documents': search_documents, 'get_fact': get_fact,
                    'verify_comparison': verify_comparison}[name](**args)
        await p.run(QUERIES, 'qoq', choose, call)
        self.assertEqual(observed[3]['previous_steps'][-1]['output']['error'], 'UNREAD_FACT')
