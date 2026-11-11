import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {appleCards,renderAppleReview,validateAppleCell} from '../web/apple-review.js';
const evidence=JSON.parse(fs.readFileSync(new URL('../data/apple-source/evidence.json',import.meta.url))).cells;
test('Apple cards preserve USD, fiscal dates, printed HTML location and signed outflows',()=>{
 const c=evidence.find(c=>c.metric==='capex_payment'&&c.year===2024);
 const html=appleCards([{cell:c}]);assert.match(html,/-9,447/);assert.match(html,/백만 미국 달러/);assert.match(html,/52주/);assert.match(html,/인쇄 33쪽/);assert.match(html,/PDF 쪽수 아님/);
});
test('wrong unit, scope, origin and link reject before render',()=>{
 for(const change of [{currency:'KRW'},{scale:1},{scope:'OFS'},{source_url:'https://evil.example'},{source_locator:'#<script>'}])assert.throws(()=>validateAppleCell({...evidence[0],...change}));
});
test('raw source row labels are escaped',()=>assert.match(appleCards([{cell:{...evidence[0],row:'<script>alert(1)</script>'}}]),/&lt;script&gt;/));
test('stale review cannot render for new question',()=>assert.throws(()=>renderAppleReview({document_id:'apple-2024-10k',query:'old'},'new')));
