"""Current product prompt/schema on eight disclosed cases; new approval only.

Prior harnesses and responses remain untouched. MCP inputs are historical replay;
only the separately approved model responses will be new. No automatic retries.
"""
import argparse
import asyncio
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import time

import httpx

from .explanation_audit import audit_explanation
from .explanation_context import INSTRUCTIONS as PUBLIC_INSTRUCTIONS, build_context
from . import evaluate_live_explanations_v3 as baseline
from .live_verification import SCHEMA, check_explanation
from .public_providers import build_payload as product_payload
from .provider_controls import Blocked
from .frozen_followup import load_frozen_followup
from .store import ROOT

DATA = ROOT / 'data/llm-guards-v5-20261110'
PREVIOUS_FREEZE = ROOT / 'data/llm-followup-20261110/freeze.json'
BASELINE = ROOT / 'artifacts/llm-followup-20261110/report.json'
MODEL = 'gpt-5.4-mini-2026-03-17'
CONTRACT = {
    'model': MODEL, 'reasoning_effort': 'none', 'max_requests': 8,
    'max_input_admission_tokens': 7500, 'max_output_tokens': 700,
    'input_counter': 'UTF-8 bytes of entire serialized payload + 1024 framing reserve',
    'input_counter_limitation': 'Conservative local admission bound; provider framing is not publicly specified. Actual provider usage is checked after every response.',
    'retries': 0, 'timeout_seconds': 60, 'input_usd_per_million': '0.75',
    'output_usd_per_million': '4.50', 'estimated_max_cost_usd': '0.0702',
    'approval_budget_usd_before_tax': '0.08',
    'pricing_url': 'https://developers.openai.com/api/docs/models/gpt-5.4-mini',
    'pricing_checked_date': '2026-11-10', 'billed_cost_usd': None,
}
INSTRUCTIONS = PUBLIC_INSTRUCTIONS
SOURCE_FILES = ('data/facts.json', 'data/sources.json', 'data/cases.json',
                'quarterguard/core.py', 'quarterguard/mcp_server.py',
                'quarterguard/orchestrator.py', 'quarterguard/explanation_audit.py',
                'quarterguard/live_verification.py', 'quarterguard/evaluate_live_explanations_v3.py',
                'quarterguard/explanation_context.py', 'quarterguard/public_providers.py',
                'quarterguard/evaluate_live_explanations_v4.py',
                'quarterguard/evaluate_live_explanations_v5.py', 'quarterguard/frozen_followup.py',
                '.github/workflows/live-explanations-v5.yml',
                'data/llm-followup-20261110/freeze.json',
                'artifacts/llm-followup-20261110/report.json',
                'data/llm-eval-20261109/freeze.json', 'artifacts/llm-live-20261109/report.json',
                'artifacts/human-review-followup-20261110/review.json')
SPECS = [
    ('normal-qoq', 'qoq', 'qoq-revenue', '2024년 3분기 연결 매출의 전분기 대비 증감률', None),
    ('normal-yoy', 'yoy', 'yoy-revenue', '2024년 3분기 연결 매출의 전년 동분기 대비 증감률', None),
    ('period-mismatch', 'period', 'ytd-trap', '9개월 누적과 전년 3개월 매출 비교의 제한', None),
    ('scope-mismatch', 'scope', 'scope-trap', '연결 매출과 별도 매출 비교의 제한', None),
    ('unit-draft', 'unit', 'qoq-revenue', '매출 증가율 및 근거 금액 단위를 설명', '금액 단위는 천 원입니다.'),
    ('no-evidence', 'no_evidence', 'no-evidence', '수집 범위 밖인 2025년 실적 조회', None),
    ('conflicting-number-draft', 'conflicting_number', 'qoq-revenue', '근거에 맞는 매출 증가율을 설명', '2024년 3분기 연결 매출은 9.9999% 증가했습니다.'),
    ('citation-draft', 'citation', 'qoq-revenue', '공시 근거에 맞는 매출 증가율을 설명', '출처 https://example.org/fake.pdf#page=4 입니다.'),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCE_FILES}


def write_json(path, value, exclusive=False):
    with path.open('x' if exclusive else 'w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def input_admission_bound(payload):
    # Byte-level BPE cannot use more tokens than UTF-8 input bytes. Count the
    # entire JSON, including schema/instructions, and reserve server framing.
    # This is NOT a claimed API-side hard input-token setting (none exists).
    return len(json.dumps(payload, ensure_ascii=False).encode('utf-8')) + 1024


def make_payload(case):
    # Reuse the product builder rather than reproducing the new prompt/schema.
    # Evaluation-model override preserves the model used in the prior two batches.
    try:
        payload = product_payload(case['tool_result'], case['task'])
    except Blocked:
        raise ValueError('INPUT_ADMISSION_LIMIT') from None
    payload['model'] = MODEL
    payload['reasoning'] = {'effort': 'none'}
    if case.get('untrusted_draft'):
        data = json.loads(payload['input'])
        data['untrusted_draft'] = case['untrusted_draft']
        data['draft_origin'] = 'authored synthetic misleading claim; not source evidence'
        payload['input'] = json.dumps(data, ensure_ascii=False)
    if input_admission_bound(payload) > CONTRACT['max_input_admission_tokens']:
        raise ValueError('INPUT_ADMISSION_LIMIT')
    return payload


check_source = baseline.check_source


async def prepare_freeze():
    original = json.loads(PREVIOUS_FREEZE.read_text())
    load_frozen_followup().validate_freeze(original)
    old_report = json.loads(BASELINE.read_text())
    if old_report['contract']['model'] != MODEL or old_report['generated_count'] != 8:
        raise ValueError('BASELINE_MISMATCH')
    frozen_cases = []
    for old in original['cases']:
        case = copy.deepcopy(old)
        case['input_origin'] = 'replayed frozen 2026-11-09 actual MCP result; not a fresh MCP/PDF run'
        payload = make_payload(case)
        case['payload_sha256'] = digest(payload)
        case['input_admission_tokens'] = input_admission_bound(payload)
        frozen_cases.append(case)
    frozen = {'version': 5, 'frozen_at': now(), 'contract': CONTRACT,
              'source_hashes': source_hashes(), 'cases': frozen_cases,
              'source_runs': original['source_runs'],
              'baseline_report_sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
              'baseline_freeze_sha256': original['content_sha256'],
              'sampling': 'same eight disclosed development cases; paired current prompt/context/schema change, not heldout or causal isolation',
              'source_execution': 'historical MCP trace replay',
              'generation_started': False, 'human_reviewed': False, 'semantic_certified': False}
    frozen['content_sha256'] = digest(frozen)
    return frozen


def validate_freeze(frozen):
    if digest({k: v for k, v in frozen.items() if k != 'content_sha256'}) != frozen.get('content_sha256'):
        raise ValueError('FREEZE_CONTENT_MISMATCH')
    if frozen['contract'] != CONTRACT or frozen['source_hashes'] != source_hashes():
        raise ValueError('FREEZE_CODE_OR_CONTRACT_MISMATCH')
    if len(frozen['cases']) != 8 or [c['id'] for c in frozen['cases']] != [s[0] for s in SPECS]:
        raise ValueError('FROZEN_CASE_SET_MISMATCH')
    original = json.loads(PREVIOUS_FREEZE.read_text())
    load_frozen_followup().validate_freeze(original)
    if frozen['source_runs'] != original['source_runs']:
        raise ValueError('BASELINE_MISMATCH')
    if frozen['baseline_report_sha256'] != hashlib.sha256(BASELINE.read_bytes()).hexdigest():
        raise ValueError('BASELINE_MISMATCH')
    for case, old in zip(frozen['cases'], original['cases']):
        for key in ('id', 'task', 'dimension', 'source_case_id', 'tool_result', 'untrusted_draft'):
            if case[key] != old[key]:
                raise ValueError('BASELINE_MISMATCH')
        run = frozen['source_runs'][case['source_case_id']]
        if run['result'] != case['tool_result'] or not all(check_source(run, case['source_case_id']).values()):
            raise ValueError('MCP_GOLD_MISMATCH')
        if digest(make_payload(case)) != case['payload_sha256']:
            raise ValueError('FROZEN_PROMPT_MISMATCH')


def structured_answer(result, prose):
    return {'status': result['status'], 'value': result.get('growth_pct', result.get('derived_value')),
            'issues': result['issues'], 'evidence_ids': [f['id'] for f in result['evidence']],
            'explanation_ko': prose}


def production_checks(answer, result):
    return check_explanation(answer, result) | {'schema_keys_exact': set(answer) == set(SCHEMA['required'])}


def audit(answer, case):
    report = audit_explanation(answer, case['tool_result'], context_years=['2025'] if case['id'] == 'no-evidence' else [])
    return report | {'semantic_certified': False, 'human_review_required': True,
                     'presentation_checks': presentation_checks(answer, case)}


def presentation_checks(answer, case):
    text = str(answer.get('explanation_ko', ''))
    context = build_context(case['tool_result'])
    # A model may use other correct phrasing. These counts must be human-adjudicated.
    refs = {(r['document_title'], r['page']) for r in context['evidence']}
    return {
        'display_unit_named': None if not refs else all(r['display_unit'] in text for r in context['evidence']),
        'scope_limited_if_no_evidence': ('검색 범위' in text) if not refs else None,
        'document_and_page_named': None if not refs else all(
            title in text and re.search(r'(?:p\.?|page|쪽)\s*' + str(page) + r'(?![0-9])', text, re.I)
            for title, page in refs),
        'internal_scale_term_absent': 'scale' not in text.lower(),
        'interpretation': 'literal presentation coverage only; not semantic certification',
    }


def synthetic_checks(frozen):
    by_id = {c['id']: c for c in frozen['cases']}
    challenges = [
        ('period', 'normal-qoq', '2024년 2분기 연결 매출은 79,098,731 백만 원입니다.', 'AMOUNT_CONTEXT_MISMATCH'),
        ('scope', 'normal-qoq', '별도 매출 증가율은 6.7916%입니다.', 'SCOPE_CLAIM_CONFLICT'),
        ('unit', 'normal-qoq', '금액 단위는 천 원입니다.', 'UNIT_CLAIM_CONFLICT'),
        ('no-evidence', 'no-evidence', '2025년 매출은 100 백만 원입니다.', 'UNSUPPORTED_NUMERIC_CLAIM'),
        ('number', 'normal-qoq', '매출 증가율은 9.9999%입니다.', 'PERCENT_MISMATCH'),
        ('citation', 'normal-qoq', '출처 https://example.org/fake.pdf#page=4 입니다.', 'INLINE_CITATION_MISMATCH'),
    ]
    rows = []
    for id_, source, text, expected in challenges:
        case = by_id[source]
        answer = structured_answer(case['tool_result'], text)
        checked = audit(answer, case)
        rows.append({'id': id_, 'source_case': source, 'origin': 'authored_synthetic_validator_challenge',
                     'answer': answer, 'expected_rule': expected, 'audit': checked,
                     'expected_rule_detected': expected in checked['issues']})
    return rows


def sanitized_response(body):
    """Only allowlisted public output/usage fields; no headers, requests, arbitrary errors."""
    raw = {key: body.get(key) for key in ('id', 'model', 'status')}
    usage = body.get('usage') or {}
    raw['usage'] = {key: usage.get(key) for key in ('input_tokens', 'output_tokens', 'total_tokens')}
    raw['output_text'] = ''.join(c.get('text', '') for item in body.get('output', [])
                                if item.get('type') == 'message' for c in item.get('content', [])
                                if c.get('type') == 'output_text')
    return raw


def execute(frozen, output, *, execute_approved=False):
    if not execute_approved:
        raise ValueError('EXPLICIT_APPROVAL_REQUIRED')
    output = Path(output)
    if (output / 'attempts.jsonl').exists():
        raise ValueError('RUN_ALREADY_ATTEMPTED')
    validate_freeze(frozen)
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_NOT_CONFIGURED')
    output.mkdir(parents=True, exist_ok=True)
    report = {'baseline_report_sha256': frozen.get('baseline_report_sha256'),
              'paired_development_followup': True, 'source_execution': 'historical MCP result replay',
              'created_at': now(), 'status': 'running', 'freeze_sha256': frozen.get('content_sha256'),
              'contract': CONTRACT, 'execution_mode': 'real_provider_responses', 'calls_attempted': 0,
              'records': [], 'semantic_certified': False, 'human_review_required': True,
              'human_reviewed': False, 'semantic_accuracy': None, 'billed_cost_usd': None}
    # The exclusive journal is durable before the first network operation. Never resume.
    with (output / 'attempts.jsonl').open('x') as journal:
        for case in frozen['cases'][:8]:
            payload = make_payload(case)
            attempt = {'case_id': case['id'], 'attempt': report['calls_attempted'] + 1, 'started_at': now(),
                       'execution_mode': 'real_provider_response', 'status': 'started',
                       'input_admission_tokens': input_admission_bound(payload)}
            journal.write(canonical(attempt) + '\n'); journal.flush(); os.fsync(journal.fileno())
            report['calls_attempted'] += 1
            row = copy.deepcopy(attempt)
            start = time.perf_counter()
            failure = None
            try:
                response = httpx.post('https://api.openai.com/v1/responses', json=payload,
                    headers={'Authorization': 'Bearer ' + key}, timeout=60)
                if response.status_code != 200:
                    failure = f'OPENAI_HTTP_{response.status_code}'
                else:
                    body = response.json()
                    raw = sanitized_response(body)
                    # A secret echoed by a provider must never be written to artifacts.
                    raw = json.loads(json.dumps(raw, ensure_ascii=False).replace(key, '[REDACTED]'))
                    row['raw_response_sanitized'] = raw
                    write_json(output / (case['id'] + '.response.json'), raw, exclusive=True)
                    usage = raw['usage']
                    i, o = usage['input_tokens'], usage['output_tokens']
                    if type(i) is not int or type(o) is not int or min(i, o) < 0:
                        raise ValueError('invalid usage')
                    row['provider'] = {'requested_model': MODEL, 'returned_model': raw['model'],
                        'input_tokens': i, 'output_tokens': o,
                        'estimated_cost_usd': str((Decimal(i) * Decimal('.75') + Decimal(o) * Decimal('4.50')) / Decimal(1000000)),
                        'billed_cost_usd': None, 'cost_note': 'Usage-based list-price estimate; billing not queried.'}
                    if i > 7500 or o > 700:
                        failure = 'PROVIDER_USAGE_LIMIT_EXCEEDED'
                    elif raw['model'] != MODEL:
                        failure = 'PROVIDER_MODEL_MISMATCH'
                    elif raw['status'] != 'completed':
                        failure = 'OPENAI_INCOMPLETE'
                    else:
                        answer = json.loads(raw['output_text'])
                        if not isinstance(answer, dict):
                            raise ValueError('invalid answer')
                        row['generated'] = answer
                        row['audit'] = audit(answer, case)
                        row['production_checks'] = production_checks(answer, case['tool_result'])
                        row['production_gate_passed'] = all(row['production_checks'].values())
                        row['source_case_id'] = case.get('source_case_id')
                        row['tool_result'] = case['tool_result']
            except httpx.HTTPError:
                failure = 'OPENAI_CONNECTION_FAILED'
            except Exception:
                failure = 'OPENAI_INVALID_RESPONSE'
            row['latency_ms'] = round((time.perf_counter() - start) * 1000, 3)
            row['finished_at'] = now()
            row['status'] = 'failed' if failure else 'completed'
            if failure:
                row['failure_code'] = failure
            report['records'].append(row)
            journal.write(canonical({'case_id': case['id'], 'attempt': row['attempt'], 'status': row['status'],
                                      'finished_at': row['finished_at'], 'failure_code': failure}) + '\n')
            journal.flush(); os.fsync(journal.fileno())
            write_json(output / 'report.json', report)
            if failure:
                break
    completed = [r for r in report['records'] if r['status'] == 'completed']
    report['status'] = 'completed' if len(completed) == len(frozen['cases']) else 'failed'
    report['generated_count'] = len(completed)
    report['automatic_flagged_count'] = sum(bool(r['audit']['issues']) for r in completed)
    report['structured_exact_count'] = sum(all(r['audit']['structured_checks'].values()) for r in completed)
    report['production_gate_passed_count'] = sum(r['production_gate_passed'] for r in completed)
    report['measured_input_tokens'] = sum(r.get('provider', {}).get('input_tokens', 0) for r in report['records'])
    report['measured_output_tokens'] = sum(r.get('provider', {}).get('output_tokens', 0) for r in report['records'])
    report['usage_estimated_cost_usd'] = str(sum((Decimal(r.get('provider', {}).get('estimated_cost_usd', '0')) for r in report['records']), Decimal(0)))
    report['unmeasured_failed_attempts'] = sum('provider' not in r for r in report['records'])
    report['cost_note'] = 'Usage estimates exclude unmeasured failed attempts, taxes, local compute and hosting; actual billing unknown.'
    report['limitations'] = ['The same disclosed development cases are reused; this does not estimate general model accuracy.',
        'No-detected-rule-violation is not semantic certification.',
        'Synthetic bad draft inputs and validator fixtures are not real model failures or human labels.',
        'Human review is required for attribution, negation, omissions, period/scope/unit meaning and citation relevance.',
        'Prompt, context and constrained schema changed together; effects cannot be causally separated.',
        'Product payload/checks are reused, but this is an isolated evaluator, not a public endpoint/cache execution.',
        'Public production still uses GPT-4.1 mini; this run uses the prior evaluation model GPT-5.4 mini.']
    write_json(output / 'report.json', report)
    write_json(output / 'human-review.json', [
        {'case_id': r['case_id'], 'generated': r['generated'], 'tool_result': r['tool_result'],
         'automatic_audit': r['audit'], 'production_checks': r['production_checks'], 'reviewer': None, 'reviewed_at': None, 'verdict': None,
         'checks': {k: None for k in ('numbers', 'period', 'scope', 'unit', 'citation_relevance', 'rejection_preserved', 'omissions')},
         'notes': None, 'semantic_certified': False} for r in completed])
    write_json(output / 'comparison.json', compare_reports(json.loads(BASELINE.read_text()), report, frozen), exclusive=True)
    return report


def compare_reports(baseline, followup, frozen):
    validate_freeze(frozen)
    if digest(baseline) != digest(json.loads(BASELINE.read_text())):
        raise ValueError('BASELINE_REPORT_MISMATCH')
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
            'baseline_product_checks':production_checks(old['generated'],case['tool_result']),
            'followup_product_checks':production_checks(new['generated'],case['tool_result']) if new else None,
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
            'Prompt, deterministic context and constrained schema changed together.',
            'Presentation checks are literal inclusion checks, not semantic or citation-relevance verification.',
            'Same GPT-5.4-mini snapshot as prior evaluation; not public GPT-4.1-mini performance.',
            'Prior b labels do not transfer to new outputs.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true', help='Freeze historical MCP inputs with new prompt/context; zero paid calls')
    parser.add_argument('--freeze', type=Path, default=DATA / 'freeze.json')
    parser.add_argument('--execute-approved', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'work/live-explanations-guards-v5-20261110')
    args = parser.parse_args()
    try:
        if args.prepare:
            if args.execute_approved:
                raise ValueError('PREPARE_AND_EXECUTE_MUST_BE_SEPARATE')
            frozen = asyncio.run(prepare_freeze())
            args.freeze.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.freeze, frozen, exclusive=True)
            write_json(args.freeze.parent / 'synthetic-validator-checks.json', synthetic_checks(frozen), exclusive=True)
            print(json.dumps({'status': 'frozen', 'cases': len(frozen['cases']), 'paid_calls': 0,
                              'max_input_admission_tokens': max(c['input_admission_tokens'] for c in frozen['cases'])}))
        else:
            frozen = json.loads(args.freeze.read_text())
            report = execute(frozen, args.output, execute_approved=args.execute_approved)
            print(json.dumps({k: report[k] for k in ('status', 'calls_attempted', 'generated_count', 'usage_estimated_cost_usd')}))
            if report['status'] != 'completed':
                raise SystemExit(1)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        allowed = {'EXPLICIT_APPROVAL_REQUIRED', 'RUN_ALREADY_ATTEMPTED', 'OPENAI_NOT_CONFIGURED',
            'FREEZE_CONTENT_MISMATCH', 'FREEZE_CODE_OR_CONTRACT_MISMATCH', 'FROZEN_CASE_SET_MISMATCH',
            'MCP_GOLD_MISMATCH', 'BASELINE_MISMATCH', 'FROZEN_PROMPT_MISMATCH', 'INPUT_ADMISSION_LIMIT', 'PREPARE_AND_EXECUTE_MUST_BE_SEPARATE'}
        code = str(exc) if str(exc) in allowed else 'LOCAL_PREFLIGHT_FAILED'
        print(json.dumps({'status': 'blocked', 'reason': code, 'paid_calls_started_by_this_invocation': 0}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
