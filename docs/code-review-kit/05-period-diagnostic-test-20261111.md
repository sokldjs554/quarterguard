# 기간 진단 테스트 파일 수신·수량 차이 확인

수신일: **2026-11-11 KST**. 본인이 앞서 보고한 실행의 날짜로 대체하지 않는다. 기준 저장소 `b67f8a4`와 첨부 `test_explanation_contract.py`를 대조했다. 변경은 `Fact` import와 `test_period_diagnostics_are_not_reported_as_tool_execution_history` 메서드1개다. 첨부 파일을 바이트 그대로 반영했다. AI는 검토·재실행·문서 정리·GitHub 통합을 담당했으며 이번 커밋을 본인의 직접 커밋으로 기록하지 않는다.

[제출 파일 해시·역할·실행 기록](../../artifacts/author-diagnostic-test-20261111/submission.json) · [앞선 구현 제출과 미수신 당시 기록](04-period-diagnostic-author-20261110.md) · [테스트 코드](../../tests/test_explanation_contract.py).

## 추가된 검사의 범위

한 메서드 안의 두 `subTest`는 테스트2개가 아니라 메서드1개로 집계한다. 저장된 v6 입력을 평가용 정본 등록과 함께 사용해 `build_context()`의 진단을 확인하고 `compare()`는 실제 로컬 실행한다.

|사례|독립 진단의 실패 조건|실제 compare 결과|
|---|---|---|
|h25-op-period|equal_months, yoy_start_month_day|PERIOD_MISMATCH, growth_pct=None|
|s22-op-qoq|qoq_adjacent|PERIOD_MISMATCH, growth_pct=None|

`diagnostic_origin == independent_recalculation`, 안내의 “별도 재계산”·“실행 이력” 포함, 저장된 문제 코드와 실제 계산 보류를 검사한다. 안내 문자열의 포함 검사는 문장 전체 의미 인증이 아니다. 모델 지침 준수·새 LLM 출력·원문 PDF 파싱·새 DART 조회·b 재검수도 이 테스트 범위에 포함하지 않는다.

## 본인 보고와 AI 재실행

|구분|앞서 본인이 보고한 실행|이번 AI 재실행|
|---|---|---|
|관련3개 모듈|24개 /0.481초 /OK|24개 /0.566초 /OK|
|전체Python|239개 /29.725초 /OK(skipped=1)|239개 /34.528초 /OK(skipped=1)|

본인 보고의24·239와 저장소23·238의 차이는 이번 메서드1개로 설명된다. 전체239개 중 이번 AI 실행은238개 통과·1개 건너뜀, 실패0·오류0이다. AI 환경의 건너뜀은 공식 PDF 캐시 부재다. 본인 환경의 건너뛴 항목은 아직 제공되지 않았으므로 같은 항목이라고 확정하지 않는다. 본인의 원래 시간·환경·도움 여부도 새로 만들어 채우지 않는다. Starlette/Pydantic 경고는 원본 로그에 남겨 실패와 구분했다.

수정 전 `f46cea1`의 `period_decision()`을 별도로 로드해 패치한 재검사에서는 한 메서드의 두 하위 사례가 `diagnostic_origin` 누락으로 오류를 냈다. 제품 파일을 되돌리거나 과거 응답을 수정하지 않았다. [수정 전 재현 로그](../../artifacts/author-diagnostic-test-20261111/ai-before.txt), [관련 검사](../../artifacts/author-diagnostic-test-20261111/ai-targeted.txt), [전체 검사](../../artifacts/author-diagnostic-test-20261111/ai-full.txt).

## 기록 상태

“추가 테스트1개 미수신”은 해소됐다. 기존 기간2개·DART3개에 이번 진단1개를 더해 제출·확인된 개인 테스트는 총6개다. 이는 한 번의 실행 로그나 모두 같은 시점의 개인 커밋이라는 뜻이 아니다. 이전238개 검사·미수신 기록·LLM 실패·b 판정은 보존한다. 제품 계산·생성 지침 변경0건, 추가 유료 호출0회, 새 모델 출력0건, 새 b 검수0건이다. v7 생성·b 검수 완료 상태는 바뀌지 않는다.

AI의 요약 화면 통합 검증: API6개·로컬 PC/모바일 크기 브라우저10개 통과. Node 첫 실행은 과거5개 요약의 합계 표시가 빠져13통과·1실패였다. 과거 표시 분기를 복구한 뒤14개 통과했고 최초 로그도 보존했다. 이 화면 문제와 수정은 AI 통합 작업이며 본인이 발견·수정한 것으로 기록하지 않는다. 물리기기·직접 공개 HTTPS 검사가 아니다.
