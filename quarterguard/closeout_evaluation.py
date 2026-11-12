"""One separately approved explanation-only batch; all 20 tool inputs replayed.

Preparation has no network or model calls. Execution preserves rejected raw
responses and blank human review fields; existing human labels are never reused.
"""
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
from .store import ROOT
from .completion_evaluation import (PaidClient, MODEL, now, dump, digest, explain,
                                    replay_payload, human_packet, replay_cases)
from .evaluate_live_explanations_v9 import registry
from .orchestrator import cases
from .public_providers import build_payload, ExplanationRejected

RAW = ROOT/'artifacts/model-completion-live-20261112/raw/completion-live/human-review.json'
FREEZE = ROOT/'data/closeout-evaluation-freeze-20261112.json'
CONTRACT = {
    'id':'final-closeout-explanations-20261112', 'model':MODEL,
    'max_calls':20, 'explanations':20, 'planner_calls':0, 'new_mcp_calls':0,
    'max_input_admission_tokens':16000, 'max_output_tokens':700, 'retries':0,
    'input_admission':'Entire payload UTF8 bytes + 1024 framing reserve; conservative admission, not a provider token-limit parameter.',
    'input_usd_per_million':'0.4', 'output_usd_per_million':'1.6',
    'estimated_max_usd':'0.15040', 'approval_budget_usd':'0.16', 'billed_cost_usd':None,
    'pricing_url':'https://developers.openai.com/api/docs/models/gpt-4.1-mini',
    'pricing_checked':'2026-11-12',
    'lifecycle':'Deprecated model; stop on unavailability, no substitution or retry.',
    'sampling':'Same 20 development cases and stored tool inputs as prior completion batch; no new documents or holdout.',
}


class CloseoutClient(PaidClient):
    CONTRACT=CONTRACT
    CONTRACT_ID=CONTRACT['id']
    MAX_CALLS=20
    WORKFLOW='closeout-explanations.yml'


def prepared_cases():
    frozen={r['id']:r for r in replay_cases()}
    live={r['id']:r for r in cases()}
    records=json.loads(RAW.read_text())
    if len(records)!=20 or len({r['case_id'] for r in records})!=20:raise ValueError('CASE_SET_MISMATCH')
    out=[]
    for row in records:
        cid=row['case_id']
        case=frozen.get(cid.removeprefix('replay-')) if cid.startswith('replay-') else None
        if case:
            if case['tool_result']!=row['tool_result']:raise ValueError('TOOL_INPUT_CHANGED')
            payload=replay_payload(case)
        else:payload=build_payload(row['tool_result'],live[cid]['description'])
        size=len(json.dumps(payload,ensure_ascii=False).encode())+1024
        if size>16000:raise ValueError('INPUT_ADMISSION_LIMIT')
        out.append({'case_id':cid,'source_execution':'stored_tool_result',
                    'tool_result':row['tool_result'],'payload':payload,'input_admission_bytes':size})
    return out


def prepare():
    paths=[*sorted((ROOT/'quarterguard').glob('*.py')),RAW,
           ROOT/'data/facts.json',ROOT/'data/sources.json',ROOT/'data/cases.json',
           ROOT/'data/llm-prose-v9-20261111/freeze.json',ROOT/'data/llm-prose-v6-20261110/new-inputs.json',
           ROOT/'.github/workflows/closeout-explanations.yml']
    value={'contract':CONTRACT,'cases':prepared_cases(),
           'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    return value|{'sha256':digest(value)}


def execute(output, approved_sha):
    frozen=json.loads(FREEZE.read_text())
    if approved_sha!=frozen['sha256'] or prepare()!=frozen:raise ValueError('APPROVAL_OR_FREEZE_MISMATCH')
    client=CloseoutClient(output,ROOT/'work/closeout-paid-ledger',approved=True)
    output=Path(output)
    report={'at':now(),'contract':CONTRACT,'freeze_sha256':approved_sha,
            'human_reviewed':False,'new_mcp_runs':0,'new_pdf_parses':0,'explanations':[]}
    registries={r['id']:r for r in replay_cases()}
    try:
        for item in frozen['cases']:
            cid=item['case_id'];case=registries.get(cid.removeprefix('replay-')) if cid.startswith('replay-') else None
            row={k:item[k] for k in ('case_id','source_execution','tool_result')}
            row['generation']='not_attempted_after_provider_failure'
            if not client.stopped:
                row['response_file']=f'response-{client.attempts+1:02}.json'
                with registry(case) if case else nullcontext():
                    try:row.update(generation='completed',output=explain(client,item['tool_result'],'',payload=item['payload']))
                    except ExplanationRejected as error:row.update(generation='rejected',checks=error.checks)
                    except Exception:row['generation']='provider_failed_or_rejected'
            report['explanations'].append(row)
            dump(output/'report.json',report)
    finally:
        from decimal import Decimal
        report.update(calls_attempted=client.attempts,usage=client.usage,billed_cost_usd=None,
            estimated_cost_usd=str(sum((Decimal(r['estimated_cost_usd']) for r in client.usage if r.get('estimated_cost_usd') is not None),Decimal(0))),
            unknown_cost_attempts=sum(r.get('estimated_cost_usd') is None for r in client.usage))
        dump(output/'report.json',report)
        dump(output/'human-review.json',human_packet(report,output))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--execute-approved',action='store_true')
    parser.add_argument('--approved-sha256')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.prepare:
        with args.output.open('x') as target:json.dump(prepare(),target,ensure_ascii=False,indent=2)
    elif args.execute_approved and args.approved_sha256:execute(args.output,args.approved_sha256)
    else:raise ValueError('EXPLICIT_APPROVAL_REQUIRED')
