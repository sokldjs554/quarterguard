import unittest, asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.orchestrator import run_case
from quarterguard.store import ROOT
class MCPTests(unittest.IsolatedAsyncioTestCase):
 async def test_actual_wire_protocol(self):
  async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.mcp_server'],cwd=str(ROOT))) as (r,w):
   async with ClientSession(r,w) as s:
    init=await s.initialize(); self.assertTrue(init.protocolVersion)
    names={t.name for t in (await s.list_tools()).tools}
    self.assertEqual(names,{'search_documents','get_fact','verify_comparison','reconcile_quarter'})
    response=await s.call_tool('get_fact',{'fact_id':'absent'})
    self.assertTrue(response.isError)
 async def test_live_path(self):
  r=await run_case('qoq-revenue')
  self.assertEqual(r['result']['growth_pct'],'6.7916')
  self.assertEqual(r['execution_mode'],'live_mcp');self.assertEqual(len(r['trace']),5)
 async def test_missing_evidence(self):
  r=await run_case('no-evidence');self.assertIn('SEARCH_EMPTY',r['result']['issues'])
if __name__=='__main__':unittest.main()
