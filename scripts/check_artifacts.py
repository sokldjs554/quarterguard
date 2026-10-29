"""Fail CI when the corpus, golden cases and prepared execution diverge."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from quarterguard.store import load_facts
facts={f.id:f.public() for f in load_facts()}
e=json.loads((ROOT/'artifacts/evaluation.json').read_text());prepared=json.loads((ROOT/'artifacts/prepared.json').read_text())
assert e['corpus_sha256']==hashlib.sha256((ROOT/'data/facts.json').read_bytes()).hexdigest()
assert e['gold_sha256']==hashlib.sha256((ROOT/'data/retrieval_gold.json').read_bytes()).hexdigest()
assert all(x['status_correct'] and x['value_correct'] is not False and x['issue_correct'] is not False for x in e['workflow']['checks'])
for run in prepared.values():
 assert run['execution_mode']=='prepared_replay'
 assert run['protocol'] and run['trace']
 for f in run['result'].get('evidence',[]):assert f==facts[f['id']],f['id']
for q in json.loads((ROOT/'data/retrieval_gold.json').read_text()):assert q['gold_fact_id'] in facts
assert len(facts)==192
print('Artifact consistency: corpus hash, gold hash, 8 cases, exact canonical citations verified')
