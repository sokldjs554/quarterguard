// Local File API only: no upload, external request, link execution or persistent storage.
const MAX_BYTES=1024*1024;
const modes={inventory_months:'재고 개월분 · 정의 확인',balance_yoy:'전년 말 잔액 증감',annual_yoy:'연간 실적 전년 대비',product_share:'제품 매출 비중'};
const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function canonical(value,depth=0,budget={nodes:0}){
 if(depth>64||++budget.nodes>20000)throw Error('파일 구조가 너무 복잡합니다. 저장한 원본 JSON을 선택해 주세요.');
 if(typeof value==='number'&&(!Number.isFinite(value)||(Number.isInteger(value)&&!Number.isSafeInteger(value))))throw Error('정확하게 읽을 수 없는 숫자가 있습니다.');
 if(Array.isArray(value))return '['+value.map(v=>canonical(v,depth+1,budget)).join(',')+']';
 if(object(value))return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k],depth+1,budget)).join(',')+'}';
 return JSON.stringify(value);
}
export function inspectSavedJSON(text,reference=null){
 if(new TextEncoder().encode(text).length>MAX_BYTES)throw Error('1MB 이하의 JSON 파일을 선택해 주세요.');
 let value;
 try{value=JSON.parse(text.replace(/^\uFEFF/,''));}catch{throw Error('JSON 형식을 읽을 수 없습니다. 내려받은 .json 파일을 선택해 주세요.');}
 const normalized=canonical(value);
 const apple=object(value)&&value.execution==='deterministic_source_review'&&value.document_id==='apple-2024-10k';
 const sk=object(value)&&value.execution==='deterministic_decimal'&&Object.hasOwn(modes,value.mode);
 if((!apple&&!sk)||!['verified','needs_review'].includes(value.status)||!Array.isArray(value.evidence)||!value.evidence.every(object)||!Array.isArray(value.messages)||!value.messages.every(m=>typeof m==='string')||!Array.isArray(value.issues)||!value.issues.every(m=>typeof m==='string'))throw Error('Apple 검토 또는 SK하이닉스 계산에서 저장한 JSON인지 확인해 주세요.');
 const lines=[apple?'Apple 검토 파일':'SK하이닉스 계산 파일',apple?'질문: '+String(value.query):'계산 방식: '+modes[value.mode],
  '파일에 기록된 판정: '+(value.status==='needs_review'?'확인 필요 / 계산·판단 보류':'조건 일치'),
  '문제 코드: '+(value.issues.join(', ')||'없음'),...value.messages];
 if(value.required_information?.length)lines.push('추가로 필요한 자료: '+value.required_information.join(' · '));
 if(apple)lines.push('통화: '+value.currency+' · 배율: '+value.scale,'계산 결과: '+JSON.stringify(value.values));
 else lines.push('증감률: '+(value.growth_pct??'계산하지 않음'),'제품 비중: '+(value.share_pct??'계산하지 않음'),'금액 차이: '+JSON.stringify(value.difference));
 for(const [i,c] of value.evidence.entries())lines.push('',`근거 ${i+1}: ${c.id}`,`항목: ${c.row??c.metric} / ${c.column} 열`,
  `금액: ${c.value} · 통화: ${c.currency} · 배율: ${c.scale} · 범위: ${c.scope}`,
  c.as_of?`기준일: ${c.as_of}`:`기간: ${c.start} — ${c.end}`,
  `문서: ${c.document_id} · PDF ${c.page??'해당 없음'} · 인쇄 ${c.printed_page??'미기재'}`,
  '원문 주소: '+c.source_url);
 return {value,summary:lines.join('\n'),match:reference===null?null:normalized===canonical(reference)};
}
let reference=null,sequence=0;
const root=typeof document==='undefined'?null:document.querySelector('#saved-json-reader');
const field=id=>root?.querySelector('#'+id);
function clear(message='파일을 선택하면 이 화면에서 내용을 읽을 수 있습니다.',resetInput=true){
 sequence++;
 if(!root)return;
 field('saved-json-status').textContent=message;
 field('saved-json-summary').textContent='';field('saved-json-raw').textContent='';
 field('saved-json-content').hidden=true;field('saved-json-error').hidden=true;
 field('saved-json-error').textContent='';if(resetInput)field('saved-json-file').value='';
}
export function setJSONReviewReference(value){
 reference=value;
 clear('검토 조건이 바뀌었습니다. 확인할 JSON 파일을 다시 선택해 주세요.');
}
if(root){
 const input=field('saved-json-file');
 input.addEventListener('click',()=>clear());
 input.addEventListener('cancel',()=>clear('파일 선택을 취소했습니다.'));
 field('saved-json-clear').addEventListener('click',()=>clear());
 input.addEventListener('change',async()=>{
  const file=input.files?.[0];clear(undefined,false);const ticket=sequence;
  if(!file)return;
  field('saved-json-status').textContent='선택한 파일을 읽는 중입니다.';
  try{
   if(file.size>MAX_BYTES)throw Error('1MB 이하의 JSON 파일을 선택해 주세요.');
   const text=await file.text();if(ticket!==sequence)return;
   const result=inspectSavedJSON(text,reference);
   field('saved-json-status').textContent=`파일: ${file.name} · ${file.size}바이트\n`+(result.match===true?'현재 검토 결과와 파일의 JSON 값·필드가 일치합니다.':result.match===false?'현재 검토 결과와 파일 내용이 다릅니다. 질문·입력·검토 시점을 확인하세요.':'현재 비교할 검토 결과가 없습니다. 파일 내용만 읽었습니다.');
   field('saved-json-summary').textContent=result.summary;
   field('saved-json-raw').textContent=text;
   field('saved-json-content').hidden=false;
  }catch(error){
   if(ticket!==sequence)return;
   field('saved-json-status').textContent='파일 확인을 완료하지 못했습니다.';
   field('saved-json-error').textContent=error.message||'파일을 읽지 못했습니다. 다시 선택해 주세요.';
   field('saved-json-error').hidden=false;
  }
 });
}
