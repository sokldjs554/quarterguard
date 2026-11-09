# DART 단위·중복 후보 테스트 직접 보강 기록 — 2026-11-09 정리

## 본인이 제공한 근거

작성자는 테스트 코드와 아래 실행 출력을 전달하고, 직접 커밋·push를 진행했다. 원본 커밋은 [`c867fcaa68d07725bf81a2367f37a4bba0356b3b`](https://github.com/sokldjs554/quarterguard/commit/c867fcaa68d07725bf81a2367f37a4bba0356b3b)이며 [`tests/test_my_dart_review.py`](../../tests/test_my_dart_review.py) 1개 파일, 59줄 추가, 삭제 0줄이다. 원본 커밋의 부모는 `beef5fa3cb866ba352f38f6b39bc733b6266b340`이다. 최신 main에서 작성한 테스트로 바꾸어 기록하지 않는다.

```text
test_rejects_amount_without_scale (test_my_dart_review.MyDartReviewTests.test_rejects_amount_without_scale) ... ok
test_rejects_two_identical_candidate_rows (test_my_dart_review.MyDartReviewTests.test_rejects_two_identical_candidate_rows) ... ok
test_won_conversion_matches_one_candidate (test_my_dart_review.MyDartReviewTests.test_won_conversion_matches_one_candidate) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

이는 본인이 제공한 로컬 출력이다. 이번 전체 테스트 출력·실행 일시·Python 버전·OS는 새로 제공되지 않았다. [기간 테스트 당시 환경과 전체 143개 기록](review-20261108.md)을 이번 DART 실행에 재사용하지 않는다. 정리일은 실제 수행일을 확정하는 값이 아니다.

## 테스트가 확인하는 내용

정본 `s24q3-CFS-revenue-2024-q-KRW` 하나와 테스트용 DART 형태의 행을 사용한다. 기대 금액을 `fact.amount`에서 생성하지 않고 원 단위 문자열 `79098731000000`으로 지정했다.

|사례|검사 내용|
|---|---|
|정상 환산|후보 1개, `expected_krw`와 `dart_krw`가 `79098731000000`, `passed=True`|
|배율 누락|후보 1개지만 `dart_krw=79098731`, 기대 금액 불일치, `passed=False`|
|같은 금액의 중복|서로 다른 딕셔너리 후보 2개, `passed=False`, `dart_krw=None`, `dart_source=None`|

작성자가 전달한 설명:

> 금액이 같다는 사실과 출처가 하나로 확정됐다는 사실은 다르기 때문입니다.

관련 코드는 [Fact.amount](../../quarterguard/core.py)의 Decimal 배율 환산과 [check_dart_rows](../../quarterguard/live_verification.py)의 `len(matches) == 1` 조건이다. 기존 방어 기능을 구체적으로 확인하는 테스트 보강이며, 제품 코드의 새 버그 발견·수정으로 기록하지 않는다.

## 원문·실호출·AI 도움 구분

이 테스트는 준비한 행을 사용하는 로컬 함수 평가다. 새 DART API 호출, 원문 PDF 파싱, 접수번호 URL의 실제 문서 내용 확인이 아니다. URL은 기존 테스트의 형식상 유효한 fixture 값이며 실문서 검증 근거로 인용하지 않는다.

AI는 코드 위치, 독립적인 기대 금액 사용, 세 검증 조건, 실행·Git 명령을 안내했다. 작성자는 코드를 제공하고 실행 결과와 커밋을 제출했다. AI 도움 없음 또는 테스트 설계 전체를 독립적으로 수행했다는 주장으로 확대하지 않는다. 이후 병합·자동 검사·문서 정리는 AI가 수행한다.

## 공개·자동 검사

- [원본 커밋 GitHub Actions](https://github.com/sokldjs554/quarterguard/actions/runs/42582583870): 성공. 본인의 로컬 전체 테스트 실행과 구분한다.
- 원본 커밋을 최신 main과 병합하며 그대로 보존한다. 테스트 파일 바이트를 원본과 대조하고, 제품 코드·기존 평가 자료는 변경하지 않는다.
- 최신 main과 합친 후의 AI 회귀 검사·병합 CI는 통합 PR에 별도로 남긴다.

통합 작업에서 AI가 실행한 전체 회귀 검사는 **147개 / 27.945초 / OK**였다. [실행 출력](../../artifacts/dart-personal-integration-20261109/python-tests.txt)과 [실행 주체·범위](../../artifacts/dart-personal-integration-20261109/manifest.json)를 보존한다. 이 수치를 본인의 직접 전체 실행 결과로 쓰지 않는다. 새 외부 공급자·유료 API 호출은 없고 청구액은 조회하지 않았다.
