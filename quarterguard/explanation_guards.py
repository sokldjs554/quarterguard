"""Narrow prose rejection rules learned from disclosed v5 failures.

These are conservative pattern checks, not semantic certification. Ambiguous
references are withheld rather than repaired. Historical model text is immutable.
"""
import re


def check_prose(answer, result):
    text = str(answer.get('explanation_ko', ''))
    evidence = result.get('evidence') or []
    documents = {f.get('document_id') for f in evidence if f.get('document_id')}
    # Even a qualified/negated reuse can be ambiguous: request explicit wording.
    absence = re.search(
        r'(?:검색|수집)\s*범위[^.!?\n]{0,60}(?:확인|찾)[^.!?\n]{0,20}수\s*없'
        r'|(?:근거|검색\s*결과)(?:가|를|는)?\s*(?:없|찾지\s*못)', text)
    same_document = re.search(
        r'(?:같은|동일한?)\s*(?:보고서|문서)|\bsame\s+(?:report|document)\b', text, re.I)
    internal = re.search(r'\bcontext\s+needs\s+review\b|\bneeds_review\b', text, re.I)
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
    return {
        'prose_evidence_presence_consistent': not (evidence and absence),
        'prose_document_reference_unambiguous': not (len(documents) > 1 and same_document),
        'prose_rate_unit_explicit': rate_units,
        'prose_review_language_localized': internal is None,
    }
