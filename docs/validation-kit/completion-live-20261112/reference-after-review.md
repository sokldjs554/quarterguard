# 판정 후 참고 — 자동 검사와 AI 분석

아래는 사람 판정이 아닙니다. 자동 차단은 거짓 판정과 같지 않고, 자동 통과도 의미 정확성을 보장하지 않습니다.

|ID|사례|실행 당시 제품 검사|실패한 검사|
|---|---|---|---|
|R01|qoq-revenue|차단|prose_evidence_anchors_present|
|R02|ytd-trap|통과|없음|
|R03|no-evidence|차단|prose_review_language_localized|
|R04|reconcile-revenue|차단|prose_evidence_anchors_present|
|R05|replay-normal-qoq|차단|prose_evidence_anchors_present|
|R06|replay-normal-yoy|차단|prose_evidence_anchors_present|
|R07|replay-period-mismatch|차단|prose_review_language_localized, prose_evidence_anchors_present|
|R08|replay-scope-mismatch|통과|없음|
|R09|replay-unit-draft|차단|prose_evidence_presence_consistent, prose_evidence_anchors_present|
|R10|replay-no-evidence|통과|없음|
|R11|replay-conflicting-number-draft|차단|prose_evidence_anchors_present|
|R12|replay-citation-draft|차단|prose_rate_unit_explicit, prose_evidence_anchors_present|
|R13|replay-s22-op-yoy|차단|prose_rate_unit_explicit, prose_evidence_anchors_present, prose_rates_match_tool|
|R14|replay-s22-net-ytd-yoy|통과|없음|
|R15|replay-s22-net-period|차단|prose_review_language_localized, prose_decision_basis_present|
|R16|replay-s22-op-qoq|차단|prose_review_language_localized, prose_decision_basis_present|
|R17|replay-h25-op-yoy|차단|prose_evidence_anchors_present, prose_rates_match_tool|
|R18|replay-h25-net-yoy|차단|prose_rates_match_tool|
|R19|replay-h25-op-period|차단|prose_review_language_localized, prose_evidence_anchors_present|
|R20|replay-cross-company-period|차단|prose_review_language_localized, prose_evidence_anchors_present|

## AI가 읽고 발견한 점 — b의 판정으로 기록하지 않음

- R02는 자동 통과했지만, 별도 재계산 안내 앞에서 “도구 실행 이력에 따르면 … 시작 월일 또한 달라서”라고 썼습니다. compare()는 개월 수 불일치 시 후속 YoY 날짜 조건을 단축 평가하므로 이 서술은 실제 실행 이력과 구분할 필요가 있습니다.
- R01·R04 등의 근거 문장 차단은 숫자 오류를 뜻하지 않습니다. 필수 문장을 그대로 복사하지 않고 조사를 붙이거나 출처 문장을 나눠 쓴 것도 차단됩니다. 의미와 형식 준수를 따로 판정하세요.
- R09는 잘못된 초안에 “근거가 없습니다”라고 한 문장을 근거 전체의 부재 주장으로 검사한 가능성이 있습니다. 부정 대상이 무엇인지 확인해야 합니다.
- R17·R18은 음수 증감률을 양의 크기와 “감소”로 표현했습니다. 예를 들어 −20.5146%와 20.5146% 감소는 같은 방향을 표현할 수 있으므로 현재 숫자 부호 검사에서 차단됐다는 이유만으로 거짓으로 판정하지 마세요.
- R13은 전년 동분기 증감률을 “연평균 성장률”이라고 표현했습니다. R12는 첫 계산값 6.7916에 % 없이 쓰고 뒤에서는 %를 붙였습니다.
- 내부 코드가 본문에 남은 사례도 있습니다. 금액 정확성과 사용자 표현의 명확성을 분리하세요.

자동 통과 사례는 R02·R08·R10·R14, 총4/20입니다. 구조 필드와 근거 ID는20/20 일치했지만 사람 의미 판정은 아직0건입니다. 이번 기록을 일반적인 모델 정확도나 독립 평가 결과로 확대하지 않습니다.

## 후속 코드 검사 — 동일 원응답 재생, 새 생성 아님

실행 뒤 감소 크기·부호, 도구 실행 이력의 잘못된 귀속, 연평균 지표 오표현 검사를 보완했습니다. 같은20개 원응답을 재생하면 R02가 추가 차단되고 R18의 부호 오탐이 해소되어, R08·R10·R14·R18 총4건이 통과합니다. 기존 4/20 판정을 덮어쓴 것이 아니며 사람 의미 판정도 아닙니다. 필수 문자열 형식과 R09의 부정 대상 구분 한계는 남습니다.
