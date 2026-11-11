"""Small sequential lab sample, no paid endpoints, no inferred cold start or SLA."""
import argparse,json,math,time
from pathlib import Path
from datetime import datetime,timezone
import httpx

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',default='https://quarterguard.onrender.com');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.base!='https://quarterguard.onrender.com':raise SystemExit('Only the authorized public demo origin')
 a.output.mkdir(parents=True,exist_ok=False)
 body={'mode':'balance_yoy','current_id':'skh2024annual-in-2025oc:financial-position:cash:2024','base_id':'skh2024annual-in-2025oc:financial-position:cash:2023'}
 endpoints=[('health','GET','/health',None),('page','GET','/',None),('search','GET','/api/search?q=samsung%202024%20Q3%20CFS%20revenue%20quarter%20KRW',None),('calculation','POST','/api/source-calculations',body)]
 rows=[]
 with httpx.Client(timeout=30,verify=True) as client:
  for n in range(5):
   for label,method,path,body in endpoints:
    t=time.perf_counter();row={'sample':n+1,'endpoint':label,'at_utc':datetime.now(timezone.utc).isoformat(),'method':method,'path':path}
    try:
     response=client.request(method,a.base+path,json=body) if body else client.request(method,a.base+path)
     row.update(http_status=response.status_code,bytes=len(response.content),ok=response.status_code==200)
     if label=='health':row['health']=response.json()
     if label=='calculation':
      value=response.json();row['growth_pct']=value.get('growth_pct');row['ok']=row['ok'] and value.get('growth_pct')=='47.6820'
     if label=='search':row['hits']=len(response.json().get('hits',[]));row['ok']=row['ok'] and row['hits']>0
    except Exception:row.update(ok=False,error='TRANSPORT_OR_RESPONSE_ERROR')
    row['elapsed_ms']=round((time.perf_counter()-t)*1000,3);rows.append(row)
    (a.output/'requests.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 summary={}
 for label,_,_,_ in endpoints:
  group=[r for r in rows if r['endpoint']==label];values=sorted(r['elapsed_ms'] for r in group)
  summary[label]={'requests':len(group),'successful':sum(r['ok'] for r in group),'first_observed_ms':group[0]['elapsed_ms'],'p50_ms':values[math.ceil(.5*len(values))-1],'p95_ms':values[math.ceil(.95*len(values))-1]}
 (a.output/'summary.json').write_text(json.dumps({'results':summary,'method':'5 sequential samples per endpoint, one HTTPS client, TLS verified, nearest-rank percentiles','paid_calls':0,'limitations':['Not customer traffic or load test','Cold start not forced or verified','Includes network/proxy transit','Five samples make p95 the maximum; not a stable population estimate','No availability SLA inferred']},indent=2))
 print(json.dumps(summary))
if __name__=='__main__':main()
