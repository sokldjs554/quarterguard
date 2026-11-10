"""Reparse cached official PDF bytes; freeze new LLM tasks without model calls."""
from contextlib import ExitStack
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from quarterguard.store import ROOT
from quarterguard.ingest import parse_statement
from quarterguard.core import compare

OUT=ROOT/'data/llm-prose-v6-20261110/new-inputs.json'
SOURCES=[('v2-final','work/v2-blind-raw'),('hyundai-final-20261109','work/hyundai-final-20261109')]


def prepare():
    sources=[];facts={};audits=[]
    for dataset,cache in SOURCES:
        folder=ROOT/'data'/dataset
        source=json.loads((folder/'sources.json').read_text())[0]
        pdf=ROOT/cache/source['cache_filename']
        sha=hashlib.sha256(pdf.read_bytes()).hexdigest()
        if sha!=source['sha256']:raise ValueError('PDF_HASH_MISMATCH')
        reader=PdfReader(pdf);page=source['statement_pages']['CFS']
        if len(reader.pages)!=source['pages']:raise ValueError('PDF_PAGES_MISMATCH')
        # Real current parser output. Gold is only used AFTER parsing to compare.
        parsed=parse_statement(reader.pages[page-1].extract_text(),source,page,
                               metrics=['revenue','gross_profit','operating_profit','net_profit'])
        krw={f.id:f for f in parsed if f.currency=='KRW'}
        gold={f['id']:f for f in json.loads((folder/'facts.json').read_text())}
        if {k:asdict(v) for k,v in krw.items()}!=gold:raise ValueError('RAW_PARSE_GOLD_MISMATCH')
        facts.update(krw);sources.append(source)
        audits.append({'document_id':source['id'],'pdf_sha256':sha,'pdf_page':page,
                       'parsed_total':len(parsed),'krw_cells_compared':len(krw),
                       'gold_equal':True,'gold_source':str((folder/'facts.json').relative_to(ROOT)),
                       'input_origin':'raw PDF bytes -> pypdf -> current parser; gold not injected'})
    specs=[
        ('s22-op-yoy','삼성전자 2022년과 2021년 3분기 연결 영업이익의 전년 동분기 증감률을 설명하세요.',
         's22q3-CFS-operating_profit-2022-q-KRW','s22q3-CFS-operating_profit-2021-q-KRW','yoy',[]),
        ('s22-net-ytd-yoy','삼성전자 2022년과 2021년 9개월 누적 연결 당기순이익의 전년 동기 증감률과 출처를 설명하세요.',
         's22q3-CFS-net_profit-2022-ytd-KRW','s22q3-CFS-net_profit-2021-ytd-KRW','yoy',[]),
        ('s22-net-period','삼성전자 2022년 3개월과 2021년 9개월 연결 순이익의 비교 제한을 설명하세요. 근거가 없는 것인지 구분하세요.',
         's22q3-CFS-net_profit-2022-q-KRW','s22q3-CFS-net_profit-2021-ytd-KRW','yoy',['PERIOD_MISMATCH']),
        ('s22-op-qoq','Explain in Korean why 2022 Q3 and 2021 Q3 consolidated operating profit cannot be used for QoQ.',
         's22q3-CFS-operating_profit-2022-q-KRW','s22q3-CFS-operating_profit-2021-q-KRW','qoq',['PERIOD_MISMATCH']),
        ('h25-op-yoy','현대자동차 2025년과 2024년 3분기 연결 영업이익의 전년 동분기 증감률을 단위와 함께 설명하세요.',
         'h25q3-CFS-operating_profit-2025-q-KRW','h25q3-CFS-operating_profit-2024-q-KRW','yoy',[]),
        ('h25-net-yoy','Explain Hyundai Motor 2025 versus 2024 third-quarter-only consolidated net profit growth in Korean, with both source columns.',
         'h25q3-CFS-net_profit-2025-q-KRW','h25q3-CFS-net_profit-2024-q-KRW','yoy',[]),
        ('h25-op-period','현대자동차 2025년 9개월 누적과 2024년 단독3개월 연결 영업이익의 비교 제한을 설명하세요.',
         'h25q3-CFS-operating_profit-2025-ytd-KRW','h25q3-CFS-operating_profit-2024-q-KRW','yoy',['PERIOD_MISMATCH']),
        ('cross-company-period','삼성전자 2022년과 현대자동차 2025년 3분기 영업이익을 전년 동분기처럼 비교할 수 없는 이유와 각각의 보고서를 설명하세요.',
         's22q3-CFS-operating_profit-2022-q-KRW','h25q3-CFS-operating_profit-2025-q-KRW','yoy',['COMPANY_MISMATCH','PERIOD_MISMATCH']),
    ]
    registry={k:asdict(f) for k,f in facts.items()};manifest={s['id']:s for s in sources}
    cases=[]
    with ExitStack() as stack:
        stack.enter_context(patch('quarterguard.core.source_facts',return_value=registry))
        stack.enter_context(patch('quarterguard.core.source_manifest',return_value=manifest))
        for id_,task,a,b,mode,issues in specs:
            result=compare(facts[a],facts[b],mode)
            # Independent arithmetic on stored literal gold, not compare() output.
            expected=None if issues else str(((Decimal(registry[a]['value'])-Decimal(registry[b]['value']))
                *100/Decimal(registry[b]['value'])).quantize(Decimal('.0001')))
            if result['issues']!=issues or result['growth_pct']!=expected:raise ValueError('EXPECTED_RESULT_MISMATCH')
            cases.append({'id':id_,'task':task,'cohort':'new_tasks_known_documents','tool_result':result,
                'expected_issues':issues,'expected_value':expected,'untrusted_draft':None,
                'input_origin':'new raw-PDF parsing and direct compare() in isolated registry; no MCP wire execution'})
    return {'production_revision_before_task_selection':'3c747d3901c2401a41e56f4540ee4e7cf9a9f3c6',
        'sources':sources,'facts':registry,'source_audits':audits,'cases':cases,
        'selection':'Eight LLM tasks selected after prose policy was fixed; existing parser evaluation documents and values, not independently unseen documents. Operating/net profit rows avoid Sales/Revenue normalization as a confound.',
        'gold_author':'same-task AI; stored source-cell gold and independent difference/base arithmetic',
        'new_task_human_reviewed':False,'new_model_calls':0}


if __name__=='__main__':
    if OUT.exists():raise ValueError('REFUSE_OVERWRITE')
    data=prepare();OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'cases':len(data['cases']),'source_audits':data['source_audits'],'paid_calls':0},ensure_ascii=False))
