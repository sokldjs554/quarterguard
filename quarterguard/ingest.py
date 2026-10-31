"""Layout-specific PDF adapter. Reject unsupported headers instead of guessing."""
import argparse, hashlib, json, re
from pathlib import Path
from .core import Fact

ROOT=Path(__file__).resolve().parents[1]
METRICS={
 'revenue':('Revenue','매출액'),
 'cost_of_sales':('Cost of sales','매출원가'),
 'gross_profit':('Gross profit','매출총이익'),
 'operating_expenses':('Selling and administrative expenses','판매관리비'),
 'operating_profit':('Operating profit','영업이익'),
 'net_profit':('Profit for the period','당기순이익')}
# Exactly eight amount cells: direct quarter then cumulative, each KRW/USD
# current/prior year. A short leading Notes cell is separately validated.
AMOUNT = r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?'
CELL = rf'(?:-?{AMOUNT}|\({AMOUNT}\))'
NOTE = r'(?:[1-9]\d?(?:,\s*[1-9]\d?){0,2}|\([1-9]\d?(?:,\s*[1-9]\d?){0,2}\))'


def _normalize_statement(text):
    # pypdf sometimes breaks the final comma group at a physical newline.
    # Join only a uniquely completable three-digit group, never whole cells.
    broken = r'(?<![\d,])(\(?-?\d{1,3}(?:,\d{3})*,)(\d{1,2})[ \t]*\r?\n[ \t]*(\d{1,2})(?=\)?(?:\s|$))'
    def join_group(match):
        if len(match[2] + match[3]) != 3:
            return match[0]
        return match[1] + match[2] + match[3]
    return re.sub(r'\s+', ' ', re.sub(broken, join_group, text)).strip()


def _statement_context(t, doc, page):
    scopes = re.findall(r'INTERIM (CONSOLIDATED|SEPARATE)', t)
    if len(scopes) != 1:
        raise ValueError('UNSUPPORTED_LAYOUT: scope')
    scope = 'CFS' if scopes[0] == 'CONSOLIDATED' else 'OFS'
    if doc.get('scope', scope) != scope or doc.get('statement_pages', {}).get(scope, page) != page:
        raise ValueError('UNSUPPORTED_LAYOUT: manifest scope or page')
    q = doc.get('quarter')
    if q not in (2, 3):
        raise ValueError('UNSUPPORTED_LAYOUT: quarter')
    month, day, word, month_name = {2: ('06', '30', 'six', 'June'),
                                   3: ('09', '30', 'nine', 'September')}[q]
    heading = rf'INTERIM {scopes[0]} STATEMENTS OF PROFIT OR LOSS '
    units = r'\(?In millions of Korean won(?: and|,) in thousands of US dollars(?: \(Note \d+(?:\.\d+)?\))?\)? '
    periods = (rf'For the three-month periods ended {month_name} {day}, '
               rf'For the {word}-month periods ended {month_name} {day}, ')
    columns = r'Notes (?P<years>(?:\d{4} ){7}\d{4}) KRW KRW USD USD KRW KRW USD USD(?= Revenue )'
    matches = list(re.finditer(heading + units + periods + columns, t))
    if len(matches) != 1 or len(re.findall(r'For the \w+-month periods ended', t)) != 2:
        raise ValueError('UNSUPPORTED_LAYOUT: ordered header, units or periods')
    years = [int(y) for y in matches[0]['years'].split()]
    year = years[0]
    if not 1901 <= year <= 9999 or years != [year, year-1] * 4:
        raise ValueError('UNSUPPORTED_LAYOUT: year columns')
    report_end = f'{year}-{month}-{day}'
    if doc.get('report_end', report_end) != report_end:
        raise ValueError('UNSUPPORTED_LAYOUT: reporting date')
    return scope, month, day, years, matches[0].end()


def _row_cells(t, metric):
    label = METRICS[metric][0]
    pattern = re.escape(label) + (r'(?: \(loss\))?' if metric == 'operating_profit' else '')
    matches = list(re.finditer(r'(?<!\w)' + pattern + r'\s+(?=[\d(.-])([\d,().\s-]+)', t))
    if len(matches) != 1:
        raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} missing or duplicate row')
    # A canonical label must start the table or follow a complete monetary row.
    # A word boundary alone admits "Adjusted Gross profit" (including wrapped
    # qualifiers). Requiring the previous eight cells also supports flattened
    # extraction without treating a qualifier's lone note number as a row end.
    prefix = t[:matches[0].start()].strip()
    if prefix:
        previous = re.search(r'(?<![\w,.])(?:\(?-?\d)[\d,().\s-]*$', prefix)
        if previous is None:
            raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} row label boundary')
        _amount_cells(previous[0], metric + ' preceding row')
    if matches[0].end() < len(t) and not t[matches[0].end()-1].isspace():
        raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} malformed amount boundary')
    return _amount_cells(matches[0][1].strip(), metric)


def _amount_cells(row, metric):
    matched = re.fullmatch(rf'(?:(?P<note>{NOTE})\s+)?(?P<cells>{CELL}(?:\s+{CELL}){{7}})', row)
    if not matched:
        raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} cells or notes')
    cells = matched['cells'].split()
    if matched['note'] is None and re.fullmatch(NOTE, cells[0]):
        raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} ambiguous note or missing cell')
    return cells


def parse_statement(text, doc, page, metrics=None):
    """Parse a bounded bilingual-currency interim layout; never infer from IDs."""
    t = _normalize_statement(text)
    scope, month, day, years, header_end = _statement_context(t, doc, page)
    out = []
    for metric in metrics or METRICS:
        if metric not in METRICS:
            raise ValueError(f'UNSUPPORTED_LAYOUT: metric {metric}')
        label = METRICS[metric][0]
        nums = _row_cells(t[header_end:], metric)
        for col, n in enumerate(nums):
            year = years[col]
            curr = 'KRW' if col % 4 < 2 else 'USD'
            cumulative = col >= 4
            start = f'{year}-01-01' if cumulative else f'{year}-{int(month)-2:02d}-01'
            end = f'{year}-{month}-{day}'
            period = 'ytd' if cumulative else 'q'
            out.append(Fact(id=f"{doc['id']}-{scope}-{metric}-{year}-{period}-{curr}",
              company=doc.get('company', 'samsung'), metric=metric, scope=scope, currency=curr,
              scale=1000000 if curr=='KRW' else 1000, start=start, end=end,
              value=n.replace(',', '').replace('(', '-').replace(')', ''),
              source_url=doc['url'], page=page, row=label, column=f'{year} {period.upper()} {curr}',
              document_id=doc['id'], document_sha256=doc['sha256'],
              translation_basis='convenience_translation' if curr=='USD' else 'reported_currency',
              translation_rate=doc.get('usd_translation_rate') if curr=='USD' else None,
              translation_note_page=doc.get('usd_note_pages', {}).get(scope) if curr=='USD' else None))
    return out

def collect(cache:Path,download=False):
    import httpx
    from pypdf import PdfReader
    sources=json.loads((ROOT/'data/sources.json').read_text())
    facts=[]; paragraphs=[]
    cache.mkdir(parents=True,exist_ok=True)
    for doc in sources:
        path=cache/(doc['id']+'.pdf')
        if download:
            with httpx.Client(timeout=90,follow_redirects=True) as client:
                r=client.get(doc['url']);r.raise_for_status();path.write_bytes(r.content)
        raw=path.read_bytes();doc['sha256']=hashlib.sha256(raw).hexdigest()
        reader=PdfReader(path);doc['pages']=len(reader.pages); tables=0
        for note_page in doc.get('usd_note_pages',{}).values():
            note=reader.pages[note_page-1].extract_text() or ''
            rate=doc['usd_translation_rate'];formatted=f'{float(rate):,.1f}'
            if 'Convenience Translation' not in note or formatted not in note:
                raise ValueError('UNSUPPORTED_LAYOUT: translation note')
        for i,p in enumerate(reader.pages):
            text=p.extract_text() or ''
            if 'STATEMENTS OF PROFIT OR LOSS' in text and 'Revenue' in text:
                parsed=parse_statement(text,doc,i+1);facts.extend(parsed);tables+=1
                doc.setdefault('statement_pages',{})[parsed[0].scope]=i+1
            else:
                paragraphs.append({'document_id':doc['id'],'page':i+1,'kind':'body','text':text})
        if tables!=2: raise ValueError(f'UNSUPPORTED_LAYOUT: expected 2 statements, got {tables}')
    # Full text stays private in ignored cache. Only atomic numeric facts are distributed.
    (cache/'body.json').write_text(json.dumps(paragraphs,ensure_ascii=False))
    (ROOT/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/facts.json').write_text(json.dumps([f.public() for f in facts],ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'documents':len(sources),'facts':len(facts),'body_pages_local_only':len(paragraphs)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');p.add_argument('--cache',type=Path,default=ROOT/'work/raw');a=p.parse_args();collect(a.cache,a.download)
