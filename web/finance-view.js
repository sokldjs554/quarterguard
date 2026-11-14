import {$,esc,labels,money,unit,scope,docTitle,issues} from './shared.js';
import {chartModel} from './finance-chart.mjs';
let active=null,inspect=null;
const range=f=>`${f.start.slice(0,7).replace('-','.')}–${f.start.slice(0,4)===f.end.slice(0,4)?f.end.slice(5,7):f.end.slice(0,7).replace('-','.')}`;
function chartHTML(row) {
 const m=chartModel(row);
 if(!m)return `<div class="chart-hold"><strong>비교 그래프를 보류했습니다.</strong><p>${row.result.issues.map(code=>esc(issues[code]?.[1]||'비교 조건을 확인하세요.')).join(' ')||'비교할 수 있는 수치를 확인하세요.'}</p><button class="secondary" data-finance-settings>비교 조건 수정 →</button></div>`;
 const mobile=innerWidth<=700,w=mobile?340:720,l=mobile?64:90,r=w-20,h=144,top=22;
 const y=v=>h-(v-m.min)/(m.max-m.min)*(h-top),zero=y(0);
 let svg='';
 for(let i=0;i<4;i++){const v=m.min+(m.max-m.min)*i/3,yy=y(v);svg+=`<line x1="${l}" y1="${yy}" x2="${r}" y2="${yy}" stroke="#e8edf1"/><text x="${l-8}" y="${yy+3}" text-anchor="end" font-size="${mobile?8:10}" fill="#788594">${esc(money(Math.round(v)))}</text>`;}
 svg+=`<line x1="${l}" y1="${zero}" x2="${r}" y2="${zero}" stroke="#aebbc6"/>`;
 m.bars.forEach((bar,i)=>{const bw=mobile?52:84,x=l+(r-l)*(i+.5)/2-bw/2,yy=y(bar.value),negative=bar.value<0;svg+=`<rect x="${x}" y="${Math.min(yy,zero)}" width="${bw}" height="${Math.abs(yy-zero)}" rx="2" fill="${bar.side==='current'?'#4e9481':'#d6dee7'}"/><text x="${x+bw/2}" y="${negative?yy+13:yy-7}" text-anchor="middle" font-size="${mobile?10:12}" fill="#435d54">${esc(money(bar.value))}</text><text x="${x+bw/2}" y="178" text-anchor="middle" font-size="${mobile?10:11}" fill="#617180">${esc(range(bar.fact))}</text><text x="${x+bw/2}" y="194" text-anchor="middle" font-size="10" fill="#788594">${bar.side==='current'?'A 기준':'B 비교'} · ${bar.fact.months}개월</text>`;});
 return `<svg class="finance-bars" viewBox="0 0 ${w} 208" role="img" aria-label="${esc(labels[row.metric])}. ${m.bars.map(b=>esc(`${range(b.fact)} ${money(b.fact)} ${unit(b.fact)}`)).join(', ')}. 축에 0 포함.">${svg}</svg>`;
}
export function renderFinance(row,mode) {
 active=row;const a=row.current,b=row.base,r=row.result,ok=r.status==='verified';
 $('#comparison-overview').innerHTML=`<div class="finance-metric"><h2>${esc(labels[row.metric])}<small>${esc(unit(a))}</small></h2><span class="finance-status ${ok?'':'hold'}">${ok?'비교 조건 일치':r.issues.map(x=>esc(issues[x]?.[0]||'확인 필요')).join(' · ')}</span></div><div class="finance-values">${[['A',a],['B',b]].map(([s,f])=>`<div class="finance-value ${s==='B'?'base':''}"><strong>${money(f)}</strong><p>${s} · ${esc(range(f))} / ${f.months}개월 · ${scope(f)} / ${unit(f)}</p></div>`).join('')}<div class="finance-growth ${ok?'':'hold'}"><strong>${ok?(Number(r.growth_pct)>0?'+':'')+esc(r.growth_pct)+'%':'계산 보류'}</strong><span>${ok?(mode==='qoq'?'전분기 대비':'전년 동기 대비'):'비교 조건 확인 필요'}</span></div></div>`;
 $('#comparison-chart').hidden=false;
 $('#comparison-chart').innerHTML=`<div class="finance-plot"><div class="chart-heading"><h3>${esc(labels[row.metric])} 비교</h3><span>단위: ${esc(unit(a))}</span></div>${chartHTML(row)}</div><aside class="finance-sources"><h3>선택 수치의 출처 <small>IR 보고서</small></h3>${[['current',a],['base',b]].map(([side,f])=>`<button data-finance-source="${side}"><span>${esc(docTitle(f.document_id))} ↗</span><small>${side==='current'?'A':'B'} · PDF ${f.page}쪽 · ${esc(f.row)}</small></button>`).join('')}<p>문서명과 실제 비교 기간을<br>함께 확인하세요.</p></aside>`;
 $('#comparison-chart').querySelectorAll('[data-finance-source]').forEach(b=>b.onclick=()=>openFinanceSources(b.dataset.financeSource));
 $('#comparison-chart').querySelector('[data-finance-settings]')?.addEventListener('click',()=>$('#settings-btn').click());
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
