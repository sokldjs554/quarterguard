import {selectCalculationCell} from './source-calculator.js';
import {esc,api,errorText,download} from './shared.js';
import {APPLE,appleCards,renderAppleReview} from './apple-review.js';

let documentId='skh2024annual-in-2025oc';
const picker=document.querySelector('#source-document'), query=document.querySelector('#source-evidence-query');
const reviewBox=document.querySelector('#apple-review-result'), reviewButton=document.querySelector('#apple-review-submit'), exportButton=document.querySelector('#apple-review-export');
let lastReview=null;
const names={cash:'현금 및 현금성자산',inventory:'재고자산',revenue:'매출',cost_of_sales:'매출원가',operating_profit:'영업손익',dram:'DRAM',nand:'NAND Flash',other_products:'기타 제품·서비스',product_total:'제품·서비스 매출 합계'};
const form=document.querySelector('#source-evidence-form');
const box=document.querySelector('#source-evidence-results');
let ticket=0;
function render(result){
 if(result.answer_status!=='not_calculated'||result.calculated_answer!==null||!Array.isArray(result.hits)||!Array.isArray(result.messages)||result.context?.document_id!==documentId)throw Error('원문 근거 응답을 확인하지 못했습니다.');
 const hits=result.blocked?[]:result.hits;
 if(documentId===APPLE)return `<div class="finding"><h3>${hits.length?'원문 근거 후보 '+hits.length+'개':'조건 확인 필요'}</h3><p>${esc(result.context.title)} · USD · 백만 미국 달러</p><p>검색은 계산 전 근거 후보입니다. ‘질문의 근거·계산 검증’을 실행해 지원 조건과 계산을 확인하세요.</p>${result.messages.map(m=>`<p class="warn">${esc(m)}</p>`).join('')}${result.unknown_terms?.length?`<p>확인할 표현: ${result.unknown_terms.map(esc).join(' · ')}</p>`:''}</div>`+appleCards(hits);
 for(const {cell:c} of hits){
  if(c.document_id!==documentId||!['instant','duration'].includes(c.period_kind)||c.currency!=='KRW'||c.scale!==1000000||c.scope!=='CFS'||!/^[-]?\d+$/.test(c.value)||!Number.isInteger(c.page)||!c.table_title||!['2024','2023'].includes(c.column))throw Error('원문 근거 조건을 확인하지 못했습니다.');
 }
 return `<div class="finding"><h3>${hits.length?'원문 근거 후보 '+hits.length+'개':'조건 확인 필요'}</h3><p>${esc(result.context.title)} · 연결 · KRW · 백만 원</p><p class="calculation-note">기업·범위·통화·단위는 선택한 문서의 조건입니다. 아래 금액으로 질문의 답이나 비율을 계산하지 않았습니다. 계산하려면 위의 별도 계산 영역에서 방식과 A/B 조건을 직접 선택하세요. 분기 비교 작업지에는 넣을 수 없습니다.</p>${result.messages.map(m=>`<p class="warn">${esc(m)}</p>`).join('')}${result.unknown_terms?.length?`<p>확인할 표현: ${result.unknown_terms.map(esc).join(' · ')}</p>`:''}</div>`+hits.map(({cell:c,role})=>{
  const date=c.period_kind==='instant'?`${c.as_of} 기준 잔액`:`${c.start} — ${c.end} · 연간 실적`;
  const link=new URL(c.source_url);
  if(link.protocol!=='https:'||link.hostname!=='links.sgx.com')throw Error('원문 주소를 확인하지 못했습니다.');
  link.hash='page='+c.page;
  return `<article class="source-cell-card" data-source-cell="${esc(c.id)}"><div><h3>${esc(names[c.metric]||c.metric)} · ${c.year}년</h3><strong class="source-cell-value">${Number(c.value).toLocaleString('en-US')} <small>백만 원</small></strong></div><p>${esc(date)} · 연결 · KRW</p>${role==='related_definition'?'<p class="warn">정의 확인용 관련 근거 · 선택된 계산 분모가 아닙니다.</p>':''}<dl><dt>원문 표</dt><dd>${esc(c.table_title)}</dd><dt>원문 행</dt><dd>${c.row?esc(c.row):'행명 없음 · 제품·서비스 유형별 표의 합계'}</dd><dt>원문 열</dt><dd>${esc(c.column)} · 금액 열 ${c.amount_column}</dd><dt>원문 위치</dt><dd>PDF ${c.page}쪽 · 인쇄 ${esc(c.printed_page)}</dd></dl><a href="${esc(link.href)}" target="_blank" rel="noopener">발행 공시 원문 ${c.page}쪽 열기 ↗</a><div class="source-candidate-actions"><button type="button" class="secondary" data-calc-side="current" data-cell-id="${esc(c.id)}">계산 A에 선택</button><button type="button" class="secondary" data-calc-side="base" data-cell-id="${esc(c.id)}">계산 B에 선택</button></div><p class="calculation-note">추출 수치와 출처를 표시한 카드입니다. 원문 이미지가 아니며, 링크에서 행·열을 직접 확인하세요.</p></article>`;
 }).join('');
}
form.addEventListener('submit',async event=>{
 event.preventDefault();invalidate();const current=ticket;
 box.innerHTML='<p role="status">선택 문서에서 근거 찾는 중</p>';
 try{
  const result=await api('/api/source-search?document_id='+documentId+'&q='+encodeURIComponent(document.querySelector('#source-evidence-query').value));
  if(current!==ticket)return;
  box.innerHTML=render(result);
 }catch(error){if(current===ticket)box.innerHTML=`<p class="error-message" role="alert">${esc(errorText(error))} · 이전 결과를 표시하지 않습니다. 연결 복구 후 다시 검색하세요.</p>`;}
});

box.addEventListener('click',event=>{const button=event.target.closest('[data-calc-side]');if(button)selectCalculationCell(button.dataset.cellId,button.dataset.calcSide);});

function invalidate(){
 ticket++;lastReview=null;exportButton.disabled=true;reviewButton.disabled=false;
 box.innerHTML='<p class="empty">현재 문서·질문으로 다시 검색해 주세요. 이전 근거는 표시하지 않습니다.</p>';
 reviewBox.innerHTML='<p class="empty">현재 문서·질문으로 검증해 주세요. 이전 결과는 표시하지 않습니다.</p>';
}
query.addEventListener('input',invalidate);
picker.addEventListener('change',()=>{
 documentId=picker.value;invalidate();
 const apple=documentId===APPLE;
 document.querySelector('#source-calculator').hidden=apple;
 document.querySelector('#apple-review-actions').hidden=!apple;
 document.querySelector('#source-document-description').textContent=apple?'SEC 공식 HTML의 선택 수치 25개와 설명 문단을 연결합니다. 제품·서비스 매출총이익률, 지역 매출, 현금흐름, 세금 대조와 판단 보류를 지원합니다. FY2024는 52주, FY2023은 53주입니다.':'SK하이닉스의 선택 수치 18개를 검색합니다. 연결 · KRW · 백만 원. 기존 연간·잔액·제품 비중 계산을 이용하세요.';
 query.value=apple?'2024회계연도에 제품과 서비스 중 어느 쪽의 매출총이익률이 더 높았나?':'현금은 2023년 말보다 얼마나 늘었나?';
});
reviewButton.addEventListener('click',async()=>{
 invalidate();const current=ticket,text=query.value,doc=documentId;
 reviewButton.disabled=true;reviewBox.innerHTML='<p role="status">원문 근거·비교 조건·계산 확인 중</p>';
 try{
  const result=await api('/api/source-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({document_id:doc,query:text})});
  if(current!==ticket)return;
  reviewBox.innerHTML=renderAppleReview(result,text);box.innerHTML='<p class="empty">검토에 사용한 근거는 위의 결과에 표시했습니다.</p>';lastReview=result;exportButton.disabled=false;
 }catch(error){if(current===ticket){lastReview=null;exportButton.disabled=true;reviewBox.innerHTML=`<p class="error-message" role="alert">${esc(errorText(error))} · 이전 결과를 표시하지 않습니다. 다시 실행해 주세요.</p>`;}}
 finally{if(current===ticket)reviewButton.disabled=false;}
});
exportButton.addEventListener('click',()=>{if(lastReview)download(lastReview,'quarterguard-apple-review.json');});
