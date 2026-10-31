"""Conservative offline claim checks; never a certificate of prose truth."""
from dataclasses import fields
from decimal import Decimal, ROUND_HALF_UP
import re
from urllib.parse import urlsplit,parse_qs
from .core import Fact,valid_source
from .live_verification import check_explanation

SCALES={'조':10**12,'억':10**8,'백만':10**6,'천':1000,'':1}

def audit_explanation(answer,result,context_years=()):
    text=str(answer.get('explanation_ko',''));issues=[];observations=[];covered=[]
    evidence=result.get('evidence',[])
    def add(code):
        if code not in issues:issues.append(code)
    valid=[]
    for row in evidence:
        try: valid.append(valid_source(Fact(**{f.name:row[f.name] for f in fields(Fact) if f.name in row})))
        except (ValueError,TypeError,KeyError):valid.append(False)
    structured=check_explanation(answer,result)
    if not all(structured.values()):add('STRUCTURED_MISMATCH')
    if not all(valid):add('CANONICAL_CITATION_MISMATCH')
    years={str(f['start'])[:4] for f in evidence}|set(map(str,context_years))
    months={int(f.get('months') or ((int(f['end'][5:7])-int(f['start'][5:7]))+1)) for f in evidence}
    quarters={(int(f['end'][5:7])+2)//3 for f in evidence}
    currencies={f['currency'] for f in evidence};scales={f['scale'] for f in evidence};scopes={f['scope'] for f in evidence}
    amounts={Decimal(f['value'])*f['scale'] for f in evidence}
    if result.get('derived_value') is not None and evidence:amounts.add(Decimal(result['derived_value'])*evidence[-1]['scale'])
    negated=bool(re.search(r'\bnot\b|아닌|않|아니라|아니다',text,re.I))
    if negated:add('NEGATION_REQUIRES_REVIEW')
    if '개별' in text:add('AMBIGUOUS_SCOPE_TERM')
    for word,scope in [('연결','CFS'),('consolidated','CFS'),('별도','OFS'),('separate','OFS'),('standalone','OFS')]:
        mentioned=bool(re.search(r'\b'+word+r'\b',text,re.I)) if word.isascii() else word in text
        if mentioned:
            if scopes and scope not in scopes and not negated:add('SCOPE_CLAIM_CONFLICT')
    for pattern,currency in [(r'\bUSD\b|달러','USD'),(r'\bKRW\b|원화','KRW')]:
        if re.search(pattern,text,re.I) and currencies and currency not in currencies and not negated:add('CURRENCY_CLAIM_CONFLICT')
    for m in re.finditer(r'(?<![\d,])(20\d{2})\s*년?',text):
        covered.append(m.span());observations.append({'type':'year','claim':m.group(1)})
        if m.group(1) not in years:add('YEAR_CLAIM_CONFLICT')
    for pattern,allowed,code in [(r'([1-4])\s*분기',quarters,'QUARTER_CLAIM_CONFLICT'),(r'\bQ([1-4])\b',quarters,'QUARTER_CLAIM_CONFLICT'),(r'(\d+)\s*개월',months,'MONTHS_CLAIM_CONFLICT')]:
        for m in re.finditer(pattern,text,re.I):
            covered.append(m.span())
            if int(m.group(1)) not in allowed:add(code)
    for m in re.finditer(r'(\d{1,2})\s*월',text):
        covered.append(m.span())
        if evidence and not any(int(f['start'][5:7])<=int(m.group(1))<=int(f['end'][5:7]) for f in evidence):add('MONTH_RANGE_REQUIRES_REVIEW')
    for m in re.finditer(r'([+-]?\d+(?:\.\d+)?)\s*%',text):
        covered.append(m.span());claim=Decimal(m.group(1));expected=result.get('growth_pct')
        if expected is None:add('UNSUPPORTED_PERCENT_CLAIM')
        else:
            rounded=Decimal(expected).quantize(Decimal(1).scaleb(claim.as_tuple().exponent),rounding=ROUND_HALF_UP)
            if claim!=rounded:add('PERCENT_MISMATCH')
        observations.append({'type':'percent','claim':str(claim),'tool_value':expected})
    # Simple scalar amounts only. Compound Korean amounts deliberately remain reviewable.
    for m in re.finditer(r'(?<![\d,.])([+-]?\d[\d,]*(?:\.\d+)?)\s*(조|억|백만|천)?\s*(원|KRW|USD|달러)(?![A-Za-z])',text,re.I):
        covered.append(m.span());value=Decimal(m.group(1).replace(',',''))*SCALES[m.group(2) or ''];currency='USD' if m.group(3).upper() in ('USD','달러') else 'KRW'
        if not evidence:add('UNSUPPORTED_NUMERIC_CLAIM')
        elif currency not in currencies:add('CURRENCY_CLAIM_CONFLICT')
        elif value not in amounts:add('AMOUNT_MISMATCH')
        else:
            # Bind a simple amount to explicit context in its sentence, not any
            # number somewhere in the tool result. Complex prose stays reviewable.
            left=max(text.rfind('. ',0,m.start()),text.rfind('! ',0,m.start()),text.rfind('? ',0,m.start()))
            sentence=text[left+2 if left>=0 else 0:]
            sentence=re.split(r'[.!?]\s+',sentence,maxsplit=1)[0]
            ys=set(re.findall(r'(?<![\d,])(20\d{2})(?![\d,])',sentence));qs={int(a or b) for a,b in re.findall(r'([1-4])\s*분기|\bQ([1-4])\b',sentence,re.I)}
            ss={v for word,v in [('연결','CFS'),('별도','OFS'),('consolidated','CFS'),('separate','OFS'),('standalone','OFS')] if (bool(re.search(r'\b'+word+r'\b',sentence,re.I)) if word.isascii() else word in sentence)}
            mm={int(n) for n in re.findall(r'(\d+)\s*개월',sentence)}
            eligible=[f for f in evidence if f['currency']==currency
                and (len(ys)!=1 or f['start'][:4] in ys)
                and (len(qs)!=1 or (int(f['end'][5:7])+2)//3 in qs)
                and (len(ss)!=1 or f['scope'] in ss)
                and (len(mm)!=1 or f.get('months') in mm)]
            if not any(Decimal(f['value'])*f['scale']==value for f in eligible):add('AMOUNT_CONTEXT_MISMATCH')
            if len(ys)>1 or len(qs)>1 or len(ss)>1 or len(mm)>1:add('AMOUNT_ATTRIBUTION_REQUIRES_REVIEW')
        observations.append({'type':'simple_amount','claim_normalized':str(value),'currency':currency})
    for m in re.finditer(r'(?:단위(?:는|가)?|in)\s*(조|억|백만|천)?\s*(원|KRW|USD|달러)',text,re.I):
        if evidence and SCALES[m.group(1) or ''] not in scales:add('UNIT_CLAIM_CONFLICT')
    if '누적' in text and months and all(n==3 for n in months):add('PERIOD_CLAIM_REQUIRES_REVIEW')
    if result.get('status')=='needs_review' and re.search(r'검증\s*통과|문제가?\s*없|계산\s*가능|확정된?\s*수치',text):add('REJECTION_OVERRIDDEN_IN_PROSE')
    for m in re.finditer(r'https?://[^\s<>]+',text):
        covered.append(m.span());url=m.group().rstrip('.,)');u=urlsplit(url);page=parse_qs(u.fragment).get('page',[None])[0]
        if not any(url.split('#')[0]==f['source_url'] and (page is None or page==str(f['page'])) for f in evidence):add('INLINE_CITATION_MISMATCH')
    for m in re.finditer(r'\d[\d,]*(?:\.\d+)?',text):
        if not any(a<=m.start() and m.end()<=b for a,b in covered):add('UNBOUND_NUMBER_REQUIRES_REVIEW')
    return {'automatic_verdict':'flagged' if issues else 'no_detected_rule_violation','issues':issues,'structured_checks':structured,
        'canonical_evidence_valid':all(valid),'citation_checks':[{'fact_id':f['id'],'document_id':f['document_id'],'page':f['page'],'row':f['row'],'column':f['column'],'canonical_match':ok} for f,ok in zip(evidence,valid)],
        'observed_claims':observations,'semantic_verified':False,'human_review_required':True,
        'limitations':['Rule checks cover explicit patterns, not all sentence meaning.','Negation, attribution, omitted context and compound quantities require human adjudication.','No expert review or LLM-as-judge was performed.']}
