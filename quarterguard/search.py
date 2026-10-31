"""Controlled comparison of chunk boundaries and retrieval representations."""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .ingest import METRICS
from .query import parse_query

CONFIGS=('fixed_word','cell_word','cell_char','hybrid_meta')
def normalize(q):
    for a,b in [('삼성전자','samsung'),('연결','CFS'),('별도','OFS'),('3분기','Q3'),('2분기','Q2'),('3개월','quarter'),('누적','ytd'),('원화','KRW'),('달러','USD')]+[(v[1],k) for k,v in METRICS.items()]: q=q.replace(a,b)
    q=re.sub(r"([1-4])분기",r"q\1",q.lower())
    return re.sub(r"(20\d{2})년",r"\1",q)

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
        metadata = sorted({f.company for f in rows}) + [key[0], key[1]]
        metadata += sorted({f.start[:4] for f in rows})
        metadata += sorted({f.currency for f in rows})
        metadata += sorted({'quarter' if f.months == 3 else 'ytd' for f in rows})
        text=' '.join(metadata)+'\n';spans=[]
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

def constraints(q, companies=None, company_aliases=None):
    parsed = parse_query(q, companies if companies is not None else ['samsung'], company_aliases)
    return None if parsed['blocked'] else parsed['filters']

def compatible(f,filters):
    for k,v in filters.items():
        actual= f.start[:4] if k=='year' else (int(f.end[5:7])+2)//3 if k=='quarter' else ('quarter' if f.months==3 else 'ytd') if k=='kind' else getattr(f,k)
        if actual!=v:return False
    return True

class SearchIndex:
    def __init__(self,facts,config='hybrid_meta',company_aliases=None):
        if config not in CONFIGS:raise ValueError('INVALID_CONFIG')
        facts=list(facts)
        self.companies={f.company for f in facts};self.company_aliases=company_aliases
        self.config=config;self.facts={f.id:f for f in facts};self.chunks=chunks(facts,'fixed' if config=='fixed_word' else 'cell')
        corpus=[normalize(c['text']) for c in self.chunks]
        self.word=TfidfVectorizer(ngram_range=(1,2));self.w=self.word.fit_transform(corpus)
        self.char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5));self.c=self.char.fit_transform(corpus)
    def search(self,query,k=5):
        if not query.strip():return []
        if not 1<=k<=20:raise ValueError('INVALID_K')
        if self.config=='hybrid_meta':return self.search_with_diagnostics(query,k)['hits']
        return self._rank(query,k,{})

    def search_with_diagnostics(self,query,k=5):
        if not 1<=k<=20:raise ValueError('INVALID_K')
        parsed=parse_query(query,self.companies,self.company_aliases)
        # Require some explicit financial context before presenting candidates.
        hits=[] if parsed['blocked'] or not query.strip() or not parsed['filters'] else self._rank(query,k,parsed['filters'])
        count=0 if parsed['blocked'] or not parsed['filters'] else sum(compatible(f,parsed['filters']) for f in self.facts.values())
        if parsed['trusted_query'] and count>1:
            parsed['issues'].append('AMBIGUOUS_FACT')
            parsed['trusted_query']=False
        status='needs_clarification' if not parsed['trusted_query'] else 'ready' if hits else 'no_results'
        return parsed|{'hits':hits,'status':status,'answer_status':'not_verified','candidate_fact_count':count}

    def _rank(self,query,k,filters):
        q=normalize(query); w=(self.w@self.word.transform([q]).T).toarray().ravel();c=(self.c@self.char.transform([q]).T).toarray().ravel()
        scores=c if self.config=='cell_char' else .5*w+.5*c if self.config=='hybrid_meta' else w
        candidates=[i for i,item in enumerate(self.chunks) if scores[i]>0 and (not filters or (item['fact_ids'] and all(compatible(self.facts[fid],filters) for fid in item['fact_ids'])))]
        order=sorted(candidates,key=lambda i:(-float(scores[i]),self.chunks[i]['id']))[:k]
        return [self.chunks[i]|{'score':round(float(scores[i]),6)} for i in order]
