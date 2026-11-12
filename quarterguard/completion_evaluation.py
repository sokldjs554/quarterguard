"""One approved production-model batch: live MCP -> production explanation;
experimental LLM selection -> real MCP. Never silently retries or overwrites.
"""
import argparse, asyncio, hashlib, json, os, sys, threading, time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .store import ROOT
from .live_verification import MODEL, CASE_IDS
from .public_providers import build_payload, generate_public, ExplanationRejected
from .orchestrator import run_case, cases
from . import bounded_planner
from .evaluate_live_explanations_v9 import registry as replay_registry
from .live_verification import check_explanation
from .explanation_guards import check_prose, check_grounding

MAX_CALLS=52
CONTRACT_ID='model-completion-20261112'
PLANNER_IDS=('qoq-revenue','ytd-trap','scope-trap','no-evidence')
CONTRACT={'id':CONTRACT_ID,'model':MODEL,'explanations':20, 'live_mcp_explanations':4, 'replayed_explanations':16,'planner_tasks':4,
 'max_planner_decisions_per_task':8,'max_calls':MAX_CALLS,'max_input_admission_tokens':16000,
 'input_admission':'serialized entire payload UTF8 bytes + 1024 framing reserve; conservative admission, not provider hard input cap',
 'max_output_tokens':700,'retries':0,'input_usd_per_million':'0.4','output_usd_per_million':'1.6',
 'estimated_max_usd':'0.39104','approval_budget_usd':'0.40','billed_cost_usd':None,
 'pricing_url':'https://developers.openai.com/api/docs/models/gpt-4.1-mini','pricing_checked':'2026-11-12',
 'model_lifecycle':'Official model page marks deprecated; do not substitute or retry if unavailable.'}

def now():return datetime.now(timezone.utc).isoformat()
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def replay_cases():
    return json.loads((ROOT/'data/llm-prose-v9-20261111/freeze.json').read_text())['cases']
def source_hashes():
    paths=list((ROOT/'quarterguard').glob('*.py'))+[ROOT/'data/facts.json',ROOT/'data/sources.json',ROOT/'data/cases.json',ROOT/'data/llm-prose-v9-20261111/freeze.json',ROOT/'data/llm-prose-v6-20261110/new-inputs.json',ROOT/'artifacts/llm-prose-v9-20261111/report.json',ROOT/'.github/workflows/completion-evaluation.yml']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def freeze():
    d={'contract':CONTRACT,'sources':source_hashes(),'explanation_cases':list(CASE_IDS), 'replayed_cases':replay_cases(),'planner_cases':list(PLANNER_IDS)}
    return d|{'sha256':digest(d)}

class PaidClient:
    def __init__(self,output,ledger,*,approved=False,transport=None):
        if not approved:raise ValueError('APPROVAL_REQUIRED')
        if transport is None and not (os.getenv('GITHUB_ACTIONS')=='true' and os.getenv('GITHUB_REPOSITORY')=='sokldjs554/quarterguard' and os.getenv('GITHUB_RUN_ATTEMPT')=='1' and os.getenv('GITHUB_WORKFLOW_REF')=='sokldjs554/quarterguard/.github/workflows/completion-evaluation.yml@refs/heads/main'):
            raise ValueError('AUTHORIZED_WORKFLOW_REQUIRED')
        self.output=Path(output);self.ledger=Path(ledger);self.ledger.mkdir(parents=True,exist_ok=True)
        # Fixed contract identity, not output path. Exclusive marker remains on any failure.
        with (self.ledger/(CONTRACT_ID+'.json')).open('x') as f:
            json.dump({'reserved_at':now(),'output':str(self.output),'contract':CONTRACT},f);f.flush();os.fsync(f.fileno())
        self.output.mkdir(parents=True,exist_ok=False)
        self.attempts=0;self.lock=threading.Lock();self.transport=transport;self.usage=[];self.stopped=False
    def post(self,url,*,json,**unused):
        payload=json
        if url!='https://api.openai.com/v1/responses':raise ValueError('DESTINATION')
        if payload.get('model')!=MODEL or payload.get('max_output_tokens')!=700:raise ValueError('MODEL_OR_OUTPUT_CONTRACT')
        if len(__import__('json').dumps(payload,ensure_ascii=False).encode())+1024>16000:raise ValueError('INPUT_ADMISSION_LIMIT')
        with self.lock:
            if self.stopped:raise ValueError('BATCH_STOPPED')
            if self.attempts>=MAX_CALLS:raise ValueError('CALL_LIMIT')
            self.attempts+=1;n=self.attempts
            dump(self.output/f'request-{n:02}.json',{'at':now(),'payload':payload,'sha256':digest(payload)})
            with (self.ledger/(CONTRACT_ID+'.attempts.jsonl')).open('a') as f:
                f.write(__import__('json').dumps({'attempt':n,'reserved_at':now(),'payload_sha256':digest(payload)})+'\n');f.flush();os.fsync(f.fileno())
        started=time.perf_counter()
        try:
            if self.transport:r=self.transport(payload)
            else:
                with httpx.Client(timeout=30) as client:
                    r=client.post(url,headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},json=payload)
            # Non-200 bodies may contain echoed secrets; persist only status, not arbitrary error text.
            body=r.json() if r.status_code==200 else {'http_status':r.status_code}
            if r.status_code!=200:self.stopped=True
            dump(self.output/f'response-{n:02}.json',body)
            usage=body.get('usage',{})
            inp,out=usage.get('input_tokens'),usage.get('output_tokens')
            self.usage.append({'attempt':n,'http_status':r.status_code,'input_tokens':inp,'output_tokens':out,
             'estimated_cost_usd':str((Decimal(inp)*Decimal('.4')+Decimal(out)*Decimal('1.6'))/1000000) if type(inp) is int and type(out) is int and min(inp,out)>=0 else None,
             'latency_ms':(time.perf_counter()-started)*1000})
            return r
        except Exception:
            self.stopped=True
            self.usage.append({'attempt':n,'status':'transport_or_decode_failed','estimated_cost_usd':None})
            raise
        finally:dump(self.output/'usage.json',self.usage)

def explain(client,result,title,*,payload=None):
    # Execute the public validator itself: exact keys, provider status, model,
    # usage types, structured checks and prose checks stay identical.
    with patch('quarterguard.public_providers.httpx.post',client.post):
        return generate_public(payload if payload is not None else build_payload(result,title),result)

def replay_payload(case):
    with replay_registry(case):payload=build_payload(case['tool_result'],case['task'])
    if case.get('untrusted_draft'):
        data=json.loads(payload['input'])
        data.update(untrusted_draft=case['untrusted_draft'], draft_origin='Synthetic misleading draft, not evidence.')
        payload['input']=json.dumps(data,ensure_ascii=False)
    if len(json.dumps(payload,ensure_ascii=False).encode())+1024>16000:raise ValueError('INPUT_ADMISSION_LIMIT')
    return payload

def human_packet(report, output):
    """Read raw successful HTTP responses even when the product gate rejected them."""
    rows=[]
    for row in report['explanations']:
        answer=None
        if row.get('response_file') and (output/row['response_file']).exists():
            body=json.loads((output/row['response_file']).read_text())
            try:
                answer=json.loads(''.join(c['text'] for m in body.get('output',[]) if m.get('type')=='message'
                    for c in m.get('content',[]) if c.get('type')=='output_text'))
            except (KeyError,ValueError,TypeError):pass
        rows.append({'case_id':row['case_id'],'source_execution':row['source_execution'],
                     'tool_result':row['tool_result'],'raw_generated':answer,
                     'generation':row['generation'],'human_verdict':None,'reviewer':None,
                     'structured_fields_match':None,'citations_match':None,'notes':None})
    return rows

def parse_action(body):
    if body.get('model')!=MODEL or body.get('status')!='completed':raise ValueError('INVALID_PROVIDER_RESPONSE')
    usage=body.get('usage',{})
    if any(type(usage.get(k)) is not int or usage[k]<0 for k in ('input_tokens','output_tokens')):raise ValueError('INVALID_USAGE')
    items=body.get('output',[])
    if len(items)!=1 or items[0].get('type')!='function_call':raise ValueError('EXACTLY_ONE_TOOL_REQUIRED')
    item=items[0]
    return {'tool':item['name'],'arguments':json.loads(item['arguments'])}

async def live_plan(case,choose):
    async def inner():
        with (ROOT/'work').joinpath('final-planner-stderr.log').open('a') as log:
            async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.mcp_server'],cwd=str(ROOT)),errlog=log) as (r,w):
                async with ClientSession(r,w) as session:
                    init=await session.initialize()
                    async def call(name,args):
                        response=await session.call_tool(name,args)
                        if response.isError:raise ValueError('MCP_ERROR')
                        return response.structuredContent if response.structuredContent is not None else json.loads(next(c.text for c in response.content if c.type=='text'))
                    return (await bounded_planner.run(case['queries'],case['mode'],choose,call))|{'mcp_protocol':init.protocolVersion}
    # Stop planning at 90s; allow the in-flight HTTP call to finish recording
    # usage (30s timeout) before finalizing the audit. No new decision is made.
    try:return await asyncio.wait_for(inner(),140)
    except Exception:return {'result':None,'failure':'MCP_SESSION_FAILED_OR_TIMEOUT','trace':[]}

def matches_public_preflight(case,result):
    """Same case-gold admission as public_providers.execute, before paid spend."""
    return (result['status']==case['expected_status'] and result['evidence']==case['expected_evidence']
      and ('expected_value' not in case or result.get('growth_pct',result.get('derived_value'))==case['expected_value'])
      and ('expected_issue' not in case or case['expected_issue'] in result['issues']))

async def execute(output,*,approved=False,dry=False):
    registry={c['id']:c for c in cases()}
    output=Path(output)
    if dry:output.mkdir(parents=True,exist_ok=False);client=None
    else:client=PaidClient(output,ROOT/'work/completion-paid-ledger',approved=approved)
    report={'at':now(),'contract':CONTRACT,'source_hashes':source_hashes(),'explanations':[],'planner':[],
      'paid':not dry,'human_reviewed':False,'source_execution':'4 live MCP explanations; 16 frozen v9 tool-result replays; 4 actual MCP planner tasks. No new raw PDF parsing.',
      'sampling':'All20 known development cases. Replay16 used GPT-5.4 mini before, now production GPT-4.1 mini: not a prompt-only comparison. Scripted dry-run choices are not model planning.'}
    try:
        for cid in CASE_IDS:
            case=registry[cid];run=await run_case(cid)
            row={'case_id':cid,'mcp':run,'generation':'not_run','tool_result':run['result'],
                 'source_execution':'live_mcp_registered_facts'}
            if run['workflow_success'] and matches_public_preflight(case,run['result']):
                payload=build_payload(run['result'],case['description']);row['payload_sha256']=digest(payload)
                if client:
                    row['response_file']=f'response-{client.attempts+1:02}.json'
                    try:row.update(generation='completed',output=explain(client,run['result'],case['description']))
                    except ExplanationRejected as e:row.update(generation='rejected',checks=e.checks)
                    except Exception:row['generation']='provider_failed_or_rejected'
            if row['generation']=='not_run' and (not run['workflow_success'] or not matches_public_preflight(case,run['result'])):row['generation']='blocked_preflight'
            report['explanations'].append(row);dump(output/'report.json',report)
        baseline={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-prose-v9-20261111/report.json').read_text())['records']}
        for case in replay_cases():
            payload=replay_payload(case)
            row={'case_id':'replay-'+case['id'],'generation':'not_run','tool_result':case['tool_result'],
                 'source_execution':'frozen_v9_tool_result_replay','previous_model':'gpt-5.4-mini-2026-03-17',
                 'previous_generated':baseline[case['id']]['generated'],'payload_sha256':digest(payload)}
            with replay_registry(case):
                row['previous_response_current_checks']=check_explanation(row['previous_generated'],case['tool_result'])|check_prose(row['previous_generated'],case['tool_result'])|check_grounding(row['previous_generated'],case['tool_result'])
                if client:
                    row['response_file']=f'response-{client.attempts+1:02}.json'
                    try:row.update(generation='completed',output=explain(client,case['tool_result'],case['task'],payload=payload))
                    except ExplanationRejected as e:row.update(generation='rejected',checks=e.checks)
                    except Exception:row['generation']='provider_failed_or_rejected'
            report['explanations'].append(row);dump(output/'report.json',report)
        for cid in PLANNER_IDS:
            case=registry[cid]
            baseline=await run_case(cid)
            if client:
                async def choose(payload):
                    pending=asyncio.create_task(asyncio.to_thread(client.post,'https://api.openai.com/v1/responses',json=payload))
                    try:response=await asyncio.shield(pending)
                    except asyncio.CancelledError:
                        try:await pending
                        except Exception:pass
                        raise
                    if response.status_code!=200:raise ValueError('PROVIDER_HTTP_ERROR')
                    return parse_action(response.json())
            else:
                async def choose(payload):
                    # Deterministic test driver, explicitly not actual LLM decisions.
                    state=json.loads(payload['input']);trace=state['previous_steps'];queries=state['queries']
                    searches={x['arguments']['query']:x['output'] for x in trace if x['tool']=='search_documents' and x['success']}
                    for q in queries:
                        if q not in searches:return {'tool':'search_documents','arguments':{'query':q}}
                    ids=[searches[q]['hits'][0]['fact_ids'][0] for q in queries]
                    if cid=='scope-trap' and not any(x['tool']=='verify_comparison' for x in trace):
                        # Deliberate omission only in the scripted free test.
                        return {'tool':'verify_comparison','arguments':{'current_id':ids[0],'base_id':ids[1],'mode':state['mode']}}
                    read={x['arguments']['fact_id'] for x in trace if x['tool']=='get_fact' and x['success']}
                    for fid in ids:
                        if fid not in read:return {'tool':'get_fact','arguments':{'fact_id':fid}}
                    return {'tool':'verify_comparison','arguments':{'current_id':ids[0],'base_id':ids[1],'mode':state['mode']}}
            planned=await live_plan(case,choose)
            row={'case_id':cid,'decision_source':'scripted_test_policy' if dry else 'actual_llm_function_calls',
                 'baseline':baseline,'planned':planned,'same_result':planned.get('result')==baseline['result']}
            # Early search-empty hold carries a null growth field; compare semantic contract only.
            if cid=='no-evidence' and planned.get('result'):
                row['same_result']=all(planned['result'].get(k)==baseline['result'].get(k) for k in ('status','issues','evidence','growth_pct'))
            report['planner'].append(row);dump(output/'report.json',report)
    finally:
        report['calls_attempted']=client.attempts if client else 0
        report['usage']=client.usage if client else []
        report['billed_cost_usd']=None
        report['measured_cost_usd']=str(sum((Decimal(r['estimated_cost_usd']) for r in report['usage'] if r.get('estimated_cost_usd') is not None),Decimal(0)))
        report['unknown_cost_attempts']=sum(r.get('estimated_cost_usd') is None for r in report['usage'])
        dump(output/'report.json',report)
        dump(output/'human-review.json',human_packet(report,output))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--execute-approved',action='store_true');p.add_argument('--freeze',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--approved-sha256');a=p.parse_args()
    if a.freeze:
        with a.output.open('x') as f:json.dump(freeze(),f,ensure_ascii=False,indent=2)
        return
    if not a.dry_run:
        frozen=json.loads((ROOT/'data/completion-evaluation-freeze.json').read_text())
        if not a.execute_approved or a.approved_sha256!=frozen['sha256'] or freeze()!=frozen:raise ValueError('APPROVAL_OR_FREEZE_MISMATCH')
    asyncio.run(execute(a.output,approved=a.execute_approved,dry=a.dry_run))
if __name__=='__main__':main()
