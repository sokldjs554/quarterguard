import {$,esc,labels,money,unit,scope,docTitle,issues} from './shared.js';
import {chartModel} from './finance-chart.mjs';
let active=null,inspect=null;
const range=f=>`${f.start.slice(0,7).replace('-','.')}–${f.start.slice(0,4)===f.end.slice(0,4)?f.end.slice(5,7):f.end.slice(0,7).replace('-','.')}`;
function chartHTML(row) {
 const m=chartModel(row);
 if(!m)return `<div class="chart-hold"><strong>계산·비교 그래프 보류</strong><p>${row.result.issues.map(code=>esc(issues[code]?.[1]||'비교 조건을 확인하세요.')).join(' ')||'비교할 수 있는 수치를 확인하세요.'}</p><button class="secondary" data-finance-settings>비교 조건 수정 →</button></div>`;
 // Shared zero baseline supports negative values; no synthetic time series.
 const left=24,right=250,axis=v=>left+(v-m.min)/(m.max-m.min)*(right-left),zero=axis(0);
 let svg=`<line x1="${zero}" x2="${zero}" y1="5" y2="62" stroke="#bac6d8"/><text x="${zero}" y="77" text-anchor="middle" font-size="8" fill="#718198">0</text>`;
 for(const [side,y] of [['current',15],['base',43]]) {
  const bar=m.bars.find(x=>x.side===side),x=axis(bar.value),label=side==='current'?'A':'B';
  svg+=`<text x="0" y="${y+8}" font-size="10" fill="#6f8097">${label}</text><rect x="${left}" y="${y}" width="${right-left}" height="8" fill="#f4f6fa"/><rect x="${Math.min(zero,x)}" y="${y}" width="${Math.abs(x-zero)}" height="8" fill="${side==='current'?'#d6b56d':'#9aa8c2'}"/><text x="350" y="${y+8}" text-anchor="end" font-size="10" fill="#4e617d">${esc(money(bar.fact))}</text>`;
 }
 return `<svg class="finance-bars" viewBox="0 0 350 80" role="img" aria-label="${esc(labels[row.metric])}: A ${esc(money(row.current))}, B ${esc(money(row.base))} ${esc(unit(row.current))}. 두 막대에 같은 축과 0 기준 적용.">${svg}</svg>`;
}
export function renderFinance(row,mode) {
 active=row;const a=row.current,b=row.base,r=row.result,ok=r.status==='verified'&&r.issues.length===0&&r.growth_pct!=null;
 const growth=(Number(r.growth_pct)>0?'+':'')+esc(r.growth_pct)+'%',basis=mode==='qoq'?'전분기 대비':'전년 동기 대비';
 $('#comparison-overview').replaceChildren();$('#comparison-chart').hidden=false;
 $('#comparison-chart').innerHTML=`<div class="inspection-head"><h2><small>선택 항목 검토</small>${esc(labels[row.metric])}</h2><span>${esc(unit(a))}</span></div><div class="inspection-body"><div class="finance-plot">${ok?`<p class="chart-period">${esc(range(b))} → ${esc(range(a))}</p><div class="chart-growth"><strong>${growth}</strong><span>${basis}</span></div>`:''}${chartHTML(row)}${ok?`<p class="chart-formula">(${money(a)} ÷ ${money(b)} − 1) × 100 = ${esc(r.growth_pct)}%</p>`:''}</div>${[['current',a],['base',b]].map(([side,f])=>`<section class="workbook-source"><div class="workbook-source-label"><span class="heading-letter">${side==='current'?'A':'B'}</span>${side==='current'?'기준':'비교'} 수치의 근거</div><h3>${esc(docTitle(f.document_id))}</h3><p>${esc(range(f))} / ${f.months}개월 · ${scope(f)}</p><p>PDF ${f.page}쪽 · ${esc(f.row)}<br>${esc(f.column)} · ${esc(unit(f))}</p><button data-finance-source="${side}">해당 수치의 출처 확인 ↗</button></section>`).join('')}</div><div class="inspection-decision ${ok?'':'hold'}">${ok?'✓ 조건 일치 · 기업 · 항목 · 기간 · 연결 범위 · 통화 · 단위를 대조했습니다.':'! 계산 보류 · '+r.issues.map(x=>esc(issues[x]?.[0]||'조건 확인 필요')).join(' · ')}</div>`;
 $('#comparison-chart').querySelectorAll('[data-finance-source]').forEach(b=>b.onclick=()=>openFinanceSources(b.dataset.financeSource));
 $('#comparison-chart').querySelector('[data-finance-settings]')?.addEventListener('click',()=>{$('#settings-btn').click();$('#comparison-settings').scrollIntoView({block:'center'});});
 $('#finance-source-btn').disabled=false;
}
export function clearFinance() {active=null;$('#comparison-chart').replaceChildren();$('#comparison-chart').hidden=true;$('#finance-source-btn').disabled=true;$('#finance-source-dialog').close();$('#finance-source-content').replaceChildren();}
export function openFinanceSources(side) {
 if(!active)return;
 const sides=side?[side]:['current','base'];
 $('#finance-source-title').textContent=labels[active.metric]+' · 원문 근거';
 $('#finance-source-content').innerHTML=`<p class="drawer-intro">선택한 공시 수치의 출처 정보입니다.</p>`+sides.map(s=>{const f=active[s];return `<section class="finance-source-box"><h3>${s==='current'?'A 기준':'B 비교'} · ${esc(docTitle(f.document_id))}</h3><strong>${money(f)} <small>${esc(unit(f))}</small></strong><dl><dt>실제 기간</dt><dd>${f.start} ~ ${f.end}</dd><dt>범위</dt><dd>${f.months}개월 · ${scope(f)}</dd><dt>통화·단위</dt><dd>${esc(f.currency)} · ${esc(unit(f))}</dd><dt>PDF 위치</dt><dd>${f.page}쪽</dd><dt>원문 행</dt><dd>${esc(f.row)}</dd><dt>선택 열</dt><dd>${esc(f.column)}</dd></dl><a href="${esc(f.source_url)}#page=${f.page}" target="_blank" rel="noopener">발행사 원문 PDF 열기 ↗</a><button class="secondary" data-inspect-side="${s}">근거표·원문 보기 →</button></section>`;}).join('')+'<p class="drawer-intro">수집한 출처 정보이며 원문 이미지가 아닙니다. 발행사 PDF에서 표 제목·행·열을 확인하세요.</p>';
 $('#finance-source-content').querySelectorAll('[data-inspect-side]').forEach(b=>b.onclick=()=>{const side=b.dataset.inspectSide;$('#finance-source-dialog').close();inspect(side);});
 $('#finance-source-dialog').showModal();
}
export function mountFinanceSources(onInspect) {inspect=onInspect;$('#finance-source-close').onclick=()=>$('#finance-source-dialog').close();$('#finance-source-btn').onclick=()=>openFinanceSources();window.addEventListener('resize',()=>{if(active){const plot=$('#comparison-chart .finance-plot');if(plot){const holder=document.createElement('div');holder.innerHTML=chartHTML(active);const old=plot.querySelector('.finance-bars');if(old)old.replaceWith(holder.firstElementChild);}}});}
