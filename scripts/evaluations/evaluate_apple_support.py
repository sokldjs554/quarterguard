"""Post-change development/regression run. Original seven questions are unchanged.

No paid API calls. Local API uses canonical source extraction, never submitted
answers. Gold is used only after execution. Qualitative scoring is rule-based AI
assessment, not independent expert judgment.
"""
import argparse,asyncio,gzip,hashlib,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from fastapi.testclient import TestClient
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.api import app
from quarterguard import apple_source as source
from quarterguard.store import ROOT
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
raw=gzip.decompress((source.DATA/'source.html.gz').read_bytes())
assert hashlib.sha256(raw).hexdigest()==source.SHA
raw_path=args.output/'source.html';raw_path.write_bytes(raw)
parsed=source.parse_html(raw_path);raw_path.unlink()
assert parsed==source.load_source()[1]
gold=json.loads((ROOT/'artifacts/apple-first-20261112/source-audit.json').read_text())['cells']
matched=[]
for g in gold:
 candidates=[c for c in parsed['cells'] if c['printed_page']==g['printed_page'] and c['row']==g['row'] and c['section']==g['section'] and c['year']==g['year_column']]
 matched.append({'row':g['row'],'section':g['section'],'year':g['year_column'],'page':g['printed_page'],'passed':len(candidates)==1 and candidates[0]['value']==g['value'] and candidates[0]['currency']=='USD' and candidates[0]['scale']==1000000,'actual_ids':[c['id'] for c in candidates]})
assert all(x['passed'] for x in matched)
expectations=[{'products_margin_pct':'37.1806','services_margin_pct':'73.8804'},{'china_difference':'-5607','total_difference':'7750'},{'operating_cash_less_capex':'108807'},{'spending_increase':'17399','signed_cash_flow_change':'-17399'},{'operating_profit_change':'8915','tax_expense_change':'13008','net_income_change':'-3259','state_aid_tax':'10246'},{'products_margin_pct':'37.1806','services_margin_pct':'73.8804'},{}]
cases=json.loads((ROOT/'data/apple-submitted-20261112/submission.json').read_text())['cases'];rows=[]
with TestClient(app) as client:
 for i,c in enumerate(cases):
  t=time.perf_counter();search=client.get('/api/source-search',params={'document_id':source.DOCUMENT_ID,'q':c['question']});review=client.post('/api/source-review',json={'document_id':source.DOCUMENT_ID,'query':c['question']});ms=(time.perf_counter()-t)*1000
  assert search.status_code==review.status_code==200
  s,r=search.json(),review.json();status='verified' if i<5 else 'needs_review'
  valid=(len(s['hits'])>0 and r['status']==status and r['values']==expectations[i] and all(client.get('/api/source-cells/'+e['id']).json()==e for e in r['evidence']))
  if i>=5:valid=valid and bool(r['required_information']) and bool(r['issues'])
  rows.append({'id':c['id'],'query':c['question'],'search':s,'review':r,'latency_ms':round(ms,3),'passed':bool(valid),'rubric':'numeric exact match + expected decision + canonical evidence lookup; qualitative rules not human grading'})
 # New AI-authored variations, not a fresh human holdout.
 variations=[('2023 products services gross margin','verified'),('2024 operating cash flow minus capex','verified'),('2024 buyback spending increase','verified'),('2024 greater china sales decline volume only','needs_review'),('2024 products services gross margin adjusted','needs_review'),('2024 products services gross margin KRW','needs_review'),('2024 products services gross margin separate','needs_review'),('2025 products services gross margin','needs_review'),('2024 products services gross margin quarter','needs_review'),('products services gross margin','needs_review'),('2024 products services gross margin forecast','needs_review'),('2024 products services gross margin not services','needs_review')]
 variations += [(q,'needs_review') for q in ['2023년 자사주 매입에 쓴 현금은 2024년보다 얼마나 늘었나?', '2023 buyback spending increase versus 2024', '2024 capex minus operating cash flow', '2024 subtract operating cash flow from capex', '2024 제품 서비스 매출총이익률 공통비 차감', '2024 products services gross margin less tax', '2024 products services gross margin and operating cash flow minus capex']]
 synthetic=[]
 for q,status in variations:
  r=client.post('/api/source-review',json={'document_id':source.DOCUMENT_ID,'query':q}).json();synthetic.append({'query':q,'expected_status':status,'actual':r,'passed':r['status']==status})
async def mcp_run():
 calls=[]
 async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.source_mcp_server'],cwd=str(ROOT))) as (r,w):
  async with ClientSession(r,w) as session:
   await session.initialize()
   async def call(name,arguments):
    output=await session.call_tool(name,arguments);data=output.structuredContent or json.loads(next(c.text for c in output.content if c.type=='text')) if not output.isError else {'error':True}
    calls.append({'order':len(calls)+1,'tool':name,'arguments':arguments,'isError':bool(output.isError),'output':data});return data
   found=await call('search_source_evidence',{'document_id':source.DOCUMENT_ID,'query':cases[2]['question']})
   for hit in found['hits']:await call('get_source_cell',{'cell_id':hit['cell']['id']})
   await call('review_source_document',{'document_id':source.DOCUMENT_ID,'query':cases[2]['question']})
   await call('review_source_document',{'document_id':source.DOCUMENT_ID,'query':cases[6]['question']})
   await call('get_source_cell',{'cell_id':'apple-2024-10k:missing'})
   await call('review_source_document',{'document_id':source.DOCUMENT_ID,'query':cases[2]['question']})
 assert len(calls)==7 and calls[5]['isError'] and not any(c['isError'] for i,c in enumerate(calls) if i!=5)
 assert calls[3]['output']['values']['operating_cash_less_capex']=='108807'
 assert calls[4]['output']['status']=='needs_review' and calls[6]['output']['values']['operating_cash_less_capex']=='108807'
 return {'transport':'actual MCP stdio, not replay','planner':'fixed Python sequence; no LLM tool planning','calls':calls}
report={'baseline_commit':'ba689ddf7bc3a8768b546155042276e6a47739f3','execution_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'worktree_code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('quarterguard').glob('*.py')},'dataset_kind':'human-authored development/regression; original pre-fix 0/7 preserved','authorship_confirmation':'data/apple-submitted-20261112/authorship-confirmation.json','source':{'format':'original SEC HTML, no PDF','raw_sha256':source.SHA,'numeric_cells_parsed':len(parsed['cells']),'narratives_parsed':len(parsed['narratives']),'matched_user_value_cells':matched},'rows':rows,'passed':sum(x['passed'] for x in rows),'total':len(rows),'synthetic_variations':synthetic,'synthetic_passed':sum(x['passed'] for x in synthetic),'new_paid_calls':0,'new_llm_generations':0,'new_human_reviews':0,'cost_usd':0,'billing_queried':False}
(args.output/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(args.output/'mcp.json').write_text(json.dumps(asyncio.run(mcp_run()),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'development':f"{report['passed']}/7",'synthetic':f"{report['synthetic_passed']}/{len(synthetic)}",'source_cells':len(parsed['cells'])}))
if report['passed']!=7 or report['synthetic_passed']!=len(synthetic):raise SystemExit(1)
