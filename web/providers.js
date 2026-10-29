import {esc, localTime} from './shared.js';

const targets={
 dart:{'s24q3-CFS':'2024년 3분기 · 연결','s24q3-OFS':'2024년 3분기 · 별도','s24q2-CFS':'2024년 반기 · 연결','s24q2-OFS':'2024년 반기 · 별도'},
 openai:{'qoq-revenue':'분기 매출 증감','ytd-trap':'누적·분기 혼동','no-evidence':'근거 부재','reconcile-revenue':'누적 차감 교차검증'}
};
const reasons={KEY_NOT_CONFIGURED:'API 키 미설정',PAID_APPROVAL_REQUIRED:'유료 호출 승인 미설정',DURABLE_LEDGER_REQUIRED:'재시작 후에도 유지되는 사용량 기록 필요',OPERATOR_DISABLED:'운영자가 호출 중지',LEDGER_UNAVAILABLE:'사용량 기록 연결 불가',QUOTA_EXHAUSTED:'공유 호출 한도 소진',COOLDOWN:'호출 간 대기 시간 미경과',BUSY_RETRY:'다른 검증 실행 중',MCP_FAILED:'선행 MCP 검증 실패',INPUT_TOO_LARGE:'입력 크기 제한 초과',UNKNOWN_TARGET:'지원하지 않는 대상',PROVIDER_SERVICE_UNAVAILABLE:'외부 검증 서비스 연결 불가',PROVIDER_REQUEST_FAILED_OR_VALIDATION_REJECTED:'외부 요청 실패 또는 응답 검증 불일치'};
const reason=x=>reasons[x]||String(x);
const time=x=>x&&Number.isFinite(Date.parse(x))?localTime(x):'기록 없음';
const number=x=>Number.isFinite(x)?String(x):'확인 불가';
function sourceLink(url) {
 try {const u=new URL(url);if(u.protocol==='https:'&&u.hostname==='dart.fss.or.kr')return `<a href="${esc(u.href)}" target="_blank" rel="noopener">DART 원문 ↗</a>`;} catch {}
 return '출처 링크 없음';
}
function details(provider,r) {
 if(provider==='dart'&&Array.isArray(r.checks))return `<div class="table-overflow"><table class="evaluation-table"><thead><tr><th>근거 ID · 필드</th><th>IR 금액 (원)</th><th>DART 금액 (원)</th><th>대조</th><th>원문</th></tr></thead><tbody>${r.checks.map(c=>`<tr><td>${esc(c.fact_id)}<small>${esc(c.source_field)}</small></td><td class="num">${esc(c.expected_krw)}</td><td class="num">${esc(c.dart_krw??'없음')}</td><td class="${c.passed?'ok':'warn'}">${c.passed?'일치':'불일치'}</td><td>${sourceLink(c.dart_source)}</td></tr>`).join('')}</tbody></table></div><p class="review-caption">매출·영업이익의 단독 분기/누적 금액을 원 단위로 대조합니다. 연결·별도 범위는 요청한 fs_div 기준입니다.</p>`;
 if(provider==='openai'&&r.generated) {
  const g=r.generated;
  return `<p class="generated-explanation">${esc(g.explanation_ko)}</p><p class="scope-notice">AI 생성 설명 · 문장 의미와 한국어 표현은 사람이 검수하지 않았습니다. 구조화된 수치·판정·근거 ID 검사와 구분하세요.</p><dl class="provider-fields"><dt>판정 / 값</dt><dd>${esc(g.status)} / ${esc(g.value??'없음')}</dd><dt>거부 사유</dt><dd>${esc((g.issues||[]).join(' · ')||'없음')}</dd><dt>근거 ID</dt><dd>${(g.evidence_ids||[]).map(esc).join('<br>')||'없음'}</dd><dt>모델 / 사용량</dt><dd>${esc(r.model)} · 입력 ${esc(number(r.input_tokens))} / 출력 ${esc(number(r.output_tokens))} 토큰</dd></dl><p class="review-caption">규칙 기반 MCP 흐름 뒤에 설명만 생성합니다. LLM이 검증 판정이나 근거를 선택하는 에이전트는 아닙니다.</p>`;
 }
 return '';
}
export function mountProviders(root) {
 let state=null,busy=false,refreshing=false;
 const counts={live:0,cached:0,failed:0,blocked:0,unknown:0};
 root.innerHTML=`<div class="provider-section-heading"><h2>외부 API 직접 확인</h2><button class="secondary" id="provider-refresh">연결 상태 새로고침</button></div><p class="review-caption">아래 버튼을 눌러야 외부 요청을 보냅니다. 작업지 계산·MCP 재검증과 별도이며, 같은 요청의 성공 응답은 최대 24시간 재사용합니다. 사용량 한도는 모든 방문자가 공유합니다.</p><p id="provider-session" class="review-caption" role="status"></p><div class="provider-grid">${['dart','openai'].map(p=>`<section class="provider-card" data-provider="${p}" aria-labelledby="${p}-title"><h3 id="${p}-title">${p==='dart'?'DART 공시 금액 대조':'OpenAI 설명 생성'}</h3><div id="${p}-availability" class="provider-availability" role="status">연결 상태 확인 중</div><label for="${p}-target">검증 대상<select id="${p}-target" disabled>${Object.entries(targets[p]).map(([id,label])=>`<option value="${id}">${label}</option>`).join('')}</select></label><button id="${p}-request" class="secondary" disabled>${p==='dart'?'DART 대조 요청':'OpenAI 설명 요청'}</button><p class="review-caption">${p==='dart'?'공개 공시 4개 고정 대상 · 별도 데이터 가져오기':'4개 고정 사례 · 유료 API · 출력 최대 700토큰 · 실제 청구액은 조회하지 않음'}</p><div id="${p}-result" class="provider-result" aria-live="polite">아직 요청하지 않았습니다.</div></section>`).join('')}</div>`;
 const el=id=>root.querySelector('#'+id);
 function controls() {
  for(const p of ['dart','openai']) {
   const disabled=busy||refreshing||state?.[p]?.enabled!==true;
   el(p+'-request').disabled=disabled;el(p+'-target').disabled=disabled;
  }
  el('provider-refresh').disabled=busy||refreshing;
  el('provider-session').textContent=`이 화면의 요청 기록 · 외부 호출 ${counts.live}회 · 캐시 응답 ${counts.cached}회 · 실패 ${counts.failed}건 · 차단 ${counts.blocked}건 · 호출 여부 미확인 ${counts.unknown}건`;
 }
 async function refresh() {
  refreshing=true;controls();
  try {
   const response=await fetch('/api/providers',{signal:AbortSignal.timeout(15000)});
   if(!response.ok)throw Error();
   state=await response.json();
   for(const p of ['dart','openai']) {
    const s=state[p];if(!s||typeof s.enabled!=='boolean')throw Error();
    const l=s.limits||{},u=s.usage||{};
    el(p+'-availability').innerHTML=`<strong class="${s.enabled?'ok':'warn'}">${s.enabled?'요청 가능':'현재 사용 불가'}</strong>${s.enabled?'':`<p>${(s.blocked_reasons||[]).map(x=>esc(reason(x))).join(' · ')||'활성화 조건 미확인'}</p>`}<p class="review-caption">누적 시도 ${esc(number(u.attempts_total))}/${esc(number(l.attempts_total))} · 오늘(UTC) ${esc(number(u.attempts_today_utc))}/${esc(number(l.attempts_per_day))}<br>호출 간 대기 ${esc(number(l.global_cooldown_seconds))}초 · 캐시 ${esc(number(l.cache_seconds))}초<br>${s.ledger_scope==='durable_volume'?'사용량 기록: 영속 볼륨':'사용량 기록: 현재 서버 인스턴스 · 재시작 시 초기화'}${p==='openai'?`<br>추정 비용 상한 $${esc(s.estimated_cost_ceiling_usd??'미확인')} · 실제 청구액 아님`:''}</p>`;
   }
  } catch {
   state=null;
   for(const p of ['dart','openai'])el(p+'-availability').textContent='연결 상태를 확인하지 못했습니다. 새로고침 후 요청하세요.';
  } finally {refreshing=false;controls();}
 }
 async function request(p) {
  if(busy||refreshing||state?.[p]?.enabled!==true)return;
  const target=el(p+'-target').value;if(!Object.hasOwn(targets[p],target))return;
  busy=true;controls();el(p+'-result').textContent='요청 진행 중 · 응답 검증 중';
  try {
   const response=await fetch(`/api/providers/${p}/${encodeURIComponent(target)}`,{method:'POST',signal:AbortSignal.timeout(65000)});
   const r=await response.json();
   if(!response.ok) {
    if([404,429].includes(response.status)) {counts.blocked++;el(p+'-result').innerHTML=`<p class="warn">요청 차단 · ${esc(reason(r.detail||'BUSY_RETRY'))} · 이번 외부 호출 0회</p>`;}
    else throw Error();
   } else {
    if(!['succeeded','failed','blocked'].includes(r.status))throw Error();
    if(typeof r.external_calls_this_request==='number')counts.live+=r.external_calls_this_request;else counts.unknown++;
    if(r.execution==='cached_provider_response')counts.cached++;
    if(r.status==='failed')counts.failed++;
    if(r.status==='blocked')counts.blocked++;
    const execution=r.execution==='cached_provider_response'?'캐시 응답 재사용':r.execution==='live_provider_request'?'현재 외부 API 요청':'외부 요청 전 차단';
    el(p+'-result').innerHTML=`<div class="provider-result-heading"><strong class="${r.status==='succeeded'?'ok':'warn'}">${r.status==='succeeded'?'응답 검증 통과':r.status==='blocked'?'요청 차단':'실패 · 검증 통과 아님'}</strong><span>${execution}</span></div><p>${esc(targets[p][target])} · 이번 외부 호출 ${esc(number(r.external_calls_this_request))}회</p><p class="review-caption">원 응답 생성: ${esc(time(r.created_at))}<br>이번 응답 제공: ${esc(time(r.served_at))}<br>원 요청 추정 API 비용: ${r.estimated_cost_usd==null?'확인 불가':'$'+esc(r.estimated_cost_usd)} · 실제 청구액: ${r.billed_cost_usd==null?'미조회':'$'+esc(r.billed_cost_usd)}</p>${r.reason?`<p class="warn">${esc(reason(r.reason))}</p>`:''}${r.blocked_reasons?`<p class="warn">${r.blocked_reasons.map(x=>esc(reason(x))).join(' · ')}</p>`:''}${details(p,r)}<details class="provider-raw"><summary>응답 기록 JSON</summary><pre>${esc(JSON.stringify(r,null,2))}</pre></details>`;
   }
  } catch {
   counts.failed++;counts.unknown++;el(p+'-result').innerHTML='<p class="warn">응답을 확인하지 못했습니다. 외부 호출·과금 발생 여부는 확인 불가입니다. 자동 재시도하지 않습니다.</p>';
  } finally {busy=false;await refresh();}
 }
 for(const p of ['dart','openai']) {
  el(p+'-request').onclick=()=>request(p);
  el(p+'-target').onchange=()=>{el(p+'-result').textContent='대상 변경 · 아직 요청하지 않았습니다.';};
 }
 el('provider-refresh').onclick=refresh;refresh();
}
