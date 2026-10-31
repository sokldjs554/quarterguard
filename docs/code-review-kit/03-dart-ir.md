# 3. DART 원 단위와 IR 백만 원 단위를 대조하기

**작성자 직접 검토: NOT_PERFORMED.** 기존 대조 구현을 설명하는 자료다. 과거 실제 호출 기록, 이번 로컬 재생, 합성 거부 사례를 구분한다. 새로운 DART 호출이나 유료 호출은 이 자료에 필요하지 않다.

## 입력에서 왜 문제가 생기는가

IR의 `79,098,731`은 백만 원이므로 79,098,731,000,000원이다. DART 응답의 원 단위 숫자와 배율 없이 비교하면 서로 다르다고 잘못 판정한다. 반대로 금액만 맞추면 `thstrm_amount`(단독 분기)와 `thstrm_add_amount`(누적), 연결/별도, 기업/연도/보고서가 다른 행을 붙일 수 있다. 이는 확인하려는 실패 방식이며, 이 키트 작성 중 새로 발견·수정한 버그라는 주장이 아니다.

## 현재 코드가 확인하는 조건

- [dart.py](../../quarterguard/dart.py)의 `fetch`: 응답의 `corp_code`, `bsns_year`, `reprt_code`가 요청과 일치하는지 확인하고 손익계산서 IS/CIS에서 필드를 분리한다. `fs_div`는 응답 확인값이 아니라 요청 메타데이터다(`scope_basis=request_fs_div`). 이 한계를 고객 시스템의 독립적인 범위 검증으로 과장하지 않는다.
- [core.py](../../quarterguard/core.py)의 `Fact.amount`: Decimal 값에 배율을 곱해 원 단위로 정규화한다.
- [live_verification.py](../../quarterguard/live_verification.py)의 `check_dart_rows`: 계정 ID·단독/누적·기업·연도·범위·통화·보고서 코드·원본 필드로 후보를 거른다. 후보가 정확히 한 개이고 DART 접수번호 URL 형식이 맞으며 유한한 금액이 정규화 IR 금액과 같아야 통과한다.

여기서 대조 범위는 삼성전자 2024 Q2/Q3, CFS/OFS, 매출/영업이익, 단독/누적이다. 임의의 회사·회계연도·계정 매핑, DART 원문 전체의 정확성, 자동 정본 편입을 검증한 것이 아니다.

## 과거 실호출 정상 근거

[artifacts/public-dart.json](../../artifacts/public-dart.json)의 `records` 중 `target=s24q3-CFS`, `response.execution=live_provider_request` 기록에 다음이 있다. 2026-10-29의 기존 자동 실행 기록이며 이번에 새로 호출하거나 사람이 검토한 결과가 아니다.

| 항목 | 보존된 값 |
| --- | --- |
| fact_id | `s24q3-CFS-revenue-2024-q-KRW` |
| source_field | `thstrm_amount` |
| expected_krw / dart_krw | `79098731000000` / `79098731000000` |
| candidate_count / passed | `1` / `true` |
| DART 근거 | [접수번호 20241114002642](https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20241114002642) |
| IR 근거 | [2024 3Q 공식 PDF](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf), p34 |

## 외부 호출 없는 정상·거부 재현

다음은 위 기존 기록의 금액·접수번호와 정본을 사용해 **대조 함수용 행을 재구성한 로컬 예제**다. raw DART API 응답 재생이나 새 실호출이 아니다. 단위 축소·중복·범위 변경은 합성 반례다.

```bash
.venv/bin/python - <<'PY'
from quarterguard.store import load_facts
from quarterguard.live_verification import check_dart_rows
fact = next(f for f in load_facts() if f.id == 's24q3-CFS-revenue-2024-q-KRW')
row = dict(company_code='00126380', year='2024', report_code='11014',
           scope='CFS', currency='KRW', account_id='ifrs-full_Revenue',
           period_kind='quarter', source_field='thstrm_amount',
           amount='79098731000000',
           source_url='https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20241114002642')
for label, rows in [
    ('normal', [row]),
    ('wrong_unit', [row | {'amount': '79098731'}]),
    ('duplicate', [row, row]),
    ('wrong_scope', [row | {'scope': 'OFS'}]),
    ('wrong_field', [row | {'source_field': 'thstrm_add_amount'}]),
]:
    check = check_dart_rows(rows, [fact], '11014')[0]
    print(label, {k: check[k] for k in ('candidate_count', 'expected_krw', 'dart_krw', 'passed')})
PY
```

2026-10-31 AI 로컬 실행에서 확인한 결과: 정상은 후보 1개·일치·`passed=True`; 단위 오류는 후보 1개지만 금액 불일치·`False`; 중복은 후보 2개·`False`; 범위나 필드 오류는 후보 0개·`False`. `False`는 불일치/검토 필요이며 곧바로 “DART 원문 오류”라는 뜻이 아니다.

[tests/test_live_verification.py](../../tests/test_live_verification.py)의 `DartCrossCheckTests.test_won_conversion_and_period_fields`, `test_rejects_missing_duplicate_and_wrong_context`, `test_raw_provider_context_mismatch_is_rejected`는 네트워크를 mock한다. [tests/test_public_providers.py](../../tests/test_public_providers.py)의 `test_dart_success_cache_no_second_network_and_context`와 `test_cache_invalidates_when_verifier_or_evidence_changes`는 캐시 경로를 다룬다. 테스트 통과를 실제 외부 호출 성공으로 쓰지 않는다.

```bash
.venv/bin/python -m unittest discover -s tests -p test_live_verification.py -v
```

## 본인이 설명할 질문

1. IR 배율은 어디서 적용되며, DART에서 단독 분기와 누적은 어떤 필드로 구분하는가?
2. 같은 금액의 후보가 두 개라면 왜 한 개를 임의 선택하면 안 되는가?
3. 응답이 독립적으로 확인하는 문맥과 요청에만 의존하는 문맥, mock 테스트와 과거 실호출 증거는 각각 무엇인가?

본인의 설명·실행 출력·남은 의문: **NOT_PERFORMED**. [기록지](review-template.md)에 실제 수행 후 작성한다.
