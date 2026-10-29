"""Optional official DART collector, separate from the verified IR demo corpus."""
import argparse,json,os
from pathlib import Path
import httpx
ENDPOINT='https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
def fetch(corp_code,year,report_code,scope='CFS'):
 key=os.getenv('DART_API_KEY')
 if not key:raise RuntimeError('DART_NOT_CONFIGURED')
 # Never include request URL / key in application error output.
 try:
  r=httpx.get(ENDPOINT,params={'crtfc_key':key,'corp_code':corp_code,'bsns_year':year,'reprt_code':report_code,'fs_div':scope},timeout=30)
  r.raise_for_status();body=r.json()
 except Exception:raise RuntimeError('DART_CONNECTION_FAILED') from None
 if body.get('status')!='000':raise RuntimeError('DART_STATUS_'+str(body.get('status','UNKNOWN')))
 out=[]
 for row in body['list']:
  if row.get('sj_div') not in ('IS','CIS'):continue
  for field,period in [('thstrm_amount','quarter' if report_code in ('11012','11013','11014') else 'annual'),('thstrm_add_amount','ytd')]:
   value=row.get(field)
   if value in ('',None,'-'):continue
   out.append({'company_code':corp_code,'year':year,'report_code':report_code,'scope':scope,
    'account_id':row['account_id'],'account_name':row['account_nm'],'period_kind':period,'currency':row.get('currency'),
    'amount':value.replace(',',''),'source_field':field,'source_url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+row['rcept_no']})
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--corp',default='00126380');p.add_argument('--year',default='2024');p.add_argument('--report',default='11014');p.add_argument('--output',type=Path,default=Path('work/dart.json'));a=p.parse_args()
 try:
  data=fetch(a.corp,a.year,a.report);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(f'{len(data)} records saved')
 except RuntimeError as e:print(str(e));raise SystemExit(1)
