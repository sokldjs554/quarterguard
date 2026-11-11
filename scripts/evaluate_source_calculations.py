"""Raw-PDF equality then real MCP search/read/calculate; no LLM calls or replay."""
import argparse,asyncio,hashlib,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.source_evidence import parse_pdf,load_source,DOCUMENT_ID,PDF_SHA
from quarterguard.store import ROOT

# Explicit evaluator selections derived from the user's submitted answers.
# Not an automatic NL planner. Exact four-decimal percentages are AI Decimal checks.
OPERATIONS=[
 ('SKH1','cash_change','cash',2024,'cash',2023,'balance_yoy',{'status':'verified','difference':'3617788','growth_pct':'47.6820','share_pct':None}),
 ('SKH2','revenue_change','revenue',2024,'revenue',2023,'annual_yoy',{'status':'verified','difference':'33427241','growth_pct':'102.0189','share_pct':None}),
 ('SKH2','inventory_change','inventory',2024,'inventory',2023,'balance_yoy',{'status':'verified','difference':'-166722','growth_pct':'-1.2367','share_pct':None}),
 ('SKH3','dram_share','dram',2024,'product_total',2024,'product_share',{'status':'verified','difference':None,'growth_pct':None,'share_pct':'67.5777'}),
 ('SKH4','loss_to_profit','operating_profit',2024,'operating_profit',2023,'annual_yoy',{'status':'needs_review','difference':'31197632','growth_pct':None,'share_pct':None,'issues':['NEGATIVE_BASE'],'transition':'loss_to_profit'}),
 ('SKH5','inventory_definition','inventory',2024,'revenue',2023,'inventory_months',{'status':'needs_review','difference':None,'growth_pct':None,'share_pct':None,'issues':['RATIO_DEFINITION_REQUIRED']}),
]

async def run(pdf,output):
 output.mkdir(parents=True,exist_ok=False)
 start=time.perf_counter();parsed=parse_pdf(pdf);parse_ms=(time.perf_counter()-start)*1000
 manifest,registered=load_source();assert parsed==registered
 by={(c['metric'],c['year']):c for c in parsed}
 questions=json.loads((ROOT/'data/skhynix-human-20261111/cases.json').read_text())
 traces=[];results=[]
 async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.source_mcp_server'],cwd=str(ROOT))) as (r,w):
  async with ClientSession(r,w) as session:
   init=await session.initialize()
   async def call(name,args):
    start=time.perf_counter();raw=await session.call_tool(name,args)
    assert not raw.isError
    out=raw.structuredContent or json.loads(next(c.text for c in raw.content if c.type=='text'))
    traces.append({'order':len(traces)+1,'tool':name,'input':args,'output':out,'elapsed_ms':(time.perf_counter()-start)*1000})
    return out
   for question in questions:
    found=await call('search_source_evidence',{'document_id':DOCUMENT_ID,'query':question['question']})
    assert found['calculated_answer'] is None
    for hit in found['hits']:
     cell=await call('get_source_cell',{'cell_id':hit['cell']['id']});assert cell==hit['cell'] and cell in parsed
    for qid,name,am,ay,bm,byear,mode,expected in OPERATIONS:
     if qid!=question['id']:continue
     args={'current_id':by[am,ay]['id'],'base_id':by[bm,byear]['id'],'mode':mode}
     # Both IDs must be present among the query's returned evidence, not invented.
     assert {args['current_id'],args['base_id']}<={h['cell']['id'] for h in found['hits']}
     out=await call('calculate_source_pair',args)
     for key,value in expected.items():
      actual=out['difference']['value'] if key=='difference' and out['difference'] else out[key]
      assert actual==value,(name,key,actual,value)
     assert all(c in parsed for c in out['evidence'])
     results.append({'question_id':qid,'operation':name,'selected_inputs':args,'selection_origin':'Explicit evaluator selection from user answer and source; not natural-language auto-planning','expected':expected,'passed':True,'result':out})
 report={'at_utc':datetime.now(timezone.utc).isoformat(),'pdf':{'sha256':PDF_SHA,'selected_pages_parsed':3,'cells':18,'registered_cells_equal_raw_pdf':True,'parse_elapsed_ms':parse_ms},
  'evaluation_type':'Known human-authored development cases; explicit pair operations, not an independent NL answer benchmark',
  'gold_origin':'User-submitted values/differences and approximate cash/DRAM percentages; exact four-decimal revenue/inventory/cash/share checks added by AI Decimal calculation',
  'operations':results,'passed_operations':len(results),'complete_numeric_operations':4,'difference_only_negative_base':1,'definition_required':1,
  'mcp':{'execution':'actual stdio calls; deterministic evaluator sequence','protocol':init.protocolVersion,'calls':len(traces),'trace':traces},
  'paid_api_calls':0,'new_llm_generations':0,'new_human_review':False,'new_external_participants':0,
  'limitations':['No new document or undisclosed query holdout.','Only registered18cells and three explicit calculation contracts.',
     'Q1 current year selected from submitted answer, not inferred silently.','Q2 uses two separate calculations; inventory remains a stock and revenue a flow.',
     'Negative-base rate withheld; inventory-months ratio undefined.','MCP caller chooses tools by rules, not LLM autonomy.','Local timing not a production performance claim.'],
  'code_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['quarterguard/source_calculations.py','quarterguard/source_mcp_server.py','quarterguard/source_evidence.py','scripts/evaluate_source_calculations.py']}}
 (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'raw_pdf_pages':3,'cells':18,'operations_passed':len(results),'actual_mcp_calls':len(traces),'paid_calls':0}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pdf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();asyncio.run(run(a.pdf,a.output))
