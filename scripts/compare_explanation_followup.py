"""Apply the frozen audit to both batches; never supply human verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from quarterguard.evaluate_live_explanations_v4 import DATA, audit, validate_freeze


def compare_reports(baseline, followup, frozen):
    validate_freeze(frozen)
    if followup['freeze_sha256'] != frozen['content_sha256']:
        raise ValueError('FOLLOWUP_FREEZE_MISMATCH')
    if baseline['contract']['model'] != followup['contract']['model']:
        raise ValueError('MODEL_MISMATCH')
    previous={r['case_id']:r for r in baseline['records']}
    after={r['case_id']:r for r in followup['records'] if r['status']=='completed'}
    pairs=[]
    for case in frozen['cases']:
        old=previous[case['id']]
        new=after.get(case['id'])
        if old['tool_result'] != case['tool_result'] or new and new['tool_result'] != case['tool_result']:
            raise ValueError('INPUT_MISMATCH')
        pairs.append({'case_id':case['id'],'baseline_generated':old['generated'],
            'followup_generated':new['generated'] if new else None,
            'baseline_audit_same_rules':audit(old['generated'],case),
            'followup_audit_same_rules':audit(new['generated'],case) if new else None,
            'followup_human_verdict':None,'followup_human_reviewer':None})
    def summarize(side):
        audits=[p[side+'_audit_same_rules'] for p in pairs if p[side+'_audit_same_rules']]
        criteria={}
        for field in ('display_unit_named','document_and_page_named','scope_limited_if_no_evidence','internal_scale_term_absent'):
            values=[a['presentation_checks'][field] for a in audits if a['presentation_checks'][field] is not None]
            criteria[field]={'met':sum(v is True for v in values),'applicable':len(values)}
        return {'completed':len(audits),'structured_exact':sum(all(a['structured_checks'].values()) for a in audits),
                'automatic_flagged':sum(bool(a['issues']) for a in audits),'literal_presentation_checks':criteria}
    return {'type':'same_disclosed_development_cases_paired_comparison',
        'freeze_sha256':frozen['content_sha256'],'new_human_review':False,'semantic_accuracy':None,
        'baseline':summarize('baseline'),'followup':summarize('followup'),'pairs':pairs,
        'limitations':['Same cases used for development; not a heldout accuracy estimate.',
            'Prompt and supplied deterministic context changed together.',
            'Presentation checks are literal inclusion checks, not semantic or citation-relevance verification.',
            'Same GPT-5.4-mini snapshot as prior evaluation; not public GPT-4.1-mini performance.',
            'Prior b labels do not transfer to new outputs.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--followup',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old=ROOT/'artifacts/llm-live-20261109/report.json'
    frozen=json.loads((DATA/'freeze.json').read_text())
    report=compare_reports(json.loads(old.read_text()),json.loads(args.followup.read_text()),frozen)
    report['input_sha256']={str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [old,args.followup]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'baseline':report['baseline'],'followup':report['followup']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
