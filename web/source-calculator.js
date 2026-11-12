import {setJSONReviewReference} from './json-file-review.js';
import {esc,api,errorText,download} from './shared.js';

const root=document.querySelector('#source-calculator');
const mode=document.querySelector('#source-calc-mode');
const current=document.querySelector('#source-calc-current');
const base=document.querySelector('#source-calc-base');
const submit=document.querySelector('#source-calc-submit');
const resultBox=document.querySelector('#source-calc-result');
const exportButton=document.querySelector('#source-calc-export');
const names={cash:'현금 및 현금성자산',inventory:'재고자산',revenue:'매출',cost_of_sales:'매출원가',operating_profit:'영업손익',dram:'DRAM',nand:'NAND Flash',other_products:'기타 제품·서비스',product_total:'제품·서비스 매출 합계'};
const checkNames={COMPANY_MISMATCH:'기업',SCOPE_MISMATCH:'연결 범위',CURRENCY_MISMATCH:'통화',SOURCE_MISMATCH:'문서·해시·연도 열',UNKNOWN_UNIT:'단위 배율',INVALID_VALUE:'금액 형식',METRIC_MISMATCH:'항목 일치',MEASUREMENT_MISMATCH:'연간 실적·시점 잔액 구분',PERIOD_MISMATCH:'전년 기간·기준일',PRODUCT_CONTEXT_MISMATCH:'제품과 합계의 표·기간',NEGATIVE_PART:'제품 금액의 음수 여부',NONPOSITIVE_TOTAL:'합계의 양수 여부',PART_EXCEEDS_TOTAL:'제품 금액과 합계',ZERO_BASE:'기준값의 0 여부',NEGATIVE_BASE:'기준값의 음수 여부',RATIO_DEFINITION_REQUIRED:'재고 개월분의 정의'};
let data=null,loading=null,sequence=0,lastResult=null;
const number=v=>Number(v).toLocaleString('en-US',{maximumFractionDigits:12});
const dateLabel=c=>c.period_kind==='instant'?`${c.as_of} 기준 잔액`:`${c.start} — ${c.end} · 연간 실적`;
const label=c=>`${c.year} · ${names[c.metric]} · ${number(c.value)}백만 원 · ${c.period_kind==='instant'?'연말 잔액':'연간'}`;
function invalidate(){
 setJSONReviewReference(null);
 sequence++;lastResult=null;exportButton.disabled=true;submit.disabled=!data;
 resultBox.innerHTML='<p class="empty">현재 조건으로 확인해 주세요. 이전 계산 결과는 표시하지 않습니다.</p>';
}
function selectedEvidence(){
 const values=[current.value,base.value].map(id=>data?.cells.find(c=>c.id===id));
 document.querySelector('#source-calc-selected').innerHTML=values.map((c,i)=>{
  if(!c)return '';
  return `<div class="source-selected"><strong>${i?'B':'A'} · ${esc(names[c.metric])} · ${number(c.value)}백만 원</strong><p>${esc(dateLabel(c))} · 연결 · KRW</p><p>원문 ${esc(c.row||'행명 없는 제품 합계')} / ${c.column} 열 · PDF ${c.page}쪽 / 인쇄 ${esc(c.printed_page)}</p><a href="${esc(c.source_url+'#page='+c.page)}" target="_blank" rel="noopener">원문 근거 확인 ↗</a></div>`;
 }).join('');
}
function defaults(){
 if(!data)return;
 const picks={balance_yoy:['cash',2024,'cash',2023],annual_yoy:['revenue',2024,'revenue',2023],product_share:['dram',2024,'product_total',2024],inventory_months:['inventory',2024,'revenue',2023]}[mode.value];
 current.value=data.cells.find(c=>c.metric===picks[0]&&c.year===picks[1]).id;
 base.value=data.cells.find(c=>c.metric===picks[2]&&c.year===picks[3]).id;
 document.querySelector('#source-calc-current-label').textContent=mode.value==='product_share'?'A · 제품 매출':'A · 기준 자료';
 document.querySelector('#source-calc-base-label').textContent=mode.value==='product_share'?'B · 같은 표의 합계':'B · 비교 자료';
 submit.textContent=mode.value==='inventory_months'?'정의 확인':'조건 검증 후 계산';
 invalidate();selectedEvidence();
}
async function loadOptions(){
 if(data)return data;
 if(loading)return loading;
 loading=(async()=>{
  document.querySelector('#source-calc-load-error').hidden=true;
  try{
   const found=await api('/api/source-calculations/options');
   if(!Array.isArray(found.cells)||found.cells.length!==18||!Array.isArray(found.modes))throw Error('계산 자료를 확인하지 못했습니다.');
   for(const c of found.cells){
    if(c.currency!=='KRW'||c.scale!==1000000||c.scope!=='CFS'||!['instant','duration'].includes(c.period_kind)||!/^[-]?\d+$/.test(c.value))throw Error('원문 조건을 확인하지 못했습니다.');
    const url=new URL(c.source_url);if(url.protocol!=='https:'||url.hostname!=='links.sgx.com')throw Error('원문 주소를 확인하지 못했습니다.');
   }
   data=found;
   for(const input of [current,base]){input.innerHTML=found.cells.map(c=>`<option value="${esc(c.id)}">${esc(label(c))}</option>`).join('');input.disabled=false;}
   mode.disabled=false;defaults();return data;
  }catch(error){
   invalidate();document.querySelector('#source-calc-load-message').textContent=errorText(error);
   document.querySelector('#source-calc-load-error').hidden=false;throw error;
  }finally{loading=null;}
 })();
 return loading;
}
function renderResult(r,request){
 if(r.mode!==request.mode||!['verified','needs_review'].includes(r.status)||!Array.isArray(r.issues)||!Array.isArray(r.messages)||!Array.isArray(r.checks)||r.source_integrity!=='registered_snapshot'||r.source_snapshot_sha256!==data.document.cells_sha256||r.evidence?.[0]?.id!==request.current_id||r.evidence?.[1]?.id!==request.base_id)throw Error('계산 응답과 선택 조건이 다릅니다.');
 for(const k of ['growth_pct','share_pct'])if(r[k]!==null&&!/^-?\d+\.\d{4}$/.test(r[k]))throw Error('계산 수치 형식을 확인하지 못했습니다.');
 if(r.difference&&(r.difference.currency!=='KRW'||r.difference.scale!==1000000||!/^[-]?\d+(\.\d+)?$/.test(r.difference.value)))throw Error('차이 금액의 단위를 확인하지 못했습니다.');
 const [a,b]=r.evidence,share=r.mode==='product_share',inventory=r.mode==='inventory_months';
 const direction=inventory?'재고 개월분 · 선택한 A/B 자료의 정의 확인':share?`${a.year}년 제품 매출 / 같은 제품 표의 합계`:r.mode==='balance_yoy'?`${b.as_of} 대비 ${a.as_of} 잔액`:`${b.year}년 대비 ${a.year}년 연간 실적`;
 const title=r.status==='verified'?'조건 일치':r.difference?'증감률 보류 · 금액 차이는 확인':'계산 보류';
 return `<section class="finding"><h3>${title}</h3><p>${esc(direction)}</p>${r.messages.map(m=>`<p class="warn">${esc(m)}</p>`).join('')}<div class="source-output-values">${r.difference?`<p>금액 차이 <strong>${number(r.difference.value)}백만 원</strong></p>`:''}<p>${inventory?'재고 개월분':share?'제품 매출 비중':'증감률'} <strong>${esc((share?r.share_pct:r.growth_pct)===null?'—':(share?r.share_pct:r.growth_pct)+'%')}</strong></p></div>${r.transition==='loss_to_profit'?'<p><strong>적자에서 흑자로 전환</strong> · 일반 증감률과 구분합니다.</p>':''}${r.percentage_status==='calculated'?`<p class="calculation-note">${share?'A ÷ B × 100':'(A ÷ B − 1) × 100'} · 원 단위 환산 후 계산 · 소수점 넷째 자리 표시</p>`:''}<p class="calculation-note">선택한 두 근거와 조건에 대한 규칙 기반 계산입니다. 자연어 질문 전체의 자동 답변이나 감사 의견이 아닙니다.</p><details><summary>실행한 조건 확인</summary><ul>${r.checks.map(c=>`<li>${esc(checkNames[c.condition]||'추가 조건')} · ${c.passed?'충족':'확인 필요'}</li>`).join('')}</ul></details></section>`;
}
root.addEventListener('toggle',()=>{if(root.open)loadOptions().catch(()=>{});});
document.querySelector('#source-calc-retry').addEventListener('click',()=>loadOptions().catch(()=>{}));
mode.addEventListener('change',defaults);
for(const input of [current,base])input.addEventListener('change',()=>{invalidate();selectedEvidence();});
document.querySelector('#source-calc-form').addEventListener('submit',async event=>{
 event.preventDefault();if(!data)return;
 invalidate();const ticket=sequence,request={current_id:current.value,base_id:base.value,mode:mode.value};
 submit.disabled=true;resultBox.innerHTML='<p role="status">원문 조건과 계산 확인 중</p>';
 try{
  const r=await api('/api/source-calculations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});
  if(ticket!==sequence)return;
  resultBox.innerHTML=renderResult(r,request);lastResult=r;setJSONReviewReference(r);exportButton.disabled=false;
 }catch(error){if(ticket===sequence){lastResult=null;exportButton.disabled=true;resultBox.innerHTML=`<p class="error-message" role="alert">${esc(errorText(error))} · 이전 계산 결과는 표시하지 않습니다. 다시 실행해 주세요.</p>`;}}
 finally{if(ticket===sequence)submit.disabled=false;}
});
exportButton.addEventListener('click',()=>{if(lastResult)download(lastResult,'quarterguard-source-calculation.json');});
export async function selectCalculationCell(id,side){
 root.open=true;
 try{await loadOptions();if(!data.cells.some(c=>c.id===id))throw Error('등록된 근거가 아닙니다.');
  const input=side==='current'?current:base;input.value=id;invalidate();selectedEvidence();input.focus();
 }catch(error){resultBox.innerHTML=`<p class="error-message" role="alert">${esc(errorText(error))}</p>`;}
}
