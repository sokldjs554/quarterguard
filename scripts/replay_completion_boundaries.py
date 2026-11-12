"""Replay immutable responses against current guards, with existing human labels.

No generation, PDF parsing, MCP execution, or new human evaluation. Refuses to
overwrite an output. Run from the repository: python scripts/replay_completion_boundaries.py --output ...
"""
import argparse
from collections import Counter
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quarterguard.evaluate_live_explanations_v9 import registry
from quarterguard.explanation_guards import check_prose, check_grounding
from quarterguard.live_verification import check_explanation


def evaluate():
    raw_path = ROOT/'artifacts/model-completion-live-20261112/raw/completion-live/human-review.json'
    old_path = ROOT/'artifacts/model-completion-live-20261112/offline-followup/replay.json'
    human_path = ROOT/'docs/validation-kit/completion-human-review-20261112/review.json'
    freeze_path = ROOT/'data/llm-prose-v9-20261111/freeze.json'
    raw = json.loads(raw_path.read_text())
    old = {r['case_id']: r for r in json.loads(old_path.read_text())['rows']}
    human = {r['case_id']: r for r in json.loads(human_path.read_text())['rows']}
    frozen = {r['id']: r for r in json.loads(freeze_path.read_text())['cases']}
    if len(raw) != 20 or {r['case_id'] for r in raw} != set(old) or set(old) != set(human):
        raise ValueError('CASE_SET_MISMATCH')
    rows = []
    for record in raw:
        cid = record['case_id']
        case = frozen[cid.removeprefix('replay-')] if cid.startswith('replay-') else None
        if case and case['tool_result'] != record['tool_result']:
            raise ValueError('TOOL_INPUT_CHANGED')
        with registry(case) if case else nullcontext():
            checks = (check_explanation(record['raw_generated'], record['tool_result']) |
                      check_prose(record['raw_generated'], record['tool_result']) |
                      check_grounding(record['raw_generated'], record['tool_result']))
        rows.append({'review_id': human[cid]['review_id'], 'case_id': cid,
                     'human_verdict': human[cid]['verdict'],
                     'before_passed': old[cid]['offline_passed'],
                     'after_passed': all(checks.values()), 'after_checks': checks,
                     'failed_checks': [key for key, value in checks.items() if not value]})
    paths = [raw_path, old_path, human_path, freeze_path,
             *(ROOT/f'quarterguard/{p}.py' for p in ('explanation_guards', 'explanation_context', 'public_providers'))]
    counts = lambda side, passed: dict(Counter(r['human_verdict'] for r in rows if r[side] == passed))
    return {'mode': 'offline_replay_of_existing_20_responses',
            'new_paid_calls': 0, 'new_human_verdicts': 0, 'new_pdf_parses': 0, 'new_mcp_runs': 0,
            'sample_role': 'known development cases used in fixes; not holdout',
            'prose_rewritten': False, 'semantic_certification': False,
            'raw_human_counts_unchanged': dict(Counter(r['human_verdict'] for r in rows)),
            'before': {'passed': sum(r['before_passed'] for r in rows),
                       'passed_human_verdicts': counts('before_passed', True),
                       'blocked_human_verdicts': counts('before_passed', False)},
            'after': {'passed': sum(r['after_passed'] for r in rows),
                      'passed_human_verdicts': counts('after_passed', True),
                      'blocked_human_verdicts': counts('after_passed', False)},
            'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate()
    with args.output.open('x') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({key: result[key] for key in ('before', 'after', 'new_paid_calls')}, ensure_ascii=False))
