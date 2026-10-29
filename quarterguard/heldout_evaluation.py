"""Frozen, AI-authored new-document evaluation. Never modifies production data.

Raw ingestion is reported separately from fixture-assisted downstream checks.
Baseline adapts the manifest; explicit post-fix mode also adapts canonical facts.
The production valid_source function is always real.
"""
import argparse
from contextlib import ExitStack
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from unittest.mock import patch

from .core import Fact, compare, reconcile, valid_source
from .ingest import parse_statement
from .search import SearchIndex

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/heldout'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen(post_fix=False):
    freeze = json.loads((DATA / 'freeze.json').read_text())
    for name, expected in (freeze['files'] | freeze['production_files']).items():
        if digest(ROOT / name) != expected and not (post_fix and name == 'quarterguard/core.py'):
            raise ValueError(f'FROZEN_INPUT_CHANGED: {name}')
    sources = json.loads((DATA / 'sources.json').read_text())
    facts = {row['id']: Fact(**row) for row in json.loads((DATA / 'facts.json').read_text())}
    cases = json.loads((DATA / 'cases.json').read_text())
    return freeze, sources, facts, cases


def audit_sources(sources, facts, cache):
    """Audit PDF hash and literal row cells, without using production ingestion.

    The fixture is KRW only. Select the first/second/fifth/sixth data cells
    from the eight-cell source row, after the note number when present.
    Join digit-only line wraps (H1 separate revenue) before tokenization.
    """
    from pypdf import PdfReader
    pages, audits = {}, []
    for source in sources:
        path = cache / source['cache_filename']
        if digest(path) != source['sha256']:
            raise ValueError('SOURCE_HASH_CHANGED: ' + source['id'])
        reader = PdfReader(path)
        if len(reader.pages) != source['pages']:
            raise ValueError('SOURCE_PAGE_COUNT_CHANGED')
        for scope, page in source['statement_pages'].items():
            text = reader.pages[page - 1].extract_text() or ''
            pages[(source['id'], scope)] = text
            joined = re.sub(r'(?<=\d)\s*\n\s*(?=\d(?:\s|$))', '', text)
            for f in [f for f in facts.values() if f.document_id == source['id'] and f.scope == scope]:
                line = re.search(re.escape(f.row) + r'\s+([^A-Za-z※]+)', joined)
                cells = re.findall(r'\(?-?\d[\d,]*(?:\.\d+)?\)?', line.group(1)) if line else []
                if f.metric in ('revenue', 'operating_profit'):
                    cells = cells[1:]
                column = (0 if f.months == 3 else 4) + (0 if f.start.startswith('2025') else 1)
                actual = cells[column].replace(',', '').replace('(', '-').replace(')', '') if len(cells) == 8 else None
                ok = (actual == f.value and 'millions of Korean won' in text
                      and ('INTERIM CONSOLIDATED' if scope == 'CFS' else 'INTERIM SEPARATE') in text)
                audits.append({'fact_id': f.id, 'source_cell': actual, 'passed': ok})
    if not all(a['passed'] for a in audits):
        raise ValueError('GOLD_SOURCE_AUDIT_FAILED: ' + json.dumps([a for a in audits if not a['passed']]))
    return pages, audits


def downstream(case, facts, index):
    stage = case['stage']
    if stage == 'fixture_retrieval':
        hits = index.search(case['query'], 5)
        rank = next((i + 1 for i, hit in enumerate(hits) if case['gold_fact_id'] in hit['fact_ids']), None)
        return {'rank': rank, 'retrieved': [h['id'] for h in hits],
                'passed': rank is not None and rank <= case['expected_rank_max']}
    if stage == 'fixture_citation':
        fact = replace(facts[case['input']], **case['mutation'])
        actual = valid_source(fact)
        return {'actual_valid': actual, 'passed': actual == case['expected_valid']}
    inputs = [facts[id] for id in case['inputs']]
    if mutation := case.get('mutation'):
        i = mutation['input_index']
        inputs[i] = replace(inputs[i], **mutation['changes'])
    result = compare(*inputs, case['mode']) if case['operation'] == 'compare' else reconcile(*inputs)
    actual_value = result.get('growth_pct', result.get('derived_value'))
    checks = {'status': result['status'] == case['expected_status'],
              'value': actual_value == case['expected_value'],
              'evidence_preserved': result['evidence'] == [f.public() for f in inputs]}
    checks['issues'] = (case['expected_issue'] in result['issues'] if 'expected_issue' in case
                        else sorted(result['issues']) == sorted(case['expected_issues']))
    return {'result': result, 'checks': checks, 'passed': all(checks.values())}


def evaluate(cache, post_fix=False):
    freeze, sources, facts, cases = load_frozen(post_fix=post_fix)
    pages, source_audit = audit_sources(sources, facts, cache)
    index = SearchIndex(list(facts.values()), 'hybrid_meta')
    manifest = {source['id']: source for source in sources}
    # Capture the real registry before the isolated adapter context.
    registry_valid = sum(valid_source(fact) for fact in facts.values())
    results = []
    for case in cases:
        if case['stage'] == 'raw_ingestion':
            source = manifest[case['document_id']]
            try:
                parsed = parse_statement(pages[(source['id'], case['scope'])], source,
                                         source['statement_pages'][case['scope']],
                                         metrics=['revenue', 'gross_profit', 'operating_profit', 'net_profit'])
                observation = {'parsed_fact_count': len(parsed), 'passed': len(parsed) == case['expected_fact_count']}
            except ValueError as exc:
                observation = {'error': str(exc), 'parsed_fact_count': 0, 'passed': False}
        else:
            with ExitStack() as stack:
                stack.enter_context(patch('quarterguard.core.source_manifest', return_value=manifest))
                if post_fix:
                    stack.enter_context(patch('quarterguard.core.source_facts',
                                              return_value={id: asdict(f) for id, f in facts.items()}))
                observation = downstream(case, facts, index)
        results.append(case | observation)
    stage_counts = {}
    for stage in sorted({r['stage'] for r in results}):
        rows = [r for r in results if r['stage'] == stage]
        stage_counts[stage] = {'total': len(rows), 'passed': sum(r['passed'] for r in rows),
                               'failed': sum(not r['passed'] for r in rows)}
    retrieval_rows = [r for r in results if r['stage'] == 'fixture_retrieval']
    retrieval_metrics = {}
    for style in ('controlled', 'natural'):
        rows = [r for r in retrieval_rows if r['query_style'] == style]
        retrieval_metrics[style] = {'n': len(rows), 'recall_at_1': sum(r['rank'] == 1 for r in rows) / len(rows),
                                   'recall_at_5': sum(r['rank'] is not None for r in rows) / len(rows),
                                   'mrr_at_5': sum(1 / r['rank'] if r['rank'] else 0 for r in rows) / len(rows)}
    return {'evaluated_at': datetime.now(timezone.utc).isoformat(), 'freeze': freeze,
            'evaluation_type': ('Post-disclosure remediation regression; NOT unseen heldout' if post_fix
                                else 'AI-authored new-document baseline; not independent human heldout'),
            'post_fix': post_fix,
            'current_production_hashes': {name: digest(ROOT / name) for name in freeze['production_files']},
            'human_reviewed': False, 'documents': len(sources), 'gold_facts': len(facts),
            'model_calls': 0, 'provider_api_cost_usd': 0,
            'cost_scope': 'Paid model APIs only; excludes CPU, storage and network',
            'adapter': ('Fixtures supplied directly to SearchIndex/core; isolated source_manifest and source_facts patches; real current valid_source' if post_fix else
                        'Fixtures supplied directly to SearchIndex/core; isolated source_manifest patch; production valid_source unchanged'),
            'raw_registry': {'accepted': registry_valid, 'total': len(facts), 'reason': '2025 documents absent from production allowlist'},
            'end_to_end': {'status': 'unsupported', 'ingested_statements': stage_counts['raw_ingestion']['passed'],
                           'claim': 'No successful raw-PDF-to-answer evaluation. Downstream fixture results are diagnostic only.'},
            'source_audit': source_audit, 'stage_counts': stage_counts,
            'retrieval_metrics': retrieval_metrics,
            'failure_ids': [r['id'] for r in results if not r['passed']], 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / 'work/heldout-raw')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/heldout-evaluation.json')
    parser.add_argument('--post-fix', action='store_true', help='Allow only core.py to differ; preserve frozen baseline; report remediation regression')
    args = parser.parse_args()
    baseline = DATA / 'first-run.json'
    # Read the existing baseline before evaluation; exclusive creation prevents replacement.
    if baseline.exists():
        baseline_data = json.loads(baseline.read_text())
    else:
        baseline_data = None
    if args.post_fix and baseline_data is None:
        raise ValueError('POST_FIX_REQUIRES_PRESERVED_BASELINE')
    result = evaluate(args.cache, post_fix=args.post_fix)
    if baseline_data is None:
        with baseline.open('x') as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    result['first_run_sha256'] = digest(baseline)
    result['first_run_path'] = str(baseline.relative_to(ROOT))
    if args.post_fix:
        result['baseline_stage_counts'] = baseline_data['stage_counts']
        result['baseline_failure_ids'] = baseline_data['failure_ids']
        (DATA / 'post-fix.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'stage_counts': result['stage_counts'], 'failure_ids': result['failure_ids'],
                      'raw_registry': result['raw_registry']}, indent=2))


if __name__ == '__main__':
    main()
