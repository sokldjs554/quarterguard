"""Archived v8 replay and frozen synthetic sentences; no model or PDF calls."""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path
from quarterguard.store import ROOT
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    baseline=ROOT/'artifacts/prose-v8-fix-20261111/before-explanation_guards.py.txt'
    old={};exec(compile(baseline.read_text(),str(baseline),'exec'),old)
    frozen_path=ROOT/'data/prose-v8-fix-20261111/synthetic-cases.json'
    frozen=json.loads(frozen_path.read_text())
    source=ROOT/frozen['source']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=frozen['source_sha256']:
        raise ValueError('SOURCE_MISMATCH')
    rows=json.loads(source.read_text())['records'];original=copy.deepcopy(rows)
    human={r['case_id']:r['explanation_verdict'] for r in json.loads(
        (ROOT/'artifacts/human-prose-v8-20261111/review.json').read_text())['records']}
    def checks(answer,result):
        start=time.perf_counter()
        after=check_explanation(answer,result)|check_prose(answer,result)
        elapsed=round((time.perf_counter()-start)*1000,3)
        before=check_explanation(answer,result)|old['check_prose'](answer,result)
        return {'before_checks':before,'after_checks':after,'before_passed':all(before.values()),
                'after_passed':all(after.values()),'after_check_ms':elapsed}
    replay=[]
    for row in rows:
        replay.append({'case_id':row['case_id'],'original_response':row['generated'],
                       'b_v8_verdict_unchanged':human[row['case_id']],**checks(row['generated'],row['tool_result'])})
    assert rows==original
    actual={r['case_id']:r for r in rows};synthetic=[]
    for case in frozen['cases']:
        row=actual[case['source_case']]
        answer=row['generated']|{'explanation_ko':case['text']}
        checked=checks(answer,row['tool_result'])
        synthetic.append(case|checked|{
            'before_matches_expectation':checked['before_passed']==case['expected_product_pass'],
            'after_matches_expectation':checked['after_passed']==case['expected_product_pass']})
    report={'mode':'archived_v8_replay_and_AI_authored_synthetic_sentences',
            'new_paid_calls':0,'new_model_generations':0,'new_pdf_parsing':False,'new_human_reviews':0,
            'source_sha256':frozen['source_sha256'],
            'synthetic_freeze_sha256':hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
            'before_guard_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'after_guard_sha256':hashlib.sha256((ROOT/'quarterguard/explanation_guards.py').read_bytes()).hexdigest(),
            'replay':replay,'synthetic':synthetic,
            'replay_summary':{'total':len(replay),'before_passed':sum(r['before_passed'] for r in replay),'after_passed':sum(r['after_passed'] for r in replay)},
            'synthetic_summary':{'total':len(synthetic),'before_matched':sum(r['before_matches_expectation'] for r in synthetic),'after_matched':sum(r['after_matches_expectation'] for r in synthetic)},
            'limitations':['Known v8 cases were used in fixes. Replay is not a new generation.',
                'Additional synthetic cases were AI-authored before implementation, not independently human reviewed or blind.',
                'Direction grammar is bounded; no explicit pair does not establish semantic correctness.']}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['replay_summary','synthetic_summary','new_paid_calls']}))
    for row in replay:
        if not row['after_passed']:print(row['case_id'],[k for k,v in row['after_checks'].items() if not v])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
