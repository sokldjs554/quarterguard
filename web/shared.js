export const $ = s => document.querySelector(s);
export const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const labels = {revenue:'매출액',cost_of_sales:'매출원가',gross_profit:'매출총이익',operating_expenses:'판매관리비',operating_profit:'영업이익',net_profit:'당기순이익'};
export const shortLabels = {revenue:'REVENUE',cost_of_sales:'COST OF SALES',gross_profit:'GROSS PROFIT',operating_expenses:'SG&A',operating_profit:'OPERATING PROFIT',net_profit:'NET PROFIT'};
export const issues = {
 PERIOD_MISMATCH:['기간 불일치','단독 분기와 누적 기간, 비교 연도와 인접 분기를 확인하세요.'],
 SCOPE_MISMATCH:['연결 범위 불일치','연결과 별도 재무제표를 같은 기준으로 선택하세요.'],
 CURRENCY_MISMATCH:['통화 불일치','동일한 표시 통화의 근거를 선택하세요.'],
 CONVENIENCE_TRANSLATION:['참고 환산액','보고서마다 적용 환율이 다른 참고 USD 금액은 계산하지 않습니다.'],
 NEGATIVE_BASE:['음수 기저','적자 기저의 성장률은 해석이 왜곡될 수 있어 계산을 보류합니다.'],
 ZERO_BASE:['0 기저','분모가 0이므로 증감률을 계산할 수 없습니다.'],
 SEARCH_EMPTY:['근거 없음','수집 범위에 해당 자료가 없습니다.'],
 AMBIGUOUS_FACT:['복수 근거','단일 근거를 확정할 수 없습니다.'],
 NUMERIC_CONFLICT:['수치 불일치','직접 공시 금액과 차감 계산 결과가 다릅니다.'],
 SOURCE_MISMATCH:['출처 불일치','문서와 원문 위치가 등록된 근거와 다릅니다.'],
 MISSING_SOURCE:['출처 누락','원문 위치를 확인할 수 없습니다.'],
 TOOL_ERROR:['재검증 실패','도구 실행을 완료하지 못했습니다. 다시 시도하세요.'],
 TOOL_TIMEOUT:['재검증 시간 초과','서버 응답이 지연되고 있습니다. 잠시 후 다시 시도하세요.']
};
export const money = value => Number(typeof value === 'object' ? value.value : value).toLocaleString('en-US');
export const unit = f => `${f.scale === 1000000 ? '백만' : f.scale === 1000 ? '천' : f.scale} ${f.currency === 'KRW' ? '원' : 'USD'}`;
export const scope = f => f.scope === 'CFS' ? '연결' : '별도';
export const docTitle = id => id === 's24q3' ? '2024년 3분기 보고서' : '2024년 반기 보고서';
export const localTime = date => new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',dateStyle:'medium',timeStyle:'medium'}).format(new Date(date))+' KST';
export async function api(path, options = {}) {
 const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 60000);
 try {
  const response = await fetch(path, {...options, signal:controller.signal});
  if (!response.ok) throw Error(response.status === 429 ? '서버 실행 대기 · 잠시 후 재시도' : `연결 오류 (${response.status})`);
  return await response.json();
 } finally { clearTimeout(timer); }
}
export function errorText(e) { return e.name === 'AbortError' ? '응답 시간 초과 · 다시 시도해 주세요.' : e.message; }
export function download(value, name) {
 const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type:'application/json'}));
 const anchor = document.createElement('a'); anchor.href = url; anchor.download = name; anchor.click(); URL.revokeObjectURL(url);
}
export function traceHTML(trace) {
 const names = {get_fact:'수치 근거 조회',verify_comparison:'문맥·수치 대조',search_documents:'문서 검색',reconcile_quarter:'누적 차감 대조'};
 return trace.map(t => `<details class="trace-row"><summary><span class="num">${String(t.step).padStart(2,'0')}</span><span>${esc(names[t.tool] || t.tool)}</span><span class="time">${t.success ? '완료' : '실패'} · ${t.latency_ms.toFixed(0)} ms</span></summary><pre>${esc(JSON.stringify({tool:t.tool,arguments:t.arguments,output:t.output,failure_type:t.failure_type},null,2))}</pre></details>`).join('');
}
