import argparse, asyncio, hashlib, json, platform, time
from datetime import datetime, timezone
import numpy as np
from .store import ROOT,load_facts
from .search import SearchIndex,CONFIGS,chunks,normalize
from .orchestrator import run_case,cases

def metrics(rows):
 n=len(rows)
 return {'n':n,'recall_at_1':sum(r['rank']==1 for r in rows)/n,'recall_at_3':sum(0<r['rank']<=3 for r in rows)/n,
  'mrr_at_5':sum(1/r['rank'] if r['rank'] else 0 for r in rows)/n,
  'latency_p50_ms':float(np.median([r['latency_ms'] for r in rows])), 'latency_p95_ms':float(np.percentile([r['latency_ms'] for r in rows],95))}

def retrieval(dense=False):
 facts=load_facts();gold=json.loads((ROOT/'data/retrieval_gold.json').read_text()); results={}
 for config in CONFIGS:
  start=time.perf_counter();index=SearchIndex(facts,config);build=(time.perf_counter()-start)*1000;rows=[]
  for q in gold:
   t=time.perf_counter();hits=index.search(q['query'],5);ms=(time.perf_counter()-t)*1000
   rank=next((i+1 for i,h in enumerate(hits) if q['gold_fact_id'] in h['fact_ids']),0)
   rows.append(q|{'rank':rank,'retrieved':[h['id'] for h in hits],'latency_ms':ms})
  results[config]={'metrics':metrics(rows),'index_build_ms':build,'chunk_count':len(index.chunks),'rows':rows}
 if dense:
  from fastembed import TextEmbedding
  corpus=chunks(facts,'cell')
  for name in ['BAAI/bge-small-en-v1.5','sentence-transformers/all-MiniLM-L6-v2']:
   t=time.perf_counter();model=TextEmbedding(model_name=name,cache_dir=str(ROOT/'work/models'),threads=2)
   vectors=np.array(list(model.embed([normalize(c['text']) for c in corpus])));build=(time.perf_counter()-t)*1000;rows=[]
   for q in gold:
    t=time.perf_counter();v=np.array(list(model.query_embed([normalize(q['query'])])))[0];scores=vectors@v
    ranked=np.argsort(-scores,kind='stable')[:5];rank=next((j+1 for j,i in enumerate(ranked) if q['gold_fact_id'] in corpus[i]['fact_ids']),0)
    rows.append(q|{'rank':rank,'retrieved':[corpus[i]['id'] for i in ranked],'latency_ms':(time.perf_counter()-t)*1000})
   results[name]={'metrics':metrics(rows),'index_build_ms':build,'dimension':vectors.shape[1],'threads':2,'chunk_count':len(corpus),'rows':rows,
    'normalization':'Korean controlled vocabulary → English; no multilingual claim', 'model_file_hashes':{str(p.relative_to(ROOT/'work/models')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'work/models').rglob('*.onnx')}}
 return results

async def evaluate_cases(prepared_path=None):
 runs=[];checks=[]
 for c in cases():
  run=await run_case(c['id']);runs.append(run);r=run['result']
  checks.append({'case_id':c['id'],'status_correct':r['status']==c['expected_status'],
   'value_correct':r.get('growth_pct',r.get('derived_value'))==c['expected_value'] if 'expected_value' in c else None,
   'issue_correct':c['expected_issue'] in r.get('issues',[]) if 'expected_issue' in c else None,
   'source_valid':r.get('evidence',[])==c['expected_evidence'],
   'workflow_success':run.get('workflow_success',False)})
 (prepared_path or ROOT/'artifacts/prepared-v2.json').write_text(json.dumps({r['case_id']:r|{'execution_mode':'prepared_replay'} for r in runs},ensure_ascii=False,indent=2)+'\n')
 for check in checks:check['case_correct']=check['workflow_success'] and check['status_correct'] and check['value_correct'] is not False and check['issue_correct'] is not False and check['source_valid']
 total_tools=sum(len(r['trace']) for r in runs)
 return {'checks':checks,'case_accuracy':sum(c['case_correct'] for c in checks)/len(checks),'workflow_success_rate':sum(c['workflow_success'] for c in checks)/len(checks),
  'citation_exact_match':sum(c['source_valid'] for c in checks)/len(checks),'issue_accuracy':sum(c['issue_correct'] for c in checks if c['issue_correct'] is not None)/sum(c['issue_correct'] is not None for c in checks),
  'status_accuracy':sum(c['status_correct'] for c in checks)/len(checks),
  'numeric_accuracy':sum(c['value_correct'] for c in checks if c['value_correct'] is not None)/sum(c['value_correct'] is not None for c in checks),
  'tool_success_rate':sum(t['success'] for r in runs for t in r['trace'])/total_tools if total_tools else None,
  'latency_p50_ms':float(np.median([r['latency_ms'] for r in runs])), 'latency_p95_ms':float(np.percentile([r['latency_ms'] for r in runs],95)),
  'model_calls':0,'provider_api_cost_usd':0,'cost_scope':'Paid model API only, excludes hosting/CPU/download costs'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dense',action='store_true');p.add_argument('--cases-only',action='store_true');p.add_argument('--output',type=__import__('pathlib').Path,default=ROOT/'artifacts/evaluation-current-v2.json');a=p.parse_args()
 path=a.output
 if path.resolve()==(ROOT/'artifacts/evaluation.json').resolve():raise ValueError('PRESERVED_HISTORICAL_ARTIFACT')
 old=ROOT/'artifacts/evaluation.json'
 out=json.loads(old.read_text()) if a.cases_only and old.exists() else {}
 if a.cases_only:out['retrieval_note']='Historical retrieval scores retained from artifacts/evaluation.json; current comparison is in ranking-v2 reports.'
 out.update({'created_at':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'platform':platform.platform(),
  'documents':2,'facts':192,'human_reviewed':False,'evaluation_type':'template regression; not held-out generalization',
  'corpus_sha256':hashlib.sha256((ROOT/'data/facts.json').read_bytes()).hexdigest(),'gold_sha256':hashlib.sha256((ROOT/'data/retrieval_gold.json').read_bytes()).hexdigest()})
 if not a.cases_only:out['retrieval']=retrieval(a.dense)
 out['workflow']=asyncio.run(evaluate_cases())
 path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'retrieval':{k:v['metrics'] for k,v in out.get('retrieval',{}).items()},'workflow':out['workflow']},indent=2))
