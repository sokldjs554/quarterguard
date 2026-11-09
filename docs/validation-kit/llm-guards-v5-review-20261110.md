# 최신 방어 적용 후 LLM 응답8개 검수 자료 — v5

**미검수 자료입니다.** 아래는 새 실제 응답과 도구 근거이며, 사람이 수행한 기록이 아닙니다. 검수자는 원문을 직접 보고 새 판정을 작성해 주세요. 이전 판정은 새 응답의 정답으로 간주하지 않습니다.

[실제 응답 원본](../../artifacts/llm-guards-v5-20261110/report.json) · [실행 기록](https://github.com/sokldjs554/quarterguard/actions/runs/42674807948). 같은 개발8건이며 입력 MCP는 과거 결과 재생, 이번 생성은 GPT-5.4-mini-2026-03-17 실제8회입니다.

## 기록할 기본 정보

- 실제 수행자/기존 b인지:
- 실제 검토 날짜·시각·시간대:
- 기기·OS·브라우저:
- 받은 도움·사용한 도구:
- 직접 원문을 본 범위와 열지 못한 자료:
- 이번 새 기록의 익명 GitHub·지원서 공개 확인 여부:

## 판정 양식

|사례|설명 판정(참/거짓/모호/판단 보류)|근거 ID 일치|문제 문구·이유|원문 확인 범위|
|---|---|---|---|---|
|normal-qoq|미작성|미작성|미작성|미작성|
|normal-yoy|미작성|미작성|미작성|미작성|
|period-mismatch|미작성|미작성|미작성|미작성|
|scope-mismatch|미작성|미작성|미작성|미작성|
|unit-draft|미작성|미작성|미작성|미작성|
|no-evidence|미작성|미작성|미작성|미작성|
|conflicting-number-draft|미작성|미작성|미작성|미작성|
|citation-draft|미작성|미작성|미작성|미작성|

숫자뿐 아니라 기간·연결/별도·표시 단위·인용 위치·보류 이유를 확인해 주세요. 근거가 있는데 없다고 설명하는지, 백분율의 단위가 빠지지 않았는지, 읽는 사람이 뜻을 오해할 표현도 살펴봐 주세요. 원문을 확인하지 못했으면 미확인으로 남겨 주세요. 과거 응답도 아래 접힌 부분에 있어 이번 비교는 맹검이 아닙니다.

## normal-qoq

### 새 설명 — 원응답 그대로

2024년 3분기 연결 매출의 전분기 대비 증감률은 6.7916%입니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW는 79,098,731 백만 원입니다. Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW는 74,068,302 백만 원입니다. 두 값은 모두 3개월 연결 기준입니다.

### 도구 결과와 구조화된 응답

도구 판정: `verified` · 문제: `[]` · 값: `6.7916`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q2-CFS-revenue-2024-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q2 PDF p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|74,068,302 백만 원(KRW)|2024-04-01~2024-06-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

2024년 3분기 연결 매출의 전분기 대비 증감률은 6.7916%입니다. 2024년 3분기 연결 매출은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue, 2024 Q KRW 기준 79,098,731 백만 원입니다. 직전 분기인 2024년 2분기 연결 매출은 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue, 2024 Q KRW 기준 74,068,302 백만 원입니다. 두 값 모두 3개월 연결 기준입니다.

</details>

## normal-yoy

### 새 설명 — 원응답 그대로

2024년 3분기 연결 매출의 전년 동분기 대비 증감률은 17.3491%입니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34에서 2024-07-01 ~ 2024-09-30 연결 매출은 79,098,731 백만 원입니다. 같은 보고서 PDF p.34에서 2023-07-01 ~ 2023-09-30 연결 매출은 67,404,652 백만 원입니다.

### 도구 결과와 구조화된 응답

도구 판정: `verified` · 문제: `[]` · 값: `17.3491`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q3-CFS-revenue-2023-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|67,404,652 백만 원(KRW)|2023-07-01~2023-09-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

2024년 3분기 연결 매출의 전년 동분기 대비 증감률은 17.3491%입니다. 2024년 7월 1일~2024년 9월 30일 3개월 연결 매출은 79,098,731 백만 원입니다. 근거: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2024 Q KRW. 2023년 7월 1일~2023년 9월 30일 3개월 연결 매출은 67,404,652 백만 원입니다. 근거: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2023 Q KRW.

</details>

## period-mismatch

### 새 설명 — 원응답 그대로

계산 보류입니다. 기간 조건이 맞지 않습니다. 비교 대상은 2024-01-01~2024-09-30의 9개월 누적 매출과 2023-07-01~2023-09-30의 3개월 매출입니다. 둘 다 연결(CFS) 기준입니다. 이 차이 때문에 성장률을 확정할 수 없습니다. 근거 문서는 Samsung Electronics 2024 3Q Interim Business Report이며, PDF 34쪽의 Revenue / 2024 YTD KRW와 Revenue / 2023 Q KRW입니다. 해당 검색 범위에서 확인할 수 없습니다.

### 도구 결과와 구조화된 응답

도구 판정: `needs_review` · 문제: `['PERIOD_MISMATCH']` · 값: `None`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-ytd-KRW",
  "s24q3-CFS-revenue-2023-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 YTD KRW|225,082,634 백만 원(KRW)|2024-01-01~2024-09-30 / 9개월 / 연결|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|67,404,652 백만 원(KRW)|2023-07-01~2023-09-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

비교 기간이 맞지 않습니다. 현재 값은 2024-01-01 ~ 2024-09-30의 9개월 누적 연결 매출입니다. 기준 값은 2023-07-01 ~ 2023-09-30의 3개월 연결 매출입니다. 따라서 같은 기간 대비 비교로 해석할 수 없습니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2024 YTD KRW. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2023 Q KRW.

</details>

## scope-mismatch

### 새 설명 — 원응답 그대로

계산 보류입니다. 연결·별도 범위가 달라 비교를 검증할 수 없습니다. 다른 분기라는 사실만으로는 보류 사유가 아닙니다. 근거: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2024 Q KRW. 79,098,731 백만 원 · 통화 KRW · 2024-07-01 ~ 2024-09-30 · 3개월 · 연결. 근거: Samsung Electronics 2024 Half-year Business Report, PDF p.104, Revenue / 2024 Q KRW. 53,734,118 백만 원 · 통화 KRW · 2024-04-01 ~ 2024-06-30 · 3개월 · 별도.

### 도구 결과와 구조화된 응답

도구 판정: `needs_review` · 문제: `['SCOPE_MISMATCH']` · 값: `None`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q2-OFS-revenue-2024-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q2 PDF p.104](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=104)|Revenue / 2024 Q KRW|53,734,118 백만 원(KRW)|2024-04-01~2024-06-30 / 3개월 / 별도|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

연결 매출과 별도 매출을 비교한 결과입니다. 다만 비교 범위가 서로 달라 검토가 필요합니다. 그래서 값은 확정하지 않았습니다.

근거 1: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34. 2024-07-01 ~ 2024-09-30, 3개월, 연결(CFS) 매출은 79,098,731 백만 원입니다.
근거 2: Samsung Electronics 2024 Half-year Business Report, PDF p.104. 2024-04-01 ~ 2024-06-30, 3개월, 별도(OFS) 매출은 53,734,118 백만 원입니다.

따라서 연결과 별도, 그리고 서로 다른 분기 기간을 직접 비교한 결과이므로 그대로 확정할 수 없습니다.

</details>

## unit-draft

### 새 설명 — 원응답 그대로

매출 증가율은 6.7916%입니다. 비교는 연결재무제표(CFS) 기준의 분기 매출입니다. 2024-07-01~2024-09-30 3개월 매출은 79,098,731 백만 원입니다. 근거 문서는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue / 2024 Q KRW입니다. 2024-04-01~2024-06-30 3개월 매출은 74,068,302 백만 원입니다. 근거 문서는 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue / 2024 Q KRW입니다. 금액의 표시 단위는 백만 원입니다.

### 도구 결과와 구조화된 응답

도구 판정: `verified` · 문제: `[]` · 값: `6.7916`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q2-CFS-revenue-2024-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q2 PDF p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|74,068,302 백만 원(KRW)|2024-04-01~2024-06-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

매출 증가율은 6.7916%입니다. 비교 기간은 분기 기준입니다. 2024년 7~9월 연결 매출은 79,098,731 백만 원입니다. 문서 제목은 Samsung Electronics 2024 3Q Interim Business Report이며 PDF 34페이지의 Revenue 항목입니다. 2024년 4~6월 연결 매출은 74,068,302 백만 원입니다. 문서 제목은 Samsung Electronics 2024 Half-year Business Report이며 PDF 48페이지의 Revenue 항목입니다. 두 금액의 표시 단위는 백만 원입니다. KRW는 통화입니다.

</details>

## no-evidence

### 새 설명 — 원응답 그대로

해당 검색 범위에서 확인할 수 없습니다. 따라서 2025년 실적을 이 결과만으로는 확인할 수 없습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인하세요. context needs review.

### 도구 결과와 구조화된 응답

도구 판정: `needs_review` · 문제: `['SEARCH_EMPTY']` · 값: `None`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[]
```

이 도구 결과의 근거 목록은 비어 있습니다. 특정 PDF가 없다는 주장으로 바꾸지 않습니다.

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

해당 검색 범위에서 확인할 수 없습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인하세요. 문서 근거가 없어 성장률이나 파생값을 확인할 수 없습니다.

</details>

## conflicting-number-draft

### 새 설명 — 원응답 그대로

연결 기준 매출 증가율은 6.7916%입니다. 2024년 3분기 연결 매출은 79,098,731 백만 원이며, Samsung Electronics 2024 3Q Interim Business Report의 PDF p.34에 있습니다. 2024년 2분기 연결 매출은 74,068,302 백만 원이며, Samsung Electronics 2024 Half-year Business Report의 PDF p.48에 있습니다. 두 분기 모두 3개월, 연결(CFS) 기준입니다.

### 도구 결과와 구조화된 응답

도구 판정: `verified` · 문제: `[]` · 값: `6.7916`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q2-CFS-revenue-2024-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q2 PDF p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|74,068,302 백만 원(KRW)|2024-04-01~2024-06-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

3개월 연결 기준 매출의 전분기 대비 증가율입니다. 2024년 3분기 연결 매출은 2024년 3분기 Samsung Electronics 2024 3Q Interim Business Report PDF p.34에서 79,098,731 백만 원입니다. 2024년 2분기 연결 매출은 2024년 2분기 Samsung Electronics 2024 Half-year Business Report PDF p.48에서 74,068,302 백만 원입니다. 도구 결과의 증가율은 6.7916%입니다. 표시 단위는 백만 원입니다.

</details>

## citation-draft

### 새 설명 — 원응답 그대로

삼성전자 2024년 3분기 연결 매출은 79,098,731 백만 원입니다. 출처는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34입니다. 같은 보고서 기준 2024년 2분기 연결 매출은 74,068,302 백만 원입니다. 출처는 Samsung Electronics 2024 Half-year Business Report, PDF p.48입니다. 두 분기는 모두 3개월 연결 기준의 분기 실적입니다. 따라서 매출 증가율은 6.7916입니다.

### 도구 결과와 구조화된 응답

도구 판정: `verified` · 문제: `[]` · 값: `6.7916`. 금액·증감률을 임의로 다시 작성하지 않았습니다.

모델의 구조화 응답:
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

도구가 요구한 근거 ID(순서 포함):
```json
[
  "s24q3-CFS-revenue-2024-q-KRW",
  "s24q2-CFS-revenue-2024-q-KRW"
]
```

|문서·쪽수|원문 행·열|금액·단위|실제 기간·범위|
|---|---|---|---|
|[s24q3 PDF p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|79,098,731 백만 원(KRW)|2024-07-01~2024-09-30 / 3개월 / 연결|
|[s24q2 PDF p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|74,068,302 백만 원(KRW)|2024-04-01~2024-06-30 / 3개월 / 연결|

<details><summary>직전 배치의 설명 — 비교용 원응답</summary>

삼성전자의 매출은 전분기 대비 증가했습니다. 2024년 3분기 연결 기준 매출은 79,098,731 백만 원입니다. 이는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue 항목입니다. 2024년 2분기 연결 기준 매출은 74,068,302 백만 원입니다. 이는 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue 항목입니다. 두 분기 모두 3개월 기준의 연결 재무제표입니다. 따라서 매출 증가율은 6.7916%입니다.

</details>

