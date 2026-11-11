import asyncio,json,os,subprocess
from functools import lru_cache
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .store import ROOT,load_facts
from .orchestrator import cases,run_case
from .worksheet import WorksheetRequest,preview,run_worksheet
app=FastAPI(title='QuarterGuard',version='1.4.0')
slots=asyncio.Semaphore(1)  # Bound subprocess CPU/RSS on the free 0.1 CPU / 512 MB instance.
@lru_cache(maxsize=1)
def index():
 # Keep the scientific retrieval stack off the homepage/health startup path.
 from .search import SearchIndex
 return SearchIndex(load_facts())
def artifact(name):
 p=ROOT/'artifacts'/name
 if not p.exists():raise HTTPException(503,'ARTIFACT_UNAVAILABLE')
 return json.loads(p.read_text())
def revision():
 if os.getenv('RENDER_GIT_COMMIT'):return os.environ['RENDER_GIT_COMMIT']
 try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=2).strip()
 except Exception:return 'local-unversioned'
@app.get('/health')
def health():return {'status':'ok','facts':len(load_facts()),'commit':revision(),'version':app.version}
@app.get('/api/cases')
def get_cases():return [{k:v for k,v in c.items() if not k.startswith('expected')} for c in cases()]
@app.get('/api/sources')
def sources():return json.loads((ROOT/'data/sources.json').read_text())
@app.get('/api/facts')
def facts():return [f.public() for f in load_facts()]
@app.get('/api/evaluation')
def evaluation():return artifact('evaluation.json')
@app.get('/api/prepared/{case_id}')
def prepared(case_id:str):
 data=artifact('prepared.json')
 if case_id not in data:raise HTTPException(404,'UNKNOWN_CASE')
 return data[case_id]
@app.post('/api/run/{case_id}')
async def run(case_id:str):
 if case_id not in {c['id'] for c in cases()}:raise HTTPException(404,'UNKNOWN_CASE')
 try:await asyncio.wait_for(slots.acquire(),timeout=.1)
 except TimeoutError:raise HTTPException(429,'BUSY_RETRY')
 try:return await run_case(case_id)
 finally:slots.release()
@app.get('/api/search')
def search(q:str=Query('',max_length=500)):
 return index().search_with_diagnostics(q,5)|{'configuration':'hybrid_meta'}
def source_request(operation):
 try:return operation()
 except ValueError as exc:
  if str(exc) in {'UNKNOWN_SOURCE_DOCUMENT','UNKNOWN_SOURCE_CELL'}:raise HTTPException(404,str(exc)) from None
  raise HTTPException(503,'SOURCE_EVIDENCE_UNAVAILABLE') from None
 except (OSError,KeyError,TypeError):raise HTTPException(503,'SOURCE_EVIDENCE_UNAVAILABLE') from None
@app.get('/api/source-documents')
def source_documents():
 from .source_calculations import options
 return source_request(lambda:[options()['document']])
@app.get('/api/source-search')
def source_search(document_id:str=Query(...,max_length=80),q:str=Query('',max_length=500)):
 from .source_evidence import search_source
 return source_request(lambda:search_source(document_id,q))
@app.get('/api/source-cells/{cell_id}')
def source_cell(cell_id:str):
 from .source_evidence import get_cell
 return source_request(lambda:get_cell(cell_id))
class SourceCalculationRequest(BaseModel):
 model_config=ConfigDict(extra='forbid')
 current_id:str=Field(min_length=1,max_length=160,strict=True)
 base_id:str=Field(min_length=1,max_length=160,strict=True)
 mode:Literal['annual_yoy','balance_yoy','product_share','inventory_months']
@app.get('/api/source-calculations/options')
def source_calculation_options():
 from .source_calculations import options
 return source_request(options)
@app.post('/api/source-calculations')
def source_calculation(request:SourceCalculationRequest):
 from .source_calculations import calculate_source_pair
 return source_request(lambda:calculate_source_pair(request.current_id,request.base_id,request.mode))
@app.post('/api/worksheet')
def worksheet(request:WorksheetRequest):return preview(request)
@app.post('/api/worksheet/run')
async def worksheet_run(request:WorksheetRequest):
 try:await asyncio.wait_for(slots.acquire(),timeout=.1)
 except TimeoutError:raise HTTPException(429,'BUSY_RETRY')
 try:return await run_worksheet(request)
 finally:slots.release()
@app.get('/api/providers')
def provider_status():
 from .public_providers import status
 return status()
@app.get('/api/connectors/dart')
def dart_status():return provider_status()['dart']
@app.post('/api/providers/{provider}/{target}')
async def call_provider(provider:str,target:str):
 from .public_providers import execute
 from .provider_controls import Blocked
 try:await asyncio.wait_for(slots.acquire(),timeout=.1)
 except TimeoutError:raise HTTPException(429,'BUSY_RETRY')
 try:
  return await asyncio.to_thread(execute,provider,target)
 except Blocked as exc:
  raise HTTPException(404 if str(exc)=='UNKNOWN_TARGET' else 429,str(exc))
 except Exception:
  raise HTTPException(503,'PROVIDER_SERVICE_UNAVAILABLE') from None
 finally:slots.release()
@app.get('/api/evaluation/heldout')
def heldout_evaluation():return artifact('heldout-evaluation.json')
@app.get('/api/evaluation/latest')
def latest_evaluation():
 from .latest_progress import load_latest_progress
 try:return {'summary':load_latest_progress(),'runtime_commit':revision()}
 except (OSError,ValueError,KeyError,TypeError):
  raise HTTPException(503,'LATEST_EVIDENCE_UNAVAILABLE') from None
@app.get('/api/evaluation/current/{report}')
def current_evaluation(report:str):
 names={'progress':'progress-v2-final.json','parser':'parser-development-v2-reviewed.json','search':'search-development-v2-followup.json','documents':'evaluation-v2-final-summary.json','ranking':'ranking-v2-disclosed-followup.json','explanations':'explanation-v2-final.json','mcp':'mcp-v2-reviewed.json'}
 if report not in names:raise HTTPException(404,'UNKNOWN_REPORT')
 return artifact(names[report])
@app.get('/')
def home():return FileResponse(ROOT/'web/index.html')
app.mount('/assets',StaticFiles(directory=ROOT/'web'),name='assets')
