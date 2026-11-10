# v7 실제 응답16건 — b에게 전달할 재검수 자료

**새 응답의 사람 검수는 아직 수행하지 않았습니다.** 아래 문장은 실제 모델 원응답이며 AI가 수정하지 않았습니다. 먼저 새 문장·구조 필드와 원문을 대조하고, 접힌 직전 응답은 그다음에 비교해 주세요. 이전 b 판정은 새 응답에 복사하지 않았습니다.

[검수 기준·공개 확인 안내](llm-prose-v7-review-20261110.md) · [실행 결과](../llm-prose-v7-results-20261110.md) · [원기록](../../artifacts/llm-prose-v7-20261110/report.json)

실제 호출: GPT-5.4-mini-2026-03-17, 2026-11-10 22:37 KST 시작,16회. 이전과 같은16개 사례이며 모두 개발에 사용한 알려진 사례입니다. 과거8+8 그룹은 구분하지만 새 독립 평가셋이 아닙니다. 도구 결과 재생이며 이번에 PDF나 MCP를 다시 실행하지 않았습니다.

본문의 수치·기간·범위·단위·문서 지칭과 JSON 값·근거ID를 각각 판정해 주세요. 내부 코드명·모호한 표현도 실제 독자가 이해할 수 있는지 확인해 주세요. 자동 통과는 설명 의미의 정확성을 보증하지 않습니다. 정답 자료도 원문과 다르면 지적해 주세요.

## 1. `normal-qoq`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 2024년 3분기 연결 매출의 전분기 대비 증감률

### 실제 생성 문장

> 2024년 3분기 연결 매출의 전분기 대비 증감률은 증가율 6.7916%입니다. 기준값은 2024년 2분기 연결 매출입니다. 근거 문서는 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34와 Samsung Electronics 2024 Half-year Business Report의 PDF p.48입니다. 각 값은 각각 79,098,731 백만 원과 74,068,302 백만 원입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "6.7916",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `6.7916` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q2-CFS-revenue-2024-q-KRW`|74068302 · KRW · ×1000000|2024-04-01 ~ 2024-06-30 · 3개월 · CFS|[Samsung Electronics 2024 Half-year Business Report · p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

2024년 3분기 연결 매출의 전분기 대비 증감률은 6.7916%입니다. 기준 문서는 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34입니다. 해당 분기 값은 79,098,731 백만 원입니다. 비교 기준 문서는 Samsung Electronics 2024 Half-year Business Report의 PDF p.48입니다. 해당 분기 값은 74,068,302 백만 원입니다. 둘 다 연결 기준입니다.

```json
{
  "status": "verified",
  "value": "6.7916%",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

</details>

## 2. `normal-yoy`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 2024년 3분기 연결 매출의 전년 동분기 대비 증감률

### 실제 생성 문장

> 2024년 3분기 연결 매출의 전년 동분기 대비 증가율은 17.3491%입니다. 기준 문서는 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34입니다. 2024 Q KRW는 79,098,731 백만 원입니다. 2023 Q KRW는 67,404,652 백만 원입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "17.3491",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `17.3491` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q3-CFS-revenue-2023-q-KRW`|67404652 · KRW · ×1000000|2023-07-01 ~ 2023-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

삼성전자 2024 3분기 연결 매출은 전년 동분기 대비 17.3491% 증가했습니다. 근거는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW와 Revenue / 2023 Q KRW입니다. 두 값은 모두 3개월 연결 기준입니다. 표시 단위는 백만 원입니다.

```json
{
  "status": "verified",
  "value": "17.3491%",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

</details>

## 3. `period-mismatch`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 9개월 누적과 전년 3개월 매출 비교의 제한

### 실제 생성 문장

> 계산 보류입니다. 두 기간의 개월 수가 같지 않습니다. 9개월 누적과 3개월 분기라서 비교 조건을 충족하지 않습니다. 두 기간의 시작 월·일도 다릅니다. 근거 1은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 YTD KRW입니다. 225,082,634 백만 원입니다. 근거 2는 같은 문서의 PDF p.34, Revenue / 2023 Q KRW입니다. 67,404,652 백만 원입니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-ytd-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['PERIOD_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-ytd-KRW`|225082634 · KRW · ×1000000|2024-01-01 ~ 2024-09-30 · 9개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 YTD KRW|
|`s24q3-CFS-revenue-2023-q-KRW`|67404652 · KRW · ×1000000|2023-07-01 ~ 2023-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

비교가 보류되었습니다. 9개월 누적과 전년 3개월은 기간 길이가 달라 같은 기준의 성장률로 비교할 수 없습니다. 첫 번째 근거는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 YTD KRW입니다. 2024-01-01 ~ 2024-09-30, 9개월, 연결, 225,082,634 백만 원입니다. 두 번째 근거는 같은 보고서의 PDF p.34의 Revenue / 2023 Q KRW입니다. 2023-07-01 ~ 2023-09-30, 3개월, 연결, 67,404,652 백만 원입니다. 도구의 비교 제한에 따라 계산을 보류했습니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-ytd-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

</details>

## 4. `scope-mismatch`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 연결 매출과 별도 매출 비교의 제한

### 실제 생성 문장

> 연결과 별도의 범위가 달라 비교를 보류했습니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue는 2024-07-01 ~ 2024-09-30, 3개월, 연결입니다. Samsung Electronics 2024 Half-year Business Report, PDF p.104의 Revenue는 2024-04-01 ~ 2024-06-30, 3개월, 별도입니다. 범위를 맞춘 뒤 다시 검증해야 합니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "SCOPE_MISMATCH"
  ],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-OFS-revenue-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['SCOPE_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q2-OFS-revenue-2024-q-KRW`|53734118 · KRW · ×1000000|2024-04-01 ~ 2024-06-30 · 3개월 · OFS|[Samsung Electronics 2024 Half-year Business Report · p.104](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=104)|Revenue / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

연결과 별도 범위가 달라 비교를 보류했습니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue는 연결입니다. 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report, PDF p.104의 Revenue는 별도입니다. 53,734,118 백만 원입니다. 두 자료는 범위가 달라 성장률을 확정하지 않았습니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "SCOPE_MISMATCH"
  ],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-OFS-revenue-2024-q-KRW"
  ]
}
```

</details>

## 5. `unit-draft`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 매출 증가율 및 근거 금액 단위를 설명

### 실제 생성 문장

> 매출 증가율은 6.7916%입니다. 기준은 2024년 2분기 연결 매출과 2024년 3분기 연결 매출입니다. 2024년 3분기 연결 매출은 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34, Revenue / 2024 Q KRW입니다. 금액은 79,098,731 백만 원입니다. 2024년 2분기 연결 매출은 Samsung Electronics 2024 Half-year Business Report의 PDF p.48, Revenue / 2024 Q KRW입니다. 금액은 74,068,302 백만 원입니다. 두 값 모두 통화는 KRW이고 표시 단위는 백만 원입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "6.7916",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `6.7916` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q2-CFS-revenue-2024-q-KRW`|74068302 · KRW · ×1000000|2024-04-01 ~ 2024-06-30 · 3개월 · CFS|[Samsung Electronics 2024 Half-year Business Report · p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

매출 증가율은 6.7916%입니다. 전기 대비 비교입니다. 근거 금액은 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34와 Samsung Electronics 2024 Half-year Business Report의 PDF p.48입니다. 두 사실 모두 연결(CFS) 기준입니다. 첫 번째 사실은 2024-07-01 ~ 2024-09-30, 3개월, Revenue / 2024 Q KRW입니다. 값은 79,098,731 백만 원입니다. 두 번째 사실은 2024-04-01 ~ 2024-06-30, 3개월, Revenue / 2024 Q KRW입니다. 값은 74,068,302 백만 원입니다. 표시 단위는 백만 원입니다.

```json
{
  "status": "verified",
  "value": "6.7916%",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

</details>

## 6. `no-evidence`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 수집 범위 밖인 2025년 실적 조회

### 실제 생성 문장

> 해당 검색 범위에서 근거를 확인할 수 없습니다. 2025년 실적은 이 검색 범위에서 확인되지 않았습니다. 이 판단의 근거는 SEARCH_EMPTY입니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "SEARCH_EMPTY"
  ],
  "evidence_ids": []
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['SEARCH_EMPTY']`

이 도구 결과에는 근거가 없습니다. 이 검색 범위의 결과이며 기업의 실적 자체가 없다는 뜻은 아닙니다.

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

해당 검색 범위에서 근거를 확인할 수 없습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인하세요. 문서 제목과 PDF 페이지 정보가 제공되지 않았습니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "SEARCH_EMPTY"
  ],
  "evidence_ids": []
}
```

</details>

## 7. `conflicting-number-draft`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 근거에 맞는 매출 증가율을 설명

### 실제 생성 문장

> Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34에서 2024-07-01 ~ 2024-09-30, 3개월, 연결 매출은 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report의 PDF p.48에서 2024-04-01 ~ 2024-06-30, 3개월, 연결 매출은 74,068,302 백만 원입니다. 이 두 값의 비교 결과 증가율은 6.7916%입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "6.7916",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `6.7916` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q2-CFS-revenue-2024-q-KRW`|74068302 · KRW · ×1000000|2024-04-01 ~ 2024-06-30 · 3개월 · CFS|[Samsung Electronics 2024 Half-year Business Report · p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34에서 확인되는 연결 매출은 2024-07-01 ~ 2024-09-30 기준 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report의 PDF p.48에서 확인되는 연결 매출은 2024-04-01 ~ 2024-06-30 기준 74,068,302 백만 원입니다. 두 값은 모두 3개월 연결 기준입니다. 따라서 분기 대비 매출 증가율은 6.7916%입니다.

```json
{
  "status": "verified",
  "value": "6.7916%",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

</details>

## 8. `citation-draft`

과거 그룹: 기존 개발8건 · 이번에는 모두 동일 사례 재평가

요청: 공시 근거에 맞는 매출 증가율을 설명

### 실제 생성 문장

> 매출 증가율은 6.7916%입니다. 비교 대상은 분기 QoQ입니다. 두 근거는 모두 연결(CFS) 기준입니다. 2024-07-01 ~ 2024-09-30 분기 매출은 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34, Revenue / 2024 Q KRW에서 79,098,731 백만 원입니다. 2024-04-01 ~ 2024-06-30 분기 매출은 Samsung Electronics 2024 Half-year Business Report의 PDF p.48, Revenue / 2024 Q KRW에서 74,068,302 백만 원입니다. 이 비교로 증가율 6.7916%가 산출되었습니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "6.7916",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `6.7916` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s24q3-CFS-revenue-2024-q-KRW`|79098731 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Samsung Electronics 2024 3Q Interim Business Report · p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|`s24q2-CFS-revenue-2024-q-KRW`|74068302 · KRW · ×1000000|2024-04-01 ~ 2024-06-30 · 3개월 · CFS|[Samsung Electronics 2024 Half-year Business Report · p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

삼성전자 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW는 79,098,731 백만 원입니다. 삼성전자 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW는 74,068,302 백만 원입니다. 두 값은 모두 연결(CFS) 기준의 3개월 분기 수치입니다. 전분기 대비 매출 증가율은 6.7916%입니다.

```json
{
  "status": "verified",
  "value": "6.7916%",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

</details>

## 9. `s22-op-yoy`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 삼성전자 2022년과 2021년 3분기 연결 영업이익의 전년 동분기 증감률을 설명하세요.

### 실제 생성 문장

> Samsung Electronics 2022 Q3 Interim Report, PDF p.37에서 연결 기준 영업이익을 확인했습니다. 2022년 3분기 영업이익은 10,852,045 백만 원입니다. 2021년 3분기 영업이익은 15,817,531 백만 원입니다. 전년 동분기 대비 증감률은 -31.3923%입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "-31.3923",
  "issues": [],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "s22q3-CFS-operating_profit-2021-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `-31.3923` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s22q3-CFS-operating_profit-2022-q-KRW`|10852045 · KRW · ×1000000|2022-07-01 ~ 2022-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Operating profit / 2022 Q KRW|
|`s22q3-CFS-operating_profit-2021-q-KRW`|15817531 · KRW · ×1000000|2021-07-01 ~ 2021-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Operating profit / 2021 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

Samsung Electronics 2022 Q3 Interim Report의 PDF p.37에서 연결 영업이익이 확인됩니다. 2022년 3분기 연결 영업이익은 10,852,045 백만 원입니다. 같은 보고서의 PDF p.37에서 2021년 3분기 연결 영업이익은 15,817,531 백만 원입니다. 2022년 3분기 연결 영업이익은 전년 동분기 대비 -31.3923%입니다.

```json
{
  "status": "verified",
  "value": "-31.3923",
  "issues": [],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "s22q3-CFS-operating_profit-2021-q-KRW"
  ]
}
```

</details>

## 10. `s22-net-ytd-yoy`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 삼성전자 2022년과 2021년 9개월 누적 연결 당기순이익의 전년 동기 증감률과 출처를 설명하세요.

### 실제 생성 문장

> 삼성전자 2022년 1월 1일~2022년 9월 30일 9개월 연결 당기순이익은 31,812,631 백만 원입니다. 출처는 Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2022 YTD KRW입니다. 삼성전자 2021년 1월 1일~2021년 9월 30일 9개월 연결 당기순이익은 29,069,502 백만 원입니다. 출처는 같은 보고서인 Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2021 YTD KRW입니다. 전년 동기 대비 증감률은 9.4364%입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "9.4364",
  "issues": [],
  "evidence_ids": [
    "s22q3-CFS-net_profit-2022-ytd-KRW",
    "s22q3-CFS-net_profit-2021-ytd-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `9.4364` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s22q3-CFS-net_profit-2022-ytd-KRW`|31812631 · KRW · ×1000000|2022-01-01 ~ 2022-09-30 · 9개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Profit for the period / 2022 YTD KRW|
|`s22q3-CFS-net_profit-2021-ytd-KRW`|29069502 · KRW · ×1000000|2021-01-01 ~ 2021-09-30 · 9개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Profit for the period / 2021 YTD KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

2022년 9개월 누적 연결 당기순이익은 31,812,631 백만 원입니다. 2021년 9개월 누적 연결 당기순이익은 29,069,502 백만 원입니다. 전년 동기 증감률은 9.4364%입니다. 근거는 Samsung Electronics 2022 Q3 Interim Report의 PDF p.37입니다. 같은 페이지의 Profit for the period 항목에서 2022 YTD KRW와 2021 YTD KRW가 확인됩니다.

```json
{
  "status": "verified",
  "value": "9.4364%",
  "issues": [],
  "evidence_ids": [
    "s22q3-CFS-net_profit-2022-ytd-KRW",
    "s22q3-CFS-net_profit-2021-ytd-KRW"
  ]
}
```

</details>

## 11. `s22-net-period`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 삼성전자 2022년 3개월과 2021년 9개월 연결 순이익의 비교 제한을 설명하세요. 근거가 없는 것인지 구분하세요.

### 실제 생성 문장

> 비교가 보류되었습니다. 두 기간의 개월 수가 같지 않습니다. 하나는 3개월이고 다른 하나는 9개월입니다. 시작 월·일도 다릅니다. 따라서 동일한 기간의 YoY 비교로 확인할 수 없습니다. 근거는 있습니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2022 Q KRW와 2021 YTD KRW에서 각각 확인됩니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-net_profit-2022-q-KRW",
    "s22q3-CFS-net_profit-2021-ytd-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['PERIOD_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s22q3-CFS-net_profit-2022-q-KRW`|9389198 · KRW · ×1000000|2022-07-01 ~ 2022-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Profit for the period / 2022 Q KRW|
|`s22q3-CFS-net_profit-2021-ytd-KRW`|29069502 · KRW · ×1000000|2021-01-01 ~ 2021-09-30 · 9개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Profit for the period / 2021 YTD KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

비교는 보류되었습니다. 기간 조건이 맞지 않습니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2022 Q KRW는 2022-07-01 ~ 2022-09-30, 3개월, 연결입니다. 같은 보고서의 PDF p.37의 Profit for the period / 2021 YTD KRW는 2021-01-01 ~ 2021-09-30, 9개월, 연결입니다. 따라서 3개월 순이익과 9개월 순이익은 같은 기간 길이의 비교가 아닙니다. 근거가 없는 것은 아닙니다. 해당 항목들의 근거는 있지만, 기간이 달라 비교가 제한됩니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-net_profit-2022-q-KRW",
    "s22q3-CFS-net_profit-2021-ytd-KRW"
  ]
}
```

</details>

## 12. `s22-op-qoq`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: Explain in Korean why 2022 Q3 and 2021 Q3 consolidated operating profit cannot be used for QoQ.

### 실제 생성 문장

> 계산을 보류합니다. QoQ는 인접한 분기끼리 비교해야 합니다. 그러나 2022-07-01 시작일이 2021-09-30 종료일의 다음 날이 아니어서 qoq_adjacent 조건을 만족하지 않습니다. 따라서 2022 Q3와 2021 Q3 연결 영업이익은 QoQ 비교에 사용할 수 없습니다. 근거 문서 제목은 Samsung Electronics 2022 Q3 Interim Report입니다. PDF p.37의 Operating profit / 2022 Q KRW와 Operating profit / 2021 Q KRW가 확인됩니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "s22q3-CFS-operating_profit-2021-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['PERIOD_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s22q3-CFS-operating_profit-2022-q-KRW`|10852045 · KRW · ×1000000|2022-07-01 ~ 2022-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Operating profit / 2022 Q KRW|
|`s22q3-CFS-operating_profit-2021-q-KRW`|15817531 · KRW · ×1000000|2021-07-01 ~ 2021-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Operating profit / 2021 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

Samsung Electronics 2022 Q3 Interim Report의 PDF p.37에서 확인한 연결 영업이익입니다. 2022-07-01~2022-09-30의 2022 Q KRW와 2021-07-01~2021-09-30의 2021 Q KRW는 둘 다 3개월 자료입니다. 다만 도구는 QoQ 비교로 사용할 수 없다고 판단했습니다. 문제 사유는 PERIOD_MISMATCH입니다. 기간 길이 또는 선택한 비교 방식의 날짜 조건이 맞지 않아 계산을 보류했습니다. 따라서 이 두 값으로 QoQ 결과를 확정할 수 없습니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "s22q3-CFS-operating_profit-2021-q-KRW"
  ]
}
```

</details>

## 13. `h25-op-yoy`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 현대자동차 2025년과 2024년 3분기 연결 영업이익의 전년 동분기 증감률을 단위와 함께 설명하세요.

### 실제 생성 문장

> 현대자동차의 2025년 3분기 연결 영업이익은 2,537,266 백만 원입니다. PDF p.8의 Hyundai Motor Company 2025 Q3 interim consolidated financial statements, Operating profit / 2025 Q KRW 근거입니다. 2024년 3분기 연결 영업이익은 3,580,900 백만 원입니다. 같은 문서의 PDF p.8, Operating profit / 2024 Q KRW 근거입니다. 전년 동분기 증감률은 -29.1445%입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "-29.1445",
  "issues": [],
  "evidence_ids": [
    "h25q3-CFS-operating_profit-2025-q-KRW",
    "h25q3-CFS-operating_profit-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `-29.1445` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`h25q3-CFS-operating_profit-2025-q-KRW`|2537266 · KRW · ×1000000|2025-07-01 ~ 2025-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Operating profit / 2025 Q KRW|
|`h25q3-CFS-operating_profit-2024-q-KRW`|3580900 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Operating profit / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

현대자동차 2025년 3분기 연결 영업이익은 2,537,266 백만 원입니다. 근거 문서는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8입니다. 같은 문서의 PDF p.8에서 2024년 3분기 연결 영업이익은 3,580,900 백만 원입니다. 전년 동분기 대비 증감률은 -29.1445%입니다.

```json
{
  "status": "verified",
  "value": "-29.1445%",
  "issues": [],
  "evidence_ids": [
    "h25q3-CFS-operating_profit-2025-q-KRW",
    "h25q3-CFS-operating_profit-2024-q-KRW"
  ]
}
```

</details>

## 14. `h25-net-yoy`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: Explain Hyundai Motor 2025 versus 2024 third-quarter-only consolidated net profit growth in Korean, with both source columns.

### 실제 생성 문장

> Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8에서 확인됩니다. 2025년 3분기 연결 순이익은 2,548,183 백만 원입니다. 같은 문서의 PDF p.8에서 2024년 3분기 연결 순이익은 3,205,850 백만 원입니다. 2025년 3분기와 2024년 3분기 연결 순이익 증감률은 -20.5146%입니다.

### 실제 구조 필드

```json
{
  "status": "verified",
  "value": "-20.5146",
  "issues": [],
  "evidence_ids": [
    "h25q3-CFS-net_profit-2025-q-KRW",
    "h25q3-CFS-net_profit-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `verified` · 값: `-20.5146` · 문제 목록: `[]`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`h25q3-CFS-net_profit-2025-q-KRW`|2548183 · KRW · ×1000000|2025-07-01 ~ 2025-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Profit for the period / 2025 Q KRW|
|`h25q3-CFS-net_profit-2024-q-KRW`|3205850 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Profit for the period / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

현대차 연결 기준 2025년 3분기 단독 순이익은 2,548,183 백만 원입니다. 근거 문서는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8입니다. 같은 문서의 PDF p.8에서 2024년 3분기 단독 순이익은 3,205,850 백만 원입니다. 따라서 2025년 3분기 단독 연결 순이익은 2024년 3분기 단독 대비 -20.5146%입니다.

```json
{
  "status": "verified",
  "value": "-20.5146%",
  "issues": [],
  "evidence_ids": [
    "h25q3-CFS-net_profit-2025-q-KRW",
    "h25q3-CFS-net_profit-2024-q-KRW"
  ]
}
```

</details>

## 15. `h25-op-period`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 현대자동차 2025년 9개월 누적과 2024년 단독3개월 연결 영업이익의 비교 제한을 설명하세요.

### 실제 생성 문장

> 계산 보류입니다. 두 기간의 개월 수가 같지 않습니다. 2025년 1월 1일~2025년 9월 30일의 9개월 연결 영업이익은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements PDF p.8의 Operating profit / 2025 YTD KRW입니다. 2024년 7월 1일~2024년 9월 30일의 3개월 연결 영업이익은 같은 문서 PDF p.8의 Operating profit / 2024 Q KRW입니다. 도구는 두 기간의 시작 월·일이 다르다고 판단해 비교를 보류했습니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "h25q3-CFS-operating_profit-2025-ytd-KRW",
    "h25q3-CFS-operating_profit-2024-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['PERIOD_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`h25q3-CFS-operating_profit-2025-ytd-KRW`|9772472 · KRW · ×1000000|2025-01-01 ~ 2025-09-30 · 9개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Operating profit / 2025 YTD KRW|
|`h25q3-CFS-operating_profit-2024-q-KRW`|3580900 · KRW · ×1000000|2024-07-01 ~ 2024-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Operating profit / 2024 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

비교는 보류되었습니다. 2025년 1월 1일~2025년 9월 30일의 9개월 연결 영업이익과 2024년 7월 1일~2024년 9월 30일의 3개월 연결 영업이익은 기간 길이가 달라 YOY 비교 조건이 맞지 않습니다. 근거는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8입니다. 첫 번째 사실은 Operating profit / 2025 YTD KRW, 두 번째 사실은 Operating profit / 2024 Q KRW입니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "h25q3-CFS-operating_profit-2025-ytd-KRW",
    "h25q3-CFS-operating_profit-2024-q-KRW"
  ]
}
```

</details>

## 16. `cross-company-period`

과거 그룹: v6에서 추가했던 문서 과제8건 · 이번에는 모두 동일 사례 재평가

요청: 삼성전자 2022년과 현대자동차 2025년 3분기 영업이익을 전년 동분기처럼 비교할 수 없는 이유와 각각의 보고서를 설명하세요.

### 실제 생성 문장

> 비교가 보류되었습니다. 서로 다른 회사입니다. 삼성전자는 Samsung Electronics 2022 Q3 Interim Report의 PDF p.37에서 확인된 연결 영업이익 10,852,045 백만 원입니다. 현대자동차는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8에서 확인된 연결 영업이익 2,537,266 백만 원입니다. 전년 동분기 비교는 같은 회사의 전년 같은 분기여야 합니다. 이 입력은 회사가 다릅니다. 또한 종료 연도도 전년 동기 조건을 충족하지 않습니다. 따라서 증가율은 산출하지 않았습니다.

### 실제 구조 필드

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "COMPANY_MISMATCH",
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "h25q3-CFS-operating_profit-2025-q-KRW"
  ]
}
```

### 도구 결과와 원문 위치

도구 판정: `needs_review` · 값: `None` · 문제 목록: `['COMPANY_MISMATCH', 'PERIOD_MISMATCH']`

|근거 ID|금액·통화·배율|기간·범위|문서·PDF쪽|행·열|
|---|---|---|---|---|
|`s22q3-CFS-operating_profit-2022-q-KRW`|10852045 · KRW · ×1000000|2022-07-01 ~ 2022-09-30 · 3개월 · CFS|[Samsung Electronics 2022 Q3 Interim Report · p.37](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf#page=37)|Operating profit / 2022 Q KRW|
|`h25q3-CFS-operating_profit-2025-q-KRW`|2537266 · KRW · ×1000000|2025-07-01 ~ 2025-09-30 · 3개월 · CFS|[Hyundai Motor Company 2025 Q3 interim consolidated financial statements · p.8](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf#page=8)|Operating profit / 2025 Q KRW|

검수자 작성: 설명 판정 **_____** / 구조 필드 일치 **_____** / 근거ID 일치 **_____** / 직접 확인한 원문 **_____** / 이유·모호한 문구 **_____**

<details><summary>직전 v6 응답 — 새 응답을 먼저 검토한 뒤 비교하세요</summary>

비교는 보류됩니다. 삼성전자 2022년 3분기 연결 영업이익은 Samsung Electronics 2022 Q3 Interim Report PDF p.37의 Operating profit / 2022 Q KRW입니다. 현대자동차 2025년 3분기 연결 영업이익은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements PDF p.8의 Operating profit / 2025 Q KRW입니다. 두 회사가 달라 COMPANY_MISMATCH가 발생했습니다. 또한 2022년 7~9월과 2025년 7~9월은 서로 다른 기준 연도라 전년 동분기 비교 조건으로 처리할 수 없어 PERIOD_MISMATCH가 발생했습니다. 따라서 전년 동분기 성장률은 산출하지 않습니다.

```json
{
  "status": "needs_review",
  "value": null,
  "issues": [
    "COMPANY_MISMATCH",
    "PERIOD_MISMATCH"
  ],
  "evidence_ids": [
    "s22q3-CFS-operating_profit-2022-q-KRW",
    "h25q3-CFS-operating_profit-2025-q-KRW"
  ]
}
```

</details>

## 검수 후 전달할 정보

실제 검수자(기존 b 여부), 날짜·시각·시간대, 기기·OS·브라우저, 받은 도움, 확인한 사례 ID, 설명·구조·근거ID 판정과 이유, 이번 기록의 익명 GitHub·지원서 공개 확인 여부를 알려 주세요. 확인하지 못한 사례는 미검수로 남깁니다.
