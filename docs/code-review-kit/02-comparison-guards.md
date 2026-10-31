# 2. 기간·연결 범위가 맞지 않을 때 계산 보류

**작성자 직접 검토: NOT_PERFORMED.** 이 자료는 기존 방어 구현의 코드 설명과 AI 로컬 시연이다. 아래 불일치 입력은 실제 정본 셀을 의도적으로 잘못 조합한 반례이며, 보고서 자체의 오류나 새 고객 제보가 아니다.

## 입력에서 왜 문제가 생기는가

삼성전자 2024 Q3 연결 매출 79,098,731백만 원과 반기 연결 매출의 단독 2분기 74,068,302백만 원은 QoQ 비교가 가능하다. 그러나 반기 **누적** 145,983,903백만 원으로 B를 바꾸면 3개월 대 6개월이 된다. B를 **별도** 매출로 바꾸면 기업집단의 포함 범위가 달라진다. 숫자만 나누는 식은 실행되더라도 업무상 비교가 성립하지 않는다.

이 파일은 “과거 코드가 이 입력을 통과시켰고 이번에 고쳤다”는 주장을 하지 않는다. 실제 변경 이력과 재현이 없는 새 발견·수정 실적을 만들지 않는다.

## 현재 코드가 확인하는 조건

- [core.py](../../quarterguard/core.py): `valid_source`는 ID와 문서 manifest, 정본 문맥, `value × scale` 금액을 묶는다. 임의의 `Fact`를 만들면 기간 테스트 전에 `SOURCE_MISMATCH`도 생길 수 있어 아래는 실제 정본 ID를 사용한다.
- `context_issues`: 회사·항목·범위·통화, 단위, 출처, 참고 환산액 검사.
- `compare`: QoQ는 양쪽이 3개월이고 기준 분기 종료 다음 날이 현재 분기 시작이어야 한다. 문제가 하나라도 있으면 `growth_pct=None`, `status=needs_review`다.
- `reconcile`: 같은 시작일의 누적 구간과 직접 공시된 3개월 구간을 확인한 뒤 누적 차감액과 직접 공시액을 대조한다.

## 정상·거부 사례 재실행

저장소 루트에서 실행한다. 데이터·평가 artifact를 수정하지 않는다.

```bash
.venv/bin/python - <<'PY'
from quarterguard.store import load_facts
from quarterguard.core import compare, reconcile
facts = {f.id: f for f in load_facts()}
a = facts['s24q3-CFS-revenue-2024-q-KRW']
for label, key in [
    ('normal', 's24q2-CFS-revenue-2024-q-KRW'),
    ('ytd', 's24q2-CFS-revenue-2024-ytd-KRW'),
    ('scope', 's24q2-OFS-revenue-2024-q-KRW'),
]:
    result = compare(a, facts[key], 'qoq')
    print(label, {k: result[k] for k in ('status', 'issues', 'growth_pct')})
result = reconcile(facts['s24q3-CFS-revenue-2024-ytd-KRW'],
                   facts['s24q2-CFS-revenue-2024-ytd-KRW'], a)
print('reconcile', {k: result[k] for k in ('status', 'issues', 'derived_value', 'difference')})
PY
```

2026-10-31 AI가 위 명령을 로컬에서 실행해 확인한 출력:

```text
normal {'status': 'verified', 'issues': [], 'growth_pct': '6.7916'}
ytd {'status': 'needs_review', 'issues': ['PERIOD_MISMATCH'], 'growth_pct': None}
scope {'status': 'needs_review', 'issues': ['SCOPE_MISMATCH'], 'growth_pct': None}
reconcile {'status': 'verified', 'issues': [], 'derived_value': '79098731', 'difference': '0'}
```

[tests/test_core.py](../../tests/test_core.py)의 `VerificationTests.test_qoq_decimal`, `test_cumulative_not_quarter`, `test_scale_conversion`, `test_reconcile_independent_report`, `test_reconcile_rejects_forged_source_amount`를 읽는다. `test_context_mismatches`의 일부 입력은 합성 변형이므로 다른 거부 원인도 함께 나올 수 있다. 단일 원인을 보여주는 위 정본 ID 예제와 구분한다.

```bash
.venv/bin/python -m unittest discover -s tests -p test_core.py -v
```

## 본인이 설명할 질문

1. `PERIOD_MISMATCH`와 `SCOPE_MISMATCH`는 어느 함수에서 추가되며, 왜 숫자를 출력하지 않는가?
2. 금액을 1,000배 늘리고 배율을 1/1,000로 줄인 경우와 배율만 바꾼 경우를 `valid_source`는 어떻게 구분하는가?
3. 누적 차감이 맞아도 이 결과만으로 PDF 파싱·모든 재무제표·전문가 검토 성공을 주장할 수 없는 이유는 무엇인가?

본인의 설명·실행 출력·남은 의문: **NOT_PERFORMED**. [기록지](review-template.md)에 실제 수행 후 작성한다.
