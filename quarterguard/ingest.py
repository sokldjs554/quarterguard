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
NUMBER=r'\(?-?\d{1,3}(?:,\d{3})+\)?|\(?-?\d+(?:\.\d+)?\)?'

def parse_statement(text,doc,page,metrics=None):
    t=re.sub(r'\s+',' ',text)
    required=['STATEMENTS OF PROFIT OR LOSS','millions of Korean won','thousands of US dollars','KRW KRW USD USD KRW KRW USD USD','2024 2023 2024 2023 2024 2023 2024 2023']
    if not all(s in t for s in required): raise ValueError('UNSUPPORTED_LAYOUT: header')
    q=doc['quarter']; month,day,word={2:('06','30','six'),3:('09','30','nine')}[q]
    month_name={2:'June',3:'September'}[q]
    expected=f'For the three-month periods ended {month_name} {day}, For the {word}-month periods ended {month_name} {day}, Notes 2024 2023 2024 2023 2024 2023 2024 2023 KRW KRW USD USD KRW KRW USD USD'
    if expected not in t or doc.get('report_end',f'2024-{month}-{day}')!=f'2024-{month}-{day}':
        raise ValueError('UNSUPPORTED_LAYOUT: ordered periods or reporting date')
    scope='CFS' if 'INTERIM CONSOLIDATED' in t else 'OFS' if 'INTERIM SEPARATE' in t else None
    if not scope: raise ValueError('UNSUPPORTED_LAYOUT: scope')
    out=[]
    for metric in metrics or METRICS:
        label=METRICS[metric][0]
        pattern=re.escape(label)+(r'(?: \(loss\))?' if metric=='operating_profit' else '')
        m=re.search(pattern+r'\s+((?:[\d,().\-]+\s+){7,12})',t)
        if not m: raise ValueError('UNSUPPORTED_LAYOUT: '+metric)
        nums=re.findall(NUMBER,m.group(1))
        # Notes precede exactly eight data cells. Metric-specific expected note count.
        notes={'revenue':1,'cost_of_sales':1,'gross_profit':0,'operating_expenses':2,'operating_profit':1,'net_profit':0}[metric]
        if len(nums)!=8+notes: raise ValueError(f'UNSUPPORTED_LAYOUT: {metric} cells {len(nums)}')
        for col,n in enumerate(nums[notes:]):
            year=2024 if col%2==0 else 2023; curr='KRW' if col%4<2 else 'USD'; cumulative=col>=4
            start=f'{year}-01-01' if cumulative else f'{year}-{int(month)-2:02d}-01'
            end=f'{year}-{month}-{day}'; period='ytd' if cumulative else 'q'
            out.append(Fact(id=f"{doc['id']}-{scope}-{metric}-{year}-{period}-{curr}",company='samsung',metric=metric,scope=scope,currency=curr,
              scale=1000000 if curr=='KRW' else 1000,start=start,end=end,value=n.replace(',','').replace('(','-').replace(')',''),
              source_url=doc['url'],page=page,row=label,column=f'{year} {period.upper()} {curr}',document_id=doc['id'],document_sha256=doc['sha256'],translation_basis='convenience_translation' if curr=='USD' else 'reported_currency',
              translation_rate=doc.get('usd_translation_rate') if curr=='USD' else None,
              translation_note_page=doc.get('usd_note_pages',{}).get(scope) if curr=='USD' else None))
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
