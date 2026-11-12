"""Free offline replay plus clearly AI-authored financial binding counterexamples."""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.record_final_human_closeout import evaluate as evaluate_current
from scripts.replay_completion_boundaries import evaluate as evaluate_previous
from quarterguard.core import compare
from quarterguard.store import load_facts
from quarterguard.explanation_context import build_generation_context
from quarterguard.explanation_guards import check_grounding,check_prose
from quarterguard.live_verification import check_explanation


def synthetic_cases():
    facts={f.id:f for f in load_facts()};rows=[]
    metrics={'gross_profit':'매출총이익','cost_of_sales':'매출원가',
             'operating_expenses':'판매관리비','net_profit':'당기순이익'}
    for metric,label in metrics.items():
        for scope in ('CFS','OFS'):
            for mode in ('qoq','yoy'):
                a=facts[f's24q3-{scope}-{metric}-2024-q-KRW']
                b=facts[f's24q2-{scope}-{metric}-2024-q-KRW' if mode=='qoq' else f's24q3-{scope}-{metric}-2023-q-KRW']
                result=compare(a,b,mode);assert result['status']=='verified'
                ctx=build_generation_context(result);parts=[]
                for f in ctx['evidence']:
                    y,m,d=map(int,f['start'].split('-'));_,em,ed=map(int,f['end'].split('-'))
                    parts.append(f"삼성전자의 {y}년 {m}월 {d}일부터 {em}월 {ed}일까지의 {f['months']}개월 간 {'연결' if scope=='CFS' else '별도'}기준 {label}은 {Decimal(f['value']):,f}백만 원입니다. 근거: {f['document_title']} PDF {f['page']}페이지.")
                text=' '.join(parts)+f" {'전분기' if mode=='qoq' else '전년 동분기'} 대비 증감률은 {result['growth_pct']}%입니다."
                answer={'status':result['status'],'value':result['growth_pct'],'issues':result['issues'],'evidence_ids':[f.id for f in (a,b)],'explanation_ko':text}
                key=f'{metric}-{scope}-{mode}'
                rows.append({'id':key+'-valid','expected_passed':True,'tool_result':result,'answer':answer})
                changes={'wrong_amount':(f'{Decimal(a.value):,f}',f'{Decimal(a.value)+1:,f}'),
                         'wrong_scope':('연결기준' if scope=='CFS' else '별도기준','별도기준' if scope=='CFS' else '연결기준'),
                         'wrong_source':(f"PDF {ctx['evidence'][0]['page']}페이지",f"PDF {ctx['evidence'][0]['page']+1}페이지"),
                         'wrong_currency':('백만 원','백만 USD')}
                for name,(old,new) in changes.items():
                    rows.append({'id':key+'-'+name,'expected_passed':False,'tool_result':result,
                                 'answer':answer|{'explanation_ko':text.replace(old,new,1)}})
    return rows


def evaluate():
    now=evaluate_current();previous=evaluate_previous()
    before=json.loads((ROOT/'artifacts/final-human-closeout-20261113/replay.json').read_text())
    old={r['case_id']:r for r in before['rows']}
    synthetic=synthetic_cases()
    for row in synthetic:
        checks=check_explanation(row['answer'],row['tool_result'])|check_prose(row['answer'],row['tool_result'])|check_grounding(row['answer'],row['tool_result'])
        row.update(passed=all(checks.values()),failed_checks=[k for k,v in checks.items() if not v])
    before_paths=['artifacts/final-human-closeout-20261113/replay.json',
                  'artifacts/closeout-live-20261112/raw/closeout-live/human-review.json',
                  'docs/validation-kit/final-human-closeout-20261113/review.json',
                  'data/facts.json','data/sources.json','quarterguard/prose_bindings.py',
                  'quarterguard/explanation_guards.py','quarterguard/public_providers.py',
                  'scripts/evaluate_prose_binding_followup.py','tests/test_prose_binding_followup.py']
    return {'mode':'offline_saved_responses_and_ai_authored_counterexamples',
            'new_paid_calls':0,'new_model_responses':0,'new_human_reviews':0,'new_pdf_parses':0,'new_mcp_runs':0,
            'human_labels_changed':False,'raw_responses_rewritten':False,
            'sample_role':'known development responses; synthetic cases are AI-authored, not human cases or independent holdout',
            'current_20':{'before':before['after'],'after':now['after'],
                          'rows':[r|{'before_passed':old[r['case_id']]['current_gate_passed']} for r in now['rows']]},
            'historical_20':{'after':previous['after'],'rows':previous['rows']},
            'synthetic':{'origin':'AI-authored additional metric/scope comparisons, using registered values; no new PDF parsing',
                         'total':len(synthetic),'positive':sum(r['expected_passed'] for r in synthetic),
                         'negative':sum(not r['expected_passed'] for r in synthetic),
                         'matched':sum(r['passed']==r['expected_passed'] for r in synthetic),'rows':synthetic},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before_paths}}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=evaluate()
    with args.output.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'current':{k:v for k,v in report['current_20'].items() if k!='rows'},
                      'historical':report['historical_20']['after'],
                      'synthetic':{k:v for k,v in report['synthetic'].items() if k!='rows'}},ensure_ascii=False))
    if report['synthetic']['matched']!=report['synthetic']['total']:raise SystemExit('SYNTHETIC_EXPECTATION_MISMATCH')
