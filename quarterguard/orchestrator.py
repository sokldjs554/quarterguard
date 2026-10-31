"""Bounded, deterministic tool workflow. This is not an LLM planner."""
import asyncio, json, sys, time, uuid
from datetime import datetime,timezone
from decimal import Decimal, InvalidOperation
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from .store import ROOT
from .core import source_facts

_WORKFLOW_TIMEOUT_SECONDS = 25

def cases():return json.loads((ROOT/'data/cases.json').read_text())

def _result_shape(value):
    return (isinstance(value,dict) and value.get('status') in ('verified','needs_review')
      and isinstance(value.get('issues'),list) and all(isinstance(x,str) for x in value['issues'])
      and isinstance(value.get('evidence'),list)
      and all(isinstance(x,dict) for x in value['evidence'])
      and (value['status']=='needs_review')==bool(value['issues']))

def _finite_amount(value):
    if not isinstance(value,str):return False
    try:return Decimal(value).is_finite()
    except InvalidOperation:return False

def _valid_tool_output(name,args,value):
    if not isinstance(value,dict):return False
    canonical=source_facts()
    if name=='search_documents':
        hits=value.get('hits')
        return isinstance(hits,list) and all(isinstance(hit,dict)
          and isinstance(hit.get('fact_ids'),list) and bool(hit['fact_ids'])
          and all(isinstance(fid,str) and fid in canonical for fid in hit['fact_ids']) for hit in hits)
    if name=='get_fact':
        expected=canonical.get(args['fact_id'])
        return expected is not None and value==expected
    if name not in ('verify_comparison','reconcile_quarter') or not _result_shape(value):return False
    keys=('current_id','base_id') if name=='verify_comparison' else ('ytd_id','previous_id','direct_id')
    expected=[canonical.get(args[key]) for key in keys]
    if any(fact is None for fact in expected) or value['evidence']!=expected:return False
    if not isinstance(value.get('formula'),str) or not value['formula']:return False
    inputs=value.get('normalized_inputs')
    if not isinstance(inputs,list) or len(inputs)!=len(keys) or not all(_finite_amount(x) for x in inputs):return False
    value_keys=('growth_pct',) if name=='verify_comparison' else ('derived_value','difference')
    if any(key not in value or not (_finite_amount(value[key]) or
      (value[key] is None and value['status']=='needs_review')) for key in value_keys):return False
    return name!='verify_comparison' or (value.get('mode')==args['mode']
      and value.get('currency')==expected[0]['currency'])

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
                        t=time.perf_counter()
                        item={'step':len(trace)+1,'tool':name,'arguments':args,'success':False}
                        trace.append(item)
                        try:
                            try:
                                response=await session.call_tool(name,args)
                            except asyncio.CancelledError:
                                item['failure_type']='TOOL_TIMEOUT';raise
                            except Exception:
                                item['failure_type']='TOOL_TRANSPORT_ERROR';raise
                            if response.isError:
                                item['failure_type']='TOOL_ERROR';raise ValueError('TOOL_ERROR')
                            try:
                                value=response.structuredContent
                                if value is None:value=json.loads(next(c.text for c in response.content if c.type=='text'))
                                if not _valid_tool_output(name,args,value):raise ValueError('INVALID_TOOL_RESPONSE')
                            except Exception:
                                item['failure_type']='INVALID_TOOL_RESPONSE';raise
                            item['output']=value;item['success']=True;return value
                        finally:
                            item['latency_ms']=round((time.perf_counter()-t)*1000,3)
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
    try: protocol=await asyncio.wait_for(execute(),timeout=_WORKFLOW_TIMEOUT_SECONDS)
    except TimeoutError:result={'status':'needs_review','issues':['TOOL_TIMEOUT'],'evidence':[]}
    except Exception:result={'status':'needs_review','issues':['TOOL_ERROR'],'evidence':[]}
    if not _result_shape(result):
        protocol=None
        result={'status':'needs_review','issues':['TOOL_ERROR'],'evidence':[]}
    return {'run_id':run_id,'case_id':case_id,'title':case['title'],'execution_mode':'live_mcp',
      'planner':'deterministic_workflow','workflow_success':protocol is not None and not any(x in result['issues'] for x in ('TOOL_ERROR','TOOL_TIMEOUT')),'protocol':protocol,'created_at':datetime.now(timezone.utc).isoformat(),
      'latency_ms':round((time.perf_counter()-start)*1000,3),'model_calls':0,'provider_api_cost_usd':0,
      'cost_scope':'No paid model API calls; hosting and local compute excluded','result':result,'trace':trace}
