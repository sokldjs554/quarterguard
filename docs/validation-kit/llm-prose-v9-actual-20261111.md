# v9 실제 응답 — b 재검수 자료

**새 사람 검수는 아직 수행하지 않았습니다.** 모델 원응답을 그대로 싣습니다. 먼저 새 문장·구조 필드와 원문을 대조하고 접힌 이전 응답은 그다음에 비교해 주세요. 이전 b 판정을 새 응답에 복사하지 않습니다.

[빈 검수표·기준](llm-prose-v9-review-20261111.md) · [실행 결과](../llm-prose-v9-results-20261111.md) · [원기록](../../artifacts/llm-prose-v9-20261111/report.json)

실제 모델: gpt-5.4-mini-2026-03-17, 시작 UTC 2026-11-11T06:55:59.867226+00:00, 호출16회. 기존16개 개발용 입력을 재사용했습니다. 사람 직접 작성 새 사례 평가와 구분합니다. 이번에는 PDF 파싱·검색·MCP를 새로 실행하지 않았습니다.

## 1. `normal-qoq`

요청: 2024년 3분기 연결 매출의 전분기 대비 증감률

### 새 실제 생성 문장

> 2024년 3분기 연결 매출의 전분기 대비 증감률은 6.7916%입니다. 기준은 2024년 2분기입니다. 2024년 3분기 연결 매출은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW에서 79,098,731 백만 원입니다. 2024년 2분기 연결 매출은 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW에서 74,068,302 백만 원입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

연결 기준 2024년 3분기 매출은 79,098,731 백만 원입니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW 항목입니다. 연결 기준 2024년 2분기 매출은 74,068,302 백만 원입니다. Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW 항목입니다. 전분기 대비 증가율은 6.7916%입니다.

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

</details>

## 2. `normal-yoy`

요청: 2024년 3분기 연결 매출의 전년 동분기 대비 증감률

### 새 실제 생성 문장

> Samsung Electronics 2024 3Q Interim Business Report, PDF p.34에서 확인됩니다. 2024년 3분기 연결 매출은 79,098,731 백만 원입니다. 같은 보고서 PDF p.34에서 2023년 3분기 연결 매출은 67,404,652 백만 원입니다. 2023년 3분기 대비 2024년 3분기 매출 증가율은 17.3491%입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW 기준 연결 매출은 79,098,731 백만 원입니다. 같은 보고서 PDF p.34의 Revenue / 2023 Q KRW 기준 연결 매출은 67,404,652 백만 원입니다. 전년 동분기 대비 증감률은 17.3491%입니다.

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

</details>

## 3. `period-mismatch`

요청: 9개월 누적과 전년 3개월 매출 비교의 제한

### 새 실제 생성 문장

> 계산 보류입니다. 기간 불일치가 있습니다. 9개월 누적과 전년 3개월은 같은 길이의 기간이 아닙니다. 따라서 비교를 확정할 수 없습니다. 근거 1은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 YTD KRW입니다. 2024-01-01 ~ 2024-09-30, 9개월, 연결입니다. 근거 2는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2023 Q KRW입니다. 2023-07-01 ~ 2023-09-30, 3개월, 연결입니다. 도구의 기간 불일치 보고를 유지합니다. 다음 재계산 사유로는 두 기간의 개월 수가 같지 않음, 전년 비교의 시작 월·일 조건 불일치가 있습니다. 

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

계산 보류입니다. 기간 불일치가 있습니다. 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 YTD KRW는 2024-01-01 ~ 2024-09-30, 9개월, 연결입니다. 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2023 Q KRW는 2023-07-01 ~ 2023-09-30, 3개월, 연결입니다. 9개월 누적과 전년 3개월은 직접 비교 기준이 맞지 않습니다. 따라서 증가율은 확정하지 않습니다.

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

요청: 연결 매출과 별도 매출 비교의 제한

### 새 실제 생성 문장

> 연결과 별도 범위가 달라 비교를 보류했습니다. 연결 매출은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34입니다. 별도 매출은 Samsung Electronics 2024 Half-year Business Report, PDF p.104입니다. 두 사실은 같은 범위가 아닙니다. 따라서 증가율은 확정하지 않습니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

연결 매출과 별도 매출의 범위가 다릅니다. 비교를 보류합니다. 확인된 근거는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW와 Samsung Electronics 2024 Half-year Business Report, PDF p.104의 Revenue / 2024 Q KRW입니다. 전자는 2024-07-01~2024-09-30 연결 79,098,731 백만 원입니다. 후자는 2024-04-01~2024-06-30 별도 53,734,118 백만 원입니다.

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

요청: 매출 증가율 및 근거 금액 단위를 설명

### 새 실제 생성 문장

> 증가율은 6.7916%입니다. 기준 기간 대비 현재 기간의 성장입니다. 현재 기간은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34입니다. 기준 기간은 Samsung Electronics 2024 Half-year Business Report, PDF p.48입니다. 두 금액의 표시 단위는 백만 원입니다. 현재 기간 매출은 79,098,731 백만 원입니다. 기준 기간 매출은 74,068,302 백만 원입니다. 통화는 KRW입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

증가율 6.7916%입니다. 연결 기준 매출입니다. 기준은 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW입니다. 금액은 74,068,302 백만 원입니다. 비교 대상은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW입니다. 금액은 79,098,731 백만 원입니다. 둘 다 통화는 KRW이고 표시 단위는 백만 원입니다.

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

</details>

## 6. `no-evidence`

요청: 수집 범위 밖인 2025년 실적 조회

### 새 실제 생성 문장

> 현재 검색 조건으로 확인할 수 있는 근거를 찾지 못했습니다. 해당 검색 범위에서 확인할 수 없습니다. 이는 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인해야 합니다. 도구의 문제 목록을 설명한 안내입니다. AI 문장 전체에 대한 의미 검증은 아닙니다.

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

이 도구 결과에는 근거가 없습니다. 해당 검색 범위에 한정합니다.

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

해당 검색 범위에서 확인할 수 없습니다. 수집 범위 밖인 2025년 실적 조회라서 근거를 확인하지 못했습니다. 문서 메타데이터가 없어 특정 보고서명과 PDF 페이지를 적을 수 없습니다. 결정 근거는 SEARCH_EMPTY입니다.

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

요청: 근거에 맞는 매출 증가율을 설명

### 새 실제 생성 문장

> Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW는 2024-07-01 ~ 2024-09-30 연결 매출 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW는 2024-04-01 ~ 2024-06-30 연결 매출 74,068,302 백만 원입니다. 2024년 2분기 대비 2024년 3분기 연결 매출 증가율은 6.7916%입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34에서 연결 매출은 2024-07-01~2024-09-30, 3개월, 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report의 PDF p.48에서 연결 매출은 2024-04-01~2024-06-30, 3개월, 74,068,302 백만 원입니다. 이 두 분기 비교의 증가율은 6.7916%입니다.

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

</details>

## 8. `citation-draft`

요청: 공시 근거에 맞는 매출 증가율을 설명

### 새 실제 생성 문장

> 연결 기준입니다. 2024년 3분기 매출은 Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34, Revenue / 2024 Q KRW에서 79,098,731 백만 원입니다. 2024년 2분기 매출은 Samsung Electronics 2024 Half-year Business Report의 PDF p.48, Revenue / 2024 Q KRW에서 74,068,302 백만 원입니다. 2024년 2분기 대비 2024년 3분기 매출 증가율은 6.7916%입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

연결 기준 매출 증가율은 6.7916%입니다. 2024년 3분기 매출은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW에서 79,098,731 백만 원입니다. 2024년 2분기 매출은 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW에서 74,068,302 백만 원입니다. 비교 기간은 각각 3개월입니다. 따라서 2024년 3분기 연결 매출 증가율은 6.7916%입니다.

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

</details>

## 9. `s22-op-yoy`

요청: 삼성전자 2022년과 2021년 3분기 연결 영업이익의 전년 동분기 증감률을 설명하세요.

### 새 실제 생성 문장

> 삼성전자 2022년 3분기 연결 영업이익은 Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Operating profit / 2022 Q KRW에서 10,852,045 백만 원입니다. 2021년 3분기 연결 영업이익은 같은 문서의 PDF p.37의 Operating profit / 2021 Q KRW에서 15,817,531 백만 원입니다. 2021년 3분기 대비 2022년 3분기의 증감률은 -31.3923%입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

삼성전자의 연결 영업이익은 2022년 3분기 10,852,045 백만 원입니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Operating profit / 2022 Q KRW 기준입니다. 2021년 3분기 연결 영업이익은 15,817,531 백만 원입니다. 같은 문서의 PDF p.37, Operating profit / 2021 Q KRW 기준입니다. 전년 동분기 증감률은 -31.3923%입니다.

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

요청: 삼성전자 2022년과 2021년 9개월 누적 연결 당기순이익의 전년 동기 증감률과 출처를 설명하세요.

### 새 실제 생성 문장

> 삼성전자 2022년 9개월 누적 연결 당기순이익은 31,812,631 백만 원입니다. 2021년 9개월 누적 연결 당기순이익은 29,069,502 백만 원입니다. 기준 기간 대비 현재 기간 증가율은 9.4364%입니다. 출처는 Samsung Electronics 2022 Q3 Interim Report입니다. PDF 37페이지의 Profit for the period 항목입니다. 2022 YTD KRW와 2021 YTD KRW를 비교했습니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

삼성전자 2022년 1월~9월 연결 당기순이익은 31,812,631 백만 원입니다. 삼성전자 2021년 1월~9월 연결 당기순이익은 29,069,502 백만 원입니다. 전년 동기 증감률은 9.4364%입니다. 출처는 Samsung Electronics 2022 Q3 Interim Report입니다. PDF p.37의 Profit for the period 항목에서 2022 YTD KRW와 2021 YTD KRW를 확인했습니다.

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

</details>

## 11. `s22-net-period`

요청: 삼성전자 2022년 3개월과 2021년 9개월 연결 순이익의 비교 제한을 설명하세요. 근거가 없는 것인지 구분하세요.

### 새 실제 생성 문장

> 비교가 보류되었습니다. 기간 불일치가 있습니다. 2022년 3개월 연결 순이익은 Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2022 Q KRW입니다. 2021년 9개월 연결 순이익은 같은 보고서의 PDF p.37의 Profit for the period / 2021 YTD KRW입니다. 3개월과 9개월은 같은 기간 길이가 아닙니다. 시작 월·일도 다릅니다. 따라서 증가율은 검증하지 않았습니다. 이는 근거가 없는 것이 아니라 기간 비교 제한입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

비교 제한이 있습니다. 도구가 기간 불일치를 보고했습니다. 2022년 3개월과 2021년 9개월은 같은 기간 길이가 아닙니다. 그래서 증가율은 보류됩니다. 이건 근거가 없는 것이 아니라, 서로 다른 기간을 비교해 검증을 멈춘 경우입니다. 근거는 있습니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Profit for the period / 2022 Q KRW는 2022-07-01 ~ 2022-09-30, 3개월, 연결입니다. 같은 보고서 PDF p.37의 Profit for the period / 2021 YTD KRW는 2021-01-01 ~ 2021-09-30, 9개월, 연결입니다. 다만 기간이 달라 직접 비교를 확정할 수 없습니다.

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

요청: Explain in Korean why 2022 Q3 and 2021 Q3 consolidated operating profit cannot be used for QoQ.

### 새 실제 생성 문장

> 보류입니다. 분기 대비 비교 조건을 충족하지 않습니다. 도구는 기간 불일치를 보고했습니다. 이는 별도 재계산 진단입니다. 2022 Q3와 2021 Q3는 바로 이어지는 분기가 아닙니다. 따라서 QoQ로 사용할 수 없습니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 Operating profit / 2022 Q KRW는 2022-07-01 ~ 2022-09-30, 3개월, 연결입니다. 같은 문서의 PDF p.37, Operating profit / 2021 Q KRW는 2021-07-01 ~ 2021-09-30, 3개월, 연결입니다. 비교 기간이 인접 분기가 아니므로 계산을 보류합니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

2022 Q3와 2021 Q3의 연결 영업이익은 QoQ용으로 쓸 수 없습니다. 도구가 기간 불일치로 보류했습니다. 비교한 두 기간은 바로 이어지는 분기가 아닙니다. 따라서 인접 분기 기준이 맞지 않습니다. Samsung Electronics 2022 Q3 Interim Report, PDF p.37의 2022 Q KRW는 2022-07-01 ~ 2022-09-30, 3개월, 연결입니다. 같은 문서의 PDF p.37의 2021 Q KRW는 2021-07-01 ~ 2021-09-30, 3개월, 연결입니다. 두 값은 서로 다른 연도의 같은 분기입니다. QoQ 비교 조건을 충족하지 않습니다.

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

요청: 현대자동차 2025년과 2024년 3분기 연결 영업이익의 전년 동분기 증감률을 단위와 함께 설명하세요.

### 새 실제 생성 문장

> 현대자동차 연결 기준 영업이익의 2025년 3분기 2,537,266 백만 원은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8에 있습니다. 2024년 3분기 3,580,900 백만 원도 같은 문서의 PDF p.8에 있습니다. 2024년 3분기 대비 2025년 3분기 증감률은 -29.1445%입니다. 즉 감소했습니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

현대자동차 연결 3분기 영업이익의 전년 동분기 증감률은 -29.1445%입니다. 2025년 3분기 영업이익은 2,537,266 백만 원입니다. 근거 문서는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements이며 PDF p.8의 Operating profit / 2025 Q KRW입니다. 2024년 3분기 영업이익은 3,580,900 백만 원입니다. 같은 문서의 PDF p.8의 Operating profit / 2024 Q KRW입니다.

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

</details>

## 14. `h25-net-yoy`

요청: Explain Hyundai Motor 2025 versus 2024 third-quarter-only consolidated net profit growth in Korean, with both source columns.

### 새 실제 생성 문장

> Hyundai Motor Company 2025 Q3 interim consolidated financial statements, PDF p.8의 Profit for the period / 2025 Q KRW는 2025년 7월 1일~2025년 9월 30일 3개월 연결 기준 2,548,183 백만 원입니다. Hyundai Motor Company 2025 Q3 interim consolidated financial statements, PDF p.8의 Profit for the period / 2024 Q KRW는 2024년 7월 1일~2024년 9월 30일 3개월 연결 기준 3,205,850 백만 원입니다. 2024년 3분기 대비 2025년 3분기 증가율은 -20.5146%입니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

현대자동차의 2025년 3분기 연결 순이익은 2,548,183 백만 원입니다. 근거 문서는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements이며 PDF 8쪽의 Profit for the period / 2025 Q KRW입니다. 2024년 3분기 연결 순이익은 3,205,850 백만 원입니다. 같은 문서의 PDF 8쪽 Profit for the period / 2024 Q KRW입니다. 2025년 3분기 대비 2024년 3분기 순이익 증가율은 -20.5146%입니다.

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

</details>

## 15. `h25-op-period`

요청: 현대자동차 2025년 9개월 누적과 2024년 단독3개월 연결 영업이익의 비교 제한을 설명하세요.

### 새 실제 생성 문장

> 비교 제한이 있습니다. 기간 불일치입니다. 도구의 비교 제한을 유지합니다. 2025-01-01 ~ 2025-09-30 9개월 연결 영업이익은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements, PDF p.8, Operating profit / 2025 YTD KRW에서 확인됩니다. 9,772,472 백만 원입니다. 2024-07-01 ~ 2024-09-30 3개월 연결 영업이익은 같은 문서의 PDF p.8, Operating profit / 2024 Q KRW에서 확인됩니다. 3,580,900 백만 원입니다. 두 기간의 개월 수가 같지 않습니다. 비교 기준이 다릅니다. 시작 월·일도 다릅니다. 따라서 증가율은 보류합니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

계산을 보류합니다. 기간이 다릅니다. 2025년 9개월 누적은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements, PDF p.8의 Operating profit / 2025 YTD KRW입니다. 2024년 단독 3개월은 Hyundai Motor Company 2025 Q3 interim consolidated financial statements, PDF p.8의 Operating profit / 2024 Q KRW입니다. 누적과 단독 3개월은 직접 비교 제한이 있습니다. 도구가 기간 불일치를 보고했습니다. 별도 재계산 기준으로도 개월 수가 같지 않고 시작 월·일이 같지 않아 보류합니다.

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

요청: 삼성전자 2022년과 현대자동차 2025년 3분기 영업이익을 전년 동분기처럼 비교할 수 없는 이유와 각각의 보고서를 설명하세요.

### 새 실제 생성 문장

> 계산을 보류합니다. 회사가 달라서 같은 지표로 전년 동분기 비교를 할 수 없습니다. 기간도 다릅니다. 삼성전자 보고서는 Samsung Electronics 2022 Q3 Interim Report의 PDF p.37입니다. 여기에 2022-07-01 ~ 2022-09-30, 3개월, 연결 기준 영업이익이 나옵니다. 값은 10,852,045 백만 원입니다. 현대자동차 보고서는 Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8입니다. 여기에 2025-07-01 ~ 2025-09-30, 3개월, 연결 기준 영업이익이 나옵니다. 값은 2,537,266 백만 원입니다. 기간 불일치 진단은 별도 재계산 결과입니다. 전년 동분기 조건은 충족하지 않습니다.

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

검수자 작성: 설명 판정 _____ / 구조 필드 _____ / 근거ID _____ / 직접 확인한 원문 _____ / 이유 _____

<details><summary>직전 v8 응답 — 새 응답을 먼저 검토한 뒤 열어 주세요</summary>

비교할 수 없는 이유는 두 가지입니다. 첫째, 회사가 다릅니다. 삼성전자 2022년 3분기와 현대자동차 2025년 3분기는 같은 회사의 전년 동분기 비교가 아닙니다. 둘째, 기간도 다릅니다. Samsung Electronics 2022 Q3 Interim Report의 PDF p.37에서 영업이익은 2022-07-01 ~ 2022-09-30, 3개월, 연결입니다. Hyundai Motor Company 2025 Q3 interim consolidated financial statements의 PDF p.8에서 영업이익은 2025-07-01 ~ 2025-09-30, 3개월, 연결입니다. 따라서 전년 동분기 비교 조건을 충족하지 못합니다. 도구가 COMPANY_MISMATCH와 PERIOD_MISMATCH를 보고했으며, 기간 문제는 종료 연도 기준의 재계산 진단에서 확인된 것입니다. 각 보고서의 값은 삼성전자 10,852,045 백만 원, 현대자동차 2,537,266 백만 원입니다.

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

## 실제 검수 후 기록

날짜·시각·환경·받은 도움·미확인 범위는 실제 수행 후 기록해 주세요. 기존 b의 역할과 확인된 공개 범위를 적용하며 새 참여자로 세지 않습니다.
