"""Offline v5 replay. Prints JSON; never calls a provider or rewrites a report."""
import hashlib
import json
from quarterguard.store import ROOT
from quarterguard.live_verification import check_explanation
from quarterguard.explanation_guards import check_prose


def replay():
    path = ROOT / 'artifacts/llm-guards-v5-20261110/report.json'
    original = path.read_bytes()
    rows = []
    for row in json.loads(original)['records']:
        structured = check_explanation(row['generated'], row['tool_result'])
        prose = check_prose(row['generated'], row['tool_result'])
        rows.append({'case_id': row['case_id'], 'original_text': row['generated']['explanation_ko'],
                     'previous_structured_gate_passed': all(structured.values()),
                     'current_gate_passed': all(structured.values()) and all(prose.values()),
                     'prose_checks': prose})
    return {'mode': 'offline_replay_of_disclosed_v5_model_outputs',
            'source': str(path.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(original).hexdigest(),
            'development_cases': True, 'heldout': False,
            'new_model_calls': 0, 'new_pdf_or_mcp_runs': 0, 'new_human_reviews': 0,
            'previous_gate_passed': sum(r['previous_structured_gate_passed'] for r in rows),
            'current_gate_passed': sum(r['current_gate_passed'] for r in rows),
            'semantic_accuracy': None,
            'note': 'Withholding previously accepted prose is a guard change, not better model generation. Existing b verdicts remain unchanged; no-evidence is still human-labelled true.',
            'records': rows}


if __name__ == '__main__':
    print(json.dumps(replay(), ensure_ascii=False, indent=2))
