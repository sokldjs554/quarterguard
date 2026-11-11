import {esc,api,errorText} from './shared.js';

const documentId='skh2024annual-in-2025oc';
const names={cash:'현금 및 현금성자산',inventory:'재고자산',revenue:'매출',cost_of_sales:'매출원가',operating_profit:'영업손익',dram:'DRAM',nand:'NAND Flash',other_products:'기타 제품·서비스',product_total:'제품·서비스 매출 합계'};
const form=document.querySelector('#source-evidence-form');
const box=document.querySelector('#source-evidence-results');
let ticket=0;
function render(result){
 if(result.answer_status!=='not_calculated'||result.calculated_answer!==null||!Array.isArray(result.hits)||!Array.isArray(result.messages)||result.context?.document_id!==documentId)throw Error('원문 근거 응답을 확인하지 못했습니다.');
 const hits=result.blocked?[]:result.hits;
 for(const {cell:c} of hits){
  if(c.document_id!==documentId||!['instant','duration'].includes(c.period_kind)||c.currency!=='KRW'||c.scale!==1000000||c.scope!=='CFS'||!/^[-]?\d+$/.test(c.value)||!Number.isInteger(c.page)||!c.table_title||!['2024','2023'].includes(c.column))throw Error('원문 근거 조건을 확인하지 못했습니다.');
 }
 return `<div class="finding"><h3>${hits.length?'원문 근거 후보 '+hits.length+'개':'조건 확인 필요'}</h3><p>${esc(result.context.title)} · 연결 · KRW · 백만 원</p><p class="calculation-note">기업·범위·통화·단위는 선택한 문서의 조건입니다. 아래 금액으로 질문의 답이나 비율을 계산하지 않았습니다. 이 자료는 분기 비교 작업지에 넣을 수 없습니다.</p>${result.messages.map(m=>`<p class="warn">${esc(m)}</p>`).join('')}${result.unknown_terms?.length?`<p>확인할 표현: ${result.unknown_terms.map(esc).join(' · ')}</p>`:''}</div>`+hits.map(({cell:c,role})=>{
  const date=c.period_kind==='instant'?`${c.as_of} 기준 잔액`:`${c.start} — ${c.end} · 연간 실적`;
  const link=new URL(c.source_url);
  if(link.protocol!=='https:'||link.hostname!=='links.sgx.com')throw Error('원문 주소를 확인하지 못했습니다.');
  link.hash='page='+c.page;
  return `<article class="source-cell-card" data-source-cell="${esc(c.id)}"><div><h3>${esc(names[c.metric]||c.metric)} · ${c.year}년</h3><strong class="source-cell-value">${Number(c.value).toLocaleString('en-US')} <small>백만 원</small></strong></div><p>${esc(date)} · 연결 · KRW</p>${role==='related_definition'?'<p class="warn">정의 확인용 관련 근거 · 선택된 계산 분모가 아닙니다.</p>':''}<dl><dt>원문 표</dt><dd>${esc(c.table_title)}</dd><dt>원문 행</dt><dd>${c.row?esc(c.row):'행명 없음 · 제품·서비스 유형별 표의 합계'}</dd><dt>원문 열</dt><dd>${esc(c.column)} · 금액 열 ${c.amount_column}</dd><dt>원문 위치</dt><dd>PDF ${c.page}쪽 · 인쇄 ${esc(c.printed_page)}</dd></dl><a href="${esc(link.href)}" target="_blank" rel="noopener">발행 공시 원문 ${c.page}쪽 열기 ↗</a><p class="calculation-note">추출 수치와 출처를 표시한 카드입니다. 원문 이미지가 아니며, 링크에서 행·열을 직접 확인하세요.</p></article>`;
 }).join('');
}
form.addEventListener('submit',async event=>{
 event.preventDefault();const current=++ticket;
 box.innerHTML='<p role="status">선택 문서에서 근거 찾는 중</p>';
 try{
  const result=await api('/api/source-search?document_id='+documentId+'&q='+encodeURIComponent(document.querySelector('#source-evidence-query').value));
  if(current!==ticket)return;
  box.innerHTML=render(result);
 }catch(error){if(current===ticket)box.innerHTML=`<p class="error-message" role="alert">${esc(errorText(error))} · 이전 결과를 표시하지 않습니다. 연결 복구 후 다시 검색하세요.</p>`;}
});
