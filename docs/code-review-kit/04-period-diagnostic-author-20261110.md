# 본인이 제출한 기간 진단 구분 코드와 실행 기록

기준 커밋: `f46cea1387170dd28737970992fb135d3b65ec82`. 프로젝트 작성자가 수정 파일 `explanation_context.py`와 실행 결과를 제출했다. 제출 파일을 바이트 그대로 반영했다. AI는 코드 대조·별도 재실행·문서 정리·통합 게시를 담당했다. 작성 시 도움 범위, 실행 날짜·환경은 이번 제출에 없으며 이전 기록에서 가져오지 않는다.

[제출 기록과 파일 해시](../../artifacts/author-period-diagnostic-20261110/submission.json) · [AI의 실제 compare 재실행](../../artifacts/author-period-diagnostic-20261110/ai-diagnostic-replay.json).

## 본인이 설명한 문제와 변경

`compare()`는 먼저 개월 수가 같은지 확인한다. 9개월과 3개월이면 `valid`가 거짓이 되고 `and`의 단락 평가 때문에 후속 YoY 날짜 조건을 실행하지 않는다. 반환 문제 코드는 `PERIOD_MISMATCH`이며 성장률은 `None`이다.

`period_conditions()`는 조건을 독립적으로 재계산한다. 따라서 그 실패 항목을 도구가 실제 실행한 조건 이력이라고 표현하면 부정확하다. 수정 파일은 모델 지침에 “separate recalculations, not the tool execution trace”를 넣고, `period_decision()`에 `diagnostic_origin: independent_recalculation`과 “도구의 조건 실행 이력이 아닙니다”라는 안내를 추가했다. 계산 코드는 변경하지 않았다.

첨부 파일에는 이 추가 외에도 기존 모델 지침 일부 축약이 있다. 따라서 이후 모델 결과를 평가한다면 이 파일 전체의 효과를 평가해야 하며, 진단 표시 한 문구만 바뀐 실험으로 표현하지 않는다. 이번 회귀 통과는 프롬프트 축약의 모든 의미적 효과를 보장하지 않는다.

## 제출된 실행 결과와 AI 재검사 구분

|검사|본인이 전달한 결과|AI: 기준 커밋에 첨부 파일만 적용|
|---|---|---|
|지정 Python 3개 모듈|24개, 0.481초, OK|23개, 0.780초, OK|
|전체 Python|239개, 29.725초, OK (skipped=1)|238개, 33.431초, OK (skipped=1)|
|Node|14개 통과, 실패 0|14개 통과, 실패 0|

본인이 실행한 명령:

```sh
python -m unittest tests.test_explanation_contract tests.test_explanation_context tests.test_live_explanations_v5
python -m unittest discover -s tests
node --test tests/*.mjs
```

전체 Python에 Starlette/Pydantic 경고가 있었다는 보고도 보존한다. 경고를 실패로 세거나, 건너뛴 테스트를 통과로 세지 않는다. 구현 파일만 제출되어 추가 테스트 1개의 코드·이름과 본인 환경의 건너뛴 항목은 미확인이다. AI가 추가 테스트를 대신 만들어 본인 작성으로 기록하지 않았다. AI 환경의 건너뜀은 공식 PDF 캐시가 없는 `test_known_official_pdf_matches_all_sixteen_frozen_cells`다. 나머지 실패는 0이다.

## 실제 함수 실행으로 확인한 두 사례

|저장된 입력을 사용한 사례|실제 compare 반환|별도 재계산 실패 항목|
|---|---|---|
|h25-op-period: 9개월·3개월 YoY|PERIOD_MISMATCH, growth_pct=null|equal_months, yoy_start_month_day|
|s22-op-qoq: 1년 차이의 같은 분기 QoQ|PERIOD_MISMATCH, growth_pct=null|qoq_adjacent|

AI는 과거 v7 입력으로 실제 `compare()`를 실행해 원래 반환값 전체와 일치함을 확인했다. 도구 결과 재생만 한 검사와 구분하지만, 새 PDF 파싱·DART 조회·새 MCP 평가·새 LLM 생성은 아니다. 평가 전용 기업 정본을 공개 코퍼스에 등록하지 않았다.

이전 v7 동결 입력·원응답·b 판정은 보존했다. 변경 코드로 과거 승인 입력을 실행하려 하면 `FREEZE_CODE_MISMATCH`로 차단된다. 기존 승인으로 새 요청을 실행하지 않으며, 새 유료 생성 평가에는 새 입력·비용 범위 승인이 필요하다.

## 완료 범위와 직접 기록할 수 있는 내용

이번 완료 범위는 제출 코드의 통합과 로컬 회귀 검증이다. 추가 유료 호출 0회·새 모델 출력 0건·b의 새 출력 검수 0건이다. 기존 b의 참 15·모호 1 판정은 그대로이고, 모호한 응답을 사후 참으로 바꾸지 않는다. `SEARCH_EMPTY`·`qoq_adjacent` 등의 내부 코드 가독성 개선도 별도 과제다.

지원서에 사용할 수 있는 표현: “기간 비교의 단락 평가와 별도 재계산 진단을 구분하도록 설명 코드를 수정하고 로컬 테스트를 실행했습니다. 실제 계산 판정과 기록된 결과는 유지했습니다.” AI의 통합·별도 검증과 본인의 실행 기록을 구분하며, 전체 독립 개발·새 LLM 정확도 개선·b의 수정 후 재검수 완료로 확대하지 않는다. 본인 추가 테스트 1개의 diff·건너뜀 이유가 제공되면 검토 기록을 후속 보강할 수 있다.
