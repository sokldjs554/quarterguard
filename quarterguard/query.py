"""Bounded bilingual query interpretation, with no inferred financial context.

Recognized spans are consumed longest-first. Every remaining word/number must be
an explicitly harmless grammatical token; otherwise retrieval is blocked.
"""
import re
import unicodedata

from .ingest import METRICS

REQUIRED = ('company', 'metric', 'year', 'quarter', 'kind', 'scope', 'currency', 'scale')
SCALES = (1, 1000, 1000000, 100000000, 1000000000, 1000000000000)
COMPANY_ALIASES = {
    'samsung': ('Samsung Electronics', '삼성전자'),
    'hyundai': ('Hyundai Motor', 'Hyundai Motor Company', '현대자동차'),
}
GRAMMAR = set('''what was is were the a an in of for on at by with please show find
tell me how much did report reported amount value financial statement statements
basis units unit and s
의 은 는 이 가 을 를 에 에서 으로 로 와 과 기준 단위 단위로 단위의 금액
얼마 얼마인가요 얼마인가 얼마인지 알려줘 알려주세요 보여줘 보여주세요 찾아줘 조회 해줘 해주세요
'''.split())
NEGATION = re.compile(r"\b(?:not|no|except|excluding|exclude|without|neither|nor|non)\b|아닌|아니|제외|말고|비연결|비별도", re.I)


def parse_query(query, companies, company_aliases=None):
    """Return explicit filters and diagnostics; missing fields allow candidates.

    Alias configuration maps a registered canonical company to its aliases. It
    cannot register a new company, or resolve an alias shared by two issuers.
    """
    remaining = unicodedata.normalize('NFKC', query).lower().replace('’', "'")
    found = {field: set() for field in REQUIRED}
    issues = []
    if NEGATION.search(remaining):
        issues.append('UNSUPPORTED_NEGATION')
    aliases = []

    def add(phrases, **values):
        for phrase in phrases:
            aliases.append((phrase.lower(), values))

    for company in sorted(set(companies)):
        add([company, *COMPANY_ALIASES.get(company, ()),
             *(company_aliases or {}).get(company, ())], company=company)
    for metric, labels in METRICS.items():
        add([metric, *labels], metric=metric)
    add(['sales', '매출'], metric='revenue')
    add(['net income', 'net profit', '순이익'], metric='net_profit')
    add(['operating income'], metric='operating_profit')
    add(['selling and administrative expenses', 'sg&a'], metric='operating_expenses')
    add(['cfs', 'consolidated', '연결', '연결재무제표'], scope='CFS')
    add(['ofs', 'separate', 'standalone', '별도', '개별', '별도재무제표'], scope='OFS')
    add(['krw', 'korean won', 'south korean won', 'won', '원화'], currency='KRW')
    add(['usd', 'us dollars', 'us dollar', 'u.s. dollars', '미국 달러', '달러'], currency='USD')
    add(['quarter', 'quarter only', 'quarter-only', 'three months', 'three-month',
         '3 months', '3개월', '당분기', '분기 단독'], kind='quarter')
    add(['ytd', 'year to date', 'year-to-date', 'cumulative', '누적'], kind='ytd')
    add(['상반기'], kind='ytd', quarter=2)
    for number, ordinal in enumerate(['first', 'second', 'third', 'fourth'], 1):
        add([f'q{number}', f'{number}분기', f'{number} 분기', f'{ordinal} quarter'], quarter=number)
    for months, word, quarter in [(6, 'six', 2), (9, 'nine', 3), (12, 'twelve', 4)]:
        add([f'first {word} months', f'first {months} months', f'{months}개월 누적'], kind='ytd', quarter=quarter)
    for scale, words in [(1000, ['thousand', 'thousands']), (1000000, ['million', 'millions']),
                         (1000000000, ['billion', 'billions']), (1000000000000, ['trillion', 'trillions'])]:
        add(words, scale=scale)
    for word, scale in [('원 단위', 1), ('천원', 1000), ('백만원', 1000000),
                        ('억원', 100000000), ('십억원', 1000000000), ('조원', 1000000000000)]:
        add([word], currency='KRW', scale=scale)
    for word, scale in [('천', 1000), ('백만', 1000000), ('억', 100000000),
                        ('십억', 1000000000), ('조', 1000000000000)]:
        add([word+' 원'], currency='KRW', scale=scale)
        add([word+' 달러', word+'달러'], currency='USD', scale=scale)
    # Merge identical aliases, preserving ambiguity instead of first-match wins.
    merged = {}
    for phrase, values in aliases:
        fields = merged.setdefault(phrase, {})
        for field, value in values.items():
            fields.setdefault(field, set()).add(value)
    for phrase in sorted(merged, key=lambda p: (-len(p), p)):
        pattern = r'(?<!\w)' + re.escape(phrase).replace(r'\ ', r'\s+') + r'(?![a-z0-9_])'
        if re.search(pattern, remaining):
            for field, values in merged[phrase].items():
                found[field].update(values)
            remaining = re.sub(pattern, ' ', remaining)

    def consume(pattern, field, transform):
        nonlocal remaining
        def record(match):
            found[field].add(transform(match.group(1)))
            return ' '
        remaining = re.sub(pattern, record, remaining)

    consume(r'\bscale\s+(\d+)\b', 'scale', int)
    consume(r'(?<!\d)((?:19|20)\d{2})(?:년)?(?!\d)', 'year', str)
    if found['scale'] - set(SCALES):
        issues.append('UNSUPPORTED_SCALE')
    unknown = sorted({t for t in re.findall(r'[\w]+', remaining) if t not in GRAMMAR})
    # Currency/percentage symbols and operators carry meaning too; punctuation
    # stripping must never silently discard them from a financial request.
    unknown += sorted(set(re.findall(r'[^\w\s.,?!\'":;()/\-]', remaining)))
    if unknown:
        issues.append('UNSUPPORTED_TERMS')
    for field, values in found.items():
        if len(values) > 1:
            issues.append('CONFLICT_' + field.upper())
    blocked = bool(issues)
    filters = {field: next(iter(values)) for field, values in found.items() if len(values) == 1}
    missing = [field for field in REQUIRED if not found[field]]
    issues.extend('MISSING_' + field.upper() for field in missing)
    return {'filters': filters, 'issues': issues, 'missing_fields': missing,
            'unknown_terms': unknown, 'blocked': blocked,
            'trusted_query': not blocked and not missing}
