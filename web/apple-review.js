import {esc} from './shared.js';
export const APPLE='apple-2024-10k';
const SOURCE='https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm';
const labels={products_margin_pct:'제품 집계 매출총이익률',services_margin_pct:'서비스 집계 매출총이익률',china_difference:'중국권 매출 변화',total_difference:'전체 매출 변화',operating_cash_less_capex:'영업현금흐름 − 취득 지출',spending_increase:'자사주 매입 지출액 변화',signed_cash_flow_change:'부호를 유지한 현금흐름 변화',operating_profit_change:'영업이익 변화',tax_expense_change:'법인세비용 변화',net_income_change:'순이익 변화',state_aid_tax:'국가보조금 결정 세액조정 영향'};
export function validateAppleCell(c){
 if(c.document_id!==APPLE||c.source_url!==SOURCE||c.source_format!=='SEC_HTML'||c.scope!=='CFS'||c.currency!=='USD'||c.scale!==1000000||c.page!==null||!Number.isInteger(c.printed_page)||!/^[-]?\d+$/.test(c.value)||!['2023','2024'].includes(c.column)||!c.row||!c.table_title)throw Error('Apple 원문 수치의 조건을 확인하지 못했습니다.');
 if(c.source_locator&&!/^#f-\d+$/.test(c.source_locator))throw Error('원문 위치를 확인하지 못했습니다.');
}
export function appleCards(hits){
 return hits.map(({cell:c})=>{
  validateAppleCell(c);
  return `<article class="source-cell-card" data-source-cell="${esc(c.id)}"><h3>${esc(c.section?c.section+' / ':'')}${esc(c.row)} · FY${c.year}</h3><strong class="source-cell-value">${Number(c.value).toLocaleString('en-US')} <small>백만 미국 달러</small></strong><p>${esc(c.start)} — ${esc(c.end)} · ${c.fiscal_weeks}주 · 연결 · USD</p><dl><dt>원문 표</dt><dd>${esc(c.table_title)}</dd><dt>원문 행·열</dt><dd>${esc(c.section||'')} / ${esc(c.row)} / ${c.column} · 금액 열 ${c.amount_column}</dd><dt>원문 위치</dt><dd>HTML · 인쇄 ${c.printed_page}쪽 (PDF 쪽수 아님)</dd></dl>${c.row_role==='cash_outflow'?'<p>원문 괄호는 현금 유출입니다. 지출액 크기와 부호를 구분하세요.</p>':''}<a href="${esc(SOURCE+(c.source_locator||''))}" target="_blank" rel="noopener">SEC 원문 확인 ↗</a><p class="calculation-note">추출 근거 카드입니다. 원문 이미지가 아니며, 행·열은 공시에서 직접 확인하세요.</p></article>`;
 }).join('');
}
export function renderAppleReview(r,query){
 if(r.document_id!==APPLE||r.query!==query||r.execution!=='deterministic_source_review'||r.source_integrity!=='registered_snapshot'||!['verified','needs_review'].includes(r.status)||r.currency!=='USD'||r.scale!==1000000||!Array.isArray(r.evidence)||!Array.isArray(r.messages)||!Array.isArray(r.warnings)||!Array.isArray(r.steps)||!Array.isArray(r.formulas))throw Error('검토 응답과 현재 조건이 다릅니다.');
 for(const c of r.evidence)validateAppleCell(c);
 for(const [k,v] of Object.entries(r.values))if(!labels[k]||!/^[-]?\d+(\.\d+)?$/.test(v))throw Error('검토 수치 형식을 확인하지 못했습니다.');
 for(const n of r.narratives)if(n.source_url!==SOURCE||n.document_id!==APPLE||typeof n.text!=='string')throw Error('설명 근거를 확인하지 못했습니다.');
 return `<section class="finding"><h3>${r.status==='verified'?'조건 확인 · 계산 완료':'판단 보류 · 확인 필요'}</h3><p>${esc(r.operation_label||'지원 조건 확인')}</p><p>Apple · 연결 · USD · 백만 미국 달러${r.context.base_year?` · ${r.context.base_year}년 대비 ${r.context.current_year}년`:''}</p>${[...r.messages,...r.warnings].map(x=>`<p class="warn">${esc(x)}</p>`).join('')}${r.unknown_terms.length?`<p>확인할 표현: ${r.unknown_terms.map(esc).join(' · ')}</p>`:''}<div class="source-output-values">${Object.entries(r.values).map(([k,v])=>`<p>${labels[k]} <strong>${Number(v).toLocaleString('en-US',{maximumFractionDigits:4})}${k.endsWith('_pct')?'%':'백만 달러'}</strong></p>`).join('')}</div>${r.explanation.map(x=>`<p>${esc(x)}</p>`).join('')}${r.required_information.length?`<p>추가로 필요한 자료: ${r.required_information.map(esc).join(' · ')}</p>`:''}<details><summary>계산식·실행 기록 확인</summary><p>규칙 기반 내부 실행 단계입니다. LLM 계획이나 MCP 통신 로그가 아닙니다.</p><pre>${esc(JSON.stringify({steps:r.steps,formulas:r.formulas,source_snapshot_sha256:r.source_snapshot_sha256},null,2))}</pre></details><p class="calculation-note">선택한 문서와 지원 작업의 검토 결과입니다. 회사 전체 공시의 정확성이나 감사 의견을 보장하지 않습니다.</p></section>${r.narratives.map(n=>`<details><summary>원문 설명 · 인쇄 ${n.printed_page}쪽</summary><blockquote>${esc(n.text)}</blockquote><a href="${SOURCE}" target="_blank" rel="noopener">SEC 원문 열기 ↗</a></details>`).join('')}${appleCards(r.evidence.map(cell=>({cell})))}`;
}
