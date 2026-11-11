import json,hashlib,sys,argparse,subprocess
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path.cwd()))
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.human_holdout import retrieve
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=args.output;root.mkdir(parents=True,exist_ok=False)
freeze=json.loads(Path('artifacts/apple-first-20261112/freeze.json').read_text())
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in freeze['code_and_existing_corpus_hashes'].items())
with (root/'first-attempt-reserved.json').open('x') as f:json.dump({'at_utc':datetime.now(timezone.utc).isoformat(),'freeze_sha256':hashlib.sha256(Path('artifacts/apple-first-20261112/freeze.json').read_bytes()).hexdigest()},f)
rows=[]
with TestClient(app) as client:
 catalog=client.get('/api/source-documents').json()
 for q in freeze['queries']:
  selected=client.get('/api/source-search',params={'document_id':'apple-2024-10k','q':q['q']})
  # Verify actual endpoint parameter name first below; q is endpoint's query parameter.
  general=client.get('/api/search',params={'q':q['q']})
  rows.append({'id':q['id'],'unaltered_question':q['q'],'selected_document_http':selected.status_code,'selected_document_response':selected.json(),
   'intake_adapter_result':retrieve(q['q'],'apple-2024-10k'),'current_search_http':general.status_code,'current_search_result':general.json()})
  (root/'first-results.json').write_text(json.dumps({'code_commit':freeze['code_commit'],'catalog':catalog,'rows':rows,'new_llm_calls':0,'raw_pdf_parsed':False,'fixture_answers_used_as_runtime_input':False,'human_authorship_confirmed':False,'first_attempt':False,'execution_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'kind':'Explicit reproduction; historical first attempt is in artifacts/apple-first-20261112'},ensure_ascii=False,indent=2))
print([(r['id'],r['selected_document_http'],len(r['current_search_result'].get('hits',[]))) for r in rows])
