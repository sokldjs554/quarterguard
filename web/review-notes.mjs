const empty = () => ({note:'', reviewed:false, updated_at:null});
export function reviewKey(row, mode) {
 return 'quarterguard-review-v1:' + JSON.stringify([mode, row.metric, ...[row.current,row.base].flatMap(f=>[f.id,f.document_sha256])]);
}
function clean(value) {
 if (!value || typeof value !== 'object') return empty();
 return {note:typeof value.note==='string'?value.note.slice(0,2000):'', reviewed:value.reviewed===true, updated_at:typeof value.updated_at==='string'?value.updated_at:null};
}
export function readReview(storage, key) {
 const raw=storage.getItem(key);
 try {return clean(JSON.parse(raw));} catch {return empty();}
}
export function writeReview(storage, key, value) {
 const record=clean(value);
 storage.setItem(key,JSON.stringify(record));
 return record;
}
function cell(value) {
 let text=String(value??'');
 // Keep numeric data numeric, but neutralize spreadsheet formulas in text.
 if (/^[\s]*[=+@-]/.test(text) && !/^-?\d+(\.\d+)?$/.test(text)) text="'"+text;
 return '"'+text.replaceAll('"','""')+'"';
}
export function csvText(rows, mode, getReview, labels) {
 const headings=['항목','비교 방식','A 값','A 통화','A 배율','A 시작','A 종료','A 범위','A 문서','A 페이지','A 출처','B 값','B 통화','B 배율','B 시작','B 종료','B 범위','B 문서','B 페이지','B 출처','자동 판정','거부 사유','증감률(%)','개인 확인','메모'];
 const fact=f=>[f.value,f.currency,f.scale,f.start,f.end,f.scope,f.document_id,f.page,f.source_url];
 return '\uFEFF'+[headings,...rows.map(row=>{
  const note=getReview(row,mode);
  return [labels[row.metric]||row.metric,mode,...fact(row.current),...fact(row.base),row.result.status,(row.result.issues||[]).join(' | '),row.result.growth_pct??'',note.reviewed?'수동 확인':'미확인',note.note];
 })].map(row=>row.map(cell).join(',')).join('\r\n')+'\r\n';
}
