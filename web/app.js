import {mountProgress} from './progress.js';
import {$,esc,labels,shortLabels,issues,money,unit,scope,docTitle,api,errorText,download,traceHTML,localTime} from './shared.js';
import {evidenceInspector} from './evidence.js';
import {mountReview} from './review.js';
import {reviewKey,readReview,writeReview,csvText} from './review-notes.mjs';
import {mountProviders} from './providers.js';
import {mountHeldout} from './heldout.js';

const defaults={current:{document:'s24q3',year:2024,scope:'CFS',period:'q',currency:'KRW'},base:{document:'s24q2',year:2024,scope:'CFS',period:'q',currency:'KRW'},mode:'qoq'};
let facts=[],sources=[],inspector=null,current=null,selectedMetric='revenue',selectedSide='current',busy=false,requestId=0,ready=false,searchId=0;
let noteKey=null,noteRecord=null,noteDirty=false;
const reviewCache=new Map(),unsavedKeys=new Set(),unreadableKeys=new Set();
function getNote(row,mode) {
 const key=reviewKey(row,mode);
 if(reviewCache.has(key))return reviewCache.get(key);
 try {const record=readReview(localStorage,key);reviewCache.set(key,record);unreadableKeys.delete(key);return record;}
 catch {unreadableKeys.add(key);return {note:'',reviewed:false,updated_at:null};}
}
function unreadableCurrent() {return current?.rows?.some(row=>unreadableKeys.has(reviewKey(row,current.selection.mode)))||false;}
function reviewControls() {
 const unavailable=busy||!ready||!current?.workflow_success||!current?.rows?.length;
 const unreadable=unreadableCurrent();
 $('#export-btn').disabled=unavailable||unreadable;
 document.querySelectorAll('#review-note, #mark-reviewed, #save-note').forEach(x=>x.disabled=unavailable||unreadableKeys.has(noteKey));
 $('#retry-note').hidden=!unreadable;$('#retry-note').disabled=unavailable;
 if(unreadable)$('#note-status').textContent='메모 읽기 실패 · 기존 기록 보호를 위해 CSV를 중지했습니다. 다시 불러오세요.';
}
function saveNote() {
 if(!noteKey||!noteRecord||unreadableKeys.has(noteKey))return;
 noteRecord={...noteRecord,note:$('#review-note').value,updated_at:new Date().toISOString()};
 reviewCache.set(noteKey,noteRecord);
 try {writeReview(localStorage,noteKey,noteRecord);unsavedKeys.delete(noteKey);noteDirty=false;$('#note-status').textContent='저장됨 · 이 브라우저에만 보관';}
 catch {unsavedKeys.add(noteKey);noteDirty=true;$('#note-status').textContent='저장 실패 · 현재 화면에만 유지됩니다. CSV로 보관하세요.';}
 reviewControls();
}
function clearNote() {
 if(noteDirty)saveNote();
 noteKey=null;noteRecord=null;noteDirty=false;
 $('#review-note').value='';$('#note-metric').textContent='';$('#mark-reviewed').textContent='확인 표시';$('#mark-reviewed').setAttribute('aria-pressed','false');
 $('#note-status').textContent='이 브라우저에만 저장됩니다.';
}
function bindNote(row) {
 const key=reviewKey(row,current.selection.mode);
 if(key!==noteKey) {
  if(noteDirty)saveNote();
  noteKey=key;noteRecord=getNote(row,current.selection.mode);noteDirty=unsavedKeys.has(key);
  $('#review-note').value=noteRecord.note;
  $('#note-status').textContent=noteDirty?'저장 실패 · 현재 화면에만 유지됩니다. CSV로 보관하세요.':noteRecord.updated_at?'저장됨 · 이 브라우저에만 보관':'이 브라우저에만 저장됩니다.';
 }
 $('#note-metric').textContent='· '+labels[row.metric];
 $('#mark-reviewed').textContent=noteRecord.reviewed?'확인함':'확인 표시';$('#mark-reviewed').setAttribute('aria-pressed',String(noteRecord.reviewed));
 reviewControls();
}
function settings(open) {
 $('#comparison-settings').hidden=!open;$('#settings-btn').setAttribute('aria-expanded',String(open));
}
function updateContext() {
 const request=selection();
 const describe=s=>`${s.year}년 ${s.document==='s24q3'?'3분기':'2분기'} ${s.period==='ytd'?'누적':'단독'} · ${s.scope==='CFS'?'연결':'별도'} · ${s.currency==='KRW'?'백만 원':'천 USD'}`;
 $('#selection-summary').textContent=`${request.mode==='qoq'?'전분기':'전년 동기'} 대비 | A ${describe(request.current)} / B ${describe(request.base)}`;
 const row=current?.rows?.find(r=>r.metric===selectedMetric);
 document.querySelectorAll('[data-document]').forEach(b=>{const active=row?.[selectedSide]?.document_id===b.dataset.document;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
}
const options={document:[['s24q3','2024년 3분기 보고서'],['s24q2','2024년 반기 보고서']],year:[[2024,'2024년'],[2023,'2023년']],scope:[['CFS','연결'],['OFS','별도']],period:[['q','단독 분기'],['ytd','누적']],currency:[['KRW','백만 원'],['USD','천 USD · 참고']]};
const optionNames={document:'문서',year:'연도',scope:'범위',period:'기간',currency:'단위'};
function view(name) {
 document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!==name);
 document.querySelectorAll('[data-view]').forEach(b=>{b.classList.toggle('active',b.dataset.view===name);if(b.dataset.view===name)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
}
function selectors() {
 for(const side of ['current','base']) {
  $(`[data-side="${side}"]`).innerHTML=Object.entries(options).map(([key,values])=>`<label class="${key==='document'?'document-select':''}" for="${side}-${key}"><span>${optionNames[key]}</span><select id="${side}-${key}" aria-label="${side==='current'?'기준':'비교'} ${optionNames[key]}">${values.map(([value,label])=>`<option value="${value}" ${defaults[side][key]===value?'selected':''}>${label}</option>`).join('')}</select></label>`).join('');
 }
 document.querySelectorAll('.selectors select').forEach(s=>s.onchange=()=>execute(false));
 $('#mode').onchange=()=>execute(false);
}
function selection() {
 const result={mode:$('#mode').value};
 for(const side of ['current','base']) result[side]=Object.fromEntries(Object.keys(options).map(k=>[k,k==='year'?Number($(`#${side}-${k}`).value):$(`#${side}-${k}`).value]));
 return result;
}
function setSelection(request) {
 for(const side of ['current','base']) for(const key of Object.keys(options))$(`#${side}-${key}`).value=request[side][key];
 $('#mode').value=request.mode;
}
function setBusy(value) {
 busy=value;$('#desk').setAttribute('aria-busy',String(value));
 document.querySelectorAll('.selectors select, #mode, #run-btn, #reset-btn, [data-document]').forEach(x=>x.disabled=value||!ready);
 reviewControls();
 $('#execution-status').classList.toggle('busy-pulse',value);
}
async function execute(live) {
 const token=++requestId,request=selection(),focusId=document.activeElement?.id;
 clearNote();current=null;updateContext();$('#work-alert').hidden=true;$('#trace-btn').disabled=true;$('#trace-dialog').close();setBusy(true);
 $('#execution-status').textContent=live?'근거 조회·문맥 대조 진행 중 · 실제 MCP 실행':'선택한 자료의 표 계산 중';
 $('#table-summary').textContent='자료 대조 중';
 $('#worksheet-rows').innerHTML='<tr><td colspan="6" class="empty" role="status">선택한 자료의 근거 대조 중</td></tr>';
 $('#finding').innerHTML='<h3>결과 대기</h3><p class="calculation-note">새 설정의 계산이 완료되면 검토 결과를 표시합니다.</p>';
 inspector?.clear();$('#source-counter').textContent='—';
 try {
  const result=await api(live?'/api/worksheet/run':'/api/worksheet',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});
  if(token!==requestId)return;
  if(!result.workflow_success) {
   current=result;$('#trace-btn').disabled=false;
   throw Error((result.issues||[]).map(x=>issues[x]?.[0]||x).join(' · ')||'재검증 실패');
  }
  current={...result,selection:request};render();
 } catch(e) {
  if(token!==requestId)return;
  $('#work-alert').textContent=errorText(e)+' · 설정 초기화 또는 근거 재검증으로 다시 시도할 수 있습니다.';$('#work-alert').hidden=false;
  $('#worksheet-rows').innerHTML='<tr><td colspan="6" class="empty">현재 설정의 결과 없음</td></tr>';
  $('#finding').innerHTML='<h3>검토 결과 없음</h3><p class="calculation-note">이전 결과를 현재 설정의 결과로 표시하지 않습니다.</p>';
  $('#table-summary').textContent='대조 미완료';$('#execution-status').textContent='실행 미완료 · 성공 판정 없음';
 } finally {if(token===requestId){setBusy(false);if(focusId&&document.activeElement===document.body)document.getElementById(focusId)?.focus({preventScroll:true});}}
}
function render() {
 const rows=current.rows,first=rows[0],failed=rows.filter(r=>r.result.status!=='verified').length;
 rows.forEach(row=>getNote(row,current.selection.mode));
 $('#current-heading').innerHTML=`기준 A <span class="column-subtitle">${first.current.start.slice(0,7)}–${first.current.end.slice(0,7)} · ${unit(first.current)}</span>`;
 $('#base-heading').innerHTML=`비교 B <span class="column-subtitle">${first.base.start.slice(0,7)}–${first.base.end.slice(0,7)} · ${unit(first.base)}</span>`;
 $('#table-summary').textContent=`${rows.length}개 항목 · ${failed?'확인 필요 '+failed+'건':'문맥 일치'}`;
 $('#worksheet-rows').innerHTML=rows.map((r,i)=>{
  const ok=r.result.status==='verified',value=r.result.growth_pct;
  return `<tr data-row="${r.metric}" class="${selectedMetric===r.metric?'selected':''}"><td class="row-index">${String(i+1).padStart(2,'0')}</td><td><button class="metric-name" data-metric="${r.metric}">${labels[r.metric]}<small>${shortLabels[r.metric]}</small></button></td>${['current','base'].map(side=>`<td class="value-cell" data-label="${side==='current'?'A 기준':'B 비교'}"><button class="number-button ${selectedMetric===r.metric&&selectedSide===side?'active':''}" data-fact="${r[side].id}" data-side="${side}" data-metric="${r.metric}" aria-label="${labels[r.metric]} ${side==='current'?'기준':'비교'} ${money(r[side])} ${unit(r[side])} 근거">${money(r[side])}</button></td>`).join('')}<td class="growth ${ok?'':'warn'}">${ok?(Number(value)>0?'+':'')+esc(value)+'%':'—'}</td><td class="status-cell"><span class="${ok?'ok':'warn'}">${ok?'조건 일치':esc(issues[r.result.issues[0]]?.[0]||'확인 필요')}</span></td></tr>`;
 }).join('');
 $('#worksheet-rows').querySelectorAll('tr').forEach(tr=>tr.onclick=e=>{
  const b=e.target.closest('[data-metric]');selectedMetric=tr.dataset.row;selectedSide=b?.dataset.side||'current';selectRow();if(b?.dataset.fact&&matchMedia('(max-width:600px)').matches)$('#source-panel').scrollIntoView({block:'start'});
 });
 $('#execution-status').textContent=current.execution_mode==='live_mcp'?`실제 MCP 재검증 완료 · ${current.trace.length}회 도구 호출 · ${(current.latency_ms/1000).toFixed(2)}초`:`수집 수치의 표 계산 · ${current.latency_ms.toFixed(1)} ms · 현재 MCP 호출 없음`;
 $('#trace-btn').disabled=false;selectRow();
}
function selectRow() {
 const row=current?.rows?.find(r=>r.metric===selectedMetric);if(!row)return;
 document.querySelectorAll('[data-row]').forEach(tr=>tr.classList.toggle('selected',tr.dataset.row===selectedMetric));
 document.querySelectorAll('[data-fact]').forEach(b=>b.classList.toggle('active',b.dataset.metric===selectedMetric&&b.dataset.side===selectedSide));
 const a=row.current,b=row.base,r=row.result,ok=r.status==='verified';
 $('#finding').innerHTML=`<div class="finding-heading"><h3>${labels[row.metric]} · 검토 근거</h3><span class="${ok?'ok':'warn'}">${ok?'비교 조건 일치':'계산 보류'}</span></div><div class="context-checks"><span class="${r.issues.includes('PERIOD_MISMATCH')?'bad':''}">기간 ${a.months}개월 ↔ ${b.months}개월</span><span class="${r.issues.includes('SCOPE_MISMATCH')?'bad':''}">범위 ${scope(a)} ↔ ${scope(b)}</span><span class="${r.issues.some(x=>['CURRENCY_MISMATCH','CONVENIENCE_TRANSLATION'].includes(x))?'bad':''}">${unit(a)} ↔ ${unit(b)}</span></div>${ok?`<div class="calculation">(${money(a)} ÷ ${money(b)} − 1) × 100 = ${esc(r.growth_pct)}%</div><p class="calculation-note">문서·행·열의 출처 확인 · Decimal 계산 · 소수점 4자리 반올림</p>`:r.issues.map(x=>`<div class="finding-issue">${esc(issues[x]?.[0]||x)}<small>${esc(issues[x]?.[1]||'근거 재확인 필요')}</small></div>`).join('')}`;
 inspector.show(row[selectedSide],[a,b],selectedSide==='current'?0:1);$('#source-counter').textContent=`${selectedSide==='current'?'A 기준':'B 비교'} · ${labels[row.metric]}`;
 bindNote(row);updateContext();
}
function openTrace() {
 if(!current)return;
 const live=current.execution_mode==='live_mcp';
 $('#trace-content').innerHTML=`<p class="trace-summary">${live?(current.workflow_success?'현재 MCP 실제 실행 완료':'현재 MCP 실행 실패'):'현재 서버의 표 계산 · MCP 실행 아님'}<br>${current.trace.length}회 도구 호출 · 생성형 모델 0회 · ${esc(localTime(current.created_at))}<br>${live?'MCP protocol '+esc(current.protocol||'미확인'):'선택한 문맥의 canonical 수치를 Decimal로 대조'}</p>${current.trace.length?traceHTML(current.trace):'<p class="review-caption">근거 재검증을 실행하면 수치 조회와 비교의 실제 도구 기록이 여기에 표시됩니다.</p>'}`;
 $('#trace-dialog').showModal();
}
async function loadReview() {
 try {const [evaluation,cases]=await Promise.all([api('/api/evaluation'),api('/api/cases')]);mountReview(evaluation,cases);}
 catch(e){$('#evaluation-content').innerHTML=`<p class="error-message" role="alert">평가 자료 연결 불가 · ${esc(errorText(e))}</p><button id="review-retry" class="secondary">평가 다시 불러오기</button>`;$('#review-retry').onclick=loadReview;$('#prepared-btn').disabled=$('#case-run-btn').disabled=true;}
}
async function boot() {
 ready=false;$('#boot-error').hidden=true;setBusy(true);
 try {
  const [fs,ss,health]=await Promise.all([api('/api/facts'),api('/api/sources'),api('/health')]);
  facts=fs;sources=ss;inspector=evidenceInspector($('#evidence-content'),facts,sources,(id,index)=>{
   const row=current?.rows.find(r=>r.current.id===id||r.base.id===id);if(!row)return;
   selectedMetric=row.metric;selectedSide=index===0?'current':'base';selectRow();
  });
  $('#version').textContent='v1.4.0 · '+health.commit.slice(0,7);
  $('#document-count').textContent=sources.length;
  $('#document-list').innerHTML=sources.map(s=>`<button class="document-item" data-document="${esc(s.id)}" aria-pressed="false"><span class="doc-icon" aria-hidden="true">PDF</span><span><strong>${s.id==='s24q3'?'2024년 3분기':'2024년 반기'}</strong><small>${s.pages}쪽 · 영문 IR</small></span></button>`).join('');
  document.querySelectorAll('[data-document]').forEach(b=>b.onclick=async()=>{
   if(busy||!ready)return;view('work');const row=current?.rows?.find(r=>r.metric===selectedMetric);
   const side=['current','base'].find(side=>row?.[side]?.document_id===b.dataset.document);
   if(side){selectedSide=side;selectRow();}
   else {const request=selection();request.current.document=b.dataset.document;setSelection(request);selectedSide='current';await execute(false);}
  });
  $('#source-index').innerHTML=sources.map(s=>`<div class="source-index-row"><a href="${esc(s.url)}" target="_blank" rel="noopener">${docTitle(s.id)} · Samsung Electronics ↗</a><span>${s.pages} pages · ${s.report_end}</span></div>`).join('');
  ready=true;await execute(false);loadReview();
 } catch(e) {$('#boot-error').hidden=false;$('#work-alert').hidden=true;$('#desk').setAttribute('aria-busy','false');$('#table-summary').textContent='연결 불가';$('#execution-status').textContent='수집 자료 연결 필요';}
}
$('#search-form').onsubmit=async e=>{
 e.preventDefault();const ticket=++searchId,box=$('#search-results');box.innerHTML='<div class="empty busy-pulse" role="status">근거 검색 중</div>';
 try {
  const result=await api('/api/search?q='+encodeURIComponent($('#query').value));if(ticket!==searchId)return;
  if(!['ready','needs_clarification','no_results'].includes(result.status)||!result.filters||!Array.isArray(result.hits)||!Array.isArray(result.issues)||!Array.isArray(result.missing_fields)||typeof result.blocked!=='boolean'||result.answer_status!=='not_verified')throw Error('검색 조건 응답을 확인하지 못했습니다.');
  const fields={company:'기업',metric:'항목',year:'연도',quarter:'종료 분기',kind:'기간 방식',scope:'범위',currency:'통화',scale:'표시 단위'};
  const fieldValue=(key,value)=>key==='company'?({samsung:'삼성전자',hyundai:'현대자동차'}[value]||value):key==='metric'?(labels[value]||value):key==='quarter'?`${value}분기`:key==='kind'?({quarter:'단독 3개월',ytd:'연초부터 누적'}[value]||value):key==='scope'?({CFS:'연결',OFS:'별도'}[value]||value):key==='scale'?({1:'1',1000:'천 (1,000)',1000000:'백만 (1,000,000)',100000000:'억 (100,000,000)',1000000000:'십억 (1,000,000,000)',1000000000000:'조 (1,000,000,000,000)'}[value]||value):value;
  const issueLabel=code=>{
   if(code.startsWith('MISSING_'))return `${fields[code.slice(8).toLowerCase()]||'필수'} 조건을 입력해 주세요.`;
   if(code.startsWith('CONFLICT_'))return `${fields[code.slice(9).toLowerCase()]||'검색'} 조건이 서로 다릅니다. 하나의 조건을 지정해 주세요.`;
   return {UNSUPPORTED_NEGATION:'제외·부정 표현은 해석하지 않습니다. 원하는 조건을 직접 지정해 주세요.',UNSUPPORTED_TERMS:'해석하지 못한 표현이 있습니다. 기업명·통화·단위를 확인해 주세요.',UNSUPPORTED_SCALE:'지원하지 않는 표시 단위입니다. 원문에 적힌 단위를 확인해 주세요.',AMBIGUOUS_FACT:'같은 조건의 근거가 여러 개입니다. 문서와 수치를 직접 확인해 주세요.'}[code]||'검색 조건을 다시 확인해 주세요.';
  };
  const found=result.blocked?[]:result.hits.flatMap(h=>h.fact_ids.map(id=>({f:facts.find(f=>f.id===id),score:h.score}))).filter(x=>x.f);
  const summary={ready:'조건을 갖춘 검색 후보',needs_clarification:'조건 추가 확인 필요',no_results:'검색 결과 없음'}[result.status];
  const detected=Object.entries(fields).filter(([key])=>Object.hasOwn(result.filters,key)).map(([key,label])=>`<span data-search-field="${key}"><strong>${label}</strong> ${esc(fieldValue(key,result.filters[key]))}</span>`).join('');
  const missing=result.missing_fields.map(key=>`<span data-search-missing="${esc(key)}">${esc(fields[key]||key)}</span>`).join(' · ');
  const diagnostics=`<section class="finding" aria-label="검색 조건 확인" data-search-status="${result.status}"><h2>${summary}</h2><p class="calculation-note">검색 후보 · 검증된 답변 아님. 선택한 후보는 작업지에서 기간·범위·통화·출처를 다시 대조합니다.</p><h3>입력에서 확인한 조건</h3><div class="context-checks">${detected||'<span>확인된 조건 없음</span>'}</div>${missing?`<p class="warn">추가할 조건: ${missing}</p>`:''}${result.issues.map(code=>`<div class="finding-issue">${esc(issueLabel(code))}</div>`).join('')}${result.unknown_terms?.length?`<p class="calculation-note">확인이 필요한 표현: ${result.unknown_terms.map(esc).join(' · ')}</p>`:''}${result.status==='needs_clarification'&&!result.blocked?'<p class="calculation-note">아래 후보는 입력한 조건만 일치합니다. 빠진 조건을 입력하면 다시 좁힐 수 있습니다.</p>':''}</section>`;
  box.innerHTML=diagnostics+(found.length?`<div class="table-overflow"><table class="search-results-table"><thead><tr><th>후보 수치 항목</th><th>기간 · 범위</th><th>금액</th><th>문서</th><th>작업</th></tr></thead><tbody>${found.map(({f})=>`<tr><td>${labels[f.metric]}<small>${esc(f.row)}</small></td><td>${f.start} — ${f.end}<small>${f.months}개월 · ${scope(f)}</small></td><td class="num">${money(f)}<small>${unit(f)}</small></td><td>${docTitle(f.document_id)}<small>p.${f.page} · ${esc(f.column)}</small></td><td><button class="link-button" data-use-fact="${esc(f.id)}">후보를 작업지에서 대조 ↗</button></td></tr>`).join('')}</tbody></table></div>`:'<div class="empty">검색 결과 없음 · 위 조건과 수집된 문서 범위를 확인해 주세요.</div>');
  box.querySelectorAll('[data-use-fact]').forEach(b=>b.onclick=async()=>{
   if(busy||!ready)return;const f=facts.find(f=>f.id===b.dataset.useFact),request=selection();
   request.current={document:f.document_id,year:Number(f.start.slice(0,4)),scope:f.scope,period:f.months===3?'q':'ytd',currency:f.currency};
   setSelection(request);selectedMetric=f.metric;selectedSide='current';view('work');await execute(false);
  });
 }catch(e){if(ticket===searchId)box.innerHTML=`<div class="error-message" role="alert">${esc(errorText(e))} · 연결 복구 후 재검색</div>`;}
};
selectors();
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
$('#reset-btn').onclick=()=>{setSelection(defaults);selectedMetric='revenue';selectedSide='current';execute(false);};
$('#run-btn').onclick=()=>execute(true);$('#trace-btn').onclick=openTrace;$('#close-trace').onclick=()=>$('#trace-dialog').close();
$('#download-btn').onclick=()=>current&&download(current,`quarterguard-worksheet-${current.run_id}.json`);
$('#boot-retry').onclick=boot;
$('#settings-btn').onclick=()=>settings($('#comparison-settings').hidden);
$('#settings-close').onclick=()=>{settings(false);$('#settings-btn').focus();};
$('#review-note').oninput=()=>{noteDirty=true;$('#note-status').textContent='작성 중 · 항목을 바꾸면 자동 저장됩니다.';};
$('#review-note').onblur=()=>{if(noteDirty)saveNote();};
$('#save-note').onclick=saveNote;
$('#retry-note').onclick=()=>{
 if(busy||!current?.workflow_success)return;
 if(noteDirty)saveNote();
 current.rows.forEach(row=>getNote(row,current.selection.mode));
 noteKey=null;bindNote(current.rows.find(row=>row.metric===selectedMetric));
};
$('#mark-reviewed').onclick=()=>{if(!noteRecord||busy)return;noteRecord={...noteRecord,reviewed:!noteRecord.reviewed};saveNote();$('#mark-reviewed').setAttribute('aria-pressed',String(noteRecord.reviewed));$('#mark-reviewed').textContent=noteRecord.reviewed?'확인함':'확인 표시';};
$('#export-btn').onclick=()=>{
 if(busy||!current?.workflow_success||!current?.rows?.length||unreadableCurrent())return;
 if(noteDirty)saveNote();
 const text=csvText(current.rows,current.selection.mode,getNote,labels),href=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');
 a.href=href;a.download=`quarterguard-review-${new Date().toISOString().slice(0,10)}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(href),1000);
};
boot();
mountProviders($('#provider-content'));
mountHeldout($('#heldout-content'));

mountProgress(document.querySelector('#current-evaluation-content'));
