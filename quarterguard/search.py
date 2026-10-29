"""Controlled comparison of chunk boundaries and retrieval representations."""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .ingest import METRICS

CONFIGS=('fixed_word','cell_word','cell_char','hybrid_meta')
def normalize(q):
    for a,b in [('삼성전자','samsung'),('연결','CFS'),('별도','OFS'),('3분기','Q3'),('2분기','Q2'),('3개월','quarter'),('누적','ytd'),('원화','KRW'),('달러','USD')]+[(v[1],k) for k,v in METRICS.items()]: q=q.replace(a,b)
    return re.sub(r"(20\d{2})년",r"\1",q.lower())

def describe(f):
    quarter=(int(f.end[5:7])+2)//3
    return f'{f.company} {f.metric} {METRICS[f.metric][0]} {METRICS[f.metric][1]} {f.scope} {f.start[:4]} Q{quarter} {"quarter" if f.months==3 else "ytd"} {f.start} {f.end} {f.currency} scale {f.scale} value {f.value}'

def chunks(facts,strategy):
    if strategy=='cell': return [{'id':f.id,'text':describe(f),'fact_ids':[f.id]} for f in facts]
    # Serialise each table once with a shared header, then split blindly every 180 chars.
    groups={}
    for f in facts: groups.setdefault((f.document_id,f.scope),[]).append(f)
    result=[]
    for key,rows in groups.items():
        text=f'samsung {key[0]} {key[1]} 2024 2023 KRW USD quarter ytd\n';spans=[]
        for metric in METRICS:
            text+=METRICS[metric][0]+' '
            for f in [f for f in rows if f.metric==metric]:
                start=len(text);text+=f.value+' ';spans.append((start,len(text)-1,f.id))
            text+='\n'
        for start in range(0,len(text),180):
            end=start+180
            result.append({'id':f'{key}-{start}','text':text[start:end],
              'fact_ids':[fid for a,b,fid in spans if a>=start and b<=end]})
    return result

def constraints(q):
    q=normalize(q); filt={}
    # The public explorer supports an explicit entity and controlled financial terms.
    # Unknown entities are not a request for the only entity in the corpus.
    if not re.search(r'\bsamsung\b',q):return None
    filt['company']='samsung'
    if any(re.search(r'\b'+c+r'\b',q) for c in ('eur','jpy','gbp','cny','hkd','cad','aud')):return None
    for key,vals in [('scope',['cfs','ofs']),('currency',['krw','usd']),('metric',list(METRICS))]:
        found=[v for v in vals if re.search(r'\b'+re.escape(v)+r'\b',q)]
        if len(found)>1:return None
        if len(found)==1:filt[key]=found[0].upper() if key in ('scope','currency') else found[0]
    years=set(re.findall(r'\b20\d{2}\b',q))
    if len(years)>1:return None
    if years:filt['year']=next(iter(years))
    qs=set(re.findall(r'\bq([1-4])\b',q))
    if len(qs)>1:return None
    if qs:filt['quarter']=int(next(iter(qs)))
    if 'ytd' in q and 'quarter' in q:return None
    if 'ytd' in q:filt['kind']='ytd'
    elif 'quarter' in q:filt['kind']='quarter'
    return filt

def compatible(f,filters):
    for k,v in filters.items():
        actual= f.start[:4] if k=='year' else (int(f.end[5:7])+2)//3 if k=='quarter' else ('quarter' if f.months==3 else 'ytd') if k=='kind' else getattr(f,k)
        if actual!=v:return False
    return True

class SearchIndex:
    def __init__(self,facts,config='hybrid_meta'):
        if config not in CONFIGS:raise ValueError('INVALID_CONFIG')
        self.config=config;self.facts={f.id:f for f in facts};self.chunks=chunks(facts,'fixed' if config=='fixed_word' else 'cell')
        corpus=[normalize(c['text']) for c in self.chunks]
        self.word=TfidfVectorizer(ngram_range=(1,2));self.w=self.word.fit_transform(corpus)
        self.char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5));self.c=self.char.fit_transform(corpus)
    def search(self,query,k=5):
        if not query.strip():return []
        if not 1<=k<=20:raise ValueError('INVALID_K')
        q=normalize(query); w=(self.w@self.word.transform([q]).T).toarray().ravel();c=(self.c@self.char.transform([q]).T).toarray().ravel()
        scores=c if self.config=='cell_char' else .5*w+.5*c if self.config=='hybrid_meta' else w
        filters=constraints(query) if self.config=='hybrid_meta' else {}
        if filters is None:return []
        candidates=[i for i,item in enumerate(self.chunks) if scores[i]>0 and (not filters or all(compatible(self.facts[fid],filters) for fid in item['fact_ids']))]
        order=sorted(candidates,key=lambda i:(-float(scores[i]),self.chunks[i]['id']))[:k]
        return [self.chunks[i]|{'score':round(float(scores[i]),6)} for i in order]
