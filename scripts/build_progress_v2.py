"""Compact UI summary derived from immutable evaluation records; no model calls."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sources={}
def read(name):
 p=ROOT/'artifacts'/name;sources[name]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
parser=read('parser-development-v2-reviewed.json');first=read('evaluation-v2-first-post-fix.json');reg=read('evaluation-v2-regression-reviewed.json');final=read('evaluation-v2-final-reviewed.json')
search=read('search-development-v2-followup.json');explanations=read('explanation-v2-final.json');mcp=read('mcp-v2-reviewed.json')
rank=[]
for label,name in [('개발 질의 36개','ranking-v2-dev-first.json'),('2023년 별도 자료 첫 평가','ranking-v2-blind-first.json'),('2022년 별도 자료 첫 평가','ranking-v2-final-first.json')]:
 r=read(name)
 for method in ['cell_hybrid','cross_encoder','cell_word']:
  rank.append({'dataset':label,'method':method,'metrics':r['same_pool_ranking']['unfiltered/'+method]['metrics']})
report={'created_at':datetime.now(timezone.utc).isoformat(),'version':'1.4.0','human_reviewed':False,'new_llm_calls':0,'participant_sessions':0,'customer_deployments':0,'personal_code_review_confirmed':False,'source_artifacts_sha256':sources,
 'development_parser':parser['raw_development_comparisons'],'document_rounds':[{'label':label,'raw_statements':r['raw_statement_summary'],'raw_cells':r['raw_cell_summary'],'raw_queries':r['stages']['raw_parsed']['query_summary'],'raw_calculations':r['stages']['raw_parsed']['calculation_summary'],'fixture_queries':r['stages']['fixture_assisted']['query_summary']} for label,r in [('2023년 자료 · 최초 별도 평가',first),('2023년 자료 · 공개 후 수정 회귀',reg),('2022년 자료 · 별도 고정 평가 재검증',final)]],
 'natural_query_regression':search['natural_summary'],'same_candidate_ranking':rank,'explanation_audit':{k:explanations[k] for k in ['recorded_count','recorded_flagged','synthetic_count','synthetic_expectations_met','semantic_accuracy','new_model_calls']},'mcp':mcp['summary'],
 'limits':['공개 작업지는 삼성전자 2024 정본 192개를 유지합니다. 새 문서의 제품 등록·다중 기업 지원은 별도입니다.','새 문서 raw 평가는 실제 PDF 추출값을 사용하되 격리된 정본 등록을 거칩니다. fixture 단계는 준비된 정답 수치를 직접 주입합니다.','현대자동차 표 형식은 원문 파싱 미지원입니다. 첫 실패와 후속 회귀를 보존했습니다.','추가 정답은 같은 작업의 AI가 작성했으며 사람·전문가 검수는 없습니다.','리랭킹은 같은 후보 집합의 실제 신경망 점수입니다. 문맥 필터는 별개이며 후보 하나인 결과는 신경망 개선 근거가 아닙니다.','사용자 참여·고객 배포·본인 코드 검토는 미수행이며 빈 양식만 준비했습니다.']}
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/progress-v2.json');args=p.parse_args();path=args.output
with path.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print('Created',path)
