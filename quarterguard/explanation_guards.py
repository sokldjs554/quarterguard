"""Narrow prose rejection rules learned from disclosed v5 failures.

These are conservative pattern checks, not semantic certification. Ambiguous
references are withheld rather than repaired. Historical model text is immutable.
"""
import re
from datetime import date


_LABEL = (r'(?:20\d{2}(?:\s*년)?(?:\s*(?:[1-4]\s*분기|Q\s*[1-4]))?'
          r'|Q\s*[1-4](?:\s*20\d{2})?|[1-4]\s*분기)')
_PAIRS = (
    (re.compile(r'(?<![\w])(?P<left>'+_LABEL+r')\s*(?:대비|에\s*비해|보다)\s*(?P<right>'+_LABEL+r')(?!\d)',re.I),(1,0)),
    (re.compile(r'\bfrom\s+(?P<left>'+_LABEL+r')\s+to\s+(?P<right>'+_LABEL+r')(?!\d)',re.I),(1,0)),
    (re.compile(r'(?<![\w])(?P<left>'+_LABEL+r')\s+compared\s+(?:with|to)\s+(?P<right>'+_LABEL+r')(?!\d)',re.I),(0,1)),
)
_INTERNAL_LABELS = {
    'SEARCH_EMPTY','COMPANY_MISMATCH','METRIC_MISMATCH','SCOPE_MISMATCH',
    'CURRENCY_MISMATCH','PERIOD_MISMATCH','SOURCE_MISMATCH','UNKNOWN_UNIT',
    'MISSING_SOURCE','CONVENIENCE_TRANSLATION','ZERO_BASE','NEGATIVE_BASE','NUMERIC_CONFLICT',
    'needs_review','equal_months','qoq_three_months','qoq_adjacent',
    'yoy_year','yoy_end_month','yoy_start_month_day',
}


def _period_role(label, evidence):
    """Resolve a stated year/quarter uniquely to current(0) or base(1)."""
    year=re.search(r'20\d{2}',label)
    quarter=re.search(r'([1-4])\s*분기|Q\s*([1-4])',label,re.I)
    q=int(next(g for g in quarter.groups() if g)) if quarter else None
    matches=[]
    try:
        for index,fact in enumerate(evidence):
            end=date.fromisoformat(fact['end'])
            if year and end.year!=int(year.group()):continue
            if q and (end.month not in (3,6,9,12) or end.month//3!=q):continue
            matches.append(index)
    except (ValueError,TypeError,KeyError):return None
    return matches[0] if len(matches)==1 else None


def comparison_direction_consistent(text,result):
    """Check explicit supported period pairs, not all free-text semantics.

    compare() evidence order is current,base. Korean X 대비 Y and from X to Y
    mean base,current; X compared with Y means current,base. Unsupported explicit
    dated pairs are withheld. A sentence with no explicit pair isn't certified.
    """
    if result.get('growth_pct') is None or result.get('mode') not in ('qoq','yoy'):
        return True
    evidence=result.get('evidence') or []
    for sentence in re.split(r'[.!?。\n](?!\d)',text):
        spans=[]
        for pattern,wanted in _PAIRS:
            for match in pattern.finditer(sentence):
                if len(evidence)!=2:return False
                # Never back off to a bare year while dropping an unsupported
                # period qualifier (e.g. "2025년 상반기" or "2025 Q9").
                if re.match(r'\s*(?:상반기|하반기|반기|누적|단독|당분기|\d+\s*(?:개월|월|분기)'
                            r'|Q\s*\d|H[12]\b|(?:first|second|third|fourth|half|quarter)\b)',
                            sentence[match.end():],re.I):return False
                roles=tuple(_period_role(match[k],evidence) for k in ('left','right'))
                if roles!=wanted:return False
                spans.append(match.span())
        # A dated comparison outside the supported grammar must not silently pass.
        for marker in re.finditer(r'대비|에\s*비해|보다|\bcompared\s+(?:with|to)\b|\bto\b',sentence,re.I):
            if any(start<=marker.start()<end for start,end in spans):continue
            left,right=sentence[:marker.start()],sentence[marker.end():]
            dated=r'(?<!\d)20\d{2}(?!\d)|[1-4]\s*분기|\bQ\s*[1-4]\b'
            if re.search(dated,left,re.I) and re.search(dated,right,re.I):return False
    return True


def check_prose(answer, result):
    text = str(answer.get('explanation_ko', ''))
    evidence = result.get('evidence') or []
    documents = {f.get('document_id') for f in evidence if f.get('document_id')}
    # Permit explicit negation of absence, including the disclosed connective.
    # Check every occurrence, so a safe prefix cannot hide a later contradiction.
    absence_pattern = re.compile(
        r'(?:검색|수집)\s*범위[^.!?\n]{0,60}(?:확인|찾)[^.!?\n]{0,20}수\s*없'
        r'|(?:근거|검색\s*결과)(?:가|를|는)?\s*(?:없|찾지\s*못)')
    absence = any(not (match.group().endswith('없') and re.match(
        r'(?:(?:는\s*것은|다는\s*뜻은)\s*아닙니다(?=$|[.!。\n])'
        r'|는\s*것이\s*아니라(?=[,\s]))', text[match.end():]))
        for match in absence_pattern.finditer(text))
    same_document = re.search(
        r'(?:같은|동일한?)\s*(?:보고서|문서)|\bsame\s+(?:report|document)\b', text, re.I)
    labels=_INTERNAL_LABELS|{s for s in result.get('issues',[]) if isinstance(s,str) and s}
    internal = re.search(r'\bcontext\s+needs\s+review\b|(?<![A-Za-z0-9_])(?:'+
                         '|'.join(re.escape(s) for s in sorted(labels))+r')(?![A-Za-z0-9_])',text,re.I)
    # Rate-labelled numbers, plus every occurrence of the exact tool growth value.
    # Rounded rates are checked when labelled. No numeric claim => no unit check.
    number = r'[+-]?\d+(?:\.\d+)?'
    rates = list(re.finditer(
        r'(?:증가율|증감률|감소율|성장률|growth\s*rate|change\s*rate)'
        r'[^\d.!?\n]{0,32}(?P<rate>'+number+r')', text, re.I))
    growth = result.get('growth_pct')
    if growth is not None:
        rates += list(re.finditer(r'(?<![\d.,])'+re.escape(str(growth))+r'(?!\d|[.,]\d)', text))
    rate_units = all(re.match(r'\s*(?:[%％]|퍼센트|percent\b)', text[m.end():], re.I)
                     for m in rates)
    # Disclosed production-model failures combined Korean large-number units
    # with an additional million-won multiplier. Withhold this unsupported
    # notation; never repair or silently reinterpret a financial amount.
    mixed_million = re.search(
        r'(?:[0-9][0-9,.]*\s*(?:조|억|만|천)\s*)+'
        r'(?:[0-9][0-9,.]*\s*)?백만\s*원', text)
    return {
        'prose_million_amount_unambiguous': mixed_million is None,
        'prose_evidence_presence_consistent': not (evidence and absence),
        'prose_document_reference_unambiguous': not (len(documents) > 1 and same_document),
        'prose_rate_unit_explicit': rate_units,
        'prose_review_language_localized': internal is None,
        'prose_comparison_direction_consistent': comparison_direction_consistent(text,result),
    }
