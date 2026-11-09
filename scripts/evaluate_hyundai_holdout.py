#!/usr/bin/env python3
"""Audit frozen Hyundai source cells and use the existing isolated evaluation adapter.

Outputs are exclusively created. No gold, source registry, or historical artifact
is modified. Run each code-root in a fresh Python process.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hyundai-holdout-20261109'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_sources(payload, cache):
    """Independent PDF-byte/header/ordered-literal-cell audit; no parser usage."""
    from pypdf import PdfReader
    facts = {f['id']: f for f in payload['facts']}
    pages, audits = {}, []
    for source in payload['sources']:
        path = cache / source['cache_filename']
        if digest(path) != source['sha256']:
            raise ValueError('SOURCE_HASH_CHANGED: ' + source['id'])
        reader = PdfReader(path)
        if len(reader.pages) != source['pages']:
            raise ValueError('SOURCE_PAGE_COUNT_CHANGED')
        for scope, page in source['statement_pages'].items():
            text = reader.pages[page - 1].extract_text() or ''
            pages[source['id'], scope] = text
            flat = re.sub(r'\s+', ' ', text)
            year = int(source['report_end'][:4])
            heading = (f'FOR THE THREE-MONTH AND NINE-MONTH PERIODS ENDED SEPTEMBER 30, '
                       f'{year} AND {year-1} (Unaudited) {year} {year-1} NOTES ')
            period_pair = 'Three-month period ended September 30 Nine-month period ended September 30 '
            header_ok = ('HYUNDAI MOTOR COMPANY AND ITS SUBSIDIARIES' in flat
                         and 'INTERIM CONSOLIDATED STATEMENTS OF INCOME' in flat
                         and heading + period_pair * 2 in flat and scope == 'CFS')
            for cell in payload['source_cells']:
                fact = facts[cell['fact_id']]
                if fact['document_id'] != source['id'] or fact['scope'] != scope:
                    continue
                lines = re.findall(r'^' + re.escape(cell['source_row']) + r'\s+([^\n]+)', text, re.MULTILINE)
                tokens = re.findall(r'(?<![\d,])\d{1,3}(?:,\d{3})+(?![\d,])', lines[0]) if len(lines) == 1 else []
                literal = tokens[cell['data_column_index_1based'] - 1] if len(tokens) == 4 else None
                ordinal = cell['data_column_index_1based']
                column_year = year if ordinal <= 2 else year - 1
                quarter = ordinal % 2 == 1
                expected_start = f'{column_year}-' + ('07-01' if quarter else '01-01')
                passed = (header_ok and cell['source_unit'] in flat and literal == cell['literal_cell']
                          and literal.replace(',', '') == fact['value']
                          and fact['start'] == expected_start and fact['end'] == f'{column_year}-09-30'
                          and cell['header_year'] == column_year and fact['currency'] == 'KRW'
                          and fact['scale'] == 1000000 and fact['page'] == page
                          and fact['document_sha256'] == source['sha256'])
                audits.append({'fact_id': fact['id'], 'literal_cell': literal,
                               'source_column_1based': ordinal, 'header_verified': header_ok, 'passed': passed})
    if len(audits) != len(facts) or not all(a['passed'] for a in audits):
        raise ValueError('GOLD_SOURCE_AUDIT_FAILED: ' + json.dumps(audits))
    return pages, audits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, default=ROOT)
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--cache', type=Path, default=ROOT / 'work/hyundai-holdout-20261109')
    parser.add_argument('--label', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('REFUSE_TO_OVERWRITE_OBSERVATION: ' + str(args.output))
    adapter_path = ROOT / 'quarterguard/evaluation_v2.py'
    spec = importlib.util.spec_from_file_location('hyundai_isolated_adapter', adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    adapter.audit_sources = audit_sources
    result = adapter.evaluate(args.cache, args.code_root.resolve(), args.label, args.data)
    result['evaluation_harness_sha256'] = digest(__file__)
    result['isolated_adapter_sha256'] = digest(adapter_path)
    result['implementation_module_hashes'] = {str(p.relative_to(args.code_root.resolve())): digest(p)
                                              for p in sorted((args.code_root.resolve() / 'quarterguard').glob('*.py'))}
    result['expert_gold'] = False
    result['limitations'] = [
        'AI-authored, AI-inspected source cells; no independent human or expert review.',
        'One newly acquired Hyundai consolidated statement; not broad issuer/layout coverage.',
        'Comparative prior-year values may overlap disclosed data; only this document was newly withheld.',
        'Raw downstream uses exact audited parser outputs with an isolated source registry adapter.',
        'Production corpus and allowlist are unchanged; fixture-assisted results are diagnostic only.',
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(args.output), 'raw_statements': result['raw_statement_summary'],
                      'raw_cells': result['raw_cell_summary'],
                      'stages': {k: {name: value for name, value in v.items() if name.endswith('_summary')}
                                 for k, v in result['stages'].items()},
                      'failures': result['first_observed_failures']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
