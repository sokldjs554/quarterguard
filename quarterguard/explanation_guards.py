"""Narrow prose rejection rules learned from disclosed v5 failures.

These are conservative pattern checks, not semantic certification. Ambiguous
references are withheld rather than repaired. Historical model text is immutable.
"""
import re
from datetime import date
from decimal import Decimal
from .explanation_context import build_context, build_generation_context


def rates_match_tool(text, growth):
    """Signed rates or explicit Korean increase/decrease magnitudes only.

    A positive decrease magnitude can describe a negative tool rate. Bare
    positive numbers cannot. Negative magnitudes with 'decrease' abstain.
    This does not infer which company/period a rate describes.
    """
    rates=list(re.finditer(r'(?<![\d.,])([+-]?\d[\d,]*(?:\.\d+)?)\s*(?:[%％]|퍼센트|percent\b)',text,re.I))
    if growth is None:return not rates
    if not rates:return False
    expected=Decimal(growth)
    for match in rates:
        value=Decimal(match[1].replace(',',''))
        suffix=re.match(r'\s*(?:만큼\s*)?(감소|하락|증가|상승)',text[match.end():])
        prefix=re.search(r'(감소율|하락률)(?:은|는|이|가)?\s*(?:약\s*)?$',text[max(0,match.start()-20):match.start()])
        directions=[]
        for marker in (suffix,prefix):
            if marker:directions.append(-1 if marker[1].startswith(('감소','하락')) else 1)
        if len(set(directions))>1:return False
        if directions:
            tail=text[match.end()+suffix.end():] if suffix else text[match.end():]
            if re.match(r'\s*(?:하지\s*(?:않|못)|한\s*것(?:은|이)?\s*(?:아니|아닙)|'
                        r'(?:가|는)?\s*(?:아니|아닙)|했다고\s*할\s*수\s*없)',tail):return False
            if directions[0]<0 and match[1].startswith('+'):return False
            if value<0 or value*directions[0]!=expected:return False
        elif value!=expected:return False
    return True


def check_grounding(answer, result):
    """Check literal evidence bindings, not the meaning of unrestricted prose.

    The raw model response must include these claims itself. No substitution,
    normalization of financial values, or deterministic fallback is performed.
    Contradictory nonnumeric prose still requires human review.
    """
    text = str(answer.get('explanation_ko', ''))
    context = build_generation_context(result)
    compact = lambda value: re.sub(r'\s+', '', value)
    unsupported_large_unit = re.search(r'\d[\d,.]*\s*(?:조|억|만|천)', text)
    if context['status'] == 'no_evidence':
        return {'prose_evidence_anchors_present': True,
                'prose_decision_basis_present': compact(context['notice']) in compact(text),
                'prose_amounts_supported': not unsupported_large_unit and not re.search(r'\d[\d,.]*\s*(?:백만\s*원|백만\s*USD|천\s*원|원)', text),
                'prose_rates_match_tool': not re.search(r'\d[\d,.]*\s*(?:[%％]|퍼센트|percent\b)', text, re.I)}
    rows = context['evidence']
    known = context['status'] == 'available' and bool(rows)
    anchors = known and all(compact(row['required_claim']) in compact(text) or
                            explicit_evidence_binding(text, row, rows) for row in rows)
    basis = all(compact(row['statement']) in compact(text) for row in context['decision_basis'])
    allowed = {(Decimal(row['value']), compact(row['display_unit'])) for row in rows}
    derived = result.get('derived_value')
    if derived is not None and len({row['display_unit'] for row in rows}) == 1:
        allowed.add((Decimal(derived), compact(rows[0]['display_unit'])))
    amounts = re.findall(r'(?<![\d.,])([+-]?\d[\d,]*(?:\.\d+)?)\s*(백만\s*원|백만\s*USD|천\s*원|원)', text)
    supported = known and all((Decimal(number.replace(',', '')), compact(unit)) in allowed
                              for number, unit in amounts)
    exact_rates = rates_match_tool(text,result.get('growth_pct'))
    # A verified reconciliation must answer whether the derived and directly
    # reported amounts agree; a list of correct cells alone is incomplete.
    # Support only affirmative explicit conclusion forms, not general semantics.
    conclusion = True
    if derived is not None and result.get('status') == 'verified':
        value = re.escape(format(Decimal(derived), ',f'))
        conclusion = bool(re.search(
            r'(?:차감(?:한)?(?:결과|값)|뺀값)(?:이|은|는|가)(?:[1-4]분기)?'
            r'직접공시(?:된)?(?:매출|금액|값|수치)(?:과|와)일치'
            r'(?:합니다|했습니다|하여'+value+r'백만원임을확인하였습니다)(?:[.!。]|$)',
            compact(text)))
    return {'prose_evidence_anchors_present': bool(anchors),
            'prose_decision_basis_present': basis, 'prose_amounts_supported': bool(supported) and not unsupported_large_unit,
            'prose_rates_match_tool': bool(exact_rates),
            'prose_reconciliation_conclusion_present': conclusion}


def explicit_evidence_binding(text, row, rows):
    """Accept bounded surface variants, never a bag of numbers across the prose.

    Bind a scalar amount to its adjacent date/month/scope group, and the exact
    registered title/page in the same passage. A single-document result may
    inherit an explicit document reference elsewhere; multiple documents may not.
    No model judgment, amount conversion, or raw-response rewriting occurs.
    Unsupported ellipsis and unrestricted attribution remain reviewable.
    """
    number = re.escape(format(Decimal(row['value']), ',f'))
    unit = r'\s*'.join(map(re.escape, row['display_unit'].split()))
    amount = re.compile(r'(?<![\d.,])'+number+r'\s*'+unit+r'(?![A-Za-z])')
    all_amounts = re.compile(r'(?<![\d.,])[+-]?\d[\d,]*(?:\.\d+)?\s*(?:백만\s*원|백만\s*USD|천\s*원|원)')
    scope = {'CFS':'연결','OFS':'별도'}[row['scope']]
    def date_range(group):
        # ISO dates, or a full Korean start date and optionally inherited end year.
        group=re.sub(r'^기간\s*:\s*','',group.strip())
        iso = re.fullmatch(r'(20\d{2}-\d{2}-\d{2})\s*(?:~|부터)\s*(20\d{2}-\d{2}-\d{2})(?:까지)?', group)
        if iso:return iso[1],iso[2]
        ko = re.fullmatch(r'(20\d{2})년\s*(\d{1,2})월\s*(\d{1,2})일(?:부터)?\s*(?:~\s*)?(?:(20\d{2})년\s*)?(\d{1,2})월\s*(\d{1,2})일(?:까지)?', group)
        if ko:return f'{ko[1]}-{int(ko[2]):02}-{int(ko[3]):02}',f'{ko[4] or ko[1]}-{int(ko[5]):02}-{int(ko[6]):02}'
        return None
    title = re.escape(row['document_title'])
    page = re.escape(str(row['page']))
    source = re.compile(title+r'[\s,\"\']*PDF\s*(?:p\.\s*'+page+r'(?!\d)|'+page+r'\s*(?:페이지|쪽))')
    one_document = len({r['document_id'] for r in rows}) == 1
    for match in amount.finditer(text):
        following = text[match.end():]
        group = re.match(r'\s*\(([^)]*)\)', following)
        if group:
            context = group[1]
        else:
            # Prefix context must belong to this amount's sentence, without
            # a preceding financial amount that could supply someone else's dates.
            prefix = re.split(r'(?<![pP])[.!?。]\s+', text[:match.start()])[-1]
            if all_amounts.search(prefix):continue
            prefix_group = re.search(r'\(([^()]*)\)[^()]*$',prefix)
            if not prefix_group:continue
            context = prefix_group[1]
        # Parse exactly one affirmative range, month count and scope. Merely
        # containing the correct token inside a negation is never sufficient.
        fields=context.split(',',2)
        if len(fields)!=3 or date_range(fields[0]) != (row['start'],row['end']):continue
        if not re.fullmatch(str(row['months'])+r'\s*개월',fields[1].strip()):continue
        scope_fields=fields[2].split(',',1)
        if not re.fullmatch(scope+r'(?:\s*기준)?',scope_fields[0].strip()):continue
        if len(scope_fields)>1 and not source.fullmatch(scope_fields[1].strip()):continue
        next_amount = all_amounts.search(text, match.end())
        sentence_start=max((m.end() for m in re.finditer(r'(?<![pP])[.!?。]\s+',text[:match.start()])),default=0)
        previous=list(all_amounts.finditer(text,sentence_start,match.start()))
        if previous:
            # Exclude the prior amount's own parenthesized source context.
            end=text.find(')',previous[-1].end(),match.start())
            sentence_start=end+1 if end>=0 else match.start()
        passage = text[sentence_start:next_amount.start() if next_amount else len(text)]
        explicit_pages = re.findall(r'PDF\s*(?:p\.\s*(\d+)|(\d+)\s*(?:페이지|쪽))',passage)
        if any((a or b)!=str(row['page']) for a,b in explicit_pages):continue
        if source.search(passage) or (one_document and not explicit_pages and source.search(text)):
            return True
    return False


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


def diagnostic_origin_consistent(text, result):
    """Reject disclosed attribution patterns, not arbitrary causal semantics.

    Strip only complete registered legacy statements before checking additional
    assertions. A copied disclaimer cannot hide a contradictory extra sentence.
    """
    if 'PERIOD_MISMATCH' not in result.get('issues', []):
        return True
    for entry in build_context(result)['decision_basis']:
        text = text.replace(entry['statement'], '')
    if re.search(r'도구(?:의)?\s*(?:조건\s*)?실행\s*이력(?:에\s*따르면|을\s*(?:보면|통해)|상)', text):
        return False
    for sentence in re.split(r'[.!?。\n](?!\d)', text):
        starts = re.search(r'시작\s*월[·\s]*일|시작\s*월(?:과|및)\s*일|시작\s*일자', sentence)
        tool_cause = re.search(r'도구(?:의|에서)?', sentence) and re.search(
            r'decision_basis|때문|이유|제기|따라|보류', sentence)
        diagnostic_action = re.search(r'(?:독립(?:적인)?|별도)\s*재계산', sentence) and re.search(
            r'보류(?:하였|했|합니다|한다)|보류를\s*결정', sentence)
        if (starts and tool_cause) or diagnostic_action:
            return False
    return True


def company_comparison_bounded(text, result):
    """Narrow rejection of blanket bans; other free-text claims need review."""
    if 'COMPANY_MISMATCH' not in result.get('issues', []):
        return True
    pattern = r'(?:직접\s*비교|모든\s*비교)(?:가|는|도)?\s*(?:불가능|불가)'
    for match in re.finditer(pattern, text):
        if not re.match(r'(?:하다는\s*뜻은|한\s*것은)\s*아닙니다(?=$|[.!?。\s])', text[match.end():]):
            return False
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
    # Only this explicit draft-scoped rejection is exempt. Other occurrences
    # in the same answer are still checked, even after a safe draft disclaimer.
    absence_text = re.sub(r"['\"][^'\"\n]*['\"]라는\s*(?:비증거\s*)?임의\s*초안\s*내용은\s*근거가\s*없습니다[.]", '', text)
    absence = any(not (match.group().endswith('없') and re.match(
        r'(?:(?:는\s*것은|다는\s*뜻은)\s*아닙니다(?=$|[.!。\n])'
        r'|는\s*것이\s*아니라(?=[,\s]))', absence_text[match.end():]))
        for match in absence_pattern.finditer(absence_text))
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
    # The tool reports PERIOD_MISMATCH, not which short-circuited predicate ran.
    # A copied safe disclaimer cannot erase a separate assertion of execution history.
    context = build_generation_context(result)
    search_scope_bounded = context['status'] != 'no_evidence' or text == context['notice']
    annualized_term = r'연평균\s*(?:성장률|증가율|증감률)|(?<![A-Za-z])CAGR(?![A-Za-z])|\bannualized\b'
    annualized_claim = result.get('mode') in ('qoq','yoy') and any(
        not re.match(r'\s*(?:(?:이나|또는|및|/|·)\s*(?:'+annualized_term+r')\s*)?'
                     r'(?:이|가|은|는)?\s*(?:아닙니다(?=$|[.!?。\s])|아니라(?=$|[\s,]))',
                     text[match.end():],re.I)
        for match in re.finditer(annualized_term,text,re.I))
    return {
        'prose_diagnostic_origin_consistent': diagnostic_origin_consistent(text, result),
        'prose_search_scope_bounded': search_scope_bounded,
        'prose_company_comparison_bounded': company_comparison_bounded(text, result),
        'prose_growth_kind_consistent': not annualized_claim,
        'prose_million_amount_unambiguous': mixed_million is None,
        'prose_evidence_presence_consistent': not (evidence and absence),
        'prose_document_reference_unambiguous': not (len(documents) > 1 and same_document),
        'prose_rate_unit_explicit': rate_units,
        'prose_review_language_localized': internal is None,
        'prose_comparison_direction_consistent': comparison_direction_consistent(text,result),
    }
