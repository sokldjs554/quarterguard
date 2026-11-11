import asyncio
import unittest
from unittest.mock import patch
from quarterguard import bounded_planner as p
from quarterguard.mcp_server import search_documents, get_fact, verify_comparison

A='s24q3-CFS-revenue-2024-q-KRW'
B='s24q2-CFS-revenue-2024-q-KRW'
QUERIES=['samsung 2024 Q3 CFS revenue quarter KRW','samsung 2024 Q2 CFS revenue quarter KRW']

def action(name, **arguments): return {'tool':name,'arguments':arguments}
def sequence():
    return [action('search_documents',query=q) for q in QUERIES]+[action('get_fact',fact_id=f) for f in (A,B)]+[action('verify_comparison',current_id=A,base_id=B,mode='qoq')]

class PlannerTests(unittest.IsolatedAsyncioTestCase):
    async def run_plan(self, actions, call=None, **kwargs):
        iterator=iter(actions)
        async def choose(payload): return next(iterator)
        async def real(name,args):
            return {'search_documents':search_documents,'get_fact':get_fact,'verify_comparison':verify_comparison}[name](**args)
        return await p.run(QUERIES,'qoq',choose,call or real,**kwargs)
    async def test_actual_tools_compute_only_after_retrieval_and_read(self):
        out=await self.run_plan(sequence())
        self.assertEqual(out['result']['growth_pct'],'6.7916')
        self.assertEqual(len(out['trace']),5)
        self.assertEqual(out['planner'],'bounded_model_tool_selection')
    async def test_unread_id_cannot_compute(self):
        out=await self.run_plan([sequence()[-1]])
        self.assertEqual(out['failure'],'UNREAD_FACT')
        self.assertIsNone(out['result'])
    async def test_search_cannot_change_user_query(self):
        out=await self.run_plan([action('search_documents',query='invent a company')])
        self.assertEqual(out['failure'],'QUERY_NOT_ALLOWED')
    async def test_unknown_tool_and_extra_fields_block(self):
        for a in [action('shell',cmd='ls'),action('search_documents',query=QUERIES[0],k=100)]:
            out=await self.run_plan([a]);self.assertIsNone(out['result'])
    async def test_repeated_action_stops(self):
        out=await self.run_plan([sequence()[0]]*2)
        self.assertEqual(out['failure'],'REPEATED_ACTION')
    async def test_wrong_direction_and_mode_block(self):
        for args in [dict(current_id=B,base_id=A,mode='qoq'),dict(current_id=A,base_id=B,mode='yoy')]:
            out=await self.run_plan(sequence()[:4]+[action('verify_comparison',**args)])
            self.assertEqual(out['failure'],'COMPARISON_NOT_ALLOWED')
    async def test_fake_search_id_and_numeric_output_block(self):
        async def forged(name,args): return {'hits':[{'fact_ids':['fake']}]}
        out=await self.run_plan(sequence(),call=forged)
        self.assertEqual(out['failure'],'INVALID_TOOL_RESPONSE')
        async def bad_math(name,args):
            out={'search_documents':search_documents,'get_fact':get_fact,'verify_comparison':verify_comparison}[name](**args)
            if name=='verify_comparison':out['growth_pct']='999'
            return out
        out=await self.run_plan(sequence(),call=bad_math)
        self.assertEqual(out['failure'],'INVALID_TOOL_RESPONSE')
    async def test_timeout_and_transport_error_clear_result(self):
        async def timeout(name,args): await asyncio.sleep(1)
        out=await self.run_plan(sequence(),call=timeout,timeout=.01)
        self.assertEqual(out['failure'],'TIMEOUT');self.assertIsNone(out['result'])
        async def fail(name,args): raise RuntimeError('secret must not leak')
        out=await self.run_plan(sequence(),call=fail)
        self.assertEqual(out['failure'],'EXECUTION_ERROR');self.assertNotIn('secret',str(out))
    async def test_empty_search_holds_without_more_decisions(self):
        queries=['samsung 2025 Q3 CFS revenue quarter KRW',QUERIES[0]]
        async def choose(payload): return action('search_documents',query=queries[0])
        async def call(name,args):return search_documents(**args)
        out=await p.run(queries,'yoy',choose,call)
        self.assertEqual(out['result']['issues'],['SEARCH_EMPTY'])
        self.assertEqual(out['model_decisions'],1)
