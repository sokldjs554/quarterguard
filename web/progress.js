import {esc,localTime} from './shared.js';
import {renderLatestProgress} from './latest-progress.js';
const repo='https://github.com/sokldjs554/quarterguard/blob/main/';
const count=r=>`${r.passed}/${r.total}`;
export function renderHistoricalProgress(r){
  const method={cell_hybrid:'혼합 검색',cross_encoder:'신경망 cross encoder',cell_word:'단어 TF-IDF'};
  return `<h3>2026-10-31 당시 평가 · 보존본</h3><p class="scope-notice">기존 실패는 보존했습니다. 첫 별도 평가, 결과 공개 후 수정한 회귀, 다음 별도 문서 평가를 구분합니다. 이 당시 정답은 AI가 작성했고 사람 검수 전이었습니다. 이후 부분 검수는 위 최신 요약에서 확인하세요.</p><p>2024년 정본 ${r.development_parser[0].matched_gold}/${r.development_parser[0].declared_gold}개 동일 · 2025년 원문 4개 표 파싱, 정답 ${r.development_parser[1].matched_gold}/${r.development_parser[1].declared_gold}개 일치. 2025년은 이미 공개된 실패를 고친 결과입니다.</p>
  <div class="table-overflow"><table class="evaluation-table" id="v2-document-table"><thead><tr><th>평가 구분</th><th>원문 표</th><th>원문 수치·출처</th><th>원문 기반 질의</th><th>fixture 질의</th></tr></thead><tbody>${r.document_rounds.map(x=>`<tr><td>${esc(x.label)}</td><td>${count(x.raw_statements)}</td><td>${count(x.raw_cells)}</td><td>${count(x.raw_queries)}</td><td>${count(x.fixture_queries)}</td></tr>`).join('')}</tbody></table></div><p class="review-caption">원문 기반 단계도 평가용 격리 정본 등록을 사용합니다. 당시 현대자동차 표는 미지원이었습니다. 이후 파서·평가 지원과 공개 작업지 미등록 상태는 위 최신 요약에 구분했습니다.</p>
  <p>기존 자연어 5개: 정답 후보 Recall@5 ${(r.natural_query_regression.candidate_recall_at_5*100).toFixed(0)}%, top1 ${(r.natural_query_regression.candidate_top1*100).toFixed(0)}% · 조건 확인 필요 ${r.natural_query_regression.needs_clarification}개 · 검증된 답변 ${r.natural_query_regression.verified_answers}개.</p>
  <details><summary>실제 리랭킹 비교 · 동일 후보와 정답</summary><div class="table-overflow"><table class="evaluation-table"><thead><tr><th>질의 집합</th><th>방법</th><th>Recall@1</th><th>MRR@5</th><th>p50</th></tr></thead><tbody>${r.same_candidate_ranking.map(x=>`<tr><td>${esc(x.dataset)}</td><td>${esc(method[x.method])}</td><td>${(x.metrics.recall_at_1*100).toFixed(1)}%</td><td>${x.metrics.mrr_at_5.toFixed(3)}</td><td>${x.metrics.latency_p50_ms.toFixed(2)} ms</td></tr>`).join('')}</tbody></table></div><p>리랭커는 개발 집합에서 악화됐고, 마지막 작은 집합에서는 혼합 검색보다 한 건 좋아졌으나 단어 검색보다 낮았습니다. 기본 검색에 배포하지 않았습니다. 이 표는 fixture 수치 후보 실험입니다.</p></details>
  <p>기존 GPT 응답 ${r.explanation_audit.recorded_count}개 재검사: ${r.explanation_audit.recorded_flagged}개 사람 검토 표시(오류 확정 아님). 합성 반례 ${r.explanation_audit.synthetic_expectations_met}/${r.explanation_audit.synthetic_count}개 기대 판정 일치 · 이 당시 추가 LLM 호출 ${r.new_llm_calls}회(프로젝트 전체 누계 아님). 문장 전체 정확도를 인증하지 않습니다.</p><p>실제 MCP 흐름 ${count(r.mcp.actual_stdio_checks)} 통과 · 실패 입력·시간 초과 기록을 별도로 확인했습니다. 규칙 기반 실행이며 자율 LLM 계획이 아닙니다.</p>
  <details><summary>당시 한계·미수행 항목과 준비 자료</summary><p>아래는 2026-10-31 당시 기록이며 현재 상태가 아닙니다. 후속 검수·구현은 위 요약을 확인하세요.</p><ul>${r.limits.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p><a href="${repo}docs/validation-kit/README.md" target="_blank" rel="noopener">사용자 검증 시나리오·빈 양식 ↗</a> · <a href="${repo}docs/code-review-kit/README.md" target="_blank" rel="noopener">직접 코드 검토 질문 ↗</a></p></details>
  <p class="review-caption">집계 ${esc(localTime(r.created_at))} · <a href="${repo}docs/completion-v1.4.md" target="_blank" rel="noopener">당시 보고·실패·재현 방법 ↗</a> · <a href="/api/evaluation/current/progress" target="_blank" rel="noopener">원본 집계 JSON ↗</a></p>`;
}

export async function mountProgress(root){
 if(!root)return;
 root.innerHTML='<p role="status">최신 요약과 과거 평가 확인 중</p>';
 const read=async path=>{const r=await fetch(path,{signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error();return r.json();};
 const [latest,history]=await Promise.allSettled([read('/api/evaluation/latest'),read('/api/evaluation/current/progress')]);
 let current,previous,failed=false;
 try{if(latest.status!=='fulfilled')throw Error();current=renderLatestProgress(latest.value);}
 catch{failed=true;current='<section id="latest-evidence-error"><h2>최신 근거 요약 확인 불가</h2><p class="warn" role="alert">최신 자료를 불러오지 못했습니다. 아래 과거 기록을 현재 결과로 해석하지 마세요.</p></section>';}
 try{if(history.status!=='fulfilled')throw Error();previous=renderHistoricalProgress(history.value);}
 catch{failed=true;previous='<p class="warn" role="alert">과거 평가 기록을 불러오지 못했습니다.</p>';}
 root.innerHTML=current+'<details id="historical-evaluation"><summary>2026-10-31 과거 평가 펼치기 · 첫 실패와 당시 한계 보존</summary>'+previous+'</details>';
 if(failed){
  const button=document.createElement('button');button.className='secondary';button.textContent='평가 자료 다시 불러오기';button.onclick=()=>mountProgress(root);root.append(button);
 }
}
