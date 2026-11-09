"""Bounded Hyundai interim income-statement adapter, KRW millions only.

Literal issuer labels are mapped to the existing canonical Fact.row vocabulary.
The four physical columns are current Q/YTD, then prior Q/YTD. No production
source registration or gold fixtures are used by this adapter.
"""
import re

from .core import Fact


ROWS = {
    'revenue': ('Sales', 'Revenue'),
    'cost_of_sales': ('Cost of sales', 'Cost of sales'),
    'gross_profit': ('Gross profit', 'Gross profit'),
    'operating_expenses': ('Selling and administrative expenses', 'Selling and administrative expenses'),
    'operating_profit': ('Operating profit', 'Operating profit'),
    'net_profit': ('Profit for the period', 'Profit for the period'),
}
AMOUNT = r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?'
CELL = rf'(?:-?{AMOUNT}|\({AMOUNT}\))'
NOTE = r'(?:[1-9]\d?(?:,\s*[1-9]\d?){0,2}|\([1-9]\d?(?:,\s*[1-9]\d?){0,2}\))'


def _context(text, doc, page):
    title = 'INTERIM CONSOLIDATED STATEMENTS OF INCOME'
    if doc.get('company') != 'hyundai' or text.count(title) != 1:
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai issuer or statement title')
    if len(re.findall(r'INTERIM (?:CONSOLIDATED|SEPARATE) STATEMENTS', text)) != 1:
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai scope ambiguity')
    if (doc.get('scope', 'CFS') != 'CFS'
            or ('statement_pages' in doc and doc['statement_pages'].get('CFS') != page)
            or not isinstance(page, int) or page < 1 or page > doc.get('pages', page)):
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai manifest scope or page')
    quarter = doc.get('quarter')
    if quarter not in (2, 3):
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai quarter')
    month, name, word = {2: ('06', 'June', 'Six'), 3: ('09', 'September', 'Nine')}[quarter]
    period = rf'Three-month period ended {name} 30 {word}-month period ended {name} 30'
    header = (
        r'HYUNDAI MOTOR COMPANY AND ITS SUBSIDIARIES '
        + title + ' '
        + rf'FOR THE THREE-MONTH AND {word.upper()}-MONTH PERIODS ENDED {name.upper()} 30, '
        + r'(?P<year>\d{4}) AND (?P<prior>\d{4}) \(Unaudited\) '
        + r'(?P=year) (?P=prior) NOTES '
        + period + ' ' + period + ' '
        + r'\(In millions of Korean Won, except per share amounts\)(?= Sales )'
    )
    matches = list(re.finditer(header, text))
    if len(matches) != 1:
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai ordered header, years, periods or units')
    match = matches[0]
    year, prior = int(match['year']), int(match['prior'])
    if not 1901 <= year <= 9999 or prior != year - 1:
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai year columns')
    if doc.get('report_end', f'{year}-{month}-30') != f'{year}-{month}-30':
        raise ValueError('UNSUPPORTED_LAYOUT: Hyundai reporting date')
    return year, prior, month, match.end()


def _amounts(row, metric, *, boundary_only=False):
    # A note may precede four complete cells. Currency signs, when present,
    # must mark every cell; partial/mixed currency rows are not accepted.
    # A printed dash can establish the end of an unrelated preceding row.
    # It is never interpreted as a number or emitted as a target metric value.
    cell = rf'(?:{CELL}|-)' if boundary_only else CELL
    match = re.fullmatch(
        rf'(?:(?P<note>{NOTE})\s+)?(?P<cells>(?:￦\s+)?{cell}(?:\s+(?:￦\s+)?{cell}){{3}})',
        row.strip())
    if not match or match['cells'].count('￦') not in (0, 4):
        raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai {metric} cells or notes')
    cells = match['cells'].replace('￦', '').split()
    if match['note'] is None and '￦' not in match['cells'] and re.fullmatch(NOTE, cells[0]):
        raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai {metric} ambiguous note or missing cell')
    return cells


def _row(text, metric):
    label = ROWS[metric][0]
    matches = list(re.finditer(r'(?<!\w)' + re.escape(label)
                              + r'\s+(?=[\d(￦.-])([\d,().\s￦-]+)', text))
    if len(matches) != 1:
        raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai {metric} missing or duplicate row')
    match = matches[0]
    prefix = text[:match.start()].strip()
    if prefix:
        previous = re.search(r'(?<![\w,.])(?:￦|\(?-?\d|-(?=\s))[\d,().\s￦-]*$', prefix)
        if previous is None:
            raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai {metric} row label boundary')
        _amounts(previous[0], metric + ' preceding row', boundary_only=True)
    if match.end() < len(text) and not text[match.end()-1].isspace():
        raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai {metric} malformed amount boundary')
    return _amounts(match[1], metric)


def parse_statement(text, doc, page, metrics=None):
    """Parse verified CFS Q2/Q3 year-grouped columns; reject unknown layouts."""
    text = re.sub(r'\s+', ' ', text).strip()
    year, prior, month, header_end = _context(text, doc, page)
    result = []
    for metric in metrics or ROWS:
        if metric not in ROWS:
            raise ValueError(f'UNSUPPORTED_LAYOUT: Hyundai metric {metric}')
        cells = _row(text[header_end:], metric)
        for col, value in enumerate(cells):
            cell_year = year if col < 2 else prior
            cumulative = col % 2 == 1
            period = 'ytd' if cumulative else 'q'
            start = f'{cell_year}-01-01' if cumulative else f'{cell_year}-{int(month)-2:02d}-01'
            result.append(Fact(
                id=f"{doc['id']}-CFS-{metric}-{cell_year}-{period}-KRW",
                company='hyundai', metric=metric, scope='CFS', currency='KRW', scale=1000000,
                start=start, end=f'{cell_year}-{month}-30',
                value=value.replace(',', '').replace('(', '-').replace(')', ''),
                source_url=doc['url'], page=page, row=ROWS[metric][1],
                column=f'{cell_year} {period.upper()} KRW', document_id=doc['id'],
                document_sha256=doc['sha256']))
    return result
