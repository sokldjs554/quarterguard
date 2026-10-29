import test from 'node:test';
import assert from 'node:assert/strict';
import {reviewKey, readReview, writeReview, csvText} from '../web/review-notes.mjs';
const fact=(id)=>({id,document_sha256:'hash',value:'100',start:'2024-07-01',end:'2024-09-30',scope:'CFS',currency:'KRW',scale:1000000,page:34,document_id:'s24q3',source_url:'https://example.org/report.pdf'});
const row={metric:'revenue',current:fact('a'),base:fact('b'),result:{status:'verified',growth_pct:'6.7916',issues:[]}};
const store=()=>{const data=new Map();return{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)}};
test('review context includes ordered evidence, mode and document version',()=>{
 const key=reviewKey(row,'qoq');
 assert.notEqual(key,reviewKey({...row,current:row.base,base:row.current},'qoq'));
 assert.notEqual(key,reviewKey(row,'yoy'));
 assert.notEqual(key,reviewKey({...row,base:{...row.base,document_sha256:'new'}},'qoq'));
});
test('review persists only valid fields; damaged storage is ignored',()=>{
 const s=store(),key=reviewKey(row,'qoq');
 writeReview(s,key,{note:'단위 재확인',reviewed:true,updated_at:'2026-10-29T00:00:00Z'});
 assert.equal(readReview(s,key).note,'단위 재확인');assert.equal(readReview(s,key).reviewed,true);
 s.setItem(key,'broken');assert.deepEqual(readReview(s,key),{note:'',reviewed:false,updated_at:null});
 s.setItem(key,JSON.stringify({note:'x',reviewed:'true'}));assert.equal(readReview(s,key).reviewed,false);
});
test('storage write failures propagate so UI cannot claim saved',()=>{
 assert.throws(()=>writeReview({setItem(){throw Error('quota')}},'x',{note:'x',reviewed:false}),/quota/);
});
test('CSV preserves numerical output and separates manual review from automated status',()=>{
 const csv=csvText([row],'qoq',()=>({note:'확인, "원문"\n검토',reviewed:true}),{revenue:'매출액'});
 assert.match(csv,/6.7916/);assert.match(csv,/verified/);assert.match(csv,/수동 확인/);assert.match(csv,/확인, ""원문""\n검토/);assert.match(csv,/https:\/\/example.org\/report.pdf/);
});
test('CSV neutralizes formula-like notes including leading whitespace',()=>{
 for(const note of ['=HYPERLINK("x")',' +SUM(1,2)','@SUM(1,2)','\t=1','-1+2']) {
  const csv=csvText([row],'qoq',()=>({note,reviewed:false}),{});assert.ok(csv.includes('"\''+note.replaceAll('"','""')+'"'));
 }
});
