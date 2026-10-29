import asyncio,json,os,subprocess
from functools import lru_cache
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .store import ROOT,load_facts
from .search import SearchIndex
from .orchestrator import cases,run_case
app=FastAPI(title='QuarterGuard',version='1.0.0')
slots=asyncio.Semaphore(1)  # Bound subprocess CPU/RSS on the free 0.1 CPU / 512 MB instance.
@lru_cache(maxsize=1)
def index():return SearchIndex(load_facts())
def artifact(name):
 p=ROOT/'artifacts'/name
 if not p.exists():raise HTTPException(503,'ARTIFACT_UNAVAILABLE')
 return json.loads(p.read_text())
def revision():
 if os.getenv('RENDER_GIT_COMMIT'):return os.environ['RENDER_GIT_COMMIT']
 try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=2).strip()
 except Exception:return 'local-unversioned'
@app.get('/health')
def health():return {'status':'ok','facts':len(load_facts()),'commit':revision()}
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
 return {'hits':index().search(q,5),'configuration':'hybrid_meta'}
@app.get('/api/connectors/dart')
def dart_status():return {'status':'configured_not_verified' if os.getenv('DART_API_KEY') else 'not_configured',
 'message':'DART API 실호출 미검증 · 공개 데모는 준비된 IR 보고서 근거 사용'}
@app.get('/')
def home():return FileResponse(ROOT/'web/index.html')
app.mount('/assets',StaticFiles(directory=ROOT/'web'),name='assets')
