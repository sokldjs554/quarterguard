"""Read-only baseline for a user-authored submission; no LLM or product edits.

Three scopes: raw PDF -> existing parser, current production-corpus search,
and an explicitly hand-prepared two-cell fixture testing the negative-base guard.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from quarterguard.core import Fact, compare
from quarterguard.ingest import parse_statement
from quarterguard.search import SearchIndex
from quarterguard.store import ROOT, load_facts

DATA = ROOT / 'data/skhynix-human-20261111'
PDF_SHA = '3b06e43298560053e2b6d9a79861c1ef505880879142242200e2d2ce06421f7c'
URL = 'https://links.sgx.com/FileOpen/SK%20hynix%20Inc._2025%20-%20Final%20Offering%20Circular%20%289.4.25%29.ashx?App=Prospectus&FileID=67332'
PAGES = {'F-73': 191, 'F-75': 193, 'F-146': 264}


def run(pdf, output):
    output.mkdir(parents=True, exist_ok=False)
    frozen = json.loads((DATA/'freeze.json').read_text())
    for name, sha in frozen['files'].items():
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('SUBMISSION_CHANGED')
    raw=pdf.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PDF_SHA:raise ValueError('PDF_CHANGED')
    reader=PdfReader(pdf)
    if len(reader.pages)!=291:raise ValueError('PAGE_COUNT_CHANGED')
    doc={'id':'skh2024annual-in-2025oc','company':'skhynix','scope':'CFS',
         'url':URL,'sha256':PDF_SHA,'pages':291,'report_end':'2024-12-31',
         'quarter':None,'period_kind':'annual'}
    parsing=[]
    for label,page in PAGES.items():
        text=reader.pages[page-1].extract_text() or ''
        if label not in text:raise ValueError('PRINTED_PAGE_LABEL_MISMATCH')
        (output/f'pdf-{page}-{label}.txt').write_text(text)
        entry={'printed_page':label,'pdf_page_1based':page,
               'text_sha256':hashlib.sha256(text.encode()).hexdigest()}
        try:
            facts=parse_statement(text,doc|{'statement_pages':{'CFS':page}},page)
            entry.update(status='parsed',facts=[x.public() for x in facts])
        except ValueError as e:entry.update(status='unsupported',error=str(e),facts=[])
        parsing.append(entry)
    cases=json.loads((DATA/'cases.json').read_text());index=SearchIndex(load_facts())
    header=(DATA/'submitted.md').read_text().split('\n\n## 1.')[0]
    # Questions are untouched; header-context execution is a separately labelled input.
    searches=[]
    for c in cases:
        searches.append({'id':c['id'],'literal_question':c['question'],
            'literal_result':index.search_with_diagnostics(c['question']),
            'with_submitted_header_query':header+'\n'+c['question'],
            'with_submitted_header_result':index.search_with_diagnostics(header+'\n'+c['question'])})
    # Manual fixture from the two verified F-75 cells. NOT emitted by parser.
    facts=[]
    for year,amount in [('2024','23467319'),('2023','-7730313')]:
        facts.append(Fact(id=f'skh-{year}-operating_profit-manual',company='skhynix',
            metric='operating_profit',scope='CFS',currency='KRW',scale=1000000,
            start=f'{year}-01-01',end=f'{year}-12-31',value=amount,source_url=URL,
            page=193,row='Operating profit',column=f'{year} YTD KRW',
            document_id=doc['id'],document_sha256=PDF_SHA))
    manifest={doc['id']:doc|{'statement_pages':{'CFS':193}}}
    with patch('quarterguard.core.source_manifest',return_value=manifest), \
            patch('quarterguard.core.source_facts',return_value={x.id:asdict(x) for x in facts}):
        guard=compare(*facts,'yoy')
    assert guard['issues']==['NEGATIVE_BASE'] and guard['growth_pct'] is None
    D=Decimal
    arithmetic={'cash_difference_million_krw':str(D('11205117')-D('7587329')),
        'cash_change_pct':str(((D('11205117')/D('7587329')-1)*100).quantize(D('.0001'))),
        'inventory_difference_million_krw':str(D('13313937')-D('13480659')),
        'dram_share_pct':str((D('44731664')/D('66192960')*100).quantize(D('.0001'))),
        'operating_profit_difference_million_krw':str(D('23467319')-D('-7730313'))}
    report={'at_utc':datetime.now(timezone.utc).isoformat(),'baseline_commit':frozen['base_commit'],
        'pdf':{'url':URL,'sha256':PDF_SHA,'pages':291,'page_mapping':PAGES},
        'raw_pdf_to_existing_parser':parsing,'current_corpus_search':searches,
        'manual_fixture_negative_base':{'origin':'AI hand-prepared from source cells; not parser output',
            'normalization':'literal Operating profit (loss) -> canonical Operating profit; annual -> 12-month YTD',
            'production_registry_modified':False,'result':guard},
        'manual_value_arithmetic':{'origin':'Decimal recomputation of supplied and PDF-checked values, not product answer generation','results':arithmetic},
        'original_question_answers_generated_by_product':0,'paid_api_calls':0,
        'new_model_generations':0,'new_external_participants':0,
        'limitations':['Selected pages/rows provided by user; no automatic document discovery.',
            'Search diagnostics are generic rejection, not financial-reasoning success on Q4/Q5.',
            'No SK hynix production source registration or parser implementation.',
            'Source-image review by AI is separate from user-reported human authorship.']}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'parsed_pages':sum(x['status']=='parsed' for x in parsing),
        'parser_attempts':len(parsing),'literal_hits':[len(x['literal_result']['hits']) for x in searches],
        'header_hits':[len(x['with_submitted_header_result']['hits']) for x in searches],
        'negative_base':guard['issues'],'arithmetic':arithmetic,'paid_calls':0},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();run(args.pdf,args.output)
