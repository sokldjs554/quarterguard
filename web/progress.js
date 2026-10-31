import {esc,localTime} from './shared.js';
const repo='https://github.com/sokldjs554/quarterguard/blob/main/';
const count=r=>`${r.passed}/${r.total}`;
export async function mountProgress(root){
 if(!root)return;
 root.innerHTML='<p role="status">현재 보완 결과 확인 중</p>';
 try{
  const response=await fetch('/api/evaluation/current/progress',{signal:AbortSignal.timeout(15000)});if(!response.ok)throw Error();const r=await response.json();
  const method={cell_hybrid:'혼합 검색',cross_encoder:'신경망 cross encoder',cell_word:'단어 TF-IDF'};
  root.innerHTML=`<h2>v1.4 · 원문 파싱과 검색 보완</h2><p class="scope-notice">기존 실패는 보존했습니다. 첫 별도 평가, 결과 공개 후 수정한 회귀, 다음 별도 문서 평가를 구분합니다. AI 작성 정답 · 사람 검수 없음.</p><p>2024년 정본 ${r.development_parser[0].matched_gold}/${r.development_parser[0].declared_gold}개 동일 · 2025년 원문 4개 표 파싱, 정답 ${r.development_parser[1].matched_gold}/${r.development_parser[1].declared_gold}개 일치. 2025년은 이미 공개된 실패를 고친 결과입니다.</p>
  <div class="table-overflow"><table class="evaluation-table" id="v2-document-table"><thead><tr><th>평가 구분</th><th>원문 표</th><th>원문 수치·출처</th><th>원문 기반 질의</th><th>fixture 질의</th></tr></thead><tbody>${r.document_rounds.map(x=>`<tr><td>${esc(x.label)}</td><td>${count(x.raw_statements)}</td><td>${count(x.raw_cells)}</td><td>${count(x.raw_queries)}</td><td>${count(x.fixture_queries)}</td></tr>`).join('')}</tbody></table></div><p class="review-caption">원문 기반 단계도 평가용 격리 정본 등록을 사용합니다. 현대자동차 원문 표는 미지원이며, 새 문서를 현재 작업지에서 지원한다는 뜻이 아닙니다.</p>
  <p>기존 자연어 5개: 정답 후보 Recall@5 ${(r.natural_query_regression.candidate_recall_at_5*100).toFixed(0)}%, top1 ${(r.natural_query_regression.candidate_top1*100).toFixed(0)}% · 조건 확인 필요 ${r.natural_query_regression.needs_clarification}개 · 검증된 답변 ${r.natural_query_regression.verified_answers}개.</p>
  <details><summary>실제 리랭킹 비교 · 동일 후보와 정답</summary><div class="table-overflow"><table class="evaluation-table"><thead><tr><th>질의 집합</th><th>방법</th><th>Recall@1</th><th>MRR@5</th><th>p50</th></tr></thead><tbody>${r.same_candidate_ranking.map(x=>`<tr><td>${esc(x.dataset)}</td><td>${esc(method[x.method])}</td><td>${(x.metrics.recall_at_1*100).toFixed(1)}%</td><td>${x.metrics.mrr_at_5.toFixed(3)}</td><td>${x.metrics.latency_p50_ms.toFixed(2)} ms</td></tr>`).join('')}</tbody></table></div><p>리랭커는 개발 집합에서 악화됐고, 마지막 작은 집합에서는 혼합 검색보다 한 건 좋아졌으나 단어 검색보다 낮았습니다. 기본 검색에 배포하지 않았습니다. 이 표는 fixture 수치 후보 실험입니다.</p></details>
  <p>기존 GPT 응답 ${r.explanation_audit.recorded_count}개 재검사: ${r.explanation_audit.recorded_flagged}개 사람 검토 표시(오류 확정 아님). 합성 반례 ${r.explanation_audit.synthetic_expectations_met}/${r.explanation_audit.synthetic_count}개 기대 판정 일치 · 새 LLM 호출 ${r.new_llm_calls}회. 문장 전체 정확도를 인증하지 않습니다.</p><p>실제 MCP 흐름 ${count(r.mcp.actual_stdio_checks)} 통과 · 실패 입력·시간 초과 기록을 별도로 확인했습니다. 규칙 기반 실행이며 자율 LLM 계획이 아닙니다.</p>
  <details><summary>남은 한계와 직접 검토 자료</summary><ul>${r.limits.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p><a href="${repo}docs/validation-kit/README.md" target="_blank" rel="noopener">사용자 검증 시나리오·빈 양식 ↗</a> · <a href="${repo}docs/code-review-kit/README.md" target="_blank" rel="noopener">직접 코드 검토 질문 ↗</a></p></details>
  <p class="review-caption">집계 ${esc(localTime(r.created_at))} · <a href="${repo}docs/completion-v1.4.md" target="_blank" rel="noopener">보완 보고·실패·재현 방법 ↗</a> · <a href="/api/evaluation/current/progress" target="_blank" rel="noopener">원본 집계 JSON ↗</a></p>`;
 }catch{root.innerHTML='<p class="warn" role="alert">현재 보완 결과를 불러오지 못했습니다.</p><button class="secondary">다시 불러오기</button>';root.querySelector('button').onclick=()=>mountProgress(root);}
}
