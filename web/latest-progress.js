import {esc} from './shared.js';
const repo='https://github.com/sokldjs554/quarterguard/blob/main/';
const link=(path,label)=>`<a href="${repo}${esc(path)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
const fraction=x=>`${x.passed}/${x.total}`;
export function renderLatestProgress(envelope) {
 const s=envelope.summary;
 if(s?.schema_version!==1||!s.source_sha256)throw Error('INVALID_LATEST_SUMMARY');
 const h=s.hyundai,b=s.human_review,l=s.llm,p=s.personal_review,v=s.verification,g=l.latest_guard_batch;
 return `<section id="latest-evidence-summary" aria-label="최신 근거 요약"><h2>최신 근거 요약 · ${esc(s.as_of_kst)} KST 기준</h2>
 <p class="scope-notice">공개 작업지: 삼성전자 ${s.production.year}년 문서 ${s.production.documents}건 · 정본 ${s.production.facts}개. 평가에서 새로 처리한 문서는 작업지에 자동 등록되지 않습니다.</p>
 <div class="table-overflow"><table class="evaluation-table"><thead><tr><th>항목</th><th>확인한 결과</th><th>범위와 남은 한계</th></tr></thead><tbody>
 <tr><td>현대자동차 원문 평가</td><td>2025년 3분기 표: 수치·출처 ${fraction(h.raw_cells)}, 질의 ${fraction(h.raw_queries)}, 계산 ${fraction(h.raw_calculations)}. ${link(h.link,'첫 실패·수정·최종 평가')}</td><td>실제 PDF부터 처리한 격리 평가입니다. 비교연도 8개 값은 앞선 자료와 겹칩니다. 현대차는 공개 작업지에 미등록이며, 2024 첫 실패도 보존했습니다.</td></tr>
 <tr><td>사람의 부분 검수</td><td>같은 b가 지정 셀 ${b.cells}개·질의 ${b.queries}개를 대조했습니다. 삼성 4개는 이미지로도 후속 확인했습니다. ${link(b.gold_link,'검수 범위')}</td><td>금융 분야 경력 3년인 친구 1명의 보고입니다. 전체 평가셋·현대2025 정답·회사 공식 검수로 확대하지 않습니다.</td></tr>
 <tr><td>LLM 실제 생성과 재검수</td><td>기존 GPT ${l.historical_gpt_calls}회와 별도로 ${g?'앞선 두 배치에서 ':''} ${l.calls_per_batch.join('회 + ')}회 실행. 설명 판정 참 ${b.baseline['참']}·모호 ${b.baseline['모호']} → 참 ${b.followup['참']}·모호 ${b.followup['모호']}. 구조 필드 ${l.structured_exact[0]}/8 → ${l.structured_exact[1]}/8. ${link(l.link,'실호출 원응답')} · ${link(b.link,'b의 재확인')}</td><td>같은 개발 8건, GPT-5.4 mini 평가입니다. YoY 근거 ID 오타와 범위 설명의 모호함을 보존했습니다. 일반 정확도 향상으로 해석하지 않습니다.</td></tr>
 ${g?`<tr><td>최근 설명·인용 방어 · 실호출</td><td>v5 새 ${esc(g.calls)}회. 구조 필드 ${esc(g.previous_structured_exact)}/8 → ${esc(g.structured_exact)}/8. 추정 비용 $${esc(g.estimated_cost_usd)} · 청구액 미조회. ${link(g.link,'실제 응답과 남은 문제')}</td><td>새 응답의 사람 검수는 미수행입니다. 근거가 있는데 검색 부재처럼 읽히는 문장, 증가율 % 누락, 영어 내부 표현은 재검토 대상입니다. 자동 경고 ${esc(g.automatic_flagged)}/8은 오류율이 아닙니다. ${link(g.review_link,'새 응답 검수 자료')}</td></tr>`:`<tr><td>최근 설명·인용 방어</td><td>도구의 보류 이유 안내, 요청별 ID 제한, 정확한 순서 대조, 실패한 설명 제거를 보강했습니다. ${link(l.guard_link,'구현·회귀')}</td><td>이 마지막 변경은 오프라인 회귀 검증입니다. 변경 후 새 실호출·b 재검수는 아직 없습니다. 공개 API 사용 가능 여부는 아래 연결 상태에서 따로 확인하세요.</td></tr>`}
 <tr><td>본인 코드 검토·실행</td><td>기간 테스트 ${p.period_tests}개와 DART 테스트 ${p.dart_tests}개, 합계 ${p.added_tests}개를 직접 보강·실행·커밋했습니다. ${link(p.period_link,'기간 기록')} · ${link(p.dart_link,'DART 기록')}</td><td>본인이 보고한 당시 전체 ${p.reported_full_suite}개와 AI의 통합 검사를 구분합니다. AI 도움 범위를 기록했으며 파서 개인 추가 실행·독립 개발 전체의 증거는 아닙니다.</td></tr>
 <tr><td>참여와 고객 환경</td><td>a: 작성자 시연을 본 대학생의 의견. b: 금융 분야 친구의 직접 과제·후속 검수. ${link(s.participants.a_link,'a 기록')} · ${link(s.participants.b_link,'b 기록')}</td><td>외부 참여자는 ${s.participants.unique_external_people}명이며 같은 b의 후속을 새 사람으로 세지 않습니다. 금융기관 고객 환경 배포 ${s.participants.customer_environment_deployments}건.</td></tr>
 </tbody></table></div>
 <p class="review-caption">공개 API 사용 가능 여부는 아래 연결 상태에서 따로 확인하세요. 실호출 평가는 GPT-5.4 mini이며 공개 제품의 GPT-4.1 mini와 구분합니다.</p>
 <p class="review-caption">직전 기능 변경(${esc(v.code_commit.slice(0,7))}) 검증: Python ${v.python_tests}개 · Node ${v.node_tests}개 · 로컬 브라우저 재생 ${v.browser_replay_checks}개 · 실제 MCP ${v.actual_mcp_cases}개 사례 통과. 실행 주체는 AI입니다. 물리 휴대폰·새 LLM 응답 검증으로 바꾸어 세지 않습니다. ${link(v.link,'당시 검사 기록')}</p>
 <p class="review-caption">요약 근거 기준 ${esc(s.evidence_basis_commit.slice(0,7))} · 현재 서버 ${esc(envelope.runtime_commit?.slice(0,7)||'확인 불가')}. 현재 서버 커밋이 모든 과거 평가의 실행 커밋이라는 뜻은 아닙니다. <a href="/api/evaluation/latest" target="_blank" rel="noopener">요약·근거 해시 JSON ↗</a></p></section>`;
}
