"""Free new-query evaluation and archived-response replay; never calls a provider.

Run with a NEW output directory. The first-run artifacts remain immutable.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
from quarterguard.store import ROOT
from quarterguard.core import Fact
from quarterguard.search import SearchIndex
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation
from quarterguard.evaluate_live_explanations_v8 import registry


def run(output):
    freeze_path=ROOT/'data/plain-language-v8-20261111/new-queries.json'
    frozen=json.loads(freeze_path.read_text())
    for path,sha in frozen['code_sha256'].items() | {frozen['source']:frozen['source_sha256']}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:
            raise ValueError('FROZEN_SOURCE_MISMATCH')
    data=json.loads((ROOT/frozen['source']).read_text())
    facts=[Fact(**f) for f in data['facts'].values()]
    index=SearchIndex(facts)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for case in frozen['cases']:
        start=time.perf_counter();actual=index.search_with_diagnostics(case['query'])
        latency=round((time.perf_counter()-start)*1000,3)
        ids=[fid for hit in actual['hits'] for fid in hit['fact_ids']]
        expected=case['expected_fact_id']
        exact=bool(ids and ids[0]==expected) if expected else None
        passed=actual['status']==case['expected_status'] and (exact if expected else True)
        rows.append(case|{'actual':actual,'latency_ms':latency,'passed':passed,'top1_exact':exact,
                         'returned_fact':data['facts'].get(ids[0]) if ids else None})
    result={'mode':'fixture_search_rerun_of_frozen_new_wordings','freeze_sha256':hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
            'passed':sum(r['passed'] for r in rows),'total':len(rows),'answerable':4,
            'human_reviewed':False,'raw_pdf_parsing':False,'new_paid_calls':0,'rows':rows}
    (output/'new-query-rerun.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    rows=[]
    for row in json.loads((ROOT/'artifacts/llm-prose-v7-20261110/report.json').read_text())['records']:
        checks=check_explanation(row['generated'],row['tool_result'])|check_prose(row['generated'],row['tool_result'])
        with registry(row):context=build_context(row['tool_result'])
        rows.append({'case_id':row['case_id'],'original_response':row['generated'],
                     'historical_gate':all(row['production_checks'].values()),'current_checks':checks,
                     'current_gate':all(checks.values()),'context':context})
    replay={'mode':'saved_v7_response_replay_not_new_generation','rows':rows,
            'current_gate_passed':sum(r['current_gate'] for r in rows),'total':len(rows),
            'new_paid_calls':0,'new_human_reviews':0}
    (output/'v7-replay.json').write_text(json.dumps(replay,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'queries':result['passed'],'query_total':result['total'],
                      'replay':replay['current_gate_passed'],'replay_total':len(rows),'new_paid_calls':0}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
