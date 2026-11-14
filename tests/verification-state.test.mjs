import test from 'node:test';
import assert from 'node:assert/strict';
import {canRetainTable} from '../web/verification-state.mjs';
const selection={mode:'qoq',current:{document:'s24q3',year:2024,scope:'CFS',period:'q',currency:'KRW'},base:{document:'s24q2',year:2024,scope:'CFS',period:'q',currency:'KRW'}};
const previous={workflow_success:true,rows:[{}],selection};
test('only successful same-condition live reverification retains the table',()=>{
 assert.equal(canRetainTable(true,previous,structuredClone(selection)),true);
 for(const old of [null,{...previous,workflow_success:false},{...previous,rows:[]},{...previous,selection:null}]) assert.equal(canRetainTable(true,old,selection),false);
 assert.equal(canRetainTable(false,previous,selection),false);
});
test('every financial context change clears the old table',()=>{
 for(const side of ['current','base']) for(const key of ['document','year','scope','period','currency']) {
  const changed=structuredClone(selection);changed[side][key]='different';
  assert.equal(canRetainTable(true,previous,changed),false,`${side}.${key}`);
 }
 assert.equal(canRetainTable(true,previous,{...selection,mode:'yoy'}),false);
});
