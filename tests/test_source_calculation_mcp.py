"""Actual MCP stdio integration, not prepared-result replay."""
import json,sys,unittest
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.store import ROOT
from quarterguard.source_evidence import DOCUMENT_ID

def unpack(r):
    return r.structuredContent or json.loads(next(c.text for c in r.content if c.type=='text'))

class SourceCalculationMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_read_and_calculate_on_wire(self):
        async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.source_mcp_server'],cwd=str(ROOT))) as (r,w):
            async with ClientSession(r,w) as s:
                await s.initialize()
                names={x.name for x in (await s.list_tools()).tools}
                self.assertIn('calculate_source_pair',names)
                found=unpack(await s.call_tool('search_source_evidence',{'document_id':DOCUMENT_ID,'query':'현금은 2023년 말보다 얼마나 늘었나?'}))
                by={h['cell']['year']:h['cell']['id'] for h in found['hits']}
                for cell_id in by.values():self.assertFalse((await s.call_tool('get_source_cell',{'cell_id':cell_id})).isError)
                result=await s.call_tool('calculate_source_pair',{'current_id':by[2024],'base_id':by[2023],'mode':'balance_yoy'})
                self.assertFalse(result.isError);self.assertEqual(unpack(result)['growth_pct'],'47.6820')
                result=await s.call_tool('calculate_source_pair',{'current_id':'bad','base_id':by[2023],'mode':'balance_yoy'})
                self.assertTrue(result.isError)
