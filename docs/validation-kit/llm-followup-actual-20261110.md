# 새 응답 검수 자료 — QuarterGuard 설명 개선 후 8건

**실제 새 모델 응답과 도구 결과입니다. 사람 판정은 모두 미작성입니다.**

실행: [Actions 42650382374](https://github.com/sokldjs554/quarterguard/actions/runs/42650382374), GPT-5.4-mini-2026-03-17, 2026-11-10 KST. 새 생성8건이며 입력 근거는 이전에 동결한 실제 MCP 결과의 재생입니다. 새 PDF 파싱이나 실시간 재조회가 아닙니다.

새 문장을 먼저 도구 결과와 발행사 원문에 대조한 뒤 기존 문장과 비교해 주세요. 자동검사 결과와 기존 사람 판정은 이 양식에 넣지 않았습니다. 이미 본 개발 사례의 후속이며 독립 블라인드 평가가 아닙니다.

금액·기간·연결/별도·통화/표시 단위·문서/페이지를 확인해 주세요. 근거 부재는 검색 범위의 한계인지, 본문이 비교 보류의 이유를 정확히 설명하는지도 봐 주세요. 문장 판정과 구조화 근거 ID 일치는 따로 적어 주세요.

검수자: ___ / 실제 수행 날짜·시각(KST): ___ / 기기·OS·브라우저: ___ / 받은 도움: ___

이번 익명 GitHub·지원서 공개 확인: ___ / 원본 보관·삭제 범위: ___

## normal-qoq

### 새 응답 — 수정하지 않은 모델 출력

2024년 3분기 연결 매출의 전분기 대비 증감률은 6.7916%입니다. 2024년 3분기 연결 매출은 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue, 2024 Q KRW 기준 79,098,731 백만 원입니다. 직전 분기인 2024년 2분기 연결 매출은 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue, 2024 Q KRW 기준 74,068,302 백만 원입니다. 두 값 모두 3개월 연결 기준입니다.

구조 필드:

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

```json
{
  "status": "verified",
  "issues": [],
  "growth_pct": "6.7916",
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|74068302|KRW / 1000000|2024-04-01 ~ 2024-06-30 / 3|CFS|[s24q2 p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

2024년 3분기 연결 매출은 2024년 2분기 대비 6.7916% 증가했습니다. 단위는 KRW이며, 비교 범위는 연결재무제표(CFS) 매출입니다.

</details>


## normal-yoy

### 새 응답 — 수정하지 않은 모델 출력

2024년 3분기 연결 매출의 전년 동분기 대비 증감률은 17.3491%입니다. 2024년 7월 1일~2024년 9월 30일 3개월 연결 매출은 79,098,731 백만 원입니다. 근거: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2024 Q KRW. 2023년 7월 1일~2023년 9월 30일 3개월 연결 매출은 67,404,652 백만 원입니다. 근거: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2023 Q KRW.

구조 필드:

```json
{
  "status": "verified",
  "value": "17.3491",
  "issues": [],
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q3-CFS-revenue-2023-q-KKR"
  ]
}
```

### 도구 결과와 원문 위치

```json
{
  "status": "verified",
  "issues": [],
  "growth_pct": "17.3491",
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|67404652|KRW / 1000000|2023-07-01 ~ 2023-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

2024년 3분기 연결 매출은 2023년 3분기 대비 17.3491% 증가했습니다. 비교 기간은 2024-07-01~2024-09-30과 2023-07-01~2023-09-30이며, 단위는 KRW 기준 연결(CFS) 매출입니다.

</details>


## period-mismatch

### 새 응답 — 수정하지 않은 모델 출력

비교 기간이 맞지 않습니다. 현재 값은 2024-01-01 ~ 2024-09-30의 9개월 누적 연결 매출입니다. 기준 값은 2023-07-01 ~ 2023-09-30의 3개월 연결 매출입니다. 따라서 같은 기간 대비 비교로 해석할 수 없습니다. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2024 YTD KRW. Samsung Electronics 2024 3Q Interim Business Report, PDF p.34, Revenue / 2023 Q KRW.

구조 필드:

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

```json
{
  "status": "needs_review",
  "issues": [
    "PERIOD_MISMATCH"
  ],
  "growth_pct": null,
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-ytd-KRW",
    "s24q3-CFS-revenue-2023-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|225082634|KRW / 1000000|2024-01-01 ~ 2024-09-30 / 9|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 YTD KRW|
|67404652|KRW / 1000000|2023-07-01 ~ 2023-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2023 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

전년 동기 비교가 아니라 2024년 9개월 누적 매출과 2023년 3개월 매출을 비교하고 있어 기간이 일치하지 않습니다. 두 값 모두 삼성 CFS 매출이며 단위는 KRW(표시 스케일은 백만원)지만, 이 비교는 제한되어 있어 검증 완료로 볼 수 없습니다.

</details>


## scope-mismatch

### 새 응답 — 수정하지 않은 모델 출력

연결 매출과 별도 매출을 비교한 결과입니다. 다만 비교 범위가 서로 달라 검토가 필요합니다. 그래서 값은 확정하지 않았습니다.

근거 1: Samsung Electronics 2024 3Q Interim Business Report, PDF p.34. 2024-07-01 ~ 2024-09-30, 3개월, 연결(CFS) 매출은 79,098,731 백만 원입니다.
근거 2: Samsung Electronics 2024 Half-year Business Report, PDF p.104. 2024-04-01 ~ 2024-06-30, 3개월, 별도(OFS) 매출은 53,734,118 백만 원입니다.

따라서 연결과 별도, 그리고 서로 다른 분기 기간을 직접 비교한 결과이므로 그대로 확정할 수 없습니다.

구조 필드:

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

```json
{
  "status": "needs_review",
  "issues": [
    "SCOPE_MISMATCH"
  ],
  "growth_pct": null,
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-OFS-revenue-2024-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|53734118|KRW / 1000000|2024-04-01 ~ 2024-06-30 / 3|OFS|[s24q2 p.104](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=104)|Revenue / 2024 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

2024년 7~9월 연결(CFS) 매출과 2024년 4~6월 별도(OFS) 매출을 같은 기준으로 직접 비교할 수 없어 검토가 필요합니다. 두 값은 매출이지만 연결/별도 범위가 달라 분기·단위는 같아도 비교 제한이 있습니다.

</details>


## unit-draft

### 새 응답 — 수정하지 않은 모델 출력

매출 증가율은 6.7916%입니다. 비교 기간은 분기 기준입니다. 2024년 7~9월 연결 매출은 79,098,731 백만 원입니다. 문서 제목은 Samsung Electronics 2024 3Q Interim Business Report이며 PDF 34페이지의 Revenue 항목입니다. 2024년 4~6월 연결 매출은 74,068,302 백만 원입니다. 문서 제목은 Samsung Electronics 2024 Half-year Business Report이며 PDF 48페이지의 Revenue 항목입니다. 두 금액의 표시 단위는 백만 원입니다. KRW는 통화입니다.

구조 필드:

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

```json
{
  "status": "verified",
  "issues": [],
  "growth_pct": "6.7916",
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|74068302|KRW / 1000000|2024-04-01 ~ 2024-06-30 / 3|CFS|[s24q2 p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

삼성의 연결재무제표(CFS) 매출은 2024년 2분기 74,068,302백만 KRW에서 2024년 3분기 79,098,731백만 KRW로 증가해 QoQ 증가율은 6.7916%입니다. 근거 금액은 모두 KRW 기준이며, 표의 scale=1,000,000에 따라 백만 원 단위로 제시되었습니다.

</details>


## no-evidence

### 새 응답 — 수정하지 않은 모델 출력

해당 검색 범위에서 확인할 수 없습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다. 검색 조건과 수집 범위를 확인하세요. 문서 근거가 없어 성장률이나 파생값을 확인할 수 없습니다.

구조 필드:

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

```json
{
  "status": "needs_review",
  "issues": [
    "SEARCH_EMPTY"
  ],
  "evidence_ids": []
}
```

이 검색 결과에는 근거가 없습니다. 보고서나 실적 자체의 부재를 뜻하지 않습니다.

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

검색 결과가 없어 2025년 실적을 확인할 수 없습니다. 수집 범위 밖이거나 조회 데이터가 비어 있어 검증이 필요합니다.

</details>


## conflicting-number-draft

### 새 응답 — 수정하지 않은 모델 출력

3개월 연결 기준 매출의 전분기 대비 증가율입니다. 2024년 3분기 연결 매출은 2024년 3분기 Samsung Electronics 2024 3Q Interim Business Report PDF p.34에서 79,098,731 백만 원입니다. 2024년 2분기 연결 매출은 2024년 2분기 Samsung Electronics 2024 Half-year Business Report PDF p.48에서 74,068,302 백만 원입니다. 도구 결과의 증가율은 6.7916%입니다. 표시 단위는 백만 원입니다.

구조 필드:

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

```json
{
  "status": "verified",
  "issues": [],
  "growth_pct": "6.7916",
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|74068302|KRW / 1000000|2024-04-01 ~ 2024-06-30 / 3|CFS|[s24q2 p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

삼성전자의 연결기준 매출은 2024년 2분기(2024-04-01~2024-06-30) 74,068,302백만 KRW에서 2024년 3분기(2024-07-01~2024-09-30) 79,098,731백만 KRW로 증가해 QoQ 기준 6.7916% 상승했습니다. 단위는 KRW이며, 비교 범위는 동일한 연결재무제표(CFS) 매출입니다.

</details>


## citation-draft

### 새 응답 — 수정하지 않은 모델 출력

삼성전자의 매출은 전분기 대비 증가했습니다. 2024년 3분기 연결 기준 매출은 79,098,731 백만 원입니다. 이는 Samsung Electronics 2024 3Q Interim Business Report, PDF p.34의 Revenue 항목입니다. 2024년 2분기 연결 기준 매출은 74,068,302 백만 원입니다. 이는 Samsung Electronics 2024 Half-year Business Report, PDF p.48의 Revenue 항목입니다. 두 분기 모두 3개월 기준의 연결 재무제표입니다. 따라서 매출 증가율은 6.7916%입니다.

구조 필드:

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

```json
{
  "status": "verified",
  "issues": [],
  "growth_pct": "6.7916",
  "evidence_ids": [
    "s24q3-CFS-revenue-2024-q-KRW",
    "s24q2-CFS-revenue-2024-q-KRW"
  ]
}
```

|금액|통화·배율|기간·개월|범위|문서·쪽수|행·열|
|---|---|---|---|---|---|
|79098731|KRW / 1000000|2024-07-01 ~ 2024-09-30 / 3|CFS|[s24q3 p.34](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34)|Revenue / 2024 Q KRW|
|74068302|KRW / 1000000|2024-04-01 ~ 2024-06-30 / 3|CFS|[s24q2 p.48](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_Half_Interim_Report.pdf#page=48)|Revenue / 2024 Q KRW|

### 직접 검수 기록 — 빈칸

- 새 문장 판정(참/거짓/모호/판단 불가): ___
- 수치·기간·범위·표시 단위 확인과 이유: ___
- 구조화 근거 ID 및 문서·페이지·행·열 확인: ___
- 남은 모호함: ___
- 기존 대비 나아진 점·나빠진 점: ___

<details><summary>기존 응답 — 새 문장 검수 후 비교</summary>

삼성전자 연결기준(CFS) 매출은 2024년 2분기 74,068,302백만 KRW에서 2024년 3분기 79,098,731백만 KRW로 증가해 전분기 대비 매출 증가율은 6.7916%입니다. 비교 기간은 2024-04-01~2024-06-30과 2024-07-01~2024-09-30의 3개월 분기이고, 단위는 KRW이며 공시 표기는 백만 단위(scale 1,000,000)입니다.

</details>

