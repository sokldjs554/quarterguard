"""Offline recorded-output re-audit plus labeled synthetic development challenges."""
import copy,hashlib,json
from datetime import datetime,timezone
from .store import ROOT
from .explanation_audit import audit_explanation

CHALLENGES=[
 ('wrong-percent',0,'2024년 3분기 연결 매출은 9.9999% 증가했습니다.','PERCENT_MISMATCH'),
 ('wrong-amount',0,'2024년 3분기 연결 매출은 79,098,732 백만 원입니다.','AMOUNT_MISMATCH'),
 ('wrong-period-amount',0,'2024년 3분기 연결 매출은 74,068,302 백만 원입니다.','AMOUNT_CONTEXT_MISMATCH'),
 ('wrong-period-spaced',0,'2024년 3 분기 연결 매출은 74,068,302 백만 원입니다.','AMOUNT_CONTEXT_MISMATCH'),
 ('wrong-period-english',0,'2024년 Q3 연결 매출은 74,068,302 백만 원입니다.','AMOUNT_CONTEXT_MISMATCH'),
 ('wrong-months-spaced',1,'3 개월 연결 매출은 225082634 백만 원입니다.','AMOUNT_CONTEXT_MISMATCH'),
 ('wrong-scope',0,'별도 매출 증가율은 6.7916%입니다.','SCOPE_CLAIM_CONFLICT'),
 ('wrong-year',0,'2026년 연결 매출 증가율입니다.','YEAR_CLAIM_CONFLICT'),
 ('wrong-months',0,'12개월 누적 매출입니다.','MONTHS_CLAIM_CONFLICT'),
 ('wrong-unit',0,'금액 단위는 천 원입니다.','UNIT_CLAIM_CONFLICT'),
 ('wrong-currency',0,'금액은 USD 단위입니다.','CURRENCY_CLAIM_CONFLICT'),
 ('unsupported-amount',2,'2025년 매출은 100 백만 원입니다.','UNSUPPORTED_NUMERIC_CLAIM'),
 ('reject-overridden',1,'검증 통과, 문제가 없습니다.','REJECTION_OVERRIDDEN_IN_PROSE'),
 ('invented-url',0,'출처 https://example.org/fake.pdf#page=4 입니다.','INLINE_CITATION_MISMATCH'),
 ('unbound-number',0,'매출은 79098731입니다.','UNBOUND_NUMBER_REQUIRES_REVIEW'),
 ('scope-negation',0,'별도가 아닌 연결 매출입니다.','NEGATION_REQUIRES_REVIEW'),
 ('correct-amount',0,'2024년 3분기 연결 매출은 79,098,731 백만 원입니다.',None),
 ('equivalent-scale',0,'2024년 3분기 연결 매출은 79.098731조원입니다.',None),
 ('rounded-percent',0,'2024년 3분기 연결 매출은 6.79% 증가했습니다.',None),
]
def evaluate():
 path=ROOT/'artifacts/live-openai.json';old=json.loads(path.read_text());rows=old['openai']['records'];recorded=[];synthetic=[]
 for row in rows:
  result=audit_explanation(row['generated'],row['mcp_run']['result'],context_years=['2025'] if row['case_id']=='no-evidence' else [])
  recorded.append({'case_id':row['case_id'],'generated':row['generated'],'audit':result})
 for id,index,text,expected in CHALLENGES:
  row=rows[index];a=copy.deepcopy(row['generated']);a['explanation_ko']=text
  result=audit_explanation(a,row['mcp_run']['result'],context_years=['2025'] if index==2 else [])
  passed=expected in result['issues'] if expected else not result['issues']
  synthetic.append({'id':id,'source_case':row['case_id'],'origin':'AI-authored synthetic development challenge; NOT a new model output','generated':a,'expected_issue':expected,'audit':result,'matches_authored_expectation':passed})
 # Citation mutation explicitly retains old tool evidence; references cannot be invented.
 a=copy.deepcopy(rows[0]['generated']);a['evidence_ids']=['invented-document-cell']
 result=audit_explanation(a,rows[0]['mcp_run']['result'])
 synthetic.append({'id':'invented-structured-citation','origin':'AI-authored synthetic development challenge','generated':a,'expected_issue':'STRUCTURED_MISMATCH','audit':result,'matches_authored_expectation':'STRUCTURED_MISMATCH' in result['issues']})
 mixed=json.loads((ROOT/'artifacts/prepared.json').read_text())['scope-trap']['result']
 other=next(f for f in mixed['evidence'] if f['scope']=='OFS')
 a={'status':mixed['status'],'value':None,'issues':mixed['issues'],'evidence_ids':[f['id'] for f in mixed['evidence']],'explanation_ko':f"consolidated 매출은 {other['value']} 백만 원입니다."}
 result=audit_explanation(a,mixed)
 synthetic.append({'id':'mixed-english-scope-amount','origin':'AI-authored synthetic development challenge on preserved scope-trap tool result','generated':a,'expected_issue':'AMOUNT_CONTEXT_MISMATCH','audit':result,'matches_authored_expectation':'AMOUNT_CONTEXT_MISMATCH' in result['issues']})
 return {'created_at':datetime.now(timezone.utc).isoformat(),'source_artifact':'artifacts/live-openai.json','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'validator_sha256':hashlib.sha256((ROOT/'quarterguard/explanation_audit.py').read_bytes()).hexdigest(),'original_call_count':4,'new_model_calls':0,'new_provider_api_cost_usd':'0','billed_cost_usd':None,'cost_note':'No new model call; historical billed amount was not queried. CPU/storage excluded.', 'human_reviewed':False,'llm_as_judge':False,'recorded_count':len(recorded),'recorded_flagged':sum(bool(r['audit']['issues']) for r in recorded),'recorded':recorded,'synthetic_count':len(synthetic),'synthetic_expectations_met':sum(r['matches_authored_expectation'] for r in synthetic),'synthetic':synthetic,'semantic_accuracy':None,'limitations':['No_detected_rule_violation is not verified prose accuracy.','Synthetic expectations are development tests, not heldout LLM quality.','Checks cover supported explicit expressions; Korean/English prose negation and complex attribution still need a human.','No new generated explanation has been sampled under these checks.']}
if __name__=='__main__':
 import argparse
 from pathlib import Path
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'artifacts/explanation-v2.json');args=parser.parse_args()
 report=evaluate();path=args.output
 previous=ROOT/'artifacts/explanation-v2.json'
 if previous.exists():report['preserved_prior_evaluation']={'path':str(previous.relative_to(ROOT)),'sha256':hashlib.sha256(previous.read_bytes()).hexdigest()}
 with path.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:report[k] for k in ['recorded_count','recorded_flagged','synthetic_count','synthetic_expectations_met','new_model_calls']},ensure_ascii=False))
