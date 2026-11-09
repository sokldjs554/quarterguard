import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {renderLatestProgress} from '../web/latest-progress.js';
import {renderHistoricalProgress} from '../web/progress.js';
const summary=JSON.parse(fs.readFileSync(new URL('../data/latest-progress-20261110.json',import.meta.url)));
const history=JSON.parse(fs.readFileSync(new URL('../artifacts/progress-v2-final.json',import.meta.url)));
test('current evidence separates product scope, reviewed responses, latest guard, and actors',()=>{
 const html=renderLatestProgress({summary,runtime_commit:'abcdef123'});
 for(const text of ['최신 근거 요약','현대차는 공개 작업지에 미등록','참 5·모호 3 → 참 7·모호 1','8/8 → 7/8','변경 후 새 실호출·b 재검수는 아직 없습니다','직전 기능 변경(f5377ad)','실행 주체는 AI','현재 서버 abcdef1'])assert.ok(html.includes(text),text);
 assert.ok(html.includes('8회 + 8회'));
 assert.ok(html.includes('합계 5개'));
});
test('historical failures are dated and never relabeled as current status',()=>{
 const html=renderHistoricalProgress(history);
 assert.ok(html.includes('2026-10-31 당시 평가 · 보존본'));
 assert.ok(html.includes('당시 현대자동차 표는 미지원이었습니다'));
 assert.ok(html.includes('프로젝트 전체 누계 아님'));
 assert.ok(html.includes('현재 상태가 아닙니다'));
 assert.ok(html.includes('사용자 참여·고객 배포·본인 코드 검토는 미수행'));
});
test('malformed current summary fails and text is escaped',()=>{
 assert.throws(()=>renderLatestProgress({summary:{}}));
 const copy=structuredClone(summary);copy.as_of_kst='<img src=x>';
 const html=renderLatestProgress({summary:copy,runtime_commit:'<script>'});
 assert.ok(!html.includes('<img'));assert.ok(!html.includes('<script>'));
});

test('latest model batch is separate from prior human labels and has unresolved prose warnings',()=>{
 const current=structuredClone(summary);
 current.llm.latest_guard_batch={calls:8,structured_exact:8,previous_structured_exact:7,automatic_flagged:7,estimated_cost_usd:'0.01510425',human_reviewed:false,link:'docs/llm-guards-v5-results-20261110.md',review_link:'docs/validation-kit/llm-guards-v5-review-20261110.md'};
 const html=renderLatestProgress({summary:current,runtime_commit:'current'});
 for(const text of ['v5 새 8회','7/8 → 8/8','새 응답의 사람 검수는 미수행','0.01510425','근거가 있는데 검색 부재처럼 읽히는 문장'])assert.ok(html.includes(text),text);
 assert.ok(!html.includes('변경 후 새 실호출·b 재검수는 아직 없습니다'));
 assert.ok(html.includes('참 5·모호 3 → 참 7·모호 1'));
});
