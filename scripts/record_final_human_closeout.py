"""Offline comparison of immutable N01–N20 responses and submitted human rows."""
import argparse
from collections import Counter
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from quarterguard.evaluate_live_explanations_v9 import registry
from quarterguard.explanation_guards import check_prose,check_grounding
from quarterguard.live_verification import check_explanation


def evaluate():
    paths=['artifacts/closeout-live-20261112/raw/closeout-live/human-review.json',
           'artifacts/closeout-live-20261112/summary.json',
           'docs/validation-kit/final-human-closeout-20261113/review.json',
           'data/llm-prose-v9-20261111/freeze.json','quarterguard/explanation_guards.py']
    raw,old,human,freeze=[json.loads((ROOT/p).read_text()) for p in paths[:4]]
    before={r['case_id']:r for r in old['rows']};labels={r['case_id']:r for r in human['rows']}
    frozen={r['id']:r for r in freeze['cases']}
    assert len(raw)==len(before)==len(labels)==20
    assert {r['case_id'] for r in raw}==set(before)==set(labels)
    rows=[]
    for record in raw:
        cid=record['case_id'];case=frozen.get(cid.removeprefix('replay-')) if cid.startswith('replay-') else None
        with registry(case) if case else nullcontext():
            checks=check_explanation(record['raw_generated'],record['tool_result'])|check_prose(record['raw_generated'],record['tool_result'])|check_grounding(record['raw_generated'],record['tool_result'])
        rows.append({'review_id':labels[cid]['review_id'],'case_id':cid,'human_verdict':labels[cid]['explanation_verdict'],
                     'execution_gate_passed':before[cid]['product_passed'],'current_gate_passed':all(checks.values()),
                     'checks':checks,'failed_checks':[k for k,v in checks.items() if not v]})
    def counts(key,passed):return dict(Counter(r['human_verdict'] for r in rows if r[key]==passed))
    return {'mode':'offline_replay_after_submitted_human_review','new_paid_calls':0,'new_mcp_runs':0,'new_pdf_parses':0,
            'new_ai_authored_human_verdicts':0,'raw_responses_rewritten':False,'new_generation_after_conclusion_guard':False,
            'sample_role':'known development cases, existing reviewer b; not blind independent evaluation',
            'human_counts':dict(Counter(r['human_verdict'] for r in rows)),
            'before':{'passed':sum(r['execution_gate_passed'] for r in rows),'accepted_by_human':counts('execution_gate_passed',True),'withheld_by_human':counts('execution_gate_passed',False)},
            'after':{'passed':sum(r['current_gate_passed'] for r in rows),'accepted_by_human':counts('current_gate_passed',True),'withheld_by_human':counts('current_gate_passed',False)},
            'rows':rows,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=evaluate()
    with args.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ('human_counts','before','after','new_paid_calls')},ensure_ascii=False))
