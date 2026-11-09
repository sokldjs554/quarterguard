"""Replay disclosed tool results through context rendering; zero provider calls."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quarterguard.explanation_context import build_context
from quarterguard.public_providers import build_payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = ROOT / 'artifacts/llm-live-20261109/report.json'
    original = json.loads(source.read_text())
    records = []
    for row in original['records']:
        result = row['tool_result']
        context = build_context(result)
        expected = 'no_evidence' if row['case_id'] == 'no-evidence' else 'available'
        assert context['status'] == expected
        assert context['comparison_status'] == result['status']
        assert context['issues'] == result['issues']
        assert len(context['evidence']) == len(result['evidence'])
        for evidence, fact in zip(context['evidence'], result['evidence']):
            for key in ('id','value','currency','scale','page','row','column','start','end','scope'):
                assert evidence[key] == fact[key]
            assert evidence['display_unit'] == '백만 원'
            assert evidence['source_href'] == fact['source_url'] + '#page=' + str(fact['page'])
        payload = build_payload(result, row['case_id'])
        records.append({'case_id': row['case_id'],
            'original_model_explanation_unchanged': row['generated']['explanation_ko'],
            'deterministic_context': context,
            'public_payload_bytes': len(json.dumps(payload, ensure_ascii=False).encode()),
            'source_context_checks_passed': True})
    report = {'evaluation_kind':'disclosed_development_tool_result_replay',
        'source_report':str(source.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'code_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ['quarterguard/explanation_context.py','quarterguard/public_providers.py','web/explanation-context.js']},
        'new_provider_calls':0,'new_provider_cost_usd':'0','historical_bill_queried':False,
        'fresh_pdf_parsing':False,'new_model_outputs':0,'new_human_review':False,
        'sample_count':len(records),'context_checks_passed':len(records),
        'semantic_accuracy':None,'records':records,
        'limitations':['Known eight development cases reused, not holdout evidence.',
            'Added context is deterministic; original model prose is not corrected or certified.',
            'Updated public prompt has not been exercised with a live model.',
            'No improvement rate or new participant review is claimed.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({k:report[k] for k in ('sample_count','context_checks_passed','new_provider_calls','new_model_outputs')}))


if __name__ == '__main__':
    main()
