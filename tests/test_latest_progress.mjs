import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {renderLatestProgress} from '../web/latest-progress.js';
import {renderHistoricalProgress} from '../web/progress.js';
const summary=JSON.parse(fs.readFileSync(new URL('../data/latest-progress-20261110.json',import.meta.url)));
const history=JSON.parse(fs.readFileSync(new URL('../artifacts/progress-v2-final.json',import.meta.url)));
test('current closeout shows completed human work and separates fresh generation from replay',()=>{
 const current=JSON.parse(fs.readFileSync(new URL('../data/latest-progress-closeout-20261112.json',import.meta.url)));
 const html=renderLatestProgress({summary:current,runtime_commit:'closeout123'});
 for(const value of ['SK 5개 + Apple 7개','참 11·거짓 4·모호 5','A7·S4 JSON 다운로드·내용 대조 완료','10건 통과','사람 참 차단 1건','새 유료 호출 0회','테스트 6개'])assert.ok(html.includes(value),value);
 for(const value of ['질문·정답은 아직 미수신','새 b 검수는 대기'])assert.ok(!html.includes(value),value);
 const bad=structuredClone(current);bad.current_status.fresh_batch_status='<script>alert(1)</script>';
 assert.ok(!renderLatestProgress({summary:bad}).includes('<script>'));
});
test('fresh paid batch displays poorer gate result without inventing human approval',()=>{
 const current=JSON.parse(fs.readFileSync(new URL('../data/latest-progress-closeout-live-20261112.json',import.meta.url)));
 const html=renderLatestProgress({summary:current,runtime_commit:'newrun'});
 for(const value of ['새 실제 생성 20건','8/20','12건 보류','0.0189500','이번 응답의 사람 판정은 아직 없습니다'])assert.ok(html.includes(value),value);
 assert.ok(!html.includes('별도 승인 대기'));
});
test('final human review is visible with remaining overblocking and no new generation claim',()=>{
 const current=JSON.parse(fs.readFileSync(new URL('../data/latest-progress-final-human-20261113.json',import.meta.url)));
 const html=renderLatestProgress({summary:current,runtime_commit:'final'});
 for(const value of ['참 17·모호 3·거짓 0','당시 제품 검사 8/20','7/20','참 10건','모호 3건','합의한 세 가지 보완 완료'])assert.ok(html.includes(value),value);
 assert.ok(!html.includes('이번 응답의 사람 판정은 아직 없습니다'));
 assert.ok(!html.includes('검수 대기'));
 assert.ok(!html.includes('마지막 코드 수정 후 새 생성'));
});
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

test('confirmed v5 human verdicts do not become an overall accuracy improvement',()=>{
 const current=structuredClone(summary);
 current.llm.latest_guard_batch={calls:8,structured_exact:8,previous_structured_exact:7,automatic_flagged:7,estimated_cost_usd:'0.01510425',human_reviewed:true,human_verdict_counts:{'참':6,'모호':1,'거짓':1},human_review_link:'docs/validation-kit/session-b-v5-20261110.md',link:'docs/llm-guards-v5-results-20261110.md'};
 const html=renderLatestProgress({summary:current,runtime_commit:'current'});
 for(const text of ['참 6·모호 1·거짓 1','기존 b의 후속 검수','전체 설명의 개선으로 해석하지 않습니다'])assert.ok(html.includes(text),text);
 assert.ok(!html.includes('새 응답의 사람 검수는 미수행'));
 assert.ok(html.includes('참 5·모호 3 → 참 7·모호 1'));
});

test('v6 separates structural regression, new tasks, and still-pending human review',()=>{
 const current=structuredClone(summary);
 current.llm.prose_batch={calls:16,previous_structured_exact:8,paired:{structured_exact:3,production_gate_passed:3},new_tasks:{structured_exact:5,production_gate_passed:4},estimated_cost_usd:'0.03177450',human_reviewed:false,link:'docs/llm-prose-v6-results-20261110.md',review_link:'docs/validation-kit/llm-prose-v6-actual-20261110.md'};
 const html=renderLatestProgress({summary:current,runtime_commit:'current'});
 for(const text of ['v6 새 16회','8/8 → 3/8','새 과제: 구조 5/8','제품 검사 4/8','새 응답의 사람 검수는 미수행','value','부정문','0.03177450'])assert.ok(html.includes(text),text);
 assert.ok(html.includes('참 5·모호 3 → 참 7·모호 1'));
});
