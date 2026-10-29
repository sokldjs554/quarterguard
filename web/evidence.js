import {esc, labels, money, scope, unit, docTitle} from './shared.js';

export function evidenceInspector(root, facts, sources, onSelect) {
 let selected = null, pair = [], mode = 'table', selectedIndex = 0;
 function show(fact, related = [], index = 0) { selected = fact; pair = related; selectedIndex = index; mode = 'table'; render(); }
 function render() {
  if (!selected) return;
  const f = selected, source = sources.find(s => s.id === f.document_id);
  const href = `${source.url}#page=${f.page}`;
  const cols = [{year:2024,months:3},{year:2023,months:3},{year:2024,months:source.quarter*3},{year:2023,months:source.quarter*3}];
  const sourceFacts = facts.filter(x => x.document_id === f.document_id && x.scope === f.scope && x.currency === f.currency);
  const metrics = Object.keys(labels);
  root.innerHTML = `
   <div class="source-switcher" aria-label="계산 근거 선택">${pair.map((x,i) => `<button data-source-id="${esc(x.id)}" data-source-index="${i}" class="${i===selectedIndex?'active':''}" aria-pressed="${i===selectedIndex}">${i===0?'A 기준':'B 비교'} · p.${x.page}</button>`).join('')}</div>
   <div class="source-header"><h3>${docTitle(f.document_id)}</h3><p>삼성전자 · ${scope(f)} 손익계산서 · PDF p.${f.page}</p></div>
   <div class="source-tools"><div class="source-tabs" aria-label="근거 표시 방식"><button data-source-mode="table" class="${mode==='table'?'active':''}" aria-pressed="${mode==='table'}">근거표</button><button data-source-mode="pdf" class="${mode==='pdf'?'active':''}" aria-pressed="${mode==='pdf'}">원문 PDF</button></div><a href="${esc(href)}" target="_blank" rel="noopener" id="publisher-link">발행사 원문 ↗</a></div>
   ${mode==='table' ? `
    <div class="document-paper"><div class="paper-title">${scope(f)} 손익계산서 · 추출 수치</div><div class="paper-subtitle">표시 단위: ${unit(f)} · 보고서 기준 ${source.report_end}</div>
     <div class="paper-rule source-table-scroll" tabindex="0" aria-label="문서 근거표 가로 스크롤"><table class="source-table"><thead><tr><th scope="col">원문 항목</th>${cols.map(c=>`<th scope="col">${c.year}<span>${c.months}개월 ${c.months===3?'분기':'누적'}</span></th>`).join('')}</tr></thead><tbody>${metrics.map(metric => {
      const row = sourceFacts.filter(x=>x.metric===metric), name=row[0]?.row||metric;
      return `<tr class="${metric===f.metric?'source-selected':''}"><td>${esc(name)}</td>${cols.map(c=>{
       const cell=row.find(x=>x.start.startsWith(String(c.year))&&x.months===c.months);
       return `<td class="${cell?.id===f.id?'chosen-cell':''}">${cell?`<span>${money(cell)}</span>`:'—'}</td>`;
      }).join('')}</tr>`;
     }).join('')}</tbody></table></div>
     <div class="paper-caption"><span>수집 수치로 재구성한 표<br>원문 이미지 아님 · 정확한 배치는 PDF 참조</span><b>${f.page}</b></div>
    </div>` : `<p class="pdf-notice">발행사 PDF 직접 표시 · 외부 연결 또는 브라우저에서 표시가 제한되면 <a href="${esc(href)}" target="_blank" rel="noopener">새 탭의 원문</a>을 이용하세요. 근거표로 돌아가도 수치 검토를 계속할 수 있습니다.</p><iframe class="pdf-frame" title="${esc(docTitle(f.document_id))} 원문 PDF ${f.page}페이지" src="${esc(href)}" referrerpolicy="no-referrer"></iframe>`}
   <div class="selected-location"><strong>${esc(f.row)} → ${esc(f.column)} · ${money(f)} ${unit(f)}</strong>${f.start} — ${f.end} · ${f.months}개월 · ${scope(f)}</div>
   ${f.currency==='USD'?`<p class="source-warning">참고 환산액 · KRW ${esc(f.translation_rate)}/USD<br>환산 주석 p.${f.translation_note_page} · 보고서 간 산술 비교 제한</p>`:''}
   <details class="source-provenance"><summary>수집·출처 정보</summary><dl><dt>수치 ID</dt><dd>${esc(f.id)}</dd><dt>문서 SHA-256</dt><dd>${esc(f.document_sha256)}</dd><dt>자료 확인</dt><dd>${esc(source.accessed)}</dd></dl></details>`;
  root.querySelectorAll('[data-source-id]').forEach(b => b.onclick = () => { const index=b.dataset.sourceIndex;onSelect(b.dataset.sourceId,Number(index));root.querySelector(`[data-source-index="${index}"]`)?.focus({preventScroll:true}); });
  root.querySelectorAll('[data-source-mode]').forEach(b => b.onclick = () => { mode=b.dataset.sourceMode;render();root.querySelector(`[data-source-mode="${mode}"]`)?.focus({preventScroll:true}); });
 }
 return {show,clear(){selected=null;root.innerHTML='<div class="empty">현재 설정의 근거 없음</div>';}};
}
