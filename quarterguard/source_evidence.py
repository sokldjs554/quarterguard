"""Bounded, deterministic source evidence. These cells are NOT worksheet Facts.

Supports selected tables of one pinned SK hynix PDF. Instant balances retain an
as_of date, never a fabricated 12-month period. No answer calculation here.
"""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from .store import ROOT

DOCUMENT_ID = 'skh2024annual-in-2025oc'
PDF_SHA = '3b06e43298560053e2b6d9a79861c1ef505880879142242200e2d2ce06421f7c'
URL = 'https://links.sgx.com/FileOpen/SK%20hynix%20Inc._2025%20-%20Final%20Offering%20Circular%20%289.4.25%29.ashx?App=Prospectus&FileID=67332'
TITLE = 'SK hynix 2025 Offering Circular · 2024·2023 연결재무제표'
DATA = ROOT / 'data/source-evidence'
TABLES = {
    191: ('F-73','financial-position','Consolidated Statements of Financial Position','instant',[
        ('cash','Cash and cash equivalents','5,6'),('inventory','Inventories, net','9')]),
    193: ('F-75','income','Consolidated Statements of Comprehensive Income (Loss)','duration',[
        ('revenue','Revenue','4,24,31'),('cost_of_sales','Cost of sales','26,31'),
        ('operating_profit','Operating profit (loss)','')]),
    264: ('F-146','note-24-2','Notes to the Consolidated Financial Statements','duration',[
        ('dram','DRAM',''),('nand','NAND Flash',''),('other_products','Others',''),('product_total','','')]),
}
MONEY = r'(?:\(\d{1,3}(?:,\d{3})+\)|\d{1,3}(?:,\d{3})+)'


def _normalize(text):
    # pypdf may split the last comma group: 23,467,3 19. Join only a partial
    # comma group whose two fragments total three digits, not valid amounts.
    pattern = r'(?<![\d,])(\d{1,3}(?:,\d{3})*,)(\d{1,2})[ \t]+(\d{1,2})(?=\)?(?:\s|$))'
    return re.sub(pattern,lambda m: m[1]+m[2]+m[3] if len(m[2]+m[3])==3 else m[0],text)


def parse_page(text, page):
    """Parse the selected rows; reject incomplete/ambiguous headers or amounts.

    Text-only callers are fixture tests. Only parse_pdf verifies source identity.
    """
    if page not in TABLES: raise ValueError('UNSUPPORTED_PAGE')
    printed,table,title,kind,rows=TABLES[page]
    normalized=_normalize(text)
    flat=re.sub(r'\s+',' ',normalized).strip()
    required=['SK hynix Inc. and Subsidiaries',title,'December 31, 2024 and 2023',printed]
    if not all(s in flat for s in required): raise ValueError('SOURCE_HEADER_MISMATCH')
    if kind=='duration' and page!=264 and 'Years ended December 31, 2024 and 2023' not in flat:
        raise ValueError('ANNUAL_PERIOD_REQUIRED')
    block=normalized
    if page==264:
        parts=re.findall(r'\(2\)(.*?)\(3\)',block,re.S)
        if len(parts)!=1: raise ValueError('AMBIGUOUS_PRODUCT_SUBSECTION')
        block=parts[0]
        prose=re.sub(r'\s+',' ',block).replace('a nd','and')
        if not all(x in prose for x in ['revenue by product and service types','years ended December 31, 2024 and 2023']):
            raise ValueError('PRODUCT_PERIOD_REQUIRED')
    unit=r'\(In millions of Korean won(?:, except per share information)?\)\s*(?:Notes\s*)?2024[ \t]+2023[ \t]*\n'
    if len(re.findall(unit,block))!=1: raise ValueError('UNIT_OR_COLUMN_HEADER_MISMATCH')
    cells=[]
    for metric,row,notes in rows:
        prefix=re.escape(row)+(r'\s+'+re.escape(notes) if notes else '')
        # Exact full lines: any extra numeric or footnote column is rejected.
        pattern=r'^\s*'+prefix+r'\s*(?:W\s*)?('+MONEY+r')\s+(?:W\s*)?('+MONEY+r')\s*$'
        matches=list(re.finditer(pattern,block,re.M))
        if len(matches)!=1: raise ValueError('AMBIGUOUS_OR_UNSUPPORTED_ROW: '+metric)
        match=matches[0]
        # Reject a second occurrence of a labelled row even if malformed.
        if row and len(re.findall(r'^\s*'+re.escape(row)+r'(?=\s)',block,re.M))!=1:
            raise ValueError('DUPLICATE_ROW: '+metric)
        for column,year in enumerate((2024,2023),1):
            raw=match[column]; value=raw.replace(',','').replace('(','-').replace(')','')
            cells.append({'id':f'{DOCUMENT_ID}:{table}:{metric}:{year}',
                'document_id':DOCUMENT_ID,'document_sha256':PDF_SHA,'source_url':URL,
                'company':'skhynix','scope':'CFS','currency':'KRW','scale':1000000,
                'metric':metric,'value':value,'raw_value':raw,'year':year,
                'period_kind':kind,'as_of':f'{year}-12-31' if kind=='instant' else None,
                'start':f'{year}-01-01' if kind=='duration' else None,
                'end':f'{year}-12-31' if kind=='duration' else None,
                'page':page,'printed_page':printed,'table_id':table,
                'table_title':title+(' · 24. Revenue (2) product and service types' if page==264 else ''),
                'row':row,'row_role':'total' if metric=='product_total' else 'labelled',
                'column':str(year),'amount_column':column,
                'raw_line':match[0].strip(),'text_sha256':hashlib.sha256(text.encode()).hexdigest()})
    if page==264:
        for year in (2024,2023):
            values={c['metric']:Decimal(c['value']) for c in cells if c['year']==year}
            if sum(values[k] for k in ('dram','nand','other_products'))!=values['product_total']:
                raise ValueError('PRODUCT_TOTAL_MISMATCH')
    return cells


def parse_pdf(path):
    """Raw PDF -> pypdf -> bounded tables; hash and physical page labels checked."""
    from pypdf import PdfReader
    path=Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=PDF_SHA: raise ValueError('UNSUPPORTED_PDF_HASH')
    reader=PdfReader(path)
    if len(reader.pages)!=291: raise ValueError('PAGE_COUNT_MISMATCH')
    return [c for page in TABLES for c in parse_page(reader.pages[page-1].extract_text() or '',page)]


def load_source():
    manifest=json.loads((DATA/'manifest.json').read_text())
    raw=(DATA/'cells.json').read_bytes()
    if (manifest['id']!=DOCUMENT_ID or manifest['sha256']!=PDF_SHA or
            hashlib.sha256(raw).hexdigest()!=manifest['cells_sha256']):
        raise ValueError('SOURCE_EVIDENCE_INTEGRITY')
    cells=json.loads(raw)
    if len(cells)!=18 or len({c['id'] for c in cells})!=18:
        raise ValueError('SOURCE_CELL_COUNT')
    return manifest,cells


def get_cell(cell_id):
    if cell_id.startswith('apple-2024-10k:'):
        from .apple_source import get_cell as apple_cell
        return apple_cell(cell_id)
    for cell in load_source()[1]:
        if cell['id']==cell_id: return cell
    raise ValueError('UNKNOWN_SOURCE_CELL')

METRICS = [
    ('cost_of_sales',r'매출원가|cost of sales'),
    ('operating_profit',r'영업(?:이익|손실)|operating (?:profit|loss)'),
    ('cash',r'현금(?:및현금성자산)?|cash(?: and cash equivalents)?'),
    ('inventory',r'재고(?:자산)?|inventor(?:y|ies)(?:,? net)?'),
    ('dram',r'\bdram\b'),('nand',r'\bnand(?: flash)?\b'),
    ('revenue',r'매출(?:액)?|revenue|sales'),
]
ISSUE_TEXT = {
    'YEAR_REQUIRED':'대상 연도를 선택해 주세요. 아래는 문서의 두 연도 후보입니다.',
    'CURRENT_YEAR_CONFIRMATION':'질문에 기준 연도가 없어 문서의 2024·2023년 후보를 함께 표시합니다. 비교할 연도를 확인해 주세요.',
    'COMPARATIVE_COLUMNS':'변화 질문에 문서의 두 연도 후보를 함께 표시합니다. 비교 조건을 확인해 주세요.',
    'RATIO_DEFINITION_REQUIRED':'재고의 기준일·평균 여부와 분모의 기간·매출 또는 매출원가를 정해야 합니다. 비율은 계산하지 않았습니다.',
    'NEGATIVE_BASE_POLICY':'문서에 음수인 영업손익이 있습니다. 음수 기준값의 증감률 해석은 확인이 필요하며 계산하지 않았습니다.',
    'UNSUPPORTED_CONTEXT':'질문의 기업·범위·기간·통화·단위가 이 문서의 지원 범위와 다릅니다.',
    'UNSUPPORTED_TERMS':'해석하지 못한 조건이 있습니다. 지원 항목과 연도를 직접 지정해 주세요.',
    'YEAR_BINDING_CONFIRMATION':'항목 뒤에 연도가 있어 각 항목의 연도를 확정하지 못했습니다. 아래는 두 연도의 후보이며, 연도를 항목 앞에 적어 다시 검색해 주세요.',
    'METRIC_REQUIRED':'지원하는 항목을 지정해 주세요: 현금, 재고, 매출, 매출원가, 영업손익, DRAM, NAND.',
}


def search_source(document_id,query):
    """Conservative rule-based candidate retrieval in an explicitly selected PDF.

    Does not infer a verified answer or calculate ratios. Human questions are
    development inputs; conditions outside this bounded vocabulary block hits.
    """
    if document_id=='apple-2024-10k':
        from .apple_review import search
        return search(query)
    if document_id!=DOCUMENT_ID: raise ValueError('UNKNOWN_SOURCE_DOCUMENT')
    if not isinstance(query,str) or len(query)>500: raise ValueError('INVALID_QUERY')
    manifest,cells=load_source()
    q=query.lower().strip()
    issues=[]
    context={'source':'selected_document','document_id':document_id,'title':manifest['title'],
        'company':'skhynix','scope':'CFS','currency':'KRW','scale':1000000,
        'available_years':[2024,2023],
        'note':'기업·연결·원화·백만 원은 선택한 문서의 조건입니다. 질문에서 모두 명시한 조건은 아닙니다.'}
    result={'status':'needs_clarification','answer_status':'not_calculated','calculated_answer':None,
        'context':context,'hits':[],'issues':issues,'messages':[],
        'blocked':False,'unknown_terms':[], 'execution':'deterministic_source_retrieval'}
    years={int(x) for x in re.findall(r'(?<!\d)(\d{4})(?!\d)',q)}
    blocked_terms=r'삼성|samsung|현대|hyundai|별도|개별|separate|standalone|\bofs\b|\busd\b|\beur\b|달러|유로|억원|천원|조원|billion|thousand|분기|quarter|\bq[1-4]\b|반기|half.year|누적|ytd|예상|forecast|조정|adjusted|제외|아닌|\bnot\b|평균|average'
    if years-{2024,2023} or re.search(blocked_terms,q) or re.search(r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',q): issues.append('UNSUPPORTED_CONTEXT')
    # Match longest metric aliases first, masking each span to avoid treating
    # 매출원가 as 매출 and to retain year bindings in mixed-metric requests.
    masked=q;mentions=[]
    for metric,pattern in METRICS:
        for m in list(re.finditer(pattern,masked)):
            mentions.append((m.start(),m.end(),metric))
            masked=masked[:m.start()]+' '*(m.end()-m.start())+masked[m.end():]
    mentions.sort()
    # 'DRAM revenue' is one product phrase; a separate revenue mention must
    # survive. Do not discard all revenue merely because a product occurs.
    qualified=[]
    for i,mention in enumerate(mentions):
        start,end,metric=mention
        if metric=='revenue' and i and mentions[i-1][2] in {'dram','nand'} and not q[mentions[i-1][1]:start].strip():
            continue
        qualified.append(mention)
    mentions=qualified
    product={m[2] for m in mentions} & {'dram','nand'}
    share=bool(re.search(r'비중|몇\s*%|share|percentage',q)) and bool(product)
    if share:
        mentions=[(a,b,'product_total' if metric=='revenue' and re.search(r'(?:전체|총|total)\s*$',q[:a]) else metric) for a,b,metric in mentions]
    metrics={m[2] for m in mentions}
    if share:metrics.add('product_total')
    ratio=bool(re.search(r'개월분|months? of',q)) and {'inventory','revenue'}<=metrics
    # A deliberately bounded grammar: unknown qualifiers do not get ignored.
    rest=re.sub(r'sk\s*하이닉스|sk\s*hynix(?: inc\.?)?|하이닉스|연결|consolidated|cfs|krw|원화|백만\s*원|million|20\d{2}년?|전체|총|기말|연말|연간|말보다|얼마나|늘었나|늘어난|함께|증가했다고|증가했나|증가|감소|표현해도|되나|인가|개월분인지|개월분|공시표만으로|단정할|있나|수|몇|비중|보다|cash|in|at|end|of|year|annual|total|share|percentage|how|much|grew|growth|change|compare|and|to|the', ' ',masked)
    rest=re.sub(r'[은는이가의을를에와과말]|[\s%?.,!·:()~\-–/]+','',rest)
    if rest:result['unknown_terms']=[rest];issues.append('UNSUPPORTED_TERMS')
    if not metrics:issues.append('METRIC_REQUIRED')
    if issues:
        result['blocked']=True;result['messages']=[ISSUE_TEXT[i] for i in issues];return result
    comparative=bool(re.search(r'늘|증가|감소|보다|grew|growth|change|compare',q)) and not ratio and not share
    selected_years=years or {2024,2023}
    if not years:issues.append('YEAR_REQUIRED')
    if comparative and len(years)<2:
        selected_years={2024,2023}
        issues.append('CURRENT_YEAR_CONFIRMATION' if 2024 not in years else 'COMPARATIVE_COLUMNS')
    # When separate metrics have separate preceding years, keep that binding.
    # Example: 2024 inventory / 2023 revenue. Unclear bindings stay candidates.
    bindings={}
    if len(metrics)>1 and len(years)>1:
        # Shared prefix years apply to all following metrics. With a year in
        # the tail, prefix-vs-suffix grammar is uncertain: show both columns
        # and ask, rather than silently assigning the nearest preceding year.
        if mentions and re.search(r'\d{4}',q[mentions[-1][1]:]):
            issues.append('YEAR_BINDING_CONFIRMATION')
        else:
            previous_end=0; local_years=selected_years
            for start,end,metric in mentions:
                stated={int(y) for y in re.findall(r'\d{4}',q[previous_end:start])}
                if stated: local_years=stated
                bindings.setdefault(metric,set()).update(local_years)
                previous_end=end
    if share and 'product_total' not in bindings:
        bindings['product_total']=set().union(*(bindings.get(p,selected_years) for p in product))
    for cell in cells:
        if cell['metric'] in metrics and cell['year'] in bindings.get(cell['metric'],selected_years):
            result['hits'].append({'cell':cell,'role':'requested_evidence'})
    if ratio:
        issues.append('RATIO_DEFINITION_REQUIRED')
        for cell in cells:
            if cell['metric']=='cost_of_sales' and cell['year'] in bindings.get('revenue',selected_years):
                result['hits'].append({'cell':cell,'role':'related_definition'})
    if 'operating_profit' in metrics and comparative and any(Decimal(h['cell']['value'])<0 for h in result['hits']):
        issues.append('NEGATIVE_BASE_POLICY')
    result['status']='needs_clarification' if issues else 'evidence_candidates'
    result['messages']=[ISSUE_TEXT[i] for i in issues]
    return result
