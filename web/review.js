import {$, esc, labels, money, issues, api, errorText, traceHTML, localTime} from './shared.js';
export function mountReview(evaluation, cases) {
 const e=evaluation,pct=x=>(x*100).toFixed(1)+'%',names={fixed_word:'고정 180자 · 단어 TF-IDF',cell_word:'문맥 셀 · 단어 TF-IDF',cell_char:'문맥 셀 · 문자 TF-IDF',hybrid_meta:'문맥 셀 · 혼합 + 문맥 필터'};
 $('#evaluation-content').innerHTML=`<section class="review-section"><h2>검색 구성 비교</h2><div class="table-overflow"><table class="evaluation-table" id="retrieval-table"><thead><tr><th>청킹 · 검색 구성</th><th>Recall@1</th><th>Recall@3</th><th>MRR@5</th><th>검색 p50</th></tr></thead><tbody>${Object.entries(e.retrieval).map(([key,r])=>`<tr class="${key==='hybrid_meta'?'chosen':''}"><td>${esc(names[key]||key)} ${key==='hybrid_meta'?'· 기본 구성':''}</td><td class="num">${pct(r.metrics.recall_at_1)}</td><td class="num">${pct(r.metrics.recall_at_3)}</td><td class="num">${r.metrics.mrr_at_5.toFixed(3)}</td><td class="num">${r.metrics.latency_p50_ms.toFixed(2)} ms</td></tr>`).join('')}</tbody></table></div><p class="review-caption">정상 질의에서는 문맥 셀 단어 검색도 Recall@1 100%입니다. 문맥 필터의 가치는 미지원·모순 조건에서 잘못된 후보를 차단하는 데 있습니다. 두 ONNX 모델은 실제 실행했으며, 한국어 제어 어휘를 영어로 치환했습니다. 신경망 리랭커 실험은 없습니다.</p></section>
 <section class="review-section"><h2>사례별 검증 결과</h2><div class="table-overflow"><table class="evaluation-table" id="case-check-table"><thead><tr><th>업무 사례</th><th>전체</th><th>판정</th><th>수치</th><th>거부 사유</th><th>출처</th><th>도구 흐름</th></tr></thead><tbody>${e.workflow.checks.map(c=>`<tr><td>${esc(cases.find(x=>x.id===c.case_id)?.title||c.case_id)}</td>${[c.case_correct,c.status_correct,c.value_correct,c.issue_correct,c.source_valid,c.workflow_success].map(x=>`<td class="${x===false?'warn':x===null?'na':'ok'}">${x===null?'해당 없음':x?'일치':'실패'}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="review-caption">기존 8개 업무 사례의 저장된 평가입니다. 새 작업지의 현재 실행 결과와 구분합니다. 측정 시각 ${esc(localTime(e.created_at))} · 실제 MCP p50 ${(e.workflow.latency_p50_ms/1000).toFixed(2)}초.<br><a href="https://github.com/sokldjs554/quarterguard/blob/main/artifacts/evaluation.json" target="_blank" rel="noopener">평가 원본·실행 환경 ↗</a></p></section>`;
 $('#case-select').innerHTML=cases.map(c=>`<option value="${esc(c.id)}">${esc(c.title)}</option>`).join('');
 $('#prepared-btn').disabled=$('#case-run-btn').disabled=$('#case-select').disabled=false;
 let ticket=0;
 async function run(live) {
  const id=$('#case-select').value,token=++ticket,box=$('#case-output');
  $('#prepared-btn').disabled=$('#case-run-btn').disabled=$('#case-select').disabled=true;
  box.innerHTML='<p class="busy-pulse" role="status">실행 기록 확인 중</p>';
  try {
   const r=await api(live?`/api/run/${id}`:`/api/prepared/${id}`,live?{method:'POST'}:{});
   if(token!==ticket)return;
   const v=r.result,value=v.growth_pct??v.derived_value;
   box.innerHTML=`<div class="case-result-head"><strong class="${v.status==='verified'?'ok':'warn'}">${v.status==='verified'?'검증 통과':'확인 필요'}${value!==undefined&&value!==null?' · '+esc(v.growth_pct!==undefined?value+'%':money(value)):''}</strong><span>${r.execution_mode==='live_mcp'?'현재 MCP 실제 실행':'저장된 MCP 기록 재생'} · ${(r.latency_ms/1000).toFixed(2)}초</span></div><div class="case-result-body">${v.issues.map(x=>`<p class="warn">${esc(issues[x]?.[0]||x)} · ${esc(issues[x]?.[1]||'')}</p>`).join('')}<p>${v.evidence.length}개 근거 · ${r.trace.length}회 도구 호출 · 생성형 모델 0회</p>${v.evidence.map(f=>`<p>${esc(labels[f.metric])} · ${money(f)} · ${f.start} — ${f.end} · <a href="${esc(f.source_url)}#page=${f.page}" target="_blank" rel="noopener">PDF p.${f.page}</a></p>`).join('')}<details><summary>실행 단계와 원본</summary>${traceHTML(r.trace)}</details></div>`;
  } catch(e) {box.innerHTML=`<p class="error-message" role="alert">${esc(errorText(e))}</p>`;}
  finally {if(token===ticket)$('#prepared-btn').disabled=$('#case-run-btn').disabled=$('#case-select').disabled=false;}
 }
 $('#prepared-btn').onclick=()=>run(false);$('#case-run-btn').onclick=()=>run(true);
 $('#case-select').onchange=()=>{$('#case-output').textContent='사례 선택 변경 · 저장 기록 또는 현재 재실행으로 확인';};
}
