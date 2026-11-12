"""Deterministic, explicitly selected source-cell calculations; no LLM planning.

Public entry points resolve IDs from the immutable, hash-checked extraction.
Internal arithmetic tests may use synthetic cells, clearly separate from PDF runs.
"""
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from . import source_evidence as source

MODES=('annual_yoy','balance_yoy','product_share','inventory_months')
SCALES=(1,1000,1000000,100000000,1000000000,1000000000000)
INCOME={'revenue','cost_of_sales','operating_profit'}
BALANCES={'cash','inventory'}
PRODUCTS={'dram','nand','other_products'}
MESSAGES={
    'COMPANY_MISMATCH':'기업이 같아야 합니다.',
    'SCOPE_MISMATCH':'연결 범위를 같게 선택해 주세요.',
    'CURRENCY_MISMATCH':'이 계산은 같은 KRW 통화의 원문 수치만 지원합니다.',
    'SOURCE_MISMATCH':'등록된 문서·해시·연도 열을 확인할 수 없습니다.',
    'UNKNOWN_UNIT':'원문 단위 배율을 확인할 수 없습니다.',
    'INVALID_VALUE':'유한한 금액을 확인할 수 없습니다.',
    'METRIC_MISMATCH':'비교하려는 항목이 같아야 합니다.',
    'MEASUREMENT_MISMATCH':'연간 실적과 기준일 잔액을 구분하고 해당 계산 방식을 선택해 주세요.',
    'PERIOD_MISMATCH':'연간 비교는 같은 달력 기준의 전년 전체 기간, 잔액 비교는 전년 말 기준일이어야 합니다.',
    'PRODUCT_CONTEXT_MISMATCH':'제품 비중은 같은 문서·제품 표·기간·연도 열의 제품 금액과 합계를 선택해야 합니다.',
    'NEGATIVE_PART':'제품 매출이 음수여서 비중 계산을 보류했습니다.',
    'PART_EXCEEDS_TOTAL':'제품 매출이 합계를 초과해 비중 계산을 보류했습니다.',
    'ZERO_BASE':'비교 기준값이 0이어서 증감률을 계산하지 않았습니다. 조건이 맞는 금액 차이는 별도 표시합니다.',
    'NEGATIVE_BASE':'비교 기준값이 음수여서 일반 증감률을 계산하지 않았습니다. 조건이 맞는 금액 차이는 별도 표시합니다.',
    'NONPOSITIVE_TOTAL':'제품 매출 합계는 양수여야 비중을 계산할 수 있습니다.',
    'RATIO_DEFINITION_REQUIRED':'재고 개월분은 기말·평균 재고, 분모의 매출·매출원가와 대상 기간을 먼저 정해야 합니다. 자동 계산하지 않습니다.',
}


def _number(cell):
    try:
        value=Decimal(cell['value'])
        if not value.is_finite() or len(cell['value'])>60:return None
        if type(cell['scale']) is not int or cell['scale'] not in SCALES:return None
        return value*cell['scale']
    except (InvalidOperation,ValueError,KeyError,TypeError):return None


def _annual(cell):
    try:
        year=cell['year'];start=date.fromisoformat(cell['start']);end=date.fromisoformat(cell['end'])
        return (cell['period_kind']=='duration' and type(year) is int and
                start==date(year,1,1) and end==date(year,12,31) and cell['as_of'] is None)
    except (KeyError,TypeError,ValueError):return False


def _year_end(cell):
    try:
        return (cell['period_kind']=='instant' and type(cell['year']) is int and
                date.fromisoformat(cell['as_of'])==date(cell['year'],12,31) and
                cell['start'] is None and cell['end'] is None)
    except (KeyError,TypeError,ValueError):return False


def _calculate_pair(current,base,mode):
    """Pure guards/arithmetic. Caller must resolve canonical IDs for production."""
    if mode not in MODES:raise ValueError('INVALID_CALCULATION_MODE')
    checks=[];issues=[]
    def check(code,passed):
        checks.append({'condition':code,'passed':bool(passed)})
        if not passed and code not in issues:issues.append(code)
    a,b=current,base
    n,d=_number(a),_number(b)
    check('COMPANY_MISMATCH',a.get('company')==b.get('company')=='skhynix')
    check('SCOPE_MISMATCH',a.get('scope')==b.get('scope')=='CFS')
    check('CURRENCY_MISMATCH',a.get('currency')==b.get('currency')=='KRW')
    check('SOURCE_MISMATCH',all(c.get('document_id')==source.DOCUMENT_ID and c.get('document_sha256')==source.PDF_SHA and
        c.get('source_url')==source.URL and c.get('column')==str(c.get('year')) for c in (a,b)))
    check('UNKNOWN_UNIT',all(type(c.get('scale')) is int and c.get('scale') in SCALES for c in (a,b)))
    check('INVALID_VALUE',n is not None and d is not None)
    result={'mode':mode,'status':'needs_review','issues':issues,'checks':checks,'messages':[],
        'difference':None,'difference_status':'not_calculated','growth_pct':None,'share_pct':None,
        'percentage_status':'not_calculated','transition':None,
        'normalized_inputs':[str(n) if n is not None else None,str(d) if d is not None else None],
        'normalized_currency':'KRW','normalized_scale':1,'display_scale':1000000,
        'evidence':[a,b],'formula':None,'difference_formula':None,'execution':'deterministic_decimal',
        'rounding':{'decimal_places':4,'mode':'ROUND_HALF_EVEN'}}
    if mode=='inventory_months':
        check('RATIO_DEFINITION_REQUIRED',False)
    elif mode in ('annual_yoy','balance_yoy'):
        metrics=INCOME if mode=='annual_yoy' else BALANCES
        check('METRIC_MISMATCH',a.get('metric')==b.get('metric'))
        check('MEASUREMENT_MISMATCH',all(c.get('metric') in metrics for c in (a,b)) and
              all(c.get('period_kind')==('duration' if mode=='annual_yoy' else 'instant') for c in (a,b)))
        valid_period=(_annual(a) and _annual(b)) if mode=='annual_yoy' else (_year_end(a) and _year_end(b))
        check('PERIOD_MISMATCH',valid_period and a['year']==b['year']+1)
        if not issues:
            difference=(n-d)/Decimal(1000000)
            result['difference']={'value':format(difference,'f'),'currency':'KRW','scale':1000000,'unit_label':'백만 원'}
            result['difference_status']='calculated'
            result['difference_formula']='(current_normalized_KRW - base_normalized_KRW) / 1000000'
            if a['metric']=='operating_profit' and d<0 and n>0:result['transition']='loss_to_profit'
            check('ZERO_BASE',d!=0);check('NEGATIVE_BASE',d>=0)
            result['formula']='(current_normalized_KRW / base_normalized_KRW - 1) * 100'
            if not issues:
                result['growth_pct']=str(((n/d-1)*100).quantize(Decimal('.0001'),rounding=ROUND_HALF_EVEN))
                result['percentage_status']='calculated'
    elif mode=='product_share':
        check('MEASUREMENT_MISMATCH',_annual(a) and _annual(b))
        check('PRODUCT_CONTEXT_MISMATCH',a.get('metric') in PRODUCTS and b.get('metric')=='product_total' and
              a.get('row_role')=='labelled' and b.get('row_role')=='total' and
              a.get('table_id')==b.get('table_id')=='note-24-2' and
              a.get('page')==b.get('page') and a.get('start')==b.get('start') and
              a.get('end')==b.get('end') and a.get('year')==b.get('year'))
        if not issues:
            check('NEGATIVE_PART',n>=0);check('NONPOSITIVE_TOTAL',d>0);check('PART_EXCEEDS_TOTAL',n<=d)
            result['formula']='product_normalized_KRW / total_normalized_KRW * 100'
            if not issues:
                result['share_pct']=str((n/d*100).quantize(Decimal('.0001'),rounding=ROUND_HALF_EVEN))
                result['percentage_status']='calculated'
    result['status']='needs_review' if issues else 'verified'
    result['messages']=[MESSAGES[code] for code in issues]
    return result


def calculate_source_pair(current_id,base_id,mode):
    if mode not in MODES:raise ValueError('INVALID_CALCULATION_MODE')
    manifest,cells=source.load_source()
    by_id={c['id']:c for c in cells}
    if current_id not in by_id or base_id not in by_id:raise ValueError('UNKNOWN_SOURCE_CELL')
    return _calculate_pair(by_id[current_id],by_id[base_id],mode)|{
        'source_integrity':'registered_snapshot','source_snapshot_sha256':manifest['cells_sha256']}


def options():
    manifest,cells=source.load_source()
    runtime=manifest|{'calculation_supported':True,'calculation_modes':['annual_yoy','balance_yoy','product_share'],'clarification_only_modes':['inventory_months'],
        'limitations':['Selected rows only; no general annual parser.',
                       'Registered cells support annual comparison, year-end balance change and product share.',
                       'Inventory months requires an explicit definition and is not calculated.',
                       'Zero or negative bases withhold percentage growth; compatible differences remain available.']}
    return {'document':runtime,'cells':cells,'modes':list(MODES),
        'calculation_modes':['annual_yoy','balance_yoy','product_share'],
        'clarification_only_modes':['inventory_months']}
