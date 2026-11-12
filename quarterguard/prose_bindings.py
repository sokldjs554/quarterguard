"""Bounded financial prose bindings; not a general natural-language judge.

Recognize literal dates or calendar-quarter labels, local amounts/units and
registered citations. Inheritance is restricted to an explicit same-period
reference or shared scope in one sentence. Never rewrite a model response.
"""
import calendar
import re
from datetime import date
from decimal import Decimal
from . import core

AMOUNT = re.compile(r'(?<![\d.,])(?P<value>[+-]?\d[\d,]*(?:\.\d+)?)\s*(?P<unit>백만\s*원|백만\s*USD|천\s*원|원)')
SENTENCE = re.compile(r'(?<![pP])[.!?。]\s+')
ISO = re.compile(r'(20\d{2}-\d{2}-\d{2})\s*~\s*(20\d{2}-\d{2}-\d{2})')
KOREAN_RANGE = re.compile(r'(?:(20\d{2})년\s*)?(\d{1,2})월\s*(\d{1,2})일(?:부터)?\s*(?:~\s*)?(?:(20\d{2})년\s*)?(\d{1,2})월\s*(\d{1,2})일(?:까지)?')
QUARTER = re.compile(r'(20\d{2})년\s*([1-4])분기')


def _periods(piece, previous):
    periods=[]
    for m in ISO.finditer(piece):periods.append((m[1],m[2]))
    quarters=list(QUARTER.finditer(piece))
    for m in quarters:
        y,q=int(m[1]),int(m[2]);month=q*3
        periods.append((f'{y}-{month-2:02}-01',f'{y}-{month:02}-{calendar.monthrange(y,month)[1]}'))
    for m in KOREAN_RANGE.finditer(piece):
        year=m[1] or (quarters[0][1] if len(quarters)==1 else None)
        if year is None:return None
        try:
            start=date(int(year),int(m[2]),int(m[3]));end=date(int(m[4] or year),int(m[5]),int(m[6]))
        except ValueError:return None
        periods.append((start.isoformat(),end.isoformat()))
    same=re.search(r'(20\d{2})년\s*동기간',piece)
    if same:
        if previous is None:return None
        periods.append((same[1]+previous['start'][4:],same[1]+previous['end'][4:]))
    return periods


# Longest metric names first so 매출 is not read inside 매출원가/매출총이익.
_METRICS={'매출총이익':'gross_profit','매출원가':'cost_of_sales','판매관리비':'operating_expenses',
          '당기순손실':'net_profit','당기순이익':'net_profit','순이익':'net_profit',
          '영업이익':'operating_profit','영업손실':'operating_profit','매출액':'revenue','매출':'revenue'}
_COMPANIES={'삼성전자':'samsung','삼성':'samsung','현대자동차':'hyundai','현대차':'hyundai',
            'SK하이닉스':'skhynix','애플':'apple'}

def _identity_consistent(piece,row):
    registered=core.source_facts().get(row['id'])
    if registered is None:return False
    if re.search(r'영업손실|당기순손실',piece) and Decimal(row['value'])>=0:return False
    for key,aliases in [('company',_COMPANIES),('metric',_METRICS)]:
        pattern='|'.join(map(re.escape,sorted(aliases,key=len,reverse=True)))
        if any(aliases[m[0]]!=registered[key] for m in re.finditer(pattern,piece)):return False
    currencies={'KRW':'KRW','USD':'USD','원화':'KRW','달러':'USD'}
    if any(currencies[m[0]]!=registered['currency'] for m in re.finditer(r'KRW|USD|원화|달러',piece)):return False
    return True


def evidence_bindings(text, rows):
    """Require every money mention to bind to one unique registered fact.

    This extra grammar handles ordered citation pairs and inflected Korean
    surface forms. It does not relax the original exact-claim path. Returns
    False for unknown, negated, conflicting or incomplete bindings.
    """
    mentions=list(AMOUNT.finditer(text))
    if len(mentions)!=len(rows) or not mentions:return False
    titles='|'.join(re.escape(x) for x in sorted({r['document_title'] for r in rows},key=len,reverse=True))
    citation=re.compile(r'(?P<title>'+titles+r')[\s,\"\']*PDF\s*(?:p\.\s*(?P<p1>\d+)|(?P<p2>\d+)\s*(?:페이지|쪽))')
    refs=list(citation.finditer(text))
    if not refs:return False
    # A standalone page mention outside a registered title/page citation cannot
    # be silently ignored, even if a correct citation is also present.
    pages=re.finditer(r'PDF\s*(?:p\.\s*\d+|\d+\s*(?:페이지|쪽))',text)
    if any(not any(r.start()<=p.start()<p.end()<=r.end() for r in refs) for p in pages):return False
    one_document=len({r['document_id'] for r in rows})==1
    ordered=(len(rows)==len(refs)==2 and refs[0].start()>mentions[-1].end() and
             re.fullmatch(r'\s*(?:와|과|및|,)\s*',text[refs[0].end():refs[1].start()]) is not None)
    seen=[]
    previous=None
    previous_sentence=None
    for i,mention in enumerate(mentions):
        candidates=[r for r in rows if Decimal(r['value'])==Decimal(mention['value'].replace(',','')) and
                    re.sub(r'\s+','',r['display_unit'])==re.sub(r'\s+','',mention['unit'])]
        if len(candidates)!=1:return False
        row=candidates[0]
        start=max((m.end() for m in SENTENCE.finditer(text,0,mention.start())),default=0)
        end_match=SENTENCE.search(text,mention.end())
        end=end_match.start() if end_match else len(text)
        left_start=max(start,mentions[i-1].end() if i else 0)
        left=text[left_start:mention.start()]
        if i and left_start==mentions[i-1].end():
            # The previous amount's trailing parentheses belong to that amount.
            group=re.match(r'\s*(?:입니다|이며|으로|이다)?\s*\([^)]*\)',left)
            if group:left=left[group.end():]
        right=text[mention.end():min(end,mentions[i+1].start() if i+1<len(mentions) else len(text))]
        group=re.match(r'\s*(?:입니다|이며|으로|이다)?\s*\(([^)]*)\)',right)
        if group:
            if re.match(r'\s*(?:이|가|은|는)?\s*(?:아니|아닙|아닌|않)',right[group.end():]):return False
            tail=re.split(r',\s*(?=20\d{2}년)',right[group.end():],maxsplit=1)[0]
            right=group[1]+' '+tail
        elif left.rstrip().endswith('(') and right.startswith(')'):right=''
        else:right=re.split(r',\s*(?=20\d{2}년)',right,maxsplit=1)[0]
        piece=citation.sub('',left+' '+right)
        if re.search(r'아니|아닌|아닙|않|못|대신',piece):return False
        inherited=previous if previous_sentence==start else None
        periods=_periods(piece,inherited)
        if not periods or any(p!=(row['start'],row['end']) for p in periods):return False
        months=re.findall(r'(\d+)\s*개월',piece)
        if any(int(n)!=row['months'] for n in months):return False
        # A bare quarter denotes a standalone calendar quarter in this output
        # grammar; cumulative prose must carry an explicit matching date range.
        if QUARTER.search(piece) and re.search(r'누적|누계',piece):return False
        if any(not any(q.start()<=m.start()<m.end()<=q.end() for q in QUARTER.finditer(piece))
               for m in re.finditer(r'[1-4]분기',piece)):return False
        if '단독' in piece and row['months']!=3:return False
        if re.search(r'누적|누계',piece) and not row['start'].endswith('-01-01'):return False
        if '연간' in piece and (row['months']!=12 or not row['start'].endswith('-01-01')):return False
        if not _identity_consistent(piece,row):return False
        scopes=set(re.findall(r'연결|별도',piece))
        expected={'CFS':'연결','OFS':'별도'}[row['scope']]
        if not scopes and inherited is not None:scopes={{'CFS':'연결','OFS':'별도'}[inherited['scope']]}
        if scopes!={expected}:return False
        def ref_matches(ref):return ref['title']==row['document_title'] and (ref['p1'] or ref['p2'])==str(row['page'])
        if ordered:
            if not ref_matches(refs[i]):return False
        elif one_document:
            if not all(ref_matches(ref) for ref in refs):return False
        else:
            next_amount=mentions[i+1].start() if i+1<len(mentions) else len(text)
            following=[ref for ref in refs if mention.end()<=ref.start()<next_amount]
            preceding=[ref for ref in refs if start<=ref.start()<mention.start()]
            local=following+preceding
            if not local or not all(ref_matches(ref) for ref in local):return False
        seen.append(row['id']);previous=row;previous_sentence=start
    return len(set(seen))==len(rows)


def checked_formula_spans(text, result):
    """Recognize one supported growth formula, validating operands without eval."""
    evidence=result.get('evidence') or []
    if len(evidence)!=2 or result.get('growth_pct') is None:return []
    number=r'([+-]?\d[\d,]*(?:\.\d+)?)'
    pattern=re.compile(r'\(\(\s*'+number+r'\s*-\s*'+number+r'\s*\)\s*/\s*'+number+r'\s*\)\s*[×*]\s*100\s*=\s*'+number+r'\s*[%％]')
    expected=[Decimal(evidence[0]['value']),Decimal(evidence[1]['value']),Decimal(evidence[1]['value']),Decimal(result['growth_pct'])]
    return [m.span() for m in pattern.finditer(text) if [Decimal(x.replace(',','')) for x in m.groups()]==expected]


def reported_decision_present(text, code):
    """Recognize reported hold statements; execution-cause guards run separately."""
    if code=='PERIOD_MISMATCH':
        return bool(re.search(r'도구가 기간 불일치를 보고하여 선택한 방식의 성장률 계산을 보류했습니다[.]',text) or
                    re.search(r'기간 불일치 문제도 보고되어 선택한 방식의 성장률 계산을 보류해야 합니다(?:\(PERIOD_MISMATCH\))?[.]',text))
    if code=='COMPANY_MISMATCH':
        return bool(re.search(r'회사명이 달라 동일 회사 간 성장률 계산이 불가능하며(?:\(COMPANY_MISMATCH\))?[,]',text))
    return False


def remove_explained_issue_codes(text, issues):
    """Codes in parentheses are readable only beside a matching Korean report.

    Raw response/structured fields remain untouched. This view is used solely
    by the readability check, not by numeric, citation or factual checks.
    """
    patterns={
        'COMPANY_MISMATCH':r'(회사명이 달라 동일 회사 간 성장률 계산이 불가능하며)\(COMPANY_MISMATCH\)',
        'PERIOD_MISMATCH':r'(기간 불일치 문제도 보고되어 선택한 방식의 성장률 계산을 보류해야 합니다)\(PERIOD_MISMATCH\)',
    }
    for code,pattern in patterns.items():
        if code in issues:text=re.sub(pattern,r'\1',text)
    return text
