import sys
import json
import unittest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.store import ROOT
from quarterguard.source_evidence import DOCUMENT_ID

class SourceMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_source_search_then_cell_no_calculation(self):
        async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.source_mcp_server'],cwd=str(ROOT))) as (r,w):
            async with ClientSession(r,w) as s:
                await s.initialize()
                names={t.name for t in (await s.list_tools()).tools}
                self.assertIn('search_source_evidence',names)
                found=await s.call_tool('search_source_evidence',{'document_id':DOCUMENT_ID,'query':'2024년 DRAM 매출 비중'})
                self.assertFalse(found.isError)
                data=found.structuredContent or json.loads(next(c.text for c in found.content if c.type=='text'))
                self.assertEqual(data['answer_status'],'not_calculated')
                cell=data['hits'][0]['cell']
                read=await s.call_tool('get_source_cell',{'cell_id':cell['id']})
                self.assertEqual(read.structuredContent or json.loads(next(c.text for c in read.content if c.type=='text')),cell)
                missing=await s.call_tool('get_source_cell',{'cell_id':'unknown'})
                self.assertTrue(missing.isError)
