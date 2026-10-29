import {esc,localTime} from './shared.js';
const names={raw_ingestion:'원본 PDF 파싱',fixture_retrieval:'정답 수치 주입 후 검색',fixture_calculation:'정답 수치 주입 후 계산',fixture_citation:'정답 수치 주입 후 출처 검사',fixture_context:'정답 수치 주입 후 문맥 검사'};
const count=c=>c?`${c.passed} / ${c.total}`:'측정 없음';
export async function mountHeldout(root) {
 root.innerHTML='<p role="status">추가 문서 평가 불러오는 중</p>';
 try {
  const response=await fetch('/api/evaluation/heldout',{signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw Error();
  const e=await response.json(),stages=e.stage_counts||{},baseline=e.baseline_stage_counts||{},failures=(e.results||[]).filter(r=>r.passed===false),natural=e.retrieval_metrics?.natural;
  root.innerHTML=`<h2>추가 문서 평가 · 실패와 수정 기록</h2><p class="scope-notice">${e.post_fix?'최초 평가 결과를 확인한 뒤 수정한 회귀 평가입니다. 현재 결과를 미공개 보류셋 성능으로 볼 수 없습니다.':'개발 자료와 다른 문서에 대한 추가 평가입니다.'} 같은 기업의 유사한 보고서 ${esc(e.documents)}건 · 정답 수치 ${esc(e.gold_facts)}개. 정답은 AI가 작성했으며 사람 검수·독립적인 사람 정답셋이 아닙니다.</p><p class="heldout-limitation warn">원본 PDF → 답변 전체 흐름: ${e.end_to_end?.status==='unsupported'?'지원하지 못함':'별도 원본 기록 확인'} · 파싱 통과 ${esc(count(stages.raw_ingestion))}개 표. ${natural?`자연어 질의 Recall@1 ${(natural.recall_at_1*100).toFixed(1)}% (${esc(natural.n)}개 질의).`:''}</p><p class="review-caption">아래 검색·계산·출처·문맥 결과는 정답 수치를 직접 주입하고 출처 등록을 평가용으로 바꾼 진단입니다. 파싱 성공이나 제품의 2025년 문서 지원을 뜻하지 않습니다.</p><div class="table-overflow"><table id="heldout-stage-table" class="evaluation-table"><thead><tr><th>단계</th><th>최초 통과 / 전체</th><th>현재 통과 / 전체</th><th>현재 실패</th></tr></thead><tbody>${Object.keys(names).filter(k=>stages[k]).map(k=>`<tr><td>${names[k]}</td><td>${esc(count(baseline[k]))}</td><td>${esc(count(stages[k]))}</td><td class="${stages[k].failed?'warn':'ok'}">${esc(stages[k].failed)}</td></tr>`).join('')}</tbody></table></div><details open class="heldout-failures"><summary>현재 실패 ${failures.length}건</summary><div class="table-overflow"><table class="evaluation-table"><thead><tr><th>사례 / 단계</th><th>질의 또는 오류</th><th>확인 기록</th></tr></thead><tbody>${failures.map(r=>`<tr><td>${esc(r.id)}<small>${esc(names[r.stage]||r.stage)}</small></td><td>${esc(r.query||r.error||r.mutation||'예상 판정과 결과 불일치')}</td><td><details><summary>상세</summary><pre>${esc(JSON.stringify(r,null,2))}</pre></details></td></tr>`).join('')}</tbody></table></div></details><p class="review-caption">평가 시각 ${esc(localTime(e.evaluated_at))} · <a href="/api/evaluation/heldout" target="_blank" rel="noopener">전체 평가 JSON ↗</a></p>${e.freeze?.known_source_anomaly?`<details class="heldout-anomaly"><summary>원문 수치 자체의 이상 관찰 · 사람 미검수</summary><p>2025년 3분기 연결 당기순이익의 인쇄 수치와 세전이익 − 세금 계산이 다릅니다. 인쇄된 금액을 임의로 수정하지 않았습니다.</p><pre>${esc(JSON.stringify(e.freeze.known_source_anomaly,null,2))}</pre></details>`:''}`;
 } catch {
  root.innerHTML='<p class="warn" role="alert">추가 문서 평가를 불러오지 못했습니다.</p><button class="secondary">평가 다시 불러오기</button>';
  root.querySelector('button').onclick=()=>mountHeldout(root);
 }
}
