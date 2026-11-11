"""Bounded Korean/English source review. Rules select operations; no LLM or gold answers.

The selected document supplies company/currency/scope and, only for explicitly
comparative operations, its two year columns. The response discloses this context.
Unrecognized qualifiers or unsupported periods never produce financial values.
"""
import re
from decimal import Decimal, ROUND_HALF_EVEN
from . import apple_source as src

LABELS={'gross_margin':'제품·서비스 매출총이익률','regional_change':'중국권·전체 보고 매출 변화',
 'operating_cash_less_capex':'영업현금흐름에서 유형자산 취득 지출 차감','buyback_change':'자사주 매입 지출액 변화',
 'tax_bridge':'영업이익·법인세비용·순이익 변화 대조','aggregate_limit':'집계 수익성의 개별 항목 일반화 한계',
 'china_causality':'중국권 매출 감소의 판매량 단독 원인 판단'}
REQUIRED={
 'gross_margin':['products_sales','services_sales','products_cost','services_cost'],
 'aggregate_limit':['products_sales','services_sales','products_cost','services_cost'],
 'regional_change':['china_sales','total_sales'],
 'china_causality':['china_sales'],
 'operating_cash_less_capex':['operating_cash','capex_payment'],
 'buyback_change':['buyback_payment'],
 'tax_bridge':['operating_profit','tax_expense','net_income','state_aid_tax']}
COMPARATIVE={'regional_change','china_causality','buyback_change','tax_bridge'}
MESSAGES={
 'UNSUPPORTED_CONTEXT':'선택 문서는 Apple의 2024·2023 회계연도 연결·USD·백만 달러 자료입니다. 다른 기업·기간·범위·단위 조건은 지원하지 않습니다.',
 'UNSUPPORTED_TERMS':'해석하지 못한 표현이 있어 계산을 보류했습니다. 지원 작업과 조건을 확인해 주세요.',
 'UNSUPPORTED_OPERATION':'이 질문의 계산·판단 방식을 지원 범위에서 확정하지 못했습니다.',
 'YEAR_REQUIRED':'2024 또는 2023 회계연도를 명시해 주세요.',
 'YEAR_DIRECTION_REQUIRED':'비교 방향을 확정할 수 없습니다. 2023년 대비 2024년의 변화를 지정해 주세요.',
 'SOURCE_CONTEXT_MISMATCH':'원문 수치의 기업·기간·통화·범위·단위·항목을 확인하지 못해 계산하지 않았습니다.',
 'NONPOSITIVE_SALES':'매출이 양수가 아니어서 매출총이익률을 계산하지 않았습니다.',
 'AGGREGATE_NOT_INDIVIDUAL':'집계 매출총이익률만으로 모든 개별 제품이 모든 개별 서비스보다 수익성이 낮다고 확정할 수 없습니다.',
 'CAUSAL_DECOMPOSITION_REQUIRED':'중국권 매출 감소를 판매량 감소만으로 설명할 수 없습니다. 원문은 제품 매출 감소와 환율 영향을 함께 언급하며 요인별 기여도를 제공하지 않습니다.'}

def interpret(query):
    if not isinstance(query,str) or len(query)>500:raise ValueError('INVALID_QUERY')
    q=query.lower().strip();issues=[]
    years={int(y) for y in re.findall(r'(?<!\d)(\d{4})(?!\d)',q)}
    blocked=r'삼성|samsung|현대|hyundai|하이닉스|hynix|별도|standalone|separate|\bofs\b|\bkrw\b|\beur\b|원화|유로|백만\s*원|억원|billion|thousand|분기|quarter|\bq[1-4]\b|반기|누적|ytd|예상|forecast|adjusted|조정|제외|아닌|아님|\bnot\b|평균|average|가정|원인만|1월|12월'
    if years-{2023,2024} or re.search(blocked,q) or re.search(r'\d{4}[-/.]\d',q):issues.append('UNSUPPORTED_CONTEXT')
    margin=bool(re.search(r'매출총이익률|gross margin',q));products=bool(re.search(r'제품|products?',q));services=bool(re.search(r'서비스|services?',q))
    china=bool(re.search(r'중국권|greater china',q));sales=bool(re.search(r'매출|sales|revenue',q));total=bool(re.search(r'전체|total',q))
    mode=None
    if margin and products and services:
        mode='aggregate_limit' if re.search(r'모든|개별|every|individual|\ball\b',q) else 'gross_margin'
    elif china and re.search(r'판매량|volume',q):mode='china_causality'
    elif china and sales and total:mode='regional_change'
    elif re.search(r'영업현금흐름|operating cash flow',q) and re.search(r'유형자산|capex|capital expenditure',q) and re.search(r'뺀|차감|minus|less|subtract',q):mode='operating_cash_less_capex'
    elif re.search(r'자사주|buyback|repurchases?',q) and re.search(r'늘|증가|change|increase',q):mode='buyback_change'
    elif re.search(r'법인세|tax',q) and re.search(r'순이익|net income',q) and re.search(r'영업이익|operating income',q):mode='tax_bridge'
    if mode is None:issues.append('UNSUPPORTED_OPERATION')
    # All remaining words must belong to the bounded supported grammar.
    # This is deliberately conservative: qualifiers are never silently dropped.
    fields={
        'gross_margin':r'매출총이익률|gross margin|수익성|제품|서비스|products?|services?',
        'aggregate_limit':r'매출총이익률|gross margin|수익성|제품|서비스|products?|services?|individual|every|all',
        'regional_change':r'greater china|중국권|전체|total|매출|sales|revenue',
        'china_causality':r'greater china|중국권|매출|sales|revenue|판매량|volume',
        'operating_cash_less_capex':r'operating cash flow|영업현금흐름|capital expenditure|capex|유형자산|취득액|금액',
        'buyback_change':r'자사주|현금|cash|buybacks?|repurchases?|spending',
        'tax_bridge':r'operating income|영업이익|net income|순이익|법인세|tax(?:es)?|수치',
    }
    aliases=fields.get(mode,r'(?!)')+r'|회계연도|재무제표|apple|애플|consolidated|연결|usd|백만 달러|million'
    rest=re.sub(aliases,' ',q)
    rest=re.sub(r'20\d{2}',' ',rest)
    allowed={'도','에','에서','의','년','년에','년보다','는','은','이','가','을','를','과','와','중','쪽의','어느','더','높았나','줄었는데도','늘었나','얼마인가','얼마나','뺀','차감','매입에','쓴','늘었는데','줄어든','이유를','일부','설명할','수','있나','낮으니','모든','개별','보다','낮다고','볼','감소는','감소만으로','감소','높은가','비교','비교해줘','비교하면','대비','증가','변화','달러','단위로','로','및','만으로','the','a','an','of','in','and','or','for','which','higher','is','was','than','did','grow','despite','decline','how','much','from','to','by','can','explain','only','why','with','versus','vs','fy','year','annual'}
    if mode=='operating_cash_less_capex':allowed|={'minus','less','subtract'}
    if mode in COMPARATIVE:allowed|={'change','increase'}
    else:allowed-={'늘었나','증가','변화','grow','decline','줄었는데도','늘었는데','줄어든','감소'}
    if mode!='operating_cash_less_capex':allowed-={'뺀','차감','minus','less','subtract'}
    tokens=re.findall(r'[^\s?.,!·:()~—–/]+',rest)
    unknown=[t for t in tokens if t not in allowed]
    if unknown:issues.append('UNSUPPORTED_TERMS')
    if mode=='operating_cash_less_capex':
        ordered=(re.search(r'영업현금흐름에서\s*유형자산\s*취득액을\s*(?:뺀|차감)',q)
                 or re.search(r'operating cash flow\s+(?:minus|less)\s+(?:capex|capital expenditure)',q)
                 or re.search(r'subtract\s+(?:capex|capital expenditure)\s+from\s+operating cash flow',q))
        single=(len(re.findall(r'영업현금흐름|operating cash flow',q))==1 and len(re.findall(r'유형자산|capex|capital expenditure',q))==1 and len(re.findall(r'뺀|차감|minus|less|subtract',q))==1)
        if not ordered or not single:issues.append('UNSUPPORTED_OPERATION')
    current=2024;base=2023;origin='query'
    if mode in COMPARATIVE:
        sequence=re.findall(r'(?<!\d)(202[34])(?!\d)',q)
        explicit_forward=bool(re.search(r'2023(?:년)?\s*(?:대비|보다|to)\s*2024',q))
        if (years=={2023} or re.search(r'2024(?:년)?\s*(?:대비|보다|to)\s*2023',q)
                or (len(years)==2 and sequence[0]=='2023' and not explicit_forward)):
            issues.append('YEAR_DIRECTION_REQUIRED')
        if not years:origin='selected_document_comparative_columns'
    else:
        if not years:issues.append('YEAR_REQUIRED')
        elif len(years)!=1:issues.append('YEAR_DIRECTION_REQUIRED')
        else:current=next(iter(years))
    return {'mode':mode,'issues':list(dict.fromkeys(issues)),'unknown_terms':unknown,'current_year':current,'base_year':base,'years_origin':origin}

def prepare(query):
    m,e=src.load_source();p=interpret(query)
    context={'document_id':src.DOCUMENT_ID,'title':src.TITLE,'company':'apple','scope':'CFS','currency':'USD','scale':1000000,
        'current_year':p['current_year'],'base_year':p['base_year'] if p['mode'] in COMPARATIVE else None,
        'years_origin':p['years_origin'],'note':'기업·연결·USD·백만 달러는 선택한 문서의 조건입니다. 비교 질문에서 생략된 연도는 선택 문서의 2024·2023 열로 표시합니다.'}
    cells=[];narratives=[]
    if not p['issues']:
        years={2024,2023} if p['mode'] in COMPARATIVE else {p['current_year']}
        cells=[c for c in e['cells'] if c['metric'] in REQUIRED[p['mode']] and c['year'] in years]
        for n in e['narratives']:
            if n['key']=='fiscal_weeks' or p['mode']=='china_causality':narratives.append(n)
    return m,p,context,cells,narratives

def search(query):
    m,p,ctx,cells,narratives=prepare(query)
    return {'status':'needs_clarification' if p['issues'] else 'evidence_candidates','answer_status':'not_calculated','calculated_answer':None,
        'context':ctx,'hits':[{'cell':c,'role':'requested_evidence'} for c in cells],'narratives':narratives,
        'issues':p['issues'],'messages':[MESSAGES[i] for i in p['issues']],'unknown_terms':p['unknown_terms'],
        'blocked':bool(p['issues']),'operation':p['mode'],'operation_label':LABELS.get(p['mode']),
        'execution':'deterministic_source_retrieval','source_snapshot_sha256':m['evidence_sha256']}

def review(query):
    m,p,ctx,cells,narratives=prepare(query)
    issues=list(p['issues']);mode=p['mode']
    r={'document_id':src.DOCUMENT_ID,'query':query,'context':ctx,'operation':mode,'operation_label':LABELS.get(mode),
       'status':'needs_review','issues':issues,'messages':[],'unknown_terms':p['unknown_terms'],'warnings':[],
       'values':{},'formulas':[],'explanation':[],'required_information':[],
       'currency':'USD','scale':1000000,'unit_label':'백만 미국 달러','evidence':cells,'narratives':narratives,
       'source_snapshot_sha256':m['evidence_sha256'],'source_integrity':'registered_snapshot',
       'execution':'deterministic_source_review','trace_kind':'internal_rule_stages_not_MCP_calls','steps':[{'stage':'search_source_evidence','status':'blocked' if issues else 'completed','evidence_ids':[c['id'] for c in cells]}]}
    if issues:
        r['messages']=[MESSAGES[i] for i in issues];return r
    lookup={(c['metric'],c['year']):c for c in cells}
    required={(metric,year) for metric in REQUIRED[mode] for year in ((2024,) if metric=='state_aid_tax' else ((2024,2023) if mode in COMPARATIVE else (p['current_year'],)))}
    valid=set(lookup)==required and len(lookup)==len(cells)
    for c in cells:
        start,end,weeks=src.PERIODS[c['year']]
        valid=valid and (c['document_id']==src.DOCUMENT_ID and c['document_sha256']==src.SHA and c['company']=='apple' and c['scope']=='CFS' and c['currency']=='USD' and c['scale']==1000000 and c['period_kind']=='duration' and c['start']==start and c['end']==end and c['fiscal_weeks']==weeks and c['column']==str(c['year']) and bool(re.fullmatch(r'-?\d+',c['value'])))
    r['steps'] += [{'stage':'get_source_cell','status':'completed','evidence_ids':[c['id'] for c in cells]}, {'stage':'validate_source_context','status':'passed' if valid else 'failed'}]
    if not valid:
        issues.append('SOURCE_CONTEXT_MISMATCH');r['messages']=[MESSAGES[i] for i in issues];return r
    def value(metric,year=None):return Decimal(lookup[(metric,p['current_year'] if year is None else year)]['value'])
    def calc(key,result,formula,ids,unit='USD_million'):
        r['values'][key]=format(result,'f');r['formulas'].append({'key':key,'formula':formula,'input_ids':[lookup[x]['id'] for x in ids],'unit':unit})
    def delta(metric,key):calc(key,value(metric,2024)-value(metric,2023),'FY2024 - FY2023',[(metric,2024),(metric,2023)])
    if mode in COMPARATIVE:
        r['warnings'].append('2024 회계연도는 52주, 2023 회계연도는 53주입니다. 아래는 보고금액 변화이며 같은 주수로 조정한 성장 비교가 아닙니다.')
    if p['years_origin']!='query':r['warnings'].append('질문에 연도가 없어 선택 문서의 2023년 대비 2024년 열을 사용했습니다. 의도한 비교 연도인지 확인해 주세요.')
    year=p['current_year']
    if mode in ('gross_margin','aggregate_limit'):
        if any(value(f'{part}_sales')<=0 for part in ('products','services')):issues.append('NONPOSITIVE_SALES')
        else:
            for part in ('products','services'):
                sale,cost=value(part+'_sales'),value(part+'_cost')
                pct=((sale-cost)/sale*100).quantize(Decimal('.0001'),rounding=ROUND_HALF_EVEN)
                calc(part+'_margin_pct',pct,'(sales - cost_of_sales) / sales * 100',[(part+'_sales',year),(part+'_cost',year)],'percent')
            r['explanation'].append(f"{year} 회계연도 제품 집계 매출총이익률은 {r['values']['products_margin_pct']}%, 서비스 집계는 {r['values']['services_margin_pct']}%입니다. 순이익률이나 개별 항목 수익성은 아닙니다.")
        if mode=='aggregate_limit':
            issues.append('AGGREGATE_NOT_INDIVIDUAL');r['required_information']=['개별 제품·서비스 매출과 직접 대응 원가','공통비 배분 기준'];r['explanation'].append(MESSAGES['AGGREGATE_NOT_INDIVIDUAL'])
    elif mode=='regional_change':
        delta('china_sales','china_difference');delta('total_sales','total_difference')
        r['explanation'].append(f"2023년 대비 2024년 중국권 매출 변화는 {r['values']['china_difference']}백만 달러, 전체 매출 변화는 {r['values']['total_difference']}백만 달러입니다.")
    elif mode=='operating_cash_less_capex':
        cash,payment=value('operating_cash'),value('capex_payment')
        if payment>=0:issues.append('SOURCE_CONTEXT_MISMATCH')
        else:
            calc('operating_cash_less_capex',cash+payment,'operating_cash + signed_capex_payment = operating_cash - abs(capex_payment)',[('operating_cash',year),('capex_payment',year)])
            r['explanation'].append(f"{year} 회계연도 영업현금흐름 {cash:,}에서 취득 지출액 {abs(payment):,}을 빼면 {cash+payment:,}백만 달러입니다. 원문 지급액은 {payment:,}이며 현금 유출입니다. 질문에서 정한 계산으로, 회사가 정의한 특정 지표와 같다고 단정하지 않습니다.")
    elif mode=='buyback_change':
        a,b=value('buyback_payment',2024),value('buyback_payment',2023)
        if a>=0 or b>=0:issues.append('SOURCE_CONTEXT_MISMATCH')
        else:
            calc('spending_increase',abs(a)-abs(b),'abs(FY2024 outflow) - abs(FY2023 outflow)',[('buyback_payment',2024),('buyback_payment',2023)])
            delta('buyback_payment','signed_cash_flow_change')
            r['explanation'].append(f"지출액 기준 {abs(b):,}에서 {abs(a):,}백만 달러로 {abs(a)-abs(b):,}백만 달러 변했습니다. 부호를 유지한 현금흐름 변화는 {a-b:,}백만 달러입니다. 매입 주식 수는 이 금액만으로 알 수 없습니다.")
    elif mode=='tax_bridge':
        for metric in ('operating_profit','tax_expense','net_income'):delta(metric,metric+'_change')
        calc('state_aid_tax',value('state_aid_tax',2024),'reported tax reconciliation amount',[('state_aid_tax',2024)])
        r['explanation'].append(f"2023년 대비 2024년 영업이익 변화 {r['values']['operating_profit_change']}, 법인세비용 변화 {r['values']['tax_expense_change']}, 순이익 변화 {r['values']['net_income_change']}백만 달러입니다. 국가보조금 결정의 세액조정 영향은 {r['values']['state_aid_tax']}백만 달러입니다. 법인세비용 증가는 순이익 감소의 일부 설명 요인이며, 다른 세전 항목도 있으므로 유일한 원인으로 단정하지 않습니다. 법인세비용은 현금 납부액과 다릅니다.")
    elif mode=='china_causality':
        issues.append('CAUSAL_DECOMPOSITION_REQUIRED');r['explanation'].append(MESSAGES['CAUSAL_DECOMPOSITION_REQUIRED']);r['required_information']=['판매량·판매가격·제품 구성·환율 효과별 기여도']
    r['status']='needs_review' if issues else 'verified'
    r['messages']=[MESSAGES[i] for i in issues]
    r['steps'].append({'stage':'calculate_or_withhold','status':r['status'],'operation':mode})
    return r
