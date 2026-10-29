"""Bounded, deterministic tool workflow. This is not an LLM planner."""
import asyncio, json, sys, time, uuid
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from .store import ROOT

def cases():return json.loads((ROOT/'data/cases.json').read_text())

async def run_case(case_id):
    case=next((c for c in cases() if c['id']==case_id),None)
    if case is None:raise ValueError('UNKNOWN_CASE')
    start=time.perf_counter(); trace=[];run_id=str(uuid.uuid4()); result=None
    async def execute():
        nonlocal result
        (ROOT/'work').mkdir(exist_ok=True)
        with open(ROOT/'work/mcp-stderr.log','a') as log:
            async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.mcp_server'],cwd=str(ROOT)),errlog=log) as (r,w):
                async with ClientSession(r,w) as session:
                    init=await session.initialize()
                    async def call(name,args):
                        t=time.perf_counter();response=await session.call_tool(name,args)
                        item={'step':len(trace)+1,'tool':name,'arguments':args,'latency_ms':round((time.perf_counter()-t)*1000,3),'success':not response.isError}
                        if response.isError:
                            item['failure_type']='TOOL_ERROR';trace.append(item);raise ValueError('TOOL_ERROR')
                        value=response.structuredContent
                        if value is None:value=json.loads(next(c.text for c in response.content if c.type=='text'))
                        item['output']=value;trace.append(item);return value
                    ids=[]
                    for query in case['queries']:
                        hits=(await call('search_documents',{'query':query,'k':3}))['hits']
                        if not hits:
                            result={'status':'needs_review','issues':['SEARCH_EMPTY'],'evidence':[]};return init.protocolVersion
                        candidates=[fid for hit in hits for fid in hit['fact_ids']]
                        if len(set(candidates))!=1:
                            result={'status':'needs_review','issues':['AMBIGUOUS_FACT'],'evidence':[]};return init.protocolVersion
                        fid=candidates[0];await call('get_fact',{'fact_id':fid});ids.append(fid)
                    if case['operation']=='compare': result=await call('verify_comparison',{'current_id':ids[0],'base_id':ids[1],'mode':case['mode']})
                    else: result=await call('reconcile_quarter',{'ytd_id':ids[0],'previous_id':ids[1],'direct_id':ids[2]})
                    return init.protocolVersion
    protocol=None
    try: protocol=await asyncio.wait_for(execute(),timeout=25)
    except TimeoutError:result={'status':'needs_review','issues':['TOOL_TIMEOUT'],'evidence':[]}
    except Exception:result={'status':'needs_review','issues':['TOOL_ERROR'],'evidence':[]}
    return {'run_id':run_id,'case_id':case_id,'title':case['title'],'execution_mode':'live_mcp',
      'planner':'deterministic_workflow','workflow_success':protocol is not None and not any(x in result['issues'] for x in ('TOOL_ERROR','TOOL_TIMEOUT')),'protocol':protocol,'created_at':datetime.now(timezone.utc).isoformat(),
      'latency_ms':round((time.perf_counter()-start)*1000,3),'model_calls':0,'provider_api_cost_usd':0,
      'cost_scope':'No paid model API calls; hosting and local compute excluded','result':result,'trace':trace}
