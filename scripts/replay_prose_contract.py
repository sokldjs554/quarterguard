"""Recheck archived v6 outputs, never generate or change historical verdicts.

Run: python scripts/replay_prose_contract.py --output work/contract-replay.json
The output path must not exist. PDF/MCP/model calls: zero.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarterguard.store import ROOT
from quarterguard.live_verification import check_explanation
from quarterguard.explanation_guards import check_prose
from quarterguard.public_providers import build_payload
from quarterguard.evaluate_live_explanations_v6 import registry


def replay():
    source=ROOT/'artifacts/llm-prose-v6-20261110/report.json'
    original=json.loads(source.read_text())
    rows=[]
    for row in original['records']:
        answer,result=row['generated'],row['tool_result']
        checks=check_explanation(answer,result)|check_prose(answer,result)
        checks['schema_keys_exact']=set(answer)=={'status','value','issues','evidence_ids','explanation_ko'}
        with registry(row):payload=build_payload(result,'Archived response diagnostic, no generation')
        context=json.loads(payload['input'])['explanation_context']
        rows.append({'case_id':row['case_id'],'cohort':row['cohort'],
            'historical_checks':row['production_checks'],
            'replay_checks':checks,'replay_passed':all(checks.values()),
            'raw_value':answer['value'],
            'next_request_allowed_value':payload['text']['format']['schema']['properties']['value']['enum'],
            'decision_basis':context['decision_basis']})
    groups={}
    for cohort in ('paired_development','new_tasks_known_documents'):
        selected=[r for r in rows if r['cohort']==cohort]
        groups[cohort]={'total':len(selected),
            'historical_product_passed':sum(all(r['historical_checks'].values()) for r in selected),
            'current_replay_passed':sum(r['replay_passed'] for r in selected),
            'structured_value_failures':sum(not r['replay_checks']['value_exact'] for r in selected)}
    return {'mode':'saved_v6_responses_with_current_validator_and_payload_builder',
        'model_calls':0,'pdf_calls':0,'mcp_calls':0,'new_human_review':False,
        'source':str(source.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'current_code_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ('quarterguard/core.py','quarterguard/explanation_context.py',
                         'quarterguard/explanation_guards.py','quarterguard/public_providers.py')},
        'cohorts':groups,'records':rows,
        'limits':'Development replay on disclosed failures. Schema acceptance by hosted API and new model prose are untested; historical human verdicts and outputs unchanged.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=replay()
    with args.output.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(report['cohorts'],ensure_ascii=False))
