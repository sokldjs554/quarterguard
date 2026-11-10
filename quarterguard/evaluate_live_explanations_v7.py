"""Approval-gated v7: same v6 development16, paired before/after.

No production policy changes, no retries, no human verdicts. The v6 source
registry is reused only for evaluation; no new documents or gold are introduced.
"""
import argparse
from contextlib import contextmanager, ExitStack
import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import time
from unittest.mock import patch
import httpx
from .store import ROOT
from . import evaluate_live_explanations_v5 as previous
from .public_providers import build_payload
from .provider_controls import Blocked
from .live_verification import SCHEMA, check_explanation
from .explanation_guards import check_prose
from .core import Fact

DATA=ROOT/'data/llm-prose-v7-20261110'
REGISTRY_DATA=ROOT/'data/llm-prose-v6-20261110'
BASELINE=ROOT/'artifacts/llm-prose-v6-20261110/report.json'
PREVIOUS_FREEZE=ROOT/'data/llm-prose-v6-20261110/freeze.json'
MODEL='gpt-5.4-mini-2026-03-17'
CONTRACT={'model':MODEL,'reasoning_effort':'none','max_requests':16,
    'max_input_admission_tokens':8500,'max_output_tokens':700,'retries':0,'timeout_seconds':60,
    'input_counter':'entire serialized request UTF-8 bytes + 1024 framing reserve; not API hard input cap',
    'input_usd_per_million':'0.75','output_usd_per_million':'4.50',
    'estimated_max_cost_usd':'0.1524','approval_budget_usd_before_tax':'0.16',
    'pricing_url':'https://developers.openai.com/api/docs/models/gpt-5.4-mini',
    'pricing_checked_date':'2026-11-10','billed_cost_usd':None}
EXTRA_SOURCES=('quarterguard/evaluate_live_explanations_v7.py','quarterguard/explanation_guards.py',
    'scripts/prepare_prose_v6_sources.py','.github/workflows/live-explanations-v7.yml',
    'data/llm-prose-v6-20261110/new-inputs.json','data/llm-prose-v6-20261110/freeze.json',
    'artifacts/llm-prose-v6-20261110/report.json')
digest=previous.digest
now=previous.now
input_admission_bound=previous.input_admission_bound


def source_hashes():
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
            for p in dict.fromkeys((*previous.SOURCE_FILES,*EXTRA_SOURCES))}


@contextmanager
def registry(case):
    with ExitStack() as stack:
        if case['cohort']=='new_tasks_known_documents':
            data=json.loads((REGISTRY_DATA/'new-inputs.json').read_text())
            manifest={s['id']:s for s in data['sources']}
            facts={key:Fact(**row).public() for key,row in data['facts'].items()}
            for module in ('core','explanation_context'):
                stack.enter_context(patch(f'quarterguard.{module}.source_facts',return_value=facts))
                stack.enter_context(patch(f'quarterguard.{module}.source_manifest',return_value=manifest))
        yield


def make_payload(case):
    try:
        with registry(case):payload=build_payload(case['tool_result'],case['task'])
    except Blocked:
        raise ValueError('INPUT_ADMISSION_LIMIT') from None
    payload['model']=MODEL;payload['reasoning']={'effort':'none'}
    if case.get('untrusted_draft'):
        data=json.loads(payload['input'])
        data.update(untrusted_draft=case['untrusted_draft'],
                    draft_origin='authored synthetic misleading claim; not source evidence')
        payload['input']=json.dumps(data,ensure_ascii=False)
    if input_admission_bound(payload)>CONTRACT['max_input_admission_tokens']:
        raise ValueError('INPUT_ADMISSION_LIMIT')
    return payload


def cases():
    old=json.loads(PREVIOUS_FREEZE.read_text())
    if digest({k:v for k,v in old.items() if k!='content_sha256'})!=old['content_sha256']:
        raise ValueError('BASELINE_FREEZE_CONTENT_MISMATCH')
    rows=copy.deepcopy(old['cases'])
    baseline=json.loads(BASELINE.read_text())
    if baseline['freeze_sha256']!=old['content_sha256']:
        raise ValueError('BASELINE_REPORT_MISMATCH')
    responses={r['case_id']:r for r in baseline['records'] if r['status']=='completed'}
    if len(rows)!=16 or len({c['id'] for c in rows})!=16 or len(responses)!=16:
        raise ValueError('CASE_COUNT_MISMATCH')
    for c in rows:
        if c['tool_result']!=responses[c['id']]['tool_result']:
            raise ValueError('PAIRED_INPUT_MISMATCH')
        payload=make_payload(c)
        c['payload_sha256']=digest(payload)
        c['input_admission_tokens']=input_admission_bound(payload)
    return rows


def prepare_freeze():
    frozen={'version':7,'frozen_at':now(),'contract':CONTRACT,'source_hashes':source_hashes(),
        'cases':cases(),'new_model_calls':0,'human_reviewed':False,'semantic_certified':False,
        'sampling':'Same v6 development16, two historical groups of8; all disclosed and used in fixes, no new holdout.',
        'source_execution':'Replay v6 frozen tool results for all16. No new PDF parsing, MCP run or user review in this batch.',
        'production_corpus_modified':False}
    frozen['content_sha256']=digest(frozen)
    return frozen


def validate_freeze(frozen):
    if digest({k:v for k,v in frozen.items() if k!='content_sha256'})!=frozen.get('content_sha256'):
        raise ValueError('FREEZE_CONTENT_MISMATCH')
    if frozen['source_hashes']!=source_hashes() or frozen['contract']!=CONTRACT:
        raise ValueError('FREEZE_CODE_MISMATCH')
    if frozen['cases']!=cases():raise ValueError('FROZEN_CASES_MISMATCH')


def checks(answer,case):
    with registry(case):
        audit=previous.audit(answer,case)
    product=check_explanation(answer,case['tool_result'])|check_prose(answer,case['tool_result'])
    product['schema_keys_exact']=set(answer)==set(SCHEMA['required'])
    return audit,product


def write(path,data):
    # Output directory is exclusively created; only this run's evolving report is updated.
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def compare_paired(report,frozen):
    before={r['case_id']:r for r in json.loads(BASELINE.read_text())['records']}
    after={r['case_id']:r for r in report['records'] if r['status']=='completed'}
    pairs=[]
    for case in frozen['cases']:
        old=before[case['id']];new=after.get(case['id'])
        if old['tool_result']!=case['tool_result']:raise ValueError('PAIRED_INPUT_MISMATCH')
        old_audit,old_checks=checks(old['generated'],case)
        pairs.append({'case_id':case['id'],'cohort':case['cohort'],
            'before_historical_gate':old['production_checks'],'before_generated':old['generated'],
            'after_generated':new['generated'] if new else None,'before_same_current_gate':old_checks,
            'after_same_current_gate':new['production_checks'] if new else None,
            'before_same_current_audit':old_audit,'after_same_current_audit':new['audit'] if new else None,
            'new_human_verdict':None})
    return {'scope':'all16 paired with v6; retain original two groups but neither is a new holdout',
            'semantic_accuracy':None,'human_reviewed':False,'pairs':pairs}


def execute(frozen,output,*,approved=False):
    if not approved:raise ValueError('EXPLICIT_APPROVAL_REQUIRED')
    output=Path(output)
    if output.exists():raise ValueError('OUTPUT_ALREADY_EXISTS')
    validate_freeze(frozen)
    key=os.environ.get('OPENAI_API_KEY')
    if not key:raise ValueError('OPENAI_NOT_CONFIGURED')
    output.mkdir(parents=True,exist_ok=False)
    report={'created_at':now(),'status':'running','contract':CONTRACT,'freeze_sha256':frozen['content_sha256'],
            'execution_mode':'real_provider_responses','calls_attempted':0,'records':[],
            'human_reviewed':False,'semantic_certified':False,'billed_cost_usd':None,
            'source_execution':frozen['source_execution']}
    with (output/'attempts.jsonl').open('x') as journal:
        for case in frozen['cases']:
            payload=make_payload(case)
            row={'case_id':case['id'],'cohort':case['cohort'],'attempt':report['calls_attempted']+1,
                 'started_at':now(),'status':'started'}
            journal.write(json.dumps(row)+'\n');journal.flush();os.fsync(journal.fileno())
            report['calls_attempted']+=1;start=time.perf_counter();failure=None
            try:
                response=httpx.post('https://api.openai.com/v1/responses',json=payload,
                    headers={'Authorization':'Bearer '+key},timeout=CONTRACT['timeout_seconds'])
                if response.status_code!=200:failure=f'OPENAI_HTTP_{response.status_code}'
                else:
                    raw=previous.sanitized_response(response.json())
                    raw=json.loads(json.dumps(raw,ensure_ascii=False).replace(key,'[REDACTED]'))
                    write(output/(case['id']+'.response.json'),raw)
                    i,o=raw['usage']['input_tokens'],raw['usage']['output_tokens']
                    if type(i) is not int or type(o) is not int or min(i,o)<0:raise ValueError()
                    row['usage']={'input_tokens':i,'output_tokens':o,
                        'estimated_cost_usd':str((Decimal(i)*Decimal('.75')+Decimal(o)*Decimal('4.50'))/1000000)}
                    if i>8500 or o>700:failure='USAGE_LIMIT_EXCEEDED'
                    elif raw['model']!=MODEL:failure='MODEL_MISMATCH'
                    elif raw['status']!='completed':failure='OPENAI_INCOMPLETE'
                    else:
                        answer=json.loads(raw['output_text'])
                        if not isinstance(answer,dict):raise ValueError()
                        audit,product=checks(answer,case)
                        row.update(generated=answer,tool_result=case['tool_result'],audit=audit,
                                   production_checks=product,production_gate_passed=all(product.values()))
            except httpx.HTTPError:failure='OPENAI_CONNECTION_FAILED'
            except Exception:failure='OPENAI_INVALID_RESPONSE'
            row.update(latency_ms=round((time.perf_counter()-start)*1000,3),finished_at=now(),
                       status='failed' if failure else 'completed')
            if failure:row['failure_code']=failure
            report['records'].append(row)
            journal.write(json.dumps({k:row[k] for k in ('case_id','attempt','status','finished_at')})+'\n')
            journal.flush();os.fsync(journal.fileno());write(output/'report.json',report)
            if failure:break
    done=[r for r in report['records'] if r['status']=='completed']
    report.update(status='completed' if len(done)==16 else 'failed',generated_count=len(done),
        measured_input_tokens=sum(r.get('usage',{}).get('input_tokens',0) for r in report['records']),
        measured_output_tokens=sum(r.get('usage',{}).get('output_tokens',0) for r in report['records']),
        usage_estimated_cost_usd=str(sum((Decimal(r.get('usage',{}).get('estimated_cost_usd','0')) for r in report['records']),Decimal(0))),
        unmeasured_failed_attempts=sum('usage' not in r for r in report['records']))
    report['cohorts']={}
    for cohort in ('paired_development','new_tasks_known_documents'):
        rows=[r for r in done if r['cohort']==cohort]
        report['cohorts'][cohort]={'planned':8,'generated':len(rows),
            'structured_exact':sum(all(r['audit']['structured_checks'].values()) for r in rows),
            'production_gate_passed':sum(r['production_gate_passed'] for r in rows),
            'automatic_flagged':sum(bool(r['audit']['issues']) for r in rows),'semantic_accuracy':None}
    report['limitations']=['All16 are disclosed development cases from v6 and used in fixes; no new independent cases.',
        'Rule flags and product acceptance are not human semantic judgments.',
        'Evaluation GPT-5.4 mini differs from public production GPT-4.1 mini.',
        'Isolated registry for new documents is not production corpus support or MCP execution.',
        'Usage-based estimates exclude unmeasured failures/tax; actual billing not queried.']
    write(output/'report.json',report)
    write(output/'comparison.json',compare_paired(report,frozen))
    write(output/'human-review.json',[{'case_id':r['case_id'],'cohort':r['cohort'],
        'generated':r['generated'],'tool_result':r['tool_result'],'automatic_checks':r['production_checks'],
        'reviewer':None,'reviewed_at':None,'verdict':None,'structured_fields_match':None,
        'evidence_ids_match':None,'notes':None}
        for r in done])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--execute-approved',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'work/llm-prose-v7-20261110')
    args=parser.parse_args()
    if args.prepare:
        if args.execute_approved:raise ValueError('PREPARE_EXECUTE_SEPARATE')
        frozen=prepare_freeze()
        with (DATA/'freeze.json').open('x') as f:json.dump(frozen,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({'cases':16,'paid_calls':0,'freeze_sha256':frozen['content_sha256'],
                         'max_input_admission':max(c['input_admission_tokens'] for c in frozen['cases'])}))
    else:
        report=execute(json.loads((DATA/'freeze.json').read_text()),args.output,approved=args.execute_approved)
        print(json.dumps({k:report[k] for k in ('status','calls_attempted','usage_estimated_cost_usd')}))
        if report['status']!='completed':raise SystemExit(1)


if __name__=='__main__':main()
