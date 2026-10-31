"""Frozen official-document evaluation; raw ingestion and fixture diagnostics stay separate.

Run this file with --code-root pointing to an isolated baseline snapshot to execute
that snapshot's actual parser/search/core. No paid providers are called.
"""
from __future__ import annotations
import argparse
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/v2-blind'
METRICS = ['revenue', 'gross_profit', 'operating_profit', 'net_profit']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_frozen(data=DATA):
    freeze = json.loads((data / 'freeze.json').read_text())
    for name, expected in freeze['files'].items():
        if digest(data / Path(name).name) != expected:
            raise ValueError('FROZEN_INPUT_CHANGED: ' + name)
    return freeze, {name: json.loads((data / (name + '.json')).read_text())
                    for name in ('sources', 'facts', 'source_cells', 'retrieval_gold', 'calculations')}


def audit_sources(payload, cache):
    """Independent literal-cell check. Does not invoke production ingestion."""
    from pypdf import PdfReader
    facts = {f['id']: f for f in payload['facts']}
    pages, audits = {}, []
    for source in payload['sources']:
        path = cache / source['cache_filename']
        if digest(path) != source['sha256']:
            raise ValueError('SOURCE_HASH_CHANGED: ' + source['id'])
        reader = PdfReader(path)
        if len(reader.pages) != source['pages']:
            raise ValueError('SOURCE_PAGE_COUNT_CHANGED: ' + source['id'])
        for scope, number in source['statement_pages'].items():
            text = reader.pages[number - 1].extract_text() or ''
            pages[(source['id'], scope)] = text
            flat = re.sub(r'\s+', ' ', text)
            if source['company'] == 'samsung':
                report_year = int(source['report_end'][:4])
                expected_years = ' '.join([str(report_year), str(report_year - 1)] * 4)
                header_ok = (expected_years + ' KRW KRW USD USD KRW KRW USD USD' in flat
                             and ('INTERIM CONSOLIDATED' if scope == 'CFS' else 'INTERIM SEPARATE') in flat
                             and ('June 30' if source['quarter'] == 2 else 'September 30') in flat)
            else:
                header_ok = ('INTERIM CONSOLIDATED STATEMENTS OF INCOME' in flat
                             and '2023 2022' in flat and 'Nine-month period ended September 30' in flat
                             and 'THREE-MONTH AND NINE-MONTH PERIODS ENDED SEPTEMBER 30, 2023 AND 2022' in flat)
            for cell in payload['source_cells']:
                fact = facts[cell['fact_id']]
                if fact['document_id'] != source['id'] or fact['scope'] != scope:
                    continue
                match = re.search(re.escape(cell['source_row']) + r'\s+([^\n]+)', text)
                tokens = re.findall(r'\(?-?\d[\d,]*(?:\.\d+)?\)?', match.group(1)) if match else []
                count = 8 if source['company'] == 'samsung' else 4
                tokens = tokens[-count:]
                actual = (tokens[cell['data_column_index_1based'] - 1].replace(',', '').replace('(', '-').replace(')', '')
                          if len(tokens) == count else None)
                passed = (actual == fact['value'] and header_ok and cell['source_unit'] in flat
                          and cell['header_year'] == int(fact['start'][:4]) and cell['header_end'] == fact['end'])
                audits.append({'fact_id': fact['id'], 'source_cell': actual, 'header_verified': header_ok, 'passed': passed})
    if not all(row['passed'] for row in audits) or len(audits) != len(facts):
        raise ValueError('GOLD_SOURCE_AUDIT_FAILED: ' + json.dumps([r for r in audits if not r['passed']]))
    return pages, audits


def exact_fact(actual, expected):
    # Match canonical row labels; literal issuer labels are separately audited above.
    return all(asdict(actual).get(k) == v for k, v in expected.items())


def query_observation(index, case):
    if index is None:
        return {'candidate_ids': [], 'rank': None, 'status': 'no_parsed_corpus',
                'issues': ['RAW_INGESTION_FAILED'], 'trusted_query': False, 'passed': False,
                'retrieval_passed': False, 'diagnostic_supported': False}
    diagnostic = hasattr(index, 'search_with_diagnostics')
    if diagnostic:
        result = index.search_with_diagnostics(case['query'], 5)
        hits = result.get('hits', result.get('candidates', []))
        status, issues = result.get('status'), result.get('issues', [])
        trusted = result.get('trusted_query', False)
    else:
        hits = index.search(case['query'], 5)
        status, issues, trusted = 'legacy_no_diagnostics', [], False
    ids = [fid for hit in hits for fid in hit.get('fact_ids', [])]
    rank = next((i + 1 for i, hit in enumerate(hits) if set(hit.get('fact_ids', [])) & set(case['gold_fact_ids'])), None)
    if case['expected_answerable']:
        retrieval_passed = rank == 1
        passed = retrieval_passed and trusted and status == 'ready'
    elif case['expected_clarification']:
        retrieval_passed = not ids
        passed = diagnostic and status == 'needs_clarification' and not trusted
    else:
        retrieval_passed = not ids
        passed = not ids and not (trusted and status == 'ready')
    return {'candidate_ids': ids, 'rank': rank, 'status': status, 'issues': issues,
            'trusted_query': trusted, 'passed': passed, 'retrieval_passed': retrieval_passed,
            'diagnostic_supported': diagnostic}


def calculation_observation(core, case, facts):
    if any(fid not in facts for fid in case['inputs']):
        return {'passed': False, 'status': 'blocked_missing_parsed_fact', 'missing': [fid for fid in case['inputs'] if fid not in facts]}
    inputs = [facts[fid] for fid in case['inputs']]
    result = (core.compare(*inputs, case['mode']) if case['operation'] == 'compare'
              else core.reconcile(*inputs))
    value = result.get('growth_pct', result.get('derived_value'))
    return {'passed': result['status'] == case['expected_status'] and value == case['expected_value']
            and result['evidence'] == [f.public() for f in inputs], 'result': result}


def summarize(rows):
    return {'total': len(rows), 'passed': sum(r['passed'] for r in rows),
            'failed': sum(not r['passed'] for r in rows)}


def evaluate(cache, code_root, label, data=DATA):
    freeze, payload = load_frozen(data)
    pages, audits = audit_sources(payload, cache)
    # A new subprocess is required for each code_root: importing two revisions in
    # one interpreter risks Python's module cache silently selecting the wrong one.
    sys.path.insert(0, str(code_root))
    core = importlib.import_module('quarterguard.core')
    ingest = importlib.import_module('quarterguard.ingest')
    search = importlib.import_module('quarterguard.search')
    if Path(core.__file__).resolve().parent.parent != code_root.resolve():
        raise ValueError('WRONG_IMPLEMENTATION_IMPORTED')
    gold = {f['id']: f for f in payload['facts']}
    manifest = {s['id']: s for s in payload['sources']}
    parsed, statements, matches = {}, [], []
    for source in payload['sources']:
        for scope, page in source['statement_pages'].items():
            try:
                result = ingest.parse_statement(pages[(source['id'], scope)], source, page, metrics=METRICS)
                parsed.update({f.id: f for f in result})
                expected = [f for f in gold.values() if f['document_id'] == source['id'] and f['scope'] == scope]
                correct = sum(f['id'] in parsed and exact_fact(parsed[f['id']], f) for f in expected)
                statements.append({'id': source['id'] + '-' + scope, 'parsed_count': len(result),
                                   'gold_cells': len(expected), 'exact_cells': correct, 'passed': correct == len(expected)})
            except (ValueError, KeyError) as exc:
                statements.append({'id': source['id'] + '-' + scope, 'parsed_count': 0, 'gold_cells': 16,
                                   'exact_cells': 0, 'error': type(exc).__name__ + ': ' + str(exc), 'passed': False})
    for fid, f in gold.items():
        actual = parsed.get(fid)
        matches.append({'fact_id': fid, 'passed': actual is not None and exact_fact(actual, f),
                        'parsed': asdict(actual) if actual else None})
    # Unmodified production registration is measured before evaluation adapters.
    production_accepted = sum(core.valid_source(f) for f in parsed.values())
    stages = {}
    for kind in ('raw_parsed', 'fixture_assisted'):
        corpus = list(parsed.values()) if kind == 'raw_parsed' else [core.Fact(**f) for f in payload['facts']]
        facts = {f.id: f for f in corpus}
        index = search.SearchIndex(corpus, 'hybrid_meta') if corpus else None
        # Raw answers/citations may use only parser output that exactly matches
        # the independently frozen source cells. Fixture stage uses supplied gold.
        registration = ({f.id: asdict(f) for f in corpus if f.id in gold and exact_fact(f, gold[f.id])}
                        if kind == 'raw_parsed' else {f.id: asdict(f) for f in corpus})
        with ExitStack() as stack:
            stack.enter_context(patch.object(core, 'source_manifest', return_value=manifest))
            stack.enter_context(patch.object(core, 'source_facts', return_value=registration))
            query_rows = [dict(id=q['id'], query=q['query'], expected_answerable=q['expected_answerable'],
                               expected_clarification=q['expected_clarification'], **query_observation(index, q)) for q in payload['retrieval_gold']]
            citation_rows = [{'fact_id': fid, 'passed': fid in facts and core.valid_source(facts[fid])} for fid in gold]
            calc_rows = [dict(id=c['id'], **calculation_observation(core, c, facts)) for c in payload['calculations']]
        positives = [r for r in query_rows if r['expected_answerable']]
        stages[kind] = {'adapter': 'isolated source_manifest + source_facts patches; production functions unchanged',
                        'registration': 'only exact independently audited parser outputs' if kind == 'raw_parsed' else 'gold fixtures supplied directly, not ingestion evidence',
                        'corpus_facts': len(corpus), 'queries': query_rows, 'query_summary': summarize(query_rows),
                        'citations': citation_rows, 'citation_summary': summarize(citation_rows),
                        'calculations': calc_rows, 'calculation_summary': summarize(calc_rows),
                        'positive_retrieval': {'n': len(positives), 'recall_at_1': sum(r['rank'] == 1 for r in positives) / len(positives),
                                               'recall_at_5': sum(r['rank'] is not None for r in positives) / len(positives),
                                               'mrr_at_5': sum(1/r['rank'] if r['rank'] else 0 for r in positives)/len(positives)}}
    hashes = {f'quarterguard/{name}.py': digest(code_root / 'quarterguard' / (name + '.py'))
              for name in ('core', 'ingest', 'search', 'query')
              if (code_root / 'quarterguard' / (name + '.py')).exists()}
    return {'schema_version': 1, 'label': label, 'evaluated_at': datetime.now(timezone.utc).isoformat(),
            'freeze_sha256': digest(data / 'freeze.json'), 'freeze': freeze,
            'implementation_hashes': hashes, 'evaluation_harness_sha256': digest(Path(__file__)),
            'human_reviewed': False, 'same_task_ai_authored': True, 'model_calls': 0, 'provider_api_cost_usd': 0,
            'cost_scope': 'Paid model APIs only; excludes local CPU, storage, and network',
            'source_audit': audits, 'raw_statements': statements, 'raw_statement_summary': summarize(statements),
            'raw_exact_cells': matches, 'raw_cell_summary': summarize(matches),
            'production_registry': {'accepted_parsed_facts': production_accepted, 'parsed_facts': len(parsed),
                                    'production_end_to_end_supported': production_accepted == len(parsed) and bool(parsed),
                                    'limitation': 'New documents are not added to production canonical registration by this evaluation.'},
            'stages': stages,
            'first_observed_failures': {'raw_statements': [r['id'] for r in statements if not r['passed']],
                                        **{kind: {'queries': [r['id'] for r in stage['queries'] if not r['passed']],
                                                  'calculations': [r['id'] for r in stage['calculations'] if not r['passed']]}
                                           for kind, stage in stages.items()}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / 'work/v2-blind-raw')
    parser.add_argument('--code-root', type=Path, default=ROOT)
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--label', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Exclusive artifact creation preserves first-observed outcomes and failures.
    if args.output.exists():
        raise ValueError('REFUSE_TO_OVERWRITE_FIRST_OBSERVATION: ' + str(args.output))
    result = evaluate(args.cache, args.code_root, args.label, args.data)
    with args.output.open('x') as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'label': args.label, 'raw_statements': result['raw_statement_summary'],
                      'raw_cells': result['raw_cell_summary'],
                      'stages': {k: {n: s[n] for n in ('query_summary', 'citation_summary', 'calculation_summary', 'positive_retrieval')}
                                 for k, s in result['stages'].items()}}, indent=2))


if __name__ == '__main__':
    main()
