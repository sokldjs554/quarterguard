import {esc} from './shared.js';

// Only backend-validated context is rendered here, never model-provided URLs.
function sourceHref(row) {
 try {
  const u=new URL(row.source_href);
  if(u.protocol==='https:'&&u.hostname==='images.samsung.com'&&!u.username&&!u.password&&
    u.pathname.endsWith('.pdf')&&Number.isInteger(row.page)&&row.page>0&&u.hash===`#page=${row.page}`)return u.href;
 } catch {}
 return null;
}
export function renderExplanationContext(context) {
 if(!context)return '<p class="scope-notice">근거 안내 없음 · 이 응답의 표시 단위와 원문 위치를 별도로 확인하세요.</p>';
 const rows=context.status==='available'&&Array.isArray(context.evidence)?context.evidence:[];
 const basis=Array.isArray(context.decision_basis)?context.decision_basis:[];
 return `<section class="explanation-context" aria-label="도구 결과의 단위와 출처"><h4>도구 결과의 단위·출처</h4><p>${esc(context.notice)}</p>${basis.length?`<div class="decision-basis"><h4>도구가 판정한 보류 사유</h4>${basis.map(x=>`<p>${esc(x.statement)}</p>`).join('')}<p class="scope-notice">${esc(context.decision_note)}</p></div>`:''}${rows.map(row=>{
  const href=sourceHref(row);
  return `<div class="explanation-source"><p>${esc(row.statement)}</p>${href?`<a href="${esc(href)}" target="_blank" rel="noopener">${esc(row.document_title)} · PDF p.${esc(row.page)} ↗</a>`:'<p>원문 링크 확인 필요</p>'}</div>`;
 }).join('')}</section>`;
}
