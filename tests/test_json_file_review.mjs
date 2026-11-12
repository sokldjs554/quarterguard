import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {inspectSavedJSON} from '../web/json-file-review.js';
const root='../artifacts/final-export-check-20261112/public-fixed/browser/';
const apple=JSON.parse(fs.readFileSync(new URL(root+'A7-390.json',import.meta.url)));
const sk=JSON.parse(fs.readFileSync(new URL(root+'S4-390.json',import.meta.url)));
test('real A7 export retains question, source location and withholding on reopen',()=>{
 const r=inspectSavedJSON(JSON.stringify(apple),apple);
 assert.equal(r.match,true);assert.match(r.summary,/판매량 감소/);assert.match(r.summary,/인쇄 22/);assert.match(r.summary,/USD/);assert.match(r.summary,/CAUSAL_DECOMPOSITION_REQUIRED/);
});
test('real S4 export retains both inputs, source locations and no computed ratio',()=>{
 const r=inspectSavedJSON(JSON.stringify(sk),sk);
 assert.equal(r.match,true);assert.match(r.summary,/13313937/);assert.match(r.summary,/32765719/);assert.match(r.summary,/F-73/);assert.match(r.summary,/F-75/);assert.match(r.summary,/RATIO_DEFINITION_REQUIRED/);assert.equal(r.value.growth_pct,null);
});
test('whitespace and object key order do not imply different JSON values',()=>{
 const reordered=Object.fromEntries(Object.entries(apple).reverse());
 assert.equal(inspectSavedJSON('\uFEFF'+JSON.stringify(reordered,null,3),apple).match,true);
});
test('changed question, amount, missing field, extra field and evidence order differ',()=>{
 const changes=[{...apple,query:'other'},{...apple,evidence:[{...apple.evidence[0],value:'1'},apple.evidence[1]]},{...apple,scale:undefined},{...apple,extra:'new'},{...apple,evidence:[...apple.evidence].reverse()}];
 for(const value of changes)assert.equal(inspectSavedJSON(JSON.stringify(value),apple).match,false);
});
test('without a current result, a readable file is not claimed to match',()=>assert.equal(inspectSavedJSON(JSON.stringify(sk),null).match,null));
test('malformed, oversized, unsupported and excessively nested files fail',()=>{
 for(const text of ['{','null','[]','{}',' '.repeat(1048577),JSON.stringify({...apple,messages:'wrong'}),JSON.stringify({...apple,nest:JSON.parse('['.repeat(70)+'0'+']'.repeat(70))})])assert.throws(()=>inspectSavedJSON(text,apple));
});
test('all loaded strings remain literal data including HTML and script-like URLs',()=>{
 const value={...apple,messages:['<img src=x onerror=alert(1)>'],evidence:[{...apple.evidence[0],source_url:'javascript:alert(1)'}]};
 const r=inspectSavedJSON(JSON.stringify(value),apple);
 assert.equal(r.match,false);assert.match(r.summary,/<img src=x/);assert.match(r.summary,/javascript:alert/);
});
test('unsafe numeric values cannot be silently rounded into a match',()=>assert.throws(()=>inspectSavedJSON(JSON.stringify(apple).replace('"scale":1000000','"scale":9007199254740993'),apple)));
