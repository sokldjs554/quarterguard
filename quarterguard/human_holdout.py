"""Freeze human-authored retrieval cases, reserve first attempt, and score separately.

Question/document selection are the only runtime inputs. Gold is never used to
rewrite a query, select a successful cell, or add a missing source to the corpus.
This is retrieval evaluation, NOT an automatic multi-part answer benchmark.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from .store import ROOT,load_facts
from .search import SearchIndex
from .source_evidence import DOCUMENT_ID,search_source

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def validate(data):
    author=data.get('author',{})
    if not isinstance(author.get('id'),str) or not author['id'].strip() or author.get('ai_used') is not False:raise ValueError('HUMAN_PROVENANCE_REQUIRED')
    rows=data.get('cases')
    if not isinstance(rows,list) or not rows or len(rows)>30:raise ValueError('CASE_COUNT')
    seen=set()
    for row in rows:
        if not isinstance(row.get('id'),str) or not row['id'] or row['id'] in seen:raise ValueError('CASE_ID')
        seen.add(row['id'])
        if not isinstance(row.get('question'),str) or not 0<len(row['question'])<=500:raise ValueError('QUESTION')
        if row.get('document_id') is not None and not isinstance(row['document_id'],str):raise ValueError('DOCUMENT')
        gold=row.get('expected',{})
        if not isinstance(gold.get('status'),str) or not isinstance(gold.get('rows'),list):raise ValueError('GOLD_REQUIRED')
        for cell in gold['rows']:
            if not isinstance(cell,dict) or not cell or any(not isinstance(k,str) for k in cell):raise ValueError('GOLD_CELL')
        sources=row.get('sources')
        if not isinstance(sources,list) or not sources:raise ValueError('SOURCE_REQUIRED')
        if any(not isinstance(s,dict) or not isinstance(s.get('url'),str) or not s['url'].startswith('https://') or type(s.get('page')) is not int or s['page']<1 or not s.get('row') or not s.get('column') for s in sources):raise ValueError('SOURCE_LOCATION_REQUIRED')
    return data

def freeze(data):
    validate(data)
    return {'dataset':data,'sha256':digest(data),'authorship_basis':'Participant declaration; not independently proven by software.'}

def retrieve(question,document_id):
    if document_id:
        if document_id!=DOCUMENT_ID:return {'status':'needs_review','issues':['UNSUPPORTED_DOCUMENT'],'hits':[]}
        return search_source(document_id,question)
    return SearchIndex(load_facts(),'hybrid_meta').search_with_diagnostics(question,3)

def score(gold,actual):
    facts={f.id:f.public() for f in load_facts()}
    cells=[]
    for hit in actual.get('hits',[]):
        if 'cell' in hit:cells.append(hit['cell'])
        else:cells.extend(facts[fid] for fid in hit.get('fact_ids',[]) if fid in facts)
    expected=gold['rows']
    matches=sum(any(all(cell.get(k)==v for k,v in wanted.items()) for cell in cells) for wanted in expected)
    return {'passed':actual.get('status')==gold['status'] and matches==len(expected) and (bool(expected) or not cells),
      'matched_rows':matches,'required_rows':len(expected),'retrieved_rows':len(cells),
      'required_row_recall':matches/len(expected) if expected else None,
      'status_match':actual.get('status')==gold['status']}

def run(frozen,output,ledger,*,runtime=retrieve):
    data=validate(frozen['dataset'])
    if digest(data)!=frozen['sha256']:raise ValueError('DATA_CHANGED_AFTER_FREEZE')
    ledger=Path(ledger);ledger.mkdir(parents=True,exist_ok=True)
    output=Path(output)
    with (ledger/(frozen['sha256']+'.json')).open('x') as f:
        json.dump({'started_at':datetime.now(timezone.utc).isoformat(),'output':str(output)},f);f.flush();os.fsync(f.fileno())
    output.mkdir(parents=True,exist_ok=False)
    report={'dataset_sha256':frozen['sha256'],'rows':[],'evaluation_scope':'retrieval only; no full-answer or LLM claim',
      'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'code_and_corpus_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ('quarterguard','data') for p in (ROOT/base).rglob('*') if p.is_file() and p.suffix in ('.py','.json')},
      'new_llm_calls':0,'human_gold':data['author'],'first_attempt':True}
    (output/'frozen.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2))
    for case in data['cases']:
        execution_success=True
        try:actual=runtime(case['question'],case.get('document_id'))
        except Exception:
            execution_success=False
            actual={'status':'needs_review','issues':['EXECUTION_ERROR'],'hits':[]}
        scored=score(case['expected'],actual)
        if not execution_success:scored['passed']=False
        report['rows'].append({'id':case['id'],'actual':actual,'execution_success':execution_success,'score':scored})
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run']);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    data=json.loads(a.input.read_text())
    if a.command=='freeze':
        with a.output.open('x') as f:json.dump(freeze(data),f,ensure_ascii=False,indent=2)
    else:run(data,a.output,ROOT/'work/human-first-attempts')
if __name__=='__main__':main()
